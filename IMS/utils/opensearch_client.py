"""
OpenSearch Vector Database Client
Handles semantic search for similar incidents using k-NN
"""

import json
import time
from typing import Dict, Any, List, Optional
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3
from config import AWSConfig, ERROR_MESSAGES
from utils.logger import get_logger

logger = get_logger(__name__)

class OpenSearchClient:
    """
    Client for OpenSearch vector database operations
    """
    
    def __init__(self):
        self.logger = logger
        self.index_name = AWSConfig.OPENSEARCH_INDEX
        self.client = self._initialize_client()
    
    def _initialize_client(self) -> OpenSearch:
        """Initialize OpenSearch client with AWS authentication"""
        try:
            # AWS authentication
            credentials = boto3.Session().get_credentials()
            awsauth = AWS4Auth(
                credentials.access_key,
                credentials.secret_key,
                AWSConfig.REGION,
                'es',
                session_token=credentials.token
            )
            
            # Parse endpoint
            endpoint = AWSConfig.OPENSEARCH_ENDPOINT.replace('https://', '').replace('http://', '')
            
            client = OpenSearch(
                hosts=[{'host': endpoint, 'port': 443}],
                http_auth=awsauth,
                use_ssl=True,
                verify_certs=True,
                connection_class=RequestsHttpConnection,
                timeout=30
            )
            
            self.logger.info("OpenSearch client initialized successfully")
            return client
            
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenSearch client: {str(e)}")
            raise
    
    def create_index(self):
        """
        Create OpenSearch index with k-NN mapping for vector search
        """
        try:
            index_body = {
                "settings": {
                    "index.knn": True,
                    "number_of_shards": 1,
                    "number_of_replicas": 1
                },
                "mappings": {
                    "properties": {
                        "incident_id": {"type": "keyword"},
                        "embedding": {
                            "type": "knn_vector",
                            "dimension": AWSConfig.OPENSEARCH_EMBEDDING_DIMENSION,
                            "method": {
                                "name": "hnsw",
                                "engine": "nmslib",
                                "space_type": "cosinesimil",
                                "parameters": {
                                    "ef_construction": 128,
                                    "m": 24
                                }
                            }
                        },
                        "description": {"type": "text"},
                        "resolution": {"type": "text"},
                        "category": {"type": "keyword"},
                        "priority": {"type": "integer"},
                        "severity": {"type": "keyword"},
                        "affected_systems": {"type": "keyword"},
                        "timestamp": {"type": "date"},
                        "resolved_at": {"type": "date"},
                        "resolution_time_minutes": {"type": "integer"},
                        "symptoms": {"type": "text"},
                        "root_cause": {"type": "text"}
                    }
                }
            }
            
            if not self.client.indices.exists(index=self.index_name):
                response = self.client.indices.create(
                    index=self.index_name,
                    body=index_body
                )
                self.logger.info(f"Index '{self.index_name}' created successfully")
                return response
            else:
                self.logger.info(f"Index '{self.index_name}' already exists")
                return {'acknowledged': True}
                
        except Exception as e:
            self.logger.error(f"Failed to create index: {str(e)}")
            raise
    
    def index_incident(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Index a single incident with embeddings
        
        Args:
            incident_data: Incident data including embeddings
            
        Returns:
            dict: Indexing result
        """
        try:
            document = {
                'incident_id': incident_data['incident_id'],
                'embedding': incident_data['embedding'],
                'description': incident_data['description'],
                'resolution': incident_data.get('resolution', ''),
                'category': incident_data['category'],
                'priority': incident_data['priority'],
                'severity': incident_data.get('severity', 'Medium'),
                'affected_systems': incident_data.get('affected_systems', []),
                'timestamp': incident_data['timestamp'],
                'resolved_at': incident_data.get('resolved_at'),
                'resolution_time_minutes': incident_data.get('resolution_time_minutes'),
                'symptoms': incident_data.get('symptoms', ''),
                'root_cause': incident_data.get('root_cause', '')
            }
            
            response = self.client.index(
                index=self.index_name,
                body=document,
                id=incident_data['incident_id'],
                refresh=True
            )
            
            self.logger.info(f"Incident indexed: {incident_data['incident_id']}")
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to index incident: {str(e)}", 
                            incident_id=incident_data.get('incident_id'))
            raise
    
    def query_similar_incidents(self, embedding: List[float], 
                               category: Optional[str] = None,
                               top_k: int = None) -> List[Dict[str, Any]]:
        """
        Query for similar incidents using k-NN vector search
        
        Args:
            embedding: Query embedding vector
            category: Optional category filter
            top_k: Number of results to return (default from config)
            
        Returns:
            list: Similar incidents with similarity scores
        """
        start_time = time.time()
        
        try:
            top_k = top_k or AWSConfig.OPENSEARCH_TOP_K
            
            # Build k-NN query
            query = {
                "size": top_k,
                "query": {
                    "knn": {
                        "embedding": {
                            "vector": embedding,
                            "k": top_k
                        }
                    }
                },
                "_source": {
                    "excludes": ["embedding"]  # Don't return embedding in results
                }
            }
            
            # Add category filter if specified
            if category:
                query["query"] = {
                    "bool": {
                        "must": [
                            query["query"]
                        ],
                        "filter": {
                            "term": {"category": category}
                        }
                    }
                }
            
            # Execute search
            response = self.client.search(
                index=self.index_name,
                body=query
            )
            
            # Parse results
            similar_incidents = []
            for hit in response['hits']['hits']:
                similarity_score = hit['_score']
                
                # Only include if above threshold
                if similarity_score >= AWSConfig.OPENSEARCH_SIMILARITY_THRESHOLD:
                    incident = hit['_source']
                    incident['similarity_score'] = round(similarity_score, 4)
                    similar_incidents.append(incident)
            
            query_time = time.time() - start_time
            
            self.logger.info(f"Similar incidents query completed",
                           results_count=len(similar_incidents),
                           query_time=round(query_time, 3),
                           category=category)
            
            # Log metric
            self.logger.log_metric(
                metric_name='VectorSearchTime',
                value=query_time,
                unit='Seconds',
                ResultCount=str(len(similar_incidents))
            )
            
            return similar_incidents
            
        except Exception as e:
            self.logger.error(f"Failed to query similar incidents: {str(e)}")
            raise
    
    def bulk_index_incidents(self, incidents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Bulk index multiple incidents
        
        Args:
            incidents: List of incident data
            
        Returns:
            dict: Bulk indexing result
        """
        try:
            from opensearchpy import helpers
            
            actions = [
                {
                    "_index": self.index_name,
                    "_id": incident['incident_id'],
                    "_source": {
                        'incident_id': incident['incident_id'],
                        'embedding': incident['embedding'],
                        'description': incident['description'],
                        'resolution': incident.get('resolution', ''),
                        'category': incident['category'],
                        'priority': incident['priority'],
                        'severity': incident.get('severity', 'Medium'),
                        'affected_systems': incident.get('affected_systems', []),
                        'timestamp': incident['timestamp'],
                        'resolved_at': incident.get('resolved_at'),
                        'resolution_time_minutes': incident.get('resolution_time_minutes'),
                        'symptoms': incident.get('symptoms', ''),
                        'root_cause': incident.get('root_cause', '')
                    }
                }
                for incident in incidents
            ]
            
            success, failed = helpers.bulk(
                self.client,
                actions,
                refresh=True
            )
            
            self.logger.info(f"Bulk indexing completed: {success} succeeded, {failed} failed")
            
            return {
                'success': success,
                'failed': failed,
                'total': len(incidents)
            }
            
        except Exception as e:
            self.logger.error(f"Bulk indexing failed: {str(e)}")
            raise
    
    def get_incident_count(self) -> int:
        """Get total count of incidents in index"""
        try:
            response = self.client.count(index=self.index_name)
            count = response['count']
            self.logger.info(f"Total incidents in database: {count}")
            return count
        except Exception as e:
            self.logger.error(f"Failed to get incident count: {str(e)}")
            return 0

# Singleton instance
_opensearch_client = None

def get_opensearch_client() -> OpenSearchClient:
    """Get or create OpenSearch client singleton"""
    global _opensearch_client
    if _opensearch_client is None:
        _opensearch_client = OpenSearchClient()
    return _opensearch_client
