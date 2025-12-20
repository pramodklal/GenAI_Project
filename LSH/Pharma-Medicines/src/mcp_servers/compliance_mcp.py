"""
Compliance MCP Server - v1.0.0

MCP server for regulatory compliance, adverse event reporting, and audit management.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Any
import logging

from mcp_servers.base_mcp_server import MCPServerBase
from database.astra_helper import get_db_helper
from agents.regulatory_compliance_agent import RegulatoryComplianceAgent
from agents.pharmacovigilance_agent import PharmacovigilanceAgent

logger = logging.getLogger(__name__)


class ComplianceMCPServer(MCPServerBase):
    """MCP Server for regulatory compliance operations."""
    
    def __init__(self):
        super().__init__("Compliance MCP Server", "1.0.0")
        self.db = get_db_helper()
        self.compliance_agent = RegulatoryComplianceAgent()
        self.pv_agent = PharmacovigilanceAgent()
    
    def _register_endpoints(self):
        """Register all compliance-related endpoints."""
        
        self.register_endpoint(
            name="check_regulatory_compliance",
            handler=self._check_regulatory_compliance,
            required_params=["batch_id"],
            description="Check batch compliance with FDA/EMA/GMP requirements"
        )
        
        self.register_endpoint(
            name="get_expiring_documents",
            handler=self._get_expiring_documents,
            required_params=["days_ahead"],
            description="Get regulatory documents expiring within specified period"
        )
        
        self.register_endpoint(
            name="submit_adverse_event",
            handler=self._submit_adverse_event,
            required_params=["ae_data"],
            description="Submit and analyze adverse event report"
        )
        
        self.register_endpoint(
            name="generate_audit_report",
            handler=self._generate_audit_report,
            required_params=["start_date", "end_date"],
            description="Generate audit trail report for specified period"
        )
        
        self.register_endpoint(
            name="search_regulations",
            handler=self._search_regulations,
            required_params=["query", "query_vector"],
            description="Search regulatory SOPs using vector search"
        )
        
        self.register_endpoint(
            name="validate_gmp_compliance",
            handler=self._validate_gmp_compliance,
            required_params=["batch_id"],
            description="Validate GMP (Good Manufacturing Practice) compliance"
        )
    
    def _check_regulatory_compliance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check batch regulatory compliance."""
        try:
            batch_id = params["batch_id"]
            
            # Use Compliance Agent for validation
            validation = self.compliance_agent.validate_batch_compliance(batch_id)
            
            return {
                "status": "success",
                "compliance_validation": validation
            }
            
        except Exception as e:
            logger.error(f"Error checking regulatory compliance: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _get_expiring_documents(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get expiring regulatory documents."""
        try:
            days_ahead = params.get("days_ahead", 30)
            
            # Use Compliance Agent
            report = self.compliance_agent.check_document_expiry(days_ahead)
            
            return {
                "status": "success",
                "expiry_report": report
            }
            
        except Exception as e:
            logger.error(f"Error getting expiring documents: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _submit_adverse_event(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Submit and analyze adverse event."""
        try:
            ae_data = params["ae_data"]
            
            # Validate required fields
            required_fields = ["ae_id", "medicine_id", "description", "patient_outcome"]
            for field in required_fields:
                if field not in ae_data:
                    return {
                        "status": "error",
                        "error": f"Missing required field: {field}"
                    }
            
            # Analyze using Pharmacovigilance Agent
            analysis = self.pv_agent.analyze_adverse_event(ae_data)
            
            # Submit to database (with vector if provided)
            vector = ae_data.get("vector")
            result = self.db.submit_adverse_event(ae_data, vector)
            
            # Suggest MedDRA code
            meddra_suggestions = self.pv_agent.suggest_meddra_code(ae_data["description"])
            
            return {
                "status": "success",
                "message": "Adverse event submitted and analyzed",
                "ae_id": ae_data["ae_id"],
                "analysis": analysis,
                "meddra_suggestions": meddra_suggestions
            }
            
        except Exception as e:
            logger.error(f"Error submitting adverse event: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _generate_audit_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate audit trail report."""
        try:
            start_date = params["start_date"]
            end_date = params["end_date"]
            entity_type = params.get("entity_type")
            
            # Use Compliance Agent
            report = self.compliance_agent.generate_audit_report(
                start_date=start_date,
                end_date=end_date,
                entity_type=entity_type
            )
            
            return {
                "status": "success",
                "audit_report": report
            }
            
        except Exception as e:
            logger.error(f"Error generating audit report: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _search_regulations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search regulatory SOPs using vector search."""
        try:
            query = params["query"]
            query_vector = params["query_vector"]
            limit = params.get("limit", 5)
            
            # Validate vector
            if not isinstance(query_vector, list) or len(query_vector) != 1536:
                return {
                    "status": "error",
                    "error": "query_vector must be a list of 1536 floats (OpenAI embedding)"
                }
            
            # Use Compliance Agent
            results = self.compliance_agent.search_regulations(query, query_vector, limit)
            
            return {
                "status": "success",
                "search_results": results
            }
            
        except Exception as e:
            logger.error(f"Error searching regulations: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _validate_gmp_compliance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate GMP compliance."""
        try:
            batch_id = params["batch_id"]
            
            # Use Compliance Agent
            validation = self.compliance_agent.validate_gmp_compliance(batch_id)
            
            return {
                "status": "success",
                "gmp_validation": validation
            }
            
        except Exception as e:
            logger.error(f"Error validating GMP compliance: {str(e)}")
            return {"status": "error", "error": str(e)}


# Server initialization
def create_server():
    """Create and return Compliance MCP Server instance."""
    return ComplianceMCPServer()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    server = create_server()
    print(f"✅ {server.server_name} v{server.version} initialized")
    print(f"📋 Registered {len(server.list_endpoints())} endpoints")
    
    # Display endpoints
    for endpoint in server.list_endpoints():
        print(f"  - {endpoint['name']}: {endpoint['description']}")
