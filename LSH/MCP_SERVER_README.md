# HealthCare Digital MCP Server

## Overview

The HealthCare Digital MCP (Model Context Protocol) Server exposes enterprise healthcare operations as programmatic tools that can be accessed by AI agents, LLMs, and other systems.

## Features

### 🍽️ **Meal Ordering Tools (6 tools)**
- `get_patient_dietary_restrictions` - Retrieve patient dietary restrictions and allergies
- `validate_meal_selection` - Validate meals against dietary requirements
- `submit_meal_order` - Submit validated meal orders
- `get_meal_history` - Get patient meal order history
- `get_meal_recommendations` - Get personalized meal recommendations
- `get_nutrition_info` - Get detailed nutritional information

### 🍳 **Food Production Tools (6 tools)**
- `get_demand_forecast` - Get meal demand forecasts
- `get_inventory_status` - Check food inventory levels
- `create_prep_schedule` - Create food preparation schedules
- `update_production_status` - Update production task status
- `get_equipment_availability` - Check kitchen equipment availability
- `identify_waste_risks` - Identify items at risk of waste/expiration

### 🧹 **EVS Management Tools (7 tools)**
- `create_evs_task` - Create environmental services tasks
- `get_pending_evs_tasks` - Get pending EVS tasks
- `assign_evs_task` - Assign tasks to EVS staff
- `update_evs_task_status` - Update task status
- `get_evs_staff_availability` - Get staff availability
- `get_environmental_metrics` - Get environmental monitoring metrics
- `prioritize_evs_tasks` - Calculate task priorities

### 📊 **Analytics & Reporting Tools (3 tools)**
- `get_daily_operations_summary` - Get comprehensive daily operations summary
- `get_waste_reduction_report` - Get waste reduction metrics
- `get_compliance_metrics` - Get dietary compliance metrics

## Total: 22 MCP Tools

## Installation

### Prerequisites
```bash
pip install mcp openai astrapy streamlit
```

### Configuration

Create `.env` file with Astra DB credentials:
```env
ASTRA_DB_API_ENDPOINT=https://your-db-id-region.apps.astra.datastax.com
ASTRA_DB_APPLICATION_TOKEN=AstraCS:...
ASTRA_DB_KEYSPACE=healthcare_digital
```

## Usage

### Running the MCP Server

#### Standalone Mode
```bash
python mcp_server.py
```

#### With MCP Client
```bash
mcp run mcp_server.py
```

#### In Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "healthcare-digital": {
      "command": "python",
      "args": ["D:/GenAI_Project_2025/HealthCareDigital/mcp_server.py"],
      "env": {
        "ASTRA_DB_API_ENDPOINT": "your-endpoint",
        "ASTRA_DB_APPLICATION_TOKEN": "your-token",
        "ASTRA_DB_KEYSPACE": "healthcare_digital"
      }
    }
  }
}
```

### Example Tool Calls

#### Get Patient Dietary Restrictions
```json
{
  "tool": "get_patient_dietary_restrictions",
  "arguments": {
    "patient_id": "P12345"
  }
}
```

#### Validate Meal Selection
```json
{
  "tool": "validate_meal_selection",
  "arguments": {
    "patient_id": "P12345",
    "meal_items": ["grilled_chicken", "steamed_broccoli", "brown_rice"]
  }
}
```

#### Create EVS Task
```json
{
  "tool": "create_evs_task",
  "arguments": {
    "location": "Room 301",
    "task_type": "terminal_cleaning",
    "priority": "high"
  }
}
```

#### Get Demand Forecast
```json
{
  "tool": "get_demand_forecast",
  "arguments": {
    "date": "2025-12-21",
    "meal_type": "lunch"
  }
}
```

## Architecture

```
mcp_server.py (Main Server)
    │
    ├── MealOrderMCPServer
    │   └── 6 meal ordering endpoints
    │
    ├── FoodProductionMCPServer
    │   └── 6 food production endpoints
    │
    ├── EVSTaskMCPServer
    │   └── 7 EVS management endpoints
    │
    └── Analytics Functions
        └── 3 reporting endpoints
```

## Integration with AI Agents

The MCP server is designed to work seamlessly with:

1. **LangGraph Workflows** - Use tools in multi-agent workflows
2. **OpenAI Function Calling** - Convert tools to OpenAI function schemas
3. **Claude Desktop** - Native MCP integration
4. **Custom AI Agents** - Access via MCP protocol

## Database Integration

All tools are backed by Astra DB with real-time data:
- Patient dietary profiles
- Meal orders and history
- Food inventory
- Production schedules
- EVS tasks and assignments

## Error Handling

All tools return standardized responses:

```json
{
  "success": true,
  "data": { ... },
  "timestamp": "2025-12-20T10:30:00Z"
}
```

Or on error:

```json
{
  "success": false,
  "error": "Error message",
  "timestamp": "2025-12-20T10:30:00Z"
}
```

## Security

- Database credentials stored in environment variables
- Input validation on all tool parameters
- Error messages sanitized to prevent information leakage

## Testing

Test the MCP server:

```bash
# Test connection
python -c "from mcp_server import init_db; print('DB Connected!' if init_db() else 'Connection Failed')"

# Run server and test tools
python mcp_server.py
```

## Monitoring

Server logs include:
- Tool invocations
- Database queries
- Error traces
- Performance metrics

## Support

For issues or questions:
- Check database connection in `.env`
- Verify MCP package installation: `pip list | grep mcp`
- Review server logs for error messages

## License

Enterprise Healthcare Digital Platform - Internal Use Only

---

**Server Version:** 1.0.0  
**Protocol:** MCP (Model Context Protocol)  
**Total Tools:** 22  
**Last Updated:** December 2025
