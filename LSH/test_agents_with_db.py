"""
Test AI Agents with Real Astra DB Data
Demonstrates agents connected to live database
"""

import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database.astra_helper import get_db_helper
from src.agents.nutrition_validation_agent import NutritionValidationAgent

async def test_nutrition_validation():
    """Test nutrition validation agent with real data"""
    print("\n" + "="*60)
    print("🧪 Testing Nutrition Validation Agent with Real Data")
    print("="*60 + "\n")
    
    # Initialize
    db = get_db_helper()
    agent = NutritionValidationAgent()
    
    # Get first patient
    patients = db.get_all_patients(limit=5)
    if not patients:
        print("❌ No patients found in database")
        return
    
    patient = patients[0]
    patient_id = patient['patient_id']
    
    print(f"👤 Patient: {patient.get('name')} (ID: {patient_id})")
    print(f"   Room: {patient.get('room_number')}")
    print(f"   Allergies: {patient.get('allergies', [])}")
    print(f"   Restrictions: {patient.get('dietary_restrictions', [])}\n")
    
    # Get menu items
    menu_items = db.get_all_patients(limit=5)  # This should be menu items
    menu_items = list(db.menu_items.find({}, limit=5))
    
    if not menu_items:
        print("❌ No menu items found in database")
        return
    
    print("🍽️  Available Menu Items:")
    for item in menu_items[:3]:
        print(f"   - {item.get('name')} ({item.get('calories')} cal)")
        print(f"     Allergens: {item.get('allergens', [])}")
        print(f"     Tags: {item.get('dietary_tags', [])}\n")
    
    # Test validation with first menu item
    menu_item_id = menu_items[0]['item_id']
    
    print(f"🔍 Validating: {menu_items[0].get('name')} for {patient.get('name')}")
    print("-" * 60)
    
    # Call agent
    result = await agent.process({
        "patient_id": patient_id,
        "meal_item_ids": [menu_item_id],
        "validation_type": "full"
    })
    
    # Display results
    print(f"\n✅ Validation Result: {'SAFE' if result.get('valid') else 'UNSAFE'}")
    
    if result.get('issues'):
        print(f"\n🚨 ISSUES ({len(result['issues'])}):")
        for issue in result['issues']:
            print(f"   - {issue.get('reason')}")
    
    if result.get('warnings'):
        print(f"\n⚠️  WARNINGS ({len(result['warnings'])}):")
        for warning in result['warnings']:
            print(f"   - {warning.get('reason')}")
            print(f"     Recommendation: {warning.get('recommendation')}")
    
    if result.get('nutrition_summary'):
        summary = result['nutrition_summary']
        print(f"\n📊 Nutrition Summary:")
        print(f"   Calories: {summary.get('total_calories')} kcal")
        print(f"   Protein: {summary.get('total_protein_g', 0):.1f}g")
        print(f"   Sodium: {summary.get('total_sodium_mg')}mg")
        print(f"   Sugar: {summary.get('total_sugar_g', 0):.1f}g")
    
    print("\n" + "="*60)

async def test_meal_orders():
    """Test querying meal orders"""
    print("\n" + "="*60)
    print("📦 Testing Meal Orders Query")
    print("="*60 + "\n")
    
    db = get_db_helper()
    
    # Get today's orders
    orders = db.get_todays_orders(limit=10)
    
    if not orders:
        print("📭 No orders found for today")
        
        # Show recent orders
        all_orders = list(db.meal_orders.find({}, limit=10))
        if all_orders:
            print(f"\n📦 Recent Orders ({len(all_orders)}):")
            for order in all_orders:
                print(f"   - Patient: {order.get('patient_id')}")
                print(f"     Meal: {order.get('meal_type')}")
                print(f"     Status: {order.get('status')}")
                print(f"     Date: {order.get('order_date')}\n")
    else:
        print(f"📦 Today's Orders: {len(orders)}")
        for order in orders:
            print(f"   - {order.get('patient_id')} - {order.get('meal_type')} ({order.get('status')})")
    
    print("="*60)

async def test_evs_tasks():
    """Test EVS tasks query"""
    print("\n" + "="*60)
    print("🧹 Testing EVS Tasks Query")
    print("="*60 + "\n")
    
    db = get_db_helper()
    
    # Get pending tasks
    pending = db.get_evs_tasks_by_status("scheduled", limit=10)
    
    print(f"📋 Scheduled EVS Tasks: {len(pending)}")
    for task in pending[:5]:
        print(f"   - {task.get('task_type')} at {task.get('location')}")
        print(f"     Priority: {task.get('priority')}")
        print(f"     Description: {task.get('description')}\n")
    
    # Get available staff
    staff = db.get_available_evs_staff()
    print(f"👷 Available Staff: {len(staff)}")
    for member in staff:
        print(f"   - {member.get('name')} ({member.get('shift')} shift)")
        print(f"     Skills: {member.get('skills', [])}\n")
    
    print("="*60)

async def test_inventory():
    """Test inventory query"""
    print("\n" + "="*60)
    print("📦 Testing Inventory Query")
    print("="*60 + "\n")
    
    db = get_db_helper()
    
    # Get low inventory
    low_items = db.get_low_inventory_items()
    
    if low_items:
        print(f"⚠️  Low Inventory Items: {len(low_items)}")
        for item in low_items[:5]:
            print(f"   - {item.get('name')}: {item.get('quantity')} {item.get('unit')}")
            print(f"     Reorder Level: {item.get('reorder_level')}")
            print(f"     Category: {item.get('category')}\n")
    else:
        print("✅ All inventory levels adequate")
        
        # Show sample items
        all_items = list(db.inventory.find({}, limit=5))
        print(f"\n📦 Sample Inventory ({len(all_items)}):")
        for item in all_items:
            print(f"   - {item.get('name')}: {item.get('quantity')} {item.get('unit')}")
    
    print("="*60)

async def main():
    """Run all tests"""
    try:
        print("\n🏥 Healthcare Digital - AI Agents with Real Astra DB Data")
        print("="*60)
        
        # Test database connection
        db = get_db_helper()
        print("\n✅ Connected to Astra DB")
        
        # Run tests
        await test_nutrition_validation()
        await test_meal_orders()
        await test_evs_tasks()
        await test_inventory()
        
        print("\n✅ All tests completed!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
