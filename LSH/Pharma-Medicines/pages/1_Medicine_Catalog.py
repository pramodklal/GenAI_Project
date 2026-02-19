"""
Medicine Catalog Page
Browse medicines, search formulations, and view medicine details
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from database.astra_helper import AstraDBHelper
from mcp_servers.medicine_mcp import MedicineMCPServer

# Page configuration
st.set_page_config(
    page_title="Medicine Catalog",
    page_icon="💊",
    layout="wide"
)

# Initialize
if 'db_helper' not in st.session_state:
    st.session_state.db_helper = AstraDBHelper()
if 'medicine_mcp' not in st.session_state:
    st.session_state.medicine_mcp = MedicineMCPServer()

# Header
st.title("💊 Medicine Catalog")
st.markdown("Browse and manage pharmaceutical products")

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    
    search_query = st.text_input("🔍 Search by Name", placeholder="e.g., Amoxicillin")
    
    dosage_form = st.selectbox(
        "Dosage Form",
        ["All", "tablet", "capsule", "injection", "syrup", "cream"]
    )
    
    therapeutic_category = st.text_input("Therapeutic Category", placeholder="e.g., Antibiotics")
    
    status_filter = st.selectbox(
        "Status",
        ["All", "active", "inactive", "discontinued"]
    )
    
    fda_approved = st.checkbox("FDA Approved Only", value=False)
    ema_approved = st.checkbox("EMA Approved Only", value=False)

# Main content
tab1, tab2, tab3, tab4 = st.tabs(["📋 Browse Medicines", "🔬 Formulations", "➕ Add Medicine", "🔍 Vector Search"])

with tab1:
    st.markdown("### Active Medicines")
    
    try:
        # Fetch all medicines (no complex query filters)
        medicines = list(st.session_state.db_helper.medicines.find({}, limit=100))
        
        # Filter in Python
        if status_filter != "All":
            medicines = [m for m in medicines if m.get("status") == status_filter]
        if dosage_form != "All":
            medicines = [m for m in medicines if m.get("dosage_form") == dosage_form]
        if fda_approved:
            medicines = [m for m in medicines if m.get("fda_approved") == True]
        if ema_approved:
            medicines = [m for m in medicines if m.get("ema_approved") == True]
        if search_query:
            medicines = [m for m in medicines if search_query.lower() in m.get("name", "").lower()]
        if therapeutic_category:
            medicines = [m for m in medicines if therapeutic_category.lower() in m.get("therapeutic_category", "").lower()]
        
        if medicines:
            st.success(f"Found {len(medicines)} medicines")
            
            # Create DataFrame
            df = pd.DataFrame([{
                "Medicine ID": m.get("medicine_id", "N/A"),
                "Name": m.get("name", "N/A"),
                "Generic Name": m.get("generic_name", "N/A"),
                "Dosage Form": m.get("dosage_form", "N/A"),
                "Strength": m.get("strength", "N/A"),
                "Category": m.get("therapeutic_category", "N/A"),
                "FDA": "✅" if m.get("fda_approved") else "❌",
                "EMA": "✅" if m.get("ema_approved") else "❌",
                "Status": m.get("status", "N/A")
            } for m in medicines])
            
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Medicine details
            st.markdown("---")
            st.markdown("### Medicine Details")
            
            selected_medicine = st.selectbox(
                "Select Medicine for Details",
                options=[m.get("medicine_id") for m in medicines],
                format_func=lambda x: next((m.get("name") for m in medicines if m.get("medicine_id") == x), x)
            )
            
            if selected_medicine:
                result = st.session_state.medicine_mcp.call_endpoint(
                    "get_medicine_details",
                    {"medicine_id": selected_medicine}
                )
                
                if result.get("status") == "success":
                    medicine = result.get("data", {})
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown("**Basic Information**")
                        st.write(f"**Name:** {medicine.get('name', 'N/A')}")
                        st.write(f"**Generic:** {medicine.get('generic_name', 'N/A')}")
                        st.write(f"**Form:** {medicine.get('dosage_form', 'N/A')}")
                        st.write(f"**Strength:** {medicine.get('strength', 'N/A')}")
                    
                    with col2:
                        st.markdown("**Regulatory Status**")
                        st.write(f"**FDA Approved:** {'✅ Yes' if medicine.get('fda_approved') else '❌ No'}")
                        st.write(f"**EMA Approved:** {'✅ Yes' if medicine.get('ema_approved') else '❌ No'}")
                        st.write(f"**Approval Date:** {medicine.get('approval_date', 'N/A')[:10]}")
                        st.write(f"**Status:** {medicine.get('status', 'N/A').upper()}")
                    
                    with col3:
                        st.markdown("**Storage & Shelf Life**")
                        st.write(f"**Storage:** {medicine.get('storage_conditions', 'N/A')}")
                        st.write(f"**Shelf Life:** {medicine.get('shelf_life_months', 'N/A')} months")
                        st.write(f"**Stability Study:** {medicine.get('stability_study', 'N/A').upper()}")
                        st.write(f"**Category:** {medicine.get('therapeutic_category', 'N/A')}")
                else:
                    st.error(f"Error: {result.get('message')}")
        else:
            st.info("No medicines found matching the criteria")
    
    except Exception as e:
        st.error(f"Error loading medicines: {str(e)}")

with tab2:
    st.markdown("### Formulation Details")
    
    try:
        medicines = list(st.session_state.db_helper.medicines.find({"status": "active"}, limit=100))
        
        if medicines:
            selected_med = st.selectbox(
                "Select Medicine",
                options=[m.get("medicine_id") for m in medicines],
                format_func=lambda x: next((m.get("name") for m in medicines if m.get("medicine_id") == x), x),
                key="formulation_select"
            )
            
            if selected_med:
                result = st.session_state.medicine_mcp.call_endpoint(
                    "get_formulation_info",
                    {"medicine_id": selected_med}
                )
                
                if result.get("status") == "success":
                    formulation = result.get("data", {})
                    
                    if formulation:
                        st.success("✅ Formulation Found")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Formulation Details**")
                            st.write(f"**ID:** {formulation.get('formulation_id', 'N/A')}")
                            st.write(f"**Version:** {formulation.get('version', 'N/A')}")
                            st.write(f"**Standard Batch Size:** {formulation.get('batch_size_standard', 'N/A'):,} units")
                            st.write(f"**Description:** {formulation.get('description', 'N/A')}")
                        
                        with col2:
                            st.markdown("**Manufacturing Parameters**")
                            st.write(f"**Mixing Time:** {formulation.get('mixing_time_minutes', 'N/A')} min")
                            st.write(f"**Compression Force:** {formulation.get('compression_force_kn', 'N/A')} kN")
                            st.write(f"**Coating Temp:** {formulation.get('coating_temperature_c', 'N/A')} °C")
                        
                        # Components
                        st.markdown("**Components**")
                        components = []
                        for i in range(1, 10):
                            comp_id = formulation.get(f"component_{i}_id")
                            if comp_id:
                                components.append({
                                    "ID": comp_id,
                                    "Name": formulation.get(f"component_{i}_name", "N/A"),
                                    "Type": formulation.get(f"component_{i}_type", "N/A"),
                                    "Quantity": formulation.get(f"component_{i}_qty", "N/A"),
                                    "Unit": formulation.get(f"component_{i}_unit", "N/A")
                                })
                        
                        if components:
                            comp_df = pd.DataFrame(components)
                            st.dataframe(comp_df, use_container_width=True, hide_index=True)
                        
                        # Manufacturing Process
                        st.markdown("**Manufacturing Process**")
                        process = formulation.get("manufacturing_process", "N/A")
                        if isinstance(process, str):
                            steps = process.split("|")
                            for idx, step in enumerate(steps, 1):
                                st.write(f"{idx}. {step}")
                    else:
                        st.warning("No formulation found for this medicine")
                else:
                    st.error(f"Error: {result.get('message')}")
    
    except Exception as e:
        st.error(f"Error loading formulations: {str(e)}")

with tab3:
    st.markdown("### Add New Medicine")
    
    with st.form("add_medicine_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            medicine_id = st.text_input("Medicine ID*", placeholder="MED-XXX")
            name = st.text_input("Name*", placeholder="e.g., Aspirin 500mg")
            generic_name = st.text_input("Generic Name*", placeholder="e.g., Acetylsalicylic Acid")
            dosage_form = st.selectbox("Dosage Form*", ["tablet", "capsule", "injection", "syrup", "cream"])
            strength = st.text_input("Strength*", placeholder="e.g., 500mg")
        
        with col2:
            therapeutic_category = st.text_input("Therapeutic Category*", placeholder="e.g., Analgesics")
            storage_conditions = st.text_input("Storage Conditions*", placeholder="Store at 20-25°C")
            shelf_life_months = st.number_input("Shelf Life (months)*", min_value=1, max_value=120, value=36)
            fda_approved = st.checkbox("FDA Approved", value=False)
            ema_approved = st.checkbox("EMA Approved", value=False)
        
        submitted = st.form_submit_button("➕ Add Medicine", use_container_width=True)
        
        if submitted:
            if not all([medicine_id, name, generic_name, dosage_form, strength, therapeutic_category, storage_conditions]):
                st.error("Please fill in all required fields marked with *")
            else:
                try:
                    result = st.session_state.medicine_mcp.call_endpoint(
                        "create_medicine",
                        {
                            "medicine_id": medicine_id,
                            "name": name,
                            "generic_name": generic_name,
                            "dosage_form": dosage_form,
                            "strength": strength,
                            "therapeutic_category": therapeutic_category,
                            "storage_conditions": storage_conditions,
                            "shelf_life_months": shelf_life_months,
                            "fda_approved": fda_approved,
                            "ema_approved": ema_approved,
                            "status": "active"
                        }
                    )
                    
                    if result.get("status") == "success":
                        st.success(f"✅ Medicine {medicine_id} created successfully!")
                        st.balloons()
                    else:
                        st.error(f"Error: {result.get('message')}")
                except Exception as e:
                    st.error(f"Error creating medicine: {str(e)}")

with tab4:
    st.markdown("### Vector Search - Similar Formulations")
    st.info("🔍 Use AI-powered vector search to find formulations with similar components and manufacturing processes")
    
    try:
        # Get sample formulation for search
        formulations = list(st.session_state.db_helper.formulations.find({}, limit=50))
        
        if formulations:
            selected_form = st.selectbox(
                "Select Formulation as Reference",
                options=[f.get("formulation_id") for f in formulations],
                format_func=lambda x: next((f"{f.get('formulation_id')} - {f.get('description', 'N/A')[:50]}" 
                                          for f in formulations if f.get("formulation_id") == x), x)
            )
            
            top_k = st.slider("Number of similar formulations", 1, 10, 3)
            
            if st.button("🔍 Find Similar Formulations", use_container_width=True):
                # Get reference formulation
                ref_formulation = next((f for f in formulations if f.get("formulation_id") == selected_form), None)
                
                if ref_formulation:
                    with st.spinner("Searching for similar formulations..."):
                        result = st.session_state.medicine_mcp.call_endpoint(
                            "get_similar_formulations",
                            {
                                "formulation_id": selected_form,
                                "top_k": top_k
                            }
                        )
                        
                        if result.get("status") == "success":
                            similar = result.get("data", [])
                            
                            if similar:
                                st.success(f"✅ Found {len(similar)} similar formulations")
                                
                                for idx, form in enumerate(similar, 1):
                                    with st.expander(f"#{idx} - {form.get('formulation_id')} (Similarity: {form.get('similarity_score', 0):.2%})"):
                                        st.write(f"**Description:** {form.get('description', 'N/A')}")
                                        st.write(f"**Version:** {form.get('version', 'N/A')}")
                                        st.write(f"**Batch Size:** {form.get('batch_size_standard', 'N/A'):,} units")
                                        st.write(f"**Manufacturing Process:** {form.get('manufacturing_process', 'N/A')}")
                            else:
                                st.info("No similar formulations found")
                        else:
                            st.error(f"Error: {result.get('message')}")
        else:
            st.warning("No formulations available for vector search")
    
    except Exception as e:
        st.error(f"Error performing vector search: {str(e)}")

# Footer
st.markdown("---")
st.markdown("💊 Medicine Catalog | [Back to Dashboard](../app.py)")
