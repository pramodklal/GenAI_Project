"""
Pharma Manufacturing - Supply Chain Agent

AI agent for demand forecasting, supplier analysis, and inventory optimization.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

from database.astra_helper import get_db_helper

logger = logging.getLogger(__name__)


class SupplyChainAgent:
    """AI Agent for supply chain management and optimization."""
    
    def __init__(self):
        self.db = get_db_helper()
        self.agent_name = "Supply Chain Agent"
        logger.info(f"{self.agent_name} initialized")
    
    def forecast_demand(self, material_id: str, forecast_days: int = 30) -> Dict[str, Any]:
        """
        Forecast material demand for specified period.
        
        Args:
            material_id: Material identifier
            forecast_days: Number of days to forecast
            
        Returns:
            Demand forecast with recommendations
        """
        try:
            material = self.db.get_material(material_id)
            if not material:
                return {"error": "Material not found"}
            
            # Get historical consumption
            # In production, would analyze historical batch consumption
            historical_daily_usage = 150.0  # Placeholder (kg/day)
            
            # Seasonal adjustment factors
            current_month = datetime.utcnow().month
            seasonal_factors = {
                1: 1.1, 2: 1.0, 3: 0.9, 4: 0.95, 5: 1.0, 6: 1.05,
                7: 1.1, 8: 1.15, 9: 1.2, 10: 1.1, 11: 1.0, 12: 0.95
            }
            seasonal_adjustment = seasonal_factors.get(current_month, 1.0)
            
            # Trend adjustment (growth rate)
            growth_rate = 1.05  # 5% growth
            
            # Calculate forecast
            adjusted_daily_usage = historical_daily_usage * seasonal_adjustment * growth_rate
            forecasted_demand = adjusted_daily_usage * forecast_days
            
            # Current stock
            current_stock = material.get("quantity_in_stock", 0)
            reorder_point = material.get("reorder_point", 0)
            
            # Calculate days until stockout
            days_until_stockout = (current_stock / adjusted_daily_usage) if adjusted_daily_usage > 0 else 999
            
            # Recommendation
            if days_until_stockout < 14:
                recommendation = "URGENT: Place order immediately"
                urgency = "critical"
            elif days_until_stockout < 30:
                recommendation = "WARNING: Order needed soon"
                urgency = "high"
            elif current_stock < reorder_point:
                recommendation = "NOTICE: Below reorder point"
                urgency = "medium"
            else:
                recommendation = "OK: Stock levels adequate"
                urgency = "low"
            
            forecast = {
                "material_id": material_id,
                "material_name": material.get("name"),
                "forecast_period_days": forecast_days,
                "current_stock": current_stock,
                "current_unit": material.get("unit"),
                "historical_daily_usage": historical_daily_usage,
                "adjusted_daily_usage": round(adjusted_daily_usage, 2),
                "forecasted_demand": round(forecasted_demand, 2),
                "days_until_stockout": round(days_until_stockout, 1),
                "reorder_point": reorder_point,
                "recommendation": recommendation,
                "urgency": urgency,
                "factors": {
                    "seasonal_adjustment": seasonal_adjustment,
                    "growth_rate": growth_rate
                },
                "forecasted_at": datetime.utcnow().isoformat(),
                "agent": self.agent_name
            }
            
            return forecast
            
        except Exception as e:
            logger.error(f"Error forecasting demand: {str(e)}")
            return {"error": str(e)}
    
    def analyze_supplier_performance(self, supplier_id: str) -> Dict[str, Any]:
        """
        Analyze supplier performance metrics.
        
        Args:
            supplier_id: Supplier identifier
            
        Returns:
            Performance analysis report
        """
        try:
            supplier = self.db.get_supplier(supplier_id)
            if not supplier:
                return {"error": "Supplier not found"}
            
            # Get supplier certifications
            certifications = supplier.get("certifications", [])
            
            # Calculate performance metrics
            # In production, would analyze actual order history
            metrics = {
                "on_time_delivery_rate": 94.5,  # Percentage
                "quality_acceptance_rate": 98.2,  # Percentage
                "lead_time_avg_days": 14,
                "lead_time_variance_days": 2,
                "price_competitiveness": "Good",  # Relative to market
                "response_time_hours": 24,
                "defect_rate": 0.5  # Percentage
            }
            
            # Calculate overall score (weighted average)
            weights = {
                "on_time_delivery_rate": 0.25,
                "quality_acceptance_rate": 0.30,
                "lead_time_consistency": 0.20,  # Lower variance is better
                "price_competitiveness": 0.15,
                "response_time": 0.10
            }
            
            # Normalize metrics to 0-100 scale
            lead_time_consistency = max(0, 100 - (metrics["lead_time_variance_days"] * 10))
            price_score = 85  # Would calculate from market comparison
            response_score = max(0, 100 - metrics["response_time_hours"])
            
            overall_score = (
                metrics["on_time_delivery_rate"] * weights["on_time_delivery_rate"] +
                metrics["quality_acceptance_rate"] * weights["quality_acceptance_rate"] +
                lead_time_consistency * weights["lead_time_consistency"] +
                price_score * weights["price_competitiveness"] +
                response_score * weights["response_time"]
            )
            
            # Rating
            if overall_score >= 90:
                rating = "Excellent"
            elif overall_score >= 80:
                rating = "Good"
            elif overall_score >= 70:
                rating = "Acceptable"
            else:
                rating = "Needs Improvement"
            
            # Recommendations
            recommendations = []
            if metrics["on_time_delivery_rate"] < 95:
                recommendations.append("Work with supplier to improve delivery timeliness")
            if metrics["quality_acceptance_rate"] < 98:
                recommendations.append("Review quality requirements with supplier")
            if metrics["defect_rate"] > 1.0:
                recommendations.append("Implement stricter incoming inspection")
            
            analysis = {
                "supplier_id": supplier_id,
                "supplier_name": supplier.get("name"),
                "contact": supplier.get("contact", {}),
                "certifications": certifications,
                "metrics": metrics,
                "overall_score": round(overall_score, 2),
                "rating": rating,
                "recommendations": recommendations,
                "status": supplier.get("status"),
                "analyzed_at": datetime.utcnow().isoformat(),
                "agent": self.agent_name
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing supplier performance: {str(e)}")
            return {"error": str(e)}
    
    def calculate_reorder_points(self, material_id: str) -> Dict[str, Any]:
        """
        Calculate optimal reorder points and quantities.
        
        Args:
            material_id: Material identifier
            
        Returns:
            Reorder calculations with safety stock
        """
        try:
            material = self.db.get_material(material_id)
            if not material:
                return {"error": "Material not found"}
            
            # Parameters
            daily_usage = 150.0  # Would calculate from historical data
            lead_time_days = 14  # Average lead time from supplier
            lead_time_variance = 2  # Standard deviation in days
            service_level = 0.95  # 95% service level (Z-score = 1.65)
            
            # Calculate safety stock
            # Safety Stock = Z-score × √(lead_time) × daily_usage_std_dev
            # Simplified: Z-score × daily_usage × lead_time_variance
            z_score = 1.65  # For 95% service level
            safety_stock = z_score * daily_usage * lead_time_variance
            
            # Calculate reorder point
            # ROP = (Daily Usage × Lead Time) + Safety Stock
            reorder_point = (daily_usage * lead_time_days) + safety_stock
            
            # Economic Order Quantity (EOQ)
            # EOQ = √(2 × Annual Demand × Order Cost / Holding Cost)
            annual_demand = daily_usage * 365
            order_cost = 500  # Cost per order (fixed)
            holding_cost_per_unit = 5  # Annual holding cost per unit
            
            import math
            eoq = math.sqrt((2 * annual_demand * order_cost) / holding_cost_per_unit)
            
            # Current status
            current_stock = material.get("quantity_in_stock", 0)
            should_reorder = current_stock <= reorder_point
            
            calculation = {
                "material_id": material_id,
                "material_name": material.get("name"),
                "current_stock": current_stock,
                "unit": material.get("unit"),
                "parameters": {
                    "daily_usage": daily_usage,
                    "lead_time_days": lead_time_days,
                    "lead_time_variance": lead_time_variance,
                    "service_level": f"{service_level * 100}%",
                    "z_score": z_score
                },
                "calculations": {
                    "safety_stock": round(safety_stock, 2),
                    "reorder_point": round(reorder_point, 2),
                    "economic_order_quantity": round(eoq, 2)
                },
                "recommendation": {
                    "should_reorder": should_reorder,
                    "order_quantity": round(eoq, 2) if should_reorder else 0,
                    "urgency": "high" if current_stock < (reorder_point * 0.8) else "normal"
                },
                "calculated_at": datetime.utcnow().isoformat(),
                "agent": self.agent_name
            }
            
            return calculation
            
        except Exception as e:
            logger.error(f"Error calculating reorder points: {str(e)}")
            return {"error": str(e)}
    
    def get_expiring_materials(self, days_ahead: int = 30) -> Dict[str, Any]:
        """
        Get materials expiring within specified period.
        
        Args:
            days_ahead: Days to look ahead
            
        Returns:
            List of expiring materials with recommendations
        """
        try:
            expiring = self.db.get_expiring_materials(days_ahead)
            
            # Categorize by urgency
            critical = []  # Expires in < 7 days
            warning = []   # Expires in 7-14 days
            watch = []     # Expires in 15-30 days
            
            for material in expiring:
                expiry_date = material.get("expiry_date")
                if not expiry_date:
                    continue
                
                expiry_dt = datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
                days_until_expiry = (expiry_dt - datetime.utcnow()).days
                
                material_info = {
                    "material_id": material.get("material_id"),
                    "name": material.get("name"),
                    "batch_number": material.get("batch_number"),
                    "quantity": material.get("quantity_in_stock"),
                    "unit": material.get("unit"),
                    "expiry_date": expiry_date,
                    "days_until_expiry": days_until_expiry,
                    "estimated_value": material.get("quantity_in_stock", 0) * 10  # Placeholder
                }
                
                if days_until_expiry < 7:
                    material_info["recommendation"] = "USE IMMEDIATELY or dispose"
                    critical.append(material_info)
                elif days_until_expiry < 14:
                    material_info["recommendation"] = "Prioritize usage in upcoming batches"
                    warning.append(material_info)
                else:
                    material_info["recommendation"] = "Monitor and plan usage"
                    watch.append(material_info)
            
            # Calculate potential waste value
            potential_waste_value = sum(m["estimated_value"] for m in critical)
            
            report = {
                "total_expiring": len(expiring),
                "by_urgency": {
                    "critical": {
                        "count": len(critical),
                        "materials": critical,
                        "total_value": potential_waste_value
                    },
                    "warning": {
                        "count": len(warning),
                        "materials": warning
                    },
                    "watch": {
                        "count": len(watch),
                        "materials": watch
                    }
                },
                "recommendations": [
                    "Schedule production to use expiring materials first (FEFO - First Expire, First Out)",
                    "Review inventory turnover rates",
                    "Adjust order quantities to reduce waste"
                ],
                "checked_at": datetime.utcnow().isoformat(),
                "days_ahead": days_ahead,
                "agent": self.agent_name
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error getting expiring materials: {str(e)}")
            return {"error": str(e)}
    
    def optimize_inventory_levels(self) -> Dict[str, Any]:
        """
        Analyze and optimize overall inventory levels.
        
        Returns:
            Inventory optimization report
        """
        try:
            # Get low stock materials
            low_stock = self.db.get_low_stock_materials(threshold=1000)
            
            # Get expiring materials
            expiring = self.db.get_expiring_materials(days=30)
            
            # Calculate inventory metrics
            # In production, would query all materials and calculate:
            # - Total inventory value
            # - Inventory turnover ratio
            # - Dead stock value
            
            metrics = {
                "materials_below_reorder_point": len(low_stock),
                "materials_expiring_soon": len(expiring),
                "estimated_total_inventory_value": 1500000,  # Placeholder
                "inventory_turnover_ratio": 6.5,  # Times per year
                "days_of_inventory_on_hand": 56,  # Days
                "dead_stock_value": 45000  # Placeholder
            }
            
            # Optimization recommendations
            recommendations = []
            
            if len(low_stock) > 5:
                recommendations.append(f"URGENT: {len(low_stock)} materials below reorder point - place orders")
            
            if len(expiring) > 10:
                recommendations.append(f"WARNING: {len(expiring)} materials expiring within 30 days")
            
            if metrics["inventory_turnover_ratio"] < 6:
                recommendations.append("Inventory turnover is low - consider reducing order quantities")
            
            if metrics["days_of_inventory_on_hand"] > 60:
                recommendations.append("Excess inventory - review demand forecasts and reorder points")
            
            if metrics["dead_stock_value"] > 50000:
                recommendations.append("Significant dead stock - implement clearance strategy")
            
            report = {
                "metrics": metrics,
                "low_stock_materials": [
                    {
                        "material_id": m.get("material_id"),
                        "name": m.get("name"),
                        "current_stock": m.get("quantity_in_stock"),
                        "reorder_point": m.get("reorder_point")
                    }
                    for m in low_stock[:10]  # Top 10
                ],
                "recommendations": recommendations,
                "overall_health": "Good" if len(recommendations) <= 2 else "Needs Attention",
                "analyzed_at": datetime.utcnow().isoformat(),
                "agent": self.agent_name
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error optimizing inventory levels: {str(e)}")
            return {"error": str(e)}


# Main execution for testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    agent = SupplyChainAgent()
    print(f"✅ {agent.agent_name} initialized successfully")
    
    # Test inventory optimization
    # result = agent.optimize_inventory_levels()
    # print(json.dumps(result, indent=2))
