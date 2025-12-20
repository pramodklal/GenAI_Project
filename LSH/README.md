# Healthcare Digital - Agentic AI System

A comprehensive multi-agent AI system for healthcare operations, featuring intelligent automation for Patient Meal Ordering, Food Production, and EVS Task Management.

## 🎯 Overview

This system implements an agentic AI architecture using Microsoft Agent Framework with MCP (Model Context Protocol) servers to provide secure, structured tool access for AI agents across healthcare workflows.

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│  Agent Orchestration & Governance   │
├─────────────────────────────────────┤
│  Multi-Agent System Layer           │
│  • Patient Meal Ordering Agents     │
│  • Food Production Agents           │
│  • EVS Task Management Agents       │
├─────────────────────────────────────┤
│  MCP Server Layer                   │
│  • Meal Order MCP                   │
│  • Food Production MCP              │
│  • EVS Task MCP                     │
├─────────────────────────────────────┤
│  Operational Data Science Layer     │
│  • Predictive Models                │
│  • Forecasting                      │
│  • Anomaly Detection                │
└─────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Azure subscription (for production deployment)
- Microsoft Foundry project (formerly Azure AI Foundry) or GitHub Models access

### Installation

1. **Clone the repository**
   ```bash
   cd d:\GenAI_Project_2025\HealthCareDigital
   ```

2. **Create and activate virtual environment**
   ```bash
   # Using the existing conda environment
   conda activate envhcd
   ```

3. **Install dependencies**
   ```bash
   pip install agent-framework-azure-ai --pre
   pip install -r requirements.txt
   ```
   
   ⚠️ **Note**: The `--pre` flag is required while Agent Framework is in preview.

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

### Run Example Workflow

```bash
python examples/multi_agent_workflow.py
```

## 📦 Project Structure

```
HealthCareDigital/
├── docs/
│   └── ARCHITECTURE.md          # Complete system architecture
├── src/
│   ├── agents/
│   │   ├── base_agent.py        # Base agent class
│   │   ├── nutrition_validation_agent.py
│   │   ├── waste_reduction_agent.py
│   │   └── evs_prioritization_agent.py
│   ├── mcp_servers/
│   │   ├── base_mcp_server.py   # Base MCP server
│   │   ├── meal_order_mcp.py
│   │   ├── food_production_mcp.py
│   │   └── evs_task_mcp.py
│   ├── models/                  # Predictive models
│   └── workflows/               # Agent orchestration workflows
├── examples/
│   └── multi_agent_workflow.py  # Complete workflow example
├── config/
│   └── agent_config.yaml
├── requirements.txt
├── .env.example
└── README.md
```

## 🤖 Key Agents

### Patient Meal Ordering
- **Nutrition Validation Agent**: Validates meals against dietary restrictions
- **Dietary Rule Enforcement Agent**: Ensures medical compliance
- **Personalization Agent**: Recommends meals based on preferences

### Food Production
- **Prep Planning Agent**: Optimizes food preparation schedules
- **Demand Forecasting Agent**: Predicts meal demand
- **Waste Reduction Agent**: Minimizes food waste

### EVS Task Management
- **Task Prioritization Agent**: Ranks cleaning tasks by urgency
- **Routing & Assignment Agent**: Optimally assigns tasks to staff
- **Environmental Monitoring Copilot**: Real-time monitoring

## 🔧 MCP Servers

### Meal Order MCP Server
Provides endpoints for:
- Patient dietary restrictions retrieval
- Meal selection validation
- Order submission
- Nutrition information
- Meal history and recommendations

### Food Production MCP Server
Provides endpoints for:
- Demand forecasting
- Inventory status
- Prep schedule creation
- Production status updates
- Waste risk identification

### EVS Task MCP Server
Provides endpoints for:
- Task creation and management
- Staff availability
- Task prioritization
- Environmental metrics
- Assignment optimization

## 🔄 Workflow Patterns

The system supports multiple orchestration patterns:

1. **Sequential**: Tasks execute in order
2. **Parallel**: Multiple agents work simultaneously
3. **Conditional**: Decision-based routing
4. **Loop**: Iterative refinement
5. **Human-in-Loop**: Human approval for critical decisions

Example workflow:
```python
workflow = (
    WorkflowBuilder()
    .add_edge(validation_agent, ordering_agent)
    .add_edge(ordering_agent, notification_agent)
    .set_start_executor(validation_agent)
    .build()
)

async for event in workflow.run_stream(order_request):
    # Handle events
    pass
```

## 🔒 Security & Compliance

- **HIPAA Compliant**: All patient data encrypted at rest and in transit
- **Audit Logging**: Complete action history for compliance
- **Role-Based Access**: Granular permission control
- **Input Validation**: Sanitization of all user inputs
- **Safety Checks**: Human-in-loop for critical decisions

## 📊 Monitoring & Observability

- **Application Insights**: Real-time performance monitoring
- **Prometheus Metrics**: Custom metrics and dashboards
- **Structured Logging**: JSON logs for analysis
- **Agent Performance**: Track success rates and response times

## 🧪 Testing

```bash
# Run unit tests
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run with coverage
pytest --cov=src tests/
```

## 🚢 Deployment

### Development (GitHub Models)
```bash
# Set environment variables
export GITHUB_TOKEN=your_token
python examples/multi_agent_workflow.py
```

### Production (Microsoft Foundry)
```bash
# Configure Azure credentials
az login
export FOUNDRY_PROJECT_ENDPOINT=your_endpoint
export FOUNDRY_MODEL_DEPLOYMENT=gpt-4o

# Deploy agents
python deploy/deploy_agents.py
```

## 📈 Success Metrics

### Operational Efficiency
- 30% reduction in meal ordering errors
- 20% improvement in food waste reduction
- 25% faster EVS task completion
- 15% reduction in labor costs

### Agent Performance
- <2 second average response time
- <1% task failure rate
- 80%+ autonomous completion rate
- 95%+ prediction accuracy

## 🤝 Contributing

This is an internal Healthcare Digital project. For questions or contributions:

1. Review [ARCHITECTURE.md](docs/ARCHITECTURE.md)
2. Create feature branch
3. Submit pull request with tests
4. Ensure all CI checks pass

## 📚 Documentation

- [Architecture Overview](docs/ARCHITECTURE.md) - Complete system design
- [API Documentation](docs/API.md) - MCP server endpoints (coming soon)
- [Agent Guide](docs/AGENTS.md) - Agent development guide (coming soon)
- [Deployment Guide](docs/DEPLOYMENT.md) - Production deployment (coming soon)

## 🔗 Resources

- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [GitHub Models](https://github.com/marketplace/models)
- [Microsoft Foundry](https://ai.azure.com/)

## 📝 License

Copyright © 2025 Healthcare Digital. All rights reserved.

## 💡 Next Steps

1. **Review** the [architecture documentation](docs/ARCHITECTURE.md)
2. **Run** the example workflow
3. **Configure** your Azure/GitHub credentials
4. **Customize** agents for your specific needs
5. **Deploy** to your environment

---

**Built with ❤️ using Microsoft Agent Framework**
