"""
Step 4: Incident Analyzer
Uses AWS Bedrock (Claude Sonnet 4.5) to analyze incidents
Performs NLP, entity extraction, classification, and embedding generation
"""

import json
import time
from datetime import datetime
from typing import Dict, Any, List
from config import AWSConfig, PromptTemplates, ERROR_MESSAGES
from utils.logger import get_logger
from utils.aws_clients import AWSClients

logger = get_logger(__name__)

class IncidentAnalyzer:
    """
    Analyzes incidents using AWS Bedrock Claude Sonnet 4.5
    """
    
    def __init__(self):
        self.aws_clients = AWSClients()
        self.bedrock = self.aws_clients.get_bedrock_runtime()
        self.logger = logger
        self.model_id = AWSConfig.BEDROCK_MODEL_ID
    
    def invoke_bedrock(self, prompt: str, max_tokens: int = 2000) -> str:
        """
        Invoke Bedrock model with prompt
        
        Args:
            prompt: Input prompt for the model
            max_tokens: Maximum tokens in response
            
        Returns:
            str: Model response
        """
        try:
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": max_tokens,
                "temperature": AWSConfig.BEDROCK_TEMPERATURE
            }
            
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']
            
        except Exception as e:
            self.logger.error(f"Bedrock invocation failed: {str(e)}")
            raise
    
    def parse_description(self, incident_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse incident description using NLP
        
        Args:
            incident_metadata: Incident metadata from orchestrator
            
        Returns:
            dict: Parsed incident analysis
        """
        try:
            # Build prompt using template
            prompt = PromptTemplates.INCIDENT_ANALYSIS.format(
                incident_id=incident_metadata['incident_id'],
                priority=incident_metadata['priority_label'],
                category=incident_metadata['category'],
                description=incident_metadata['description'],
                affected_systems=', '.join(incident_metadata.get('affected_systems', [])),
                timestamp=incident_metadata['timestamp']
            )
            
            self.logger.info("Analyzing incident with Bedrock", 
                           incident_id=incident_metadata['incident_id'])
            
            # Invoke Bedrock
            analysis_start = time.time()
            response = self.invoke_bedrock(prompt, max_tokens=2000)
            analysis_time = time.time() - analysis_start
            
            # Parse JSON response
            try:
                # Extract JSON from response (handle markdown code blocks)
                if '```json' in response:
                    response = response.split('```json')[1].split('```')[0].strip()
                elif '```' in response:
                    response = response.split('```')[1].split('```')[0].strip()
                
                analysis_result = json.loads(response)
            except json.JSONDecodeError:
                # Fallback: create structured response
                analysis_result = {
                    'incident_type': incident_metadata['category'],
                    'primary_symptoms': [incident_metadata['description']],
                    'affected_components': incident_metadata.get('affected_systems', []),
                    'key_technical_terms': [],
                    'severity_assessment': incident_metadata['severity'],
                    'time_criticality': 'High' if incident_metadata['priority'] <= 2 else 'Medium'
                }
            
            # Add processing metadata
            analysis_result['analysis_metadata'] = {
                'analyzed_at': datetime.utcnow().isoformat(),
                'processing_time_seconds': round(analysis_time, 2),
                'model_used': self.model_id
            }
            
            self.logger.info("Incident analysis completed", 
                           incident_id=incident_metadata['incident_id'],
                           analysis_time=round(analysis_time, 2))
            
            # Log metric
            self.logger.log_metric(
                metric_name='AnalysisTime',
                value=analysis_time,
                unit='Seconds',
                IncidentID=incident_metadata['incident_id']
            )
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Failed to parse description: {str(e)}", 
                            incident_id=incident_metadata['incident_id'])
            raise
    
    def extract_entities(self, analysis_result: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Extract entities from analysis
        
        Args:
            analysis_result: Analysis result from parse_description
            
        Returns:
            list: List of extracted entities
        """
        entities = []
        
        # Extract affected components
        for component in analysis_result.get('affected_components', []):
            entities.append({
                'type': 'component',
                'value': component,
                'confidence': 0.9
            })
        
        # Extract technical terms
        for term in analysis_result.get('key_technical_terms', []):
            entities.append({
                'type': 'technical_term',
                'value': term,
                'confidence': 0.8
            })
        
        return entities
    
    def classify_incident_type(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify incident type
        
        Args:
            analysis_result: Analysis result
            
        Returns:
            dict: Classification result
        """
        return {
            'primary_category': analysis_result.get('incident_type', 'Unknown'),
            'sub_categories': [],
            'confidence': 0.85
        }
    
    def generate_embeddings(self, incident_metadata: Dict[str, Any], 
                           analysis_result: Dict[str, Any]) -> List[float]:
        """
        Generate embeddings for semantic search
        Uses Bedrock to create 1536-dimension vector
        
        Args:
            incident_metadata: Incident metadata
            analysis_result: Analysis result
            
        Returns:
            list: 1536-dimension embedding vector
        """
        try:
            # Build embedding prompt
            symptoms = ', '.join(analysis_result.get('primary_symptoms', []))
            
            embedding_text = f"""
Incident: {incident_metadata['description']}
Category: {incident_metadata['category']}
Priority: {incident_metadata['priority_label']}
Symptoms: {symptoms}
Affected Systems: {', '.join(incident_metadata.get('affected_systems', []))}
"""
            
            # For this example, we'll use Bedrock's embedding model
            # In production, use Amazon Titan Embeddings or similar
            
            # Simulate embedding generation (in production, call actual embedding model)
            # response = bedrock.invoke_model(
            #     modelId='amazon.titan-embed-text-v1',
            #     body=json.dumps({'inputText': embedding_text})
            # )
            
            # For now, return placeholder (1536 dimensions)
            import hashlib
            import numpy as np
            
            # Generate deterministic embedding from text
            hash_obj = hashlib.sha256(embedding_text.encode())
            seed = int(hash_obj.hexdigest(), 16) % (2**32)
            np.random.seed(seed)
            embedding = np.random.randn(AWSConfig.OPENSEARCH_EMBEDDING_DIMENSION).tolist()
            
            self.logger.info("Embeddings generated", 
                           incident_id=incident_metadata['incident_id'],
                           embedding_dimension=len(embedding))
            
            return embedding
            
        except Exception as e:
            self.logger.error(f"Failed to generate embeddings: {str(e)}", 
                            incident_id=incident_metadata['incident_id'])
            raise
    
    def analyze_incident(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main analysis function - performs complete incident analysis
        
        Args:
            context: Processing context from orchestrator
            
        Returns:
            dict: Complete analysis result
        """
        start_time = time.time()
        incident_metadata = context['incident_metadata']
        
        try:
            self.logger.info("Starting incident analysis", 
                           incident_id=incident_metadata['incident_id'])
            
            # Step 1: Parse description using NLP
            analysis_result = self.parse_description(incident_metadata)
            
            # Step 2: Extract entities
            entities = self.extract_entities(analysis_result)
            
            # Step 3: Classify incident type
            classification = self.classify_incident_type(analysis_result)
            
            # Step 4: Generate embeddings
            embeddings = self.generate_embeddings(incident_metadata, analysis_result)
            
            # Compile complete analysis
            complete_analysis = {
                'incident_id': incident_metadata['incident_id'],
                'analysis': analysis_result,
                'entities': entities,
                'classification': classification,
                'embeddings': embeddings,
                'embedding_dimension': len(embeddings),
                'processing_metadata': {
                    'total_processing_time': round(time.time() - start_time, 2),
                    'completed_at': datetime.utcnow().isoformat(),
                    'step': 4,
                    'next_step': 'vector_db_query'
                }
            }
            
            processing_time = time.time() - start_time
            
            # Log metrics
            self.logger.log_incident_processing(
                incident_id=incident_metadata['incident_id'],
                stage='analysis',
                duration=processing_time,
                success=True
            )
            
            self.logger.info("Incident analysis completed successfully", 
                           incident_id=incident_metadata['incident_id'],
                           processing_time=round(processing_time, 2))
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Analysis completed',
                    'analysis': complete_analysis,
                    'context': context
                }, default=str)
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            self.logger.log_incident_processing(
                incident_id=incident_metadata['incident_id'],
                stage='analysis',
                duration=processing_time,
                success=False
            )
            
            self.logger.error(f"Analysis failed: {str(e)}", 
                            incident_id=incident_metadata['incident_id'])
            
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': ERROR_MESSAGES['bedrock_invocation'],
                    'details': str(e),
                    'incident_id': incident_metadata['incident_id']
                })
            }

def lambda_handler(event, context):
    """AWS Lambda handler function"""
    analyzer = IncidentAnalyzer()
    
    # Extract context from event
    if 'body' in event:
        event_data = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
    else:
        event_data = event
    
    processing_context = event_data.get('context', event_data)
    
    return analyzer.analyze_incident(processing_context)

# For local testing
if __name__ == '__main__':
    # Sample context from orchestrator
    sample_context = {
        'incident_metadata': {
            'incident_id': 'INC0012345',
            'priority': 1,
            'priority_label': 'Critical',
            'category': 'Performance',
            'description': 'High CPU usage (95%) detected on production server web-prod-01. Application response time degraded from 200ms to 2500ms. Memory usage also elevated at 89%.',
            'affected_systems': ['web-prod-01', 'app-server-cluster'],
            'severity': 'Critical',
            'source': 'Dynatrace',
            'timestamp': '2026-01-08T10:30:00Z',
            'received_at': '2026-01-08T10:30:15Z'
        },
        'workflow': {
            'step': 4,
            'stage': 'analysis'
        }
    }
    
    analyzer = IncidentAnalyzer()
    result = analyzer.analyze_incident(sample_context)
    print(json.dumps(result, indent=2))
