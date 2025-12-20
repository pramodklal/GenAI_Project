# Research Laboratory MCP Server

## Overview
MCP (Model Context Protocol) server for the Research Laboratory solution, providing programmatic access to pharmaceutical research database operations.

## Features

### Query Tools
- `query_research_projects` - Query research projects with filters
- `query_clinical_trials` - Query clinical trials
- `query_drug_candidates` - Query drug candidates
- `query_lab_experiments` - Query laboratory experiments
- `query_research_compounds` - Query research compounds

### Insert Tools
- `insert_research_project` - Add new research project
- `insert_clinical_trial` - Add new clinical trial
- `insert_drug_candidate` - Add new drug candidate

### Vector Search Tools
- `vector_search_molecular_structures` - Find similar molecules
- `vector_search_research_papers` - Find similar research papers
- `vector_search_patents` - Find similar patent documents

### Analytics Tools
- `get_collection_stats` - Get document counts for all collections
- `get_project_summary` - Get research project statistics
- `get_trial_summary` - Get clinical trial statistics by phase/status

### Bulk Operations
- `bulk_insert` - Insert multiple documents at once
- `update_document` - Update existing document
- `delete_document` - Delete document by ID

## Installation

1. Install MCP Python SDK:
```bash
pip install mcp
```

2. Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

3. Configure environment variables in `.env`:
```
ASTRA_DB_TOKEN_MRL=your_token_here
ASTRA_DB_API_ENDPOINT_MRL=your_endpoint_here
ASTRA_DB_KEYSPACE_MRL=medicines_research
OPENAI_API_KEY=your_openai_key_here
```

## Running the Server

### Standalone Mode
```bash
python mcp_server.py
```

### With MCP Client
Add to your MCP client configuration:
```json
{
  "mcpServers": {
    "research-laboratory": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "d:\\GenAI_Project_2025\\HealthCareDigital\\Research-Laboratory"
    }
  }
}
```

## Usage Examples

### Query Research Projects
```json
{
  "tool": "query_research_projects",
  "arguments": {
    "filter": {"status": "active"},
    "limit": 10
  }
}
```

### Insert Clinical Trial
```json
{
  "tool": "insert_clinical_trial",
  "arguments": {
    "document": {
      "trial_id": "CT-2025-001",
      "title": "Phase II Study of Novel Antibiotic",
      "phase": "Phase II",
      "status": "recruiting",
      "start_date": "2025-01-15"
    }
  }
}
```

### Vector Search for Similar Molecules
```json
{
  "tool": "vector_search_molecular_structures",
  "arguments": {
    "query": "aspirin-like pain relief compound",
    "limit": 5
  }
}
```

### Get Collection Statistics
```json
{
  "tool": "get_collection_stats",
  "arguments": {}
}
```

## Database Collections

### Regular Collections (7)
- `research_projects` - Research project metadata
- `clinical_trials` - Clinical trial information
- `drug_candidates` - Drug candidate compounds
- `lab_experiments` - Laboratory experiment records
- `research_compounds` - Chemical compound data
- `trial_participants` - Clinical trial participant data
- `research_publications` - Scientific publication metadata

### Vector Collections (3) [1536D embeddings]
- `molecular_structures` - Molecular structure data with embeddings
- `research_papers` - Research paper abstracts with embeddings
- `patent_documents` - Patent document text with embeddings

## Architecture

```
mcp_server.py (MCP Server)
    ↓
src/database/astra_helper.py (Database Layer)
    ↓
Astra DB (DataStax)
    ↓
10 Collections (7 Regular + 3 Vector)
```

## Error Handling
All tools return structured JSON responses with error messages when operations fail:
```json
{
  "error": "Error description",
  "tool": "tool_name"
}
```

## Vector Search
Vector search tools automatically:
1. Generate embeddings using OpenAI `text-embedding-3-small` model
2. Perform cosine similarity search in Astra DB
3. Return top K most similar results with similarity scores

## Security
- Database credentials loaded from environment variables
- No hardcoded secrets in code
- All operations logged for audit trail

## Logging
Server logs all operations to console with timestamps and severity levels:
- ✅ INFO: Successful operations
- ⚠️ WARNING: Warnings
- ❌ ERROR: Failed operations

## Support
For issues or questions, refer to the main Research-Laboratory README.md
