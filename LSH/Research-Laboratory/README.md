# Research Laboratory Solution

Advanced research laboratory management system with AI-powered agents for clinical trials, drug discovery, and patent analysis.

## 🏗️ Solution Architecture

```
Research-Laboratory/
├── src/
│   ├── agents/                          # AI Agents
│   │   ├── clinical_trial_agent.py      # Clinical trial management
│   │   ├── drug_discovery_agent.py      # Drug candidate analysis
│   │   ├── lab_experiment_agent.py      # Lab experiment tracking
│   │   ├── research_publication_agent.py # Literature management
│   │   ├── patent_analysis_agent.py     # Patent search & IP
│   │   └── research_analytics_agent.py  # Analytics & reporting
│   ├── mcp_servers/                     # MCP Protocol Servers
│   │   ├── base_mcp_server.py           # Base MCP functionality
│   │   ├── research_project_mcp.py      # Project operations
│   │   ├── clinical_trial_mcp.py        # Trial operations
│   │   ├── drug_discovery_mcp.py        # Drug candidate operations
│   │   └── analytics_mcp.py             # Analytics operations
│   ├── database/
│   │   └── astra_helper.py              # Astra DB wrapper
│   └── utils/
│       └── validators.py                # Data validators
├── ui/                                   # Streamlit UI
│   ├── app.py                           # Main application
│   └── pages/
│       ├── 1_Research_Projects.py       # 🔬 Projects
│       ├── 2_Clinical_Trials.py         # 💊 Trials
│       ├── 3_Drug_Discovery.py          # 🧪 Drug candidates
│       ├── 4_Lab_Experiments.py         # 🧬 Experiments
│       ├── 5_CSV_Import.py              # 📤 Data import
│       └── 6_Analytics.py               # 📊 Analytics (to be added)
├── docs/
│   ├── Architecture_Diagram.drawio      # System architecture
│   ├── DataFlow_Diagram.drawio          # Data flow
│   └── solution_design.md               # Design docs
├── tests/                                # Unit tests
├── data/
│   └── sample_data/                     # Sample CSV files
├── csv/                                  # User CSV files
├── mcp_server.py                        # MCP server entry point
├── mcp_config.json                      # MCP configuration
├── requirements.txt
└── README.md
```

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run ui/app.py
```

**Access**: http://localhost:8501

## 📊 10 Collections (7 Regular + 3 Vector)

**Regular**: research_projects, clinical_trials, drug_candidates, lab_experiments, research_compounds, trial_participants, research_publications

**Vector (1536D)**: molecular_structures, research_papers, patent_documents

## 🤖 6 AI Agents

1. **Clinical Trial Agent** - Trial management & compliance
2. **Drug Discovery Agent** - Candidate evaluation & pipeline
3. **Lab Experiment Agent** - Experiment tracking & analysis
4. **Research Publication Agent** - Literature search & review
5. **Patent Analysis Agent** - IP landscape & prior art
6. **Research Analytics Agent** - Metrics & reporting

## 🔌 MCP Server - 18 Tools

Query (5) | Insert (3) | Vector Search (3) | Analytics (3) | Bulk Ops (4)

See [MCP_README.md](MCP_README.md) for details.

---

**Version 2.0** - Organized structure matching Pharma-Medicines layout
