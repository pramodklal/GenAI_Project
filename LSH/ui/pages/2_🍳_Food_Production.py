"""
Food Production Page - Streamlit UI

Food production planning with demand forecasting and waste reduction.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from mcp_servers import FoodProductionMCPServer
from agents import WasteReductionAgent

# Initialize services
@st.cache_resource
def get_services():
    food_mcp = FoodProductionMCPServer()
    waste_agent = WasteReductionAgent()
    waste_agent.register_mcp_server("food_production", food_mcp)
    return food_mcp, waste_agent

food_mcp, waste_agent = get_services()

# Page header
st.markdown("# 🍳 Food Production Management")
st.markdown("### AI-Powered Production Planning & Waste Reduction")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "📦 Inventory", "🗓️ Prep Schedule", "♻️ Waste Reduction"])

with tab1:
    st.markdown("## Production Dashboard")
    
    # Date selector
    col1, col2 = st.columns([2, 1])
    with col1:
        forecast_date = st.date_input(
            "Forecast Date",
            value=(datetime.now() + timedelta(days=1)).date()
        )
    with col2:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
    
    # Get demand forecast
    with st.spinner("Loading demand forecast..."):
        forecast_result = food_mcp.call_endpoint(
            "get_demand_forecast",
            {"target_date": forecast_date.isoformat()}
        )
        
        if forecast_result.get("success"):
            forecast_data = forecast_result["data"]
            
            # Display key metrics
            st.markdown("### 📈 Demand Forecast")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Meals",
                    forecast_data.get("total_meals_forecasted", 0),
                    f"{forecast_data.get('confidence_level', 0) * 100:.0f}% confidence"
                )
            
            with col2:
                meal_breakdown = forecast_data.get("meal_breakdown", {})
                st.metric("Breakfast", meal_breakdown.get("breakfast", 0))
            
            with col3:
                st.metric("Lunch", meal_breakdown.get("lunch", 0))
            
            with col4:
                st.metric("Dinner", meal_breakdown.get("dinner", 0))
            
            # Meal type breakdown chart
            st.markdown("### 🍽️ Meal Type Distribution")
            meal_df = pd.DataFrame([
                {"Meal Type": k.title(), "Quantity": v}
                for k, v in meal_breakdown.items()
            ])
            st.bar_chart(meal_df.set_index("Meal Type"))
            
            # Item-specific forecast
            st.markdown("### 📋 Top Items by Demand")
            items_forecast = forecast_data.get("items_forecast", [])
            if items_forecast:
                items_df = pd.DataFrame(items_forecast)
                st.dataframe(
                    items_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "item_id": "Item",
                        "forecasted_quantity": st.column_config.NumberColumn("Quantity", format="%d"),
                        "confidence": st.column_config.ProgressColumn("Confidence", format="%.0f%%", min_value=0, max_value=100)
                    }
                )
        else:
            st.error("Failed to load demand forecast")
    
    st.markdown("---")
    
    # Equipment availability
    st.markdown("### 🔧 Equipment Status")
    equipment_result = food_mcp.call_endpoint("get_equipment_availability", {})
    
    if equipment_result.get("success"):
        equipment_data = equipment_result["data"]
        equipment_list = equipment_data.get("equipment", [])
        
        # Display equipment in columns
        cols = st.columns(3)
        for idx, equipment in enumerate(equipment_list):
            with cols[idx % 3]:
                status_icon = "✅" if equipment["available"] else "❌"
                maintenance = "🔧 In Maintenance" if equipment.get("in_maintenance") else ""
                
                st.markdown(f"""
                    <div class="metric-card">
                        <h4>{status_icon} {equipment['equipment_id']}</h4>
                        <p><strong>{equipment['type'].replace('_', ' ').title()}</strong></p>
                        <p>Status: {equipment['status'].upper()}</p>
                        {f'<p style="color: orange;">{maintenance}</p>' if maintenance else ''}
                    </div>
                """, unsafe_allow_html=True)

with tab2:
    st.markdown("## 📦 Inventory Management")
    
    # Get inventory status
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### Current Inventory")
    with col2:
        if st.button("🔄 Refresh Inventory", use_container_width=True):
            st.rerun()
    
    with st.spinner("Loading inventory data..."):
        inventory_result = food_mcp.call_endpoint("get_inventory_status", {})
        
        if inventory_result.get("success"):
            inventory_data = inventory_result["data"]
            items = inventory_data.get("items", [])
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Items", len(items))
            with col2:
                low_stock = sum(1 for item in items if item.get("stock_status") == "low")
                st.metric("Low Stock", low_stock, delta=None if low_stock == 0 else -low_stock, delta_color="inverse")
            with col3:
                expiring_soon = sum(1 for item in items if item.get("expiring_soon"))
                st.metric("Expiring Soon", expiring_soon, delta=None if expiring_soon == 0 else -expiring_soon, delta_color="inverse")
            with col4:
                st.metric("Last Updated", inventory_data.get("last_updated", "N/A")[:10])
            
            st.markdown("---")
            
            # Filters
            col1, col2 = st.columns(2)
            with col1:
                stock_filter = st.multiselect(
                    "Filter by Stock Status",
                    ["low", "medium", "high"],
                    default=["low", "medium", "high"]
                )
            with col2:
                expiring_filter = st.checkbox("Show only items expiring soon", value=False)
            
            # Filter items
            filtered_items = [
                item for item in items
                if item.get("stock_status") in stock_filter
                and (not expiring_filter or item.get("expiring_soon"))
            ]
            
            # Create DataFrame
            if filtered_items:
                inventory_df = pd.DataFrame(filtered_items)
                
                # Format DataFrame
                st.dataframe(
                    inventory_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "item_id": "Item ID",
                        "name": "Item Name",
                        "current_quantity": st.column_config.NumberColumn("Quantity", format="%d"),
                        "unit": "Unit",
                        "stock_status": st.column_config.TextColumn("Stock Status"),
                        "expiration_date": "Expires",
                        "expiring_soon": st.column_config.CheckboxColumn("⚠️ Expiring")
                    }
                )
                
                # Highlight critical items
                critical_items = [item for item in filtered_items if item.get("stock_status") == "low" or item.get("expiring_soon")]
                if critical_items:
                    st.markdown("### ⚠️ Items Requiring Attention")
                    for item in critical_items:
                        reason = []
                        if item.get("stock_status") == "low":
                            reason.append("Low Stock")
                        if item.get("expiring_soon"):
                            reason.append(f"Expires {item.get('expiration_date')}")
                        
                        st.warning(f"**{item['name']}**: {' | '.join(reason)}")
            else:
                st.info("No items match the selected filters")
        else:
            st.error("Failed to load inventory data")

with tab3:
    st.markdown("## 🗓️ Prep Schedule")
    
    # Date and meal type selection
    col1, col2 = st.columns(2)
    with col1:
        prep_date = st.date_input(
            "Prep Date",
            value=(datetime.now() + timedelta(days=1)).date(),
            key="prep_date"
        )
    with col2:
        prep_meal_type = st.selectbox(
            "Meal Type",
            ["breakfast", "lunch", "dinner"],
            index=1,
            key="prep_meal_type"
        )
    
    # Equipment constraints
    with st.expander("⚙️ Equipment Constraints (Optional)"):
        st.multiselect(
            "Unavailable Equipment",
            ["oven_1", "oven_2", "stove_1", "stove_2", "mixer_1"],
            default=[],
            key="unavailable_equipment"
        )
    
    # Generate schedule
    if st.button("📅 Generate Prep Schedule", type="primary", use_container_width=True):
        with st.spinner("🤖 AI generating optimal prep schedule..."):
            schedule_result = food_mcp.call_endpoint(
                "create_prep_schedule",
                {
                    "target_date": prep_date.isoformat(),
                    "meal_type": prep_meal_type,
                    "constraints": {"unavailable_equipment": st.session_state.get("unavailable_equipment", [])}
                }
            )
            
            if schedule_result.get("success"):
                schedule_data = schedule_result["data"]
                
                st.success(f"✅ Schedule created: {schedule_data.get('schedule_id')}")
                
                # Summary
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Tasks", schedule_data.get("total_tasks", 0))
                with col2:
                    st.metric("Est. Time", f"{schedule_data.get('estimated_total_time_minutes', 0)} min")
                with col3:
                    st.metric("Staff Needed", schedule_data.get("staff_required", 0))
                
                st.markdown("---")
                
                # Display tasks
                st.markdown("### 📋 Prep Tasks Timeline")
                tasks = schedule_data.get("tasks", [])
                
                for task in tasks:
                    with st.container():
                        col1, col2, col3, col4 = st.columns([1, 3, 2, 1])
                        
                        with col1:
                            st.markdown(f"**{task['start_time']}**")
                        
                        with col2:
                            st.markdown(f"**{task['task']}**")
                            st.caption(f"Item: {task['item_id']}")
                        
                        with col3:
                            st.markdown(f"⏱️ {task['duration_minutes']} min")
                            if task.get('equipment_needed'):
                                st.caption(f"🔧 {', '.join(task['equipment_needed'])}")
                        
                        with col4:
                            if task.get('priority') == 'high':
                                st.markdown("🔴 **HIGH**")
                            elif task.get('priority') == 'medium':
                                st.markdown("🟡 Medium")
                            else:
                                st.markdown("🟢 Low")
                        
                        st.markdown("---")
                
                # Download schedule
                if st.button("📥 Export Schedule to CSV"):
                    tasks_df = pd.DataFrame(tasks)
                    csv = tasks_df.to_csv(index=False)
                    st.download_button(
                        "Download CSV",
                        csv,
                        f"prep_schedule_{prep_date}_{prep_meal_type}.csv",
                        "text/csv"
                    )
            else:
                st.error("Failed to generate prep schedule")

with tab4:
    st.markdown("## ♻️ Waste Reduction")
    st.markdown("AI-powered waste identification and action recommendations")
    
    # Run waste analysis
    if st.button("🤖 Run Waste Analysis", type="primary", use_container_width=True):
        with st.spinner("AI Agent analyzing inventory for waste risks..."):
            async def analyze_waste():
                return await waste_agent.process({
                    "analysis_type": "full",
                    "days_ahead": 3
                })
            
            waste_result = asyncio.run(analyze_waste())
            st.session_state["waste_analysis"] = waste_result
            
            if waste_result.get("success"):
                st.success("✅ Waste analysis completed")
                
                # Display summary
                summary = waste_result.get("summary", {})
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Items at Risk",
                        summary.get("items_at_risk", 0),
                        delta=None if summary.get("items_at_risk", 0) == 0 else -summary.get("items_at_risk", 0),
                        delta_color="inverse"
                    )
                
                with col2:
                    st.metric(
                        "Potential Waste",
                        f"{summary.get('potential_waste_value', 0):.0f}",
                        delta_color="inverse"
                    )
                
                with col3:
                    st.metric(
                        "Action Items",
                        summary.get("total_actions", 0)
                    )
                
                with col4:
                    risk_level = summary.get("risk_level", "low")
                    risk_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(risk_level, "")
                    st.metric("Risk Level", f"{risk_icon} {risk_level.upper()}")
            else:
                st.error("Failed to run waste analysis")
    
    # Display waste analysis results
    if "waste_analysis" in st.session_state:
        waste_result = st.session_state["waste_analysis"]
        
        st.markdown("---")
        st.markdown("### 📊 Waste Risk Items")
        
        waste_items = waste_result.get("waste_items", [])
        if waste_items:
            for item in waste_items:
                with st.expander(f"⚠️ {item['name']} - {item['risk_category'].upper()} Risk", expanded=True):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Item ID:** {item['item_id']}")
                        st.markdown(f"**Quantity:** {item['quantity']} {item.get('unit', '')}")
                        st.markdown(f"**Expires:** {item['expiration_date']}")
                    
                    with col2:
                        st.markdown(f"**Risk Category:** {item['risk_category'].upper()}")
                        reasons = item.get('reasons', [])
                        if reasons:
                            st.markdown("**Reasons:**")
                            for reason in reasons:
                                st.markdown(f"- {reason}")
        else:
            st.info("✅ No items at significant waste risk")
        
        # Display actions
        st.markdown("---")
        st.markdown("### 💡 Recommended Actions")
        
        actions = waste_result.get("actions", [])
        if actions:
            # Group actions by category
            action_categories = {}
            for action in actions:
                category = action.get("category", "other")
                if category not in action_categories:
                    action_categories[category] = []
                action_categories[category].append(action)
            
            # Display by category
            for category, category_actions in action_categories.items():
                st.markdown(f"#### {category.replace('_', ' ').title()}")
                
                for action in category_actions:
                    priority_colors = {
                        "high": "🔴",
                        "medium": "🟡",
                        "low": "🟢"
                    }
                    priority_icon = priority_colors.get(action.get("priority", "low"), "")
                    
                    with st.container():
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            st.markdown(f"{priority_icon} **{action['action']}**")
                            st.caption(action.get('description', ''))
                        
                        with col2:
                            impact = action.get('estimated_impact', {})
                            if impact.get('waste_reduced_units'):
                                st.markdown(f"💰 Save {impact['waste_reduced_units']} units")
                        
                        with col3:
                            if st.button("✅ Done", key=f"action_{action.get('action_id', '')}"):
                                st.success("Action marked as complete")
                        
                        st.markdown("---")
        else:
            st.info("No actions needed at this time")
        
        # Export report
        if st.button("📥 Export Waste Report"):
            report_df = pd.DataFrame(waste_items)
            csv = report_df.to_csv(index=False)
            st.download_button(
                "Download CSV",
                csv,
                f"waste_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv"
            )

# Help section
with st.expander("❓ Help & Instructions"):
    st.markdown("""
    ### Food Production Management Guide
    
    **Dashboard Tab:**
    - View demand forecasts for upcoming meals
    - Monitor equipment availability
    - Track meal type distribution
    
    **Inventory Tab:**
    - Check current stock levels
    - Identify items expiring soon
    - Filter items by stock status
    - Monitor critical inventory items
    
    **Prep Schedule Tab:**
    - Generate optimized prep schedules
    - Account for equipment constraints
    - View task timelines and priorities
    - Export schedules to CSV
    
    **Waste Reduction Tab:**
    - Run AI-powered waste analysis
    - Identify items at risk
    - Get actionable recommendations
    - Track waste reduction impact
    
    **AI Features:**
    - Demand forecasting based on historical data
    - Automated prep scheduling optimization
    - Intelligent waste risk identification
    - Prioritized action recommendations
    """)
