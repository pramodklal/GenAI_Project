"""
Research Projects Management Page
Track and manage pharmaceutical research projects
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import uuid

parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))
from src.database.astra_helper import AstraDBHelper

db = AstraDBHelper()

st.set_page_config(page_title="Research Projects", page_icon="🔬", layout="wide")

st.title("🔬 Research Projects Management")
st.markdown("Track and manage pharmaceutical research projects")

tab1, tab2, tab3 = st.tabs(["📋 All Projects", "➕ Create Project", "📊 Project Analytics"])

with tab1:
    st.markdown("### Active Research Projects")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Status", ["All", "active", "planning", "on_hold", "completed", "cancelled"])
    with col2:
        search_term = st.text_input("Search by name")
    with col3:
        sort_by = st.selectbox("Sort by", ["Created Date", "Budget", "Progress"])
    
    try:
        projects = db.get_research_projects(limit=1000)
        
        # Apply filters
        if status_filter != "All":
            projects = [p for p in projects if p.get("status") == status_filter]
        
        if search_term:
            projects = [p for p in projects if search_term.lower() in p.get("project_name", "").lower()]
        
        # Sort
        if sort_by == "Created Date":
            projects = sorted(projects, key=lambda x: x.get("created_at", ""), reverse=True)
        elif sort_by == "Budget":
            projects = sorted(projects, key=lambda x: x.get("budget", 0), reverse=True)
        elif sort_by == "Progress":
            projects = sorted(projects, key=lambda x: x.get("completion_percentage", 0), reverse=True)
        
        if projects:
            st.write(f"**Total Projects:** {len(projects)}")
            
            for project in projects:
                with st.expander(f"🔬 {project.get('project_name', 'N/A')} - {project.get('status', 'N/A').upper()}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Project ID:** {project.get('project_id', 'N/A')}")
                        st.write(f"**Lead Scientist:** {project.get('lead_scientist', 'N/A')}")
                        st.write(f"**Department:** {project.get('department', 'N/A')}")
                        st.write(f"**Priority:** {project.get('priority', 'N/A')}")
                    
                    with col2:
                        st.write(f"**Status:** {project.get('status', 'N/A')}")
                        st.write(f"**Progress:** {project.get('completion_percentage', 0)}%")
                        st.write(f"**Start Date:** {project.get('start_date', 'N/A')}")
                        st.write(f"**Expected End:** {project.get('expected_end_date', 'N/A')}")
                    
                    with col3:
                        st.write(f"**Budget:** ${project.get('budget', 0):,.2f}")
                        st.write(f"**Spent:** ${project.get('budget_spent', 0):,.2f}")
                        st.write(f"**Remaining:** ${project.get('budget', 0) - project.get('budget_spent', 0):,.2f}")
                        st.write(f"**Team Size:** {project.get('team_size', 0)} members")
                    
                    if project.get("description"):
                        st.write(f"**Description:** {project.get('description')}")
                    
                    if project.get("objectives"):
                        st.write(f"**Objectives:** {project.get('objectives')}")
                    
                    if project.get("therapeutic_area"):
                        st.write(f"**Therapeutic Area:** {project.get('therapeutic_area')}")
        else:
            st.info("No research projects found. Create your first project below!")
    
    except Exception as e:
        st.error(f"Error loading projects: {str(e)}")

with tab2:
    st.markdown("### Create New Research Project")
    
    with st.form("create_project_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            project_name = st.text_input("Project Name *", placeholder="e.g., Novel Antibiotic Development")
            lead_scientist = st.text_input("Lead Scientist *", placeholder="Dr. Jane Smith")
            department = st.selectbox("Department *", [
                "Drug Discovery",
                "Molecular Biology",
                "Pharmacology",
                "Clinical Research",
                "Formulation Development",
                "Bioinformatics"
            ])
            therapeutic_area = st.selectbox("Therapeutic Area *", [
                "Oncology",
                "Cardiovascular",
                "Neurology",
                "Infectious Diseases",
                "Immunology",
                "Endocrinology",
                "Respiratory",
                "Other"
            ])
            priority = st.selectbox("Priority", ["High", "Medium", "Low"])
        
        with col2:
            budget = st.number_input("Budget ($) *", min_value=0, value=500000, step=10000)
            team_size = st.number_input("Team Size", min_value=1, value=5, step=1)
            start_date = st.date_input("Start Date *")
            expected_end_date = st.date_input("Expected End Date")
            status = st.selectbox("Initial Status", ["planning", "active", "on_hold"])
        
        description = st.text_area("Project Description", placeholder="Brief description of the research project...")
        objectives = st.text_area("Research Objectives", placeholder="Key objectives and milestones...")
        
        submitted = st.form_submit_button("🚀 Create Research Project", use_container_width=True)
        
        if submitted:
            if not project_name or not lead_scientist or not department:
                st.error("Please fill in all required fields marked with *")
            else:
                try:
                    project_data = {
                        "project_id": f"PROJ-{str(uuid.uuid4())[:8].upper()}",
                        "project_name": project_name,
                        "lead_scientist": lead_scientist,
                        "department": department,
                        "therapeutic_area": therapeutic_area,
                        "priority": priority.lower(),
                        "budget": budget,
                        "budget_spent": 0,
                        "team_size": team_size,
                        "start_date": start_date.isoformat(),
                        "expected_end_date": expected_end_date.isoformat(),
                        "status": status,
                        "completion_percentage": 0,
                        "description": description,
                        "objectives": objectives,
                        "created_by": "System",
                        "milestones": [],
                        "deliverables": []
                    }
                    
                    project_id = db.create_research_project(project_data)
                    
                    if project_id:
                        st.success(f"✅ Research project created successfully! Project ID: {project_data['project_id']}")
                        st.balloons()
                    else:
                        st.error("Failed to create research project")
                
                except Exception as e:
                    st.error(f"Error creating project: {str(e)}")

with tab3:
    st.markdown("### Research Project Analytics")
    
    try:
        projects = db.get_research_projects(limit=1000)
        
        if projects:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_projects = len(projects)
                st.metric("Total Projects", total_projects)
            
            with col2:
                active_projects = len([p for p in projects if p.get("status") == "active"])
                st.metric("Active Projects", active_projects)
            
            with col3:
                total_budget = sum(p.get("budget", 0) for p in projects)
                st.metric("Total Budget", f"${total_budget:,.0f}")
            
            with col4:
                total_spent = sum(p.get("budget_spent", 0) for p in projects)
                st.metric("Total Spent", f"${total_spent:,.0f}")
            
            st.markdown("---")
            
            # Status distribution
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Projects by Status")
                status_counts = {}
                for p in projects:
                    status = p.get("status", "unknown")
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                for status, count in sorted(status_counts.items()):
                    st.write(f"**{status.capitalize()}:** {count}")
            
            with col2:
                st.markdown("#### Projects by Therapeutic Area")
                area_counts = {}
                for p in projects:
                    area = p.get("therapeutic_area", "unknown")
                    area_counts[area] = area_counts.get(area, 0) + 1
                
                for area, count in sorted(area_counts.items()):
                    st.write(f"**{area}:** {count}")
            
            st.markdown("---")
            
            # Budget analysis
            st.markdown("#### Budget Analysis")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Top 5 Projects by Budget:**")
                top_budget = sorted(projects, key=lambda x: x.get("budget", 0), reverse=True)[:5]
                for p in top_budget:
                    st.write(f"• {p.get('project_name')}: ${p.get('budget', 0):,.0f}")
            
            with col2:
                st.markdown("**Projects by Priority:**")
                priority_counts = {}
                for p in projects:
                    priority = p.get("priority", "unknown")
                    priority_counts[priority] = priority_counts.get(priority, 0) + 1
                
                for priority, count in sorted(priority_counts.items()):
                    st.write(f"**{priority.capitalize()}:** {count}")
        
        else:
            st.info("No project data available for analytics")
    
    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")
