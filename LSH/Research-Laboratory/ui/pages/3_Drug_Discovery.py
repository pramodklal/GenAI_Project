"""
Drug Discovery Pipeline Page
Track drug candidates through discovery and development stages
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

st.set_page_config(page_title="Drug Discovery", page_icon="💊", layout="wide")

st.title("💊 Drug Discovery Pipeline")
st.markdown("Track drug candidates from discovery to clinical development")

tab1, tab2, tab3 = st.tabs(["📋 Pipeline Overview", "➕ Add Candidate", "📊 Pipeline Analytics"])

with tab1:
    st.markdown("### Drug Development Pipeline")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        stage_filter = st.selectbox("Development Stage", [
            "All", "discovery", "lead_optimization", "preclinical", 
            "phase1", "phase2", "phase3", "regulatory_review", "approved"
        ])
    with col2:
        therapeutic_area_filter = st.selectbox("Therapeutic Area", [
            "All", "Oncology", "Cardiovascular", "Neurology", 
            "Infectious Diseases", "Immunology", "Other"
        ])
    with col3:
        search_term = st.text_input("Search by compound name")
    
    try:
        candidates = db.get_drug_candidates(limit=1000)
        
        # Apply filters
        if stage_filter != "All":
            candidates = [c for c in candidates if c.get("stage") == stage_filter]
        
        if therapeutic_area_filter != "All":
            candidates = [c for c in candidates if c.get("therapeutic_area") == therapeutic_area_filter]
        
        if search_term:
            candidates = [c for c in candidates if search_term.lower() in c.get("compound_name", "").lower()]
        
        # Sort by stage priority
        stage_order = ["discovery", "lead_optimization", "preclinical", "phase1", "phase2", "phase3", "regulatory_review", "approved"]
        candidates = sorted(candidates, key=lambda x: stage_order.index(x.get("stage", "discovery")) if x.get("stage") in stage_order else 999)
        
        if candidates:
            st.write(f"**Total Candidates:** {len(candidates)}")
            
            for candidate in candidates:
                stage_emoji = {
                    "discovery": "🔍",
                    "lead_optimization": "⚗️",
                    "preclinical": "🧪",
                    "phase1": "1️⃣",
                    "phase2": "2️⃣",
                    "phase3": "3️⃣",
                    "regulatory_review": "📋",
                    "approved": "✅"
                }.get(candidate.get("stage"), "💊")
                
                with st.expander(f"{stage_emoji} {candidate.get('compound_name', 'N/A')} - {candidate.get('stage', 'N/A').replace('_', ' ').title()}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Compound ID:** {candidate.get('compound_id', 'N/A')}")
                        st.write(f"**Compound Name:** {candidate.get('compound_name', 'N/A')}")
                        st.write(f"**Target:** {candidate.get('target', 'N/A')}")
                        st.write(f"**Mechanism:** {candidate.get('mechanism_of_action', 'N/A')}")
                    
                    with col2:
                        st.write(f"**Stage:** {candidate.get('stage', 'N/A').replace('_', ' ').title()}")
                        st.write(f"**Therapeutic Area:** {candidate.get('therapeutic_area', 'N/A')}")
                        st.write(f"**Indication:** {candidate.get('indication', 'N/A')}")
                        st.write(f"**Lead Researcher:** {candidate.get('lead_researcher', 'N/A')}")
                    
                    with col3:
                        st.write(f"**Discovery Date:** {candidate.get('discovery_date', 'N/A')}")
                        st.write(f"**Success Probability:** {candidate.get('success_probability', 0)}%")
                        st.write(f"**Est. Market Size:** ${candidate.get('estimated_market_size', 0):,.0f}M")
                        st.write(f"**Patent Status:** {candidate.get('patent_status', 'N/A')}")
                    
                    if candidate.get("chemical_formula"):
                        st.write(f"**Chemical Formula:** {candidate.get('chemical_formula')}")
                    
                    if candidate.get("efficacy_data"):
                        st.write(f"**Efficacy Data:** {candidate.get('efficacy_data')}")
                    
                    if candidate.get("safety_profile"):
                        st.write(f"**Safety Profile:** {candidate.get('safety_profile')}")
        else:
            st.info("No drug candidates found. Add your first candidate below!")
    
    except Exception as e:
        st.error(f"Error loading candidates: {str(e)}")

with tab2:
    st.markdown("### Add New Drug Candidate")
    
    with st.form("add_candidate_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            compound_name = st.text_input("Compound Name *", placeholder="e.g., XYZ-123")
            compound_id = st.text_input("Compound ID", placeholder="e.g., COMP-2025-001")
            target = st.text_input("Target *", placeholder="e.g., EGFR, PD-1, IL-6")
            mechanism_of_action = st.text_area("Mechanism of Action", placeholder="Describe how the compound works...")
            chemical_formula = st.text_input("Chemical Formula", placeholder="e.g., C21H27N7O")
        
        with col2:
            stage = st.selectbox("Development Stage *", [
                "discovery",
                "lead_optimization",
                "preclinical",
                "phase1",
                "phase2",
                "phase3",
                "regulatory_review",
                "approved"
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
            indication = st.text_input("Indication *", placeholder="e.g., Non-Small Cell Lung Cancer")
            lead_researcher = st.text_input("Lead Researcher", placeholder="Dr. Jane Smith")
            discovery_date = st.date_input("Discovery Date")
        
        col1, col2 = st.columns(2)
        with col1:
            success_probability = st.slider("Success Probability (%)", 0, 100, 50)
            estimated_market_size = st.number_input("Estimated Market Size ($M)", min_value=0, value=500)
        
        with col2:
            patent_status = st.selectbox("Patent Status", ["filed", "granted", "pending", "none"])
            ip_strategy = st.text_input("IP Strategy", placeholder="Patent protection strategy...")
        
        efficacy_data = st.text_area("Efficacy Data", placeholder="Summary of efficacy results...")
        safety_profile = st.text_area("Safety Profile", placeholder="Safety and tolerability data...")
        competitive_landscape = st.text_area("Competitive Landscape", placeholder="Competing drugs or candidates...")
        
        submitted = st.form_submit_button("💊 Add Drug Candidate", use_container_width=True)
        
        if submitted:
            if not compound_name or not target or not indication:
                st.error("Please fill in all required fields marked with *")
            else:
                try:
                    if not compound_id:
                        compound_id = f"COMP-{str(uuid.uuid4())[:8].upper()}"
                    
                    candidate_data = {
                        "compound_id": compound_id,
                        "compound_name": compound_name,
                        "target": target,
                        "mechanism_of_action": mechanism_of_action,
                        "chemical_formula": chemical_formula,
                        "stage": stage,
                        "therapeutic_area": therapeutic_area,
                        "indication": indication,
                        "lead_researcher": lead_researcher,
                        "discovery_date": discovery_date.isoformat(),
                        "success_probability": success_probability,
                        "estimated_market_size": estimated_market_size,
                        "patent_status": patent_status,
                        "ip_strategy": ip_strategy,
                        "efficacy_data": efficacy_data,
                        "safety_profile": safety_profile,
                        "competitive_landscape": competitive_landscape,
                        "preclinical_studies": [],
                        "clinical_trials": [],
                        "regulatory_milestones": []
                    }
                    
                    candidate_id = db.create_drug_candidate(candidate_data)
                    
                    if candidate_id:
                        st.success(f"✅ Drug candidate added successfully! Compound ID: {compound_id}")
                        st.balloons()
                    else:
                        st.error("Failed to add drug candidate")
                
                except Exception as e:
                    st.error(f"Error adding candidate: {str(e)}")

with tab3:
    st.markdown("### Drug Pipeline Analytics")
    
    try:
        candidates = db.get_drug_candidates(limit=1000)
        
        if candidates:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_candidates = len(candidates)
                st.metric("Total Candidates", total_candidates)
            
            with col2:
                clinical_candidates = len([c for c in candidates if c.get("stage") in ["phase1", "phase2", "phase3"]])
                st.metric("In Clinical Trials", clinical_candidates)
            
            with col3:
                approved_drugs = len([c for c in candidates if c.get("stage") == "approved"])
                st.metric("Approved Drugs", approved_drugs)
            
            with col4:
                avg_success_prob = sum(c.get("success_probability", 0) for c in candidates) / len(candidates)
                st.metric("Avg Success Prob", f"{avg_success_prob:.1f}%")
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Pipeline by Stage")
                stage_counts = {}
                for c in candidates:
                    stage = c.get("stage", "unknown")
                    stage_counts[stage] = stage_counts.get(stage, 0) + 1
                
                stage_order = ["discovery", "lead_optimization", "preclinical", "phase1", "phase2", "phase3", "regulatory_review", "approved"]
                for stage in stage_order:
                    if stage in stage_counts:
                        st.write(f"**{stage.replace('_', ' ').title()}:** {stage_counts[stage]}")
            
            with col2:
                st.markdown("#### Candidates by Therapeutic Area")
                area_counts = {}
                for c in candidates:
                    area = c.get("therapeutic_area", "unknown")
                    area_counts[area] = area_counts.get(area, 0) + 1
                
                for area, count in sorted(area_counts.items(), key=lambda x: x[1], reverse=True):
                    st.write(f"**{area}:** {count}")
            
            st.markdown("---")
            
            # High priority candidates
            st.markdown("#### High Potential Candidates (Success Probability > 70%)")
            high_potential = [c for c in candidates if c.get("success_probability", 0) > 70]
            
            if high_potential:
                high_potential_data = [{
                    "Compound": c.get("compound_name"),
                    "Stage": c.get("stage", "").replace("_", " ").title(),
                    "Therapeutic Area": c.get("therapeutic_area"),
                    "Success Prob": f"{c.get('success_probability', 0)}%",
                    "Market Size ($M)": f"${c.get('estimated_market_size', 0):,.0f}"
                } for c in high_potential]
                
                st.dataframe(high_potential_data, use_container_width=True)
            else:
                st.info("No high potential candidates found")
            
            st.markdown("---")
            
            # Market potential
            st.markdown("#### Market Potential Analysis")
            total_market = sum(c.get("estimated_market_size", 0) for c in candidates)
            st.metric("Total Estimated Market Size", f"${total_market:,.0f}M")
            
            # Top 5 by market size
            top_market = sorted(candidates, key=lambda x: x.get("estimated_market_size", 0), reverse=True)[:5]
            st.markdown("**Top 5 Candidates by Market Size:**")
            for c in top_market:
                st.write(f"• {c.get('compound_name')}: ${c.get('estimated_market_size', 0):,.0f}M ({c.get('therapeutic_area')})")
        
        else:
            st.info("No candidate data available for analytics")
    
    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")
