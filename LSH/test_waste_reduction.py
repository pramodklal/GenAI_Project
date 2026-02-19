"""
Test script for Waste Reduction Agent with real Astra DB data
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.agents.waste_reduction_agent import WasteReductionAgent
from database.astra_helper import get_db_helper


async def test_waste_reduction():
    """Test the Waste Reduction Agent with real database data"""
    print("=" * 80)
    print("WASTE REDUCTION AGENT TEST - Real Astra DB Data")
    print("=" * 80)
    
    # Initialize agent
    agent = WasteReductionAgent()
    db = get_db_helper()
    
    # Test 1: Analyze waste risks
    print("\n1. ANALYZING WASTE RISKS AND INVENTORY")
    print("-" * 80)
    
    result = await agent.process({
        "threshold_days": 3,
        "generate_actions": True
    })
    
    if result.get("success"):
        print(f"\n   ✅ Waste analysis completed successfully")
        
        # Show at-risk items
        at_risk_items = result.get("at_risk_items", [])
        print(f"\n   At-Risk Inventory Items: {len(at_risk_items)}")
        
        for i, item in enumerate(at_risk_items[:5], 1):
            print(f"\n   {i}. {item.get('item_name', 'Unknown')}")
            print(f"      Quantity: {item.get('quantity', 0)} {item.get('unit', 'units')}")
            print(f"      Reorder Point: {item.get('reorder_point', 0)}")
            print(f"      Risk Level: {item.get('risk_level', 'unknown').upper()}")
            print(f"      Unit Cost: ${item.get('unit_cost', 0):.2f}")
            print(f"      Reason: {item.get('risk_reason', 'N/A')}")
        
        # Show analysis
        analysis = result.get("analysis", {})
        risk_breakdown = analysis.get("risk_breakdown", {})
        
        print(f"\n   Risk Breakdown:")
        print(f"      High Risk: {risk_breakdown.get('high_risk_count', 0)} items")
        print(f"      Medium Risk: {risk_breakdown.get('medium_risk_count', 0)} items")
        print(f"      Low Risk: {risk_breakdown.get('low_risk_count', 0)} items")
        print(f"      Total At Risk: {risk_breakdown.get('total_at_risk', 0)} items")
        
        # Show actionable categories
        categories = analysis.get("actionable_categories", {})
        print(f"\n   Actionable Categories:")
        print(f"      Use in Next Meal: {categories.get('use_in_next_meal', 0)} items")
        print(f"      Freeze Candidates: {categories.get('freeze_candidates', 0)} items")
        print(f"      Reorder Needed: {categories.get('reorder_needed', 0)} items")
        
        # Show waste prevention potential
        potential = analysis.get("waste_prevention_potential", {})
        print(f"\n   Waste Prevention Potential:")
        print(f"      Items Savable: {potential.get('items_savable', 0)}")
        print(f"      Estimated Value Savable: ${potential.get('estimated_value_savable', 0):.2f}")
        
        # Show estimated waste value
        print(f"\n   Estimated Waste Value: ${result.get('estimated_waste_value', 0):.2f}")
        
        # Show recommended actions
        actions = analysis.get("recommended_actions", [])
        if actions:
            print(f"\n   Recommended Actions ({len(actions)} total):")
            
            for i, action in enumerate(actions, 1):
                print(f"\n   {i}. [{action.get('priority', 'medium').upper()}] {action.get('description')}")
                print(f"      Type: {action.get('type')}")
                
                impact = action.get("estimated_impact", {})
                print(f"      Impact:")
                for key, value in impact.items():
                    print(f"         - {key.replace('_', ' ').title()}: {value}")
                
                print(f"      Implementation: {action.get('implementation')}")
    else:
        print(f"   ❌ Error: {result.get('error')}")
    
    # Test 2: Show historical waste analysis
    print("\n\n2. HISTORICAL WASTE ANALYSIS")
    print("-" * 80)
    
    waste_analysis = result.get("waste_analysis", {})
    if waste_analysis:
        print(f"\n   Total Waste: {waste_analysis.get('total_waste_kg', 0):.2f} kg")
        print(f"   Total Meals Produced: {waste_analysis.get('total_meals_produced', 0)}")
        print(f"   Waste Percentage: {waste_analysis.get('waste_percentage', 0):.2f}%")
        print(f"   Average Waste per Schedule: {waste_analysis.get('average_waste_per_schedule', 0):.2f} kg")
        
        # Show waste by meal type
        waste_by_meal = waste_analysis.get("waste_by_meal_type", {})
        if waste_by_meal:
            print(f"\n   Waste by Meal Type:")
            for meal_type, waste_kg in waste_by_meal.items():
                print(f"      {meal_type.title()}: {waste_kg:.2f} kg")
        
        # Show high-waste meals
        high_waste = waste_analysis.get("high_waste_meals", [])
        if high_waste:
            print(f"\n   Top Waste-Producing Meal Types:")
            for i, item in enumerate(high_waste, 1):
                print(f"      {i}. {item['meal_type'].title()}: {item['waste_kg']:.2f} kg")
    
    # Test 3: Show current inventory status
    print("\n\n3. CURRENT INVENTORY STATUS")
    print("-" * 80)
    
    all_inventory = db.get_low_inventory_items()
    print(f"\n   Total Inventory Items: {len(all_inventory)}")
    
    # Group by category
    by_category = {}
    for item in all_inventory:
        category = item.get("category", "Other")
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(item)
    
    print(f"\n   Inventory by Category:")
    for category, items in by_category.items():
        total_value = sum(
            item.get("quantity", 0) * item.get("unit_cost", 0)
            for item in items
        )
        print(f"      {category}: {len(items)} items (${total_value:.2f} value)")
    
    # Test 4: Show demand forecast
    print("\n\n4. DEMAND FORECAST")
    print("-" * 80)
    
    demand_insights = analysis.get("demand_insights", {})
    predicted_meals = demand_insights.get("predicted_meals_tomorrow", 0)
    current_waste_rate = demand_insights.get("current_waste_rate", "0%")
    
    print(f"\n   Predicted Meals Tomorrow: {predicted_meals}")
    print(f"   Current Waste Rate: {current_waste_rate}")
    
    # Show today's orders
    todays_orders = db.get_todays_orders()
    print(f"\n   Today's Orders: {len(todays_orders)}")
    
    # Count by meal time
    by_meal_time = {}
    for order in todays_orders:
        meal_time = order.get("meal_time", "unknown")
        by_meal_time[meal_time] = by_meal_time.get(meal_time, 0) + 1
    
    if by_meal_time:
        print(f"\n   Orders by Meal Time:")
        for meal_time, count in by_meal_time.items():
            print(f"      {meal_time.title()}: {count} orders")
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
    print("=" * 80)
    
    # Summary
    print("\n📊 SUMMARY:")
    print(f"   - {len(at_risk_items)} items at risk of waste")
    print(f"   - ${result.get('estimated_waste_value', 0):.2f} potential waste value")
    print(f"   - {len(actions)} recommended actions generated")
    print(f"   - {waste_analysis.get('waste_percentage', 0):.2f}% current waste rate")
    print(f"   - {predicted_meals} meals predicted for tomorrow")


if __name__ == "__main__":
    asyncio.run(test_waste_reduction())
