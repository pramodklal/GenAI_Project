"""
Healthcare Digital - Quick Start Guide

This script demonstrates the basic setup and usage of the agentic AI system.
"""

import asyncio
from datetime import datetime
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mcp_servers import MealOrderMCPServer, FoodProductionMCPServer, EVSTaskMCPServer
from agents import NutritionValidationAgent, WasteReductionAgent, EVSTaskPrioritizationAgent


async def demo_meal_order_agent():
    """Demonstrate meal order validation with nutrition agent."""
    print("\n" + "="*60)
    print("DEMO 1: Meal Order Validation Agent")
    print("="*60)
    
    # Initialize MCP server
    meal_mcp = MealOrderMCPServer()
    
    # Initialize agent
    nutrition_agent = NutritionValidationAgent()
    nutrition_agent.register_mcp_server("meal_order", meal_mcp)
    
    # Test meal order validation
    print("\n📋 Testing meal order validation...")
    result = await nutrition_agent.process({
        "patient_id": "P12345",
        "meal_items": ["grilled_chicken_salad", "fruit_cup"],
        "validation_type": "full"
    })
    
    print(f"\n✅ Validation Result:")
    print(f"   Valid: {result.get('valid')}")
    print(f"   Issues: {len(result.get('issues', []))}")
    print(f"   Warnings: {len(result.get('warnings', []))}")
    
    if result.get('nutrition_summary'):
        summary = result['nutrition_summary']
        print(f"\n📊 Nutrition Summary:")
        print(f"   Calories: {summary.get('total_calories')}")
        print(f"   Protein: {summary.get('total_protein_g')}g")
        print(f"   Sodium: {summary.get('total_sodium_mg')}mg")
    
    if result.get('recommendations'):
        print(f"\n💡 Recommendations: {len(result['recommendations'])} alternatives suggested")


async def demo_waste_reduction_agent():
    """Demonstrate waste reduction agent."""
    print("\n" + "="*60)
    print("DEMO 2: Waste Reduction Agent")
    print("="*60)
    
    # Initialize MCP server
    food_production_mcp = FoodProductionMCPServer()
    
    # Initialize agent
    waste_agent = WasteReductionAgent()
    waste_agent.register_mcp_server("food_production", food_production_mcp)
    
    # Analyze waste risks
    print("\n🔍 Analyzing waste risks...")
    result = await waste_agent.process({
        "date": datetime.utcnow().isoformat(),
        "threshold_days": 3,
        "generate_actions": True
    })
    
    if result.get('success'):
        at_risk = result.get('at_risk_items', [])
        analysis = result.get('analysis', {})
        
        print(f"\n⚠️  Items at Risk: {len(at_risk)}")
        
        if at_risk:
            print("\nSample items:")
            for item in at_risk[:3]:
                print(f"   - {item['item']}: {item['days_until_expiration']} days left")
        
        actions = analysis.get('recommended_actions', [])
        if actions:
            print(f"\n📋 Recommended Actions: {len(actions)}")
            for action in actions[:2]:
                print(f"   - [{action['priority']}] {action['description']}")


async def demo_evs_prioritization_agent():
    """Demonstrate EVS task prioritization agent."""
    print("\n" + "="*60)
    print("DEMO 3: EVS Task Prioritization Agent")
    print("="*60)
    
    # Initialize MCP server
    evs_mcp = EVSTaskMCPServer()
    
    # Initialize agent
    evs_agent = EVSTaskPrioritizationAgent()
    evs_agent.register_mcp_server("evs_task_management", evs_mcp)
    
    # Prioritize tasks
    print("\n📊 Prioritizing EVS tasks...")
    result = await evs_agent.process({
        "location": None,
        "include_assigned": False
    })
    
    if result.get('success'):
        tasks = result.get('prioritized_tasks', [])
        schedule = result.get('recommended_schedule', {})
        
        print(f"\n📋 Total Tasks: {len(tasks)}")
        
        if tasks:
            highest = result.get('highest_priority')
            if highest:
                print(f"\n🔴 Highest Priority Task:")
                print(f"   Location: {highest.get('location')}")
                print(f"   Type: {highest.get('task_type')}")
                print(f"   Score: {highest.get('priority_score')}")
        
        immediate = schedule.get('immediate_tasks', {})
        print(f"\n⚡ Immediate Tasks: {immediate.get('count', 0)}")
        print(f"   Action: {immediate.get('recommended_action')}")


async def demo_mcp_servers():
    """Demonstrate direct MCP server usage."""
    print("\n" + "="*60)
    print("DEMO 4: Direct MCP Server Calls")
    print("="*60)
    
    # Test Meal Order MCP
    print("\n1️⃣ Meal Order MCP Server")
    meal_mcp = MealOrderMCPServer()
    
    endpoints = meal_mcp.list_endpoints()
    print(f"   Available Endpoints: {len(endpoints)}")
    
    result = meal_mcp.call_endpoint(
        "get_patient_dietary_restrictions",
        {"patient_id": "P12345"}
    )
    
    if result.get('success'):
        data = result['data']
        print(f"   ✅ Retrieved restrictions for patient")
        print(f"      Allergies: {', '.join(data.get('allergies', []))}")
        print(f"      Diet Type: {data.get('dietary_type')}")
    
    # Test Food Production MCP
    print("\n2️⃣ Food Production MCP Server")
    food_mcp = FoodProductionMCPServer()
    
    result = food_mcp.call_endpoint(
        "get_demand_forecast",
        {"date": datetime.utcnow().isoformat()}
    )
    
    if result.get('success'):
        data = result['data']
        forecast = data.get('forecast', {})
        print(f"   ✅ Demand forecast retrieved")
        print(f"      Breakfast: {forecast.get('breakfast', 0)} meals")
        print(f"      Lunch: {forecast.get('lunch', 0)} meals")
        print(f"      Dinner: {forecast.get('dinner', 0)} meals")
    
    # Test EVS Task MCP
    print("\n3️⃣ EVS Task MCP Server")
    evs_mcp = EVSTaskMCPServer()
    
    result = evs_mcp.call_endpoint(
        "get_pending_tasks",
        {}
    )
    
    if result.get('success'):
        data = result['data']
        print(f"   ✅ Retrieved pending tasks")
        print(f"      Total Pending: {data.get('total_pending', 0)}")
        by_priority = data.get('by_priority', {})
        print(f"      Critical: {by_priority.get('critical', 0)}")
        print(f"      High: {by_priority.get('high', 0)}")


async def main():
    """Run all demos."""
    print("\n" + "="*70)
    print(" Healthcare Digital - Agentic AI System Demo")
    print("="*70)
    print("\nThis demo showcases the core components of the system:")
    print("  • MCP Servers for tool access")
    print("  • Specialized agents for different domains")
    print("  • Agent-MCP integration patterns")
    
    try:
        # Run demos
        await demo_meal_order_agent()
        await demo_waste_reduction_agent()
        await demo_evs_prioritization_agent()
        await demo_mcp_servers()
        
        print("\n" + "="*70)
        print("✅ All demos completed successfully!")
        print("="*70)
        
        print("\n📚 Next Steps:")
        print("   1. Review the architecture: docs/ARCHITECTURE.md")
        print("   2. Run the multi-agent workflow: python examples/multi_agent_workflow.py")
        print("   3. Customize agents for your use case")
        print("   4. Configure Azure/GitHub credentials for production")
        
    except Exception as e:
        print(f"\n❌ Error running demos: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    """
    Run this quick start demo:
    
        python quickstart.py
    
    This demonstrates the core capabilities without requiring
    external dependencies or credentials.
    """
    asyncio.run(main())
