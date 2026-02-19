"""
Research Project MCP Server
Handles research project operations via MCP protocol
"""

from mcp.server import Server
from mcp.types import Tool, TextContent
from .base_mcp_server import BaseMCPServer
import json

class ResearchProjectMCP(BaseMCPServer):
    """MCP server for research project operations"""
    
    def __init__(self, db_helper):
        super().__init__("research-project-mcp", db_helper)
        self._register_tools()
    
    def _register_tools(self):
        """Register all research project tools"""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            return [
                Tool(
                    name="query_research_projects",
                    description="Query research projects with optional filters",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "description": "Filter by status"},
                            "principal_investigator": {"type": "string"},
                            "limit": {"type": "number", "default": 50}
                        }
                    }
                ),
                Tool(
                    name="get_project_details",
                    description="Get detailed information about a specific project",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": {"type": "string", "description": "Project ID"}
                        },
                        "required": ["project_id"]
                    }
                ),
                Tool(
                    name="create_research_project",
                    description="Create a new research project",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_name": {"type": "string"},
                            "principal_investigator": {"type": "string"},
                            "start_date": {"type": "string"},
                            "status": {"type": "string"},
                            "funding_source": {"type": "string"},
                            "budget": {"type": "number"}
                        },
                        "required": ["project_name", "principal_investigator", "start_date"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            try:
                if name == "query_research_projects":
                    return await self._query_projects(arguments)
                elif name == "get_project_details":
                    return await self._get_project_details(arguments)
                elif name == "create_research_project":
                    return await self._create_project(arguments)
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
            except Exception as e:
                return [self.handle_error(e, name)]
    
    async def _query_projects(self, args: dict) -> list[TextContent]:
        """Query research projects"""
        filter_dict = {}
        if 'status' in args:
            filter_dict['status'] = args['status']
        if 'principal_investigator' in args:
            filter_dict['principal_investigator'] = args['principal_investigator']
        
        limit = args.get('limit', 50)
        
        results = self.db.query_documents('research_projects', filter_dict, limit=limit)
        return [TextContent(type="text", text=json.dumps(results, indent=2))]
    
    async def _get_project_details(self, args: dict) -> list[TextContent]:
        """Get project details"""
        is_valid, msg = self.validate_required_params(args, ['project_id'])
        if not is_valid:
            return [self.format_response(msg, success=False)]
        
        project = self.db.get_document_by_id('research_projects', args['project_id'])
        return [TextContent(type="text", text=json.dumps(project, indent=2))]
    
    async def _create_project(self, args: dict) -> list[TextContent]:
        """Create new project"""
        is_valid, msg = self.validate_required_params(
            args, 
            ['project_name', 'principal_investigator', 'start_date']
        )
        if not is_valid:
            return [self.format_response(msg, success=False)]
        
        result = self.db.insert_document('research_projects', args)
        return [self.format_response(f"Created project: {result}")]
