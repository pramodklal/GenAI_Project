"""
Astra DB Helper - Data Access Layer for Healthcare Digital
Provides easy access to all collections with common query patterns
"""

import os
from typing import List, Dict, Optional, Any
from astrapy import DataAPIClient
from dotenv import load_dotenv
from datetime import datetime
import uuid

load_dotenv()

class AstraDBHelper:
    """Helper class for Astra DB operations"""
    
    def __init__(self):
        """Initialize connection to Astra DB"""
        token = os.getenv('ASTRA_DB_TOKEN')
        api_endpoint = os.getenv('ASTRA_DB_API_ENDPOINT')
        
        if not token or not api_endpoint:
            raise ValueError("Missing Astra DB credentials in .env file")
        
        self.client = DataAPIClient(token)
        self.db = self.client.get_database_by_api_endpoint(api_endpoint)
        
        # Initialize collections
        self.patients = self.db.get_collection('patients')
        self.dietary_profiles = self.db.get_collection('patient_dietary_profiles')
        self.menu_items = self.db.get_collection('menu_items')
        self.meal_orders = self.db.get_collection('meal_orders')
        self.evs_tasks = self.db.get_collection('evs_tasks')
        self.evs_staff = self.db.get_collection('evs_staff')
        self.agent_activities = self.db.get_collection('agent_activities')
        self.audit_logs = self.db.get_collection('system_audit_logs')
        self.inventory = self.db.get_collection('food_inventory')
        self.production = self.db.get_collection('production_schedules')
        self.preferences = self.db.get_collection('patient_preferences')
    
    # ===== PATIENT OPERATIONS =====
    
    def get_patient(self, patient_id: str) -> Optional[Dict]:
        """Get patient by ID"""
        return self.patients.find_one({"patient_id": patient_id})
    
    def get_all_patients(self, limit: int = 100) -> List[Dict]:
        """Get all patients"""
        return list(self.patients.find({}, limit=limit))
    
    def get_patients_by_room(self, room_number: str) -> List[Dict]:
        """Get patients in specific room"""
        return list(self.patients.find({"room_number": room_number}))
    
    def get_patient_dietary_profile(self, patient_id: str) -> Optional[Dict]:
        """Get dietary profile for patient"""
        return self.dietary_profiles.find_one({"patient_id": patient_id})
    
    def get_patient_preferences(self, patient_id: str) -> Optional[Dict]:
        """Get patient food preferences"""
        return self.preferences.find_one({"patient_id": patient_id})
    
    def create_patient(self, patient_data: Dict) -> str:
        """Create new patient"""
        patient_id = str(uuid.uuid4())
        patient_data['patient_id'] = patient_id
        patient_data['created_at'] = datetime.now().isoformat()
        patient_data['updated_at'] = datetime.now().isoformat()
        
        self.patients.insert_one(patient_data)
        return patient_id
    
    # ===== MENU OPERATIONS =====
    
    def get_menu_item(self, item_id: str) -> Optional[Dict]:
        """Get menu item by ID"""
        return self.menu_items.find_one({"item_id": item_id})
    
    def get_menu_items_by_category(self, category: str, limit: int = 50) -> List[Dict]:
        """Get menu items by category"""
        return list(self.menu_items.find({"category": category}, limit=limit))
    
    def get_menu_items_by_dietary_tags(self, tags: List[str], limit: int = 50) -> List[Dict]:
        """Get menu items matching dietary tags"""
        return list(self.menu_items.find(
            {"dietary_tags": {"$in": tags}},
            limit=limit
        ))
    
    def search_menu_items(self, filters: Dict, limit: int = 50) -> List[Dict]:
        """Search menu items with custom filters"""
        return list(self.menu_items.find(filters, limit=limit))
    
    def vector_search_menu_items(self, query_text: str, dietary_restrictions: List[str] = None, 
                                 allergies: List[str] = None, limit: int = 5) -> List[Dict]:
        """
        Semantic vector search for menu items
        
        Args:
            query_text: Natural language query (e.g., "healthy protein for diabetic patient")
            dietary_restrictions: List of dietary restrictions to filter by
            allergies: List of allergens to exclude
            limit: Maximum number of results
            
        Returns:
            List of menu items with similarity scores
        """
        try:
            # Generate embedding for query
            import os
            from openai import OpenAI
            
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            # Create embedding
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=query_text
            )
            query_embedding = response.data[0].embedding
            
            # Perform vector search
            results = self.menu_items.find(
                sort={"$vector": query_embedding},
                limit=limit * 3,  # Get more to filter
                projection={"*": True},
                include_similarity=True
            )
            
            # Filter results based on allergens (strict) and dietary restrictions (preferential)
            filtered_results = []
            for item in results:
                # Skip if contains allergens (strict exclusion)
                if allergies:
                    item_allergens = [a.lower() for a in item.get("allergens", [])]
                    if any(allergen.lower() in item_allergens for allergen in allergies):
                        continue
                
                # Add dietary match score for ranking
                if dietary_restrictions:
                    item_tags = [t.lower() for t in item.get("dietary_tags", [])]
                    matches = sum(1 for r in dietary_restrictions if r.lower() in item_tags)
                    item["_dietary_match_score"] = matches
                else:
                    item["_dietary_match_score"] = 0
                
                filtered_results.append(item)
            
            # Sort by dietary match score (higher is better) and similarity
            if dietary_restrictions:
                filtered_results.sort(
                    key=lambda x: (x.get("_dietary_match_score", 0), x.get("$similarity", 0)),
                    reverse=True
                )
            
            return filtered_results[:limit]
            
        except Exception as e:
            print(f"Vector search error: {e}")
            # Fallback to text search
            return self.search_menu_items({}, limit=limit)
    
    # ===== MEAL ORDER OPERATIONS =====
    
    def get_patient_orders(self, patient_id: str, limit: int = 20) -> List[Dict]:
        """Get all orders for a patient"""
        return list(self.meal_orders.find(
            {"patient_id": patient_id},
            limit=limit
        ))
    
    def get_orders_by_status(self, status: str, limit: int = 100) -> List[Dict]:
        """Get orders by status"""
        return list(self.meal_orders.find({"status": status}, limit=limit))
    
    def get_todays_orders(self, limit: int = 200) -> List[Dict]:
        """Get today's meal orders"""
        today = datetime.now().strftime("%Y-%m-%d")
        return list(self.meal_orders.find(
            {"order_date": today},
            limit=limit
        ))
    
    def create_meal_order(self, order_data: Dict) -> str:
        """Create new meal order"""
        order_id = str(uuid.uuid4())
        order_data['order_id'] = order_id
        order_data['created_at'] = datetime.now().isoformat()
        order_data['updated_at'] = datetime.now().isoformat()
        
        self.meal_orders.insert_one(order_data)
        return order_id
    
    def update_order_status(self, order_id: str, status: str, notes: str = None) -> bool:
        """Update order status"""
        update_data = {
            "status": status,
            "updated_at": datetime.now().isoformat()
        }
        if notes:
            update_data["validation_notes"] = notes
        
        result = self.meal_orders.update_one(
            {"order_id": order_id},
            {"$set": update_data}
        )
        return result.update_info.get('updated_count', 0) > 0
    
    # ===== EVS OPERATIONS =====
    
    def get_evs_tasks(self, status: str = None, limit: int = 100) -> List[Dict]:
        """Get EVS tasks with optional status filter"""
        if status:
            return list(self.evs_tasks.find({"status": status}, limit=limit))
        return list(self.evs_tasks.find({}, limit=limit))
    
    def get_evs_tasks_by_status(self, status: str, limit: int = 50) -> List[Dict]:
        """Get EVS tasks by status"""
        return list(self.evs_tasks.find({"status": status}, limit=limit))
    
    def get_evs_tasks_by_location(self, location: str, limit: int = 50) -> List[Dict]:
        """Get EVS tasks by location"""
        return list(self.evs_tasks.find({"location": location}, limit=limit))
    
    def get_available_evs_staff(self) -> List[Dict]:
        """Get available EVS staff"""
        return list(self.evs_staff.find({
            "status": "active",
            "availability_status": "available"
        }))
    
    def get_evs_staff_by_shift(self, shift: str) -> List[Dict]:
        """Get EVS staff by shift"""
        return list(self.evs_staff.find({"shift": shift}))
    
    def create_evs_task(self, task_data: Dict) -> str:
        """Create new EVS task"""
        task_id = str(uuid.uuid4())
        task_data['task_id'] = task_id
        task_data['created_at'] = datetime.now().isoformat()
        task_data['updated_at'] = datetime.now().isoformat()
        
        self.evs_tasks.insert_one(task_data)
        return task_id
    
    def update_evs_task(self, task_id: str, update_data: Dict) -> bool:
        """Update EVS task"""
        update_data['updated_at'] = datetime.now().isoformat()
        
        result = self.evs_tasks.update_one(
            {"task_id": task_id},
            {"$set": update_data}
        )
        return result.update_info.get('updated_count', 0) > 0
    
    # ===== INVENTORY OPERATIONS =====
    
    def get_low_inventory_items(self, threshold: Optional[int] = None) -> List[Dict]:
        """Get inventory items below reorder level or all items if threshold is high"""
        items = list(self.inventory.find({}, limit=1000))
        if threshold and threshold >= 1000:
            # Return all items if threshold is very high
            return items
        return [
            item for item in items 
            if item.get('quantity', 0) <= item.get('reorder_level', 0)
        ]
    
    def get_inventory_item(self, ingredient_id: str) -> Optional[Dict]:
        """Get inventory item by ID"""
        return self.inventory.find_one({"ingredient_id": ingredient_id})
    
    def get_inventory_by_category(self, category: str) -> List[Dict]:
        """Get inventory items by category"""
        return list(self.inventory.find({"category": category}, limit=100))
    
    # ===== PRODUCTION OPERATIONS =====
    
    def get_production_schedule(self, date: str, meal_type: str = None) -> List[Dict]:
        """Get production schedule for date"""
        filter_query = {"date": date}
        if meal_type:
            filter_query["meal_type"] = meal_type
        
        return list(self.production.find(filter_query, limit=10))
    
    def create_production_schedule(self, schedule_data: Dict) -> str:
        """Create production schedule"""
        schedule_id = str(uuid.uuid4())
        schedule_data['schedule_id'] = schedule_id
        schedule_data['created_at'] = datetime.now().isoformat()
        schedule_data['updated_at'] = datetime.now().isoformat()
        
        self.production.insert_one(schedule_data)
        return schedule_id
    
    # ===== AGENT ACTIVITY LOGGING =====
    
    def log_agent_activity(self, agent_name: str, action_type: str, 
                          input_data: Any, output_data: Any, 
                          success: bool = True, error_message: str = None,
                          execution_time_ms: int = 0) -> str:
        """Log agent activity"""
        activity_id = str(uuid.uuid4())
        
        activity = {
            "activity_id": activity_id,
            "agent_name": agent_name,
            "action_type": action_type,
            "timestamp": datetime.now().isoformat(),
            "input_data": str(input_data),
            "output_data": str(output_data),
            "success": success,
            "error_message": error_message,
            "execution_time_ms": execution_time_ms
        }
        
        self.agent_activities.insert_one(activity)
        return activity_id
    
    # ===== AUDIT LOGGING =====
    
    def log_audit(self, resource_type: str, resource_id: str, 
                  user_id: str, action: str, 
                  action_details: str = None, 
                  success: bool = True) -> str:
        """Log audit trail for HIPAA compliance"""
        log_id = str(uuid.uuid4())
        
        audit_log = {
            "log_id": log_id,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "user_id": user_id,
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "action_details": action_details,
            "success": success
        }
        
        self.audit_logs.insert_one(audit_log)
        return log_id
    
    # ===== VALIDATION HELPERS =====
    
    def validate_meal_for_patient(self, patient_id: str, menu_item_id: str) -> Dict:
        """Validate if meal is safe for patient"""
        patient = self.get_patient(patient_id)
        dietary_profile = self.get_patient_dietary_profile(patient_id)
        menu_item = self.get_menu_item(menu_item_id)
        
        if not patient or not menu_item:
            return {"valid": False, "reason": "Patient or menu item not found"}
        
        warnings = []
        
        # Check allergens
        patient_allergies = patient.get('allergies', [])
        menu_allergens = menu_item.get('allergens', [])
        
        for allergen in menu_allergens:
            if allergen in patient_allergies:
                warnings.append(f"ALLERGEN ALERT: {allergen}")
        
        # Check dietary restrictions
        patient_restrictions = patient.get('dietary_restrictions', [])
        menu_tags = menu_item.get('dietary_tags', [])
        
        # Simple validation - can be enhanced with more complex rules
        if 'low-sodium' in patient_restrictions:
            if menu_item.get('sodium_mg', 0) > 500:
                warnings.append("High sodium content")
        
        if 'diabetic' in patient_restrictions:
            if menu_item.get('sugar_g', 0) > 15:
                warnings.append("High sugar content")
        
        if 'low-fat' in patient_restrictions:
            if menu_item.get('fat_g', 0) > 15:
                warnings.append("High fat content")
        
        return {
            "valid": len([w for w in warnings if 'ALLERGEN' in w]) == 0,
            "warnings": warnings,
            "patient": patient.get('name'),
            "menu_item": menu_item.get('name')
        }

# Global instance
_db_helper = None

def get_db_helper() -> AstraDBHelper:
    """Get or create AstraDB helper singleton"""
    global _db_helper
    if _db_helper is None:
        _db_helper = AstraDBHelper()
    return _db_helper
