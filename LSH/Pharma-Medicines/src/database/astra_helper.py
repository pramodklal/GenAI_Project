"""
Pharma Manufacturing - Astra DB Helper
Handles all database operations for the pharmaceutical manufacturing system.
"""

import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from astrapy import DataAPIClient
from dotenv import load_dotenv
import uuid
import logging

# Load environment variables from root .env file
from pathlib import Path
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)


class AstraDBHelper:
    """Singleton helper class for Astra DB operations."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AstraDBHelper, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.token = os.getenv("ASTRA_DB_TOKEN_MMD")
        self.api_endpoint = os.getenv("ASTRA_DB_API_ENDPOINT_MMD")
        self.keyspace = os.getenv("ASTRA_DB_KEYSPACE_MMD", "medicines_manufacture")
        
        if not self.token or not self.api_endpoint:
            raise ValueError("ASTRA_DB_TOKEN_MMD and ASTRA_DB_API_ENDPOINT_MMD must be set in .env file")
        
        # Initialize client
        self.client = DataAPIClient(self.token)
        self.db = self.client.get_database(self.api_endpoint)
        
        # Initialize collections
        self._init_collections()
        
        self._initialized = True
        logger.info("AstraDBHelper initialized successfully")
    
    def _init_collections(self):
        """Initialize all collection references."""
        # Regular collections
        self.medicines = self.db.get_collection("medicines")
        self.manufacturing_batches = self.db.get_collection("manufacturing_batches")
        self.raw_materials = self.db.get_collection("raw_materials")
        self.quality_control_tests = self.db.get_collection("quality_control_tests")
        self.production_schedules = self.db.get_collection("production_schedules")
        self.regulatory_documents = self.db.get_collection("regulatory_documents")
        self.audit_logs = self.db.get_collection("audit_logs")
        
        # Vector collections
        self.formulations = self.db.get_collection("formulations")
        self.adverse_events = self.db.get_collection("adverse_events")
        self.sop_documents = self.db.get_collection("sop_documents")
    
    # ===================== MEDICINE OPERATIONS =====================
    
    def get_medicine(self, medicine_id: str) -> Optional[Dict]:
        """Get medicine by ID."""
        try:
            result = self.medicines.find_one({"medicine_id": medicine_id})
            return result
        except Exception as e:
            logger.error(f"Error getting medicine {medicine_id}: {str(e)}")
            return None
    
    def search_medicines(self, name: str = None, category: str = None) -> List[Dict]:
        """Search medicines by name or category."""
        try:
            query = {}
            if name:
                query["name"] = {"$regex": name, "$options": "i"}
            if category:
                query["category"] = category
            
            results = list(self.medicines.find(query, limit=50))
            return results
        except Exception as e:
            logger.error(f"Error searching medicines: {str(e)}")
            return []
    
    def create_medicine(self, medicine_data: Dict) -> str:
        """Create new medicine record."""
        try:
            medicine_id = str(uuid.uuid4())
            medicine_data["medicine_id"] = medicine_id
            medicine_data["created_at"] = datetime.utcnow().isoformat()
            
            self.medicines.insert_one(medicine_data)
            self._log_audit("create", "medicine", medicine_id, None, medicine_data)
            
            return medicine_id
        except Exception as e:
            logger.error(f"Error creating medicine: {str(e)}")
            raise
    
    def update_medicine_status(self, medicine_id: str, status: str) -> bool:
        """Update medicine status."""
        try:
            old_value = self.get_medicine(medicine_id)
            result = self.medicines.update_one(
                {"medicine_id": medicine_id},
                {"$set": {"status": status, "updated_at": datetime.utcnow().isoformat()}}
            )
            
            if result.update_info["updatedExisting"]:
                self._log_audit("update", "medicine", medicine_id, old_value, {"status": status})
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating medicine status: {str(e)}")
            return False
    
    # ===================== FORMULATION OPERATIONS (Vector) =====================
    
    def get_formulation(self, medicine_id: str) -> Optional[Dict]:
        """Get formulation for a medicine."""
        try:
            result = self.formulations.find_one({"medicine_id": medicine_id})
            return result
        except Exception as e:
            logger.error(f"Error getting formulation: {str(e)}")
            return None
    
    def vector_search_formulations(self, query_vector: List[float], limit: int = 5) -> List[Dict]:
        """Vector search for similar formulations."""
        try:
            results = list(self.formulations.find(
                {},
                sort={"$vector": query_vector},
                limit=limit,
                projection={"$vector": 0}
            ))
            return results
        except Exception as e:
            logger.error(f"Error in vector search formulations: {str(e)}")
            return []
    
    # ===================== BATCH OPERATIONS =====================
    
    def create_batch(self, batch_data: Dict) -> str:
        """Create new manufacturing batch."""
        try:
            batch_id = str(uuid.uuid4())
            batch_data["batch_id"] = batch_id
            batch_data["created_at"] = datetime.utcnow().isoformat()
            batch_data["status"] = batch_data.get("status", "in_progress")
            batch_data["stage"] = batch_data.get("stage", "mixing")
            
            self.manufacturing_batches.insert_one(batch_data)
            self._log_audit("create", "batch", batch_id, None, batch_data)
            
            return batch_id
        except Exception as e:
            logger.error(f"Error creating batch: {str(e)}")
            raise
    
    def get_batch(self, batch_id: str) -> Optional[Dict]:
        """Get batch by ID."""
        try:
            result = self.manufacturing_batches.find_one({"batch_id": batch_id})
            return result
        except Exception as e:
            logger.error(f"Error getting batch: {str(e)}")
            return None
    
    def update_batch_stage(self, batch_id: str, stage: str) -> bool:
        """Update batch manufacturing stage."""
        try:
            old_value = self.get_batch(batch_id)
            result = self.manufacturing_batches.update_one(
                {"batch_id": batch_id},
                {"$set": {"stage": stage, "updated_at": datetime.utcnow().isoformat()}}
            )
            
            if result.update_info["updatedExisting"]:
                self._log_audit("update", "batch", batch_id, old_value, {"stage": stage})
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating batch stage: {str(e)}")
            return False
    
    def update_batch_status(self, batch_id: str, status: str, approved_by: str = None) -> bool:
        """Update batch status (e.g., approved, rejected)."""
        try:
            old_value = self.get_batch(batch_id)
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow().isoformat()
            }
            if approved_by:
                update_data["approved_by"] = approved_by
                update_data["approved_date"] = datetime.utcnow().isoformat()
            
            result = self.manufacturing_batches.update_one(
                {"batch_id": batch_id},
                {"$set": update_data}
            )
            
            if result.update_info["updatedExisting"]:
                self._log_audit("update", "batch", batch_id, old_value, update_data)
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating batch status: {str(e)}")
            return False
    
    def get_batches_by_status(self, status: str) -> List[Dict]:
        """Get batches by status."""
        try:
            results = list(self.manufacturing_batches.find({"status": status}, limit=100))
            return results
        except Exception as e:
            logger.error(f"Error getting batches by status: {str(e)}")
            return []
    
    # ===================== QUALITY CONTROL OPERATIONS =====================
    
    def submit_qc_test(self, test_data: Dict) -> str:
        """Submit QC test results."""
        try:
            test_id = str(uuid.uuid4())
            test_data["test_id"] = test_id
            test_data["test_date"] = test_data.get("test_date", datetime.utcnow().isoformat())
            
            self.quality_control_tests.insert_one(test_data)
            self._log_audit("create", "qc_test", test_id, None, test_data)
            
            return test_id
        except Exception as e:
            logger.error(f"Error submitting QC test: {str(e)}")
            raise
    
    def get_qc_tests(self, batch_id: str) -> List[Dict]:
        """Get all QC tests for a batch."""
        try:
            results = list(self.quality_control_tests.find({"batch_id": batch_id}))
            return results
        except Exception as e:
            logger.error(f"Error getting QC tests: {str(e)}")
            return []
    
    def get_oos_tests(self, batch_id: str = None) -> List[Dict]:
        """Get out-of-specification test results."""
        try:
            query = {"pass_fail_status": "fail"}
            if batch_id:
                query["batch_id"] = batch_id
            
            results = list(self.quality_control_tests.find(query, limit=50))
            return results
        except Exception as e:
            logger.error(f"Error getting OOS tests: {str(e)}")
            return []
    
    # ===================== PRODUCTION SCHEDULE OPERATIONS =====================
    
    def create_schedule(self, schedule_data: Dict) -> str:
        """Create production schedule."""
        try:
            schedule_id = str(uuid.uuid4())
            schedule_data["schedule_id"] = schedule_id
            schedule_data["created_at"] = datetime.utcnow().isoformat()
            
            self.production_schedules.insert_one(schedule_data)
            return schedule_id
        except Exception as e:
            logger.error(f"Error creating schedule: {str(e)}")
            raise
    
    def get_schedule_by_date(self, start_date: str, end_date: str) -> List[Dict]:
        """Get production schedules within date range."""
        try:
            results = list(self.production_schedules.find({
                "scheduled_date": {"$gte": start_date, "$lte": end_date}
            }))
            return results
        except Exception as e:
            logger.error(f"Error getting schedules: {str(e)}")
            return []
    
    # ===================== INVENTORY OPERATIONS =====================
    
    def get_material(self, material_id: str) -> Optional[Dict]:
        """Get raw material by ID."""
        try:
            result = self.raw_materials.find_one({"material_id": material_id})
            return result
        except Exception as e:
            logger.error(f"Error getting material: {str(e)}")
            return None
    
    def get_low_stock_materials(self, threshold: float = None) -> List[Dict]:
        """Get materials below reorder level."""
        try:
            query = {}
            if threshold:
                query["quantity_on_hand"] = {"$lt": threshold}
            else:
                # Materials where quantity < reorder level
                query = {"$expr": {"$lt": ["$quantity_on_hand", "$reorder_level"]}}
            
            results = list(self.raw_materials.find(query))
            return results
        except Exception as e:
            logger.error(f"Error getting low stock materials: {str(e)}")
            return []
    
    def update_material_quantity(self, material_id: str, quantity: float, 
                                 transaction_type: str) -> bool:
        """Update material quantity (add/subtract)."""
        try:
            old_value = self.get_material(material_id)
            if not old_value:
                return False
            
            current_qty = old_value.get("quantity_on_hand", 0)
            new_qty = current_qty + quantity if transaction_type == "add" else current_qty - quantity
            
            result = self.raw_materials.update_one(
                {"material_id": material_id},
                {"$set": {
                    "quantity_on_hand": new_qty,
                    "last_updated": datetime.utcnow().isoformat()
                }}
            )
            
            if result.update_info["updatedExisting"]:
                self._log_audit("update", "material", material_id, old_value, 
                              {"quantity_on_hand": new_qty, "transaction_type": transaction_type})
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating material quantity: {str(e)}")
            return False
    
    def get_expiring_materials(self, days: int) -> List[Dict]:
        """Get materials expiring within specified days."""
        try:
            expiry_date = (datetime.utcnow() + timedelta(days=days)).isoformat()
            results = list(self.raw_materials.find({
                "expiry_date": {"$lte": expiry_date}
            }))
            return results
        except Exception as e:
            logger.error(f"Error getting expiring materials: {str(e)}")
            return []
    
    # ===================== SUPPLIER OPERATIONS =====================
    
    def get_supplier(self, supplier_id: str) -> Optional[Dict]:
        """Get supplier by ID."""
        try:
            result = self.suppliers.find_one({"supplier_id": supplier_id})
            return result
        except Exception as e:
            logger.error(f"Error getting supplier: {str(e)}")
            return None
    
    def get_active_suppliers(self) -> List[Dict]:
        """Get all active suppliers."""
        try:
            results = list(self.suppliers.find({"status": "active"}))
            return results
        except Exception as e:
            logger.error(f"Error getting active suppliers: {str(e)}")
            return []
    
    # ===================== PURCHASE ORDER OPERATIONS =====================
    
    def create_purchase_order(self, po_data: Dict) -> str:
        """Create purchase order."""
        try:
            po_id = str(uuid.uuid4())
            po_data["po_id"] = po_id
            po_data["order_date"] = datetime.utcnow().isoformat()
            po_data["status"] = po_data.get("status", "pending")
            
            self.purchase_orders.insert_one(po_data)
            self._log_audit("create", "purchase_order", po_id, None, po_data)
            
            return po_id
        except Exception as e:
            logger.error(f"Error creating purchase order: {str(e)}")
            raise
    
    # ===================== EQUIPMENT OPERATIONS =====================
    
    def get_equipment(self, equipment_id: str) -> Optional[Dict]:
        """Get equipment by ID."""
        try:
            result = self.equipment_maintenance.find_one({"equipment_id": equipment_id})
            return result
        except Exception as e:
            logger.error(f"Error getting equipment: {str(e)}")
            return None
    
    def get_operational_equipment(self) -> List[Dict]:
        """Get all operational equipment."""
        try:
            results = list(self.equipment_maintenance.find({"status": "operational"}))
            return results
        except Exception as e:
            logger.error(f"Error getting operational equipment: {str(e)}")
            return []
    
    def get_maintenance_due(self, days: int) -> List[Dict]:
        """Get equipment with maintenance due within specified days."""
        try:
            due_date = (datetime.utcnow() + timedelta(days=days)).isoformat()
            results = list(self.equipment_maintenance.find({
                "next_maintenance_date": {"$lte": due_date}
            }))
            return results
        except Exception as e:
            logger.error(f"Error getting maintenance due: {str(e)}")
            return []
    
    # ===================== REGULATORY DOCUMENT OPERATIONS =====================
    
    def get_regulatory_documents(self, medicine_id: str = None, 
                                  document_type: str = None) -> List[Dict]:
        """Get regulatory documents with optional filters."""
        try:
            query = {}
            if medicine_id:
                query["medicine_id"] = medicine_id
            if document_type:
                query["document_type"] = document_type
            
            results = list(self.regulatory_documents.find(query))
            return results
        except Exception as e:
            logger.error(f"Error getting regulatory documents: {str(e)}")
            return []
    
    def get_expiring_documents(self, days: int) -> List[Dict]:
        """Get documents expiring within specified days."""
        try:
            expiry_date = (datetime.utcnow() + timedelta(days=days)).isoformat()
            results = list(self.regulatory_documents.find({
                "expiry_date": {"$lte": expiry_date},
                "status": "active"
            }))
            return results
        except Exception as e:
            logger.error(f"Error getting expiring documents: {str(e)}")
            return []
    
    # ===================== ADVERSE EVENT OPERATIONS (Vector) =====================
    
    def submit_adverse_event(self, ae_data: Dict, vector: List[float] = None) -> str:
        """Submit adverse event report with optional vector embedding."""
        try:
            ae_id = str(uuid.uuid4())
            ae_data["ae_id"] = ae_id
            ae_data["report_date"] = ae_data.get("report_date", datetime.utcnow().isoformat())
            
            if vector:
                ae_data["$vector"] = vector
            
            self.adverse_events.insert_one(ae_data)
            self._log_audit("create", "adverse_event", ae_id, None, ae_data)
            
            return ae_id
        except Exception as e:
            logger.error(f"Error submitting adverse event: {str(e)}")
            raise
    
    def vector_search_adverse_events(self, query_vector: List[float], 
                                     limit: int = 10) -> List[Dict]:
        """Vector search for similar adverse events."""
        try:
            results = list(self.adverse_events.find(
                {},
                sort={"$vector": query_vector},
                limit=limit,
                projection={"$vector": 0}
            ))
            return results
        except Exception as e:
            logger.error(f"Error in vector search adverse events: {str(e)}")
            return []
    
    # ===================== SOP DOCUMENT OPERATIONS (Vector) =====================
    
    def vector_search_sops(self, query_vector: List[float], limit: int = 5) -> List[Dict]:
        """Vector search for relevant SOPs."""
        try:
            results = list(self.sop_documents.find(
                {},
                sort={"$vector": query_vector},
                limit=limit,
                projection={"$vector": 0}
            ))
            return results
        except Exception as e:
            logger.error(f"Error in vector search SOPs: {str(e)}")
            return []
    
    # ===================== AUDIT LOG OPERATIONS =====================
    
    def _log_audit(self, action: str, entity_type: str, entity_id: str, 
                   old_value: Any, new_value: Any):
        """Internal method to log audit trail."""
        try:
            audit_data = {
                "log_id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": "system",  # TODO: Get from session context
                "action": action,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "old_value": old_value,
                "new_value": new_value,
                "compliance_category": "GMP"
            }
            
            self.audit_logs.insert_one(audit_data)
        except Exception as e:
            logger.error(f"Error logging audit: {str(e)}")
    
    def get_audit_logs(self, start_date: str, end_date: str, 
                       entity_type: str = None) -> List[Dict]:
        """Get audit logs within date range."""
        try:
            query = {
                "timestamp": {"$gte": start_date, "$lte": end_date}
            }
            if entity_type:
                query["entity_type"] = entity_type
            
            results = list(self.audit_logs.find(query).sort("timestamp", -1).limit(1000))
            return results
        except Exception as e:
            logger.error(f"Error getting audit logs: {str(e)}")
            return []
    
    # ===================== UTILITY OPERATIONS =====================
    
    def get_collection_names(self) -> List[str]:
        """Get list of all collection names in the database."""
        try:
            collections = self.db.list_collection_names()
            return list(collections)
        except Exception as e:
            logger.error(f"Error getting collection names: {str(e)}")
            return []


# Singleton instance getter
def get_db_helper() -> AstraDBHelper:
    """Get AstraDBHelper singleton instance."""
    return AstraDBHelper()
