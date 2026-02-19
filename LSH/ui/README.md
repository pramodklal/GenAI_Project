# Healthcare Digital UI

Streamlit-based web interface for the Healthcare Digital Agentic AI System.

## Running the Application

```bash
# Navigate to project root
cd d:\GenAI_Project_2025\HealthCareDigital

# Install dependencies (if not already done)
pip install -r requirements.txt

# Run the Streamlit app
streamlit run ui/app.py
```

The application will open in your default browser at `http://localhost:8501`

## Pages

1. **🍽️ Meal Ordering** - Patient meal ordering with AI validation
2. **🍳 Food Production** - Production planning and waste reduction
3. **🧹 EVS Management** - Task prioritization and assignment
4. **📊 Analytics** - Reports and performance metrics
5. **📁 Data Import** - CSV data upload to Astra DB collections
6. **⚙️ System Status** - Health monitoring and configuration
7. **👤 Add Patient** - Patient registration and management

## Features

- 🤖 AI-powered meal validation
- 📊 Real-time analytics and reporting
- 🍳 Intelligent food production planning
- 🧹 Smart EVS task prioritization
- ⚙️ System health monitoring
- 📈 Performance metrics visualization

## Configuration

Before running, ensure your `.env` file has the required credentials:

```
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
```

See `.env.example` for all configuration options.
