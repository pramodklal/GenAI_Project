"""
Clinical Trials Management Page
Manage clinical trials from Phase 1 to Phase 4
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

st.set_page_config(page_title="Clinical Trials", page_icon="🏥", layout="wide")

st.title("🏥 Clinical Trials Management")
st.markdown("Manage clinical trials across all phases")

tab1, tab2, tab3 = st.tabs(["📋 Active Trials", "➕ Register Trial", "📊 Trial Analytics"])

with tab1:
    st.markdown("### Clinical Trials Overview")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        phase_filter = st.selectbox("Phase", ["All", "phase1", "phase2", "phase3", "phase4"])
    with col2:
        status_filter = st.selectbox("Status", ["All", "recruiting", "active", "completed", "suspended", "terminated"])
    with col3:
        search_term = st.text_input("Search by drug name or trial ID")
    
    try:
        trials = db.get_clinical_trials(limit=1000)
        
        # Apply filters
        if phase_filter != "All":
            trials = [t for t in trials if t.get("phase") == phase_filter]
        
        if status_filter != "All":
            trials = [t for t in trials if t.get("status") == status_filter]
        
        if search_term:
            trials = [t for t in trials if 
                     search_term.lower() in t.get("drug_name", "").lower() or 
                     search_term.lower() in t.get("trial_id", "").lower()]
        
        # Sort by start date
        trials = sorted(trials, key=lambda x: x.get("start_date", ""), reverse=True)
        
        if trials:
            st.write(f"**Total Trials:** {len(trials)}")
            
            for trial in trials:
                status_color = {
                    "recruiting": "🟢",
                    "active": "🔵",
                    "completed": "✅",
                    "suspended": "🟡",
                    "terminated": "🔴"
                }.get(trial.get("status"), "⚪")
                
                with st.expander(f"{status_color} {trial.get('trial_id', 'N/A')} - {trial.get('drug_name', 'N/A')} ({trial.get('phase', 'N/A').upper()})"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Trial ID:** {trial.get('trial_id', 'N/A')}")
                        st.write(f"**Drug Name:** {trial.get('drug_name', 'N/A')}")
                        st.write(f"**Phase:** {trial.get('phase', 'N/A').upper()}")
                        st.write(f"**Indication:** {trial.get('indication', 'N/A')}")
                    
                    with col2:
                        st.write(f"**Status:** {trial.get('status', 'N/A')}")
                        st.write(f"**Principal Investigator:** {trial.get('principal_investigator', 'N/A')}")
                        st.write(f"**Sponsor:** {trial.get('sponsor', 'N/A')}")
                        st.write(f"**CRO:** {trial.get('cro', 'N/A')}")
                    
                    with col3:
                        enrolled = trial.get('enrolled_participants', 0)
                        target = trial.get('target_participants', 0)
                        enrollment_pct = (enrolled / target * 100) if target > 0 else 0
                        
                        st.write(f"**Enrollment:** {enrolled}/{target} ({enrollment_pct:.0f}%)")
                        st.write(f"**Sites:** {trial.get('number_of_sites', 0)}")
                        st.write(f"**Start Date:** {trial.get('start_date', 'N/A')}")
                        st.write(f"**Expected End:** {trial.get('expected_completion_date', 'N/A')}")
                    
                    if trial.get("primary_endpoint"):
                        st.write(f"**Primary Endpoint:** {trial.get('primary_endpoint')}")
                    
                    if trial.get("secondary_endpoints"):
                        st.write(f"**Secondary Endpoints:** {trial.get('secondary_endpoints')}")
                    
                    if trial.get("inclusion_criteria"):
                        st.write(f"**Inclusion Criteria:** {trial.get('inclusion_criteria')}")
        else:
            st.info("No clinical trials found. Register your first trial below!")
    
    except Exception as e:
        st.error(f"Error loading trials: {str(e)}")

with tab2:
    st.markdown("### Register New Clinical Trial")
    
    with st.form("register_trial_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            trial_id = st.text_input("Trial ID *", placeholder="e.g., NCT12345678")
            drug_name = st.text_input("Drug Name *", placeholder="e.g., XYZ-123")
            indication = st.text_input("Indication *", placeholder="e.g., Type 2 Diabetes")
            phase = st.selectbox("Phase *", ["phase1", "phase2", "phase3", "phase4"])
            status = st.selectbox("Status *", ["recruiting", "active", "completed", "suspended", "terminated"])
            
        with col2:
            principal_investigator = st.text_input("Principal Investigator *", placeholder="Dr. John Doe")
            sponsor = st.text_input("Sponsor", placeholder="Pharmaceutical Company")
            cro = st.text_input("CRO (Contract Research Org)", placeholder="CRO Name")
            target_participants = st.number_input("Target Participants *", min_value=1, value=100)
            number_of_sites = st.number_input("Number of Sites", min_value=1, value=10)
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date *")
        with col2:
            expected_completion_date = st.date_input("Expected Completion Date")
        
        primary_endpoint = st.text_input("Primary Endpoint", placeholder="e.g., Change in HbA1c at 12 weeks")
        secondary_endpoints = st.text_area("Secondary Endpoints", placeholder="List secondary endpoints...")
        inclusion_criteria = st.text_area("Inclusion Criteria", placeholder="Patient inclusion criteria...")
        exclusion_criteria = st.text_area("Exclusion Criteria", placeholder="Patient exclusion criteria...")
        
        submitted = st.form_submit_button("🏥 Register Clinical Trial", use_container_width=True)
        
        if submitted:
            if not trial_id or not drug_name or not indication or not principal_investigator:
                st.error("Please fill in all required fields marked with *")
            else:
                try:
                    trial_data = {
                        "trial_id": trial_id,
                        "drug_name": drug_name,
                        "indication": indication,
                        "phase": phase,
                        "status": status,
                        "principal_investigator": principal_investigator,
                        "sponsor": sponsor,
                        "cro": cro,
                        "target_participants": target_participants,
                        "enrolled_participants": 0,
                        "number_of_sites": number_of_sites,
                        "start_date": start_date.isoformat(),
                        "expected_completion_date": expected_completion_date.isoformat(),
                        "primary_endpoint": primary_endpoint,
                        "secondary_endpoints": secondary_endpoints,
                        "inclusion_criteria": inclusion_criteria,
                        "exclusion_criteria": exclusion_criteria,
                        "adverse_events_reported": 0,
                        "serious_adverse_events": 0,
                        "dropout_rate": 0.0,
                        "protocol_version": "1.0",
                        "regulatory_approvals": []
                    }
                    
                    trial_db_id = db.create_clinical_trial(trial_data)
                    
                    if trial_db_id:
                        st.success(f"✅ Clinical trial registered successfully! Trial ID: {trial_id}")
                        st.balloons()
                    else:
                        st.error("Failed to register clinical trial")
                
                except Exception as e:
                    st.error(f"Error registering trial: {str(e)}")

with tab3:
    st.markdown("### Clinical Trial Analytics")
    
    try:
        trials = db.get_clinical_trials(limit=1000)
        
        if trials:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_trials = len(trials)
                st.metric("Total Trials", total_trials)
            
            with col2:
                active_trials = len([t for t in trials if t.get("status") in ["recruiting", "active"]])
                st.metric("Active Trials", active_trials)
            
            with col3:
                total_participants = sum(t.get("enrolled_participants", 0) for t in trials)
                st.metric("Total Participants", total_participants)
            
            with col4:
                completed_trials = len([t for t in trials if t.get("status") == "completed"])
                st.metric("Completed Trials", completed_trials)
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Trials by Phase")
                phase_counts = {}
                for t in trials:
                    phase = t.get("phase", "unknown")
                    phase_counts[phase] = phase_counts.get(phase, 0) + 1
                
                for phase, count in sorted(phase_counts.items()):
                    st.write(f"**{phase.upper()}:** {count}")
            
            with col2:
                st.markdown("#### Trials by Status")
                status_counts = {}
                for t in trials:
                    status = t.get("status", "unknown")
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                for status, count in sorted(status_counts.items()):
                    st.write(f"**{status.capitalize()}:** {count}")
            
            st.markdown("---")
            
            # Enrollment progress
            st.markdown("#### Enrollment Progress")
            enrollment_data = []
            for t in trials:
                if t.get("status") in ["recruiting", "active"]:
                    enrolled = t.get("enrolled_participants", 0)
                    target = t.get("target_participants", 1)
                    pct = (enrolled / target * 100) if target > 0 else 0
                    enrollment_data.append({
                        "Trial ID": t.get("trial_id"),
                        "Drug": t.get("drug_name"),
                        "Enrolled": enrolled,
                        "Target": target,
                        "Progress": f"{pct:.1f}%"
                    })
            
            if enrollment_data:
                st.dataframe(enrollment_data, use_container_width=True)
            else:
                st.info("No active trials with enrollment data")
        
        else:
            st.info("No trial data available for analytics")
    
    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")
