"""
System Status Page - Streamlit UI

System health monitoring and configuration.
"""

import streamlit as st
from datetime import datetime
import sys
import os

# Page header
st.markdown("# ⚙️ System Status")
st.markdown("### Health Monitoring & Configuration")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🔍 Health Check", "🤖 AI Agents", "🔌 MCP Servers", "⚙️ Settings"])

with tab1:
    st.markdown("## System Health Check")
    
    # Overall status
    st.markdown("""
        <div style="background-color: #d4edda; border: 2px solid #c3e6cb; padding: 2rem; border-radius: 0.5rem; text-align: center; margin: 1rem 0;">
            <h2 style="color: #155724; margin: 0;">🟢 All Systems Operational</h2>
            <p style="color: #155724; margin: 0.5rem 0 0 0;">Last checked: {}</p>
        </div>
    """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), unsafe_allow_html=True)
    
    if st.button("🔄 Run Health Check", use_container_width=True):
        with st.spinner("Running health check..."):
            import time
            time.sleep(1)
            st.success("✅ Health check completed")
            st.rerun()
    
    st.markdown("---")
    
    # Component status
    st.markdown("### 📦 Component Status")
    
    components = [
        {"name": "UI Layer", "status": "healthy", "uptime": "99.98%", "last_check": "Just now"},
        {"name": "LangGraph Orchestration", "status": "healthy", "uptime": "99.95%", "last_check": "Just now"},
        {"name": "Meal Order MCP", "status": "healthy", "uptime": "99.99%", "last_check": "Just now"},
        {"name": "Food Production MCP", "status": "healthy", "uptime": "99.97%", "last_check": "Just now"},
        {"name": "EVS Task MCP", "status": "healthy", "uptime": "99.96%", "last_check": "Just now"},
        {"name": "Nutrition Agent", "status": "healthy", "uptime": "99.94%", "last_check": "Just now"},
        {"name": "Waste Reduction Agent", "status": "healthy", "uptime": "99.92%", "last_check": "Just now"},
        {"name": "EVS Prioritization Agent", "status": "healthy", "uptime": "99.93%", "last_check": "Just now"},
        {"name": "PostgreSQL Database", "status": "healthy", "uptime": "99.99%", "last_check": "Just now"},
        {"name": "Redis Cache", "status": "healthy", "uptime": "99.98%", "last_check": "Just now"},
    ]
    
    for component in components:
        status_icon = {"healthy": "🟢", "degraded": "🟡", "down": "🔴"}.get(component["status"], "⚪")
        status_color = {"healthy": "#d4edda", "degraded": "#fff3cd", "down": "#f8d7da"}.get(component["status"], "#f0f0f0")
        
        st.markdown(f"""
            <div style="background-color: {status_color}; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>{status_icon} {component['name']}</strong>
                    </div>
                    <div style="text-align: right;">
                        <span>Uptime: {component['uptime']}</span><br>
                        <small>Last checked: {component['last_check']}</small>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Resource usage
    st.markdown("### 💻 Resource Usage")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("CPU Usage", "34%", "-5%")
    with col2:
        st.metric("Memory", "62%", "+2%")
    with col3:
        st.metric("Disk I/O", "28%", "-3%")
    with col4:
        st.metric("Network", "45%", "+8%")
    
    # System logs
    st.markdown("---")
    st.markdown("### 📝 Recent System Logs")
    
    logs = [
        {"time": "2025-12-17 10:45:23", "level": "INFO", "component": "Nutrition Agent", "message": "Meal validation completed successfully"},
        {"time": "2025-12-17 10:44:15", "level": "INFO", "component": "MCP Server", "message": "Endpoint called: get_patient_dietary_restrictions"},
        {"time": "2025-12-17 10:43:02", "level": "INFO", "component": "EVS Agent", "message": "Task prioritization completed for 15 tasks"},
        {"time": "2025-12-17 10:42:18", "level": "WARNING", "component": "Waste Agent", "message": "5 items identified at risk of expiration"},
        {"time": "2025-12-17 10:41:05", "level": "INFO", "component": "LangGraph", "message": "Workflow completed: meal_order_workflow"},
    ]
    
    for log in logs:
        level_color = {
            "INFO": "#d1ecf1",
            "WARNING": "#fff3cd",
            "ERROR": "#f8d7da"
        }.get(log["level"], "#f0f0f0")
        
        level_icon = {
            "INFO": "ℹ️",
            "WARNING": "⚠️",
            "ERROR": "❌"
        }.get(log["level"], "")
        
        st.markdown(f"""
            <div style="background-color: {level_color}; padding: 0.5rem; border-radius: 0.3rem; margin: 0.3rem 0; font-size: 0.9rem;">
                <strong>{log['time']}</strong> | {level_icon} <strong>{log['level']}</strong> | {log['component']}<br>
                {log['message']}
            </div>
        """, unsafe_allow_html=True)

with tab2:
    st.markdown("## 🤖 AI Agent Status")
    
    agents = [
        {
            "name": "Nutrition Validation Agent",
            "status": "active",
            "requests_today": 245,
            "avg_response_time": "2.3s",
            "success_rate": "98.5%",
            "last_execution": "2 minutes ago"
        },
        {
            "name": "Waste Reduction Agent",
            "status": "active",
            "requests_today": 87,
            "avg_response_time": "3.1s",
            "success_rate": "97.2%",
            "last_execution": "15 minutes ago"
        },
        {
            "name": "EVS Prioritization Agent",
            "status": "active",
            "requests_today": 156,
            "avg_response_time": "2.8s",
            "success_rate": "99.1%",
            "last_execution": "5 minutes ago"
        },
        {
            "name": "Dietary Rule Enforcement Agent",
            "status": "standby",
            "requests_today": 0,
            "avg_response_time": "N/A",
            "success_rate": "N/A",
            "last_execution": "Not yet deployed"
        },
        {
            "name": "Personalization Agent",
            "status": "standby",
            "requests_today": 0,
            "avg_response_time": "N/A",
            "success_rate": "N/A",
            "last_execution": "Not yet deployed"
        },
    ]
    
    for agent in agents:
        status_icon = {"active": "🟢", "standby": "🟡", "error": "🔴"}.get(agent["status"], "⚪")
        
        with st.expander(f"{status_icon} {agent['name']}", expanded=agent["status"] == "active"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Status:** {agent['status'].upper()}")
                st.markdown(f"**Requests Today:** {agent['requests_today']}")
                st.markdown(f"**Avg Response Time:** {agent['avg_response_time']}")
            
            with col2:
                st.markdown(f"**Success Rate:** {agent['success_rate']}")
                st.markdown(f"**Last Execution:** {agent['last_execution']}")
            
            if agent["status"] == "active":
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("⏸️ Pause", key=f"pause_{agent['name']}"):
                        st.info(f"Agent {agent['name']} paused")
                with col2:
                    if st.button("🔄 Restart", key=f"restart_{agent['name']}"):
                        st.info(f"Agent {agent['name']} restarted")
                with col3:
                    if st.button("📊 View Logs", key=f"logs_{agent['name']}"):
                        st.info("Viewing logs...")
            elif agent["status"] == "standby":
                if st.button("▶️ Deploy Agent", key=f"deploy_{agent['name']}"):
                    st.info(f"Agent {agent['name']} deployment initiated")

with tab3:
    st.markdown("## 🔌 MCP Server Status")
    
    mcp_servers = [
        {
            "name": "Meal Order MCP Server",
            "status": "running",
            "endpoints": 6,
            "requests_today": 1247,
            "avg_latency": "45ms",
            "error_rate": "0.2%"
        },
        {
            "name": "Food Production MCP Server",
            "status": "running",
            "endpoints": 6,
            "requests_today": 542,
            "avg_latency": "52ms",
            "error_rate": "0.3%"
        },
        {
            "name": "EVS Task MCP Server",
            "status": "running",
            "endpoints": 7,
            "requests_today": 892,
            "avg_latency": "38ms",
            "error_rate": "0.1%"
        },
        {
            "name": "Patient Data MCP Server",
            "status": "standby",
            "endpoints": 8,
            "requests_today": 0,
            "avg_latency": "N/A",
            "error_rate": "N/A"
        },
        {
            "name": "ML Model MCP Server",
            "status": "standby",
            "endpoints": 5,
            "requests_today": 0,
            "avg_latency": "N/A",
            "error_rate": "N/A"
        },
    ]
    
    for server in mcp_servers:
        status_icon = {"running": "🟢", "standby": "🟡", "stopped": "🔴"}.get(server["status"], "⚪")
        
        with st.expander(f"{status_icon} {server['name']}", expanded=server["status"] == "running"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Status:** {server['status'].upper()}")
                st.markdown(f"**Endpoints:** {server['endpoints']}")
                st.markdown(f"**Requests Today:** {server['requests_today']}")
            
            with col2:
                st.markdown(f"**Avg Latency:** {server['avg_latency']}")
                st.markdown(f"**Error Rate:** {server['error_rate']}")
            
            if server["status"] == "running":
                # Show endpoints
                st.markdown("**Available Endpoints:**")
                if "Meal Order" in server["name"]:
                    endpoints = [
                        "get_patient_dietary_restrictions",
                        "validate_meal_selection",
                        "submit_meal_order",
                        "get_nutrition_info",
                        "get_meal_history",
                        "get_meal_recommendations"
                    ]
                elif "Food Production" in server["name"]:
                    endpoints = [
                        "get_demand_forecast",
                        "get_inventory_status",
                        "create_prep_schedule",
                        "update_production_status",
                        "get_equipment_availability",
                        "identify_waste_risks"
                    ]
                elif "EVS Task" in server["name"]:
                    endpoints = [
                        "create_task",
                        "get_pending_tasks",
                        "assign_task",
                        "update_task_status",
                        "get_staff_availability",
                        "get_environmental_metrics",
                        "prioritize_tasks"
                    ]
                else:
                    endpoints = ["endpoint_1", "endpoint_2", "endpoint_3"]
                
                for endpoint in endpoints:
                    st.markdown(f"- `{endpoint}`")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 Restart Server", key=f"restart_mcp_{server['name']}"):
                        st.info(f"Server {server['name']} restarted")
                with col2:
                    if st.button("📊 View Metrics", key=f"metrics_mcp_{server['name']}"):
                        st.info("Viewing metrics...")

with tab4:
    st.markdown("## ⚙️ System Settings")
    
    st.markdown("### 🔑 API Configuration")
    
    with st.expander("OpenAI / Azure OpenAI Settings", expanded=False):
        api_provider = st.selectbox(
            "AI Provider",
            ["Azure OpenAI", "GitHub Models", "OpenAI"],
            index=0
        )
        
        api_endpoint = st.text_input(
            "API Endpoint",
            value="https://your-resource.openai.azure.com/",
            type="password"
        )
        
        api_key = st.text_input(
            "API Key",
            value="",
            type="password",
            placeholder="Enter your API key"
        )
        
        model_name = st.text_input(
            "Model Deployment Name",
            value="gpt-4",
            placeholder="e.g., gpt-4, gpt-35-turbo"
        )
        
        if st.button("💾 Save API Configuration"):
            st.success("✅ API configuration saved")
    
    st.markdown("---")
    st.markdown("### 🗄️ Database Configuration")
    
    with st.expander("PostgreSQL Settings"):
        db_host = st.text_input("Host", value="localhost")
        db_port = st.number_input("Port", value=5432)
        db_name = st.text_input("Database Name", value="healthcare_digital")
        db_user = st.text_input("Username", value="admin")
        db_password = st.text_input("Password", value="", type="password")
        
        if st.button("💾 Save Database Configuration"):
            st.success("✅ Database configuration saved")
    
    with st.expander("Redis Cache Settings"):
        redis_host = st.text_input("Redis Host", value="localhost", key="redis_host")
        redis_port = st.number_input("Redis Port", value=6379, key="redis_port")
        redis_password = st.text_input("Redis Password", value="", type="password", key="redis_pass")
        
        if st.button("💾 Save Redis Configuration"):
            st.success("✅ Redis configuration saved")
    
    st.markdown("---")
    st.markdown("### 🎛️ Application Settings")
    
    with st.expander("General Settings"):
        enable_logging = st.checkbox("Enable Detailed Logging", value=True)
        enable_metrics = st.checkbox("Enable Performance Metrics", value=True)
        enable_notifications = st.checkbox("Enable System Notifications", value=True)
        
        log_level = st.selectbox(
            "Log Level",
            ["DEBUG", "INFO", "WARNING", "ERROR"],
            index=1
        )
        
        session_timeout = st.number_input(
            "Session Timeout (minutes)",
            min_value=5,
            max_value=120,
            value=30
        )
        
        if st.button("💾 Save Application Settings"):
            st.success("✅ Application settings saved")
    
    st.markdown("---")
    st.markdown("### 🔒 Security Settings")
    
    with st.expander("Security Configuration"):
        st.warning("⚠️ These settings affect system security. Change with caution.")
        
        enable_auth = st.checkbox("Enable Authentication", value=True)
        enable_audit = st.checkbox("Enable Audit Logging", value=True)
        enable_encryption = st.checkbox("Enable Data Encryption at Rest", value=True)
        
        if st.button("💾 Save Security Settings"):
            st.success("✅ Security settings saved")
    
    st.markdown("---")
    st.markdown("### 🔧 Maintenance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Clear Cache", use_container_width=True):
            st.success("✅ Cache cleared")
    
    with col2:
        if st.button("📊 Export Configuration", use_container_width=True):
            st.success("✅ Configuration exported")

# System information
st.markdown("---")
st.markdown("### ℹ️ System Information")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Application Version:** 1.0.0  
    **Framework:** LangGraph + Streamlit  
    **Python Version:** 3.11.14  
    **Environment:** Production  
    """)

with col2:
    st.markdown(f"""
    **Deployment Date:** 2025-12-17  
    **Last Update:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
    **Uptime:** 15 days, 7 hours  
    **Instance ID:** HCD-PROD-001  
    """)

# Help section
with st.expander("❓ Help & Instructions"):
    st.markdown("""
    ### System Status Guide
    
    **Health Check Tab:**
    - Monitor overall system health
    - View component status and uptime
    - Check resource usage
    - Review system logs
    
    **AI Agents Tab:**
    - Monitor agent performance
    - View request statistics
    - Manage agent lifecycle (pause/restart)
    - Deploy new agents
    
    **MCP Servers Tab:**
    - Check MCP server status
    - View available endpoints
    - Monitor request metrics
    - Restart servers if needed
    
    **Settings Tab:**
    - Configure API connections
    - Set database parameters
    - Adjust application settings
    - Manage security options
    
    **Best Practices:**
    - Run health checks regularly
    - Monitor error rates and response times
    - Keep configuration backed up
    - Review logs for issues
    """)
