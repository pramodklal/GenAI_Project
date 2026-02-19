"""
Analytics & Reports Page - Streamlit UI

System analytics, reports, and performance metrics.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Page header
st.markdown("# 📊 Analytics & Reports")
st.markdown("### System Performance & Insights")

# Date range selector
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    start_date = st.date_input(
        "Start Date",
        value=(datetime.now() - timedelta(days=7)).date()
    )
with col2:
    end_date = st.date_input(
        "End Date",
        value=datetime.now().date()
    )
with col3:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "🍽️ Meal Orders", "🍳 Food Production", "🧹 EVS Tasks"])

with tab1:
    st.markdown("## System Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Orders",
            "1,247",
            "+15.2%"
        )
    
    with col2:
        st.metric(
            "Success Rate",
            "98.5%",
            "+1.2%"
        )
    
    with col3:
        st.metric(
            "EVS Tasks",
            "892",
            "-5.3%"
        )
    
    with col4:
        st.metric(
            "Cost Savings",
            "$12,450",
            "+$2,100"
        )
    
    st.markdown("---")
    
    # Activity trends
    st.markdown("### 📈 Activity Trends (Last 7 Days)")
    
    # Sample data
    dates = pd.date_range(end=datetime.now(), periods=7).strftime('%Y-%m-%d').tolist()
    trends_df = pd.DataFrame({
        'Date': dates,
        'Meal Orders': [145, 152, 148, 160, 155, 158, 162],
        'EVS Tasks': [125, 130, 128, 135, 132, 138, 140],
        'Validation Success': [98, 97, 99, 98, 99, 98, 99]
    })
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=trends_df['Date'], y=trends_df['Meal Orders'], 
                             mode='lines+markers', name='Meal Orders'))
    fig.add_trace(go.Scatter(x=trends_df['Date'], y=trends_df['EVS Tasks'], 
                             mode='lines+markers', name='EVS Tasks'))
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Count",
        hovermode='x unified',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Department breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏥 Department Activity")
        dept_df = pd.DataFrame({
            'Department': ['ICU', 'General Ward', 'Emergency', 'Surgery', 'Pediatrics'],
            'Orders': [180, 245, 95, 160, 140]
        })
        fig = px.pie(dept_df, values='Orders', names='Department', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### ⏱️ Response Times")
        response_df = pd.DataFrame({
            'Metric': ['Meal Validation', 'Order Submission', 'EVS Assignment', 'Task Completion'],
            'Avg Time (min)': [2.3, 5.1, 3.8, 28.5]
        })
        fig = px.bar(response_df, x='Metric', y='Avg Time (min)', color='Avg Time (min)')
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("## 🍽️ Meal Order Analytics")
    
    # Meal order metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Orders", "1,247", "+12%")
    with col2:
        st.metric("Validation Rate", "98.5%", "+0.8%")
    with col3:
        st.metric("Avg Processing Time", "4.2 min", "-0.5 min")
    
    st.markdown("---")
    
    # Meal type distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Meal Type Distribution")
        meal_types_df = pd.DataFrame({
            'Meal Type': ['Breakfast', 'Lunch', 'Dinner', 'Snack'],
            'Count': [385, 445, 340, 77]
        })
        fig = px.bar(meal_types_df, x='Meal Type', y='Count', color='Meal Type')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Dietary Restrictions")
        restrictions_df = pd.DataFrame({
            'Restriction': ['Low Sodium', 'Diabetic', 'Vegetarian', 'Gluten Free', 'None'],
            'Count': [245, 198, 156, 89, 559]
        })
        fig = px.bar(restrictions_df, x='Restriction', y='Count', color='Restriction')
        st.plotly_chart(fig, use_container_width=True)
    
    # Validation issues
    st.markdown("### ⚠️ Top Validation Issues")
    issues_df = pd.DataFrame({
        'Issue': ['Sodium Limit Exceeded', 'Allergen Detected', 'Calorie Limit', 'Missing Nutrients', 'Other'],
        'Occurrences': [45, 28, 18, 12, 8],
        'Resolution Rate': [95, 98, 92, 88, 90]
    })
    
    st.dataframe(
        issues_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Issue": "Issue Type",
            "Occurrences": st.column_config.NumberColumn("Count", format="%d"),
            "Resolution Rate": st.column_config.ProgressColumn("Resolution %", format="%.0f%%", min_value=0, max_value=100)
        }
    )
    
    # Patient satisfaction
    st.markdown("### ⭐ Patient Satisfaction")
    satisfaction_df = pd.DataFrame({
        'Rating': ['5 Stars', '4 Stars', '3 Stars', '2 Stars', '1 Star'],
        'Count': [678, 345, 145, 52, 27]
    })
    fig = px.bar(satisfaction_df, x='Rating', y='Count', color='Count', 
                 color_continuous_scale='RdYlGn')
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("## 🍳 Food Production Analytics")
    
    # Production metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Forecast Accuracy", "94.2%", "+2.1%")
    with col2:
        st.metric("Waste Reduction", "22%", "+5%")
    with col3:
        st.metric("Cost Savings", "$8,450", "+$1,200")
    with col4:
        st.metric("Prep Efficiency", "89%", "+3%")
    
    st.markdown("---")
    
    # Demand forecast vs actual
    st.markdown("### 📊 Demand Forecast vs Actual")
    forecast_df = pd.DataFrame({
        'Date': dates,
        'Forecasted': [145, 152, 148, 160, 155, 158, 162],
        'Actual': [142, 155, 145, 158, 157, 156, 164]
    })
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=forecast_df['Date'], y=forecast_df['Forecasted'], 
                             mode='lines+markers', name='Forecasted'))
    fig.add_trace(go.Scatter(x=forecast_df['Date'], y=forecast_df['Actual'], 
                             mode='lines+markers', name='Actual'))
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Meal Count",
        hovermode='x unified',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Waste analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ♻️ Waste by Category")
        waste_df = pd.DataFrame({
            'Category': ['Expired Items', 'Overproduction', 'Spoilage', 'Spillage'],
            'Units': [45, 32, 18, 12],
            'Value ($)': [380, 290, 165, 85]
        })
        fig = px.bar(waste_df, x='Category', y='Value ($)', color='Category')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📈 Waste Trend")
        waste_trend_df = pd.DataFrame({
            'Week': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            'Waste Units': [125, 108, 95, 87]
        })
        fig = px.line(waste_trend_df, x='Week', y='Waste Units', markers=True)
        st.plotly_chart(fig, use_container_width=True)
    
    # Inventory turnover
    st.markdown("### 📦 Inventory Turnover")
    turnover_df = pd.DataFrame({
        'Item Category': ['Proteins', 'Vegetables', 'Grains', 'Dairy', 'Beverages'],
        'Turnover Days': [3.2, 2.1, 5.4, 4.8, 6.2],
        'Stock Level': [85, 92, 78, 88, 95]
    })
    
    st.dataframe(
        turnover_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Item Category": "Category",
            "Turnover Days": st.column_config.NumberColumn("Avg Turnover (days)", format="%.1f"),
            "Stock Level": st.column_config.ProgressColumn("Stock Level %", format="%.0f%%", min_value=0, max_value=100)
        }
    )

with tab4:
    st.markdown("## 🧹 EVS Task Analytics")
    
    # EVS metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Tasks Completed", "892", "+8%")
    with col2:
        st.metric("Avg Response Time", "12.5 min", "-2 min")
    with col3:
        st.metric("Staff Utilization", "87%", "+4%")
    with col4:
        st.metric("Compliance Rate", "99.2%", "+0.5%")
    
    st.markdown("---")
    
    # Task distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Task Type Distribution")
        task_types_df = pd.DataFrame({
            'Task Type': ['Room Cleaning', 'Terminal Cleaning', 'Spill Response', 'Trash Removal', 'Restroom'],
            'Count': [345, 198, 87, 156, 106]
        })
        fig = px.pie(task_types_df, values='Count', names='Task Type', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Priority Distribution")
        priority_df = pd.DataFrame({
            'Priority': ['High', 'Medium', 'Low'],
            'Count': [245, 456, 191]
        })
        fig = px.bar(priority_df, x='Priority', y='Count', color='Priority',
                     color_discrete_map={'High': 'red', 'Medium': 'yellow', 'Low': 'green'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Completion time analysis
    st.markdown("### ⏱️ Task Completion Times")
    completion_df = pd.DataFrame({
        'Task Type': ['Room Cleaning', 'Terminal Cleaning', 'Spill Response', 'Trash Removal', 'Restroom'],
        'Avg Time (min)': [28, 45, 15, 12, 22],
        'Target (min)': [30, 50, 20, 15, 25]
    })
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Actual', x=completion_df['Task Type'], y=completion_df['Avg Time (min)']))
    fig.add_trace(go.Bar(name='Target', x=completion_df['Task Type'], y=completion_df['Target (min)']))
    
    fig.update_layout(barmode='group', xaxis_title="Task Type", yaxis_title="Minutes")
    st.plotly_chart(fig, use_container_width=True)
    
    # Staff performance
    st.markdown("### 👥 Staff Performance")
    staff_perf_df = pd.DataFrame({
        'Staff ID': ['EVS-001', 'EVS-002', 'EVS-003', 'EVS-004', 'EVS-005'],
        'Tasks Completed': [145, 138, 142, 135, 128],
        'Avg Time (min)': [24, 26, 23, 27, 25],
        'Quality Score': [98, 95, 97, 94, 96]
    })
    
    st.dataframe(
        staff_perf_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Staff ID": "Staff",
            "Tasks Completed": st.column_config.NumberColumn("Tasks", format="%d"),
            "Avg Time (min)": st.column_config.NumberColumn("Avg Time", format="%.1f min"),
            "Quality Score": st.column_config.ProgressColumn("Quality", format="%.0f%%", min_value=0, max_value=100)
        }
    )

# Export reports
st.markdown("---")
st.markdown("## 📥 Export Reports")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 Export All Analytics", use_container_width=True):
        st.info("Full analytics report exported")

with col2:
    if st.button("📈 Export Charts", use_container_width=True):
        st.info("Charts exported as images")

with col3:
    if st.button("📋 Export Raw Data", use_container_width=True):
        st.info("Raw data exported as CSV")

# Help section
with st.expander("❓ Help & Instructions"):
    st.markdown("""
    ### Analytics & Reports Guide
    
    **Overview Tab:**
    - System-wide performance metrics
    - Activity trends across all modules
    - Department breakdown
    - Response time analysis
    
    **Meal Orders Tab:**
    - Order volume and validation rates
    - Dietary restriction analysis
    - Validation issue tracking
    - Patient satisfaction ratings
    
    **Food Production Tab:**
    - Forecast accuracy metrics
    - Waste reduction tracking
    - Inventory turnover analysis
    - Cost savings calculations
    
    **EVS Tasks Tab:**
    - Task completion statistics
    - Response time analysis
    - Staff performance tracking
    - Compliance monitoring
    
    **Export Options:**
    - Export complete analytics reports
    - Save charts as images
    - Download raw data as CSV files
    """)
