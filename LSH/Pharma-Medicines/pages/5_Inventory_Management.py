"""
Inventory Management Page
Material inventory, stock alerts, purchase orders, and demand forecasting
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from database.astra_helper import AstraDBHelper
from mcp_servers.inventory_mcp import InventoryMCPServer

# Page configuration
st.set_page_config(
    page_title="Inventory Management",
    page_icon="📦",
    layout="wide"
)

# Initialize
if 'db_helper' not in st.session_state:
    st.session_state.db_helper = AstraDBHelper()
if 'inventory_mcp' not in st.session_state:
    st.session_state.inventory_mcp = InventoryMCPServer()

# Header
st.title("📦 Inventory Management")
st.markdown("Raw materials, purchase orders, and AI-powered demand forecasting")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📦 Material Inventory", "⚠️ Low Stock Alerts", "🛒 Purchase Orders", "📅 Expiring Materials", "📈 Demand Forecast"])

with tab1:
    st.markdown("### Raw Material Inventory")
    
    # Inventory statistics
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        materials = list(st.session_state.db_helper.raw_materials.find({}, limit=500))
        
        total_materials = len(materials)
        api_materials = sum(1 for m in materials if m.get("type") == "API")
        excipient_materials = sum(1 for m in materials if m.get("type") == "excipient")
        low_stock = sum(1 for m in materials if m.get("quantity_in_stock", 0) <= m.get("reorder_point", 0))
        
        with col1:
            st.metric("Total Materials", total_materials)
        with col2:
            st.metric("APIs", api_materials)
        with col3:
            st.metric("Excipients", excipient_materials)
        with col4:
            st.metric("Low Stock", low_stock, delta_color="inverse")
        
        st.markdown("---")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            type_filter = st.selectbox("Material Type", ["All", "API", "excipient"])
        with col2:
            supplier_filter = st.text_input("Supplier ID", placeholder="e.g., SUP-001")
        with col3:
            status_filter = st.selectbox("Status", ["All", "available", "low_stock", "out_of_stock"])
        
        # Get inventory with analysis
        result = st.session_state.inventory_mcp.call_endpoint("get_material_inventory", {})
        
        if result.get("status") == "success":
            inventory = result.get("data", [])
            
            # Apply filters
            if type_filter != "All":
                inventory = [i for i in inventory if i.get("type") == type_filter]
            if supplier_filter:
                inventory = [i for i in inventory if i.get("supplier_id") == supplier_filter]
            if status_filter != "All":
                inventory = [i for i in inventory if i.get("stock_status") == status_filter]
            
            if inventory:
                st.success(f"Found {len(inventory)} materials")
                
                # Create DataFrame
                df = pd.DataFrame([{
                    "Material ID": m.get("material_id", "N/A"),
                    "Name": m.get("name", "N/A"),
                    "Type": m.get("type", "N/A"),
                    "Supplier": m.get("supplier_id", "N/A"),
                    "Stock": f"{m.get('quantity_in_stock', 0):,.0f} {m.get('unit', '')}",
                    "Reorder Point": f"{m.get('reorder_point', 0):,.0f}",
                    "Status": m.get("stock_status", "N/A"),
                    "Reorder Needed": "✅ Yes" if m.get("reorder_recommended") else "❌ No",
                    "Expiry Date": m.get("expiry_date", "N/A")[:10]
                } for m in inventory])
                
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # Material details
                st.markdown("---")
                st.markdown("### Material Details")
                
                selected_material = st.selectbox(
                    "Select Material",
                    options=[m.get("material_id") for m in inventory],
                    format_func=lambda x: next((m.get("name") for m in inventory if m.get("material_id") == x), x)
                )
                
                if selected_material:
                    material = next((m for m in inventory if m.get("material_id") == selected_material), None)
                    
                    if material:
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown("**Material Information**")
                            st.write(f"**ID:** {material.get('material_id', 'N/A')}")
                            st.write(f"**Name:** {material.get('name', 'N/A')}")
                            st.write(f"**Type:** {material.get('type', 'N/A')}")
                            st.write(f"**Batch:** {material.get('batch_number', 'N/A')}")
                        
                        with col2:
                            st.markdown("**Inventory Status**")
                            st.write(f"**Stock:** {material.get('quantity_in_stock', 0):,.0f} {material.get('unit', '')}")
                            st.write(f"**Reorder Point:** {material.get('reorder_point', 0):,.0f}")
                            
                            status = material.get("stock_status", "unknown")
                            if status == "low_stock":
                                st.warning(f"**Status:** ⚠️ {status.upper()}")
                            elif status == "out_of_stock":
                                st.error(f"**Status:** 🔴 {status.upper()}")
                            else:
                                st.success(f"**Status:** ✅ {status.upper()}")
                            
                            if material.get("reorder_recommended"):
                                st.error("⚠️ Reorder Recommended")
                        
                        with col3:
                            st.markdown("**Storage & Expiry**")
                            st.write(f"**Location:** {material.get('storage_location', 'N/A')}")
                            st.write(f"**Supplier:** {material.get('supplier_id', 'N/A')}")
                            st.write(f"**Expiry:** {material.get('expiry_date', 'N/A')[:10]}")
                            st.write(f"**Last Updated:** {material.get('last_updated', 'N/A')[:10]}")
            else:
                st.info("No materials found matching the criteria")
        else:
            st.error(f"Error: {result.get('message')}")
    
    except Exception as e:
        st.error(f"Error loading inventory: {str(e)}")

with tab2:
    st.markdown("### 🚨 Low Stock Alerts")
    st.info("🤖 AI-powered stock analysis with demand forecasting")
    
    try:
        result = st.session_state.inventory_mcp.call_endpoint("check_low_stock_items", {})
        
        if result.get("status") == "success":
            low_stock = result.get("data", [])
            
            if low_stock:
                st.warning(f"⚠️ {len(low_stock)} materials below reorder point")
                
                # Create DataFrame
                df = pd.DataFrame([{
                    "Material ID": m.get("material_id", "N/A"),
                    "Name": m.get("name", "N/A"),
                    "Type": m.get("type", "N/A"),
                    "Current Stock": f"{m.get('quantity_in_stock', 0):,.0f} {m.get('unit', '')}",
                    "Reorder Point": f"{m.get('reorder_point', 0):,.0f}",
                    "Shortage": f"{m.get('shortage_quantity', 0):,.0f}",
                    "Forecast Demand (30d)": f"{m.get('forecasted_demand_30days', 0):,.0f}",
                    "Urgency": m.get("urgency", "N/A")
                } for m in low_stock])
                
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # Urgency distribution
                st.markdown("---")
                st.markdown("### Urgency Level Distribution")
                
                urgency_counts = {}
                for item in low_stock:
                    urgency = item.get("urgency", "unknown")
                    urgency_counts[urgency] = urgency_counts.get(urgency, 0) + 1
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Critical", urgency_counts.get("critical", 0))
                with col2:
                    st.metric("High", urgency_counts.get("high", 0))
                with col3:
                    st.metric("Medium", urgency_counts.get("medium", 0))
                
                # Quick reorder
                st.markdown("---")
                st.markdown("### 🛒 Quick Reorder")
                
                selected_material = st.selectbox(
                    "Select Material to Reorder",
                    options=[m.get("material_id") for m in low_stock],
                    format_func=lambda x: next((m.get("name") for m in low_stock if m.get("material_id") == x), x)
                )
                
                material = next((m for m in low_stock if m.get("material_id") == selected_material), None)
                if material:
                    suggested_qty = material.get("recommended_order_quantity", 0)
                    st.info(f"💡 AI Recommendation: Order {suggested_qty:,.0f} {material.get('unit', '')} based on demand forecast")
            else:
                st.success("✅ All materials are adequately stocked")
        else:
            st.error(f"Error: {result.get('message')}")
    
    except Exception as e:
        st.error(f"Error checking low stock: {str(e)}")

with tab3:
    st.markdown("### Purchase Orders Management")
    
    # PO statistics
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        pos = list(st.session_state.db_helper.purchase_orders.find({}, limit=500))
        
        total_pos = len(pos)
        pending_pos = sum(1 for po in pos if po.get("status") == "pending")
        confirmed_pos = sum(1 for po in pos if po.get("status") == "confirmed")
        delivered_pos = sum(1 for po in pos if po.get("status") == "delivered")
        
        with col1:
            st.metric("Total POs", total_pos)
        with col2:
            st.metric("Pending", pending_pos)
        with col3:
            st.metric("Confirmed", confirmed_pos)
        with col4:
            st.metric("Delivered", delivered_pos)
        
        st.markdown("---")
        
        # Create new PO
        st.markdown("### ➕ Create Purchase Order")
        st.info("🤖 AI-powered supplier selection based on performance analysis")
        
        with st.form("create_po_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                po_id = st.text_input("PO ID*", placeholder="PO-YYYY-XXX")
                
                # Get suppliers
                suppliers = list(st.session_state.db_helper.suppliers.find({"status": "active"}, limit=100))
                supplier_options = {s.get("supplier_id"): s.get("name") for s in suppliers}
                
                supplier_id = st.selectbox(
                    "Supplier*",
                    options=list(supplier_options.keys()),
                    format_func=lambda x: f"{x} - {supplier_options.get(x, 'N/A')}"
                )
                
                # Get materials
                materials = list(st.session_state.db_helper.raw_materials.find({}, limit=500))
                material_options = {m.get("material_id"): m.get("name") for m in materials}
                
                material_id = st.selectbox(
                    "Material*",
                    options=list(material_options.keys()),
                    format_func=lambda x: f"{x} - {material_options.get(x, 'N/A')}"
                )
            
            with col2:
                quantity = st.number_input("Quantity*", min_value=1, max_value=100000, value=1000, step=100)
                unit_price = st.number_input("Unit Price (USD)*", min_value=0.01, max_value=10000.0, value=100.0, step=0.01)
                
                order_date = st.date_input("Order Date*", value=datetime.now())
                expected_delivery = st.date_input("Expected Delivery*", value=datetime.now() + timedelta(days=14))
            
            submitted = st.form_submit_button("🛒 Create PO (AI Analysis)", use_container_width=True)
            
            if submitted:
                if not all([po_id, supplier_id, material_id, quantity, unit_price]):
                    st.error("Please fill in all required fields marked with *")
                else:
                    try:
                        with st.spinner("Creating purchase order with supplier analysis..."):
                            result = st.session_state.inventory_mcp.call_endpoint(
                                "create_purchase_order",
                                {
                                    "po_id": po_id,
                                    "supplier_id": supplier_id,
                                    "material_id": material_id,
                                    "quantity": quantity,
                                    "unit_price": unit_price,
                                    "order_date": order_date.isoformat(),
                                    "expected_delivery_date": expected_delivery.isoformat()
                                }
                            )
                            
                            if result.get("status") == "success":
                                data = result.get("data", {})
                                supplier_analysis = data.get("supplier_analysis", {})
                                
                                st.success(f"✅ Purchase Order {po_id} created successfully!")
                                
                                # Show supplier analysis
                                if supplier_analysis:
                                    st.markdown("### 🤖 Supplier Analysis")
                                    
                                    col1, col2, col3 = st.columns(3)
                                    
                                    with col1:
                                        score = supplier_analysis.get("performance_score", 0)
                                        st.metric("Performance Score", f"{score:.1f}/100")
                                    
                                    with col2:
                                        st.write(f"**On-Time Delivery:** {supplier_analysis.get('on_time_delivery_rate', 0):.1f}%")
                                        st.write(f"**Quality Score:** {supplier_analysis.get('quality_score', 0):.1f}/100")
                                    
                                    with col3:
                                        st.write(f"**Total POs:** {supplier_analysis.get('total_orders', 0)}")
                                        st.write(f"**Recommendation:** {supplier_analysis.get('recommendation', 'N/A')}")
                                
                                st.balloons()
                            else:
                                st.error(f"Error: {result.get('message')}")
                    except Exception as e:
                        st.error(f"Error creating PO: {str(e)}")
        
        # Existing POs
        st.markdown("---")
        st.markdown("### 📋 Purchase Orders")
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.selectbox("Status", ["All", "pending", "confirmed", "shipped", "delivered"])
        with col2:
            supplier_filter = st.selectbox("Supplier", ["All"] + list(supplier_options.values()))
        
        # Apply filters
        filtered_pos = pos
        if status_filter != "All":
            filtered_pos = [po for po in filtered_pos if po.get("status") == status_filter]
        if supplier_filter != "All":
            supplier_id_filter = next((k for k, v in supplier_options.items() if v == supplier_filter), None)
            if supplier_id_filter:
                filtered_pos = [po for po in filtered_pos if po.get("supplier_id") == supplier_id_filter]
        
        if filtered_pos:
            po_df = pd.DataFrame([{
                "PO ID": po.get("po_id", "N/A"),
                "Supplier": po.get("supplier_id", "N/A"),
                "Order Date": po.get("order_date", "N/A")[:10],
                "Expected Delivery": po.get("expected_delivery_date", "N/A")[:10],
                "Total Amount": f"${po.get('total_amount', 0):,.2f}",
                "Status": po.get("status", "N/A")
            } for po in filtered_pos])
            
            st.dataframe(po_df, use_container_width=True, hide_index=True)
        else:
            st.info("No purchase orders found matching the criteria")
    
    except Exception as e:
        st.error(f"Error loading purchase orders: {str(e)}")

with tab4:
    st.markdown("### 📅 Expiring Materials")
    
    # Days filter
    days_ahead = st.slider("Show materials expiring within (days)", 30, 365, 90)
    
    try:
        result = st.session_state.inventory_mcp.call_endpoint(
            "get_expiring_materials",
            {"days": days_ahead}
        )
        
        if result.get("status") == "success":
            expiring = result.get("data", [])
            
            if expiring:
                st.warning(f"⚠️ {len(expiring)} materials expiring in the next {days_ahead} days")
                
                # Create DataFrame
                df = pd.DataFrame([{
                    "Material ID": m.get("material_id", "N/A"),
                    "Name": m.get("name", "N/A"),
                    "Type": m.get("type", "N/A"),
                    "Batch": m.get("batch_number", "N/A"),
                    "Stock": f"{m.get('quantity_in_stock', 0):,.0f} {m.get('unit', '')}",
                    "Expiry Date": m.get("expiry_date", "N/A")[:10],
                    "Days Until Expiry": m.get("days_until_expiry", 0),
                    "Urgency": m.get("urgency", "N/A")
                } for m in expiring])
                
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # Expiry timeline
                st.markdown("---")
                st.markdown("### Expiry Timeline")
                
                # Group by urgency
                urgency_counts = {}
                for item in expiring:
                    urgency = item.get("urgency", "unknown")
                    urgency_counts[urgency] = urgency_counts.get(urgency, 0) + 1
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Critical (<30d)", urgency_counts.get("critical", 0), delta_color="inverse")
                with col2:
                    st.metric("High (30-60d)", urgency_counts.get("high", 0))
                with col3:
                    st.metric("Medium (60-90d)", urgency_counts.get("medium", 0))
                
                # Chart
                fig = px.bar(
                    df,
                    x="Name",
                    y="Days Until Expiry",
                    color="Urgency",
                    title="Materials by Days Until Expiry",
                    color_discrete_map={"critical": "#ef4444", "high": "#f59e0b", "medium": "#3b82f6"}
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.success(f"✅ No materials expiring in the next {days_ahead} days")
        else:
            st.error(f"Error: {result.get('message')}")
    
    except Exception as e:
        st.error(f"Error loading expiring materials: {str(e)}")

with tab5:
    st.markdown("### 📈 AI-Powered Demand Forecasting")
    st.info("🤖 Machine learning-based material demand prediction")
    
    # Get materials for forecasting
    materials = list(st.session_state.db_helper.raw_materials.find({}, limit=500))
    
    if materials:
        material_options = {m.get("material_id"): m.get("name") for m in materials}
        
        selected_material = st.selectbox(
            "Select Material for Forecast",
            options=list(material_options.keys()),
            format_func=lambda x: material_options.get(x, x)
        )
        
        forecast_days = st.slider("Forecast Period (days)", 7, 90, 30)
        
        if st.button("📈 Generate Forecast", use_container_width=True):
            with st.spinner("Running AI demand forecasting model..."):
                try:
                    result = st.session_state.inventory_mcp.call_endpoint(
                        "forecast_material_demand",
                        {
                            "material_id": selected_material,
                            "days_ahead": forecast_days
                        }
                    )
                    
                    if result.get("status") == "success":
                        forecast = result.get("data", {})
                        
                        st.success("✅ Forecast generated successfully")
                        
                        # Key metrics
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric(
                                "Total Forecast Demand",
                                f"{forecast.get('total_forecast_demand', 0):,.0f}",
                                delta=f"{forecast.get('trend', 'N/A')}"
                            )
                        
                        with col2:
                            st.metric("Avg Daily Demand", f"{forecast.get('average_daily_demand', 0):,.1f}")
                        
                        with col3:
                            st.metric("Current Stock", f"{forecast.get('current_stock', 0):,.0f}")
                        
                        with col4:
                            shortage_days = forecast.get("shortage_in_days", 999)
                            if shortage_days < 999:
                                st.metric("Shortage In", f"{shortage_days} days", delta_color="inverse")
                            else:
                                st.metric("Shortage In", "No shortage")
                        
                        # Forecast chart
                        st.markdown("---")
                        st.markdown("### Demand Forecast Visualization")
                        
                        if forecast.get("daily_forecast"):
                            daily_data = forecast.get("daily_forecast", [])
                            
                            fig = go.Figure()
                            
                            # Add forecast line
                            fig.add_trace(go.Scatter(
                                x=[d.get("date") for d in daily_data],
                                y=[d.get("forecast_demand") for d in daily_data],
                                mode='lines+markers',
                                name='Forecast Demand',
                                line=dict(color='#3b82f6', width=2)
                            ))
                            
                            # Add stock level line
                            current_stock = forecast.get("current_stock", 0)
                            fig.add_hline(
                                y=current_stock,
                                line_dash="dash",
                                line_color="green",
                                annotation_text=f"Current Stock: {current_stock:,.0f}"
                            )
                            
                            # Add reorder point
                            reorder_point = forecast.get("reorder_point", 0)
                            fig.add_hline(
                                y=reorder_point,
                                line_dash="dash",
                                line_color="red",
                                annotation_text=f"Reorder Point: {reorder_point:,.0f}"
                            )
                            
                            fig.update_layout(
                                title=f"Demand Forecast for {material_options.get(selected_material)}",
                                xaxis_title="Date",
                                yaxis_title="Quantity",
                                height=400
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # Recommendations
                        st.markdown("---")
                        st.markdown("### 🤖 AI Recommendations")
                        
                        if forecast.get("reorder_recommended"):
                            st.error(f"⚠️ **Reorder Recommended:** Order {forecast.get('recommended_order_quantity', 0):,.0f} units")
                        else:
                            st.success("✅ Current stock is sufficient for the forecast period")
                        
                        if forecast.get("recommendations"):
                            for rec in forecast.get("recommendations", []):
                                st.info(f"• {rec}")
                    else:
                        st.error(f"Error: {result.get('message')}")
                except Exception as e:
                    st.error(f"Error generating forecast: {str(e)}")
    else:
        st.info("No materials available for forecasting")

# Footer
st.markdown("---")
st.markdown("📦 Inventory Management | [Back to Dashboard](../app.py)")
