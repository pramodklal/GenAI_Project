"""
EVS Task Management MCP Server

Provides tools for environmental services task management, scheduling, and monitoring.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from .base_mcp_server import MCPServerBase
from database.astra_helper import get_db_helper


class EVSTaskMCPServer(MCPServerBase):
    """MCP Server for EVS task management operations."""
    
    def __init__(self):
        super().__init__("evs_task_management", version="1.0.0")
        self.db = get_db_helper()
        
    def _register_endpoints(self):
        """Register all EVS task management endpoints."""
        
        self.register_endpoint(
            name="create_task",
            handler=self._create_task,
            required_params=["location", "task_type"],
            description="Create a new EVS task"
        )
        
        self.register_endpoint(
            name="get_pending_tasks",
            handler=self._get_pending_tasks,
            required_params=[],
            description="Get list of pending EVS tasks"
        )
        
        self.register_endpoint(
            name="assign_task",
            handler=self._assign_task,
            required_params=["task_id", "staff_id"],
            description="Assign a task to EVS staff member"
        )
        
        self.register_endpoint(
            name="update_task_status",
            handler=self._update_task_status,
            required_params=["task_id", "status"],
            description="Update task status"
        )
        
        self.register_endpoint(
            name="get_staff_availability",
            handler=self._get_staff_availability,
            required_params=[],
            description="Get EVS staff availability"
        )
        
        self.register_endpoint(
            name="get_environmental_metrics",
            handler=self._get_environmental_metrics,
            required_params=["location"],
            description="Get environmental monitoring metrics"
        )
        
        self.register_endpoint(
            name="prioritize_tasks",
            handler=self._prioritize_tasks,
            required_params=["task_ids"],
            description="Calculate priority scores for tasks"
        )
    
    def _create_task(self, location: str, task_type: str, 
                    priority: Optional[str] = "medium",
                    description: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new EVS task.
        
        Args:
            location: Room or area identifier
            task_type: Type of task (cleaning, disinfection, maintenance)
            priority: Task priority (low, medium, high, critical)
            description: Additional task details
            
        Returns:
            Created task information
        """
        task_id = f"EVS-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        # Validate task type
        valid_types = ["terminal_cleaning", "daily_cleaning", "disinfection", 
                      "maintenance", "spill_cleanup", "inspection"]
        
        if task_type not in valid_types:
            return {
                "success": False,
                "error": f"Invalid task type. Must be one of: {valid_types}"
            }
        
        # Estimate duration based on task type
        duration_map = {
            "terminal_cleaning": 60,
            "daily_cleaning": 30,
            "disinfection": 45,
            "maintenance": 40,
            "spill_cleanup": 20,
            "inspection": 15
        }
        
        task_data = {
            "task_id": task_id,
            "location": location,
            "task_type": task_type,
            "priority": priority,
            "description": description or f"{task_type} for {location}",
            "status": "pending",
            "estimated_duration_minutes": duration_map.get(task_type, 30),
            "created_at": datetime.utcnow().isoformat(),
            "due_by": (datetime.utcnow() + timedelta(hours=2)).isoformat()
        }
        
        # Save to database
        try:
            self.db.create_evs_task(task_data)
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to save task to database: {str(e)}"
            }
        
        return {
            "success": True,
            "data": task_data
        }
    
    def _get_pending_tasks(self, location: Optional[str] = None,
                          priority: Optional[str] = None,
                          task_type: Optional[str] = None) -> Dict[str, Any]:
        """Get list of pending EVS tasks with optional filters from database."""
        try:
            # Get tasks from database
            all_tasks = self.db.get_evs_tasks()
            
            # Filter to pending/assigned/in_progress tasks
            tasks = [t for t in all_tasks if t.get("status") in ["pending", "assigned", "in_progress"]]
            
            # Apply additional filters
            if location:
                tasks = [t for t in tasks if location.lower() in t.get("location", "").lower()]
            if priority:
                tasks = [t for t in tasks if t.get("priority") == priority]
            if task_type:
                tasks = [t for t in tasks if t.get("task_type") == task_type]
            
            return {
                "success": True,
                "data": {
                    "tasks": tasks,
                    "total_pending": len(tasks),
                    "by_priority": {
                        "critical": len([t for t in tasks if t.get("priority") == "critical"]),
                        "high": len([t for t in tasks if t.get("priority") == "high"]),
                        "medium": len([t for t in tasks if t.get("priority") == "medium"]),
                        "low": len([t for t in tasks if t.get("priority") == "low"])
                    },
                    "retrieved_at": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to retrieve tasks: {str(e)}"
            }
    
    def _assign_task(self, task_id: str, staff_id: str,
                    notes: Optional[str] = None) -> Dict[str, Any]:
        """Assign a task to EVS staff member."""
        return {
            "success": True,
            "task_id": task_id,
            "assigned_to": staff_id,
            "assigned_at": datetime.utcnow().isoformat(),
            "status": "assigned",
            "notes": notes,
            "estimated_start": datetime.utcnow().isoformat(),
            "estimated_completion": (datetime.utcnow() + timedelta(minutes=45)).isoformat()
        }
    
    def _update_task_status(self, task_id: str, status: str,
                           completion_notes: Optional[str] = None) -> Dict[str, Any]:
        """Update task status."""
        valid_statuses = ["pending", "assigned", "in_progress", "completed", 
                         "delayed", "cancelled", "requires_inspection"]
        
        if status not in valid_statuses:
            return {
                "success": False,
                "error": f"Invalid status. Must be one of: {valid_statuses}"
            }
        
        response = {
            "success": True,
            "task_id": task_id,
            "old_status": "in_progress",
            "new_status": status,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if status == "completed":
            response["completed_at"] = datetime.utcnow().isoformat()
            response["completion_notes"] = completion_notes
            response["quality_check_required"] = True
        
        return response
    
    def _get_staff_availability(self, shift: Optional[str] = None,
                               location: Optional[str] = None) -> Dict[str, Any]:
        """Get EVS staff availability."""
        # Mock staff availability
        staff_members = [
            {
                "staff_id": "EVS-001",
                "name": "John Smith",
                "role": "EVS Technician",
                "shift": "day",
                "location": "Floor 3",
                "status": "available",
                "current_task": None,
                "certifications": ["terminal_cleaning", "disinfection"],
                "workload_capacity": 0.3  # 30% utilized
            },
            {
                "staff_id": "EVS-002",
                "name": "Maria Garcia",
                "role": "EVS Supervisor",
                "shift": "day",
                "location": "Floor 2",
                "status": "busy",
                "current_task": "EVS-20241217-001",
                "certifications": ["terminal_cleaning", "disinfection", "inspection"],
                "workload_capacity": 0.8
            },
            {
                "staff_id": "EVS-003",
                "name": "David Lee",
                "role": "EVS Technician",
                "shift": "night",
                "location": "Floor 1",
                "status": "available",
                "current_task": None,
                "certifications": ["daily_cleaning", "maintenance"],
                "workload_capacity": 0.2
            }
        ]
        
        # Apply filters
        if shift:
            staff_members = [s for s in staff_members if s["shift"] == shift]
        if location:
            staff_members = [s for s in staff_members if location.lower() in s["location"].lower()]
        
        return {
            "staff_members": staff_members,
            "total_staff": len(staff_members),
            "available_count": len([s for s in staff_members if s["status"] == "available"]),
            "average_workload": sum(s["workload_capacity"] for s in staff_members) / len(staff_members) if staff_members else 0,
            "retrieved_at": datetime.utcnow().isoformat()
        }
    
    def _get_environmental_metrics(self, location: str,
                                  metric_type: Optional[str] = None) -> Dict[str, Any]:
        """Get environmental monitoring metrics."""
        # Mock environmental metrics
        metrics = {
            "location": location,
            "temperature": {
                "current": 72.5,
                "target": 72.0,
                "unit": "fahrenheit",
                "status": "normal"
            },
            "humidity": {
                "current": 45,
                "target_range": [40, 60],
                "unit": "percent",
                "status": "normal"
            },
            "air_quality": {
                "particulate_matter": 12,
                "unit": "ug/m3",
                "status": "good",
                "last_filter_change": (datetime.utcnow() - timedelta(days=15)).isoformat()
            },
            "cleanliness_score": {
                "score": 95,
                "scale": 100,
                "last_inspection": (datetime.utcnow() - timedelta(hours=8)).isoformat(),
                "status": "excellent"
            },
            "alerts": []
        }
        
        # Add alert if any metric is out of range
        if metrics["temperature"]["current"] > 75:
            metrics["alerts"].append({
                "type": "temperature",
                "severity": "warning",
                "message": "Temperature above target range"
            })
        
        if metric_type and metric_type in metrics:
            return {
                "location": location,
                "metric_type": metric_type,
                "value": metrics[metric_type],
                "measured_at": datetime.utcnow().isoformat()
            }
        
        return {
            "location": location,
            "metrics": metrics,
            "measured_at": datetime.utcnow().isoformat()
        }
    
    def _prioritize_tasks(self, task_ids: List[str]) -> Dict[str, Any]:
        """
        Calculate priority scores for tasks using multiple factors.
        
        Factors considered:
        - Urgency (time until due)
        - Patient safety impact
        - Location criticality
        - Task type severity
        """
        # Get tasks
        all_tasks = self._get_pending_tasks()["pending_tasks"]
        tasks_to_prioritize = [t for t in all_tasks if t["task_id"] in task_ids]
        
        prioritized = []
        for task in tasks_to_prioritize:
            # Calculate urgency score (0-100)
            due_time = datetime.fromisoformat(task["due_by"])
            time_until_due = (due_time - datetime.utcnow()).total_seconds() / 60  # minutes
            urgency_score = max(0, min(100, 100 - (time_until_due / 120) * 100))
            
            # Priority weight
            priority_weights = {"critical": 100, "high": 75, "medium": 50, "low": 25}
            priority_score = priority_weights.get(task["priority"], 50)
            
            # Location criticality (mock)
            location_scores = {
                "ICU": 100,
                "OR": 95,
                "ER": 90,
                "Patient Room": 70,
                "Cafeteria": 40,
                "Hallway": 30
            }
            location_score = 50  # default
            for loc_type, score in location_scores.items():
                if loc_type.lower() in task["location"].lower():
                    location_score = score
                    break
            
            # Task type severity
            task_type_scores = {
                "disinfection": 90,
                "terminal_cleaning": 85,
                "spill_cleanup": 80,
                "daily_cleaning": 50,
                "maintenance": 45,
                "inspection": 40
            }
            task_type_score = task_type_scores.get(task["task_type"], 50)
            
            # Weighted final score
            final_score = (
                urgency_score * 0.3 +
                priority_score * 0.3 +
                location_score * 0.25 +
                task_type_score * 0.15
            )
            
            prioritized.append({
                "task_id": task["task_id"],
                "location": task["location"],
                "task_type": task["task_type"],
                "priority_score": round(final_score, 2),
                "urgency_score": round(urgency_score, 2),
                "location_criticality": round(location_score, 2),
                "recommended_order": 0  # Will be set after sorting
            })
        
        # Sort by priority score
        prioritized.sort(key=lambda x: x["priority_score"], reverse=True)
        
        # Set recommended order
        for idx, task in enumerate(prioritized):
            task["recommended_order"] = idx + 1
        
        return {
            "prioritized_tasks": prioritized,
            "total_tasks": len(prioritized),
            "highest_priority": prioritized[0] if prioritized else None,
            "prioritized_at": datetime.utcnow().isoformat()
        }
