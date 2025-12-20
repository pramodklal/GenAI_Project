"""
EVS Task Management Page - Streamlit UI

Environmental Services task prioritization and assignment.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from mcp_servers import EVSTaskMCPServer
from agents import EVSTaskPrioritizationAgent

# Initialize services
@st.cache_resource
def get_services():
    evs_mcp = EVSTaskMCPServer()
    evs_agent = EVSTaskPrioritizationAgent()
    evs_agent.register_mcp_server("evs_task", evs_mcp)
    return evs_mcp, evs_agent

evs_mcp, evs_agent = get_services()

# Page header
st.markdown("# 🧹 EVS Task Management")
st.markdown("### AI-Powered Task Prioritization & Scheduling")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📋 Tasks", "➕ Create Task", "👥 Staff", "🤖 AI Prioritization"])

with tab1:
    st.markdown("## Task Dashboard")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.multiselect(
            "Filter by Status",
            ["pending", "assigned", "in_progress", "completed"],
            default=["pending", "assigned", "in_progress"]
        )
    with col2:
        priority_filter = st.multiselect(
            "Filter by Priority",
            ["high", "medium", "low"],
            default=["high", "medium", "low"]
        )
    with col3:
        if st.button("🔄 Refresh Tasks", use_container_width=True):
            st.rerun()
    
    # Get pending tasks
    with st.spinner("Loading tasks..."):
        tasks_result = evs_mcp.call_endpoint("get_pending_tasks", {})
        
        if tasks_result.get("success"):
            tasks_data = tasks_result["data"]
            tasks = tasks_data.get("tasks", [])
            
            # Filter tasks
            filtered_tasks = [
                task for task in tasks
                if task.get("status") in status_filter
                and task.get("priority") in priority_filter
            ]
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Tasks", len(filtered_tasks))
            with col2:
                high_priority = sum(1 for task in filtered_tasks if task.get("priority") == "high")
                st.metric("High Priority", high_priority, delta=None if high_priority == 0 else -high_priority, delta_color="inverse")
            with col3:
                pending = sum(1 for task in filtered_tasks if task.get("status") == "pending")
                st.metric("Pending", pending)
            with col4:
                in_progress = sum(1 for task in filtered_tasks if task.get("status") == "in_progress")
                st.metric("In Progress", in_progress)
            
            st.markdown("---")
            
            # Display tasks
            if filtered_tasks:
                # Sort by priority and created time
                priority_order = {"high": 0, "medium": 1, "low": 2}
                sorted_tasks = sorted(
                    filtered_tasks,
                    key=lambda x: (priority_order.get(x.get("priority", "low"), 3), x.get("created_at", ""))
                )
                
                for task in sorted_tasks:
                    # Priority icon
                    priority_icons = {
                        "high": "🔴",
                        "medium": "🟡",
                        "low": "🟢"
                    }
                    priority_icon = priority_icons.get(task.get("priority", "low"), "")
                    
                    # Status badge
                    status_colors = {
                        "pending": "orange",
                        "assigned": "blue",
                        "in_progress": "purple",
                        "completed": "green"
                    }
                    status_color = status_colors.get(task.get("status", "pending"), "gray")
                    
                    with st.expander(
                        f"{priority_icon} {task['task_id']} - {task['task_type'].replace('_', ' ').title()} ({task.get('location', 'Unknown')})",
                        expanded=task.get("priority") == "high"
                    ):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**Type:** {task['task_type'].replace('_', ' ').title()}")
                            st.markdown(f"**Location:** {task.get('location', 'N/A')}")
                            st.markdown(f"**Priority:** {priority_icon} {task.get('priority', 'N/A').upper()}")
                            st.markdown(f"**Status:** :{status_color}[{task.get('status', 'N/A').upper()}]")
                        
                        with col2:
                            st.markdown(f"**Created:** {task.get('created_at', 'N/A')[:16]}")
                            if task.get('assigned_to'):
                                st.markdown(f"**Assigned to:** {task['assigned_to']}")
                            if task.get('estimated_duration_minutes'):
                                st.markdown(f"**Duration:** {task['estimated_duration_minutes']} min")
                            if task.get('patient_nearby'):
                                st.markdown("⚕️ **Patient Nearby**")
                        
                        # Task description
                        if task.get('description'):
                            st.markdown("**Description:**")
                            st.info(task['description'])
                        
                        # Actions
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if task.get("status") == "pending" and st.button("✅ Assign", key=f"assign_{task['task_id']}"):
                                st.info("Use AI Prioritization tab for smart assignment")
                        
                        with col2:
                            if task.get("status") in ["assigned", "in_progress"] and st.button("📝 Update", key=f"update_{task['task_id']}"):
                                # Update status
                                new_status = "completed" if task.get("status") == "in_progress" else "in_progress"
                                update_result = evs_mcp.call_endpoint(
                                    "update_task_status",
                                    {
                                        "task_id": task["task_id"],
                                        "new_status": new_status,
                                        "updated_by": "UI_USER"
                                    }
                                )
                                if update_result.get("success"):
                                    st.success(f"Task updated to {new_status}")
                                    st.rerun()
                        
                        with col3:
                            if st.button("📊 Details", key=f"details_{task['task_id']}"):
                                st.json(task)
            else:
                st.info("No tasks match the selected filters")
        else:
            st.error("Failed to load tasks")

with tab2:
    st.markdown("## ➕ Create New Task")
    
    # Task creation form
    with st.form("create_task_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            task_type = st.selectbox(
                "Task Type",
                ["room_cleaning", "terminal_cleaning", "spill_response", "trash_removal", "restroom_cleaning", "common_area"],
                format_func=lambda x: x.replace("_", " ").title()
            )
            
            location = st.text_input(
                "Location",
                placeholder="e.g., Room 301, Floor 3 Hallway"
            )
            
            priority = st.selectbox(
                "Priority",
                ["high", "medium", "low"],
                index=1
            )
        
        with col2:
            patient_nearby = st.checkbox("Patient Nearby", value=False)
            
            isolation_required = st.checkbox("Isolation Precautions", value=False)
            
            estimated_duration = st.number_input(
                "Estimated Duration (minutes)",
                min_value=5,
                max_value=240,
                value=30,
                step=5
            )
        
        description = st.text_area(
            "Description",
            placeholder="Additional details about the task..."
        )
        
        submitted = st.form_submit_button("✅ Create Task", type="primary", use_container_width=True)
        
        if submitted:
            if not location:
                st.error("Location is required")
            else:
                with st.spinner("Creating task..."):
                    create_result = evs_mcp.call_endpoint(
                        "create_task",
                        {
                            "task_type": task_type,
                            "location": location,
                            "priority": priority,
                            "description": description,
                            "patient_nearby": patient_nearby,
                            "isolation_required": isolation_required,
                            "estimated_duration_minutes": estimated_duration
                        }
                    )
                    
                    if create_result.get("success"):
                        task_data = create_result["data"]
                        st.markdown(f"""
                            <div class="success-box">
                                <h3>✅ Task Created Successfully!</h3>
                                <p><strong>Task ID:</strong> {task_data.get('task_id')}</p>
                                <p><strong>Priority:</strong> {task_data.get('priority').upper()}</p>
                                <p><strong>Status:</strong> {task_data.get('status').upper()}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        st.balloons()
                    else:
                        st.error("Failed to create task")

with tab3:
    st.markdown("## 👥 Staff Availability")
    
    # Shift selection
    col1, col2 = st.columns([2, 1])
    with col1:
        shift = st.selectbox(
            "Select Shift",
            ["morning", "afternoon", "evening", "night"],
            index=0
        )
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    # Get staff availability
    with st.spinner("Loading staff availability..."):
        staff_result = evs_mcp.call_endpoint(
            "get_staff_availability",
            {"shift": shift}
        )
        
        if staff_result.get("success"):
            staff_data = staff_result["data"]
            staff_list = staff_data.get("staff", [])
            
            # Summary
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Staff", len(staff_list))
            with col2:
                available_count = sum(1 for s in staff_list if s.get("available"))
                st.metric("Available", available_count)
            with col3:
                assigned_count = sum(1 for s in staff_list if s.get("current_task"))
                st.metric("Assigned", assigned_count)
            
            st.markdown("---")
            
            # Display staff
            for staff in staff_list:
                status_icon = "✅" if staff.get("available") else "🔴"
                
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                    
                    with col1:
                        st.markdown(f"### {status_icon} {staff['staff_id']}")
                        st.caption(f"Shift: {staff.get('shift', 'N/A').title()}")
                    
                    with col2:
                        st.markdown(f"**Status:** {staff.get('status', 'N/A').title()}")
                        if staff.get('current_task'):
                            st.markdown(f"📝 Task: {staff['current_task']}")
                    
                    with col3:
                        st.markdown(f"**Location:** {staff.get('current_location', 'N/A')}")
                        if staff.get('skills'):
                            st.caption(f"Skills: {', '.join(staff['skills'])}")
                    
                    with col4:
                        tasks_completed = staff.get('tasks_completed_today', 0)
                        st.metric("Today", tasks_completed)
                    
                    st.markdown("---")
        else:
            st.error("Failed to load staff availability")

with tab4:
    st.markdown("## 🤖 AI-Powered Task Prioritization")
    st.markdown("Let AI analyze and prioritize pending tasks for optimal assignment.")
    
    # Options
    with st.expander("⚙️ Prioritization Options"):
        consider_staff = st.checkbox("Consider Staff Availability", value=True)
        consider_equipment = st.checkbox("Consider Equipment Status", value=True)
        consider_environment = st.checkbox("Consider Environmental Metrics", value=True)
    
    # Run prioritization
    if st.button("🤖 Run AI Prioritization", type="primary", use_container_width=True):
        with st.spinner("🤖 AI Agent analyzing tasks and optimizing priorities..."):
            async def prioritize():
                return await evs_agent.process({
                    "analysis_type": "full",
                    "include_assignments": True,
                    "shift": "current"
                })
            
            priority_result = asyncio.run(prioritize())
            st.session_state["priority_analysis"] = priority_result
            
            if priority_result.get("success"):
                st.success("✅ Prioritization analysis completed")
                
                # Display summary
                summary = priority_result.get("summary", {})
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Tasks Analyzed", summary.get("tasks_analyzed", 0))
                with col2:
                    st.metric("High Priority", summary.get("high_priority_count", 0))
                with col3:
                    st.metric("Assignments", summary.get("assignments_recommended", 0))
                with col4:
                    st.metric("Est. Time", f"{summary.get('total_estimated_minutes', 0)} min")
            else:
                st.error("Failed to run prioritization")
    
    # Display results
    if "priority_analysis" in st.session_state:
        priority_result = st.session_state["priority_analysis"]
        
        st.markdown("---")
        st.markdown("### 📊 Prioritized Tasks")
        
        prioritized_tasks = priority_result.get("prioritized_tasks", [])
        if prioritized_tasks:
            for idx, task in enumerate(prioritized_tasks, 1):
                priority_icons = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                priority_icon = priority_icons.get(task.get("priority", "low"), "")
                
                with st.expander(
                    f"#{idx} {priority_icon} {task['task_id']} - Score: {task.get('priority_score', 0):.1f}",
                    expanded=idx <= 3
                ):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Type:** {task['task_type'].replace('_', ' ').title()}")
                        st.markdown(f"**Location:** {task.get('location', 'N/A')}")
                        st.markdown(f"**Priority:** {task.get('priority', 'N/A').upper()}")
                        st.markdown(f"**Duration:** {task.get('estimated_duration_minutes', 0)} min")
                    
                    with col2:
                        st.markdown(f"**Priority Score:** {task.get('priority_score', 0):.2f}")
                        
                        # Show scoring factors
                        factors = task.get("priority_factors", {})
                        if factors:
                            st.markdown("**Factors:**")
                            for factor, value in factors.items():
                                st.markdown(f"- {factor.replace('_', ' ').title()}: {value:.2f}")
                    
                    # Assignment recommendation
                    if task.get("recommended_assignment"):
                        assignment = task["recommended_assignment"]
                        st.markdown(f"""
                            <div style="background-color: #e3f2fd; padding: 1rem; border-radius: 0.5rem; margin-top: 1rem;">
                                <strong>👤 Recommended Assignment:</strong> {assignment.get('staff_id')}<br>
                                <strong>Reason:</strong> {assignment.get('reason')}<br>
                                <strong>Match Score:</strong> {assignment.get('match_score', 0) * 100:.0f}%
                            </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button(f"✅ Assign to {assignment.get('staff_id')}", key=f"assign_ai_{task['task_id']}"):
                            assign_result = evs_mcp.call_endpoint(
                                "assign_task",
                                {
                                    "task_id": task["task_id"],
                                    "staff_id": assignment.get('staff_id'),
                                    "assigned_by": "AI_AGENT"
                                }
                            )
                            
                            if assign_result.get("success"):
                                st.success(f"✅ Task assigned to {assignment.get('staff_id')}")
                                st.rerun()
        else:
            st.info("No tasks to prioritize")
        
        # Recommended schedule
        if priority_result.get("recommended_schedule"):
            st.markdown("---")
            st.markdown("### 📅 Recommended Task Schedule")
            
            schedule = priority_result["recommended_schedule"]
            schedule_df = pd.DataFrame(schedule)
            
            st.dataframe(
                schedule_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "task_id": "Task ID",
                    "staff_id": "Staff",
                    "start_time": "Start Time",
                    "end_time": "End Time",
                    "priority": "Priority"
                }
            )
            
            # Export schedule
            if st.button("📥 Export Schedule"):
                csv = schedule_df.to_csv(index=False)
                st.download_button(
                    "Download CSV",
                    csv,
                    f"evs_schedule_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    "text/csv"
                )

# Help section
with st.expander("❓ Help & Instructions"):
    st.markdown("""
    ### EVS Task Management Guide
    
    **Tasks Tab:**
    - View all tasks with filtering options
    - Update task status and assignments
    - Monitor high-priority items
    - Quick task overview
    
    **Create Task Tab:**
    - Create new cleaning tasks
    - Set priority and requirements
    - Add special instructions
    - Specify patient proximity
    
    **Staff Tab:**
    - View staff availability by shift
    - Monitor current assignments
    - Track task completion
    - Check staff skills and locations
    
    **AI Prioritization Tab:**
    - Run intelligent task analysis
    - Get optimized priority scores
    - Receive assignment recommendations
    - Generate optimal schedules
    
    **AI Features:**
    - Multi-factor priority scoring
    - Smart staff assignment matching
    - Route optimization
    - Workload balancing
    - Environmental compliance monitoring
    """)
