"""
Astra DB Table Creation Script for Healthcare Digital System

This script creates all 11 Cassandra tables in your Astra DB database.

Prerequisites:
1. Download Secure Connect Bundle from Astra DB Console
2. Generate Application Token with Database Administrator role
3. Update .env file with credentials

Usage:
    python database/create_astra_tables.py
"""

import os
import sys
from pathlib import Path
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def get_connection():
    """Establish connection to Astra DB using secure connect bundle"""
    
    # Get credentials from environment
    token = os.getenv('ASTRA_DB_TOKEN')
    bundle_path = os.getenv('ASTRA_SECURE_BUNDLE_PATH')
    keyspace = os.getenv('ASTRA_DB_KEYSPACE', 'healthcare_digital')
    
    # Validate credentials
    if not token:
        print(f"{RED}❌ Error: ASTRA_DB_TOKEN not found in .env file{RESET}")
        return None, None
    
    if not bundle_path or not Path(bundle_path).exists():
        print(f"{RED}❌ Error: Secure Connect Bundle not found at: {bundle_path}{RESET}")
        print(f"{YELLOW}Please download it from Astra DB Console → Connect tab{RESET}")
        return None, None
    
    print(f"{BLUE}🔌 Connecting to Astra DB...{RESET}")
    print(f"   Keyspace: {keyspace}")
    print(f"   Bundle: {bundle_path}")
    
    try:
        # Create authentication provider
        auth_provider = PlainTextAuthProvider('token', token)
        
        # Create cluster connection
        cluster = Cluster(
            cloud={
                'secure_connect_bundle': bundle_path
            },
            auth_provider=auth_provider
        )
        
        # Connect to keyspace
        session = cluster.connect(keyspace)
        print(f"{GREEN}✅ Connected successfully!{RESET}\n")
        
        return cluster, session
        
    except Exception as e:
        print(f"{RED}❌ Connection failed: {str(e)}{RESET}")
        return None, None

# Define all table schemas
TABLE_SCHEMAS = {
    'patients': """
        CREATE TABLE IF NOT EXISTS patients (
            patient_id TEXT PRIMARY KEY,
            name TEXT,
            room_number TEXT,
            allergies LIST<TEXT>,
            dietary_restrictions LIST<TEXT>,
            medical_conditions LIST<TEXT>,
            preferences MAP<TEXT, TEXT>,
            cultural_requirements TEXT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
    """,
    
    'patient_dietary_profiles': """
        CREATE TABLE IF NOT EXISTS patient_dietary_profiles (
            profile_id UUID PRIMARY KEY,
            patient_id TEXT,
            calories_target INT,
            protein_target_g FLOAT,
            sodium_limit_mg INT,
            sugar_limit_g FLOAT,
            fat_limit_g FLOAT,
            texture_modification TEXT,
            fluid_restriction_ml INT,
            special_considerations TEXT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
    """,
    
    'menu_items': """
        CREATE TABLE IF NOT EXISTS menu_items (
            item_id TEXT PRIMARY KEY,
            name TEXT,
            description TEXT,
            category TEXT,
            calories INT,
            protein_g FLOAT,
            carbs_g FLOAT,
            fat_g FLOAT,
            sodium_mg INT,
            sugar_g FLOAT,
            fiber_g FLOAT,
            allergens LIST<TEXT>,
            dietary_tags LIST<TEXT>,
            cost FLOAT,
            ingredients LIST<TEXT>,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
    """,
    
    'meal_orders': """
        CREATE TABLE IF NOT EXISTS meal_orders (
            patient_id TEXT,
            order_date DATE,
            order_id UUID,
            meal_type TEXT,
            delivery_time TIMESTAMP,
            status TEXT,
            validated_by_ai BOOLEAN,
            validation_notes TEXT,
            prepared_at TIMESTAMP,
            delivered_at TIMESTAMP,
            rating INT,
            feedback TEXT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            PRIMARY KEY ((patient_id), order_date, order_id)
        ) WITH CLUSTERING ORDER BY (order_date DESC, order_id DESC)
    """,
    
    'meal_order_items': """
        CREATE TABLE IF NOT EXISTS meal_order_items (
            order_id UUID,
            item_id UUID,
            menu_item_id TEXT,
            quantity INT,
            special_instructions TEXT,
            menu_item_name TEXT,
            calories INT,
            allergens LIST<TEXT>,
            PRIMARY KEY ((order_id), item_id)
        )
    """,
    
    'evs_tasks': """
        CREATE TABLE IF NOT EXISTS evs_tasks (
            location TEXT,
            status TEXT,
            created_at TIMESTAMP,
            task_id UUID,
            task_type TEXT,
            building TEXT,
            floor INT,
            room_number TEXT,
            priority TEXT,
            priority_score FLOAT,
            description TEXT,
            patient_nearby BOOLEAN,
            isolation_required BOOLEAN,
            estimated_duration_minutes INT,
            assigned_to TEXT,
            assigned_at TIMESTAMP,
            completed_at TIMESTAMP,
            completed_by TEXT,
            quality_rating INT,
            quality_notes TEXT,
            equipment_needed LIST<TEXT>,
            supplies_used MAP<TEXT, INT>,
            updated_at TIMESTAMP,
            PRIMARY KEY ((location, status), created_at, task_id)
        ) WITH CLUSTERING ORDER BY (created_at DESC, task_id DESC)
    """,
    
    'evs_staff': """
        CREATE TABLE IF NOT EXISTS evs_staff (
            staff_id TEXT PRIMARY KEY,
            name TEXT,
            employee_number TEXT,
            shift TEXT,
            status TEXT,
            skills LIST<TEXT>,
            certifications LIST<TEXT>,
            training_completed LIST<TEXT>,
            current_location TEXT,
            availability_status TEXT,
            tasks_completed_today INT,
            avg_task_duration_minutes FLOAT,
            quality_score FLOAT,
            last_break_time TIMESTAMP,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
    """,
    
    'agent_activities': """
        CREATE TABLE IF NOT EXISTS agent_activities (
            agent_name TEXT,
            timestamp TIMESTAMP,
            activity_id UUID,
            agent_type TEXT,
            action_type TEXT,
            input_data TEXT,
            output_data TEXT,
            success BOOLEAN,
            error_message TEXT,
            execution_time_ms INT,
            user_id TEXT,
            session_id TEXT,
            PRIMARY KEY ((agent_name), timestamp, activity_id)
        ) WITH CLUSTERING ORDER BY (timestamp DESC, activity_id DESC)
    """,
    
    'system_audit_logs': """
        CREATE TABLE IF NOT EXISTS system_audit_logs (
            resource_type TEXT,
            timestamp TIMESTAMP,
            log_id UUID,
            user_id TEXT,
            action TEXT,
            resource_id TEXT,
            action_details TEXT,
            ip_address TEXT,
            user_agent TEXT,
            success BOOLEAN,
            error_message TEXT,
            PRIMARY KEY ((resource_type), timestamp, log_id)
        ) WITH CLUSTERING ORDER BY (timestamp DESC, log_id DESC)
    """,
    
    'food_inventory': """
        CREATE TABLE IF NOT EXISTS food_inventory (
            ingredient_id TEXT PRIMARY KEY,
            name TEXT,
            category TEXT,
            quantity FLOAT,
            unit TEXT,
            reorder_level FLOAT,
            expiration_date DATE,
            batch_number TEXT,
            supplier TEXT,
            storage_location TEXT,
            temperature_requirement TEXT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
    """,
    
    'production_schedules': """
        CREATE TABLE IF NOT EXISTS production_schedules (
            date DATE,
            meal_type TEXT,
            schedule_id UUID,
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
        ) WITH CLUSTERING ORDER BY (meal_type ASC, schedule_id DESC)
    """
}

def create_all_tables(session):
    """Create all tables in Astra DB"""
    
    print(f"{BLUE}📝 Creating tables...{RESET}\n")
    
    success_count = 0
    failed_count = 0
    
    for table_name, schema in TABLE_SCHEMAS.items():
        try:
            print(f"   Creating table: {table_name}...", end=' ')
            session.execute(schema)
            print(f"{GREEN}✅{RESET}")
            success_count += 1
        except Exception as e:
            print(f"{RED}❌ Failed: {str(e)}{RESET}")
            failed_count += 1
    
    print(f"\n{BLUE}📊 Summary:{RESET}")
    print(f"   {GREEN}✅ Successfully created: {success_count} tables{RESET}")
    if failed_count > 0:
        print(f"   {RED}❌ Failed: {failed_count} tables{RESET}")
    
    return success_count, failed_count

def verify_tables(session, keyspace):
    """Verify that all tables were created successfully"""
    
    print(f"\n{BLUE}🔍 Verifying tables...{RESET}\n")
    
    # Query system schema to get list of tables
    query = """
        SELECT table_name 
        FROM system_schema.tables 
        WHERE keyspace_name = %s
    """
    
    try:
        rows = session.execute(query, [keyspace])
        existing_tables = [row.table_name for row in rows]
        
        print(f"   Found {len(existing_tables)} tables in keyspace '{keyspace}':")
        for table in sorted(existing_tables):
            print(f"   {GREEN}✓{RESET} {table}")
        
        # Check if all expected tables exist
        expected_tables = set(TABLE_SCHEMAS.keys())
        actual_tables = set(existing_tables)
        missing_tables = expected_tables - actual_tables
        
        if missing_tables:
            print(f"\n   {YELLOW}⚠️  Missing tables: {', '.join(missing_tables)}{RESET}")
            return False
        else:
            print(f"\n   {GREEN}✅ All tables verified successfully!{RESET}")
            return True
            
    except Exception as e:
        print(f"{RED}❌ Verification failed: {str(e)}{RESET}")
        return False

def main():
    """Main execution function"""
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}🏥 Healthcare Digital - Astra DB Table Creation{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    # Connect to Astra DB
    cluster, session = get_connection()
    
    if not cluster or not session:
        print(f"\n{RED}❌ Setup failed. Please check your configuration.{RESET}\n")
        sys.exit(1)
    
    try:
        # Create all tables
        success_count, failed_count = create_all_tables(session)
        
        # Verify tables
        keyspace = os.getenv('ASTRA_DB_KEYSPACE', 'healthcare_digital')
        all_verified = verify_tables(session, keyspace)
        
        # Final summary
        print(f"\n{BLUE}{'='*60}{RESET}")
        if all_verified and failed_count == 0:
            print(f"{GREEN}✅ Setup completed successfully!{RESET}")
            print(f"\n{BLUE}Next steps:{RESET}")
            print(f"   1. Run: python database/init_astra_db.py")
            print(f"   2. This will create vector collections and insert sample data")
        else:
            print(f"{YELLOW}⚠️  Setup completed with warnings{RESET}")
            print(f"   Please check the errors above")
        print(f"{BLUE}{'='*60}{RESET}\n")
        
    except Exception as e:
        print(f"\n{RED}❌ Unexpected error: {str(e)}{RESET}\n")
        sys.exit(1)
    finally:
        # Close connection
        if cluster:
            cluster.shutdown()
            print(f"{BLUE}🔌 Connection closed{RESET}\n")

if __name__ == "__main__":
    main()
