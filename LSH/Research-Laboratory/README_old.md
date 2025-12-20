# 🔬 Medicines Research Laboratory

AI-Powered Pharmaceutical Research & Drug Discovery Platform

## Overview

The Medicines Research Laboratory is a comprehensive Streamlit-based application for managing pharmaceutical research operations, clinical trials, drug discovery pipelines, and laboratory experiments. Built on **Astra DB Serverless** with vector search capabilities.

## Features

### 📊 **Research Project Management**
- Track R&D projects across multiple therapeutic areas
- Budget tracking and resource allocation
- Project milestones and deliverables
- Priority-based project management

### 🏥 **Clinical Trials Management**
- Complete trial lifecycle from Phase 1 to Phase 4
- Enrollment tracking and participant management
- Multi-site trial coordination
- Regulatory compliance monitoring

### 💊 **Drug Discovery Pipeline**
- Track drug candidates from discovery to approval
- Development stage progression tracking
- Success probability analysis
- Market size estimation
- Patent and IP management

### 🧪 **Laboratory Experiments**
- Record and track experiments (in vitro, in vivo, analytical)
- Experiment metadata and results logging
- Success rate analytics
- Scientist productivity tracking

### 🔍 **Vector Search (AI-Powered)**
- Molecular structure similarity search (1536D embeddings)
- Research paper semantic search
- Patent document analysis

## Database Schema

### Collections (10 Total: 7 Regular + 3 Vector)

**Regular Collections:**
1. `research_projects` - R&D project tracking
2. `clinical_trials` - Clinical trial management
3. `drug_candidates` - Drug development pipeline
4. `lab_experiments` - Laboratory experiment records
5. `research_compounds` - Chemical compounds library
6. `trial_participants` - Clinical trial participant data
7. `research_publications` - Published research papers

**Vector Collections (1536D OpenAI Embeddings):**
1. `molecular_structures` - Chemical structure embeddings
2. `research_papers` - Research paper embeddings
3. `patent_documents` - Patent document embeddings

## Technology Stack

- **Frontend:** Streamlit 1.31+
- **Database:** DataStax Astra DB Serverless
- **Python SDK:** astrapy 2.1.0
- **AI/ML:** OpenAI API (text-embedding-3-small)
- **Vector Dimension:** 1536D
- **Authentication:** Token-based (Astra DB)

## Prerequisites

- Python 3.11+
- Astra DB account
- OpenAI API key
- Conda or venv environment

## Installation

### 1. Clone Repository
```bash
cd Research-Laboratory
```

### 2. Create Virtual Environment
```bash
conda create -n research-lab python=3.11
conda activate research-lab
```

### 3. Install Dependencies
```bash
pip install streamlit astrapy python-dotenv openai pandas numpy
```

### 4. Configure Environment

Create or update `.env` file in the root directory:

```env
# Research Laboratory - Astra DB Configuration
ASTRA_DB_TOKEN_MRL=AstraCS:xxxxx:yyyyy
ASTRA_DB_API_ENDPOINT_MRL=https://xxxxx-us-east-2.apps.astra.datastax.com
ASTRA_DB_KEYSPACE_MRL=medicines_research

# OpenAI Configuration
OPENAI_API_KEY=sk-proj-xxxxx
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536
```

### 5. Run Application
```bash
streamlit run app.py
```

The application will open at `http://localhost:8501`

## Project Structure

```
Research-Laboratory/
├── app.py                          # Main dashboard
├── pages/
│   ├── 1_Research_Projects.py     # Project management
│   ├── 2_Clinical_Trials.py       # Clinical trials
│   ├── 3_Drug_Discovery.py        # Drug pipeline
│   └── 4_Lab_Experiments.py       # Experiment tracking
├── src/
│   └── database/
│       └── astra_helper.py        # Astra DB operations
├── README.md
└── requirements.txt
```

## Usage Guide

### Creating a Research Project

1. Navigate to **Research Projects** page
2. Click **Create Project** tab
3. Fill in project details:
   - Project name and lead scientist
   - Department and therapeutic area
   - Budget and team size
   - Start/end dates
4. Submit to create project

### Registering a Clinical Trial

1. Go to **Clinical Trials** page
2. Click **Register Trial** tab
3. Enter trial information:
   - Trial ID (e.g., NCT12345678)
   - Drug name and indication
   - Phase (1, 2, 3, or 4)
   - Target participants and sites
5. Submit to register trial

### Adding Drug Candidates

1. Open **Drug Discovery** page
2. Click **Add Candidate** tab
3. Provide compound details:
   - Compound name and target
   - Mechanism of action
   - Development stage
   - Success probability
4. Save candidate to pipeline

### Recording Experiments

1. Navigate to **Lab Experiments** page
2. Click **Record Experiment** tab
3. Enter experiment details:
   - Experiment type (in vitro, in vivo, etc.)
   - Scientist name and lab location
   - Methodology and objectives
   - Results and observations
4. Submit to log experiment

## API Operations

### Research Projects
```python
from src.database.astra_helper import db

# Create project
project_id = db.create_research_project({
    "project_name": "Novel Antibiotic Development",
    "lead_scientist": "Dr. Jane Smith",
    "budget": 500000
})

# Get all projects
projects = db.get_research_projects(limit=100)
```

### Clinical Trials
```python
# Register trial
trial_id = db.create_clinical_trial({
    "trial_id": "NCT12345678",
    "drug_name": "XYZ-123",
    "phase": "phase2"
})

# Get trials
trials = db.get_clinical_trials(limit=100)
```

### Vector Search
```python
# Search similar molecules
results = db.search_similar_molecules(query_vector, limit=10)

# Search research papers
papers = db.search_research_papers(query_vector, limit=10)
```

## Features Roadmap

### Phase 1 ✅ (Current)
- Research project management
- Clinical trial tracking
- Drug discovery pipeline
- Lab experiment logging
- Basic analytics

### Phase 2 (Planned)
- AI agents for research assistance
- Automated literature review
- Molecular property prediction
- Clinical trial optimization
- Real-time collaboration

### Phase 3 (Future)
- Integration with ELN systems
- LIMS integration
- Advanced ML models
- Regulatory submission automation
- Multi-site synchronization

## Security & Compliance

- **Data Encryption:** All data encrypted at rest and in transit
- **Access Control:** Token-based authentication
- **Audit Logging:** Complete activity tracking
- **HIPAA Considerations:** PHI data handling (see documentation)
- **GLP Compliance:** Good Laboratory Practice support

## Troubleshooting

### Connection Issues
```python
# Test Astra DB connection
from src.database.astra_helper import db
print(db.get_collection_names())
```

### Collection Limit Error
- Astra DB free tier: 10 collections maximum
- Current usage: 10/10 collections
- Consider upgrading plan or archiving unused collections

### Environment Variables
- Ensure `.env` file exists in root directory
- Verify `_MRL` suffix for Research Laboratory credentials
- Check token validity in Astra DB console

## Support

- **Documentation:** See `docs/` folder
- **Issues:** Create GitHub issue
- **Astra DB Support:** https://docs.datastax.com/

## License

Proprietary - Internal Use Only

## Contributors

- Research Laboratory Development Team
- Pharmaceutical R&D Division

---

**Version:** 1.0.0  
**Last Updated:** December 2025  
**Database:** medicines_research  
**Status:** Production Ready ✅
