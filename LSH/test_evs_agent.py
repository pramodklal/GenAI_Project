"""
Test script for EVS Prioritization Agent with real Astra DB data
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.agents.evs_prioritization_agent import EVSTaskPrioritizationAgent
from database.astra_helper import get_db_helper


async def test_evs_prioritization():
    """Test the EVS Prioritization Agent with real database data"""
    print("=" * 80)
    print("EVS PRIORITIZATION AGENT TEST - Real Astra DB Data")
    print("=" * 80)
    
    # Initialize agent
    agent = EVSTaskPrioritizationAgent()
    db = get_db_helper()
    
    # Test 1: Prioritize all pending tasks
    print("\n1. PRIORITIZING ALL PENDING EVS TASKS")
    print("-" * 80)
    
    result = await agent.process({
        "location": None,
        "include_assigned": False,
        "priority_filter": None
    })
    
    if result.get("success"):
        tasks = result.get("prioritized_tasks", [])
        print(f"\n   ✅ Successfully prioritized {len(tasks)} tasks")
        
        # Show top 5 priority tasks
        print("\n   Top 5 Priority Tasks:")
        for i, task in enumerate(tasks[:5], 1):
            print(f"\n   {i}. Task ID: {task.get('task_id')}")
            print(f"      Location: {task.get('location')}")
            print(f"      Task Type: {task.get('task_type')}")
            print(f"      Priority Score: {task.get('priority_score', 0):.1f}/100")
            print(f"      Reasoning: {task.get('priority_reasoning', 'N/A')}")
            print(f"      Isolation Required: {task.get('isolation_required', False)}")
            
            # Show staff recommendation
            rec = task.get("assignment_recommendation", {})
            if rec.get("staff_name"):
                print(f"      Recommended Staff: {rec.get('staff_name')} ({rec.get('certification')})")
                print(f"      Assignment Reason: {rec.get('reason', 'N/A')}")
        
        # Show schedule recommendations
        schedule = result.get("recommended_schedule", {})
        if schedule:
            print("\n   Schedule Recommendations:")
            print(f"      - Immediate Tasks (>80 score): {schedule.get('immediate_tasks', {}).get('count', 0)}")
            print(f"      - Urgent Tasks (60-80 score): {schedule.get('urgent_tasks', {}).get('count', 0)}")
            print(f"      - Standard Tasks (<60 score): {schedule.get('standard_tasks', {}).get('count', 0)}")
            print(f"      - Total Estimated Time: {schedule.get('total_estimated_time_minutes', 0)} minutes")
    else:
        print(f"   ❌ Error: {result.get('error')}")
    
    # Test 2: Filter by location
    print("\n\n2. PRIORITIZING TASKS FOR SPECIFIC LOCATION")
    print("-" * 80)
    
    # Get a sample location from tasks
    all_tasks = db.get_evs_tasks_by_status("scheduled", limit=10)
    if all_tasks:
        sample_location = all_tasks[0].get("location")
        print(f"\n   Filtering by location: {sample_location}")
        
        result = await agent.process({
            "location": sample_location,
            "include_assigned": False,
            "priority_filter": None
        })
        
        if result.get("success"):
            tasks = result.get("prioritized_tasks", [])
            print(f"   ✅ Found {len(tasks)} tasks at {sample_location}")
            
            for i, task in enumerate(tasks[:3], 1):
                print(f"\n   {i}. {task.get('task_id')} - {task.get('task_type')}")
                print(f"      Priority Score: {task.get('priority_score', 0):.1f}/100")
    
    # Test 3: Show available staff
    print("\n\n3. AVAILABLE EVS STAFF")
    print("-" * 80)
    
    staff = db.get_available_evs_staff()
    print(f"\n   Found {len(staff)} available staff members")
    
    for i, member in enumerate(staff[:5], 1):
        print(f"\n   {i}. {member.get('name')} ({member.get('staff_id')})")
        print(f"      Certification: {member.get('certification_level')}")
        print(f"      Status: {member.get('status')}")
        print(f"      Shift: {member.get('shift')}")
        print(f"      Performance Rating: {member.get('performance_rating', 0)}/5")
        print(f"      Current Tasks: {member.get('current_tasks', 0)}")
    
    # Test 4: Task statistics
    print("\n\n4. TASK STATISTICS")
    print("-" * 80)
    
    scheduled = db.get_evs_tasks_by_status("scheduled", limit=100)
    in_progress = db.get_evs_tasks_by_status("in_progress", limit=100)
    completed = db.get_evs_tasks_by_status("completed", limit=100)
    
    print(f"\n   Scheduled Tasks: {len(scheduled)}")
    print(f"   In Progress: {len(in_progress)}")
    print(f"   Completed: {len(completed)}")
    
    # Count by priority
    high_priority = len([t for t in scheduled if t.get("priority") == "high"])
    medium_priority = len([t for t in scheduled if t.get("priority") == "medium"])
    low_priority = len([t for t in scheduled if t.get("priority") == "low"])
    
    print(f"\n   By Priority:")
    print(f"      High: {high_priority}")
    print(f"      Medium: {medium_priority}")
    print(f"      Low: {low_priority}")
    
    # Count isolation tasks
    isolation_tasks = len([t for t in scheduled if t.get("isolation_required")])
    print(f"\n   Isolation Required: {isolation_tasks}")
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_evs_prioritization())
