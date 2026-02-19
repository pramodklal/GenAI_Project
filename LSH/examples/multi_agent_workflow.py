"""
Healthcare Digital - Multi-Agent Workflow Example

Demonstrates a complete workflow orchestrating multiple agents for meal order processing.
"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime

# Import Agent Framework components
# NOTE: Install with: pip install agent-framework-azure-ai --pre
from agent_framework import (
    Executor,
    WorkflowBuilder,
    WorkflowContext,
    handler,
)
from typing_extensions import Never

# Import MCP Servers
from src.mcp_servers.meal_order_mcp import MealOrderMCPServer
from src.mcp_servers.food_production_mcp import FoodProductionMCPServer

# Import Agents
from src.agents.nutrition_validation_agent import NutritionValidationAgent
from src.agents.waste_reduction_agent import WasteReductionAgent


class MealOrderWorkflowExecutor(Executor):
    """
    Executor that orchestrates the meal order validation workflow.
    
    This demonstrates:
    1. Integration of custom agents with Agent Framework executors
    2. MCP server usage for tool access
    3. Multi-step workflow coordination
    """
    
    def __init__(self, id: str = "meal_order_workflow"):
        super().__init__(id=id)
        
        # Initialize MCP servers
        self.meal_order_mcp = MealOrderMCPServer()
        self.food_production_mcp = FoodProductionMCPServer()
        
        # Initialize agents
        self.nutrition_agent = NutritionValidationAgent()
        self.waste_agent = WasteReductionAgent()
        
        # Register MCP servers with agents
        self.nutrition_agent.register_mcp_server("meal_order", self.meal_order_mcp)
        self.waste_agent.register_mcp_server("food_production", self.food_production_mcp)
    
    @handler
    async def process_meal_order(self, order_request: Dict[str, Any], 
                                ctx: WorkflowContext[Dict[str, Any]]) -> None:
        """
        Process a meal order request through validation and submission.
        
        Workflow steps:
        1. Validate nutrition and dietary restrictions
        2. Check inventory and waste implications
        3. Submit order if valid
        4. Return result to next executor
        """
        patient_id = order_request.get("patient_id")
        meal_items = order_request.get("meal_items")
        meal_time = order_request.get("meal_time")
        
        print(f"\n=== Processing Meal Order ===")
        print(f"Patient: {patient_id}")
        print(f"Items: {meal_items}")
        print(f"Time: {meal_time}")
        
        # Step 1: Nutrition validation
        print("\n[Agent: Nutrition Validator] Validating meal...")
        validation_result = await self.nutrition_agent.process({
            "patient_id": patient_id,
            "meal_items": meal_items,
            "validation_type": "full"
        })
        
        if not validation_result.get("valid"):
            print("❌ Validation failed!")
            result = {
                "success": False,
                "reason": "Nutrition validation failed",
                "validation": validation_result,
                "order_id": None
            }
            await ctx.send_message(result)
            return
        
        print("✅ Nutrition validation passed")
        
        # Step 2: Submit order via MCP
        print("\n[MCP: Meal Order] Submitting order...")
        order_result = self.meal_order_mcp.call_endpoint(
            "submit_meal_order",
            {
                "patient_id": patient_id,
                "meal_items": meal_items,
                "meal_time": meal_time
            }
        )
        
        if not order_result.get("success"):
            print("❌ Order submission failed!")
            result = {
                "success": False,
                "reason": "Order submission failed",
                "details": order_result
            }
            await ctx.send_message(result)
            return
        
        order_data = order_result.get("data", {})
        print(f"✅ Order submitted: {order_data.get('order_id')}")
        
        # Step 3: Trigger waste analysis (parallel concern)
        print("\n[Agent: Waste Reducer] Analyzing waste implications...")
        waste_analysis = await self.waste_agent.process({
            "date": meal_time,
            "threshold_days": 3,
            "generate_actions": True
        })
        
        # Compile complete result
        result = {
            "success": True,
            "order_id": order_data.get("order_id"),
            "patient_id": patient_id,
            "scheduled_time": meal_time,
            "validation": validation_result,
            "waste_analysis": waste_analysis,
            "warnings": validation_result.get("warnings", [])
        }
        
        # Send to next executor
        await ctx.send_message(result)


class NotificationExecutor(Executor):
    """
    Executor that handles notifications and final output.
    """
    
    def __init__(self, id: str = "notification_executor"):
        super().__init__(id=id)
    
    @handler
    async def send_notifications(self, order_result: Dict[str, Any], 
                                 ctx: WorkflowContext[Never, Dict[str, Any]]) -> None:
        """
        Send notifications and yield final workflow output.
        """
        print("\n=== Order Processing Complete ===")
        
        if order_result.get("success"):
            print(f"✅ Order ID: {order_result.get('order_id')}")
            print(f"📅 Scheduled: {order_result.get('scheduled_time')}")
            
            if order_result.get("warnings"):
                print(f"⚠️  Warnings: {len(order_result['warnings'])} warnings")
            
            # Check waste recommendations
            waste_analysis = order_result.get("waste_analysis", {})
            if waste_analysis.get("success"):
                actions = waste_analysis.get("analysis", {}).get("recommended_actions", [])
                if actions:
                    print(f"\n💡 Waste reduction recommendations:")
                    for action in actions[:2]:  # Show top 2
                        print(f"   - {action.get('description')}")
        else:
            print(f"❌ Order failed: {order_result.get('reason')}")
        
        # Yield final output
        await ctx.yield_output(order_result)


async def main():
    """
    Main function demonstrating the multi-agent workflow.
    """
    print("=" * 60)
    print("Healthcare Digital - Multi-Agent Meal Order Workflow")
    print("=" * 60)
    
    # Create executors
    meal_order_executor = MealOrderWorkflowExecutor()
    notification_executor = NotificationExecutor()
    
    # Build workflow
    workflow = (
        WorkflowBuilder()
        .add_edge(meal_order_executor, notification_executor)
        .set_start_executor(meal_order_executor)
        .build()
    )
    
    # Sample meal order request
    order_request = {
        "patient_id": "P12345",
        "meal_items": ["grilled_chicken_salad", "fruit_cup", "whole_grain_bread"],
        "meal_time": datetime.utcnow().isoformat()
    }
    
    # Run workflow with streaming
    print("\n🚀 Starting workflow...\n")
    
    final_result = None
    async for event in workflow.run_stream(order_request):
        # In production, you would handle different event types
        # For this demo, we just capture the final output
        if hasattr(event, 'data') and isinstance(event.data, dict):
            if event.data.get('order_id'):
                final_result = event.data
    
    print("\n" + "=" * 60)
    print("Workflow Complete")
    print("=" * 60)
    
    if final_result:
        print(f"\nFinal Result:")
        print(f"  Success: {final_result.get('success')}")
        print(f"  Order ID: {final_result.get('order_id')}")
        print(f"  Patient: {final_result.get('patient_id')}")


if __name__ == "__main__":
    """
    To run this example:
    
    1. Install dependencies:
       pip install agent-framework-azure-ai --pre
       pip install -r requirements.txt
    
    2. Run the script:
       python examples/multi_agent_workflow.py
    
    Note: This example uses mock MCP servers for demonstration.
    In production, connect to actual healthcare data systems.
    """
    asyncio.run(main())
