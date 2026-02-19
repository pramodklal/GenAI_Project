import streamlit as st
import pandas as pd
import sys
import os
from pathlib import Path
import json
from datetime import datetime

# Add parent directory to path for imports
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.database.astra_helper import AstraDBHelper

# Page configuration
st.set_page_config(
    page_title="CSV Import - Research Laboratory",
    page_icon="📤",
    layout="wide"
)

st.title("📤 CSV Data Import")
st.markdown("---")

# Initialize database helper
@st.cache_resource
def init_db():
    try:
        return AstraDBHelper()
    except Exception as e:
        st.error(f"Failed to initialize database: {str(e)}")
        return None

db = init_db()

if db is None:
    st.stop()

# Get all collection names
try:
    # Predefined collections from the database schema
    all_collections = [
        "research_projects", "clinical_trials", "drug_candidates",
        "lab_experiments", "research_compounds", "trial_participants",
        "research_publications", "molecular_structures", "research_papers",
        "patent_documents"
    ]
    
    # Try to get existing collections from database
    existing_collections = db.get_collection_names()
    
    # Use existing collections if available, otherwise use predefined list
    collection_names = existing_collections if existing_collections else all_collections
    
    if not collection_names:
        st.warning("⚠️ No collections configured. Please check database setup.")
        st.stop()
        
except Exception as e:
    st.error(f"❌ Error fetching collections: {str(e)}")
    st.stop()

# Identify vector collections
vector_collections = ['molecular_structures', 'research_papers', 'patent_documents']

# Main UI
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📋 Select Collection")
    
    # Collection dropdown
    selected_collection = st.selectbox(
        "Choose a collection to import data into:",
        options=collection_names,
        help="Select the target collection for CSV import"
    )
    
    # Display collection info
    if selected_collection:
        is_vector = selected_collection in vector_collections
        st.info(
            f"**Collection Type:** {'🔷 Vector (1536D)' if is_vector else '📄 Regular'}\n\n"
            f"**Name:** `{selected_collection}`"
        )
        
        if is_vector:
            st.warning("⚠️ **Vector Collection:** Embeddings will be generated automatically for text content.")

with col2:
    st.subheader("📁 Upload CSV File")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload a CSV file with data to import. Column names should match collection field names."
    )
    
    if uploaded_file is not None:
        try:
            # Read CSV file
            df = pd.read_csv(uploaded_file)
            
            st.success(f"✅ CSV file loaded successfully!")
            st.write(f"**Rows:** {len(df)} | **Columns:** {len(df.columns)}")
            
            # Display preview
            with st.expander("👁️ Preview Data (First 5 rows)", expanded=True):
                st.dataframe(df.head(), use_container_width=True)
            
            # Display columns
            with st.expander("📊 Column Information"):
                col_info = pd.DataFrame({
                    'Column Name': df.columns,
                    'Data Type': df.dtypes.values,
                    'Non-Null Count': df.count().values,
                    'Null Count': df.isnull().sum().values
                })
                st.dataframe(col_info, use_container_width=True)
            
            st.markdown("---")
            
            # Import options
            st.subheader("⚙️ Import Options")
            
            col_opt1, col_opt2 = st.columns(2)
            
            with col_opt1:
                clear_collection = st.checkbox(
                    "Clear collection before import",
                    value=False,
                    help="Delete all existing documents in the collection before importing"
                )
            
            with col_opt2:
                batch_size = st.number_input(
                    "Batch size",
                    min_value=1,
                    max_value=100,
                    value=20,
                    help="Number of documents to insert at once"
                )
            
            # Generate embeddings option (only for vector collections)
            generate_embeddings = False
            embedding_field = None
            
            if selected_collection in vector_collections:
                st.markdown("#### 🤖 Vector Embedding Configuration")
                generate_embeddings = st.checkbox(
                    "Generate embeddings from text field",
                    value=True,
                    help="Automatically generate 1536D embeddings from specified text field"
                )
                
                if generate_embeddings:
                    text_columns = df.select_dtypes(include=['object']).columns.tolist()
                    
                    # Suggest embedding field based on collection type
                    suggested_field = None
                    if selected_collection == 'molecular_structures':
                        suggested_field = 'abstract' if 'abstract' in text_columns else text_columns[0] if text_columns else None
                    elif selected_collection == 'research_papers':
                        suggested_field = 'abstract' if 'abstract' in text_columns else text_columns[0] if text_columns else None
                    elif selected_collection == 'patent_documents':
                        suggested_field = 'abstract' if 'abstract' in text_columns else text_columns[0] if text_columns else None
                    
                    embedding_field = st.selectbox(
                        "Select text field for embedding generation:",
                        options=text_columns,
                        index=text_columns.index(suggested_field) if suggested_field in text_columns else 0,
                        help="This field will be used to generate vector embeddings"
                    )
            
            st.markdown("---")
            
            # Import button
            if st.button("🚀 Import Data to Collection", type="primary", use_container_width=True):
                with st.spinner("Processing..."):
                    try:
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        # Clear collection if requested
                        if clear_collection:
                            status_text.text("🗑️ Clearing existing data...")
                            # Note: Astra DB doesn't have a direct "clear all" method, 
                            # so we'd need to implement this if needed
                            st.warning("⚠️ Clear collection functionality requires implementation")
                        
                        # Convert DataFrame to list of dictionaries
                        records = df.to_dict('records')
                        total_records = len(records)
                        imported_count = 0
                        error_count = 0
                        errors = []
                        
                        # Process in batches
                        for i in range(0, total_records, batch_size):
                            batch = records[i:i + batch_size]
                            batch_num = i // batch_size + 1
                            total_batches = (total_records + batch_size - 1) // batch_size
                            
                            status_text.text(f"📥 Importing batch {batch_num}/{total_batches}...")
                            
                            # Process each document in batch
                            for record in batch:
                                try:
                                    # Clean up NaN values
                                    doc = {k: (None if pd.isna(v) else v) for k, v in record.items()}
                                    
                                    # Generate embedding for vector collections
                                    if generate_embeddings and embedding_field and selected_collection in vector_collections:
                                        text_content = doc.get(embedding_field, '')
                                        if text_content and isinstance(text_content, str):
                                            # Generate embedding using OpenAI
                                            try:
                                                import openai
                                                client = openai.OpenAI()
                                                response = client.embeddings.create(
                                                    model="text-embedding-3-small",
                                                    input=text_content[:8000]  # Limit text length
                                                )
                                                doc['$vector'] = response.data[0].embedding
                                            except Exception as e:
                                                st.warning(f"⚠️ Failed to generate embedding: {str(e)}")
                                                # Continue without embedding
                                    
                                    # Insert document using generic insert method
                                    success = db.insert_document(selected_collection, doc)
                                    
                                    if success:
                                        imported_count += 1
                                    else:
                                        error_count += 1
                                        errors.append(f"Row {imported_count + error_count}: Failed to insert document")
                                    
                                except Exception as e:
                                    error_count += 1
                                    errors.append(f"Row {imported_count + error_count}: {str(e)}")
                            
                            # Update progress
                            progress = min((i + batch_size) / total_records, 1.0)
                            progress_bar.progress(progress)
                        
                        # Complete
                        progress_bar.progress(1.0)
                        status_text.empty()
                        
                        # Display results
                        st.success(f"✅ **Import Complete!**")
                        
                        col_res1, col_res2, col_res3 = st.columns(3)
                        with col_res1:
                            st.metric("Total Records", total_records)
                        with col_res2:
                            st.metric("Successfully Imported", imported_count)
                        with col_res3:
                            st.metric("Errors", error_count)
                        
                        if errors:
                            with st.expander("⚠️ View Errors", expanded=False):
                                for error in errors[:50]:  # Show first 50 errors
                                    st.text(error)
                                if len(errors) > 50:
                                    st.text(f"... and {len(errors) - 50} more errors")
                        
                        # Refresh button
                        if st.button("🔄 Import Another File"):
                            st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Import failed: {str(e)}")
                        st.exception(e)
        
        except Exception as e:
            st.error(f"❌ Error reading CSV file: {str(e)}")
            st.exception(e)
    
    else:
        st.info("👆 Please upload a CSV file to begin import")

# Sidebar - Help and Info
with st.sidebar:
    st.header("📖 Help & Information")
    
    st.markdown("""
    ### How to Import CSV Data
    
    1. **Select Collection**: Choose the target collection from dropdown
    2. **Upload CSV**: Click to upload your CSV file
    3. **Preview Data**: Review the data and column information
    4. **Configure Options**: 
       - Choose batch size
       - Clear collection (if needed)
       - Configure embeddings (for vector collections)
    5. **Import**: Click the import button
    
    ### CSV Format Guidelines
    
    - **Column Names**: Should match collection field names
    - **Data Types**: Will be auto-detected from CSV
    - **Missing Values**: Empty cells will be treated as NULL
    - **Dates**: Use ISO format (YYYY-MM-DD)
    
    ### Vector Collections
    
    For vector-enabled collections:
    - `molecular_structures`
    - `research_papers`
    - `patent_documents`
    
    Embeddings will be generated automatically from selected text field using OpenAI's `text-embedding-3-small` model (1536 dimensions).
    
    ### Batch Processing
    
    Data is imported in batches to optimize performance:
    - Default batch size: 20 documents
    - Adjust based on document size
    - Progress is shown in real-time
    """)
    
    st.markdown("---")
    st.caption("Research Laboratory Data Management")
    st.caption(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
