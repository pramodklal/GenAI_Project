"""
Meal Order MCP Server

Provides tools for patient meal ordering, dietary validation, and nutrition management.
Now uses real Astra DB data.
"""

import sys
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database.astra_helper import get_db_helper
from .base_mcp_server import MCPServerBase


class MealOrderMCPServer(MCPServerBase):
    """MCP Server for meal ordering operations with real database integration."""
    
    def __init__(self):
        super().__init__("meal_order", version="2.0.0")
        self.db = get_db_helper()
        
    def _register_endpoints(self):
        """Register all meal order endpoints."""
        
        self.register_endpoint(
            name="get_patient_dietary_restrictions",
            handler=self._get_patient_dietary_restrictions,
            required_params=["patient_id"],
            description="Retrieve dietary restrictions for a patient"
        )
        
        self.register_endpoint(
            name="validate_meal_selection",
            handler=self._validate_meal_selection,
            required_params=["patient_id", "meal_items"],
            description="Validate meal selection against dietary restrictions"
        )
        
        self.register_endpoint(
            name="submit_meal_order",
            handler=self._submit_meal_order,
            required_params=["patient_id", "meal_items", "meal_time"],
            description="Submit a meal order for a patient"
        )
        
        self.register_endpoint(
            name="get_nutrition_info",
            handler=self._get_nutrition_info,
            required_params=["meal_id"],
            description="Get nutritional information for a meal"
        )
        
        self.register_endpoint(
            name="get_meal_history",
            handler=self._get_meal_history,
            required_params=["patient_id"],
            description="Get meal order history for a patient"
        )
        
        self.register_endpoint(
            name="get_meal_recommendations",
            handler=self._get_meal_recommendations,
            required_params=["patient_id"],
            description="Get personalized meal recommendations"
        )
    
    def _get_patient_dietary_restrictions(self, patient_id: str) -> Dict[str, Any]:
        """
        Retrieve dietary restrictions for a patient from Astra DB.
        """
        # Get patient data
        patient = self.db.get_patient(patient_id)
        if not patient:
            return {
                "patient_id": patient_id,
                "error": "Patient not found"
            }
        
        # Get dietary profile
        dietary_profile = self.db.get_patient_dietary_profile(patient_id)
        
        return {
            "patient_id": patient_id,
            "allergies": patient.get("allergies", []),
            "dietary_type": dietary_profile.get("dietary_type", "Standard") if dietary_profile else "Standard",
            "medical_restrictions": {
                "dietary_restrictions": patient.get("dietary_restrictions", []),
                "calorie_target": dietary_profile.get("calorie_target", 2000) if dietary_profile else 2000
            },
            "texture_modifications": dietary_profile.get("texture_modifications") if dietary_profile else None,
            "cultural_preferences": dietary_profile.get("cultural_preferences", []) if dietary_profile else [],
            "last_updated": datetime.now().isoformat()
        }
    
    def _validate_meal_selection(self, patient_id: str, meal_items: List[str]) -> Dict[str, Any]:
        """
        Validate meal selection against patient restrictions using real database.
        
        Args:
            patient_id: Patient identifier
            meal_items: List of meal item IDs
            
        Returns:
            Validation result with issues if any
        """
        # Use database validation
        validation_result = self.db.validate_meal_for_patient(patient_id, meal_items)
        
        if not validation_result.get("success"):
            return {
                "valid": False,
                "issues": [{"severity": "error", "reason": "Validation failed"}],
                "warnings": [],
                "validated_at": datetime.now().isoformat()
            }
        
        # Extract validation details
        issues = []
        warnings = []
        
        # Check for allergen conflicts
        allergen_conflicts = validation_result.get("allergen_conflicts", [])
        for conflict in allergen_conflicts:
            issues.append({
                "severity": "critical",
                "item": conflict.get("item_name"),
                "reason": f"Contains {conflict.get('allergen')} - patient has allergy"
            })
        
        # Check for dietary restrictions
        restriction_warnings = validation_result.get("restriction_warnings", [])
        for warning in restriction_warnings:
            warnings.append({
                "severity": "warning",
                "item": warning.get("item_name"),
                "reason": warning.get("reason"),
                "suggested_action": "Consider alternative"
            })
        
        nutrition_totals = validation_result.get("nutrition_totals", {})
        
        is_valid = len(issues) == 0
        
        return {
            "valid": is_valid,
            "issues": issues,
            "warnings": warnings,
            "total_calories": nutrition_totals.get("calories", 0),
            "total_protein_g": nutrition_totals.get("protein_g", 0),
            "total_sodium_mg": nutrition_totals.get("sodium_mg", 0),
            "validated_at": datetime.now().isoformat()
        }
    
    def _submit_meal_order(self, patient_id: str, meal_items: List[str], 
                          meal_time: str, **kwargs) -> Dict[str, Any]:
        """
        Submit a meal order to Astra DB.
        
        Args:
            patient_id: Patient identifier
            meal_items: List of meal item IDs
            meal_time: Meal time (Breakfast/Lunch/Dinner)
            
        Returns:
            Order confirmation
        """
        # Validate first
        validation = self._validate_meal_selection(patient_id, meal_items)
        
        if not validation["valid"]:
            return {
                "success": False,
                "reason": "Validation failed",
                "validation_issues": validation["issues"]
            }
        
        # Create order in database
        try:
            order_data = {
                "patient_id": patient_id,
                "meal_items": meal_items,
                "meal_time": meal_time,
                "order_date": datetime.now().isoformat(),
                "scheduled_delivery_time": kwargs.get("scheduled_time", datetime.now().isoformat()),
                "status": "pending",
                "special_instructions": kwargs.get("special_instructions", "")
            }
            
            order_id = self.db.create_meal_order(order_data)
            
            return {
                "success": True,
                "order_id": order_id,
                "patient_id": patient_id,
                "meal_items": meal_items,
                "meal_time": meal_time,
                "status": "pending",
                "warnings": validation.get("warnings", [])
            }
        except Exception as e:
            return {
                "success": False,
                "reason": f"Order creation failed: {str(e)}"
            }
    
    def _get_nutrition_info(self, meal_id: str) -> Dict[str, Any]:
        """Get nutritional information for a meal from database."""
        menu_item = self.db.get_menu_item(meal_id)
        
        if not menu_item:
            return {
                "meal_id": meal_id,
                "error": "Menu item not found"
            }
        
        return {
            "meal_id": meal_id,
            "name": menu_item.get("name"),
            "description": menu_item.get("description"),
            "calories": menu_item.get("calories"),
            "protein_g": menu_item.get("protein_g"),
            "carbohydrates_g": menu_item.get("carbs_g"),
            "fat_g": menu_item.get("fat_g"),
            "fiber_g": menu_item.get("fiber_g"),
            "sodium_mg": menu_item.get("sodium_mg"),
            "sugar_g": menu_item.get("sugar_g"),
            "category": menu_item.get("category"),
            "dietary_tags": menu_item.get("dietary_tags", []),
            "allergens": menu_item.get("allergens", [])
        }
    
    def _get_meal_history(self, patient_id: str, days: int = 7) -> Dict[str, Any]:
        """Get meal order history for a patient from database."""
        orders = self.db.get_patient_orders(patient_id, limit=50)
        
        # Filter by date range if needed
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        recent_orders = [
            order for order in orders
            if order.get("order_date", "") >= cutoff_date
        ]
        
        return {
            "patient_id": patient_id,
            "period_days": days,
            "total_orders": len(recent_orders),
            "orders": recent_orders,
            "average_rating": 0  # Not tracked yet
        }
    
    def _get_meal_recommendations(self, patient_id: str, meal_type: str = "lunch") -> Dict[str, Any]:
        """Get personalized meal recommendations using vector search."""
        # Get patient data
        patient = self.db.get_patient(patient_id)
        dietary_profile = self.db.get_patient_dietary_profile(patient_id)
        
        if not patient:
            return {
                "patient_id": patient_id,
                "error": "Patient not found"
            }
        
        restrictions = patient.get("dietary_restrictions", [])
        allergies = patient.get("allergies", [])
        dietary_type = dietary_profile.get("dietary_type", "Standard") if dietary_profile else "Standard"
        
        # Build semantic query
        query_parts = [meal_type, "nutritious meal"]
        if dietary_type != "Standard":
            query_parts.append(dietary_type)
        if restrictions:
            query_parts.extend(restrictions)
        
        query = " ".join(query_parts)
        
        # Use vector search
        results = self.db.vector_search_menu_items(
            query_text=query,
            dietary_restrictions=restrictions if restrictions else None,
            allergies=allergies if allergies else None,
            limit=5
        )
        
        recommendations = []
        for item in results:
            similarity = item.get("$similarity", 0.7)
            recommendations.append({
                "meal_id": item.get("item_id"),
                "name": item.get("name"),
                "description": item.get("description"),
                "calories": item.get("calories"),
                "match_score": similarity,
                "reason": "Semantic match based on dietary needs"
            })
        
        return {
            "patient_id": patient_id,
            "meal_type": meal_type,
            "recommendations": recommendations,
            "based_on": {
                "dietary_type": dietary_type,
                "dietary_restrictions": restrictions,
                "allergies": allergies
            },
            "generated_at": datetime.now().isoformat()
        }
