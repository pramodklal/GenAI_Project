"""
Pharma Manufacturing - Production Optimization Agent

AI agent for production scheduling, yield prediction, and resource optimization.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

from database.astra_helper import get_db_helper

logger = logging.getLogger(__name__)


class ProductionOptimizationAgent:
    """AI Agent for production planning and optimization."""
    
    def __init__(self):
        self.db = get_db_helper()
        self.agent_name = "Production Optimization Agent"
        logger.info(f"{self.agent_name} initialized")
    
    def optimize_batch_schedule(self, week_offset: int = 0) -> Dict[str, Any]:
        """
        Optimize production schedule for the specified week.
        
        Args:
            week_offset: Weeks from current week (0 = current week)
            
        Returns:
            Optimized schedule with recommendations
        """
        try:
            # Calculate week date range
            today = datetime.utcnow()
            start_of_week = today + timedelta(weeks=week_offset)
            end_of_week = start_of_week + timedelta(days=7)
            
            # Get scheduled batches for the week
            # In real implementation, would query production_schedules collection
            scheduled_batches = []  # Placeholder
            
            # Get equipment availability
            operational_equipment = self.db.get_operational_equipment()
            
            # Calculate capacity
            total_capacity = len(operational_equipment) * 8 * 7  # equipment * hours/day * days
            
            # Optimization recommendations
            recommendations = []
            
            if len(operational_equipment) < 5:
                recommendations.append("⚠️ Limited equipment availability - consider maintenance scheduling")
            
            # Check for bottlenecks
            bottlenecks = self.identify_bottlenecks()
            if bottlenecks.get("bottlenecks"):
                recommendations.append(f"⚠️ Bottlenecks detected: {', '.join(bottlenecks['bottlenecks'])}")
            
            # Material availability check
            low_stock = self.db.get_low_stock_materials(threshold=1000)
            if low_stock:
                recommendations.append(f"⚠️ {len(low_stock)} materials below threshold")
            
            schedule = {
                "week": {
                    "start_date": start_of_week.isoformat(),
                    "end_date": end_of_week.isoformat(),
                    "week_number": start_of_week.isocalendar()[1]
                },
                "scheduled_batches": len(scheduled_batches),
                "available_equipment": len(operational_equipment),
                "total_capacity_hours": total_capacity,
                "capacity_utilization": "75%",  # Would calculate from actual schedules
                "recommendations": recommendations,
                "priority_batches": self._identify_priority_batches(),
                "optimized_at": datetime.utcnow().isoformat(),
                "agent": self.agent_name
            }
            
            return schedule
            
        except Exception as e:
            logger.error(f"Error optimizing batch schedule: {str(e)}")
            return {"error": str(e)}
    
    def _identify_priority_batches(self) -> List[Dict]:
        """Identify high-priority batches based on various criteria."""
        # In production, would query batches with:
        # - Expiring materials
        # - High demand products
        # - Low inventory levels
        # - Regulatory deadlines
        
        priority_batches = []
        
        # Example logic (simplified)
        low_stock_materials = self.db.get_low_stock_materials(threshold=1000)
        for material in low_stock_materials[:3]:  # Top 3
            priority_batches.append({
                "material": material.get("name"),
                "reason": "Low stock",
                "urgency": "high",
                "current_quantity": material.get("quantity_in_stock")
            })
        
        return priority_batches
    
    def calculate_material_requirements(self, batch_id: str) -> Dict[str, Any]:
        """
        Calculate material requirements for a batch.
        
        Args:
            batch_id: Batch identifier
            
        Returns:
            Material requirements breakdown
        """
        try:
            batch = self.db.get_batch(batch_id)
            if not batch:
                return {"error": "Batch not found"}
            
            medicine_id = batch.get("medicine_id")
            batch_size = batch.get("quantity", 0)
            
            # Get formulation
            formulation = self.db.get_formulation(medicine_id)
            if not formulation:
                return {"error": "Formulation not found"}
            
            # Calculate requirements
            components = formulation.get("components", [])
            requirements = []
            
            for component in components:
                material_id = component.get("material_id")
                quantity_per_unit = component.get("quantity_per_unit", 0)
                unit = component.get("unit", "mg")
                
                # Calculate total needed
                total_needed = quantity_per_unit * batch_size
                
                # Add overage (typically 10% for API, 5% for excipients)
                overage = 0.10 if component.get("type") == "API" else 0.05
                total_with_overage = total_needed * (1 + overage)
                
                # Check current stock
                material = self.db.get_material(material_id)
                current_stock = material.get("quantity_in_stock", 0) if material else 0
                
                requirements.append({
                    "material_id": material_id,
                    "material_name": material.get("name") if material else "Unknown",
                    "required_quantity": round(total_needed, 2),
                    "with_overage": round(total_with_overage, 2),
                    "unit": unit,
                    "current_stock": current_stock,
                    "sufficient": current_stock >= total_with_overage,
                    "shortage": max(0, total_with_overage - current_stock)
                })
            
            # Determine if all materials available
            all_available = all(r["sufficient"] for r in requirements)
            shortages = [r for r in requirements if not r["sufficient"]]
            
            result = {
                "batch_id": batch_id,
                "batch_size": batch_size,
                "medicine_id": medicine_id,
                "requirements": requirements,
                "all_materials_available": all_available,
                "shortages": shortages,
                "can_proceed": all_available,
                "calculated_at": datetime.utcnow().isoformat(),
                "agent": self.agent_name
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating material requirements: {str(e)}")
            return {"error": str(e)}
    
    def predict_yield(self, batch_id: str) -> Dict[str, Any]:
        """
        Predict batch yield based on historical data and current conditions.
        
        Args:
            batch_id: Batch identifier
            
        Returns:
            Yield prediction with confidence
        """
        try:
            batch = self.db.get_batch(batch_id)
            if not batch:
                return {"error": "Batch not found"}
            
            medicine_id = batch.get("medicine_id")
            
            # Get historical batches for the same medicine
            # In production, would query completed batches and calculate average yield
            historical_yield = 95.0  # Placeholder
            
            # Factors affecting yield
            factors = {
                "equipment_age": 0.98,  # 98% efficiency for newer equipment
                "operator_experience": 0.99,  # 99% for experienced operators
                "material_quality": 1.0,  # 100% for qualified materials
                "environmental_controls": 1.0  # 100% for controlled environment
            }
            
            # Calculate adjusted prediction
            adjustment_factor = 1.0
            for factor, value in factors.items():
                adjustment_factor *= value
            
            predicted_yield = historical_yield * adjustment_factor
            
            # Confidence based on historical data points
            confidence = 85  # Would calculate from actual historical variance
            
            prediction = {
                "batch_id": batch_id,
                "medicine_id": medicine_id,
                "predicted_yield_percentage": round(predicted_yield, 2),
                "historical_average": historical_yield,
                "adjustment_factors": factors,
                "confidence_level": f"{confidence}%",
                "expected_quantity": round(batch.get("quantity", 0) * predicted_yield / 100, 0),
                "predicted_at": datetime.utcnow().isoformat(),
                "agent": self.agent_name
            }
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error predicting yield: {str(e)}")
            return {"error": str(e)}
    
    def identify_bottlenecks(self) -> Dict[str, Any]:
        """
        Identify production bottlenecks.
        
        Returns:
            Bottleneck analysis with recommendations
        """
        try:
            bottlenecks = []
            
            # Check equipment availability
            operational = self.db.get_operational_equipment()
            maintenance_due = self.db.get_maintenance_due(days=7)
            
            if len(maintenance_due) > 2:
                bottlenecks.append("Equipment maintenance backlog")
            
            # Check material shortages
            low_stock = self.db.get_low_stock_materials(threshold=1000)
            if len(low_stock) > 5:
                bottlenecks.append("Multiple material shortages")
            
            # Check QC backlog
            # Would check for batches waiting for QC approval
            qc_backlog = 0  # Placeholder
            if qc_backlog > 3:
                bottlenecks.append("QC testing backlog")
            
            # Check pending batches
            pending_batches = self.db.get_batches_by_status("in_production")
            if len(pending_batches) > 10:
                bottlenecks.append("High WIP (Work in Progress)")
            
            # Recommendations
            recommendations = []
            if "Equipment maintenance backlog" in bottlenecks:
                recommendations.append("Schedule preventive maintenance during low-demand periods")
            if "Multiple material shortages" in bottlenecks:
                recommendations.append("Review reorder points and lead times")
            if "QC testing backlog" in bottlenecks:
                recommendations.append("Increase QC staffing or implement automated testing")
            if "High WIP" in bottlenecks:
                recommendations.append("Focus on completing in-progress batches before starting new ones")
            
            analysis = {
                "bottlenecks_detected": len(bottlenecks),
                "bottlenecks": bottlenecks,
                "details": {
                    "operational_equipment": len(operational),
                    "maintenance_due": len(maintenance_due),
                    "low_stock_materials": len(low_stock),
                    "pending_batches": len(pending_batches)
                },
                "recommendations": recommendations,
                "severity": "high" if len(bottlenecks) >= 3 else "medium" if len(bottlenecks) > 0 else "low",
                "analyzed_at": datetime.utcnow().isoformat(),
                "agent": self.agent_name
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error identifying bottlenecks: {str(e)}")
            return {"error": str(e)}
    
    def optimize_equipment_allocation(self, batch_id: str) -> Dict[str, Any]:
        """
        Recommend optimal equipment allocation for a batch.
        
        Args:
            batch_id: Batch identifier
            
        Returns:
            Equipment allocation recommendations
        """
        try:
            batch = self.db.get_batch(batch_id)
            if not batch:
                return {"error": "Batch not found"}
            
            # Get operational equipment
            equipment_list = self.db.get_operational_equipment()
            
            # Get batch requirements
            current_stage = batch.get("current_stage", "mixing")
            
            # Equipment requirements by stage
            stage_equipment = {
                "mixing": ["Mixer", "Blender"],
                "granulation": ["Granulator", "Fluid Bed Dryer"],
                "compression": ["Tablet Press", "Compression Machine"],
                "coating": ["Coating Pan", "Film Coater"],
                "packaging": ["Blister Packer", "Bottle Filler"]
            }
            
            required_types = stage_equipment.get(current_stage, [])
            
            # Find suitable equipment
            suitable = [
                eq for eq in equipment_list 
                if eq.get("equipment_type") in required_types
            ]
            
            # Rank by utilization (lower is better)
            # In production, would calculate actual utilization from schedules
            for eq in suitable:
                eq["utilization_score"] = 0.65  # Placeholder
                eq["recommended"] = True
            
            allocation = {
                "batch_id": batch_id,
                "current_stage": current_stage,
                "required_equipment_types": required_types,
                "available_equipment": len(suitable),
                "recommendations": [
                    {
                        "equipment_id": eq.get("equipment_id"),
                        "name": eq.get("name"),
                        "type": eq.get("equipment_type"),
                        "utilization": eq.get("utilization_score"),
                        "priority": "high" if eq.get("utilization_score", 1) < 0.7 else "medium"
                    }
                    for eq in suitable[:3]  # Top 3 recommendations
                ],
                "optimized_at": datetime.utcnow().isoformat(),
                "agent": self.agent_name
            }
            
            return allocation
            
        except Exception as e:
            logger.error(f"Error optimizing equipment allocation: {str(e)}")
            return {"error": str(e)}


# Main execution for testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    agent = ProductionOptimizationAgent()
    print(f"✅ {agent.agent_name} initialized successfully")
    
    # Test bottleneck identification
    # result = agent.identify_bottlenecks()
    # print(json.dumps(result, indent=2))
