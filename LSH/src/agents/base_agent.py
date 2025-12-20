"""
Healthcare Digital Agent Base Class

Base class for all agents in the system with common functionality.
"""

from typing import Dict, Any, List, Optional, Callable
from abc import ABC, abstractmethod
from datetime import datetime
import logging


class HealthcareAgentBase(ABC):
    """Base class for all healthcare agents."""
    
    def __init__(self, agent_id: str, agent_type: str, description: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.description = description
        self.logger = logging.getLogger(f"agent.{agent_id}")
        self.mcp_servers: Dict[str, Any] = {}
        
    def register_mcp_server(self, name: str, server: Any):
        """Register an MCP server for this agent to use."""
        self.mcp_servers[name] = server
        self.logger.info(f"Registered MCP server: {name}")
    
    def call_mcp(self, server_name: str, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call an MCP server endpoint.
        
        Args:
            server_name: Name of the MCP server
            endpoint: Endpoint to call
            params: Parameters for the endpoint
            
        Returns:
            Result from the MCP server
        """
        if server_name not in self.mcp_servers:
            return {
                "success": False,
                "error": f"MCP server '{server_name}' not registered"
            }
        
        server = self.mcp_servers[server_name]
        return server.call_endpoint(endpoint, params)
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input and return result.
        This method must be implemented by all agent subclasses.
        """
        pass
    
    def log_action(self, action: str, data: Dict[str, Any]):
        """Log agent action for monitoring and audit."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "action": action,
            "data": data
        }
        self.logger.info(f"Action: {action}", extra=log_entry)
        return log_entry
