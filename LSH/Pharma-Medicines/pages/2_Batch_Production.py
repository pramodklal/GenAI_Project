"""
Batch Production Page
Create, track, and manage manufacturing batches
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
from mcp_servers.production_mcp import ProductionMCPServer

# Page configuration
st.set_page_config(
    page_title="Batch Production",
    page_icon="🏭",
    layout="wide"
)

# Initialize
if 'db_helper' not in st.session_state:
    st.session_state.db_helper = AstraDBHelper()
if 'production_mcp' not in st.session_state:
    st.session_state.production_mcp = ProductionMCPServer()

# Header
st.title("🏭 Batch Production Management")
st.markdown("Create, monitor, and manage pharmaceutical manufacturing batches")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📋 Active Batches", "➕ Create Batch", "📊 Production Schedule", "📈 Batch Analytics"])

with tab1:
    st.markdown("### Active Manufacturing Batches")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox(
            "Status",
            ["All", "in_production", "in_qc", "approved", "rejected"]
        )
    with col2:
        medicine_filter = st.text_input("Medicine ID", placeholder="e.g., MED-001")
    with col3:
        sort_by = st.selectbox("Sort By", ["Manufacturing Date", "Batch Number", "Status"])
    
    try:
        # Build query
        query = {}
        if status_filter != "All":
            query["status"] = status_filter
        if medicine_filter:
            query["medicine_id"] = medicine_filter
        
        # Fetch batches
        batches = list(st.session_state.db_helper.manufacturing_batches.find(query, limit=100))
        
        if batches:
            st.success(f"Found {len(batches)} batches")
            
            # Create DataFrame
            df = pd.DataFrame([{
                "Batch ID": b.get("batch_id", "N/A"),
                "Batch Number": b.get("batch_number", "N/A"),
                "Medicine ID": b.get("medicine_id", "N/A"),
                "Quantity": f"{b.get('quantity', 0):,}",
                "Manufacturing Date": b.get("manufacturing_date", "N/A")[:10],
                "Current Stage": b.get("current_stage", "N/A"),
                "Status": b.get("status", "N/A"),
                "Yield %": f"{b.get('yield_percentage', 0):.1f}%",
                "GMP": "✅" if b.get("gmp_certified") else "❌"
            } for b in batches])
            
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Batch details
            st.markdown("---")
            st.markdown("### Batch Details & Actions")
            
            selected_batch = st.selectbox(
                "Select Batch",
                options=[b.get("batch_id") for b in batches],
                format_func=lambda x: next((b.get("batch_number") for b in batches if b.get("batch_id") == x), x)
            )
            
            if selected_batch:
                result = st.session_state.production_mcp.call_endpoint(
                    "get_batch_status",
                    {"batch_id": selected_batch}
                )
                
                if result.get("status") == "success":
                    batch = result.get("data", {})
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown("**Batch Information**")
                        st.write(f"**Batch ID:** {batch.get('batch_id', 'N/A')}")
                        st.write(f"**Batch Number:** {batch.get('batch_number', 'N/A')}")
                        st.write(f"**Medicine:** {batch.get('medicine_id', 'N/A')}")
                        st.write(f"**Quantity:** {batch.get('quantity', 0):,} units")
                        st.write(f"**Yield:** {batch.get('yield_percentage', 0):.1f}%")
                    
                    with col2:
                        st.markdown("**Production Status**")
                        st.write(f"**Current Stage:** {batch.get('current_stage', 'N/A').upper()}")
                        st.write(f"**Status:** {batch.get('status', 'N/A').upper()}")
                        st.write(f"**GMP Certified:** {'✅ Yes' if batch.get('gmp_certified') else '❌ No'}")
                        st.write(f"**Manufacturing Date:** {batch.get('manufacturing_date', 'N/A')[:10]}")
                    
                    with col3:
                        st.markdown("**Approval Details**")
                        if batch.get("approved_by"):
                            st.write(f"**Approved By:** {batch.get('approved_by', 'N/A')}")
                            st.write(f"**Approval Date:** {batch.get('approved_date', 'N/A')[:10]}")
                        else:
                            st.write("**Status:** Pending Approval")
                        st.write(f"**Expiry Date:** {batch.get('expiry_date', 'N/A')[:10]}")
                    
                    # Stage update
                    st.markdown("---")
                    st.markdown("**Update Production Stage**")
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        new_stage = st.selectbox(
                            "New Stage",
                            ["mixing", "granulation", "drying", "compression", "coating", "packaging", "completed"],
                            key="stage_update"
                        )
                    with col2:
                        if st.button("🔄 Update Stage", use_container_width=True):
                            update_result = st.session_state.production_mcp.call_endpoint(
                                "update_batch_stage",
                                {
                                    "batch_id": selected_batch,
                                    "new_stage": new_stage
                                }
                            )
                            if update_result.get("status") == "success":
                                st.success(f"✅ Stage updated to {new_stage}")
                                st.rerun()
                            else:
                                st.error(f"Error: {update_result.get('message')}")
                else:
                    st.error(f"Error: {result.get('message')}")
        else:
            st.info("No batches found matching the criteria")
    
    except Exception as e:
        st.error(f"Error loading batches: {str(e)}")

with tab2:
    st.markdown("### Create New Manufacturing Batch")
    
    with st.form("create_batch_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            batch_id = st.text_input("Batch ID*", placeholder="BATCH-YYYY-XXX")
            batch_number = st.text_input("Batch Number*", placeholder="e.g., AMX-2025-001")
            
            # Get medicines for dropdown
            medicines = list(st.session_state.db_helper.medicines.find({"status": "active"}, limit=100))
            medicine_options = {m.get("medicine_id"): m.get("name") for m in medicines}
            
            medicine_id = st.selectbox(
                "Medicine*",
                options=list(medicine_options.keys()),
                format_func=lambda x: f"{x} - {medicine_options[x]}"
            )
            
            quantity = st.number_input("Quantity (units)*", min_value=1000, max_value=1000000, value=100000, step=1000)
        
        with col2:
            manufacturing_date = st.date_input("Manufacturing Date*", value=datetime.now())
            
            # Calculate expiry date based on medicine shelf life
            if medicine_id:
                selected_medicine = next((m for m in medicines if m.get("medicine_id") == medicine_id), None)
                if selected_medicine:
                    shelf_life = selected_medicine.get("shelf_life_months", 36)
                    default_expiry = manufacturing_date + timedelta(days=shelf_life * 30)
                    expiry_date = st.date_input("Expiry Date*", value=default_expiry)
            
            current_stage = st.selectbox(
                "Initial Stage*",
                ["mixing", "granulation", "drying", "compression", "coating", "packaging"]
            )
            
            gmp_certified = st.checkbox("GMP Certified", value=True)
        
        submitted = st.form_submit_button("🏭 Create Batch", use_container_width=True)
        
        if submitted:
            if not all([batch_id, batch_number, medicine_id, quantity]):
                st.error("Please fill in all required fields marked with *")
            else:
                try:
                    with st.spinner("Creating batch and validating materials..."):
                        result = st.session_state.production_mcp.call_endpoint(
                            "create_batch",
                            {
                                "batch_id": batch_id,
                                "batch_number": batch_number,
                                "medicine_id": medicine_id,
                                "quantity": quantity,
                                "manufacturing_date": manufacturing_date.isoformat(),
                                "expiry_date": expiry_date.isoformat(),
                                "current_stage": current_stage,
                                "gmp_certified": gmp_certified
                            }
                        )
                        
                        if result.get("status") == "success":
                            st.success(f"✅ Batch {batch_number} created successfully!")
                            
                            # Show material requirements
                            data = result.get("data", {})
                            if "material_check" in data:
                                st.info("📦 Material requirements calculated and validated")
                            
                            st.balloons()
                        else:
                            st.error(f"Error: {result.get('message')}")
                except Exception as e:
                    st.error(f"Error creating batch: {str(e)}")

with tab3:
    st.markdown("### Production Schedule")
    
    try:
        # Get optimized schedule
        col1, col2 = st.columns([3, 1])
        with col1:
            days_ahead = st.slider("Schedule Days Ahead", 1, 30, 7)
        with col2:
            if st.button("🔄 Refresh Schedule", use_container_width=True):
                st.rerun()
        
        result = st.session_state.production_mcp.call_endpoint(
            "get_production_schedule",
            {"days_ahead": days_ahead}
        )
        
        if result.get("status") == "success":
            schedule = result.get("data", [])
            
            if schedule:
                st.success(f"✅ {len(schedule)} scheduled operations")
                
                # Create timeline chart
                fig = go.Figure()
                
                for item in schedule:
                    batch_id = item.get("batch_id", "Unknown")
                    start = item.get("scheduled_start", "")
                    end = item.get("scheduled_end", "")
                    status = item.get("status", "unknown")
                    equipment = item.get("equipment_id", "N/A")
                    
                    color_map = {
                        "completed": "#10b981",
                        "in_progress": "#3b82f6",
                        "scheduled": "#f59e0b"
                    }
                    color = color_map.get(status, "#9ca3af")
                    
                    fig.add_trace(go.Scatter(
                        x=[start, end],
                        y=[f"{batch_id} ({equipment})", f"{batch_id} ({equipment})"],
                        mode='lines+markers',
                        name=batch_id,
                        line=dict(color=color, width=10),
                        marker=dict(size=12),
                        hovertemplate=f"<b>{batch_id}</b><br>Equipment: {equipment}<br>Status: {status}<br>Start: %{{x[0]}}<br>End: %{{x[1]}}<extra></extra>"
                    ))
                
                fig.update_layout(
                    title=f"Production Schedule (Next {days_ahead} Days)",
                    xaxis_title="Date/Time",
                    yaxis_title="Batch (Equipment)",
                    height=500,
                    showlegend=False,
                    hovermode='closest'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Table view
                st.markdown("---")
                st.markdown("### Schedule Details")
                
                df = pd.DataFrame([{
                    "Batch ID": s.get("batch_id", "N/A"),
                    "Equipment": s.get("equipment_id", "N/A"),
                    "Start": s.get("scheduled_start", "N/A")[:16].replace("T", " "),
                    "End": s.get("scheduled_end", "N/A")[:16].replace("T", " "),
                    "Status": s.get("status", "N/A"),
                    "Operator 1": s.get("operator_1", "N/A"),
                    "Operator 2": s.get("operator_2", "N/A")
                } for s in schedule])
                
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No scheduled operations found")
        else:
            st.error(f"Error: {result.get('message')}")
    
    except Exception as e:
        st.error(f"Error loading schedule: {str(e)}")

with tab4:
    st.markdown("### Batch Analytics")
    
    try:
        batches = list(st.session_state.db_helper.manufacturing_batches.find({}, limit=500))
        
        if batches:
            # Yield analysis
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Yield Distribution**")
                
                yields = [b.get("yield_percentage", 0) for b in batches if b.get("yield_percentage")]
                
                fig = px.histogram(
                    x=yields,
                    nbins=20,
                    labels={'x': 'Yield (%)', 'y': 'Count'},
                    title="Batch Yield Distribution"
                )
                fig.add_vline(x=95, line_dash="dash", line_color="red", annotation_text="Target: 95%")
                
                st.plotly_chart(fig, use_container_width=True)
                
                avg_yield = sum(yields) / len(yields) if yields else 0
                st.metric("Average Yield", f"{avg_yield:.1f}%", delta=f"{avg_yield - 95:.1f}%")
            
            with col2:
                st.markdown("**Status Distribution**")
                
                status_counts = {}
                for batch in batches:
                    status = batch.get("status", "unknown")
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                fig = px.pie(
                    names=list(status_counts.keys()),
                    values=list(status_counts.values()),
                    title="Batch Status Distribution",
                    hole=0.4
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Stage analysis
            st.markdown("---")
            st.markdown("**Current Stage Distribution**")
            
            stage_counts = {}
            for batch in batches:
                if batch.get("status") == "in_production":
                    stage = batch.get("current_stage", "unknown")
                    stage_counts[stage] = stage_counts.get(stage, 0) + 1
            
            if stage_counts:
                fig = px.bar(
                    x=list(stage_counts.keys()),
                    y=list(stage_counts.values()),
                    labels={'x': 'Production Stage', 'y': 'Number of Batches'},
                    title="Active Batches by Production Stage"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No batches currently in production")
        else:
            st.info("No batch data available for analytics")
    
    except Exception as e:
        st.error(f"Error generating analytics: {str(e)}")

# Footer
st.markdown("---")
st.markdown("🏭 Batch Production | [Back to Dashboard](../app.py)")
