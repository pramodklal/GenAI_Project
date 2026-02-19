"""
MCP Server for Research Laboratory Solution
Exposes pharmaceutical research database operations as MCP tools
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
from src.database.astra_helper import AstraDBHelper

# Initialize MCP Server
app = Server("research-laboratory")

# Initialize database helper
db_helper = None

def init_db():
    """Initialize database connection"""
    global db_helper
    if db_helper is None:
        try:
            db_helper = AstraDBHelper()
            return True
        except Exception as e:
            print(f"Failed to initialize database: {e}", file=sys.stderr)
            return False
    return True

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available MCP tools for Research Laboratory"""
    return [
        # Query Tools
        Tool(
            name="query_research_projects",
            description="Query research projects from the database with optional filters",
            inputSchema={
                "type": "object",
                "properties": {
                    "filter": {
                        "type": "object",
                        "description": "MongoDB-style filter query (e.g., {'status': 'active'})"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 10
                    }
                }
            }
        ),
        Tool(
            name="query_clinical_trials",
            description="Query clinical trials from the database with optional filters",
            inputSchema={
                "type": "object",
                "properties": {
                    "filter": {
                        "type": "object",
                        "description": "MongoDB-style filter query"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 10
                    }
                }
            }
        ),
        Tool(
            name="query_drug_candidates",
            description="Query drug candidates from the database",
            inputSchema={
                "type": "object",
                "properties": {
                    "filter": {"type": "object"},
                    "limit": {"type": "integer", "default": 10}
                }
            }
        ),
        Tool(
            name="query_lab_experiments",
            description="Query laboratory experiments from the database",
            inputSchema={
                "type": "object",
                "properties": {
                    "filter": {"type": "object"},
                    "limit": {"type": "integer", "default": 10}
                }
            }
        ),
        Tool(
            name="query_research_compounds",
            description="Query research compounds from the database",
            inputSchema={
                "type": "object",
                "properties": {
                    "filter": {"type": "object"},
                    "limit": {"type": "integer", "default": 10}
                }
            }
        ),
        
        # Insert Tools
        Tool(
            name="insert_research_project",
            description="Insert a new research project into the database",
            inputSchema={
                "type": "object",
                "properties": {
                    "document": {
                        "type": "object",
                        "description": "Research project document with fields like title, principal_investigator, status, start_date, budget",
                        "required": ["title", "principal_investigator", "status"]
                    }
                },
                "required": ["document"]
            }
        ),
        Tool(
            name="insert_clinical_trial",
            description="Insert a new clinical trial into the database",
            inputSchema={
                "type": "object",
                "properties": {
                    "document": {
                        "type": "object",
                        "description": "Clinical trial document",
                        "required": ["trial_id", "title", "phase"]
                    }
                },
                "required": ["document"]
            }
        ),
        Tool(
            name="insert_drug_candidate",
            description="Insert a new drug candidate into the database",
            inputSchema={
                "type": "object",
                "properties": {
                    "document": {
                        "type": "object",
                        "description": "Drug candidate document",
                        "required": ["compound_name", "target_disease"]
                    }
                },
                "required": ["document"]
            }
        ),
        
        # Vector Search Tools
        Tool(
            name="vector_search_molecular_structures",
            description="Perform vector similarity search on molecular structures using text query",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Text query to search for similar molecular structures"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of similar results to return",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="vector_search_research_papers",
            description="Perform vector similarity search on research papers using text query",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Text query to find similar research papers"
                    },
                    "limit": {
                        "type": "integer",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="vector_search_patents",
            description="Perform vector similarity search on patent documents",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Text query to find similar patents"
                    },
                    "limit": {
                        "type": "integer",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),
        
        # Analytics Tools
        Tool(
            name="get_collection_stats",
            description="Get document counts and statistics for all collections",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_project_summary",
            description="Get summary statistics for research projects (active, completed, budget totals)",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_trial_summary",
            description="Get summary statistics for clinical trials by phase and status",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        
        # Bulk Operations
        Tool(
            name="bulk_insert",
            description="Insert multiple documents into a collection at once",
            inputSchema={
                "type": "object",
                "properties": {
                    "collection_name": {
                        "type": "string",
                        "description": "Target collection name",
                        "enum": [
                            "research_projects", "clinical_trials", "drug_candidates",
                            "lab_experiments", "research_compounds", "trial_participants",
                            "research_publications", "molecular_structures", "research_papers",
                            "patent_documents"
                        ]
                    },
                    "documents": {
                        "type": "array",
                        "description": "Array of documents to insert",
                        "items": {"type": "object"}
                    }
                },
                "required": ["collection_name", "documents"]
            }
        ),
        
        # Update/Delete Tools
        Tool(
            name="update_document",
            description="Update a document in a collection by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "collection_name": {"type": "string"},
                    "document_id": {"type": "string"},
                    "updates": {
                        "type": "object",
                        "description": "Fields to update"
                    }
                },
                "required": ["collection_name", "document_id", "updates"]
            }
        ),
        Tool(
            name="delete_document",
            description="Delete a document from a collection by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "collection_name": {"type": "string"},
                    "document_id": {"type": "string"}
                },
                "required": ["collection_name", "document_id"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    
    # Ensure database is initialized
    if not init_db():
        return [TextContent(type="text", text="Error: Failed to initialize database connection")]
    
    try:
        # Query Tools
        if name == "query_research_projects":
            result = await query_collection("research_projects", arguments)
            
        elif name == "query_clinical_trials":
            result = await query_collection("clinical_trials", arguments)
            
        elif name == "query_drug_candidates":
            result = await query_collection("drug_candidates", arguments)
            
        elif name == "query_lab_experiments":
            result = await query_collection("lab_experiments", arguments)
            
        elif name == "query_research_compounds":
            result = await query_collection("research_compounds", arguments)
        
        # Insert Tools
        elif name == "insert_research_project":
            result = await insert_document("research_projects", arguments.get("document", {}))
            
        elif name == "insert_clinical_trial":
            result = await insert_document("clinical_trials", arguments.get("document", {}))
            
        elif name == "insert_drug_candidate":
            result = await insert_document("drug_candidates", arguments.get("document", {}))
        
        # Vector Search Tools
        elif name == "vector_search_molecular_structures":
            result = await vector_search("molecular_structures", arguments)
            
        elif name == "vector_search_research_papers":
            result = await vector_search("research_papers", arguments)
            
        elif name == "vector_search_patents":
            result = await vector_search("patent_documents", arguments)
        
        # Analytics Tools
        elif name == "get_collection_stats":
            result = await get_stats()
            
        elif name == "get_project_summary":
            result = await get_project_summary()
            
        elif name == "get_trial_summary":
            result = await get_trial_summary()
        
        # Bulk Operations
        elif name == "bulk_insert":
            result = await bulk_insert_documents(
                arguments.get("collection_name"),
                arguments.get("documents", [])
            )
        
        # Update/Delete
        elif name == "update_document":
            result = await update_doc(
                arguments.get("collection_name"),
                arguments.get("document_id"),
                arguments.get("updates", {})
            )
            
        elif name == "delete_document":
            result = await delete_doc(
                arguments.get("collection_name"),
                arguments.get("document_id")
            )
        
        else:
            result = {"error": f"Unknown tool: {name}"}
        
        return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        
    except Exception as e:
        error_msg = {"error": str(e), "tool": name}
        return [TextContent(type="text", text=json.dumps(error_msg, indent=2))]

# Helper Functions

async def query_collection(collection_name: str, args: Dict) -> Dict:
    """Query a collection with filters"""
    filter_query = args.get("filter", {})
    limit = args.get("limit", 10)
    
    docs = db_helper.query_documents(collection_name, filter_query, limit)
    return {
        "collection": collection_name,
        "count": len(docs),
        "documents": docs
    }

async def insert_document(collection_name: str, document: Dict) -> Dict:
    """Insert a document into a collection"""
    success = db_helper.insert_document(collection_name, document)
    return {
        "collection": collection_name,
        "success": success,
        "message": "Document inserted successfully" if success else "Failed to insert document"
    }

async def vector_search(collection_name: str, args: Dict) -> Dict:
    """Perform vector similarity search"""
    query = args.get("query", "")
    limit = args.get("limit", 10)
    
    # Generate embedding for query
    import openai
    try:
        client = openai.OpenAI()
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        )
        query_vector = response.data[0].embedding
        
        # Perform vector search
        results = db_helper.vector_search(collection_name, query_vector, limit)
        
        return {
            "collection": collection_name,
            "query": query,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        return {"error": f"Vector search failed: {str(e)}"}

async def get_stats() -> Dict:
    """Get collection statistics"""
    stats = db_helper.get_collection_stats()
    return {
        "statistics": stats,
        "total_documents": sum(stats.values())
    }

async def get_project_summary() -> Dict:
    """Get research project summary"""
    all_projects = db_helper.query_documents("research_projects", {}, 1000)
    
    active = sum(1 for p in all_projects if p.get("status") == "active")
    completed = sum(1 for p in all_projects if p.get("status") == "completed")
    total_budget = sum(p.get("budget", 0) for p in all_projects if p.get("budget"))
    
    return {
        "total_projects": len(all_projects),
        "active": active,
        "completed": completed,
        "total_budget": total_budget
    }

async def get_trial_summary() -> Dict:
    """Get clinical trial summary"""
    all_trials = db_helper.query_documents("clinical_trials", {}, 1000)
    
    by_phase = {}
    by_status = {}
    
    for trial in all_trials:
        phase = trial.get("phase", "unknown")
        status = trial.get("status", "unknown")
        by_phase[phase] = by_phase.get(phase, 0) + 1
        by_status[status] = by_status.get(status, 0) + 1
    
    return {
        "total_trials": len(all_trials),
        "by_phase": by_phase,
        "by_status": by_status
    }

async def bulk_insert_documents(collection_name: str, documents: List[Dict]) -> Dict:
    """Bulk insert documents"""
    success_count = 0
    error_count = 0
    
    for doc in documents:
        if db_helper.insert_document(collection_name, doc):
            success_count += 1
        else:
            error_count += 1
    
    return {
        "collection": collection_name,
        "total": len(documents),
        "success": success_count,
        "errors": error_count
    }

async def update_doc(collection_name: str, doc_id: str, updates: Dict) -> Dict:
    """Update a document"""
    success = db_helper.update_document(collection_name, doc_id, updates)
    return {
        "collection": collection_name,
        "document_id": doc_id,
        "success": success
    }

async def delete_doc(collection_name: str, doc_id: str) -> Dict:
    """Delete a document"""
    success = db_helper.delete_document(collection_name, doc_id)
    return {
        "collection": collection_name,
        "document_id": doc_id,
        "success": success
    }

async def main():
    """Run the MCP server"""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
