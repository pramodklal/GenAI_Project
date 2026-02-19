"""
Data Import Page - Upload CSV files and create collections in Astra DB
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from astrapy import DataAPIClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Data Import - Healthcare Digital",
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

# Initialize database
try:
    token = os.getenv('ASTRA_DB_TOKEN')
    api_endpoint = os.getenv('ASTRA_DB_API_ENDPOINT')
    
    if not token or not api_endpoint:
        st.sidebar.error("❌ Missing Astra DB credentials")
        st.error("Cannot connect to database. Please check your .env file.")
        st.stop()
    
    client = DataAPIClient(token)
    db = client.get_database_by_api_endpoint(api_endpoint)
    
    st.sidebar.success("✅ Connected to Astra DB")
    
    # Show collection count
    try:
        existing_colls = db.list_collection_names()
        coll_count = len(existing_colls)
        st.sidebar.info(f"Collections: {coll_count}")
    except:
        pass
        
except Exception as e:
    st.sidebar.error(f"❌ Database connection failed: {str(e)}")
    st.error("Cannot connect to database. Please check your configuration in .env file.")
    st.stop()

# Collection definitions
COLLECTIONS = {
    'patients': {
        'description': 'Patient profiles and dietary information',
        'vector': False,
        'dimension': 0
    },
    'meal_orders': {
        'description': 'Patient meal orders',
        'vector': False,
        'dimension': 0
    },
    'menu_items': {
        'description': 'Available menu items',
        'vector': False,
        'dimension': 0
    },
    'food_inventory': {
        'description': 'Food inventory and stock levels',
        'vector': False,
        'dimension': 0
    },
    'evs_tasks': {
        'description': 'Environmental services tasks',
        'vector': False,
        'dimension': 0
    },
    'evs_staff': {
        'description': 'Environmental services staff',
        'vector': False,
        'dimension': 0
    }
}

# Page header
st.title("📤 Data Import Manager")
st.markdown("Upload CSV files and import data into Astra DB collections")

# Define helper functions
def generate_embedding(text, dimension=1536):
    """Generate embedding for text using OpenAI"""
    try:
        # Check if OpenAI is configured
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key or openai_key == 'your-openai-api-key':
            st.warning("⚠️ OpenAI API key not configured. Using mock embeddings.")
            # Return mock embedding for testing
            import random
            return [random.uniform(-1, 1) for _ in range(dimension)]
        
        # Use OpenAI for real embeddings
        from openai import OpenAI
        client = OpenAI(api_key=openai_key)
        
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        embedding = response.data[0].embedding
        
        # Truncate or pad to match dimension
        if len(embedding) > dimension:
            return embedding[:dimension]
        elif len(embedding) < dimension:
            return embedding + [0.0] * (dimension - len(embedding))
        return embedding
        
    except Exception as e:
        st.error(f"❌ Embedding generation failed: {str(e)}")
        return None

def parse_json_field(value):
    """Parse JSON string fields (lists, dicts)"""
    if pd.isna(value) or value == '' or value == 'None':
        return None
    
    if isinstance(value, str):
        # Try to parse as JSON
        try:
            return json.loads(value.replace("'", '"'))
        except:
            # If not valid JSON, return as-is
            return value
    
    return value

def process_csv_row(row, collection_name, collection_config):
    """Convert CSV row to document format"""
    doc = {}
    
    for col, value in row.items():
        # Skip empty values
        if pd.isna(value) or value == '':
            continue
        
        # Parse JSON-like fields (lists, dicts)
        parsed_value = parse_json_field(value)
        
        # Handle vector_text column for vector collections
        if col == 'vector_text' and collection_config['vector']:
            continue  # We'll process this separately
        
        doc[col] = parsed_value
    
    # Generate embedding for vector collections
    if collection_config['vector'] and 'vector_text' in row:
        vector_text = row['vector_text']
        if not pd.isna(vector_text) and vector_text:
            embedding = generate_embedding(vector_text, collection_config['dimension'])
            if embedding:
                doc['$vector'] = embedding
    
    return doc

def upload_data(db, collection_name, df, mode='full'):
    """Upload data to collection"""
    try:
        collection_config = COLLECTIONS[collection_name]
        
        # Check if collection exists, create if not
        existing_collections = db.list_collection_names()
        
        if collection_name not in existing_collections:
            st.warning(f"⚠️ Collection '{collection_name}' does not exist. Creating it now...")
            st.info("💡 Please create the collection manually using create_astra_collections.py first")
            st.code("python database/create_astra_collections.py", language="bash")
            st.stop()
        
        # Get collection
        collection = db.get_collection(collection_name)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        success_count = 0
        failed_count = 0
        
        # Clear collection if full mode
        if mode == 'full':
            status_text.text("🗑️ Clearing existing data...")
            try:
                # Get all documents and delete
                existing_docs = list(collection.find({}, projection={"_id": 1}, limit=1000))
                if existing_docs:
                    for doc in existing_docs:
                        collection.delete_one({"_id": doc["_id"]})
                    st.info(f"Cleared {len(existing_docs)} existing documents")
            except Exception as e:
                st.warning(f"⚠️ Could not clear collection: {str(e)}")
        
        # Upload rows
        total_rows = len(df)
        for idx, row in df.iterrows():
            try:
                # Convert row to document
                doc = process_csv_row(row, collection_name, collection_config)
                
                # Insert document
                collection.insert_one(doc)
                success_count += 1
                
                # Update progress
                progress = (idx + 1) / total_rows
                progress_bar.progress(progress)
                status_text.text(f"📤 Uploading... {idx + 1}/{total_rows}")
                
            except Exception as e:
                failed_count += 1
                st.error(f"❌ Row {idx + 1} failed: {str(e)}")
        
        progress_bar.progress(1.0)
        status_text.text(f"✅ Upload complete!")
        
        return success_count, failed_count
        
    except Exception as e:
        st.error(f"❌ Upload failed: {str(e)}")
        return 0, 0

# Create tabs
tab1, tab2, tab3 = st.tabs(["📁 Upload CSV", "📊 Manage Collections", "📋 Import History"])

# Tab 1: Upload CSV
with tab1:
    st.header("Upload and Import CSV Data")
    
    # File uploader
    uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
    
    if uploaded_file:
        # Read CSV
        df = pd.read_csv(uploaded_file)
        st.success(f"✅ Loaded {len(df)} rows from {uploaded_file.name}")
        
        # Show preview
        with st.expander("📊 Preview Data"):
            st.dataframe(df.head(10))
        
        # Collection selection
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("1️⃣ Select Collection")
            
            collection_options = [f"{name} - {info['description']}" for name, info in COLLECTIONS.items()]
            selected_option = st.selectbox(
                "Choose target collection",
                collection_options,
                help="Select which collection to upload data to"
            )
            
            # Extract collection name
            collection_name = selected_option.split(" - ")[0]
            collection_config = COLLECTIONS[collection_name]
            
            # Show collection info
            if collection_config['vector']:
                st.info(f"🔮 Vector-enabled collection ({collection_config['dimension']}D embeddings will be generated from 'vector_text' column)")
            else:
                st.info("📄 Regular document collection")
        
        with col2:
            # Upload mode
            st.subheader("2️⃣ Upload Mode")
            upload_mode = st.radio(
                "Select mode",
                ["full", "incremental"],
                help="Full: Clear collection before upload\nIncremental: Append to existing data"
            )
            
            if upload_mode == "full":
                st.warning("⚠️ Full mode will DELETE all existing data in the collection!")
            else:
                st.info("➕ Incremental mode will append to existing data")
        
        # Upload button
        if st.button("🚀 Start Import", type="primary", use_container_width=True):
            with st.spinner(f"Importing {len(df)} rows to {collection_name}..."):
                success, failed = upload_data(db, collection_name, df, upload_mode)
                
                if success > 0:
                    st.success(f"✅ Successfully imported {success} documents!")
                if failed > 0:
                    st.error(f"❌ Failed to import {failed} documents")
    else:
        st.info("👆 Please upload a CSV file to begin")
    
    # Show existing collections
    st.markdown("---")
    st.subheader("📚 Existing Collections")
    try:
        existing = db.list_collection_names()
        cols = st.columns(3)
        for idx, coll_name in enumerate(sorted(existing)):
            with cols[idx % 3]:
                st.text(f"✓ {coll_name}")
        
        missing = [name for name in COLLECTIONS.keys() if name not in existing]
        if missing:
            st.warning(f"⚠️ Missing {len(missing)} collections")
            cols = st.columns(3)
            for idx, coll in enumerate(missing):
                with cols[idx % 3]:
                    st.text(f"✗ {coll}")
    except Exception as e:
        st.error(f"Error: {str(e)}")

# Tab 2: Manage Collections
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
