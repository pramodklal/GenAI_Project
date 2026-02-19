"""
Data Import Page - Upload CSV files and create collections in Astra DB
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.database.astra_helper import AstraDBHelper

# Page configuration
st.set_page_config(
    page_title="Data Import - Pharma Manufacturing System",
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
        color: #155724;
        padding: 15px;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
        margin: 10px 0;
    }
    .error-box {
        background-color: #f8d7da;
        color: #721c24;
        padding: 15px;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
        margin: 10px 0;
    }
    .info-box {
        background-color: #d1ecf1;
        color: #0c5460;
        padding: 15px;
        border-radius: 5px;
        border: 1px solid #bee5eb;
        margin: 10px 0;
    }
    .warning-box {
        background-color: #fff3cd;
        color: #856404;
        padding: 15px;
        border-radius: 5px;
        border: 1px solid #ffeeba;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize database helper
try:
    db = AstraDBHelper()
    st.sidebar.success("✅ Connected to Astra DB")
    st.sidebar.info(f"Keyspace: {db.keyspace}")
    
    # Show collection count
    try:
        existing_colls = db.get_collection_names()
        coll_count = len(existing_colls)
        st.sidebar.info(f"Collections: {coll_count}/10")
        if coll_count >= 10:
            st.sidebar.warning("⚠️ Collection limit reached!")
    except:
        pass
except Exception as e:
    st.sidebar.error(f"❌ Database connection failed: {str(e)}")
    st.error("Cannot connect to database. Please check your configuration in .mmdenv file.")
    st.stop()

# Page header
st.title("📤 Data Import Manager")
st.markdown("Upload CSV files and import data into Astra DB collections")

# Create tabs
tab1, tab2, tab3 = st.tabs(["📁 Upload CSV", "📊 Manage Collections", "📋 Import History"])

with tab1:
    st.header("Upload and Import CSV Data")
    
    # Step 1: Select Collection
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    st.subheader("Step 1: Select Collection")
    
    # Define standard collections for pharmaceutical manufacturing system
    standard_collections = {
        "medicines": "Medicine catalog and product information",
        "formulations": "Medicine formulations with components (Vector-enabled)",
        "manufacturing_batches": "Production batches and manufacturing data",
        "quality_control_tests": "QC test results and validations",
        "raw_materials": "Raw materials inventory and specifications",
        "production_schedules": "Production planning and schedules",
        "regulatory_documents": "Regulatory compliance documents",
        "audit_logs": "System audit trail (21 CFR Part 11)",
        "adverse_events": "Adverse event reports (Vector-enabled)",
        "sop_documents": "Standard Operating Procedures (Vector-enabled)"
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
            help="Choose a collection from the pharma manufacturing system"
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
    
    if collection_exists:
        collection_mode = "existing"
    else:
        collection_mode = "create"
    
    # Handle collection creation or selection
    if not collection_exists:
        st.markdown("---")
        st.subheader("Collection Configuration")
        st.info(f"📝 Collection **'{collection_name}'** will be created during import")
        
        # Check if this is a vector-enabled collection
        vector_collections = ["formulations", "adverse_events", "sop_documents"]
        
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
        else:
            vector_metric = "cosine"
        
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
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Step 2: Upload CSV (only if collection is selected/named)
    if collection_name:
        st.markdown("---")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # File uploader
            st.markdown('<div class="upload-section">', unsafe_allow_html=True)
            st.subheader("Step 2: Upload CSV File")
            uploaded_file = st.file_uploader(
                "Choose a CSV file",
                type=['csv'],
                help="Upload a CSV file containing your data"
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        if uploaded_file is not None:
            try:
                # Read CSV
                df = pd.read_csv(uploaded_file)
                
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
                    'Column': df.columns,
                    'Type': df.dtypes.astype(str),
                    'Non-Null': df.count().values,
                    'Null': df.isnull().sum().values,
                    'Unique': df.nunique().values
                })
                st.dataframe(col_info, use_container_width=True)
                
                # Store dataframe in session state
                st.session_state['uploaded_df'] = df
                st.session_state['uploaded_filename'] = uploaded_file.name
                st.session_state['selected_collection'] = collection_name
                
            except Exception as e:
                st.markdown(f'<div class="error-box">Error reading CSV: {str(e)}</div>', unsafe_allow_html=True)
        
        with col2:
            if uploaded_file is not None and 'uploaded_df' in st.session_state:
                st.markdown('<div class="upload-section">', unsafe_allow_html=True)
                st.subheader("Step 3: Import Settings")
                
                # Show collection info
                collection_exists = collection_name in existing_collections
                if collection_exists:
                    st.warning(f"⚠️ Collection exists")
                    action = st.radio(
                        "Action",
                        ["Append to existing", "Replace existing (delete & recreate)"],
                        help="Choose how to handle existing collection"
                    )
                else:
                    st.success(f"✅ Will create new collection")
                    action = "Create new"
                
                # ID field selection
                st.subheader("Step 4: ID Field")
                df = st.session_state['uploaded_df']
            
            id_option = st.radio(
                "ID Field Option",
                ["Auto-generate IDs", "Use existing column"],
                help="Choose how to handle document IDs"
            )
            
            if id_option == "Use existing column":
                id_column = st.selectbox(
                    "Select ID Column",
                    options=df.columns.tolist(),
                    help="Column to use as document ID (_id)"
                )
            else:
                id_column = None
            
            # Vector field (optional)
            st.subheader("Step 5: Vector Field (Optional)")
            has_vector = st.checkbox(
                "Enable vector search",
                help="Check if your data includes vector embeddings"
            )
            
            if has_vector:
                vector_column = st.selectbox(
                    "Vector Column",
                    options=df.columns.tolist(),
                    help="Column containing vector embeddings (should be array/list)"
                )
                vector_dimension = st.number_input(
                    "Vector Dimension",
                    min_value=128,
                    max_value=4096,
                    value=1536,
                    step=128,
                    help="Dimension of vector embeddings"
                )
            else:
                vector_column = None
                vector_dimension = None
            
                st.markdown('</div>', unsafe_allow_html=True)
    
    # Import section
    if uploaded_file is not None and 'uploaded_df' in st.session_state:
        st.markdown("---")
        st.header("Step 6: Import Data")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
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
    
    with col3:
        dry_run = st.checkbox(
            "Dry run",
            value=False,
            help="Validate without actually importing data"
        )
    
        # Import button
        if st.button("🚀 Start Import", type="primary", use_container_width=True):
            df = st.session_state['uploaded_df']
            collection_name = st.session_state['selected_collection']
            
            with st.spinner("Importing data..."):
                try:
                    # Progress tracking
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Handle collection creation/deletion
                    if not dry_run:
                        # Check if collection exists (fresh check)
                        current_collections = db.get_collection_names()
                        collection_exists = collection_name in current_collections
                        
                        if collection_exists and action == "Replace existing (delete & recreate)":
                            status_text.text("Deleting existing collection...")
                            db.db.drop_collection(collection_name)
                            st.warning(f"🗑️ Deleted existing collection: {collection_name}")
                            collection_exists = False
                        
                        # Create collection if it doesn't exist
                        if not collection_exists:
                            status_text.text("Creating collection...")
                            
                            # Check if we need vector support
                            create_vector = False
                            create_dimension = 1536
                            create_metric = "cosine"
                            
                            if collection_mode == "create" and st.session_state.get('enable_vector'):
                                # New collection with vector from settings
                                create_vector = True
                                create_dimension = st.session_state.get('vector_dimension', 1536)
                                create_metric = st.session_state.get('vector_metric', 'cosine')
                            elif has_vector and vector_column:
                                # Existing collection mode but vector data detected
                                create_vector = True
                                create_dimension = vector_dimension
                            
                            if create_vector:
                                collection = db.db.create_collection(
                                    collection_name
                                )
                                st.success(f"✅ Created vector-enabled collection: {collection_name} (dim={create_dimension})")
                                st.info(f"Note: Vector configuration with dimension {create_dimension} and {create_metric} metric")
                            else:
                                collection = db.db.create_collection(collection_name)
                                st.success(f"✅ Created collection: {collection_name}")
                        else:
                            collection = db.db.get_collection(collection_name)
                            st.info(f"📦 Using existing collection: {collection_name}")
                    
                    # Prepare documents
                    status_text.text("Preparing documents...")
                    documents = []
                    errors = []
                    
                    for idx, row in df.iterrows():
                        try:
                            doc = row.to_dict()
                            
                            # Handle ID field
                            if id_column:
                                doc['_id'] = str(doc[id_column])
                                if id_column != '_id':
                                    del doc[id_column]
                            
                            # Handle vector field
                            if has_vector and vector_column:
                                vector_data = doc.get(vector_column)
                                if isinstance(vector_data, str):
                                    # Parse string representation of list
                                    import ast
                                    vector_data = ast.literal_eval(vector_data)
                                doc['$vector'] = vector_data
                                if vector_column != '$vector':
                                    del doc[vector_column]
                            
                            # Convert NaN to None
                            for key, value in doc.items():
                                if pd.isna(value):
                                    doc[key] = None
                            
                            documents.append(doc)
                            
                        except Exception as e:
                            error_msg = f"Row {idx}: {str(e)}"
                            errors.append(error_msg)
                            if not skip_errors:
                                raise Exception(error_msg)
                    
                    # Insert documents in batches
                    if not dry_run:
                        status_text.text("Inserting documents...")
                        total_inserted = 0
                        total_failed = 0
                        
                        for i in range(0, len(documents), batch_size):
                            batch = documents[i:i + batch_size]
                            try:
                                result = collection.insert_many(batch)
                                total_inserted += len(result.inserted_ids)
                            except Exception as e:
                                if skip_errors:
                                    total_failed += len(batch)
                                    errors.append(f"Batch {i//batch_size}: {str(e)}")
                                else:
                                    raise e
                            
                            # Update progress
                            progress = min((i + batch_size) / len(documents), 1.0)
                            progress_bar.progress(progress)
                            status_text.text(f"Processed {min(i + batch_size, len(documents))}/{len(documents)} documents")
                    
                    # Show results
                    progress_bar.progress(1.0)
                    status_text.text("Import complete!")
                    
                    if dry_run:
                        st.markdown('<div class="info-box">', unsafe_allow_html=True)
                        st.write("**Dry Run Results**")
                        st.write(f"✅ Validated {len(documents)} documents")
                        if errors:
                            st.write(f"⚠️ {len(errors)} documents have issues")
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="success-box">', unsafe_allow_html=True)
                        st.write("**Import Complete!**")
                        st.write(f"✅ Successfully inserted: {total_inserted} documents")
                        if total_failed > 0:
                            st.write(f"❌ Failed: {total_failed} documents")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Show errors if any
                    if errors:
                        with st.expander(f"⚠️ View {len(errors)} errors"):
                            for error in errors[:50]:  # Show first 50 errors
                                st.text(error)
                            if len(errors) > 50:
                                st.text(f"... and {len(errors) - 50} more errors")
                    
                    # Store import history
                    if 'import_history' not in st.session_state:
                        st.session_state['import_history'] = []
                    
                    st.session_state['import_history'].append({
                        'timestamp': pd.Timestamp.now(),
                        'filename': st.session_state['uploaded_filename'],
                        'collection': collection_name,
                        'total': len(documents),
                        'inserted': total_inserted if not dry_run else 0,
                        'failed': total_failed if not dry_run else 0,
                        'dry_run': dry_run
                    })
                    
                except Exception as e:
                    error_msg = str(e)
                    st.markdown(f'<div class="error-box">Import failed: {error_msg}</div>', unsafe_allow_html=True)
                    
                    # Provide helpful context for common errors
                    if "TOO_MANY_INDEXES" in error_msg or "Too many indexes" in error_msg:
                        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
                        st.write("**💡 Collection Limit Reached**")
                        st.write("Your Astra DB keyspace has reached the maximum number of collections (indexes).")
                        st.write("**Solutions:**")
                        st.write("1. Delete unused collections from the 'Manage Collections' tab")
                        st.write("2. Upgrade your Astra DB plan for more collections")
                        st.write("3. Use a different keyspace")
                        st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.header("Manage Collections")
    
    # Get existing collections
    try:
        collections = db.get_collection_names()
        
        if collections:
            st.subheader(f"Existing Collections ({len(collections)})")
            
            for coll_name in collections:
                with st.expander(f"📦 {coll_name}"):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        try:
                            # Get collection stats
                            coll = db.db.get_collection(coll_name)
                            sample_doc = coll.find_one()
                            
                            if sample_doc:
                                doc_count = coll.count_documents({}, limit=10000)
                                st.write(f"**Documents:** ~{doc_count}")
                                st.write(f"**Fields:** {', '.join(list(sample_doc.keys())[:10])}")
                                
                                # Check if vector-enabled
                                if '$vector' in sample_doc:
                                    st.success("🔍 Vector search enabled")
                            else:
                                st.write("**Documents:** 0 (empty collection)")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                    
                    with col2:
                        if st.button("View Sample", key=f"view_{coll_name}"):
                            try:
                                coll = db.db.get_collection(coll_name)
                                docs = list(coll.find().limit(5))
                                if docs:
                                    st.json([{k: v for k, v in doc.items() if k != '$vector'} for doc in docs])
                                else:
                                    st.info("No documents found")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                    
                    with col3:
                        if st.button("🗑️ Delete", key=f"delete_{coll_name}"):
                            if st.session_state.get(f'confirm_delete_{coll_name}'):
                                try:
                                    db.db.drop_collection(coll_name)
                                    st.success(f"Deleted collection: {coll_name}")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                            else:
                                st.session_state[f'confirm_delete_{coll_name}'] = True
                                st.warning("Click again to confirm deletion")
        else:
            st.info("No collections found in this keyspace")
    
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
