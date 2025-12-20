"""
Base MCP Server for Research Laboratory
Provides common functionality for all MCP servers
"""

from mcp.server import Server
from mcp.types import Tool, TextContent
import logging
from typing import Any, Dict

class BaseMCPServer:
    """Base class for all MCP servers"""
    
    def __init__(self, name: str, db_helper):
        self.name = name
        self.db = db_helper
        self.server = Server(name)
        self.logger = logging.getLogger(name)
        
    def register_tool(self, tool: Tool):
        """Register a tool with the MCP server"""
        # Tool registration logic
        pass
    
    def handle_error(self, error: Exception, context: str) -> TextContent:
        """Standard error handling"""
        error_msg = f"Error in {context}: {str(error)}"
        self.logger.error(error_msg)
        return TextContent(
            type="text",
            text=f"❌ {error_msg}"
        )
    
    def format_response(self, data: Any, success: bool = True) -> TextContent:
        """Format response in standard way"""
        if success:
            return TextContent(
                type="text",
                text=f"✅ {str(data)}"
            )
        else:
            return TextContent(
                type="text",
                text=f"❌ {str(data)}"
            )
    
    def validate_required_params(self, params: Dict, required: list) -> tuple[bool, str]:
        """Validate required parameters"""
        missing = [p for p in required if p not in params]
        if missing:
            return False, f"Missing required parameters: {', '.join(missing)}"
        return True, ""
