"""
Quality Control MCP Server - v1.0.0

MCP server for QC testing, batch approval, and Certificate of Analysis generation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Any
import logging

from mcp_servers.base_mcp_server import MCPServerBase
from database.astra_helper import get_db_helper
from agents.quality_control_agent import QualityControlAgent

logger = logging.getLogger(__name__)


class QualityControlMCPServer(MCPServerBase):
    """MCP Server for quality control operations."""
    
    def __init__(self):
        super().__init__("Quality Control MCP Server", "1.0.0")
        self.db = get_db_helper()
        self.qc_agent = QualityControlAgent()
    
    def _register_endpoints(self):
        """Register all QC-related endpoints."""
        
        self.register_endpoint(
            name="submit_qc_test",
            handler=self._submit_qc_test,
            required_params=["test_data"],
            description="Submit QC test results for a batch"
        )
        
        self.register_endpoint(
            name="get_qc_results",
            handler=self._get_qc_results,
            required_params=["batch_id"],
            description="Get all QC test results for a batch"
        )
        
        self.register_endpoint(
            name="validate_batch_quality",
            handler=self._validate_batch_quality,
            required_params=["batch_id"],
            description="AI-powered batch quality validation using QC Agent"
        )
        
        self.register_endpoint(
            name="get_oos_investigations",
            handler=self._get_oos_investigations,
            required_params=[],
            description="Get all Out-of-Specification investigations"
        )
        
        self.register_endpoint(
            name="approve_batch",
            handler=self._approve_batch,
            required_params=["batch_id", "approved_by"],
            description="Approve a batch for release (requires QC validation)"
        )
        
        self.register_endpoint(
            name="generate_coa",
            handler=self._generate_coa,
            required_params=["batch_id"],
            description="Generate Certificate of Analysis for approved batch"
        )
    
    def _submit_qc_test(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Submit QC test results."""
        try:
            test_data = params["test_data"]
            
            # Validate required fields
            required_fields = ["test_id", "batch_id", "test_type", "results"]
            for field in required_fields:
                if field not in test_data:
                    return {
                        "status": "error",
                        "error": f"Missing required field: {field}"
                    }
            
            result = self.db.submit_qc_test(test_data)
            
            # Analyze the test result
            batch_id = test_data["batch_id"]
            analysis = self.qc_agent.analyze_test_results(batch_id)
            
            return {
                "status": "success",
                "message": "QC test submitted successfully",
                "test_id": test_data["test_id"],
                "batch_analysis": analysis
            }
            
        except Exception as e:
            logger.error(f"Error submitting QC test: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _get_qc_results(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get QC results for a batch."""
        try:
            batch_id = params["batch_id"]
            
            tests = self.db.get_qc_tests(batch_id)
            
            if not tests:
                return {
                    "status": "not_found",
                    "message": f"No QC tests found for batch {batch_id}"
                }
            
            # Get batch info
            batch = self.db.get_batch(batch_id)
            
            return {
                "status": "success",
                "batch_id": batch_id,
                "batch_number": batch.get("batch_number") if batch else None,
                "test_count": len(tests),
                "tests": tests
            }
            
        except Exception as e:
            logger.error(f"Error getting QC results: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _validate_batch_quality(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """AI-powered batch quality validation."""
        try:
            batch_id = params["batch_id"]
            
            # Use QC Agent for comprehensive validation
            validation = self.qc_agent.validate_batch_quality(batch_id)
            
            return {
                "status": "success",
                "validation": validation
            }
            
        except Exception as e:
            logger.error(f"Error validating batch quality: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _get_oos_investigations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get OOS investigations."""
        try:
            oos_tests = self.db.get_oos_tests()
            
            # Detect OOS details using agent
            oos_details = self.qc_agent.detect_oos(oos_tests)
            
            return {
                "status": "success",
                "total_oos": len(oos_tests),
                "investigations": oos_details
            }
            
        except Exception as e:
            logger.error(f"Error getting OOS investigations: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _approve_batch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Approve batch for release."""
        try:
            batch_id = params["batch_id"]
            approved_by = params["approved_by"]
            
            # First validate the batch
            validation = self.qc_agent.validate_batch_quality(batch_id)
            
            if not validation.get("is_valid"):
                return {
                    "status": "rejected",
                    "message": "Batch failed quality validation",
                    "validation": validation
                }
            
            # Get AI recommendation
            recommendation = self.qc_agent.recommend_batch_decision(batch_id)
            
            if recommendation != "approve":
                return {
                    "status": "rejected",
                    "message": f"AI Agent recommends: {recommendation}",
                    "recommendation": recommendation
                }
            
            # Update batch status
            from datetime import datetime
            result = self.db.update_batch_status(
                batch_id=batch_id,
                new_status="approved",
                approved_by=approved_by,
                approved_date=datetime.utcnow().isoformat()
            )
            
            return {
                "status": "success",
                "message": "Batch approved for release",
                "batch_id": batch_id,
                "approved_by": approved_by
            }
            
        except Exception as e:
            logger.error(f"Error approving batch: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _generate_coa(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Certificate of Analysis."""
        try:
            batch_id = params["batch_id"]
            
            # Use QC Agent to generate COA
            coa = self.qc_agent.generate_coa(batch_id)
            
            if "error" in coa:
                return {
                    "status": "error",
                    "error": coa["error"]
                }
            
            return {
                "status": "success",
                "coa": coa
            }
            
        except Exception as e:
            logger.error(f"Error generating COA: {str(e)}")
            return {"status": "error", "error": str(e)}


# Server initialization
def create_server():
    """Create and return Quality Control MCP Server instance."""
    return QualityControlMCPServer()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    server = create_server()
    print(f"✅ {server.server_name} v{server.version} initialized")
    print(f"📋 Registered {len(server.list_endpoints())} endpoints")
    
    # Display endpoints
    for endpoint in server.list_endpoints():
        print(f"  - {endpoint['name']}: {endpoint['description']}")
