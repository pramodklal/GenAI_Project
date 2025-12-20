"""
Healthcare Digital - Streamlit UI Main Application

Multi-page Streamlit application for Healthcare Digital's Agentic AI System.
"""

import streamlit as st
from datetime import datetime
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Page configuration
st.set_page_config(
    page_title="Healthcare Digital AI System",
    page_icon="🏥",
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
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("🏥 HealthCare Digital")
    st.markdown("**Enterprise AI Platform**")
    st.markdown("**Environment:** Astra DB Serverless")
    st.markdown("---")
    
    # Solution Summary
    st.markdown("#### 🎯 Solution Overview")
    st.info("""
    **Enterprise Healthcare Operations Platform**
    
    🍽️ **Patient Meal Services**
    - AI-Powered Meal Ordering
    - Nutrition Validation & Compliance
    - Dietary Rule Enforcement
    - Personalized Recommendations
    - Automated Order Processing
    
    🍳 **Food Production**
    - Demand Forecasting
    - Prep Planning & Scheduling
    - Inventory Management
    - Waste Reduction Strategies
    - Equipment Optimization
    
    🧹 **EVS Management**
    - Smart Task Assignment
    - Route Optimization
    - Priority Scheduling
    - Environmental Monitoring
    - Compliance Tracking
    
    📊 **Analytics & Insights**
    - Real-time Operational Metrics
    - Waste Reduction Analytics
    - Performance Dashboards
    - Predictive Analytics
    - Compliance Reporting
    
    🤖 **AI & Integration**
    - Multi-Agent AI System
    - Natural Language Processing
    - 🔌 **22 MCP Tools** (Meal, Production, EVS, Analytics)
    - Automated Validation
    - 24/7 Operational Support
    """)
    
    st.markdown("---")
    
    # System Status
    st.markdown("#### 📈 System Status")
    st.success("✅ All Systems Operational")
    st.caption(f"🕒 Last Updated: {datetime.now().strftime('%H:%M:%S')}")
    st.caption("🟢 Database Connected")
    st.caption("🤖 AI Agents Active")
    
    st.markdown("---")
    st.caption("🚀 Enterprise Healthcare AI | Dec 2025")

# Main content area - Home Dashboard
st.markdown('<div class="main-header">Healthcare Digital AI System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Intelligent Automation for Healthcare Operations</div>', unsafe_allow_html=True)

# Key metrics
st.markdown("## 📈 Today's Overview")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Meal Orders",
        value="124",
        delta="12 from yesterday",
        delta_color="normal"
    )

with col2:
    st.metric(
        label="Validation Rate",
        value="98.5%",
        delta="1.2%",
        delta_color="normal"
    )

with col3:
    st.metric(
        label="EVS Tasks",
        value="47",
        delta="-8 from yesterday",
        delta_color="inverse"
    )

with col4:
    st.metric(
        label="Waste Reduction",
        value="22%",
        delta="5%",
        delta_color="normal"
    )

st.markdown("---")

# System capabilities
st.markdown("## 🤖 AI Agent Capabilities")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🍽️ Patient Meal Ordering")
    st.markdown("""
    - ✅ Nutrition Validation
    - ✅ Dietary Rule Enforcement
    - ✅ Personalized Recommendations
    - ✅ Automated Order Processing
    - ✅ Real-time Compliance Checks
    """)
    st.info("👈 Use the sidebar to navigate to pages")

with col2:
    st.markdown("### 🍳 Food Production")
    st.markdown("""
    - ✅ Demand Forecasting
    - ✅ Prep Planning & Scheduling
    - ✅ Inventory Management
    - ✅ Waste Reduction Strategies
    - ✅ Equipment Optimization
    """)
    st.info("👈 Use the sidebar to navigate to pages")

with col3:
    st.markdown("### 🧹 EVS Task Management")
    st.markdown("""
    - ✅ Task Prioritization
    - ✅ Smart Assignment
    - ✅ Route Optimization
    - ✅ Environmental Monitoring
    - ✅ Compliance Tracking
    """)
    st.info("👈 Use the sidebar to navigate to pages")

st.markdown("---")

# Recent activity
st.markdown("## 📋 Recent Activity")

activities = [
    {"time": "10:45 AM", "type": "Meal Order", "description": "Order #1234 validated and submitted for Patient P12345", "status": "success"},
    {"time": "10:42 AM", "type": "EVS Task", "description": "Task #EVS-567 assigned to Staff EVS-001", "status": "success"},
    {"time": "10:38 AM", "type": "Waste Alert", "description": "5 items identified at risk of expiration in next 24 hours", "status": "warning"},
    {"time": "10:35 AM", "type": "Food Production", "description": "Prep schedule generated for lunch service", "status": "success"},
    {"time": "10:30 AM", "type": "System", "description": "Daily demand forecast completed", "status": "info"},
]

for activity in activities:
    status_icon = {
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
        "info": "ℹ️"
    }
    
    cols = st.columns([1, 2, 6, 1])
    with cols[0]:
        st.markdown(f"**{activity['time']}**")
    with cols[1]:
        st.markdown(f"*{activity['type']}*")
    with cols[2]:
        st.markdown(activity['description'])
    with cols[3]:
        st.markdown(status_icon.get(activity['status'], ""))

st.markdown("---")

# System architecture
with st.expander("📐 View System Architecture"):
    st.markdown("""
    ### Multi-Layer Architecture
    
    1. **UI Layer** - Streamlit interface (this application)
    2. **Agent Orchestration** - LangGraph workflow management
    3. **Multi-Agent System** - Specialized AI agents
    4. **MCP Server Layer** - Secure tool access via Model Context Protocol
    5. **Data Science Layer** - Predictive models and ML
    6. **Data Layer** - PostgreSQL, Redis, EHR integration
    """)
    
    st.info("📊 View detailed architecture diagrams in `docs/architecture_diagram.drawio`")

# Healthcare Services
st.markdown("## 🏥 Healthcare Services")
st.info("👈 Use the sidebar menu above to navigate to different sections")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("**🍽️ Meal Ordering**")
    st.caption("Create and validate patient meal orders")

with col2:
    st.markdown("**🍳 Food Production**")
    st.caption("Manage inventory and production")

with col3:
    st.markdown("**🧹 EVS Management**")
    st.caption("Prioritize and assign tasks")

with col4:
    st.markdown("**📊 Analytics**")
    st.caption("View reports and metrics")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    st.markdown("""
        <div style='text-align: center; color: #666; font-size: 0.8rem;'>
        Healthcare Digital © 2025<br>
        Powered by MCP | OpenAI | Astra DB | LangGraph & AI Agents<br>
        <span style='color: #ff4b4b;'>❤️</span> Developed by Pramod Lal Das with Love
        </div>
    """, unsafe_allow_html=True)
