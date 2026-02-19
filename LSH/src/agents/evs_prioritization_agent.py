"""
EVS Task Prioritization Agent

Prioritizes EVS tasks based on multiple factors including urgency, location, and patient safety.
Uses real Astra DB data for task management.
"""

import sys
import os
from typing import Dict, Any, List
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database.astra_helper import get_db_helper
from .base_agent import HealthcareAgentBase


class EVSTaskPrioritizationAgent(HealthcareAgentBase):
    """Agent for prioritizing EVS tasks using real database data."""
    
    def __init__(self, agent_id: str = "evs_task_prioritizer"):
        super().__init__(
            agent_id=agent_id,
            agent_type="evs_task_prioritization",
            description="Prioritizes EVS tasks based on urgency, safety, and operational needs"
        )
        self.db = get_db_helper()
        
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prioritize EVS tasks.
        
        Expected input_data:
        {
            "location": Optional[str],  # Filter by location
            "include_assigned": bool,   # Include already assigned tasks
            "priority_filter": Optional[str]  # Filter by priority level
        }
        """
        location = input_data.get("location")
        include_assigned = input_data.get("include_assigned", False)
        priority_filter = input_data.get("priority_filter")
        
        self.log_action("prioritize_tasks", {
            "location": location,
            "include_assigned": include_assigned
        })
        
        # Get pending tasks from database
        pending_tasks = self.db.get_evs_tasks_by_status("scheduled", limit=100)
        
        # Filter by location if specified
        if location:
            pending_tasks = [t for t in pending_tasks if t.get("location") == location]
        
        # Filter by priority if specified
        if priority_filter:
            pending_tasks = [t for t in pending_tasks if t.get("priority") == priority_filter]
        
        # Filter out assigned tasks if requested
        if not include_assigned:
            assigned_statuses = ["assigned", "in_progress", "completed"]
            pending_tasks = [t for t in pending_tasks if t.get("status") not in assigned_statuses]
        
        if not pending_tasks:
            return {
                "success": True,
                "prioritized_tasks": [],
                "message": "No pending tasks to prioritize"
            }
        
        # Calculate priority scores for all tasks
        prioritized_tasks = []
        for task in pending_tasks:
            score = self._calculate_priority_score(task)
            prioritized_tasks.append({
                **task,
                "priority_score": score,
                "priority_reasoning": self._get_priority_reasoning(task, score)
            })
        
        # Sort by priority score (descending)
        prioritized_tasks.sort(key=lambda x: x["priority_score"], reverse=True)
        
        # Enhance with assignment recommendations
        enhanced_tasks = await self._add_assignment_recommendations(prioritized_tasks)
        
        # Generate scheduling recommendations
        schedule = self._generate_task_schedule(enhanced_tasks)
        
        # Log activity to database
        self.db.log_agent_activity(
            agent_name=self.agent_id,
            action_type="prioritize_tasks",
            input_data={
                "location": location,
                "priority_filter": priority_filter,
                "include_assigned": include_assigned
            },
            output_data={
                "total_tasks": len(prioritized_tasks),
                "highest_priority_task": prioritized_tasks[0]["task_id"] if prioritized_tasks else None,
                "highest_priority_score": prioritized_tasks[0]["priority_score"] if prioritized_tasks else 0
            },
            success=True
        )
        
        return {
            "success": True,
            "prioritized_tasks": enhanced_tasks,
            "total_tasks": len(enhanced_tasks),
            "highest_priority": prioritized_tasks[0] if prioritized_tasks else None,
            "recommended_schedule": schedule,
            "timestamp": datetime.now().isoformat()
        }
    
    def _calculate_priority_score(self, task: Dict[str, Any]) -> float:
        """
        Calculate priority score for a task (0-100)
        
        Factors:
        - Isolation required: +40 points
        - High priority: +30 points
        - Patient nearby: +20 points
        - Overdue: +20 points
        - Terminal clean: +15 points
        """
        score = 0.0
        
        # Isolation rooms highest priority
        if task.get("isolation_required"):
            score += 40
        
        # Priority level
        priority = task.get("priority", "medium").lower()
        if priority == "high":
            score += 30
        elif priority == "medium":
            score += 15
        
        # Patient nearby (room occupied)
        if task.get("patient_nearby"):
            score += 20
        
        # Check if overdue
        scheduled_time = task.get("scheduled_time")
        if scheduled_time:
            try:
                scheduled_dt = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
                if scheduled_dt < datetime.now():
                    score += 20
            except:
                pass
        
        # Task type priority
        task_type = task.get("task_type", "").lower()
        if "terminal" in task_type:
            score += 15
        elif "stat" in task_type or "urgent" in task_type:
            score += 10
        
        return min(score, 100.0)
    
    def _get_priority_reasoning(self, task: Dict[str, Any], score: float) -> str:
        """Generate human-readable reasoning for priority score"""
        reasons = []
        
        if task.get("isolation_required"):
            reasons.append("Isolation protocol required")
        
        if task.get("priority") == "high":
            reasons.append("High priority")
        
        if task.get("patient_nearby"):
            reasons.append("Patient occupying room")
        
        scheduled_time = task.get("scheduled_time")
        if scheduled_time:
            try:
                scheduled_dt = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
                if scheduled_dt < datetime.now():
                    reasons.append("Overdue")
            except:
                pass
        
        task_type = task.get("task_type", "")
        if "terminal" in task_type.lower():
            reasons.append("Terminal cleaning")
        
        if not reasons:
            reasons.append("Standard task")
        
        return " | ".join(reasons)
    
    async def _add_assignment_recommendations(self, 
                                            prioritized_tasks: List[Dict]) -> List[Dict]:
        """Add staff assignment recommendations to prioritized tasks."""
        # Get available staff from database
        available_staff = self.db.get_available_evs_staff()
        
        enhanced_tasks = []
        
        for task in prioritized_tasks:
            task_copy = task.copy()
            
            # Find best staff for this task
            best_staff = self._find_best_staff_for_task(task, available_staff)
            
            if best_staff:
                task_copy["assignment_recommendation"] = {
                    "staff_id": best_staff["staff_id"],
                    "staff_name": best_staff["name"],
                    "certification": best_staff.get("certification_level"),
                    "performance_rating": best_staff.get("performance_rating"),
                    "current_tasks": best_staff.get("current_tasks", 0),
                    "reason": self._get_assignment_reasoning(task, best_staff),
                    "confidence": 0.85
                }
            else:
                task_copy["assignment_recommendation"] = {
                    "status": "no_staff_available",
                    "reason": "No suitable staff available for this task"
                }
            
            enhanced_tasks.append(task_copy)
        
        return enhanced_tasks
    
    def _find_best_staff_for_task(self, task: Dict[str, Any], available_staff: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find the best staff member for a given task"""
        if not available_staff:
            return None
        
        scored_staff = []
        
        for staff in available_staff:
            score = 0.0
            
            # Certification level
            cert_level = staff.get("certification_level", "Basic")
            if task.get("isolation_required"):
                if cert_level == "Advanced":
                    score += 40
                elif cert_level == "Intermediate":
                    score += 20
                else:
                    continue  # Skip basic for isolation tasks
            else:
                score += 10
            
            # Performance rating
            performance = staff.get("performance_rating", 3.0)
            score += performance * 10
            
            # Availability
            if staff.get("status") == "available":
                score += 20
            
            # Workload
            current_tasks = staff.get("current_tasks", 0)
            if current_tasks == 0:
                score += 15
            elif current_tasks == 1:
                score += 10
            elif current_tasks == 2:
                score += 5
            
            scored_staff.append({
                "staff": staff,
                "score": score
            })
        
        if scored_staff:
            scored_staff.sort(key=lambda x: x["score"], reverse=True)
            return scored_staff[0]["staff"]
        
        return None
    
    def _get_assignment_reasoning(self, task: Dict[str, Any], staff: Dict[str, Any]) -> str:
        """Generate reasoning for staff assignment"""
        reasons = []
        
        cert_level = staff.get("certification_level")
        reasons.append(f"{cert_level} certification")
        
        if task.get("isolation_required"):
            reasons.append("Qualified for isolation")
        
        performance = staff.get("performance_rating", 0)
        if performance >= 4.0:
            reasons.append(f"High rating ({performance}/5)")
        
        current_tasks = staff.get("current_tasks", 0)
        if current_tasks == 0:
            reasons.append("No current tasks")
        
        return " | ".join(reasons)
    
    def _generate_task_schedule(self, prioritized_tasks: List[Dict]) -> Dict[str, Any]:
        """Generate recommended task schedule."""
        # Group tasks by urgency
        immediate = []  # Tasks with priority_score > 80
        urgent = []  # Tasks with priority_score 60-80
        standard = []  # Tasks with priority_score < 60
        
        for task in prioritized_tasks:
            score = task.get("priority_score", 0)
            if score > 80:
                immediate.append(task)
            elif score >= 60:
                urgent.append(task)
            else:
                standard.append(task)
        
        return {
            "immediate_tasks": {
                "count": len(immediate),
                "task_ids": [t["task_id"] for t in immediate],
                "recommended_action": "Assign immediately, interrupt current low-priority tasks if needed"
            },
            "urgent_tasks": {
                "count": len(urgent),
                "task_ids": [t["task_id"] for t in urgent],
                "recommended_action": "Assign within next 30 minutes"
            },
            "standard_tasks": {
                "count": len(standard),
                "task_ids": [t["task_id"] for t in standard],
                "recommended_action": "Schedule based on staff availability and workflow"
            },
            "total_estimated_time_minutes": sum(
                t.get("estimated_duration", 30) for t in prioritized_tasks
            )
        }
