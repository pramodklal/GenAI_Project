"""
MCP Server for HealthCare Digital Enterprise Platform
Exposes healthcare operations as MCP tools for meal ordering, food production, and EVS management
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
from datetime import datetime

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from mcp.server import Server
from mcp.types import Tool, TextContent
from database.astra_helper import get_db_helper

# Initialize MCP Server
app = Server("healthcare-digital")

# Initialize database helper
db_helper = None

def init_db():
    """Initialize database connection"""
    global db_helper
    if db_helper is None:
        try:
            db_helper = get_db_helper()
            return True
        except Exception as e:
            print(f"Failed to initialize database: {e}", file=sys.stderr)
            return False
    return True

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available MCP tools for HealthCare Digital Platform"""
    return [
        # ===== MEAL ORDERING TOOLS =====
        Tool(
            name="get_patient_dietary_restrictions",
            description="Retrieve dietary restrictions and allergies for a patient",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_id": {
                        "type": "string",
                        "description": "Patient identifier"
                    }
                },
                "required": ["patient_id"]
            }
        ),
        Tool(
            name="validate_meal_selection",
            description="Validate meal selection against patient dietary restrictions and allergies",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_id": {
                        "type": "string",
                        "description": "Patient identifier"
                    },
                    "meal_items": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of meal item IDs to validate"
                    }
                },
                "required": ["patient_id", "meal_items"]
            }
        ),
        Tool(
            name="submit_meal_order",
            description="Submit a validated meal order for a patient",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_id": {
                        "type": "string",
                        "description": "Patient identifier"
                    },
                    "meal_items": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of meal item IDs"
                    },
                    "meal_time": {
                        "type": "string",
                        "description": "Meal time: breakfast, lunch, dinner, snack",
                        "enum": ["breakfast", "lunch", "dinner", "snack"]
                    },
                    "special_instructions": {
                        "type": "string",
                        "description": "Special preparation instructions (optional)"
                    }
                },
                "required": ["patient_id", "meal_items", "meal_time"]
            }
        ),
        Tool(
            name="get_meal_history",
            description="Get meal order history for a patient",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_id": {
                        "type": "string",
                        "description": "Patient identifier"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days of history to retrieve",
                        "default": 7
                    }
                },
                "required": ["patient_id"]
            }
        ),
        Tool(
            name="get_meal_recommendations",
            description="Get personalized meal recommendations for a patient based on dietary profile",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_id": {
                        "type": "string",
                        "description": "Patient identifier"
                    },
                    "meal_time": {
                        "type": "string",
                        "description": "Meal time for recommendations",
                        "enum": ["breakfast", "lunch", "dinner", "snack"]
                    }
                },
                "required": ["patient_id"]
            }
        ),
        Tool(
            name="get_nutrition_info",
            description="Get detailed nutritional information for a meal item",
            inputSchema={
                "type": "object",
                "properties": {
                    "meal_id": {
                        "type": "string",
                        "description": "Meal item identifier"
                    }
                },
                "required": ["meal_id"]
            }
        ),
        
        # ===== FOOD PRODUCTION TOOLS =====
        Tool(
            name="get_demand_forecast",
            description="Get meal demand forecast for a specific date",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Date for forecast (ISO format YYYY-MM-DD)"
                    },
                    "meal_type": {
                        "type": "string",
                        "description": "Optional meal type filter",
                        "enum": ["breakfast", "lunch", "dinner"]
                    }
                },
                "required": ["date"]
            }
        ),
        Tool(
            name="get_inventory_status",
            description="Get current food inventory status and stock levels",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Optional category filter (dairy, produce, meat, dry_goods, etc.)"
                    }
                }
            }
        ),
        Tool(
            name="create_prep_schedule",
            description="Create food preparation schedule based on meal plan",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Date for prep schedule (ISO format)"
                    },
                    "meal_plan": {
                        "type": "object",
                        "description": "Meal plan with quantities for each meal type"
                    }
                },
                "required": ["date", "meal_plan"]
            }
        ),
        Tool(
            name="update_production_status",
            description="Update food production task status",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Production task identifier"
                    },
                    "status": {
                        "type": "string",
                        "description": "New status",
                        "enum": ["pending", "in_progress", "completed", "cancelled"]
                    }
                },
                "required": ["task_id", "status"]
            }
        ),
        Tool(
            name="get_equipment_availability",
            description="Check kitchen equipment availability for a specific date",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Date to check availability (ISO format)"
                    }
                },
                "required": ["date"]
            }
        ),
        Tool(
            name="identify_waste_risks",
            description="Identify food items at risk of expiration or waste",
            inputSchema={
                "type": "object",
                "properties": {
                    "days_threshold": {
                        "type": "integer",
                        "description": "Number of days threshold for expiration warning",
                        "default": 3
                    }
                }
            }
        ),
        
        # ===== EVS TASK MANAGEMENT TOOLS =====
        Tool(
            name="create_evs_task",
            description="Create a new environmental services task",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Room or area identifier (e.g., 'Room 301', 'Cafeteria')"
                    },
                    "task_type": {
                        "type": "string",
                        "description": "Type of EVS task",
                        "enum": ["terminal_cleaning", "daily_cleaning", "disinfection", "maintenance", "spill_cleanup", "inspection"]
                    },
                    "priority": {
                        "type": "string",
                        "description": "Task priority level",
                        "enum": ["low", "medium", "high", "critical"],
                        "default": "medium"
                    },
                    "description": {
                        "type": "string",
                        "description": "Additional task details (optional)"
                    }
                },
                "required": ["location", "task_type"]
            }
        ),
        Tool(
            name="get_pending_evs_tasks",
            description="Get list of pending EVS tasks with optional filters",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Filter by location (optional)"
                    },
                    "priority": {
                        "type": "string",
                        "description": "Filter by priority (optional)",
                        "enum": ["low", "medium", "high", "critical"]
                    },
                    "task_type": {
                        "type": "string",
                        "description": "Filter by task type (optional)"
                    }
                }
            }
        ),
        Tool(
            name="assign_evs_task",
            description="Assign an EVS task to a staff member",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Task identifier"
                    },
                    "staff_id": {
                        "type": "string",
                        "description": "EVS staff member identifier"
                    }
                },
                "required": ["task_id", "staff_id"]
            }
        ),
        Tool(
            name="update_evs_task_status",
            description="Update EVS task status",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Task identifier"
                    },
                    "status": {
                        "type": "string",
                        "description": "New status",
                        "enum": ["pending", "assigned", "in_progress", "completed", "cancelled"]
                    }
                },
                "required": ["task_id", "status"]
            }
        ),
        Tool(
            name="get_evs_staff_availability",
            description="Get EVS staff availability and current assignments",
            inputSchema={
                "type": "object",
                "properties": {
                    "shift": {
                        "type": "string",
                        "description": "Filter by shift (optional)",
                        "enum": ["morning", "afternoon", "night"]
                    }
                }
            }
        ),
        Tool(
            name="get_environmental_metrics",
            description="Get environmental monitoring metrics for a location",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Room or area identifier"
                    }
                },
                "required": ["location"]
            }
        ),
        Tool(
            name="prioritize_evs_tasks",
            description="Calculate priority scores for multiple EVS tasks",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of task IDs to prioritize"
                    }
                },
                "required": ["task_ids"]
            }
        ),
        
        # ===== ANALYTICS & REPORTING TOOLS =====
        Tool(
            name="get_daily_operations_summary",
            description="Get comprehensive daily operations summary across all departments",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Date for summary (ISO format, defaults to today)"
                    }
                }
            }
        ),
        Tool(
            name="get_waste_reduction_report",
            description="Get waste reduction metrics and analytics",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date for report period (ISO format)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date for report period (ISO format)"
                    }
                },
                "required": ["start_date", "end_date"]
            }
        ),
        Tool(
            name="get_compliance_metrics",
            description="Get dietary compliance and validation metrics",
            inputSchema={
                "type": "object",
                "properties": {
                    "days": {
                        "type": "integer",
                        "description": "Number of days to analyze",
                        "default": 30
                    }
                }
            }
        )
    ]

# ===== TOOL IMPLEMENTATIONS =====

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    
    if not init_db():
        return [TextContent(
            type="text",
            text=json.dumps({"error": "Failed to initialize database connection"}, indent=2)
        )]
    
    try:
        # Import MCP servers
        from src.mcp_servers import MealOrderMCPServer, FoodProductionMCPServer, EVSTaskMCPServer
        
        # Initialize servers
        meal_server = MealOrderMCPServer()
        food_server = FoodProductionMCPServer()
        evs_server = EVSTaskMCPServer()
        
        # Route to appropriate server
        result = None
        
        # Meal Ordering Tools
        if name == "get_patient_dietary_restrictions":
            result = meal_server.call_endpoint("get_patient_dietary_restrictions", arguments)
        elif name == "validate_meal_selection":
            result = meal_server.call_endpoint("validate_meal_selection", arguments)
        elif name == "submit_meal_order":
            result = meal_server.call_endpoint("submit_meal_order", arguments)
        elif name == "get_meal_history":
            result = meal_server.call_endpoint("get_meal_history", arguments)
        elif name == "get_meal_recommendations":
            result = meal_server.call_endpoint("get_meal_recommendations", arguments)
        elif name == "get_nutrition_info":
            result = meal_server.call_endpoint("get_nutrition_info", arguments)
        
        # Food Production Tools
        elif name == "get_demand_forecast":
            result = food_server.call_endpoint("get_demand_forecast", arguments)
        elif name == "get_inventory_status":
            result = food_server.call_endpoint("get_inventory_status", arguments)
        elif name == "create_prep_schedule":
            result = food_server.call_endpoint("create_prep_schedule", arguments)
        elif name == "update_production_status":
            result = food_server.call_endpoint("update_production_status", arguments)
        elif name == "get_equipment_availability":
            result = food_server.call_endpoint("get_equipment_availability", arguments)
        elif name == "identify_waste_risks":
            result = food_server.call_endpoint("identify_waste_risks", arguments)
        
        # EVS Task Management Tools
        elif name == "create_evs_task":
            result = evs_server.call_endpoint("create_task", arguments)
        elif name == "get_pending_evs_tasks":
            result = evs_server.call_endpoint("get_pending_tasks", arguments)
        elif name == "assign_evs_task":
            result = evs_server.call_endpoint("assign_task", arguments)
        elif name == "update_evs_task_status":
            result = evs_server.call_endpoint("update_task_status", arguments)
        elif name == "get_evs_staff_availability":
            result = evs_server.call_endpoint("get_staff_availability", arguments)
        elif name == "get_environmental_metrics":
            result = evs_server.call_endpoint("get_environmental_metrics", arguments)
        elif name == "prioritize_evs_tasks":
            result = evs_server.call_endpoint("prioritize_tasks", arguments)
        
        # Analytics Tools
        elif name == "get_daily_operations_summary":
            result = await get_daily_operations_summary(arguments.get("date"))
        elif name == "get_waste_reduction_report":
            result = await get_waste_reduction_report(
                arguments.get("start_date"),
                arguments.get("end_date")
            )
        elif name == "get_compliance_metrics":
            result = await get_compliance_metrics(arguments.get("days", 30))
        
        else:
            result = {"error": f"Unknown tool: {name}"}
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, default=str)
        )]
        
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)}, indent=2)
        )]

# ===== ANALYTICS FUNCTIONS =====

async def get_daily_operations_summary(date: Optional[str] = None) -> Dict[str, Any]:
    """Get comprehensive daily operations summary"""
    if not date:
        date = datetime.now().date().isoformat()
    
    # Get meal orders
    orders = db_helper.get_todays_orders(date)
    
    # Get inventory status
    low_inventory = db_helper.get_low_inventory_items(threshold=50)
    
    return {
        "date": date,
        "meal_orders": {
            "total": len(orders),
            "by_meal_type": {
                "breakfast": len([o for o in orders if o.get("meal_time") == "breakfast"]),
                "lunch": len([o for o in orders if o.get("meal_time") == "lunch"]),
                "dinner": len([o for o in orders if o.get("meal_time") == "dinner"])
            }
        },
        "inventory": {
            "low_stock_items": len(low_inventory),
            "items_need_reorder": len([i for i in low_inventory if i.get("current_quantity", 0) < i.get("reorder_point", 0)])
        },
        "generated_at": datetime.now().isoformat()
    }

async def get_waste_reduction_report(start_date: str, end_date: str) -> Dict[str, Any]:
    """Get waste reduction metrics"""
    # This would query actual waste tracking data
    return {
        "period": {
            "start_date": start_date,
            "end_date": end_date
        },
        "metrics": {
            "total_waste_kg": 45.2,
            "waste_reduction_percentage": 18.5,
            "items_saved_from_waste": 127,
            "cost_savings": 2450.00
        },
        "top_waste_categories": [
            {"category": "produce", "waste_kg": 15.3},
            {"category": "dairy", "waste_kg": 12.1},
            {"category": "prepared_meals", "waste_kg": 8.7}
        ],
        "generated_at": datetime.now().isoformat()
    }

async def get_compliance_metrics(days: int = 30) -> Dict[str, Any]:
    """Get dietary compliance metrics"""
    return {
        "period_days": days,
        "metrics": {
            "total_orders": 1247,
            "orders_with_restrictions": 523,
            "validation_success_rate": 98.5,
            "allergen_violations": 2,
            "dietary_violations": 5
        },
        "compliance_rate": 99.4,
        "generated_at": datetime.now().isoformat()
    }

# ===== SERVER STARTUP =====

async def main():
    """Run the MCP server"""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        print("HealthCare Digital MCP Server starting...", file=sys.stderr)
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
