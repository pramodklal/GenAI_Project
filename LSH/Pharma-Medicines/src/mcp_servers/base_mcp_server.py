"""
Pharma Manufacturing - Base MCP Server

Provides standardized interface for all MCP servers in the pharmaceutical system.
"""

from typing import Dict, Any, List, Optional, Callable
from abc import ABC, abstractmethod
from datetime import datetime
import logging
import json


class MCPServerBase(ABC):
    """Base class for all MCP servers in Pharma Manufacturing system."""
    
    def __init__(self, server_name: str, version: str = "1.0.0"):
        self.server_name = server_name
        self.version = version
        self.logger = logging.getLogger(f"mcp.{server_name}")
        self.endpoints: Dict[str, Callable] = {}
        self._register_endpoints()
        
    @abstractmethod
    def _register_endpoints(self):
        """Register all endpoints for this MCP server."""
        pass
    
    def register_endpoint(self, name: str, handler: Callable, 
                         required_params: List[str], 
                         description: str):
        """Register an endpoint with validation."""
        self.endpoints[name] = {
            "handler": handler,
            "required_params": required_params,
            "description": description
        }
        self.logger.info(f"Registered endpoint: {name}")
    
    def call_endpoint(self, endpoint_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call an endpoint with parameters and return result.
        
        Args:
            endpoint_name: Name of the endpoint to call
            params: Parameters to pass to the endpoint
            
        Returns:
            Dictionary with result or error
        """
        try:
            if endpoint_name not in self.endpoints:
                return {
                    "success": False,
                    "error": f"Endpoint '{endpoint_name}' not found",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            endpoint = self.endpoints[endpoint_name]
            
            # Validate required parameters
            missing_params = [
                p for p in endpoint["required_params"] 
                if p not in params
            ]
            
            if missing_params:
                return {
                    "success": False,
                    "error": f"Missing required parameters: {missing_params}",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Call the handler
            result = endpoint["handler"](**params)
            
            return {
                "success": True,
                "data": result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error calling endpoint {endpoint_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def list_endpoints(self) -> List[Dict[str, Any]]:
        """List all available endpoints."""
        return [
            {
                "name": name,
                "description": endpoint["description"],
                "required_params": endpoint["required_params"]
            }
            for name, endpoint in self.endpoints.items()
        ]
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information."""
        return {
            "name": self.server_name,
            "version": self.version,
            "endpoints": len(self.endpoints),
            "timestamp": datetime.utcnow().isoformat()
        }
