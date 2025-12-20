"""
Healthcare Digital - LangGraph Multi-Agent Workflow

Demonstrates multi-agent orchestration using LangGraph for meal order processing.
"""

import asyncio
from typing import Dict, Any, TypedDict, Annotated, Sequence
from datetime import datetime
import operator

# LangGraph imports
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Import MCP Servers and Agents
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mcp_servers import MealOrderMCPServer, FoodProductionMCPServer
from agents import NutritionValidationAgent, WasteReductionAgent


# Define the state that will be passed between nodes
class WorkflowState(TypedDict):
    """State object that tracks the workflow progress."""
    order_request: Dict[str, Any]
    validation_result: Dict[str, Any]
    order_result: Dict[str, Any]
    waste_analysis: Dict[str, Any]
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next_step: str
    

class MealOrderWorkflow:
    """LangGraph-based workflow for meal order processing."""
    
    def __init__(self):
        # Initialize MCP servers
        self.meal_order_mcp = MealOrderMCPServer()
        self.food_production_mcp = FoodProductionMCPServer()
        
        # Initialize agents
        self.nutrition_agent = NutritionValidationAgent()
        self.waste_agent = WasteReductionAgent()
        
        # Register MCP servers with agents
        self.nutrition_agent.register_mcp_server("meal_order", self.meal_order_mcp)
        self.waste_agent.register_mcp_server("food_production", self.food_production_mcp)
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow."""
        
        # Create the graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("validate_nutrition", self._validate_nutrition_node)
        workflow.add_node("submit_order", self._submit_order_node)
        workflow.add_node("analyze_waste", self._analyze_waste_node)
        workflow.add_node("send_notification", self._notification_node)
        
        # Define edges (workflow paths)
        workflow.set_entry_point("validate_nutrition")
        
        # Conditional edge after validation
        workflow.add_conditional_edges(
            "validate_nutrition",
            self._should_continue_after_validation,
            {
                "submit": "submit_order",
                "reject": "send_notification"
            }
        )
        
        workflow.add_edge("submit_order", "analyze_waste")
        workflow.add_edge("analyze_waste", "send_notification")
        workflow.add_edge("send_notification", END)
        
        return workflow.compile()
    
    async def _validate_nutrition_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Node: Validate meal nutrition and dietary restrictions."""
        print("\n[Node: Nutrition Validation]")
        
        order_request = state["order_request"]
        patient_id = order_request.get("patient_id")
        meal_items = order_request.get("meal_items")
        
        print(f"  Validating meals for patient {patient_id}...")
        
        # Run nutrition validation agent
        validation_result = await self.nutrition_agent.process({
            "patient_id": patient_id,
            "meal_items": meal_items,
            "validation_type": "full"
        })
        
        is_valid = validation_result.get("valid")
        print(f"  ✅ Valid: {is_valid}")
        
        if not is_valid:
            issues = validation_result.get("issues", [])
            print(f"  ❌ Issues found: {len(issues)}")
        
        return {
            "validation_result": validation_result,
            "messages": [AIMessage(content=f"Validation complete. Valid: {is_valid}")]
        }
    
    def _should_continue_after_validation(self, state: WorkflowState) -> str:
        """Conditional logic: proceed or reject based on validation."""
        validation = state.get("validation_result", {})
        return "submit" if validation.get("valid") else "reject"
    
    async def _submit_order_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Node: Submit the meal order."""
        print("\n[Node: Order Submission]")
        
        order_request = state["order_request"]
        
        # Submit via MCP
        order_result = self.meal_order_mcp.call_endpoint(
            "submit_meal_order",
            {
                "patient_id": order_request["patient_id"],
                "meal_items": order_request["meal_items"],
                "meal_time": order_request["meal_time"]
            }
        )
        
        if order_result.get("success"):
            order_id = order_result["data"].get("order_id")
            print(f"  ✅ Order submitted: {order_id}")
        else:
            print(f"  ❌ Order submission failed")
        
        return {
            "order_result": order_result.get("data", {}),
            "messages": [AIMessage(content=f"Order submitted successfully")]
        }
    
    async def _analyze_waste_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Node: Analyze waste implications."""
        print("\n[Node: Waste Analysis]")
        
        order_request = state["order_request"]
        
        # Run waste analysis
        waste_analysis = await self.waste_agent.process({
            "date": order_request["meal_time"],
            "threshold_days": 3,
            "generate_actions": True
        })
        
        at_risk_count = len(waste_analysis.get("at_risk_items", []))
        print(f"  📊 Items at risk: {at_risk_count}")
        
        actions = waste_analysis.get("analysis", {}).get("recommended_actions", [])
        if actions:
            print(f"  💡 Recommendations: {len(actions)} actions suggested")
        
        return {
            "waste_analysis": waste_analysis,
            "messages": [AIMessage(content=f"Waste analysis complete. {at_risk_count} items at risk.")]
        }
    
    async def _notification_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Node: Send notifications and finalize workflow."""
        print("\n[Node: Notifications]")
        
        validation = state.get("validation_result", {})
        order = state.get("order_result", {})
        waste = state.get("waste_analysis", {})
        
        if order.get("order_id"):
            print(f"  ✅ Order {order['order_id']} processed successfully")
            
            if validation.get("warnings"):
                print(f"  ⚠️  {len(validation['warnings'])} warnings")
            
            waste_actions = waste.get("analysis", {}).get("recommended_actions", [])
            if waste_actions:
                print(f"  💡 {len(waste_actions)} waste reduction recommendations")
        else:
            print(f"  ❌ Order rejected due to validation failures")
            issues = validation.get("issues", [])
            for issue in issues[:3]:
                print(f"     - {issue.get('reason')}")
        
        return {
            "messages": [AIMessage(content="Workflow complete. Notifications sent.")]
        }
    
    async def run(self, order_request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the workflow."""
        initial_state = {
            "order_request": order_request,
            "validation_result": {},
            "order_result": {},
            "waste_analysis": {},
            "messages": [HumanMessage(content=f"Process meal order for {order_request['patient_id']}")],
            "next_step": ""
        }
        
        # Run the workflow
        final_state = await self.workflow.ainvoke(initial_state)
        
        return {
            "success": bool(final_state.get("order_result", {}).get("order_id")),
            "order_result": final_state.get("order_result"),
            "validation_result": final_state.get("validation_result"),
            "waste_analysis": final_state.get("waste_analysis"),
            "messages": final_state.get("messages", [])
        }


async def main():
    """Main function demonstrating the LangGraph workflow."""
    print("=" * 70)
    print("Healthcare Digital - LangGraph Multi-Agent Workflow")
    print("=" * 70)
    
    # Create workflow
    workflow = MealOrderWorkflow()
    
    # Sample meal order request
    order_request = {
        "patient_id": "P12345",
        "meal_items": ["grilled_chicken_salad", "fruit_cup", "whole_grain_bread"],
        "meal_time": datetime.utcnow().isoformat()
    }
    
    print(f"\n📋 Processing order for patient: {order_request['patient_id']}")
    print(f"   Items: {', '.join(order_request['meal_items'])}")
    
    # Run workflow
    result = await workflow.run(order_request)
    
    print("\n" + "=" * 70)
    print("Workflow Complete")
    print("=" * 70)
    
    print(f"\n✅ Success: {result['success']}")
    if result.get('order_result', {}).get('order_id'):
        print(f"📦 Order ID: {result['order_result']['order_id']}")
    
    # Show summary
    validation = result.get('validation_result', {})
    if validation.get('warnings'):
        print(f"\n⚠️  Warnings: {len(validation['warnings'])}")
    
    waste = result.get('waste_analysis', {})
    if waste.get('success'):
        actions = waste.get('analysis', {}).get('recommended_actions', [])
        print(f"💡 Waste Reduction Actions: {len(actions)}")
    
    print("\n" + "=" * 70)


async def demonstrate_graph_structure():
    """Show the workflow graph structure."""
    print("\n" + "=" * 70)
    print("Workflow Graph Structure")
    print("=" * 70)
    
    print("""
    
    ┌─────────────┐
    │   START     │
    └──────┬──────┘
           │
           ▼
    ┌─────────────────────┐
    │ Validate Nutrition  │
    └──────┬──────────────┘
           │
           ├─────────────┐
           │             │
           ▼             ▼
    [Valid?]        [Invalid]
           │             │
           ▼             │
    ┌──────────────┐     │
    │ Submit Order │     │
    └──────┬───────┘     │
           │             │
           ▼             │
    ┌──────────────┐     │
    │ Analyze      │     │
    │ Waste        │     │
    └──────┬───────┘     │
           │             │
           └─────┬───────┘
                 │
                 ▼
          ┌──────────────┐
          │ Notification │
          └──────┬───────┘
                 │
                 ▼
              [END]
    
    """)
    
    print("Key Features:")
    print("  • Conditional routing based on validation")
    print("  • Parallel-capable nodes (can be extended)")
    print("  • State management across nodes")
    print("  • Agent integration with MCP servers")
    print("=" * 70)


if __name__ == "__main__":
    """
    To run this example:
    
    1. Install dependencies:
       pip install langgraph langchain langchain-openai
       
    2. Run the script:
       python examples/langgraph_workflow.py
    
    Note: This uses mock MCP servers for demonstration.
    For production, configure Azure OpenAI credentials.
    """
    
    asyncio.run(demonstrate_graph_structure())
    asyncio.run(main())
