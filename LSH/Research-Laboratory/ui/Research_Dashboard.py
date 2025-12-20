"""
Medicines Research Laboratory - Main Dashboard
Streamlit application for pharmaceutical R&D operations
Database: medicines_research (Astra DB)
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory (Research-Laboratory) to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from src.database.astra_helper import AstraDBHelper

# Initialize database
db = AstraDBHelper()

# Page configuration
st.set_page_config(
    page_title="Medicines Research Laboratory",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .status-active { color: #28a745; font-weight: bold; }
    .status-pending { color: #ffc107; font-weight: bold; }
    .status-completed { color: #17a2b8; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🔬 Medicines Research Laboratory</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Powered Drug Discovery & Clinical Research Platform | Astra DB Serverless</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🔬 Research Laboratory")
    st.markdown("**Database:** medicines_research")
    st.markdown("**Environment:** Astra DB Serverless")
    st.markdown("---")
    
    # Solution Summary
    st.markdown("#### 🎯 Solution Overview")
    st.info("""
    **AI-Powered Research Platform**
    
    🤖 **6 AI Agents** (GPT-4o)
    - Clinical Trial Analysis
    - Drug Discovery
    - Lab Experiments
    - Research Publications
    - Patent Analysis
    - Analytics & Reports
    
    💾 **10 Collections**
    - 7 Regular Collections
    - 3 Vector Search (1536D)
    
    🔌 **MCP Server**
    - 18 API Tools
    - Programmatic Access
    
    📊 **Features**
    - CSV Import/Export
    - Vector Similarity Search
    - Real-time Analytics
    - AI-Powered Insights
    """)
    
    st.markdown("---")
    
    # Data stats
    st.markdown("#### 📈 Data Status")
    try:
        stats = db.get_collection_stats()
        total_docs = sum(stats.values())
        if total_docs > 0:
            st.success(f"✅ **{total_docs:,}** Total Documents")
            st.caption(f"📁 Projects: {stats.get('research_projects', 0)}")
            st.caption(f"🏥 Trials: {stats.get('clinical_trials', 0)}")
            st.caption(f"💊 Candidates: {stats.get('drug_candidates', 0)}")
            st.caption(f"🧪 Experiments: {stats.get('lab_experiments', 0)}")
        else:
            st.warning("📤 No data yet. Use **CSV Import** to get started!")
    except Exception as e:
        st.error(f"Error: {str(e)}")
    
    st.markdown("---")
    st.caption("🚀 Professional AI Architecture | Dec 2025")

# Main content
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🧪 Recent Activity", "📈 Analytics", "⚙️ System Info"])

with tab1:
    st.markdown("### Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        # Get data
        research_projects = db.get_research_projects(limit=1000)
        clinical_trials = db.get_clinical_trials(limit=1000)
        drug_candidates = db.get_drug_candidates(limit=1000)
        lab_experiments = db.get_lab_experiments(limit=1000)
        
        # Active research projects
        active_projects = [p for p in research_projects if p.get("status") == "active"]
        with col1:
            st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                    <p class="metric-value">{len(active_projects)}</p>
                    <p class="metric-label">Active Research Projects</p>
                </div>
            """, unsafe_allow_html=True)
        
        # Ongoing clinical trials
        ongoing_trials = [t for t in clinical_trials if t.get("status") in ["recruiting", "active"]]
        with col2:
            st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                    <p class="metric-value">{len(ongoing_trials)}</p>
                    <p class="metric-label">Ongoing Clinical Trials</p>
                </div>
            """, unsafe_allow_html=True)
        
        # Drug candidates in pipeline
        pipeline_candidates = [c for c in drug_candidates if c.get("stage") in ["preclinical", "phase1", "phase2", "phase3"]]
        with col3:
            st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                    <p class="metric-value">{len(pipeline_candidates)}</p>
                    <p class="metric-label">Drug Candidates in Pipeline</p>
                </div>
            """, unsafe_allow_html=True)
        
        # Experiments this month
        current_month = datetime.utcnow().strftime("%Y-%m")
        monthly_experiments = [e for e in lab_experiments if e.get("created_at", "").startswith(current_month)]
        with col4:
            st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
                    <p class="metric-value">{len(monthly_experiments)}</p>
                    <p class="metric-label">Experiments This Month</p>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Research projects by status
        st.markdown("### 🔬 Research Projects Overview")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if research_projects:
                st.dataframe(
                    [{
                        "Project Name": p.get("project_name", "N/A"),
                        "Lead Scientist": p.get("lead_scientist", "N/A"),
                        "Status": p.get("status", "N/A"),
                        "Progress": f"{p.get('completion_percentage', 0)}%",
                        "Budget": f"${p.get('budget', 0):,.0f}",
                        "Start Date": p.get("start_date", "N/A")
                    } for p in research_projects[:10]],
                    use_container_width=True,
                    height=300
                )
            else:
                st.info("No research projects found. Create your first project in the Research Projects page.")
        
        with col2:
            st.markdown("#### Project Status Distribution")
            if research_projects:
                status_counts = {}
                for p in research_projects:
                    status = p.get("status", "unknown")
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                for status, count in status_counts.items():
                    st.metric(status.capitalize(), count)
            else:
                st.info("No data available")
        
        # Clinical trials
        st.markdown("### 🏥 Clinical Trials Status")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if clinical_trials:
                st.dataframe(
                    [{
                        "Trial ID": t.get("trial_id", "N/A"),
                        "Drug Name": t.get("drug_name", "N/A"),
                        "Phase": t.get("phase", "N/A"),
                        "Status": t.get("status", "N/A"),
                        "Participants": f"{t.get('enrolled_participants', 0)}/{t.get('target_participants', 0)}",
                        "Start Date": t.get("start_date", "N/A")
                    } for t in clinical_trials[:10]],
                    use_container_width=True,
                    height=300
                )
            else:
                st.info("No clinical trials found. Create your first trial in the Clinical Trials page.")
        
        with col2:
            st.markdown("#### Trial Phase Distribution")
            if clinical_trials:
                phase_counts = {}
                for t in clinical_trials:
                    phase = t.get("phase", "unknown")
                    phase_counts[phase] = phase_counts.get(phase, 0) + 1
                
                for phase, count in phase_counts.items():
                    st.metric(phase.capitalize(), count)
            else:
                st.info("No data available")
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")

with tab2:
    st.markdown("### 🧪 Recent Laboratory Activity")
    
    try:
        # Recent experiments
        experiments = db.get_lab_experiments(limit=20)
        experiments_sorted = sorted(experiments, key=lambda x: x.get("created_at", ""), reverse=True)
        
        if experiments_sorted:
            st.markdown("#### Latest Experiments")
            for exp in experiments_sorted[:10]:
                with st.expander(f"🧪 {exp.get('experiment_id', 'N/A')} - {exp.get('experiment_type', 'N/A')}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Scientist:** {exp.get('scientist_name', 'N/A')}")
                        st.write(f"**Type:** {exp.get('experiment_type', 'N/A')}")
                    with col2:
                        st.write(f"**Status:** {exp.get('status', 'N/A')}")
                        st.write(f"**Date:** {exp.get('experiment_date', 'N/A')}")
                    with col3:
                        st.write(f"**Compound:** {exp.get('compound_tested', 'N/A')}")
                        st.write(f"**Success:** {exp.get('success', 'N/A')}")
                    
                    if exp.get("results"):
                        st.write(f"**Results:** {exp.get('results')}")
        else:
            st.info("No recent experiments found. Record your first experiment in the Lab Experiments page.")
        
    except Exception as e:
        st.error(f"Error loading recent activity: {str(e)}")

with tab3:
    st.markdown("### 📈 Research Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Drug Development Pipeline")
        try:
            drug_candidates = db.get_drug_candidates(limit=1000)
            
            if drug_candidates:
                stage_counts = {}
                for candidate in drug_candidates:
                    stage = candidate.get("stage", "unknown")
                    stage_counts[stage] = stage_counts.get(stage, 0) + 1
                
                st.write("**Candidates by Development Stage:**")
                for stage, count in sorted(stage_counts.items()):
                    st.metric(stage.replace("_", " ").title(), count)
            else:
                st.info("No drug candidates in pipeline")
        except Exception as e:
            st.error(f"Error loading pipeline data: {str(e)}")
    
    with col2:
        st.markdown("#### Research Output Metrics")
        try:
            stats = db.get_collection_stats()
            
            st.metric("Total Publications", stats.get("research_publications", 0))
            st.metric("Patent Applications", stats.get("patent_documents", 0))
            st.metric("Research Compounds", stats.get("research_compounds", 0))
            st.metric("Molecular Structures", stats.get("molecular_structures", 0))
            
        except Exception as e:
            st.error(f"Error loading metrics: {str(e)}")

with tab4:
    st.markdown("### ⚙️ System Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Database Connection")
        st.write(f"**Keyspace:** medicines_research")
        st.write(f"**Provider:** DataStax Astra DB Serverless")
        st.write(f"**Region:** US-East-2")
        st.write(f"**Status:** ✅ Connected")
        
        st.markdown("#### Collection Overview")
        try:
            collection_names = db.get_collection_names()
            st.write(f"**Total Collections:** {len(collection_names)}/10")
            st.write("**Collections:**")
            for name in sorted(collection_names):
                st.write(f"  • {name}")
        except Exception as e:
            st.error(f"Error loading collections: {str(e)}")
    
    with col2:
        st.markdown("#### Collection Statistics")
        try:
            stats = db.get_collection_stats()
            
            st.markdown("**Regular Collections (7):**")
            st.write(f"  • research_projects: {stats.get('research_projects', 0)}")
            st.write(f"  • clinical_trials: {stats.get('clinical_trials', 0)}")
            st.write(f"  • drug_candidates: {stats.get('drug_candidates', 0)}")
            st.write(f"  • lab_experiments: {stats.get('lab_experiments', 0)}")
            st.write(f"  • research_compounds: {stats.get('research_compounds', 0)}")
            st.write(f"  • trial_participants: {stats.get('trial_participants', 0)}")
            st.write(f"  • research_publications: {stats.get('research_publications', 0)}")
            
            st.markdown("**Vector Collections (3) - 1536D:**")
            st.write(f"  • molecular_structures: {stats.get('molecular_structures', 0)}")
            st.write(f"  • research_papers: {stats.get('research_papers', 0)}")
            st.write(f"  • patent_documents: {stats.get('patent_documents', 0)}")
            
        except Exception as e:
            st.error(f"Error loading statistics: {str(e)}")
        
        st.markdown("#### Features")
        st.write("✅ Vector Search (1536D)")
        st.write("✅ OpenAI Embeddings")
        st.write("✅ Real-time Research Tracking")
        st.write("✅ Clinical Trial Management")
        st.write("✅ Drug Discovery Pipeline")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "🔬 Medicines Research Laboratory | Powered by Astra DB Serverless & OpenAI | Version 1.0.0"
    "</div>",
    unsafe_allow_html=True
)
