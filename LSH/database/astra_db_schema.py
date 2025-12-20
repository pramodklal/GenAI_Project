"""
Astra DB Schema Creation Script for Healthcare Digital
Creates all 11 Cassandra tables with proper schema

Run this script to automatically create all tables in your Astra DB database.
"""

import os
import sys
from dotenv import load_dotenv
from astrapy import DataAPIClient
import time

# Load environment variables
load_dotenv()

class AstraDBSchemaCreator:
    """Creates all tables and collections in Astra DB"""
    
    def __init__(self):
        self.token = os.getenv('ASTRA_DB_TOKEN')
        self.api_endpoint = os.getenv('ASTRA_DB_API_ENDPOINT')
        self.keyspace = os.getenv('ASTRA_DB_KEYSPACE', 'healthcare_digital')
        
        if not self.token or not self.api_endpoint:
            raise ValueError("ASTRA_DB_TOKEN and ASTRA_DB_API_ENDPOINT are required in .env file")
        
        # Initialize client
        self.client = DataAPIClient(self.token)
        self.database = self.client.get_database(self.api_endpoint)
        
        print(f"✅ Connected to Astra DB")
        print(f"   Endpoint: {self.api_endpoint}")
        print(f"   Keyspace: {self.keyspace}")
    
    def get_table_schemas(self):
        """Return all table creation CQL statements"""
        return {
            "patients": """
                CREATE TABLE IF NOT EXISTS {keyspace}.patients (
                    patient_id TEXT PRIMARY KEY,
                    name TEXT,
                    room_number TEXT,
                    admission_date TIMESTAMP,
                    discharge_date TIMESTAMP,
                    allergies LIST<TEXT>,
                    dietary_restrictions LIST<TEXT>,
                    medical_conditions LIST<TEXT>,
                    preferences MAP<TEXT, TEXT>,
                    cultural_requirements TEXT,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """,
            
            "patient_dietary_profiles": """
                CREATE TABLE IF NOT EXISTS {keyspace}.patient_dietary_profiles (
                    profile_id UUID PRIMARY KEY,
                    patient_id TEXT,
                    daily_calories_target INT,
                    daily_protein_g FLOAT,
                    daily_sodium_mg FLOAT,
                    daily_sugar_g FLOAT,
                    daily_fat_g FLOAT,
                    texture_modification TEXT,
                    fluid_restriction_ml INT,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    created_by TEXT
                )
            """,
            
            "patient_dietary_profiles_index": """
                CREATE INDEX IF NOT EXISTS ON {keyspace}.patient_dietary_profiles (patient_id)
            """,
            
            "menu_items": """
                CREATE TABLE IF NOT EXISTS {keyspace}.menu_items (
                    item_id TEXT PRIMARY KEY,
                    name TEXT,
                    description TEXT,
                    category TEXT,
                    calories INT,
                    protein_g FLOAT,
                    carbs_g FLOAT,
                    fat_g FLOAT,
                    sodium_mg FLOAT,
                    sugar_g FLOAT,
                    fiber_g FLOAT,
                    allergens LIST<TEXT>,
                    dietary_tags LIST<TEXT>,
                    available BOOLEAN,
                    seasonal BOOLEAN,
                    cost FLOAT,
                    ingredients LIST<TEXT>,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """,
            
            "meal_orders": """
                CREATE TABLE IF NOT EXISTS {keyspace}.meal_orders (
                    order_id TEXT,
                    patient_id TEXT,
                    meal_type TEXT,
                    order_date TIMESTAMP,
                    delivery_time TIMESTAMP,
                    status TEXT,
                    validated_by_ai BOOLEAN,
                    validation_notes TEXT,
                    prepared_at TIMESTAMP,
                    delivered_at TIMESTAMP,
                    delivered_by TEXT,
                    rating INT,
                    feedback TEXT,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    PRIMARY KEY ((patient_id), order_date, order_id)
                ) WITH CLUSTERING ORDER BY (order_date DESC)
            """,
            
            "meal_order_items": """
                CREATE TABLE IF NOT EXISTS {keyspace}.meal_order_items (
                    order_id TEXT,
                    item_id TEXT,
                    menu_item_id TEXT,
                    quantity INT,
                    special_instructions TEXT,
                    menu_item_name TEXT,
                    calories INT,
                    allergens LIST<TEXT>,
                    PRIMARY KEY ((order_id), item_id)
                )
            """,
            
            "evs_tasks": """
                CREATE TABLE IF NOT EXISTS {keyspace}.evs_tasks (
                    task_id TEXT,
                    location TEXT,
                    task_type TEXT,
                    building TEXT,
                    floor TEXT,
                    room_number TEXT,
                    priority TEXT,
                    status TEXT,
                    priority_score FLOAT,
                    description TEXT,
                    patient_nearby BOOLEAN,
                    isolation_required BOOLEAN,
                    estimated_duration_minutes INT,
                    assigned_to TEXT,
                    assigned_at TIMESTAMP,
                    assigned_by TEXT,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    actual_duration_minutes INT,
                    quality_check_passed BOOLEAN,
                    quality_checked_by TEXT,
                    quality_notes TEXT,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    created_by TEXT,
                    PRIMARY KEY ((location, status), created_at, task_id)
                ) WITH CLUSTERING ORDER BY (created_at DESC)
            """,
            
            "evs_staff": """
                CREATE TABLE IF NOT EXISTS {keyspace}.evs_staff (
                    staff_id TEXT PRIMARY KEY,
                    name TEXT,
                    employee_number TEXT,
                    shift TEXT,
                    status TEXT,
                    skills LIST<TEXT>,
                    certifications LIST<TEXT>,
                    training_completed LIST<TEXT>,
                    current_location TEXT,
                    available BOOLEAN,
                    current_task_id TEXT,
                    tasks_completed_today INT,
                    average_task_duration_minutes FLOAT,
                    quality_score FLOAT,
                    hire_date TIMESTAMP,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """,
            
            "agent_activities": """
                CREATE TABLE IF NOT EXISTS {keyspace}.agent_activities (
                    activity_id UUID,
                    agent_name TEXT,
                    agent_type TEXT,
                    action_type TEXT,
                    input_data TEXT,
                    output_data TEXT,
                    success BOOLEAN,
                    error_message TEXT,
                    execution_time_ms INT,
                    user_id TEXT,
                    session_id TEXT,
                    timestamp TIMESTAMP,
                    PRIMARY KEY ((agent_name), timestamp, activity_id)
                ) WITH CLUSTERING ORDER BY (timestamp DESC)
            """,
            
            "system_audit_logs": """
                CREATE TABLE IF NOT EXISTS {keyspace}.system_audit_logs (
                    log_id UUID,
                    user_id TEXT,
                    action TEXT,
                    resource_type TEXT,
                    resource_id TEXT,
                    action_details TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    success BOOLEAN,
                    error_message TEXT,
                    timestamp TIMESTAMP,
                    PRIMARY KEY ((resource_type), timestamp, log_id)
                ) WITH CLUSTERING ORDER BY (timestamp DESC)
            """,
            
            "food_inventory": """
                CREATE TABLE IF NOT EXISTS {keyspace}.food_inventory (
                    ingredient_id TEXT PRIMARY KEY,
                    name TEXT,
                    category TEXT,
                    quantity FLOAT,
                    unit TEXT,
                    reorder_level FLOAT,
                    expiration_date TIMESTAMP,
                    batch_number TEXT,
                    supplier TEXT,
                    storage_location TEXT,
                    temperature_requirement TEXT,
                    last_updated TIMESTAMP,
                    updated_by TEXT
                )
            """,
            
            "production_schedules": """
                CREATE TABLE IF NOT EXISTS {keyspace}.production_schedules (
                    schedule_id TEXT,
                    date TIMESTAMP,
                    meal_type TEXT,
                    estimated_meals INT,
                    forecasted_by_ai BOOLEAN,
                    confidence_score FLOAT,
                    actual_meals_produced INT,
                    waste_amount_kg FLOAT,
                    staff_assigned LIST<TEXT>,
                    supervisor TEXT,
                    status TEXT,
                    notes TEXT,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    PRIMARY KEY ((date), meal_type, schedule_id)
                )
            """
        }
    
    def create_tables(self):
        """Create all Cassandra tables"""
        print("\n" + "=" * 60)
        print("📊 Creating Cassandra Tables")
        print("=" * 60)
        
        schemas = self.get_table_schemas()
        created = []
        failed = []
        
        for table_name, schema_cql in schemas.items():
            try:
                # Format with keyspace
                formatted_cql = schema_cql.format(keyspace=self.keyspace)
                
                # Execute using Data API
                self.database.command(
                    body={
                        "executeCql": formatted_cql
                    }
                )
                
                created.append(table_name)
                print(f"   ✅ {table_name}")
                time.sleep(0.5)  # Small delay to avoid rate limits
                
            except Exception as e:
                error_msg = str(e)
                if "already exists" in error_msg.lower():
                    print(f"   📌 {table_name} (already exists)")
                else:
                    failed.append((table_name, error_msg))
                    print(f"   ❌ {table_name}: {error_msg}")
        
        # Summary
        print("\n" + "-" * 60)
        print(f"✅ Created: {len(created)} tables")
        if failed:
            print(f"❌ Failed: {len(failed)} tables")
            for name, error in failed:
                print(f"   - {name}: {error}")
        
        return len(failed) == 0
    
    def get_vector_collections(self):
        """Return vector collection configurations"""
        return [
            {
                "name": "meal_embeddings",
                "dimension": 1536,
                "description": "Semantic search for meal recommendations",
                "metadata": ["item_id", "name", "category", "calories", "dietary_tags"]
            },
            {
                "name": "patient_preferences",
                "dimension": 1536,
                "description": "Patient meal preference learning",
                "metadata": ["patient_id", "preference_text", "dietary_restrictions"]
            },
            {
                "name": "evs_task_history",
                "dimension": 768,
                "description": "EVS task similarity and duration prediction",
                "metadata": ["task_id", "task_type", "location", "duration_minutes"]
            },
            {
                "name": "agent_conversations",
                "dimension": 1536,
                "description": "Agent memory and conversation context",
                "metadata": ["agent_name", "user_id", "session_id", "message"]
            },
            {
                "name": "clinical_documents",
                "dimension": 1536,
                "description": "RAG for clinical guidelines and SOPs",
                "metadata": ["document_id", "title", "document_type", "category"]
            }
        ]
    
    def create_vector_collections(self):
        """Create vector search collections"""
        print("\n" + "=" * 60)
        print("🔍 Creating Vector Search Collections")
        print("=" * 60)
        
        collections = self.get_vector_collections()
        created = []
        existing = []
        failed = []
        
        for config in collections:
            try:
                collection = self.database.create_collection(
                    name=config["name"],
                    dimension=config["dimension"],
                    metric="cosine"
                )
                created.append(config["name"])
                print(f"   ✅ {config['name']} ({config['dimension']}D)")
                print(f"      └─ {config['description']}")
                time.sleep(0.5)
                
            except Exception as e:
                error_msg = str(e)
                if "already exists" in error_msg.lower() or "COLLECTION_ALREADY_EXISTS" in error_msg:
                    existing.append(config["name"])
                    print(f"   📌 {config['name']} ({config['dimension']}D) - already exists")
                else:
                    failed.append((config["name"], error_msg))
                    print(f"   ❌ {config['name']}: {error_msg}")
        
        # Summary
        print("\n" + "-" * 60)
        print(f"✅ Created: {len(created)} collections")
        print(f"📌 Already existed: {len(existing)} collections")
        if failed:
            print(f"❌ Failed: {len(failed)} collections")
            for name, error in failed:
                print(f"   - {name}: {error}")
        
        return len(failed) == 0
    
    def verify_setup(self):
        """Verify tables and collections were created"""
        print("\n" + "=" * 60)
        print("🔍 Verifying Setup")
        print("=" * 60)
        
        try:
            # List collections
            collections = self.database.list_collection_names()
            print(f"\n📊 Vector Collections ({len(collections)}):")
            for col in collections:
                print(f"   ✓ {col}")
            
            # Note: Listing tables via Data API is not straightforward
            # User can verify in Astra CQL Console
            print(f"\n💡 To verify Cassandra tables, use Astra CQL Console:")
            print(f"   DESCRIBE TABLES;")
            
            return True
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False
    
    def insert_sample_data(self):
        """Insert sample data for testing"""
        print("\n" + "=" * 60)
        print("📝 Inserting Sample Data")
        print("=" * 60)
        
        sample_data = {
            "patient": """
                INSERT INTO {keyspace}.patients (
                    patient_id, name, room_number, allergies, dietary_restrictions,
                    medical_conditions, created_at, updated_at
                ) VALUES (
                    'PAT001', 'John Doe', '301', ['peanuts', 'shellfish'],
                    ['low_sodium', 'diabetic'], ['diabetes', 'hypertension'],
                    toTimestamp(now()), toTimestamp(now())
                )
            """,
            
            "menu_item": """
                INSERT INTO {keyspace}.menu_items (
                    item_id, name, description, category, calories, protein_g,
                    sodium_mg, allergens, dietary_tags, available, created_at, updated_at
                ) VALUES (
                    'MEAL001', 'Grilled Chicken Breast', 'Lean protein with herbs',
                    'entree', 250, 35.0, 180.0, [], ['low_sodium', 'high_protein'],
                    true, toTimestamp(now()), toTimestamp(now())
                )
            """,
            
            "evs_staff": """
                INSERT INTO {keyspace}.evs_staff (
                    staff_id, name, employee_number, shift, status, skills,
                    available, tasks_completed_today, hire_date, created_at, updated_at
                ) VALUES (
                    'EMP001', 'Jane Smith', 'EMP001', 'morning', 'active',
                    ['room_cleaning', 'terminal_cleaning'], true, 0,
                    toTimestamp(now()), toTimestamp(now()), toTimestamp(now())
                )
            """,
            
            "evs_task": """
                INSERT INTO {keyspace}.evs_tasks (
                    task_id, location, status, task_type, priority, description,
                    patient_nearby, estimated_duration_minutes, created_at,
                    updated_at, created_by
                ) VALUES (
                    'TASK001', 'Room 301', 'pending', 'room_cleaning', 'high',
                    'Post-discharge cleaning required', false, 30,
                    toTimestamp(now()), toTimestamp(now()), 'SYSTEM'
                )
            """,
            
            "inventory": """
                INSERT INTO {keyspace}.food_inventory (
                    ingredient_id, name, category, quantity, unit, reorder_level,
                    expiration_date, storage_location, last_updated, updated_by
                ) VALUES (
                    'ING001', 'Chicken Breast', 'protein', 50.0, 'kg', 10.0,
                    toTimestamp(now()), 'Walk-in Freezer 1', toTimestamp(now()), 'SYSTEM'
                )
            """
        }
        
        inserted = []
        failed = []
        
        for name, cql in sample_data.items():
            try:
                formatted_cql = cql.format(keyspace=self.keyspace)
                self.database.command(body={"executeCql": formatted_cql})
                inserted.append(name)
                print(f"   ✅ Sample {name}")
            except Exception as e:
                failed.append((name, str(e)))
                print(f"   ❌ Sample {name}: {str(e)}")
        
        print("\n" + "-" * 60)
        print(f"✅ Inserted: {len(inserted)} samples")
        if failed:
            print(f"❌ Failed: {len(failed)} samples")
        
        return len(failed) == 0

def main():
    """Main execution function"""
    print("\n" + "=" * 70)
    print("🚀 Healthcare Digital - Astra DB Schema Setup")
    print("=" * 70)
    
    try:
        # Initialize schema creator
        creator = AstraDBSchemaCreator()
        
        # Create tables
        tables_success = creator.create_tables()
        
        # Create vector collections
        collections_success = creator.create_vector_collections()
        
        # Verify setup
        creator.verify_setup()
        
        # Ask about sample data
        print("\n" + "=" * 70)
        response = input("Would you like to insert sample data for testing? (y/n): ")
        if response.lower() == 'y':
            creator.insert_sample_data()
        
        # Final summary
        print("\n" + "=" * 70)
        print("🎉 Setup Complete!")
        print("=" * 70)
        
        if tables_success and collections_success:
            print("\n✅ Your Astra DB is ready to use!")
            print("\n📋 What was created:")
            print("   • 11 Cassandra tables for structured data")
            print("   • 5 Vector collections for AI features")
            if response.lower() == 'y':
                print("   • Sample data for testing")
            
            print("\n🚀 Next Steps:")
            print("   1. Verify in Astra console: https://astra.datastax.com/")
            print("   2. Run Streamlit app: streamlit run ui/app.py")
            print("   3. Test agents: python examples/langgraph_workflow.py")
            
            print("\n💡 View your data:")
            print("   - CQL Console: SELECT * FROM patients;")
            print("   - Vector search: Use meal_embeddings collection")
        else:
            print("\n⚠️ Setup completed with some errors")
            print("   Please check the error messages above")
            print("   You may need to create some tables manually in CQL Console")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Setup failed: {str(e)}")
        print("\n🔧 Troubleshooting:")
        print("   1. Check your .env file has correct values:")
        print("      - ASTRA_DB_TOKEN")
        print("      - ASTRA_DB_API_ENDPOINT")
        print("   2. Verify your database is active in Astra console")
        print("   3. Ensure you have admin permissions on the database")
        return 1

if __name__ == "__main__":
    sys.exit(main())
