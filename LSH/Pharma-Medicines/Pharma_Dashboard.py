"""
Pharma-Medicines Manufacturing System - Landing Page
Main dashboard with real-time metrics and navigation
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from database.astra_helper import AstraDBHelper
from mcp_servers.medicine_mcp import MedicineMCPServer
from mcp_servers.quality_control_mcp import QualityControlMCPServer
from mcp_servers.production_mcp import ProductionMCPServer
from mcp_servers.compliance_mcp import ComplianceMCPServer
from mcp_servers.inventory_mcp import InventoryMCPServer

# Page configuration
st.set_page_config(
    page_title="Pharma-Medicines Manufacturing System",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #7f7f7f;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
    }
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.875rem;
        font-weight: 600;
    }
    .status-operational {
        background-color: #10b981;
        color: white;
    }
    .status-warning {
        background-color: #f59e0b;
        color: white;
    }
    .status-critical {
        background-color: #ef4444;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'db_helper' not in st.session_state:
    st.session_state.db_helper = AstraDBHelper()
if 'medicine_mcp' not in st.session_state:
    st.session_state.medicine_mcp = MedicineMCPServer()
if 'qc_mcp' not in st.session_state:
    st.session_state.qc_mcp = QualityControlMCPServer()
if 'production_mcp' not in st.session_state:
    st.session_state.production_mcp = ProductionMCPServer()
if 'compliance_mcp' not in st.session_state:
    st.session_state.compliance_mcp = ComplianceMCPServer()
if 'inventory_mcp' not in st.session_state:
    st.session_state.inventory_mcp = InventoryMCPServer()

def get_dashboard_metrics():
    """Fetch key metrics for dashboard"""
    db = st.session_state.db_helper
    
    try:
        # Total medicines
        medicines = list(db.medicines.find({}, limit=1000))
        total_medicines = len(medicines)
        
        # Active batches
        batches = list(db.manufacturing_batches.find({}, limit=1000))
        active_batches = len([b for b in batches if b.get("status") == "in_production"])
        
        # Pending QC tests
        qc_tests = list(db.quality_control_tests.find({}, limit=1000))
        pending_tests = len([q for q in qc_tests if q.get("pass_fail_status") == "pending"])
        
        # Low stock materials
        materials = list(db.raw_materials.find({}, limit=1000))
        low_stock = sum(1 for m in materials if m.get("quantity_in_stock", 0) <= m.get("reorder_point", 0))
        
        # Expiring documents (next 60 days)
        expiry_date = (datetime.utcnow() + timedelta(days=60)).isoformat()
        documents = list(db.regulatory_documents.find({}, limit=1000))
        expiring_docs = len([d for d in documents if d.get("expiry_date", "") <= expiry_date])
        
        # Recent adverse events (last 30 days)
        ae_date = (datetime.utcnow() - timedelta(days=30)).isoformat()
        adverse_events = list(db.adverse_events.find({}, limit=1000))
        recent_aes = len([ae for ae in adverse_events if ae.get("report_date", "") >= ae_date])
        
        return {
            "total_medicines": total_medicines,
            "active_batches": active_batches,
            "pending_tests": pending_tests,
            "low_stock": low_stock,
            "expiring_docs": expiring_docs,
            "recent_aes": recent_aes
        }
    except Exception as e:
        st.error(f"Error fetching metrics: {str(e)}")
        return {
            "total_medicines": 0,
            "active_batches": 0,
            "pending_tests": 0,
            "low_stock": 0,
            "expiring_docs": 0,
            "recent_aes": 0
        }

def get_batch_status_chart():
    """Create batch status distribution chart"""
    db = st.session_state.db_helper
    
    try:
        batches = list(db.manufacturing_batches.find({}, limit=1000))
        status_counts = {}
        for batch in batches:
            status = batch.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        fig = go.Figure(data=[go.Pie(
            labels=list(status_counts.keys()),
            values=list(status_counts.values()),
            hole=0.4,
            marker=dict(colors=['#10b981', '#3b82f6', '#f59e0b', '#ef4444'])
        )])
        
        fig.update_layout(
            title="Batch Status Distribution",
            height=300,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        return fig
    except Exception as e:
        st.error(f"Error creating chart: {str(e)}")
        return None

def get_production_timeline():
    """Create production timeline chart"""
    db = st.session_state.db_helper
    
    try:
        schedules = list(db.production_schedules.find({}, limit=100))
        
        if not schedules:
            return None
        
        fig = go.Figure()
        
        for schedule in schedules[:10]:  # Show last 10
            batch_id = schedule.get("batch_id", "Unknown")
            start = schedule.get("scheduled_start", "")
            end = schedule.get("scheduled_end", "")
            status = schedule.get("status", "unknown")
            
            color = '#10b981' if status == 'completed' else '#3b82f6' if status == 'in_progress' else '#9ca3af'
            
            fig.add_trace(go.Scatter(
                x=[start, end],
                y=[batch_id, batch_id],
                mode='lines+markers',
                name=batch_id,
                line=dict(color=color, width=8),
                marker=dict(size=10)
            ))
        
        fig.update_layout(
            title="Production Schedule Timeline",
            xaxis_title="Date",
            yaxis_title="Batch ID",
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
            showlegend=False
        )
        
        return fig
    except Exception as e:
        st.error(f"Error creating timeline: {str(e)}")
        return None

def get_quality_metrics():
    """Get quality control metrics"""
    db = st.session_state.db_helper
    
    try:
        tests = list(db.quality_control_tests.find({}, limit=1000))
        
        total_tests = len(tests)
        passed_tests = sum(1 for t in tests if t.get("pass_fail_status") == "pass")
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "pass_rate": pass_rate
        }
    except Exception as e:
        st.error(f"Error fetching quality metrics: {str(e)}")
        return {"total_tests": 0, "passed_tests": 0, "pass_rate": 0}

# Header
st.markdown('<div class="main-header">💊 Pharma-Medicines Manufacturing System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Powered Pharmaceutical Manufacturing & Quality Management Platform</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("💊 Pharma-Medicines")
    st.markdown("**Database:** pharma_manufacturing")
    st.markdown("**Environment:** Astra DB Serverless")
    st.markdown("---")
    
    # Solution Summary
    st.markdown("#### 🎯 Solution Overview")
    st.info("""
    **AI-Powered Manufacturing Platform**
    
    🤖 **6 AI Agents** (GPT-4o)
    - Quality Control Agent
    - Regulatory Compliance
    - Supply Chain Agent
    - Pharmacovigilance
    - Production Optimization
    - Equipment Maintenance
    
    💾 **13 Collections**
    - 10 Regular Collections
    - 3 Vector Search (1536D)
    
    🔌 **MCP Servers (5)**
    - Medicine MCP
    - Quality Control MCP
    - Production MCP
    - Compliance MCP
    - Inventory MCP
    
    📊 **Features**
    - Real-time Production Tracking
    - Quality Assurance (QA/QC)
    - Regulatory Compliance
    - Analytics Dashboard
    - CSV Import/Export
    """)
    
    st.markdown("---")
    
    # Data stats
    st.markdown("#### 📈 Data Status")
    try:
        metrics = get_dashboard_metrics()
        st.success(f"✅ System Operational")
        st.caption(f"💊 Medicines: {metrics['total_medicines']}")
        st.caption(f"🏭 Active Batches: {metrics['active_batches']}")
        st.caption(f"✅ Pending Tests: {metrics['pending_tests']}")
        st.caption(f"� Low Stock Items: {metrics['low_stock']}")
        st.caption(f"📜 Expiring Docs: {metrics['expiring_docs']}")
    except Exception as e:
        st.error(f"Error: {str(e)}")
    
    st.markdown("---")
    
    # Navigation
    st.markdown("### 🔬 Operations")
    st.page_link("pages/1_Medicine_Catalog.py", label="💊 Medicine Catalog", icon="💊")
    st.page_link("pages/2_Batch_Production.py", label="🏭 Batch Production", icon="🏭")
    st.page_link("pages/3_Quality_Control.py", label="✅ Quality Control", icon="✅")
    
    st.markdown("### 📋 Management")
    st.page_link("pages/4_Regulatory_Compliance.py", label="📜 Regulatory Compliance", icon="📜")
    st.page_link("pages/5_Inventory_Management.py", label="📦 Inventory Management", icon="📦")
    
    st.markdown("### 📈 Analytics")
    st.page_link("pages/6_Analytics.py", label="📊 Analytics Dashboard", icon="📊")
    
    st.markdown("---")
    st.caption("🚀 Professional Manufacturing System | Dec 2025")

# Main content
try:
    metrics = get_dashboard_metrics()
    
    # Key Metrics Row
    st.markdown("## 📊 Key Performance Indicators")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("Active Medicines", metrics["total_medicines"], delta=None)
    with col2:
        st.metric("Active Batches", metrics["active_batches"], delta=None)
    with col3:
        st.metric("Pending QC Tests", metrics["pending_tests"], delta=None)
    with col4:
        st.metric("Low Stock Items", metrics["low_stock"], delta=None, delta_color="inverse")
    with col5:
        st.metric("Expiring Docs", metrics["expiring_docs"], delta=None, delta_color="inverse")
    with col6:
        st.metric("Recent AEs (30d)", metrics["recent_aes"], delta=None)
    
    st.markdown("---")
    
    # Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Batch Status Overview")
        batch_chart = get_batch_status_chart()
        if batch_chart:
            st.plotly_chart(batch_chart, use_container_width=True)
    
    with col2:
        st.markdown("### ✅ Quality Control Performance")
        qc_metrics = get_quality_metrics()
        
        # Create gauge chart for pass rate
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=qc_metrics["pass_rate"],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "QC Pass Rate (%)"},
            delta={'reference': 95},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "#10b981"},
                'steps': [
                    {'range': [0, 80], 'color': "#fee2e2"},
                    {'range': [80, 95], 'color': "#fef3c7"},
                    {'range': [95, 100], 'color': "#d1fae5"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 95
                }
            }
        ))
        
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown(f"**Total Tests:** {qc_metrics['total_tests']}")
        st.markdown(f"**Passed:** {qc_metrics['passed_tests']}")
    
    st.markdown("---")
    
    # Production Timeline
    st.markdown("### 🏭 Production Schedule Overview")
    timeline = get_production_timeline()
    if timeline:
        st.plotly_chart(timeline, use_container_width=True)
    
    st.markdown("---")
    
    # Recent Activity
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Recent Batch Approvals")
        db = st.session_state.db_helper
        recent_batches = list(db.manufacturing_batches.find(
            {"status": "approved"},
            limit=5
        ))
        
        if recent_batches:
            for batch in recent_batches:
                with st.container():
                    st.markdown(f"""
                    **{batch.get('batch_number', 'N/A')}** - {batch.get('medicine_id', 'N/A')}  
                    Approved: {batch.get('approved_date', 'N/A')[:10]}  
                    Yield: {batch.get('yield_percentage', 0):.1f}%
                    """)
        else:
            st.info("No recent approvals")
    
    with col2:
        st.markdown("### ⚠️ Alerts & Notifications")
        
        # Low stock alerts
        if metrics["low_stock"] > 0:
            st.warning(f"🔴 {metrics['low_stock']} materials below reorder point")
        
        # Expiring documents
        if metrics["expiring_docs"] > 0:
            st.warning(f"⚠️ {metrics['expiring_docs']} documents expiring in 60 days")
        
        # Pending tests
        if metrics["pending_tests"] > 0:
            st.info(f"🔵 {metrics['pending_tests']} QC tests pending")
        
        # Recent adverse events
        if metrics["recent_aes"] > 0:
            st.info(f"📋 {metrics['recent_aes']} adverse events reported (30 days)")
        
        if metrics["low_stock"] == 0 and metrics["expiring_docs"] == 0 and metrics["pending_tests"] == 0:
            st.success("✅ All systems operational - No critical alerts")
    
    st.markdown("---")
    
    # Quick Actions
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🏭 Create New Batch", use_container_width=True):
            st.switch_page("pages/2_Batch_Production.py")
    
    with col2:
        if st.button("✅ Submit QC Test", use_container_width=True):
            st.switch_page("pages/3_Quality_Control.py")
    
    with col3:
        if st.button("📦 Check Inventory", use_container_width=True):
            st.switch_page("pages/5_Inventory_Management.py")
    
    with col4:
        if st.button("📊 View Analytics", use_container_width=True):
            st.switch_page("pages/6_Analytics.py")

except Exception as e:
    st.error(f"Error loading dashboard: {str(e)}")
    st.info("Please ensure Astra DB connection is configured correctly in .env file")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #7f7f7f; padding: 1rem;'>
    <p>Pharma-Medicines Manufacturing System v1.0 | Built with Streamlit & Astra DB</p>
    <p>Compliance: FDA 21 CFR Part 11 | GMP | ISO 9001:2015</p>
</div>
""", unsafe_allow_html=True)
