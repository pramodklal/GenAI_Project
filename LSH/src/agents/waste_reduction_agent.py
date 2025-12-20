"""
Waste Reduction Agent

Identifies food waste risks and recommends actions to minimize waste.
Uses real Astra DB data for analysis.
"""

import sys
import os
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database.astra_helper import get_db_helper
from .base_agent import HealthcareAgentBase


class WasteReductionAgent(HealthcareAgentBase):
    """Agent for identifying and reducing food waste using real database data."""
    
    def __init__(self, agent_id: str = "waste_reducer"):
        super().__init__(
            agent_id=agent_id,
            agent_type="waste_reduction",
            description="Identifies waste risks and recommends waste reduction strategies"
        )
        self.db = get_db_helper()
        
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze inventory and demand to identify waste risks.
        
        Expected input_data:
        {
            "date": str,  # Date to analyze for (ISO format)
            "threshold_days": int,  # Days until expiration threshold (default: 3)
            "generate_actions": bool  # Whether to generate actionable recommendations
        }
        """
        date = input_data.get("date", datetime.now().isoformat())
        threshold_days = input_data.get("threshold_days", 3)
        generate_actions = input_data.get("generate_actions", True)
        
        self.log_action("analyze_waste_risks", {
            "date": date,
            "threshold_days": threshold_days
        })
        
        # Get low inventory items (items that need to be used soon)
        low_inventory = self.db.get_low_inventory_items()
        
        # Get production schedules to analyze waste patterns (last 7 days)
        production_schedules = []
        for days_back in range(7):
            schedule_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
            schedules_for_date = self.db.get_production_schedule(schedule_date)
            production_schedules.extend(schedules_for_date)
        
        # Analyze inventory for items at risk
        at_risk_items = self._identify_at_risk_inventory(low_inventory, threshold_days)
        
        # Analyze historical waste from production schedules
        waste_analysis = self._analyze_historical_waste(production_schedules)
        
        # Get demand forecast based on recent orders
        forecast = self._forecast_demand()
        
        # Analyze and generate recommendations
        analysis = self._analyze_waste_patterns(at_risk_items, forecast, waste_analysis)
        
        if generate_actions:
            actions = await self._generate_waste_reduction_actions(
                at_risk_items,
                forecast,
                analysis
            )
            analysis["recommended_actions"] = actions
        
        # Calculate estimated waste value
        estimated_waste_value = sum(
            item.get("quantity", 0) * item.get("unit_cost", 5.0) 
            for item in at_risk_items
        )
        
        # Log activity to database
        self.db.log_agent_activity(
            agent_name=self.agent_id,
            action_type="analyze_waste_risks",
            input_data={
                "date": date,
                "threshold_days": threshold_days
            },
            output_data={
                "at_risk_items": len(at_risk_items),
                "estimated_waste_value": estimated_waste_value,
                "total_waste_kg": waste_analysis.get("total_waste_kg", 0),
                "actions_generated": len(analysis.get("recommended_actions", []))
            },
            success=True
        )
        
        return {
            "success": True,
            "date": date,
            "at_risk_items": at_risk_items,
            "analysis": analysis,
            "waste_analysis": waste_analysis,
            "estimated_waste_value": estimated_waste_value,
            "timestamp": datetime.now().isoformat()
        }
    
    def _identify_at_risk_inventory(self, inventory_items: List[Dict], threshold_days: int) -> List[Dict]:
        """Identify inventory items at risk of expiring"""
        at_risk = []
        now = datetime.now()
        
        for item in inventory_items:
            # Items with low quantity or approaching reorder
            quantity = item.get("quantity", 0)
            reorder_point = item.get("reorder_point", 10)
            
            # Calculate risk level
            risk_level = "low"
            if quantity <= reorder_point * 0.5:
                risk_level = "high"
            elif quantity <= reorder_point:
                risk_level = "medium"
            
            # Add to at-risk if low quantity
            if quantity <= reorder_point:
                at_risk.append({
                    **item,
                    "risk_level": risk_level,
                    "risk_reason": "Low inventory - use soon to avoid spoilage",
                    "days_until_expiration": threshold_days  # Estimate based on threshold
                })
        
        return at_risk
    
    def _analyze_historical_waste(self, production_schedules: List[Dict]) -> Dict[str, Any]:
        """Analyze historical waste from production schedules"""
        total_waste_kg = 0
        waste_by_category = defaultdict(float)
        waste_by_meal_type = defaultdict(float)
        total_meals_produced = 0
        
        for schedule in production_schedules:
            waste_kg = schedule.get("waste_amount_kg", 0)
            total_waste_kg += waste_kg
            
            meal_type = schedule.get("meal_type", "unknown")
            waste_by_meal_type[meal_type] += waste_kg
            
            meals_produced = schedule.get("meals_produced", 0)
            total_meals_produced += meals_produced
        
        # Calculate waste percentage
        waste_percentage = 0
        if total_meals_produced > 0:
            waste_percentage = (total_waste_kg / total_meals_produced) * 100
        
        # Identify high-waste meal types
        high_waste_meals = sorted(
            waste_by_meal_type.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        return {
            "total_waste_kg": total_waste_kg,
            "total_meals_produced": total_meals_produced,
            "waste_percentage": round(waste_percentage, 2),
            "waste_by_meal_type": dict(waste_by_meal_type),
            "high_waste_meals": [
                {"meal_type": meal, "waste_kg": waste}
                for meal, waste in high_waste_meals
            ],
            "average_waste_per_schedule": round(total_waste_kg / len(production_schedules), 2) if production_schedules else 0
        }
    
    def _forecast_demand(self) -> Dict[str, int]:
        """Forecast demand based on recent orders"""
        # Get today's orders
        todays_orders = self.db.get_todays_orders()
        
        # Count orders by meal time
        demand_forecast = defaultdict(int)
        
        for order in todays_orders:
            meal_time = order.get("meal_time", "lunch")
            demand_forecast[meal_time] += 1
        
        # Add predictions for tomorrow based on today
        forecast = dict(demand_forecast)
        forecast["predicted_tomorrow"] = sum(demand_forecast.values())
        
        return forecast
    
    def _analyze_waste_patterns(self, at_risk_items: List[Dict], 
                                forecast: Dict[str, int],
                                waste_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze waste patterns and categorize risks."""
        # Categorize by risk level
        high_risk = [item for item in at_risk_items if item.get("risk_level") == "high"]
        medium_risk = [item for item in at_risk_items if item.get("risk_level") == "medium"]
        low_risk = [item for item in at_risk_items if item.get("risk_level") == "low"]
        
        # Categorize by potential use
        usable_in_next_meal = []
        donation_candidates = []
        freeze_candidates = []
        reorder_needed = []
        
        for item in at_risk_items:
            quantity = item.get("quantity", 0)
            reorder_point = item.get("reorder_point", 10)
            
            # Items with very low quantity need immediate use
            if quantity <= reorder_point * 0.3:
                usable_in_next_meal.append(item)
            elif quantity <= reorder_point * 0.5:
                freeze_candidates.append(item)
            
            # Items at reorder point
            if quantity <= reorder_point:
                reorder_needed.append(item)
        
        # Calculate potential savings
        estimated_value_savable = sum(
            item.get("quantity", 0) * item.get("unit_cost", 5.0)
            for item in at_risk_items
        )
        
        return {
            "risk_breakdown": {
                "high_risk_count": len(high_risk),
                "medium_risk_count": len(medium_risk),
                "low_risk_count": len(low_risk),
                "total_at_risk": len(at_risk_items)
            },
            "actionable_categories": {
                "use_in_next_meal": len(usable_in_next_meal),
                "donation_candidates": len(donation_candidates),
                "freeze_candidates": len(freeze_candidates),
                "reorder_needed": len(reorder_needed)
            },
            "waste_prevention_potential": {
                "items_savable": len(at_risk_items),
                "estimated_value_savable": round(estimated_value_savable, 2)
            },
            "demand_insights": {
                "predicted_meals_tomorrow": forecast.get("predicted_tomorrow", 0),
                "current_waste_rate": f"{waste_analysis.get('waste_percentage', 0)}%"
            }
        }
    
    async def _generate_waste_reduction_actions(self, at_risk_items: List[Dict],
                                                forecast: Dict[str, int],
                                                analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate specific actions to reduce waste."""
        actions = []
        
        # Action 1: Use low-inventory items in meals
        use_in_meals = analysis["actionable_categories"]["use_in_next_meal"]
        if use_in_meals > 0:
            high_risk_items = [i for i in at_risk_items if i.get("risk_level") == "high"]
            actions.append({
                "action_id": "menu_adjustment",
                "priority": "high",
                "type": "menu_modification",
                "description": f"Prioritize {use_in_meals} low-inventory items in next meals",
                "affected_items": [item["item_name"] for item in high_risk_items[:5]],
                "estimated_impact": {
                    "items_saved": use_in_meals,
                    "value_saved": sum(
                        item.get("quantity", 0) * item.get("unit_cost", 5.0)
                        for item in high_risk_items
                    )
                },
                "implementation": "Update production schedule to feature these ingredients"
            })
        
        # Action 2: Reorder needed items
        reorder_items = analysis["actionable_categories"]["reorder_needed"]
        if reorder_items > 0:
            items_to_reorder = [i for i in at_risk_items if i.get("quantity", 0) <= i.get("reorder_point", 10)]
            actions.append({
                "action_id": "reorder_inventory",
                "priority": "high",
                "type": "procurement",
                "description": f"Reorder {reorder_items} items below reorder point",
                "affected_items": [item["item_name"] for item in items_to_reorder[:5]],
                "estimated_impact": {
                    "items_to_order": reorder_items,
                    "prevent_stockout": True
                },
                "implementation": "Submit purchase orders for low-stock items"
            })
        
        # Action 3: Optimize production quantities
        predicted_demand = forecast.get("predicted_tomorrow", 0)
        if predicted_demand > 0:
            actions.append({
                "action_id": "optimize_production",
                "priority": "medium",
                "type": "production_planning",
                "description": f"Adjust production quantities based on demand forecast ({predicted_demand} meals)",
                "affected_items": "all_meal_types",
                "estimated_impact": {
                    "waste_reduction": "10-15% expected",
                    "cost_savings": "estimated $200-400/week"
                },
                "implementation": "Use demand forecast to plan meal quantities"
            })
        
        # Action 4: Reduce high-waste meal types
        waste_rate = analysis.get("demand_insights", {}).get("current_waste_rate", "0%")
        if float(waste_rate.rstrip('%')) > 5:
            actions.append({
                "action_id": "reduce_high_waste_meals",
                "priority": "medium",
                "type": "process_improvement",
                "description": f"Review high-waste meal types (current waste rate: {waste_rate})",
                "affected_items": "meal_types_with_high_waste",
                "estimated_impact": {
                    "long_term_reduction": "20-30% waste reduction over 3 months",
                    "cost_savings": "estimated $800-1200/month"
                },
                "implementation": "Analyze production schedules and adjust portions"
            })
        
        # Action 5: Freeze surplus items
        freeze_candidates = analysis["actionable_categories"]["freeze_candidates"]
        if freeze_candidates > 0:
            items_to_freeze = [i for i in at_risk_items if i.get("risk_level") == "medium"]
            actions.append({
                "action_id": "freeze_surplus",
                "priority": "low",
                "type": "preservation",
                "description": f"Freeze {freeze_candidates} items for future use",
                "affected_items": [item["item_name"] for item in items_to_freeze[:5]],
                "estimated_impact": {
                    "shelf_life_extension": "30-90 days",
                    "items_preserved": freeze_candidates
                },
                "implementation": "Prepare and freeze within 48 hours"
            })
        
        return actions
