"""
Pharma Manufacturing - Quality Control Agent

AI agent for automated QC analysis, OOS detection, and batch release decisions.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List, Any
from datetime import datetime
import logging

from database.astra_helper import get_db_helper

logger = logging.getLogger(__name__)


class QualityControlAgent:
    """AI Agent for quality control analysis and decision support."""
    
    def __init__(self):
        self.db = get_db_helper()
        self.agent_name = "Quality Control Agent"
        logger.info(f"{self.agent_name} initialized")
    
    def analyze_test_results(self, batch_id: str) -> Dict[str, Any]:
        """
        Analyze all QC test results for a batch.
        
        Args:
            batch_id: Batch identifier
            
        Returns:
            Analysis summary with recommendations
        """
        try:
            # Get all QC tests for the batch
            tests = self.db.get_qc_tests(batch_id)
            
            if not tests:
                return {
                    "status": "no_tests",
                    "message": "No QC tests found for this batch",
                    "batch_id": batch_id
                }
            
            # Analyze test results
            total_tests = len(tests)
            passed_tests = sum(1 for t in tests if t.get("pass_fail_status") == "pass")
            failed_tests = sum(1 for t in tests if t.get("pass_fail_status") == "fail")
            pending_tests = sum(1 for t in tests if t.get("pass_fail_status") == "pending")
            
            pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
            
            # Detect OOS (Out of Specification)
            oos_tests = [t for t in tests if t.get("pass_fail_status") == "fail"]
            
            # Determine recommendation
            if pending_tests > 0:
                recommendation = "PENDING - Awaiting test completion"
                decision = "pending"
            elif failed_tests > 0:
                recommendation = "REJECT - Out of specification detected"
                decision = "reject"
            elif pass_rate >= 100:
                recommendation = "APPROVE - All tests passed"
                decision = "approve"
            else:
                recommendation = "RETEST - Incomplete results"
                decision = "retest"
            
            analysis = {
                "batch_id": batch_id,
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "pending": pending_tests,
                "pass_rate": round(pass_rate, 2),
                "oos_tests": len(oos_tests),
                "oos_details": [
                    {
                        "test_type": t.get("test_type"),
                        "test_id": t.get("test_id"),
                        "result": t.get("results", {}).get("value"),
                        "specification": t.get("parameters", {}).get("specification")
                    }
                    for t in oos_tests
                ],
                "recommendation": recommendation,
                "decision": decision,
                "analyzed_at": datetime.utcnow().isoformat(),
                "agent": self.agent_name
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing test results: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "batch_id": batch_id
            }
    
    def detect_oos(self, test_results: List[Dict]) -> List[Dict]:
        """
        Detect Out-of-Specification test results.
        
        Args:
            test_results: List of test result dictionaries
            
        Returns:
            List of OOS test results with details
        """
        try:
            oos_results = []
            
            for test in test_results:
                if test.get("pass_fail_status") == "fail":
                    oos_detail = {
                        "test_id": test.get("test_id"),
                        "batch_id": test.get("batch_id"),
                        "test_type": test.get("test_type"),
                        "result_value": test.get("results", {}).get("value"),
                        "unit": test.get("results", {}).get("unit"),
                        "specification": test.get("parameters", {}).get("specification"),
                        "acceptance_criteria": test.get("parameters", {}).get("acceptance_criteria"),
                        "deviation": self._calculate_deviation(test),
                        "severity": self._assess_severity(test),
                        "recommended_action": self._recommend_action(test)
                    }
                    oos_results.append(oos_detail)
            
            return oos_results
            
        except Exception as e:
            logger.error(f"Error detecting OOS: {str(e)}")
            return []
    
    def _calculate_deviation(self, test: Dict) -> str:
        """Calculate percentage deviation from specification."""
        try:
            result_value = test.get("results", {}).get("value")
            spec = test.get("parameters", {}).get("specification", "")
            
            # Simple parser for specifications like "≥80%"
            if isinstance(result_value, (int, float)):
                if "≥" in spec:
                    target = float(spec.replace("≥", "").replace("%", "").strip())
                    deviation = ((result_value - target) / target) * 100
                    return f"{deviation:+.2f}%"
                elif "≤" in spec:
                    target = float(spec.replace("≤", "").replace("%", "").strip())
                    deviation = ((result_value - target) / target) * 100
                    return f"{deviation:+.2f}%"
            
            return "N/A"
        except:
            return "N/A"
    
    def _assess_severity(self, test: Dict) -> str:
        """Assess severity of OOS result."""
        test_type = test.get("test_type", "").lower()
        
        # Critical tests
        if test_type in ["microbial", "sterility", "endotoxin"]:
            return "critical"
        
        # Major tests
        if test_type in ["assay", "dissolution", "content_uniformity"]:
            return "major"
        
        # Minor tests
        return "minor"
    
    def _recommend_action(self, test: Dict) -> str:
        """Recommend corrective action for OOS."""
        severity = self._assess_severity(test)
        test_type = test.get("test_type", "")
        
        if severity == "critical":
            return f"IMMEDIATE ACTION: Investigate {test_type} failure. Batch must be rejected until investigation complete."
        elif severity == "major":
            return f"REQUIRED: Conduct OOS investigation for {test_type}. Retest may be warranted."
        else:
            return f"REVIEW: Assess {test_type} result. Document findings."
    
    def generate_coa(self, batch_id: str) -> Dict[str, Any]:
        """
        Generate Certificate of Analysis for approved batch.
        
        Args:
            batch_id: Batch identifier
            
        Returns:
            COA document data
        """
        try:
            # Get batch details
            batch = self.db.get_batch(batch_id)
            if not batch:
                return {"error": "Batch not found"}
            
            # Get medicine details
            medicine = self.db.get_medicine(batch.get("medicine_id"))
            
            # Get test results
            tests = self.db.get_qc_tests(batch_id)
            
            # Check if batch is approved
            if batch.get("status") != "approved":
                return {
                    "error": "Cannot generate COA for non-approved batch",
                    "current_status": batch.get("status")
                }
            
            # Build COA
            coa = {
                "coa_number": f"COA-{batch.get('batch_number')}",
                "batch_id": batch_id,
                "batch_number": batch.get("batch_number"),
                "medicine_name": medicine.get("name") if medicine else "Unknown",
                "manufacturing_date": batch.get("manufacturing_date"),
                "expiry_date": batch.get("expiry_date"),
                "quantity": batch.get("quantity"),
                "yield_percentage": batch.get("yield_percentage", 0),
                "test_results": [
                    {
                        "test_type": t.get("test_type"),
                        "specification": t.get("parameters", {}).get("specification"),
                        "result": t.get("results", {}).get("value"),
                        "unit": t.get("results", {}).get("unit"),
                        "status": t.get("pass_fail_status"),
                        "tested_by": t.get("tested_by"),
                        "test_date": t.get("test_date")
                    }
                    for t in tests
                ],
                "approved_by": batch.get("approved_by"),
                "approved_date": batch.get("approved_date"),
                "conclusion": "This batch meets all specifications and is released for commercial use.",
                "generated_at": datetime.utcnow().isoformat(),
                "generated_by": self.agent_name
            }
            
            return coa
            
        except Exception as e:
            logger.error(f"Error generating COA: {str(e)}")
            return {"error": str(e)}
    
    def recommend_batch_decision(self, batch_id: str) -> str:
        """
        Provide AI recommendation for batch release decision.
        
        Args:
            batch_id: Batch identifier
            
        Returns:
            Decision recommendation (approve/reject/retest/pending)
        """
        try:
            analysis = self.analyze_test_results(batch_id)
            
            if analysis.get("status") == "error":
                return "error"
            
            if analysis.get("status") == "no_tests":
                return "pending"
            
            return analysis.get("decision", "pending")
            
        except Exception as e:
            logger.error(f"Error recommending batch decision: {str(e)}")
            return "error"
    
    def validate_batch_quality(self, batch_id: str) -> Dict[str, Any]:
        """
        Comprehensive batch quality validation.
        
        Args:
            batch_id: Batch identifier
            
        Returns:
            Validation report
        """
        try:
            # Analyze test results
            analysis = self.analyze_test_results(batch_id)
            
            # Get batch info
            batch = self.db.get_batch(batch_id)
            
            # Validate yield
            yield_ok = True
            yield_message = "Acceptable"
            if batch:
                yield_pct = batch.get("yield_percentage", 0)
                if yield_pct < 90:
                    yield_ok = False
                    yield_message = f"Low yield: {yield_pct}%"
            
            # Overall validation
            is_valid = (
                analysis.get("decision") == "approve" and
                yield_ok and
                analysis.get("oos_tests", 0) == 0
            )
            
            validation = {
                "batch_id": batch_id,
                "is_valid": is_valid,
                "qc_analysis": analysis,
                "yield_validation": {
                    "ok": yield_ok,
                    "message": yield_message,
                    "value": batch.get("yield_percentage") if batch else None
                },
                "overall_recommendation": "RELEASE" if is_valid else "HOLD",
                "validated_at": datetime.utcnow().isoformat(),
                "agent": self.agent_name
            }
            
            return validation
            
        except Exception as e:
            logger.error(f"Error validating batch quality: {str(e)}")
            return {
                "batch_id": batch_id,
                "is_valid": False,
                "error": str(e)
            }


# Main execution for testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    agent = QualityControlAgent()
    print(f"✅ {agent.agent_name} initialized successfully")
    
    # Test with sample batch_id
    # result = agent.analyze_test_results("BATCH-2025-001")
    # print(json.dumps(result, indent=2))
