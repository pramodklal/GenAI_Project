"""
Astra DB Collection Creation Script - Data API Method
Creates document collections instead of Cassandra tables using REST API

Note: Data API uses document-based collections, not traditional Cassandra tables.
This is simpler (no bundle needed) but has different data modeling.
"""

import os
import sys
from astrapy import DataAPIClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

# Define collections schema
COLLECTIONS = {
    'patients': {
        'dimension': None,  # Non-vector collection
        'description': 'Patient profiles with allergies and dietary restrictions'
    },
    'patient_dietary_profiles': {
        'dimension': None,
        'description': 'Nutritional targets and dietary modifications'
    },
    'menu_items': {
        'dimension': 1536,  # Vector enabled for semantic search
        'description': 'Menu catalog with embeddings for recommendations'
    },
    'meal_orders': {
        'dimension': None,
        'description': 'Patient meal orders with AI validation'
    },
    'evs_tasks': {
        'dimension': 768,  # Vector enabled for task similarity
        'description': 'Environmental Services tasks with embeddings'
    },
    'evs_staff': {
        'dimension': None,
        'description': 'EVS staff profiles and certifications'
    },
    'agent_activities': {
        'dimension': None,
        'description': 'Agent execution logs for monitoring'
    },
    'system_audit_logs': {
        'dimension': None,
        'description': 'HIPAA-compliant audit trail'
    },
    'food_inventory': {
        'dimension': None,
        'description': 'Ingredient inventory tracking'
    },
    'production_schedules': {
        'dimension': None,
        'description': 'AI-forecasted meal production plans'
    },
    'patient_preferences': {
        'dimension': None,  # Regular collection (avoid index limit)
        'description': 'Patient preference data'
    }
}

def get_database():
    """Connect to Astra DB using Data API"""
    
    token = os.getenv('ASTRA_DB_TOKEN')
    api_endpoint = os.getenv('ASTRA_DB_API_ENDPOINT')
    
    if not token:
        print(f"{RED}❌ Error: ASTRA_DB_TOKEN not found in .env file{RESET}")
        return None
    
    if not api_endpoint:
        print(f"{RED}❌ Error: ASTRA_DB_API_ENDPOINT not found in .env file{RESET}")
        return None
    
    print(f"{BLUE}🔌 Connecting to Astra DB via Data API...{RESET}")
    print(f"   Endpoint: {api_endpoint}")
    
    try:
        client = DataAPIClient(token)
        db = client.get_database_by_api_endpoint(api_endpoint)
        
        # Test connection
        existing_collections = db.list_collection_names()
        print(f"{GREEN}✅ Connected successfully!{RESET}")
        print(f"   Existing collections: {len(existing_collections)}\n")
        
        return db
        
    except Exception as e:
        print(f"{RED}❌ Connection failed: {str(e)}{RESET}")
        return None

def create_all_collections(db):
    """Create all collections in Astra DB"""
    
    print(f"{BLUE}📝 Creating collections...{RESET}\n")
    
    success_count = 0
    failed_count = 0
    skipped_count = 0
    
    existing_collections = db.list_collection_names()
    
    for collection_name, config in COLLECTIONS.items():
        try:
            if collection_name in existing_collections:
                print(f"   {collection_name}... {YELLOW}⏭️  Already exists{RESET}")
                skipped_count += 1
                continue
            
            print(f"   Creating: {collection_name}...", end=' ')
            
            if config['dimension']:
                # Create vector-enabled collection using direct API call
                import requests
                token = os.getenv('ASTRA_DB_TOKEN')
                api_endpoint = os.getenv('ASTRA_DB_API_ENDPOINT')
                
                # Use Data API v2 to create vector collection
                url = f"{api_endpoint}/api/json/v1/default_keyspace"
                headers = {
                    "Token": token,
                    "Content-Type": "application/json"
                }
                payload = {
                    "createCollection": {
                        "name": collection_name,
                        "options": {
                            "vector": {
                                "dimension": config['dimension'],
                                "metric": "cosine"
                            }
                        }
                    }
                }
                response = requests.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    print(f"{GREEN}✅ (Vector {config['dimension']}D){RESET}")
                else:
                    raise Exception(f"API error: {response.text}")
            else:
                # Create standard document collection
                db.create_collection(collection_name)
                print(f"{GREEN}✅ (Document){RESET}")
            
            success_count += 1
            
        except Exception as e:
            print(f"{RED}❌ Failed: {str(e)}{RESET}")
            failed_count += 1
    
    print(f"\n{BLUE}📊 Summary:{RESET}")
    print(f"   {GREEN}✅ Successfully created: {success_count} collections{RESET}")
    if skipped_count > 0:
        print(f"   {YELLOW}⏭️  Already existed: {skipped_count} collections{RESET}")
    if failed_count > 0:
        print(f"   {RED}❌ Failed: {failed_count} collections{RESET}")
    
    return success_count, failed_count

def verify_collections(db):
    """Verify all collections were created"""
    
    print(f"\n{BLUE}🔍 Verifying collections...{RESET}\n")
    print(f"   {YELLOW}⏳ Waiting for collections to sync...{RESET}")
    
    import time
    time.sleep(3)  # Wait for collections to propagate
    
    try:
        existing_collections = db.list_collection_names()
        
        print(f"   Found {len(existing_collections)} collections:")
        for collection in sorted(existing_collections):
            # Check if vector enabled
            coll = db.get_collection(collection)
            try:
                info = coll.options()
                if info and 'vector' in info:
                    vector_info = info['vector']
                    dimension = vector_info.get('dimension', 'unknown')
                    print(f"   {GREEN}✓{RESET} {collection} (Vector {dimension}D)")
                else:
                    print(f"   {GREEN}✓{RESET} {collection} (Document)")
            except:
                print(f"   {GREEN}✓{RESET} {collection}")
        
        # Check if all expected collections exist
        expected = set(COLLECTIONS.keys())
        actual = set(existing_collections)
        missing = expected - actual
        
        if missing:
            print(f"\n   {YELLOW}⚠️  Missing collections: {', '.join(missing)}{RESET}")
            return False
        else:
            print(f"\n   {GREEN}✅ All collections verified successfully!{RESET}")
            return True
            
    except Exception as e:
        print(f"{RED}❌ Verification failed: {str(e)}{RESET}")
        return False

def insert_sample_data(db):
    """Insert sample documents to test collections"""
    
    print(f"\n{BLUE}📥 Inserting sample data...{RESET}\n")
    
    try:
        # Sample patient
        patients = db.get_collection('patients')
        sample_patient = {
            "patient_id": "P001",
            "name": "John Doe",
            "room_number": "301A",
            "allergies": ["peanuts", "shellfish"],
            "dietary_restrictions": ["low-sodium", "diabetic"],
            "preferences": {"texture": "regular", "temperature": "warm"}
        }
        patients.insert_one(sample_patient)
        print(f"   {GREEN}✓{RESET} Inserted sample patient")
        
        # Sample menu item (non-vector for now)
        menu_items = db.get_collection('menu_items')
        sample_item = {
            "item_id": "MENU001",
            "name": "Grilled Chicken Breast",
            "category": "Entree",
            "calories": 250,
            "protein_g": 35.0,
            "allergens": [],
            "dietary_tags": ["low-sodium", "high-protein"]
        }
        menu_items.insert_one(sample_item)
        print(f"   {GREEN}✓{RESET} Inserted sample menu item")
        
        # Sample EVS staff
        evs_staff = db.get_collection('evs_staff')
        sample_staff = {
            "staff_id": "EVS001",
            "name": "Jane Smith",
            "shift": "morning",
            "skills": ["floor-cleaning", "disinfection"],
            "status": "available"
        }
        evs_staff.insert_one(sample_staff)
        print(f"   {GREEN}✓{RESET} Inserted sample EVS staff")
        
        print(f"\n   {GREEN}✅ Sample data inserted successfully!{RESET}")
        return True
        
    except Exception as e:
        print(f"   {RED}❌ Failed to insert sample data: {str(e)}{RESET}")
        return False

def main():
    """Main execution function"""
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}🏥 Healthcare Digital - Astra DB Setup (Data API){RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    # Connect to database
    db = get_database()
    if not db:
        print(f"\n{RED}❌ Setup failed. Please check your configuration.{RESET}\n")
        sys.exit(1)
    
    try:
        # Create all collections
        success_count, failed_count = create_all_collections(db)
        
        # Verify collections
        all_verified = verify_collections(db)
        
        # Insert sample data
        if all_verified:
            insert_sample = input(f"\n{BLUE}Insert sample data? (y/n): {RESET}").lower().strip()
            if insert_sample == 'y':
                insert_sample_data(db)
        
        # Final summary
        print(f"\n{BLUE}{'='*60}{RESET}")
        if all_verified and failed_count == 0:
            print(f"{GREEN}✅ Setup completed successfully!{RESET}")
            print(f"\n{BLUE}Key Differences from Cassandra Tables:{RESET}")
            print(f"   • Collections use flexible JSON documents")
            print(f"   • No predefined schema required")
            print(f"   • Vector search enabled on select collections")
            print(f"   • Simpler API, no CQL needed")
            print(f"\n{BLUE}Next steps:{RESET}")
            print(f"   1. Start using the Data API in your application")
            print(f"   2. Add embeddings to vector-enabled collections")
            print(f"   3. Test Streamlit UI: streamlit run ui/app.py")
        else:
            print(f"{YELLOW}⚠️  Setup completed with warnings{RESET}")
            print(f"   Please check the errors above")
        print(f"{BLUE}{'='*60}{RESET}\n")
        
    except Exception as e:
        print(f"\n{RED}❌ Unexpected error: {str(e)}{RESET}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
