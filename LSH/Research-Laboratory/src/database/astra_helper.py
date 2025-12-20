"""
Astra DB Helper for Medicines Research Laboratory
Manages database connections and operations for research activities
Keyspace: medicines_research
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
from dotenv import load_dotenv
from astrapy import DataAPIClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AstraDBHelper:
    """Singleton class for Astra DB operations - Medicines Research Laboratory"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AstraDBHelper, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        # Load environment variables from root .env file
        env_path = Path(__file__).parent.parent.parent.parent / ".env"
        load_dotenv(dotenv_path=env_path)
        
        # Get credentials with _MRL suffix for Medicines Research Laboratory
        self.token = os.getenv("ASTRA_DB_TOKEN_MRL")
        self.api_endpoint = os.getenv("ASTRA_DB_API_ENDPOINT_MRL")
        self.keyspace = os.getenv("ASTRA_DB_KEYSPACE_MRL", "medicines_research")
        
        if not self.token or not self.api_endpoint:
            raise ValueError(
                "Missing Astra DB credentials. Please set ASTRA_DB_TOKEN_MRL and "
                "ASTRA_DB_API_ENDPOINT_MRL in .env file"
            )
        
        # Initialize client
        self.client = DataAPIClient(self.token)
        self.db = self.client.get_database(self.api_endpoint)
        
        logger.info(f"✅ Connected to Astra DB - Medicines Research Laboratory")
        logger.info(f"📊 Keyspace: {self.keyspace}")
        
        # Initialize collections
        self._init_collections()
        self._initialized = True
    
    def _init_collections(self):
        """Initialize collection references for research laboratory"""
        try:
            # Regular collections (Research-focused)
            self.research_projects = self.db.get_collection("research_projects")
            self.clinical_trials = self.db.get_collection("clinical_trials")
            self.drug_candidates = self.db.get_collection("drug_candidates")
            self.lab_experiments = self.db.get_collection("lab_experiments")
            self.research_compounds = self.db.get_collection("research_compounds")
            self.trial_participants = self.db.get_collection("trial_participants")
            self.research_publications = self.db.get_collection("research_publications")
            
            # Vector-enabled collections
            self.molecular_structures = self.db.get_collection("molecular_structures")
            self.research_papers = self.db.get_collection("research_papers")
            self.patent_documents = self.db.get_collection("patent_documents")
            
            logger.info("✅ Collections initialized (7 regular + 3 vector)")
            
        except Exception as e:
            logger.error(f"Error initializing collections: {str(e)}")
            raise
    
    def get_collection_names(self) -> List[str]:
        """Get list of all collection names in the database"""
        try:
            collections = self.db.list_collection_names()
            return list(collections)
        except Exception as e:
            logger.error(f"Error getting collection names: {str(e)}")
            return []
    
    def create_collection(self, name: str, vector_enabled: bool = False) -> bool:
        """Create a new collection"""
        try:
            if vector_enabled:
                # Vector-enabled collection for embeddings
                self.db.create_collection(name)
            else:
                # Regular collection
                self.db.create_collection(name)
            logger.info(f"✅ Created collection: {name}")
            return True
        except Exception as e:
            logger.error(f"Error creating collection {name}: {str(e)}")
            return False
    
    def delete_collection(self, name: str) -> bool:
        """Delete a collection"""
        try:
            self.db.drop_collection(name)
            logger.info(f"🗑️ Deleted collection: {name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection {name}: {str(e)}")
            return False
    
    # Research Projects Operations
    def create_research_project(self, project_data: Dict[str, Any]) -> Optional[str]:
        """Create a new research project"""
        try:
            project_data["created_at"] = datetime.utcnow().isoformat()
            project_data["updated_at"] = datetime.utcnow().isoformat()
            result = self.research_projects.insert_one(project_data)
            logger.info(f"✅ Created research project: {project_data.get('project_name')}")
            return str(result.inserted_id) if hasattr(result, 'inserted_id') else None
        except Exception as e:
            logger.error(f"Error creating research project: {str(e)}")
            return None
    
    def get_research_projects(self, filter_dict: Dict = None, limit: int = 100) -> List[Dict]:
        """Get research projects with optional filters"""
        try:
            filter_dict = filter_dict or {}
            projects = list(self.research_projects.find(filter_dict, limit=limit))
            return projects
        except Exception as e:
            logger.error(f"Error getting research projects: {str(e)}")
            return []
    
    # Clinical Trials Operations
    def create_clinical_trial(self, trial_data: Dict[str, Any]) -> Optional[str]:
        """Create a new clinical trial"""
        try:
            trial_data["created_at"] = datetime.utcnow().isoformat()
            trial_data["updated_at"] = datetime.utcnow().isoformat()
            result = self.clinical_trials.insert_one(trial_data)
            logger.info(f"✅ Created clinical trial: {trial_data.get('trial_id')}")
            return str(result.inserted_id) if hasattr(result, 'inserted_id') else None
        except Exception as e:
            logger.error(f"Error creating clinical trial: {str(e)}")
            return None
    
    def get_clinical_trials(self, filter_dict: Dict = None, limit: int = 100) -> List[Dict]:
        """Get clinical trials with optional filters"""
        try:
            filter_dict = filter_dict or {}
            trials = list(self.clinical_trials.find(filter_dict, limit=limit))
            return trials
        except Exception as e:
            logger.error(f"Error getting clinical trials: {str(e)}")
            return []
    
    # Drug Candidates Operations
    def create_drug_candidate(self, candidate_data: Dict[str, Any]) -> Optional[str]:
        """Create a new drug candidate"""
        try:
            candidate_data["created_at"] = datetime.utcnow().isoformat()
            candidate_data["updated_at"] = datetime.utcnow().isoformat()
            result = self.drug_candidates.insert_one(candidate_data)
            logger.info(f"✅ Created drug candidate: {candidate_data.get('compound_name')}")
            return str(result.inserted_id) if hasattr(result, 'inserted_id') else None
        except Exception as e:
            logger.error(f"Error creating drug candidate: {str(e)}")
            return None
    
    def get_drug_candidates(self, filter_dict: Dict = None, limit: int = 100) -> List[Dict]:
        """Get drug candidates with optional filters"""
        try:
            filter_dict = filter_dict or {}
            candidates = list(self.drug_candidates.find(filter_dict, limit=limit))
            return candidates
        except Exception as e:
            logger.error(f"Error getting drug candidates: {str(e)}")
            return []
    
    # Lab Experiments Operations
    def create_lab_experiment(self, experiment_data: Dict[str, Any]) -> Optional[str]:
        """Create a new lab experiment"""
        try:
            experiment_data["created_at"] = datetime.utcnow().isoformat()
            experiment_data["updated_at"] = datetime.utcnow().isoformat()
            result = self.lab_experiments.insert_one(experiment_data)
            logger.info(f"✅ Created lab experiment: {experiment_data.get('experiment_id')}")
            return str(result.inserted_id) if hasattr(result, 'inserted_id') else None
        except Exception as e:
            logger.error(f"Error creating lab experiment: {str(e)}")
            return None
    
    def get_lab_experiments(self, filter_dict: Dict = None, limit: int = 100) -> List[Dict]:
        """Get lab experiments with optional filters"""
        try:
            filter_dict = filter_dict or {}
            experiments = list(self.lab_experiments.find(filter_dict, limit=limit))
            return experiments
        except Exception as e:
            logger.error(f"Error getting lab experiments: {str(e)}")
            return []
    
    # Vector Search Operations
    def search_similar_molecules(self, query_vector: List[float], limit: int = 10) -> List[Dict]:
        """Search for similar molecular structures using vector search"""
        try:
            results = list(self.molecular_structures.find(
                {},
                sort={"$vector": query_vector},
                limit=limit
            ))
            return results
        except Exception as e:
            logger.error(f"Error searching similar molecules: {str(e)}")
            return []
    
    def search_research_papers(self, query_vector: List[float], limit: int = 10) -> List[Dict]:
        """Search for similar research papers using vector search"""
        try:
            results = list(self.research_papers.find(
                {},
                sort={"$vector": query_vector},
                limit=limit
            ))
            return results
        except Exception as e:
            logger.error(f"Error searching research papers: {str(e)}")
            return []
    
    def search_patents(self, query_vector: List[float], limit: int = 10) -> List[Dict]:
        """Search for similar patents using vector search"""
        try:
            results = list(self.patent_documents.find(
                {},
                sort={"$vector": query_vector},
                limit=limit
            ))
            return results
        except Exception as e:
            logger.error(f"Error searching patents: {str(e)}")
            return []
    
    # Generic Operations
    def insert_document(self, collection_name: str, document: Dict[str, Any]) -> bool:
        """Insert a document into specified collection"""
        try:
            # Get or create collection
            try:
                collection = self.db.get_collection(collection_name)
            except Exception:
                # Collection doesn't exist, create it
                logger.info(f"Creating collection: {collection_name}")
                # Check if it's a vector collection
                vector_collections = ["molecular_structures", "research_papers", "patent_documents"]
                if collection_name in vector_collections:
                    collection = self.db.create_collection(
                        name=collection_name,
                        dimension=1536,
                        metric="cosine"
                    )
                else:
                    collection = self.db.create_collection(name=collection_name)
            
            document["created_at"] = datetime.utcnow().isoformat()
            collection.insert_one(document)
            logger.info(f"✅ Inserted document into {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error inserting document into {collection_name}: {str(e)}")
            return False
    
    def update_document(self, collection_name: str, filter_dict: Dict, update_dict: Dict) -> bool:
        """Update a document in specified collection"""
        try:
            collection = self.db.get_collection(collection_name)
            update_dict["updated_at"] = datetime.utcnow().isoformat()
            collection.update_one(filter_dict, {"$set": update_dict})
            logger.info(f"✅ Updated document in {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error updating document: {str(e)}")
            return False
    
    def delete_document(self, collection_name: str, filter_dict: Dict) -> bool:
        """Delete a document from specified collection"""
        try:
            collection = self.db.get_collection(collection_name)
            collection.delete_one(filter_dict)
            logger.info(f"🗑️ Deleted document from {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            return False
    
    def query_documents(self, collection_name: str, filter_dict: Dict = None, limit: int = 100) -> List[Dict]:
        """Query documents from specified collection"""
        try:
            collection = self.db.get_collection(collection_name)
            filter_dict = filter_dict or {}
            docs = list(collection.find(filter_dict, limit=limit))
            return docs
        except Exception as e:
            logger.error(f"Error querying documents: {str(e)}")
            return []
    
    def vector_search(self, collection_name: str, query_vector: List[float], limit: int = 10) -> List[Dict]:
        """Perform vector similarity search on specified collection"""
        try:
            collection = self.db.get_collection(collection_name)
            results = list(collection.find(
                {},
                sort={"$vector": query_vector},
                limit=limit
            ))
            return results
        except Exception as e:
            logger.error(f"Error performing vector search: {str(e)}")
            return []
    
    def get_collection_stats(self) -> Dict[str, int]:
        """Get document counts for all collections"""
        stats = {}
        collections = [
            "research_projects", "clinical_trials", "drug_candidates",
            "lab_experiments", "research_compounds", "trial_participants",
            "research_publications", "molecular_structures", "research_papers",
            "patent_documents"
        ]
        
        for coll_name in collections:
            try:
                collection = self.db.get_collection(coll_name)
                count = collection.count_documents({})
                stats[coll_name] = count
            except:
                stats[coll_name] = 0
        
        return stats


# Singleton instance
db = AstraDBHelper()
