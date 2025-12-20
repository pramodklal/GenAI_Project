"""
Nutrition Validation Agent

Validates meal selections against nutritional requirements and patient restrictions.
"""

from typing import Dict, Any, List
from .base_agent import HealthcareAgentBase
import sys
import os

# Add database to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from database.astra_helper import get_db_helper


class NutritionValidationAgent(HealthcareAgentBase):
    """Agent for validating meal selections against nutritional requirements."""
    
    def __init__(self, agent_id: str = "nutrition_validator"):
        super().__init__(
            agent_id=agent_id,
            agent_type="nutrition_validation",
            description="Validates meals against nutritional requirements and dietary restrictions"
        )
        self.db = get_db_helper()
        
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate meal selection.
        
        Expected input_data:
        {
            "patient_id": str,
            "meal_item_ids": List[str],  # Menu item IDs
            "validation_type": str  # "full" or "quick"
        }
        
        Returns validation result with recommendations.
        """
        patient_id = input_data.get("patient_id")
        meal_item_ids = input_data.get("meal_item_ids", [])
        validation_type = input_data.get("validation_type", "full")
        
        self.log_action("validate_meal", {
            "patient_id": patient_id,
            "item_count": len(meal_item_ids)
        })
        
        # Get patient data from Astra DB
        patient = self.db.get_patient(patient_id)
        if not patient:
            return {
                "valid": False,
                "error": f"Patient {patient_id} not found"
            }
        
        dietary_profile = self.db.get_patient_dietary_profile(patient_id)
        
        # Get menu items from Astra DB
        menu_items = []
        for item_id in meal_item_ids:
            item = self.db.get_menu_item(item_id)
            if item:
                menu_items.append(item)
        
        if not menu_items:
            return {
                "valid": False,
                "error": "No valid menu items found"
            }
        
        # Perform validation with real data
        validation_result = self._validate_meal_with_db_data(
            patient,
            dietary_profile,
            menu_items,
            validation_type
        )
        
        # Log to Astra DB
        self.db.log_agent_activity(
            agent_name=self.agent_id,
            action_type="validate_meal",
            input_data=input_data,
            output_data=validation_result,
            success=validation_result.get("valid", False)
        )
        
        # Get recommendations if there are issues
        if validation_result.get("warnings") or not validation_result.get("valid"):
            recommendations = await self._generate_recommendations_from_db(
                patient_id,
                validation_result
            )
            validation_result["recommendations"] = recommendations
        
        self.log_action("validation_complete", {
            "valid": validation_result["valid"],
            "issue_count": len(validation_result["issues"])
        })
        
        return validation_result
    
    def _validate_meal(self, meal_items: List[str], nutrition_data: List[Dict],
                      restrictions: Dict[str, Any], validation_type: str) -> Dict[str, Any]:
        """Internal validation logic."""
        issues = []
        warnings = []
        
        # Calculate totals
        total_calories = sum(n.get("calories", 0) for n in nutrition_data)
        total_sodium = sum(n.get("sodium_mg", 0) for n in nutrition_data)
        total_protein = sum(n.get("protein_g", 0) for n in nutrition_data)
        total_carbs = sum(n.get("carbohydrates_g", 0) for n in nutrition_data)
        
        # Check allergies
        patient_allergies = restrictions.get("allergies", [])
        for nutrition in nutrition_data:
            meal_id = nutrition.get("meal_id")
            ingredients = nutrition.get("ingredients", [])
            allergens = nutrition.get("allergen_info", [])
            
            for allergy in patient_allergies:
                if any(allergy.lower() in ing.lower() for ing in ingredients):
                    issues.append({
                        "severity": "critical",
                        "type": "allergy",
                        "meal_id": meal_id,
                        "allergen": allergy,
                        "reason": f"Contains {allergy} - patient has allergy"
                    })
        
        # Check dietary restrictions
        dietary_type = restrictions.get("dietary_type")
        if dietary_type == "vegetarian":
            meat_items = ["chicken", "beef", "pork", "fish"]
            for nutrition in nutrition_data:
                ingredients = nutrition.get("ingredients", [])
                if any(meat in " ".join(ingredients).lower() for meat in meat_items):
                    issues.append({
                        "severity": "high",
                        "type": "dietary_restriction",
                        "meal_id": nutrition.get("meal_id"),
                        "reason": "Contains meat - patient is vegetarian"
                    })
        
        # Check medical restrictions
        medical_restrictions = restrictions.get("medical_restrictions", {})
        
        if medical_restrictions.get("low_sodium") and total_sodium > 2000:
            warnings.append({
                "severity": "warning",
                "type": "medical_restriction",
                "reason": f"Sodium content ({total_sodium}mg) exceeds recommended limit for low-sodium diet",
                "recommendation": "Consider lower-sodium alternatives"
            })
        
        if medical_restrictions.get("diabetic_diet"):
            if total_carbs > 60:
                warnings.append({
                    "severity": "warning",
                    "type": "medical_restriction",
                    "reason": f"Carbohydrate content ({total_carbs}g) is high for diabetic diet",
                    "recommendation": "Consider reducing carbohydrate portions"
                })
        
        max_calories = medical_restrictions.get("max_calories", 2500)
        if total_calories > max_calories:
            warnings.append({
                "severity": "warning",
                "type": "calorie_limit",
                "reason": f"Total calories ({total_calories}) exceeds recommended limit ({max_calories})",
                "recommendation": "Consider smaller portions or lower-calorie options"
            })
        
        # Determine validity
        is_valid = len(issues) == 0
        
        return {
            "valid": is_valid,
            "issues": issues,
            "warnings": warnings,
            "nutrition_summary": {
                "total_calories": total_calories,
                "total_sodium_mg": total_sodium,
                "total_protein_g": total_protein,
                "total_carbohydrates_g": total_carbs
            },
            "restrictions_checked": {
                "allergies": len(patient_allergies),
                "dietary_type": dietary_type,
                "medical_restrictions": list(medical_restrictions.keys())
            }
        }
    
    def _validate_meal_with_db_data(self, patient: Dict, dietary_profile: Dict, 
                                     menu_items: List[Dict], validation_type: str) -> Dict:
        """Validate meal using real Astra DB data"""
        issues = []
        warnings = []
        
        # Calculate totals
        total_calories = sum(item.get('calories', 0) for item in menu_items)
        total_sodium = sum(item.get('sodium_mg', 0) for item in menu_items)
        total_protein = sum(item.get('protein_g', 0) for item in menu_items)
        total_carbs = sum(item.get('carbs_g', 0) for item in menu_items)
        total_sugar = sum(item.get('sugar_g', 0) for item in menu_items)
        total_fat = sum(item.get('fat_g', 0) for item in menu_items)
        
        # Check allergens
        patient_allergies = patient.get('allergies', [])
        for item in menu_items:
            item_allergens = item.get('allergens', [])
            for allergen in item_allergens:
                if allergen in patient_allergies:
                    issues.append({
                        "severity": "critical",
                        "type": "allergen",
                        "item": item.get('name'),
                        "allergen": allergen,
                        "reason": f"ALLERGEN ALERT: Contains {allergen}"
                    })
        
        # Check dietary restrictions
        patient_restrictions = patient.get('dietary_restrictions', [])
        for restriction in patient_restrictions:
            if restriction == 'low-sodium' and total_sodium > 500:
                warnings.append({
                    "severity": "warning",
                    "type": "dietary",
                    "reason": f"High sodium ({total_sodium}mg) for low-sodium diet",
                    "recommendation": "Consider lower-sodium alternatives"
                })
            
            if restriction == 'diabetic' and total_sugar > 15:
                warnings.append({
                    "severity": "warning",
                    "type": "dietary",
                    "reason": f"High sugar ({total_sugar}g) for diabetic diet",
                    "recommendation": "Reduce sugar content"
                })
            
            if restriction == 'low-fat' and total_fat > 15:
                warnings.append({
                    "severity": "warning",
                    "type": "dietary",
                    "reason": f"High fat ({total_fat}g) for low-fat diet",
                    "recommendation": "Choose lower-fat options"
                })
        
        # Check dietary profile targets if available
        if dietary_profile:
            target_calories = dietary_profile.get('calories_target', 2000)
            if abs(total_calories - target_calories) > 300:
                warnings.append({
                    "severity": "info",
                    "type": "calorie_target",
                    "reason": f"Calories ({total_calories}) differ from target ({target_calories})",
                    "recommendation": "Adjust portion sizes"
                })
        
        is_valid = len(issues) == 0
        
        return {
            "valid": is_valid,
            "issues": issues,
            "warnings": warnings,
            "nutrition_summary": {
                "total_calories": total_calories,
                "total_sodium_mg": total_sodium,
                "total_protein_g": total_protein,
                "total_carbs_g": total_carbs,
                "total_sugar_g": total_sugar,
                "total_fat_g": total_fat
            },
            "patient": patient.get('name'),
            "menu_items": [item.get('name') for item in menu_items]
        }
    
    async def _generate_recommendations_from_db(self, patient_id: str, 
                                               validation_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate alternative meal recommendations using vector search"""
        patient = self.db.get_patient(patient_id)
        dietary_profile = self.db.get_patient_dietary_profile(patient_id)
        
        restrictions = patient.get('dietary_restrictions', [])
        allergies = patient.get('allergies', [])
        dietary_type = dietary_profile.get('dietary_type', 'Standard') if dietary_profile else 'Standard'
        
        # Build semantic query based on patient needs
        query_parts = []
        
        if dietary_type and dietary_type != 'Standard':
            query_parts.append(dietary_type)
        
        if restrictions:
            query_parts.extend(restrictions)
        
        # Add general healthy meal query
        query_parts.append("nutritious balanced meal")
        
        query_text = " ".join(query_parts)
        
        # Use vector search for semantic recommendations
        try:
            vector_results = self.db.vector_search_menu_items(
                query_text=query_text,
                dietary_restrictions=restrictions if restrictions else None,
                allergies=allergies if allergies else None,
                limit=5
            )
            
            recommendations = []
            for item in vector_results:
                # Calculate match score based on similarity and dietary compliance
                similarity = item.get('$similarity', 0.7)  # Default similarity
                
                # Boost score for matching dietary tags
                item_tags = [t.lower() for t in item.get('dietary_tags', [])]
                matches_diet = any(r.lower() in item_tags for r in restrictions) if restrictions else False
                
                match_score = similarity
                if matches_diet:
                    match_score = min(match_score + 0.2, 1.0)
                
                # Build reason
                reasons = []
                if matches_diet:
                    reasons.append("Matches dietary requirements")
                if similarity > 0.8:
                    reasons.append("High semantic similarity")
                if item.get('calories', 0) < 400:
                    reasons.append("Appropriate calorie content")
                
                reason = " | ".join(reasons) if reasons else "Suitable alternative"
                
                recommendations.append({
                    "meal_id": item.get('item_id'),
                    "name": item.get('name'),
                    "description": item.get('description', 'Nutritious meal option'),
                    "match_score": round(match_score, 2),
                    "reason": reason,
                    "calories": item.get('calories'),
                    "dietary_tags": item.get('dietary_tags', [])
                })
            
            return recommendations[:3]  # Top 3 recommendations
            
        except Exception as e:
            # Fallback to tag-based search if vector search fails
            suitable_items = []
            for restriction in restrictions:
                items = self.db.get_menu_items_by_dietary_tags([restriction], limit=3)
                suitable_items.extend(items)
            
            recommendations = []
            for item in suitable_items[:3]:
                recommendations.append({
                    "meal_id": item.get('item_id'),
                    "name": item.get('name'),
                    "description": item.get('description'),
                    "match_score": 0.75,
                    "reason": "Matches dietary requirements",
                    "calories": item.get('calories')
                })
            
            return recommendations
