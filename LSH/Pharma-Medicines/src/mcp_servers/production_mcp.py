"""
Production MCP Server - v1.0.0

MCP server for production scheduling, batch management, and resource allocation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Any
import logging

from mcp_servers.base_mcp_server import MCPServerBase
from database.astra_helper import get_db_helper
from agents.production_optimization_agent import ProductionOptimizationAgent

logger = logging.getLogger(__name__)


class ProductionMCPServer(MCPServerBase):
    """MCP Server for production operations."""
    
    def __init__(self):
        super().__init__("Production MCP Server", "1.0.0")
        self.db = get_db_helper()
        self.prod_agent = ProductionOptimizationAgent()
    
    def _register_endpoints(self):
        """Register all production-related endpoints."""
        
        self.register_endpoint(
            name="create_batch",
            handler=self._create_batch,
            required_params=["batch_data"],
            description="Create a new manufacturing batch"
        )
        
        self.register_endpoint(
            name="get_batch_status",
            handler=self._get_batch_status,
            required_params=["batch_id"],
            description="Get current status and details of a batch"
        )
        
        self.register_endpoint(
            name="update_batch_stage",
            handler=self._update_batch_stage,
            required_params=["batch_id", "new_stage"],
            description="Update batch manufacturing stage"
        )
        
        self.register_endpoint(
            name="get_production_schedule",
            handler=self._get_production_schedule,
            required_params=["week_offset"],
            description="Get optimized production schedule for specified week"
        )
        
        self.register_endpoint(
            name="allocate_equipment",
            handler=self._allocate_equipment,
            required_params=["batch_id"],
            description="Get optimal equipment allocation for a batch"
        )
        
        self.register_endpoint(
            name="calculate_material_requirements",
            handler=self._calculate_material_requirements,
            required_params=["batch_id"],
            description="Calculate material requirements for batch production"
        )
    
    def _create_batch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create new manufacturing batch."""
        try:
            batch_data = params["batch_data"]
            
            # Validate required fields
            required_fields = ["batch_id", "batch_number", "medicine_id", "quantity"]
            for field in required_fields:
                if field not in batch_data:
                    return {
                        "status": "error",
                        "error": f"Missing required field: {field}"
                    }
            
            # Check material requirements first
            batch_id = batch_data["batch_id"]
            material_check = self.prod_agent.calculate_material_requirements(batch_id)
            
            if not material_check.get("can_proceed"):
                return {
                    "status": "insufficient_materials",
                    "message": "Cannot create batch due to material shortages",
                    "material_requirements": material_check
                }
            
            # Create batch
            result = self.db.create_batch(batch_data)
            
            # Predict yield
            yield_prediction = self.prod_agent.predict_yield(batch_id)
            
            return {
                "status": "success",
                "message": "Batch created successfully",
                "batch_id": batch_id,
                "batch_number": batch_data["batch_number"],
                "yield_prediction": yield_prediction
            }
            
        except Exception as e:
            logger.error(f"Error creating batch: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _get_batch_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get batch status."""
        try:
            batch_id = params["batch_id"]
            
            batch = self.db.get_batch(batch_id)
            if not batch:
                return {
                    "status": "not_found",
                    "message": f"Batch {batch_id} not found"
                }
            
            # Get medicine info
            medicine = self.db.get_medicine(batch.get("medicine_id"))
            
            # Get QC tests
            qc_tests = self.db.get_qc_tests(batch_id)
            
            return {
                "status": "success",
                "batch": batch,
                "medicine": medicine,
                "qc_tests_count": len(qc_tests),
                "current_stage": batch.get("current_stage"),
                "batch_status": batch.get("status")
            }
            
        except Exception as e:
            logger.error(f"Error getting batch status: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _update_batch_stage(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update batch manufacturing stage."""
        try:
            batch_id = params["batch_id"]
            new_stage = params["new_stage"]
            
            # Validate stage
            valid_stages = ["mixing", "granulation", "compression", "coating", "packaging", "completed"]
            if new_stage not in valid_stages:
                return {
                    "status": "error",
                    "error": f"Invalid stage. Must be one of: {', '.join(valid_stages)}"
                }
            
            result = self.db.update_batch_stage(batch_id, new_stage)
            
            return {
                "status": "success",
                "message": f"Batch stage updated to {new_stage}",
                "batch_id": batch_id,
                "new_stage": new_stage
            }
            
        except Exception as e:
            logger.error(f"Error updating batch stage: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _get_production_schedule(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get optimized production schedule."""
        try:
            week_offset = params.get("week_offset", 0)
            
            # Use Production Agent for optimization
            schedule = self.prod_agent.optimize_batch_schedule(week_offset)
            
            # Check for bottlenecks
            bottlenecks = self.prod_agent.identify_bottlenecks()
            
            return {
                "status": "success",
                "schedule": schedule,
                "bottleneck_analysis": bottlenecks
            }
            
        except Exception as e:
            logger.error(f"Error getting production schedule: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _allocate_equipment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get optimal equipment allocation."""
        try:
            batch_id = params["batch_id"]
            
            # Use Production Agent for optimization
            allocation = self.prod_agent.optimize_equipment_allocation(batch_id)
            
            return {
                "status": "success",
                "allocation": allocation
            }
            
        except Exception as e:
            logger.error(f"Error allocating equipment: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _calculate_material_requirements(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate material requirements."""
        try:
            batch_id = params["batch_id"]
            
            # Use Production Agent for calculation
            requirements = self.prod_agent.calculate_material_requirements(batch_id)
            
            return {
                "status": "success",
                "requirements": requirements
            }
            
        except Exception as e:
            logger.error(f"Error calculating material requirements: {str(e)}")
            return {"status": "error", "error": str(e)}


# Server initialization
def create_server():
    """Create and return Production MCP Server instance."""
    return ProductionMCPServer()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    server = create_server()
    print(f"✅ {server.server_name} v{server.version} initialized")
    print(f"📋 Registered {len(server.list_endpoints())} endpoints")
    
    # Display endpoints
    for endpoint in server.list_endpoints():
        print(f"  - {endpoint['name']}: {endpoint['description']}")
