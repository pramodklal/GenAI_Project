"""
Medicine MCP Server - v1.0.0

MCP server for medicine catalog operations, formulation management, and vector search.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Any
import logging

from mcp_servers.base_mcp_server import MCPServerBase
from database.astra_helper import get_db_helper

logger = logging.getLogger(__name__)


class MedicineMCPServer(MCPServerBase):
    """MCP Server for medicine and formulation operations."""
    
    def __init__(self):
        super().__init__("Medicine MCP Server", "1.0.0")
        self.db = get_db_helper()
    
    def _register_endpoints(self):
        """Register all medicine-related endpoints."""
        
        self.register_endpoint(
            name="get_medicine_details",
            handler=self._get_medicine_details,
            required_params=["medicine_id"],
            description="Get detailed information about a specific medicine"
        )
        
        self.register_endpoint(
            name="search_medicines",
            handler=self._search_medicines,
            required_params=["query"],
            description="Search medicines by name, dosage form, or therapeutic category"
        )
        
        self.register_endpoint(
            name="get_formulation_info",
            handler=self._get_formulation_info,
            required_params=["medicine_id"],
            description="Get formulation details including components and manufacturing process"
        )
        
        self.register_endpoint(
            name="get_similar_formulations",
            handler=self._get_similar_formulations,
            required_params=["medicine_id", "query_vector"],
            description="Find similar formulations using vector search (requires embedding)"
        )
        
        self.register_endpoint(
            name="create_medicine",
            handler=self._create_medicine,
            required_params=["medicine_data"],
            description="Create a new medicine entry in the catalog"
        )
        
        self.register_endpoint(
            name="update_medicine_status",
            handler=self._update_medicine_status,
            required_params=["medicine_id", "status"],
            description="Update medicine status (active/discontinued/under_review)"
        )
    
    def _get_medicine_details(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed medicine information."""
        try:
            medicine_id = params["medicine_id"]
            
            medicine = self.db.get_medicine(medicine_id)
            if not medicine:
                return {
                    "status": "not_found",
                    "message": f"Medicine {medicine_id} not found"
                }
            
            # Get formulation if available
            formulation = self.db.get_formulation(medicine_id)
            
            # Get active batches
            batches = self.db.get_batches_by_status("in_production")
            medicine_batches = [b for b in batches if b.get("medicine_id") == medicine_id]
            
            return {
                "status": "success",
                "medicine": medicine,
                "formulation": formulation,
                "active_batches": len(medicine_batches),
                "batch_details": medicine_batches[:5]  # Last 5 batches
            }
            
        except Exception as e:
            logger.error(f"Error getting medicine details: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _search_medicines(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search medicines by query."""
        try:
            query = params["query"]
            
            medicines = self.db.search_medicines(query)
            
            return {
                "status": "success",
                "query": query,
                "results_count": len(medicines),
                "medicines": medicines
            }
            
        except Exception as e:
            logger.error(f"Error searching medicines: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _get_formulation_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get formulation details."""
        try:
            medicine_id = params["medicine_id"]
            
            formulation = self.db.get_formulation(medicine_id)
            if not formulation:
                return {
                    "status": "not_found",
                    "message": f"Formulation for medicine {medicine_id} not found"
                }
            
            # Get medicine name
            medicine = self.db.get_medicine(medicine_id)
            
            return {
                "status": "success",
                "medicine_name": medicine.get("name") if medicine else "Unknown",
                "formulation": formulation
            }
            
        except Exception as e:
            logger.error(f"Error getting formulation info: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _get_similar_formulations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Find similar formulations using vector search."""
        try:
            medicine_id = params["medicine_id"]
            query_vector = params["query_vector"]
            limit = params.get("limit", 5)
            
            # Validate vector
            if not isinstance(query_vector, list) or len(query_vector) != 1536:
                return {
                    "status": "error",
                    "error": "query_vector must be a list of 1536 floats (OpenAI embedding)"
                }
            
            # Perform vector search
            results = self.db.vector_search_formulations(query_vector, limit)
            
            # Filter out the query medicine itself
            filtered_results = [r for r in results if r.get("medicine_id") != medicine_id]
            
            return {
                "status": "success",
                "medicine_id": medicine_id,
                "similar_formulations": filtered_results
            }
            
        except Exception as e:
            logger.error(f"Error finding similar formulations: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _create_medicine(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create new medicine."""
        try:
            medicine_data = params["medicine_data"]
            
            # Validate required fields
            required_fields = ["medicine_id", "name", "dosage_form", "strength"]
            for field in required_fields:
                if field not in medicine_data:
                    return {
                        "status": "error",
                        "error": f"Missing required field: {field}"
                    }
            
            result = self.db.create_medicine(medicine_data)
            
            return {
                "status": "success",
                "message": "Medicine created successfully",
                "medicine_id": medicine_data["medicine_id"]
            }
            
        except Exception as e:
            logger.error(f"Error creating medicine: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _update_medicine_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update medicine status."""
        try:
            medicine_id = params["medicine_id"]
            new_status = params["status"]
            
            # Validate status
            valid_statuses = ["active", "discontinued", "under_review"]
            if new_status not in valid_statuses:
                return {
                    "status": "error",
                    "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
                }
            
            result = self.db.update_medicine_status(medicine_id, new_status)
            
            return {
                "status": "success",
                "message": f"Medicine status updated to {new_status}",
                "medicine_id": medicine_id
            }
            
        except Exception as e:
            logger.error(f"Error updating medicine status: {str(e)}")
            return {"status": "error", "error": str(e)}


# Server initialization
def create_server():
    """Create and return Medicine MCP Server instance."""
    return MedicineMCPServer()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    server = create_server()
    print(f"✅ {server.server_name} v{server.version} initialized")
    print(f"📋 Registered {len(server.list_endpoints())} endpoints")
    
    # Display endpoints
    for endpoint in server.list_endpoints():
        print(f"  - {endpoint['name']}: {endpoint['description']}")
