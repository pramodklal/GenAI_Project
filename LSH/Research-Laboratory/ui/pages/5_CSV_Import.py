"""
CSV Import Page - Upload CSV files and manage collections in Astra DB
Research Laboratory System
"""

import streamlit as st
import pandas as pd
import json
import csv
from pathlib import Path
import sys
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

# Custom CSS
st.markdown("""
<style>
.upload-section {
    background-color: #f0f2f6;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
}

.success-box {
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    color: #155724;
    padding: 15px;
    border-radius: 5px;
    margin: 10px 0;
}

.error-box {
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    color: #721c24;
    padding: 15px;
    border-radius: 5px;
    margin: 10px 0;
}

.info-box {
    background-color: #d1ecf1;
    border: 1px solid #bee5eb;
    color: #0c5460;
    padding: 15px;
    border-radius: 5px;
    margin: 10px 0;
}

.warning-box {
    background-color: #fff3cd;
    border: 1px solid #ffeeba;
    color: #856404;
    padding: 15px;
    border-radius: 5px;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

# Page header
st.title("📤 CSV Import - Research Laboratory")
st.markdown("Upload CSV files and manage collections for research data")

# Initialize database connection
@st.cache_resource
def init_db():
    try:
        return AstraDBHelper()
    except Exception as e:
        return None

db = init_db()

# Sidebar status
with st.sidebar:
    st.header("Connection Status")
    if db:
        st.success("✅ Astra DB Connected")
        try:
            collections = db.get_collection_names()
            st.info(f"📊 {len(collections)} collections")
        except Exception as e:
            st.warning(f"⚠️ {str(e)}")
    else:
        st.error("❌ Not Connected")
        st.stop()

# Tabs
tab1, tab2, tab3 = st.tabs(["📁 Upload CSV", "📊 Manage Collections", "📋 Import History"])

with tab1:
    st.header("Upload and Import CSV Data")
    
    # Define standard collections for Research Laboratory system
    standard_collections = {
        "research_projects": "Research projects and studies",
        "clinical_trials": "Clinical trial data and protocols",
        "drug_candidates": "Drug candidate compounds",
        "lab_experiments": "Laboratory experiment records",
        "research_compounds": "Chemical compound catalog",
        "trial_participants": "Clinical trial participant data",
        "research_publications": "Scientific publications",
        "molecular_structures": "Molecular structure data (Vector-enabled)",
        "research_papers": "Research paper documents (Vector-enabled)",
        "patent_documents": "Patent documentation (Vector-enabled)"
    }
    
    # Get existing collections from database
    try:
        existing_collections = db.get_collection_names()
    except Exception as e:
        st.error(f"Error fetching collections: {str(e)}")
        existing_collections = []
    
    # Combine standard and existing collections
    all_collections = list(standard_collections.keys())
    for coll in existing_collections:
        if coll not in all_collections:
            all_collections.append(coll)
    
    # Collection selection
    col1, col2 = st.columns([3, 1])
    with col1:
        collection_options = []
        for coll_name in all_collections:
            if coll_name in existing_collections:
                collection_options.append(f"📦 {coll_name}")
            else:
                collection_options.append(f"📝 {coll_name} (not created)")
        
        selected_option = st.selectbox(
            "Select Collection",
            options=collection_options,
            help="Choose a collection from the Research Laboratory system"
        )
        
        # Show description if available
        clean_name = selected_option.replace("📦 ", "").replace("📝 ", "").replace(" (not created)", "")
        if clean_name in standard_collections:
            st.caption(f"ℹ️ {standard_collections[clean_name]}")
    
    with col2:
        st.write("")
        st.write("")
        if st.button("🔄 Refresh", help="Refresh collection list"):
            st.rerun()
    
    # Parse selection
    collection_name = selected_option.replace("📦 ", "").replace("📝 ", "").replace(" (not created)", "")
    collection_exists = collection_name in existing_collections
    
    if not collection_exists:
        st.markdown("---")
        st.subheader("Collection Configuration")
        st.info(f"📝 Collection **'{collection_name}'** will be created during import")
        
        # Check if this is a vector-enabled collection
        vector_collections = ["molecular_structures", "research_papers", "patent_documents"]
        
        col1, col2 = st.columns(2)
        with col1:
            if collection_name in vector_collections:
                enable_vector = st.checkbox(
                    "Enable Vector Search",
                    value=True,
                    help="This collection typically uses vector embeddings"
                )
            else:
                enable_vector = st.checkbox(
                    "Enable Vector Search",
                    value=False,
                    help="Enable if your data contains vector embeddings"
                )
        
        with col2:
            if enable_vector:
                vector_dimension = st.number_input(
                    "Vector Dimension",
                    min_value=128,
                    max_value=4096,
                    value=1536,
                    step=128,
                    help="Dimension of vector embeddings"
                )
        
        if enable_vector:
            vector_metric = st.selectbox(
                "Distance Metric",
                ["cosine", "euclidean", "dot_product"],
                help="Metric for vector similarity"
            )
        
        # Store creation settings
        st.session_state['new_collection_name'] = collection_name
        st.session_state['enable_vector'] = enable_vector
        if enable_vector:
            st.session_state['vector_dimension'] = vector_dimension
            st.session_state['vector_metric'] = vector_metric
    else:
        st.success(f"✅ Selected collection: **{collection_name}**")
        
        # Show collection info
        try:
            coll = db.db.get_collection(collection_name)
            sample_doc = coll.find_one()
            
            if sample_doc:
                doc_count = coll.count_documents({}, limit=10000)
                st.info(f"📊 Current documents: ~{doc_count}")
                
                # Show sample fields
                fields = list(sample_doc.keys())
                if '$vector' in fields:
                    st.info("🔍 Vector search is enabled for this collection")
                    fields.remove('$vector')
                
                with st.expander("View Collection Fields"):
                    st.write(", ".join(fields[:20]))
            else:
                st.info("📊 Collection is empty (0 documents)")
        except Exception as e:
            st.warning(f"Could not fetch collection info: {str(e)}")
    
    # Step 2: Upload CSV
    if collection_name:
        st.markdown("---")
        st.subheader("Step 2: Upload CSV File")
        
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type=['csv'],
            help="Upload a CSV file containing your research data"
        )
        
        if uploaded_file is not None:
            try:
                # Read CSV with error handling for malformed data
                df = pd.read_csv(
                    uploaded_file,
                    on_bad_lines='skip',  # Skip lines with parsing errors
                    encoding='utf-8',
                    quotechar='"',
                    escapechar='\\',
                    low_memory=False
                )
                
                # Display file info
                st.markdown('<div class="info-box">', unsafe_allow_html=True)
                st.write(f"**File:** {uploaded_file.name}")
                st.write(f"**Rows:** {len(df)}")
                st.write(f"**Columns:** {len(df.columns)}")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Preview data
                st.subheader("Data Preview")
                st.dataframe(df.head(10), use_container_width=True)
                
                # Column information
                st.subheader("Column Information")
                col_info = pd.DataFrame({
                    'Column': list(df.columns),
                    'Type': [str(dtype) for dtype in df.dtypes],
                    'Non-Null': [int(count) for count in df.count()],
                    'Null': [int(null) for null in df.isnull().sum()],
                    'Unique': [int(unique) for unique in df.nunique()]
                })
                st.dataframe(col_info, use_container_width=True)
                
                # Store dataframe in session state
                st.session_state['uploaded_df'] = df
                st.session_state['uploaded_filename'] = uploaded_file.name
                st.session_state['selected_collection'] = collection_name
                
                # Import settings
                st.markdown("---")
                st.subheader("Step 3: Import Settings")
                
                col1, col2 = st.columns(2)
                with col1:
                    batch_size = st.number_input(
                        "Batch Size",
                        min_value=1,
                        max_value=100,
                        value=20,
                        help="Number of documents to insert per batch"
                    )
                    
                with col2:
                    skip_errors = st.checkbox(
                        "Skip errors",
                        value=True,
                        help="Continue importing even if some documents fail"
                    )
                
                dry_run = st.checkbox(
                    "Dry run (validate without inserting)",
                    value=False,
                    help="Test the import without actually writing to database"
                )
                
                # Start import button
                if st.button("🚀 Start Import", type="primary", use_container_width=True):
                    if dry_run:
                        st.warning("🧪 Dry run mode - no data will be inserted")
                    
                    # Create collection if needed
                    if not collection_exists:
                        try:
                            if st.session_state.get('enable_vector', False):
                                dim = st.session_state.get('vector_dimension', 1536)
                                metric = st.session_state.get('vector_metric', 'cosine')
                                db.db.create_collection(collection_name)
                                st.success(f"✅ Created vector collection: {collection_name} (dim={dim}, metric={metric})")
                            else:
                                db.db.create_collection(collection_name)
                                st.success(f"✅ Created collection: {collection_name}")
                        except Exception as e:
                            st.error(f"Error creating collection: {str(e)}")
                            st.stop()
                    
                    # Import data
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    success_count = 0
                    failed_count = 0
                    error_rows = []
                    
                    total_rows = len(df)
                    for idx, row in df.iterrows():
                        try:
                            # Convert row to document
                            doc = row.to_dict()
                            
                            # Clean up None/NaN values
                            doc = {k: v for k, v in doc.items() if pd.notna(v)}
                            
                            if not dry_run:
                                # Insert document using AstraDBHelper
                                db.insert_document(collection_name, doc)
                            
                            success_count += 1
                            
                        except Exception as e:
                            failed_count += 1
                            error_rows.append({"row": idx + 1, "error": str(e)})
                            if not skip_errors:
                                st.error(f"❌ Row {idx + 1} failed: {str(e)}")
                                break
                        
                        # Update progress
                        progress = (idx + 1) / total_rows
                        progress_bar.progress(progress)
                        status_text.text(f"Processing: {idx + 1}/{total_rows}")
                    
                    progress_bar.progress(1.0)
                    
                    # Show results
                    if dry_run:
                        st.markdown('<div class="info-box">', unsafe_allow_html=True)
                        st.write(f"**Dry Run Complete**")
                        st.write(f"- Would insert: {success_count}")
                        st.write(f"- Would fail: {failed_count}")
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="success-box">', unsafe_allow_html=True)
                        st.write(f"**Import Complete**")
                        st.write(f"✅ Successfully inserted: {success_count}")
                        if failed_count > 0:
                            st.write(f"❌ Failed: {failed_count}")
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Store import history
                        if 'import_history' not in st.session_state:
                            st.session_state['import_history'] = []
                        
                        st.session_state['import_history'].append({
                            'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'filename': uploaded_file.name,
                            'collection': collection_name,
                            'total': total_rows,
                            'inserted': success_count,
                            'failed': failed_count,
                            'dry_run': dry_run
                        })
                    
                    # Show errors if any
                    if error_rows:
                        with st.expander(f"❌ View {len(error_rows)} Errors"):
                            error_df = pd.DataFrame(error_rows)
                            st.dataframe(error_df, use_container_width=True)
                
            except Exception as e:
                st.markdown(f'<div class="error-box">Error reading CSV: {str(e)}</div>', unsafe_allow_html=True)

with tab2:
    st.header("Manage Collections")
    
    # List existing collections
    st.subheader("Existing Collections")
    
    try:
        existing = db.get_collection_names()
        
        if existing:
            # Show each collection with info
            for coll_name in sorted(existing):
                with st.expander(f"📦 {coll_name}"):
                    try:
                        coll = db.db.get_collection(coll_name)
                        doc_count = coll.count_documents({}, limit=10000)
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Documents", f"~{doc_count}")
                        
                        # Check if vector-enabled
                        sample = coll.find_one()
                        if sample and '$vector' in sample:
                            with col2:
                                vector_dim = len(sample['$vector'])
                                st.metric("Vector Dimension", vector_dim)
                            with col3:
                                st.info("🔍 Vector search enabled")
                        
                        # Show sample fields
                        if sample:
                            fields = [k for k in sample.keys() if k != '$vector']
                            st.write(f"**Fields:** {', '.join(fields[:15])}")
                            if len(fields) > 15:
                                st.caption(f"... and {len(fields) - 15} more")
                        
                        # Delete button
                        if st.button(f"🗑️ Delete Collection", key=f"del_{coll_name}"):
                            if st.checkbox(f"⚠️ Confirm delete '{coll_name}'", key=f"confirm_{coll_name}"):
                                try:
                                    db.db.drop_collection(coll_name)
                                    st.success(f"✅ Deleted collection: {coll_name}")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error deleting: {str(e)}")
                    
                    except Exception as e:
                        st.error(f"Error fetching info: {str(e)}")
        else:
            st.info("No collections found")
    
    except Exception as e:
        st.error(f"Error listing collections: {str(e)}")
    
    # Create new empty collection
    st.markdown("---")
    st.subheader("Create New Empty Collection")
    
    col1, col2 = st.columns(2)
    with col1:
        new_coll_name = st.text_input("Collection Name", key="new_coll")
    with col2:
        enable_vector = st.checkbox("Enable Vector Search", key="new_vector")
    
    if enable_vector:
        col1, col2 = st.columns(2)
        with col1:
            new_dimension = st.number_input("Vector Dimension", min_value=128, max_value=4096, value=1536, step=128)
        with col2:
            new_metric = st.selectbox("Distance Metric", ["cosine", "euclidean", "dot_product"])
    
    if st.button("Create Collection", type="primary"):
        if new_coll_name:
            try:
                if enable_vector:
                    db.db.create_collection(new_coll_name)
                    st.info(f"Note: Created with vector dimension {new_dimension} and {new_metric} metric")
                else:
                    db.db.create_collection(new_coll_name)
                st.success(f"✅ Created collection: {new_coll_name}")
                st.rerun()
            except Exception as e:
                st.error(f"Error creating collection: {str(e)}")
        else:
            st.error("Please enter a collection name")

with tab3:
    st.header("Import History")
    
    if 'import_history' in st.session_state and st.session_state['import_history']:
        history_df = pd.DataFrame(st.session_state['import_history'])
        
        # Display summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Imports", len(history_df))
        with col2:
            st.metric("Total Documents", history_df['inserted'].sum())
        with col3:
            st.metric("Total Failures", history_df['failed'].sum())
        with col4:
            success_rate = (history_df['inserted'].sum() / history_df['total'].sum() * 100) if history_df['total'].sum() > 0 else 0
            st.metric("Success Rate", f"{success_rate:.1f}%")
        
        # Display history table
        st.dataframe(
            history_df[['timestamp', 'filename', 'collection', 'total', 'inserted', 'failed', 'dry_run']],
            use_container_width=True
        )
        
        # Clear history button
        if st.button("Clear History"):
            st.session_state['import_history'] = []
            st.rerun()
    else:
        st.info("No import history yet. Upload and import some data to see history here.")

# Sidebar information
with st.sidebar:
    st.markdown("---")
    st.subheader("📖 Quick Guide")
    st.markdown("""
    **Steps to import data:**
    
    1. **Upload CSV** - Choose your CSV file
    2. **Configure** - Set collection name and options
    3. **Review** - Check data preview and column info
    4. **Import** - Click 'Start Import' button
    
    **Tips:**
    - Use descriptive collection names
    - Enable vector search for embeddings
    - Use batch size 20-50 for best performance
    - Enable 'Skip errors' for large imports
    - Use 'Dry run' to validate first
    """)
    
    st.markdown("---")
    st.subheader("⚙️ Supported Data Types")
    st.markdown("""
    - **Text**: String values
    - **Numbers**: Integers, floats
    - **Dates**: ISO format strings
    - **Booleans**: true/false
    - **Arrays**: List values (comma-separated)
    - **Vectors**: Embedding arrays (for vector search)
    - **Null**: Empty values (converted to None)
    """)
    
    st.markdown("---")
    st.info("💡 For best results, ensure your CSV has clean data with consistent types per column.")
