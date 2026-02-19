"""
Laboratory Experiments Page
Record and track laboratory experiments
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

st.set_page_config(page_title="Lab Experiments", page_icon="🧪", layout="wide")

st.title("🧪 Laboratory Experiments")
st.markdown("Record and track laboratory experiments and results")

tab1, tab2, tab3 = st.tabs(["📋 Experiment Log", "➕ Record Experiment", "📊 Experiment Analytics"])

with tab1:
    st.markdown("### Laboratory Experiment Log")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        experiment_type_filter = st.selectbox("Experiment Type", [
            "All", "in_vitro", "in_vivo", "biochemical", "pharmacokinetics",
            "toxicology", "formulation", "analytical"
        ])
    with col2:
        status_filter = st.selectbox("Status", ["All", "planned", "in_progress", "completed", "failed"])
    with col3:
        date_range = st.date_input("Date Range", value=(datetime.now().date(), datetime.now().date()))
    
    try:
        experiments = db.get_lab_experiments(limit=1000)
        
        # Apply filters
        if experiment_type_filter != "All":
            experiments = [e for e in experiments if e.get("experiment_type") == experiment_type_filter]
        
        if status_filter != "All":
            experiments = [e for e in experiments if e.get("status") == status_filter]
        
        # Sort by date
        experiments = sorted(experiments, key=lambda x: x.get("experiment_date", ""), reverse=True)
        
        if experiments:
            st.write(f"**Total Experiments:** {len(experiments)}")
            
            for exp in experiments:
                status_icon = {
                    "planned": "📅",
                    "in_progress": "⏳",
                    "completed": "✅",
                    "failed": "❌"
                }.get(exp.get("status") or "", "🧪")
                
                with st.expander(f"{status_icon} {exp.get('experiment_id', 'N/A')} - {exp.get('experiment_type', 'N/A').replace('_', ' ').title()} ({exp.get('experiment_date', 'N/A')})"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Experiment ID:** {exp.get('experiment_id', 'N/A')}")
                        st.write(f"**Type:** {exp.get('experiment_type', 'N/A').replace('_', ' ').title()}")
                        st.write(f"**Scientist:** {exp.get('scientist_name', 'N/A')}")
                        st.write(f"**Lab Location:** {exp.get('lab_location', 'N/A')}")
                    
                    with col2:
                        st.write(f"**Status:** {exp.get('status', 'N/A')}")
                        st.write(f"**Date:** {exp.get('experiment_date', 'N/A')}")
                        st.write(f"**Duration:** {exp.get('duration_hours', 0)} hours")
                        st.write(f"**Success:** {exp.get('success', 'N/A')}")
                    
                    with col3:
                        st.write(f"**Compound Tested:** {exp.get('compound_tested', 'N/A')}")
                        st.write(f"**Concentration:** {exp.get('concentration', 'N/A')}")
                        st.write(f"**Temperature:** {exp.get('temperature_celsius', 'N/A')}°C")
                        st.write(f"**pH:** {exp.get('ph_level', 'N/A')}")
                    
                    if exp.get("objective"):
                        st.write(f"**Objective:** {exp.get('objective')}")
                    
                    if exp.get("methodology"):
                        st.write(f"**Methodology:** {exp.get('methodology')}")
                    
                    if exp.get("results"):
                        st.write(f"**Results:** {exp.get('results')}")
                    
                    if exp.get("observations"):
                        st.write(f"**Observations:** {exp.get('observations')}")
                    
                    if exp.get("conclusion"):
                        st.write(f"**Conclusion:** {exp.get('conclusion')}")
        else:
            st.info("No experiments found. Record your first experiment below!")
    
    except Exception as e:
        st.error(f"Error loading experiments: {str(e)}")

with tab2:
    st.markdown("### Record New Experiment")
    
    with st.form("record_experiment_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            experiment_id = st.text_input("Experiment ID", placeholder="Auto-generated if empty")
            experiment_type = st.selectbox("Experiment Type *", [
                "in_vitro",
                "in_vivo",
                "biochemical",
                "pharmacokinetics",
                "toxicology",
                "formulation",
                "analytical",
                "stability"
            ])
            scientist_name = st.text_input("Scientist Name *", placeholder="Dr. Jane Smith")
            lab_location = st.text_input("Lab Location", placeholder="e.g., Building A, Lab 101")
            compound_tested = st.text_input("Compound Tested", placeholder="e.g., XYZ-123")
        
        with col2:
            status = st.selectbox("Status *", ["planned", "in_progress", "completed", "failed"])
            experiment_date = st.date_input("Experiment Date *")
            duration_hours = st.number_input("Duration (hours)", min_value=0.0, value=2.0, step=0.5)
            concentration = st.text_input("Concentration", placeholder="e.g., 10 µM")
            temperature_celsius = st.number_input("Temperature (°C)", value=25.0)
            ph_level = st.number_input("pH Level", min_value=0.0, max_value=14.0, value=7.0, step=0.1)
        
        objective = st.text_area("Objective *", placeholder="What is the goal of this experiment?")
        methodology = st.text_area("Methodology", placeholder="Describe the experimental procedure...")
        
        col1, col2 = st.columns(2)
        with col1:
            results = st.text_area("Results", placeholder="Quantitative and qualitative results...")
            observations = st.text_area("Observations", placeholder="Additional observations during experiment...")
        
        with col2:
            conclusion = st.text_area("Conclusion", placeholder="Interpretation of results...")
            success = st.radio("Success", ["Yes", "No", "Partial"])
        
        equipment_used = st.text_input("Equipment Used", placeholder="e.g., HPLC, Mass Spectrometer")
        reagents = st.text_area("Reagents", placeholder="List all reagents used...")
        
        submitted = st.form_submit_button("🧪 Record Experiment", use_container_width=True)
        
        if submitted:
            if not scientist_name or not objective:
                st.error("Please fill in all required fields marked with *")
            else:
                try:
                    if not experiment_id:
                        experiment_id = f"EXP-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"
                    
                    experiment_data = {
                        "experiment_id": experiment_id,
                        "experiment_type": experiment_type,
                        "scientist_name": scientist_name,
                        "lab_location": lab_location,
                        "compound_tested": compound_tested,
                        "status": status,
                        "experiment_date": experiment_date.isoformat(),
                        "duration_hours": duration_hours,
                        "concentration": concentration,
                        "temperature_celsius": temperature_celsius,
                        "ph_level": ph_level,
                        "objective": objective,
                        "methodology": methodology,
                        "results": results,
                        "observations": observations,
                        "conclusion": conclusion,
                        "success": success.lower(),
                        "equipment_used": equipment_used,
                        "reagents": reagents,
                        "data_files": [],
                        "peer_reviewed": False
                    }
                    
                    exp_id = db.create_lab_experiment(experiment_data)
                    
                    if exp_id:
                        st.success(f"✅ Experiment recorded successfully! ID: {experiment_id}")
                        st.balloons()
                    else:
                        st.error("Failed to record experiment")
                
                except Exception as e:
                    st.error(f"Error recording experiment: {str(e)}")

with tab3:
    st.markdown("### Experiment Analytics")
    
    try:
        experiments = db.get_lab_experiments(limit=1000)
        
        if experiments:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_experiments = len(experiments)
                st.metric("Total Experiments", total_experiments)
            
            with col2:
                completed_experiments = len([e for e in experiments if e.get("status") == "completed"])
                st.metric("Completed", completed_experiments)
            
            with col3:
                successful_experiments = len([e for e in experiments if e.get("success") == "yes"])
                success_rate = (successful_experiments / total_experiments * 100) if total_experiments > 0 else 0
                st.metric("Success Rate", f"{success_rate:.1f}%")
            
            with col4:
                in_progress = len([e for e in experiments if e.get("status") == "in_progress"])
                st.metric("In Progress", in_progress)
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Experiments by Type")
                type_counts = {}
                for e in experiments:
                    exp_type = e.get("experiment_type", "unknown")
                    type_counts[exp_type] = type_counts.get(exp_type, 0) + 1
                
                for exp_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
                    st.write(f"**{exp_type.replace('_', ' ').title()}:** {count}")
            
            with col2:
                st.markdown("#### Experiments by Status")
                status_counts = {}
                for e in experiments:
                    status = e.get("status", "unknown")
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                for status, count in sorted(status_counts.items()):
                    st.write(f"**{status.capitalize()}:** {count}")
            
            st.markdown("---")
            
            # Top scientists
            st.markdown("#### Top Scientists by Experiments")
            scientist_counts = {}
            for e in experiments:
                scientist = e.get("scientist_name", "Unknown")
                scientist_counts[scientist] = scientist_counts.get(scientist, 0) + 1
            
            top_scientists = sorted(scientist_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            for scientist, count in top_scientists:
                st.write(f"• {scientist}: {count} experiments")
            
            st.markdown("---")
            
            # Monthly trend
            st.markdown("#### Experiment Trend (Last 12 Months)")
            current_year = datetime.now().year
            current_month = datetime.now().month
            
            monthly_counts = {}
            for e in experiments:
                exp_date = e.get("experiment_date", "")
                if exp_date:
                    month = exp_date[:7]  # YYYY-MM
                    monthly_counts[month] = monthly_counts.get(month, 0) + 1
            
            if monthly_counts:
                for month, count in sorted(monthly_counts.items(), reverse=True)[:12]:
                    st.write(f"**{month}:** {count} experiments")
            else:
                st.info("No monthly data available")
        
        else:
            st.info("No experiment data available for analytics")
    
    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")
