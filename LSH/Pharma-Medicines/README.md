# Pharma-Medicines Manufacturing System

AI-powered pharmaceutical manufacturing management system with quality control, regulatory compliance, and inventory management.

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI Layer                    │
│  (Landing Page + 6 Functional Pages)                    │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│                  AI Agents Layer                         │
│  • Quality Control Agent    • Supply Chain Agent        │
│  • Regulatory Compliance    • Pharmacovigilance Agent   │
│  • Production Optimization  • Equipment Maintenance     │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│                MCP Servers Layer                         │
│  • Medicine MCP    • Quality Control MCP                │
│  • Production MCP  • Compliance MCP                     │
│  • Inventory MCP                                        │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│               Astra DB (Database Layer)                  │
│  13 Collections: 10 Regular + 3 Vector (1536D)          │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Features

### 💊 Medicine Catalog
- Browse and manage pharmaceutical products
- Formulation details with components
- **AI-powered vector search** for similar formulations

### 🏭 Batch Production
- Create and track manufacturing batches
- Update production stages
- **AI-optimized production scheduling**
- Real-time batch analytics

### ✅ Quality Control
- Submit QC tests with **AI-powered OOS detection**
- Comprehensive batch validation
- Generate Certificates of Analysis (COA)
- OOS investigations dashboard

### 📜 Regulatory Compliance
- Regulatory documents management
- **AI-powered adverse event reporting** with pharmacovigilance analysis
- Audit trail reports (21 CFR Part 11)
- **Vector search** for SOPs
- GMP compliance validation

### 📦 Inventory Management
- Material inventory with stock status
- **AI-powered low stock alerts** with demand forecasting
- Purchase order management with **supplier performance analysis**
- Expiring materials tracking
- **AI demand forecasting** with visualization

### 📊 Analytics Dashboard
- Production KPIs (yield, volume, status)
- Quality metrics (pass rates, OOS trends)
- Compliance dashboard
- **AI-generated insights**

## 🗄️ Database Schema

### Regular Collections (10)
- `medicines` - Pharmaceutical products
- `manufacturing_batches` - Production batches
- `quality_control_tests` - QC test results
- `raw_materials` - API & excipients inventory
- `suppliers` - Supplier information
- `production_schedules` - Production planning
- `equipment_maintenance` - Equipment tracking
- `regulatory_documents` - FDA, EMA, GMP documents
- `purchase_orders` - Material procurement
- `audit_logs` - 21 CFR Part 11 compliance

### Vector Collections (3) - 1536D Embeddings
- `formulations` - Medicine formulations with vector search
- `adverse_events` - Pharmacovigilance with similarity search
- `sop_documents` - Standard Operating Procedures

## 📋 Prerequisites

- Python 3.11+
- Astra DB account (serverless)
- OpenAI API key (for AI agents & embeddings)

## ⚙️ Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd Pharma-Medicines
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment:**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables:**
   ```bash
   # Copy template
   cp .env.example .env
   
   # Edit .env with your credentials
   # - ASTRA_DB_TOKEN
   # - ASTRA_DB_API_ENDPOINT
   # - OPENAI_API_KEY
   ```

## 🗃️ Database Setup

1. **Create Astra DB database:**
   - Go to [astra.datastax.com](https://astra.datastax.com)
   - Create a serverless database
   - Create keyspace: `medicines_manufacture`

2. **Create collections** (13 total):
   
   **Regular collections:**
   ```bash
   medicines
   manufacturing_batches
   quality_control_tests
   raw_materials
   suppliers
   production_schedules
   equipment_maintenance
   regulatory_documents
   purchase_orders
   audit_logs
   ```
   
   **Vector collections (1536 dimensions):**
   ```bash
   formulations (with $vector field, 1536D)
   adverse_events (with $vector field, 1536D)
   sop_documents (with $vector field, 1536D)
   ```

3. **Load sample data:**
   ```bash
   python data/load_sample_data.py
   ```

## 🚀 Running the Application

```bash
streamlit run app.py
```

The application will open at `http://localhost:8501`

## 📁 Project Structure

```
Pharma-Medicines/
├── app.py                          # Landing page dashboard
├── pages/                          # Streamlit pages
│   ├── 1_Medicine_Catalog.py
│   ├── 2_Batch_Production.py
│   ├── 3_Quality_Control.py
│   ├── 4_Regulatory_Compliance.py
│   ├── 5_Inventory_Management.py
│   └── 6_Analytics.py
├── src/
│   ├── database/
│   │   └── astra_helper.py        # Astra DB operations
│   ├── agents/                    # AI agents (6)
│   │   ├── quality_control_agent.py
│   │   ├── regulatory_compliance_agent.py
│   │   ├── production_optimization_agent.py
│   │   ├── supply_chain_agent.py
│   │   ├── pharmacovigilance_agent.py
│   │   └── equipment_maintenance_agent.py
│   └── mcp_servers/               # MCP servers (5)
│       ├── base_mcp_server.py
│       ├── medicine_mcp.py
│       ├── quality_control_mcp.py
│       ├── production_mcp.py
│       ├── compliance_mcp.py
│       └── inventory_mcp.py
├── data/
│   └── csv/                       # Sample data (13 CSV files)
├── .env.example                   # Configuration template
└── requirements.txt               # Python dependencies
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ASTRA_DB_TOKEN` | Astra DB application token | Yes |
| `ASTRA_DB_API_ENDPOINT` | Astra DB API endpoint | Yes |
| `ASTRA_DB_KEYSPACE` | Database keyspace | Yes |
| `OPENAI_API_KEY` | OpenAI API key | Yes |
| `EMBEDDING_MODEL` | Embedding model name | No (default: text-embedding-3-small) |
| `EMBEDDING_DIMENSION` | Embedding dimensions | No (default: 1536) |

## 🤖 AI Agents

### Quality Control Agent
- OOS detection with deviation analysis
- Batch quality validation
- Certificate of Analysis generation

### Regulatory Compliance Agent
- FDA/EMA/GMP compliance validation
- Document expiry tracking
- Audit trail analysis

### Production Optimization Agent
- Schedule optimization
- Material requirements calculation
- Yield prediction
- Bottleneck detection

### Supply Chain Agent
- Demand forecasting
- Supplier performance analysis
- EOQ/ROP calculations
- FEFO inventory management

### Pharmacovigilance Agent
- Adverse event causality assessment (WHO-UMC scale)
- Severity classification
- Signal detection
- Regulatory reporting timelines

### Equipment Maintenance Agent
- OEE calculation (Availability × Performance × Quality)
- Preventive/predictive maintenance
- Calibration tracking

## 📊 MCP Servers (30 Endpoints Total)

### Medicine MCP (6 endpoints)
- Medicine details, search, formulations
- **Vector search** for similar formulations

### Quality Control MCP (6 endpoints)
- Submit tests with **AI analysis**
- Validate batches, approve, generate COA

### Production MCP (6 endpoints)
- Create batches, update stages
- **AI-optimized scheduling**

### Compliance MCP (6 endpoints)
- Regulatory compliance checks
- AE reporting with **PV agent analysis**
- **Vector SOP search**

### Inventory MCP (6 endpoints)
- Material inventory
- **AI demand forecasting**
- Supplier analysis

## 📜 Compliance

- **FDA 21 CFR Part 11** - Electronic records & signatures
- **GMP** - Good Manufacturing Practices
- **ISO 9001:2015** - Quality management
- **FDA/EMA** - Regulatory standards

## 🧪 Testing

```bash
# Run unit tests
python -m pytest tests/

# Test individual agents
python tests/test_qc_agent.py
```

## 📚 Documentation

- [Architecture Diagram](architecture_diagram.drawio)
- [Dataflow Diagram](dataflow_diagram.drawio)
- [Solution Design](solution_design.md)
- [Database Schema](database_schema_with_sample_data.md)

## 🛠️ Technology Stack

- **Frontend:** Streamlit
- **Database:** Astra DB (DataStax)
- **AI/ML:** OpenAI GPT-4, text-embedding-3-small
- **Vector Search:** Astra DB Vector Search
- **Visualization:** Plotly
- **Python:** 3.11+

## 📝 License

MIT License

## 🤝 Support

For issues, questions, or contributions, please create an issue in the repository.

## 🎯 Roadmap

- [ ] Email notifications for critical alerts
- [ ] Mobile app for production floor operators
- [ ] Advanced ML models for yield prediction
- [ ] Integration with ERP systems
- [ ] Multi-language support
- [ ] PDF report generation

## 👥 Authors

Built with ❤️ for pharmaceutical manufacturing excellence
