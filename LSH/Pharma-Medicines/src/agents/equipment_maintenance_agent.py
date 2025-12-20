"""
Pharma Manufacturing - Equipment Maintenance Agent

AI agent for predictive maintenance, OEE calculation, and calibration tracking.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

from database.astra_helper import get_db_helper

logger = logging.getLogger(__name__)


class EquipmentMaintenanceAgent:
    """AI Agent for equipment maintenance and performance monitoring."""
    
    def __init__(self):
        self.db = get_db_helper()
        self.agent_name = "Equipment Maintenance Agent"
        logger.info(f"{self.agent_name} initialized")
    
    def schedule_maintenance(self, equipment_id: str) -> Dict[str, Any]:
        """
        Schedule maintenance for equipment based on usage and condition.
        
        Args:
            equipment_id: Equipment identifier
            
        Returns:
            Maintenance schedule with recommendations
        """
        try:
            equipment = self.db.get_equipment(equipment_id)
            if not equipment:
                return {"error": "Equipment not found"}
            
            # Get last maintenance date
            last_maintenance = equipment.get("last_maintenance_date")
            if last_maintenance:
                last_maintenance_dt = datetime.fromisoformat(last_maintenance.replace('Z', '+00:00'))
                days_since_maintenance = (datetime.utcnow() - last_maintenance_dt).days
            else:
                days_since_maintenance = 999
            
            # Get next calibration date
            next_calibration = equipment.get("next_calibration_date")
            if next_calibration:
                next_calibration_dt = datetime.fromisoformat(next_calibration.replace('Z', '+00:00'))
                days_until_calibration = (next_calibration_dt - datetime.utcnow()).days
            else:
                days_until_calibration = 999
            
            # Maintenance interval (days) based on equipment type
            maintenance_intervals = {
                "Mixer": 180,
                "Tablet Press": 90,
                "Coating Pan": 120,
                "Granulator": 150,
                "Blister Packer": 60,
                "Blender": 180
            }
            
            equipment_type = equipment.get("equipment_type", "Other")
            interval = maintenance_intervals.get(equipment_type, 365)
            
            # Calculate next maintenance date
            if last_maintenance:
                next_maintenance_dt = last_maintenance_dt + timedelta(days=interval)
            else:
                next_maintenance_dt = datetime.utcnow() + timedelta(days=interval)
            
            days_until_maintenance = (next_maintenance_dt - datetime.utcnow()).days
            
            # Determine priority
            if days_until_maintenance < 0:
                priority = "overdue"
                urgency = "critical"
            elif days_until_maintenance < 7:
                priority = "urgent"
                urgency = "high"
            elif days_until_maintenance < 30:
                priority = "soon"
                urgency = "medium"
            else:
                priority = "scheduled"
                urgency = "low"
            
            # Maintenance tasks
            maintenance_tasks = self._get_maintenance_tasks(equipment_type)
            
            schedule = {
                "equipment_id": equipment_id,
                "equipment_name": equipment.get("name"),
                "equipment_type": equipment_type,
                "last_maintenance": last_maintenance,
                "days_since_maintenance": days_since_maintenance,
                "next_maintenance_date": next_maintenance_dt.isoformat(),
                "days_until_maintenance": days_until_maintenance,
                "maintenance_interval_days": interval,
                "priority": priority,
                "urgency": urgency,
                "next_calibration_date": next_calibration,
                "days_until_calibration": days_until_calibration,
                "maintenance_tasks": maintenance_tasks,
                "estimated_downtime_hours": self._estimate_downtime(equipment_type),
                "scheduled_at": datetime.utcnow().isoformat(),
                "agent": self.agent_name
            }
            
            return schedule
            
        except Exception as e:
            logger.error(f"Error scheduling maintenance: {str(e)}")
            return {"error": str(e)}
    
    def _get_maintenance_tasks(self, equipment_type: str) -> List[Dict]:
        """Get maintenance tasks for equipment type."""
        common_tasks = [
            {"task": "Visual inspection", "duration_minutes": 30},
            {"task": "Lubrication", "duration_minutes": 45},
            {"task": "Filter replacement", "duration_minutes": 60},
            {"task": "Belt/chain inspection", "duration_minutes": 30},
            {"task": "Electrical connections check", "duration_minutes": 45}
        ]
        
        type_specific_tasks = {
            "Mixer": [
                {"task": "Blade sharpness check", "duration_minutes": 30},
                {"task": "Motor bearing inspection", "duration_minutes": 45}
            ],
            "Tablet Press": [
                {"task": "Punch and die inspection", "duration_minutes": 90},
                {"task": "Compression force calibration", "duration_minutes": 120}
            ],
            "Coating Pan": [
                {"task": "Spray nozzle cleaning", "duration_minutes": 60},
                {"task": "Pan surface inspection", "duration_minutes": 30}
            ]
        }
        
        tasks = common_tasks.copy()
        tasks.extend(type_specific_tasks.get(equipment_type, []))
        
        return tasks
    
    def _estimate_downtime(self, equipment_type: str) -> float:
        """Estimate maintenance downtime in hours."""
        downtime_estimates = {
            "Mixer": 4.0,
            "Tablet Press": 6.0,
            "Coating Pan": 5.0,
            "Granulator": 5.0,
            "Blister Packer": 3.0,
            "Blender": 4.0
        }
        return downtime_estimates.get(equipment_type, 4.0)
    
    def calculate_oee(self, equipment_id: str, period_days: int = 30) -> Dict[str, Any]:
        """
        Calculate Overall Equipment Effectiveness (OEE).
        OEE = Availability × Performance × Quality
        
        Args:
            equipment_id: Equipment identifier
            period_days: Analysis period in days
            
        Returns:
            OEE calculation with breakdown
        """
        try:
            equipment = self.db.get_equipment(equipment_id)
            if not equipment:
                return {"error": "Equipment not found"}
            
            # In production, would query actual production data
            # Placeholder calculations
            
            # Availability = Operating Time / Planned Production Time
            planned_time_hours = period_days * 24  # Could be running 24/7
            downtime_hours = 48  # Maintenance, breakdowns
            operating_time_hours = planned_time_hours - downtime_hours
            availability = operating_time_hours / planned_time_hours
            
            # Performance = (Actual Output / Maximum Possible Output)
            ideal_cycle_time = 0.5  # 0.5 min per unit
            actual_cycle_time = 0.58  # 0.58 min per unit (slower than ideal)
            performance = ideal_cycle_time / actual_cycle_time
            
            # Quality = (Good Units / Total Units Produced)
            total_units = 86400  # Units produced
            defective_units = 1728  # Defective units
            good_units = total_units - defective_units
            quality = good_units / total_units
            
            # Overall OEE
            oee = availability * performance * quality
            oee_percentage = oee * 100
            
            # Losses breakdown
            losses = {
                "availability_loss": {
                    "value": (1 - availability) * 100,
                    "causes": [
                        {"cause": "Planned maintenance", "hours": 24},
                        {"cause": "Unplanned downtime", "hours": 16},
                        {"cause": "Setup/changeover", "hours": 8}
                    ]
                },
                "performance_loss": {
                    "value": (1 - performance) * 100,
                    "causes": [
                        {"cause": "Minor stops", "frequency": 45},
                        {"cause": "Reduced speed", "percentage": 13.8}
                    ]
                },
                "quality_loss": {
                    "value": (1 - quality) * 100,
                    "causes": [
                        {"cause": "Startup rejects", "units": 864},
                        {"cause": "Production rejects", "units": 864}
                    ]
                }
            }
            
            # Benchmarking
            if oee_percentage >= 85:
                rating = "World Class"
            elif oee_percentage >= 60:
                rating = "Good"
            elif oee_percentage >= 40:
                rating = "Fair"
            else:
                rating = "Poor"
            
            # Recommendations
            recommendations = []
            if availability < 0.90:
                recommendations.append("Focus on reducing downtime - implement TPM (Total Productive Maintenance)")
            if performance < 0.95:
                recommendations.append("Optimize cycle times - address minor stops and speed losses")
            if quality < 0.99:
                recommendations.append("Improve quality controls - reduce startup and production rejects")
            
            oee_report = {
                "equipment_id": equipment_id,
                "equipment_name": equipment.get("name"),
                "analysis_period_days": period_days,
                "oee_percentage": round(oee_percentage, 2),
                "rating": rating,
                "components": {
                    "availability": round(availability * 100, 2),
                    "performance": round(performance * 100, 2),
                    "quality": round(quality * 100, 2)
                },
                "metrics": {
                    "planned_time_hours": planned_time_hours,
                    "operating_time_hours": operating_time_hours,
                    "downtime_hours": downtime_hours,
                    "total_units": total_units,
                    "good_units": good_units,
                    "defective_units": defective_units
                },
                "losses": losses,
                "recommendations": recommendations,
                "calculated_at": datetime.utcnow().isoformat(),
                "agent": self.agent_name
            }
            
            return oee_report
            
        except Exception as e:
            logger.error(f"Error calculating OEE: {str(e)}")
            return {"error": str(e)}
    
    def track_calibrations(self, days_ahead: int = 30) -> Dict[str, Any]:
        """
        Track equipment calibrations due within specified period.
        
        Args:
            days_ahead: Days to look ahead
            
        Returns:
            Calibration tracking report
        """
        try:
            # Get all equipment
            operational_equipment = self.db.get_operational_equipment()
            
            # Check calibration due dates
            due_soon = []
            overdue = []
            
            for equipment in operational_equipment:
                next_calibration = equipment.get("next_calibration_date")
                if not next_calibration:
                    continue
                
                calibration_dt = datetime.fromisoformat(next_calibration.replace('Z', '+00:00'))
                days_until = (calibration_dt - datetime.utcnow()).days
                
                equipment_info = {
                    "equipment_id": equipment.get("equipment_id"),
                    "name": equipment.get("name"),
                    "type": equipment.get("equipment_type"),
                    "next_calibration_date": next_calibration,
                    "days_until_calibration": days_until,
                    "calibration_frequency_days": equipment.get("calibration_frequency_days", 365)
                }
                
                if days_until < 0:
                    equipment_info["status"] = "OVERDUE"
                    overdue.append(equipment_info)
                elif days_until <= days_ahead:
                    equipment_info["status"] = "DUE SOON"
                    due_soon.append(equipment_info)
            
            # Sort by urgency
            overdue.sort(key=lambda x: x["days_until_calibration"])
            due_soon.sort(key=lambda x: x["days_until_calibration"])
            
            report = {
                "total_equipment": len(operational_equipment),
                "overdue_calibrations": {
                    "count": len(overdue),
                    "equipment": overdue,
                    "urgency": "CRITICAL"
                },
                "due_soon": {
                    "count": len(due_soon),
                    "equipment": due_soon,
                    "urgency": "HIGH"
                },
                "recommendations": [
                    "Schedule calibrations immediately for overdue equipment",
                    "Plan calibrations during scheduled maintenance windows",
                    "Ensure qualified technicians are available",
                    "Prepare calibration standards and documentation"
                ] if (len(overdue) + len(due_soon)) > 0 else ["All calibrations up to date"],
                "checked_at": datetime.utcnow().isoformat(),
                "days_ahead": days_ahead,
                "agent": self.agent_name
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error tracking calibrations: {str(e)}")
            return {"error": str(e)}
    
    def analyze_downtime(self, equipment_id: str, period_days: int = 30) -> Dict[str, Any]:
        """
        Analyze equipment downtime patterns.
        
        Args:
            equipment_id: Equipment identifier
            period_days: Analysis period in days
            
        Returns:
            Downtime analysis report
        """
        try:
            equipment = self.db.get_equipment(equipment_id)
            if not equipment:
                return {"error": "Equipment not found"}
            
            # In production, would query actual downtime events
            # Placeholder data
            
            downtime_events = [
                {
                    "date": "2025-01-15",
                    "duration_hours": 4.5,
                    "reason": "Planned maintenance",
                    "category": "planned"
                },
                {
                    "date": "2025-01-22",
                    "duration_hours": 2.0,
                    "reason": "Belt replacement",
                    "category": "planned"
                },
                {
                    "date": "2025-01-28",
                    "duration_hours": 6.5,
                    "reason": "Motor failure",
                    "category": "breakdown"
                },
                {
                    "date": "2025-02-03",
                    "duration_hours": 1.5,
                    "reason": "Sensor malfunction",
                    "category": "breakdown"
                }
            ]
            
            # Calculate statistics
            total_downtime_hours = sum(e["duration_hours"] for e in downtime_events)
            planned_downtime = sum(e["duration_hours"] for e in downtime_events if e["category"] == "planned")
            unplanned_downtime = sum(e["duration_hours"] for e in downtime_events if e["category"] == "breakdown")
            
            total_hours = period_days * 24
            availability = (total_hours - total_downtime_hours) / total_hours * 100
            
            # Breakdown causes
            causes = {}
            for event in downtime_events:
                reason = event["reason"]
                causes[reason] = causes.get(reason, 0) + event["duration_hours"]
            
            # Top causes
            top_causes = sorted(
                [{"cause": k, "hours": v} for k, v in causes.items()],
                key=lambda x: x["hours"],
                reverse=True
            )
            
            # Trends and recommendations
            recommendations = []
            
            if unplanned_downtime > planned_downtime:
                recommendations.append("⚠️ Unplanned downtime exceeds planned - implement predictive maintenance")
            
            if "failure" in str(downtime_events).lower():
                recommendations.append("Address recurring failure modes through root cause analysis")
            
            if total_downtime_hours > (total_hours * 0.10):
                recommendations.append("Downtime exceeds 10% - review maintenance strategy")
            
            recommendations.append("Maintain spare parts inventory for critical components")
            recommendations.append("Train operators on preventive checks")
            
            analysis = {
                "equipment_id": equipment_id,
                "equipment_name": equipment.get("name"),
                "analysis_period_days": period_days,
                "total_downtime_hours": round(total_downtime_hours, 2),
                "planned_downtime_hours": round(planned_downtime, 2),
                "unplanned_downtime_hours": round(unplanned_downtime, 2),
                "availability_percentage": round(availability, 2),
                "downtime_events": len(downtime_events),
                "event_details": downtime_events,
                "top_causes": top_causes,
                "recommendations": recommendations,
                "analyzed_at": datetime.utcnow().isoformat(),
                "agent": self.agent_name
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing downtime: {str(e)}")
            return {"error": str(e)}
    
    def predict_maintenance_needs(self, equipment_id: str) -> Dict[str, Any]:
        """
        Predict maintenance needs using predictive maintenance algorithms.
        
        Args:
            equipment_id: Equipment identifier
            
        Returns:
            Predictive maintenance recommendations
        """
        try:
            equipment = self.db.get_equipment(equipment_id)
            if not equipment:
                return {"error": "Equipment not found"}
            
            # In production, would use ML models based on:
            # - Sensor data (temperature, vibration, pressure)
            # - Historical failure patterns
            # - Maintenance records
            # - Operating hours
            
            # Placeholder predictive analysis
            equipment_age_years = 5  # Would calculate from installation date
            operating_hours = 12000  # Would get from equipment logs
            
            # Risk scoring
            risk_factors = {
                "age": equipment_age_years / 15 * 100,  # 15 year expected life
                "usage": operating_hours / 20000 * 100,  # 20k hours expected
                "maintenance_compliance": 85,  # Based on maintenance history
                "failure_history": 15  # Based on past failures
            }
            
            overall_risk = (
                risk_factors["age"] * 0.25 +
                risk_factors["usage"] * 0.25 +
                (100 - risk_factors["maintenance_compliance"]) * 0.30 +
                risk_factors["failure_history"] * 0.20
            )
            
            # Prediction
            if overall_risk > 70:
                prediction = "HIGH RISK - Maintenance needed within 30 days"
                priority = "urgent"
            elif overall_risk > 50:
                prediction = "MODERATE RISK - Schedule maintenance within 60 days"
                priority = "medium"
            else:
                prediction = "LOW RISK - Continue normal maintenance schedule"
                priority = "low"
            
            # Component-specific predictions
            components_at_risk = []
            if equipment_age_years > 4:
                components_at_risk.append({
                    "component": "Motor bearings",
                    "risk_level": "high",
                    "recommended_action": "Replace during next maintenance"
                })
            if operating_hours > 10000:
                components_at_risk.append({
                    "component": "Drive belts",
                    "risk_level": "medium",
                    "recommended_action": "Inspect and replace if worn"
                })
            
            prediction_report = {
                "equipment_id": equipment_id,
                "equipment_name": equipment.get("name"),
                "equipment_type": equipment.get("equipment_type"),
                "equipment_age_years": equipment_age_years,
                "operating_hours": operating_hours,
                "risk_factors": risk_factors,
                "overall_risk_score": round(overall_risk, 2),
                "prediction": prediction,
                "priority": priority,
                "components_at_risk": components_at_risk,
                "recommended_actions": [
                    "Schedule detailed inspection",
                    "Monitor equipment performance closely",
                    "Prepare spare parts inventory",
                    "Plan maintenance window"
                ] if priority in ["urgent", "medium"] else ["Continue routine monitoring"],
                "predicted_at": datetime.utcnow().isoformat(),
                "agent": self.agent_name
            }
            
            return prediction_report
            
        except Exception as e:
            logger.error(f"Error predicting maintenance needs: {str(e)}")
            return {"error": str(e)}


# Main execution for testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    agent = EquipmentMaintenanceAgent()
    print(f"✅ {agent.agent_name} initialized successfully")
    
    # Test calibration tracking
    # result = agent.track_calibrations(30)
    # print(json.dumps(result, indent=2))
