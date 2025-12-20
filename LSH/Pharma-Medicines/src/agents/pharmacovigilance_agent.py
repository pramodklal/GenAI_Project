"""
Pharma Manufacturing - Pharmacovigilance Agent

AI agent for adverse event monitoring, signal detection, and MedDRA coding.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

from database.astra_helper import get_db_helper

logger = logging.getLogger(__name__)


class PharmacovigilanceAgent:
    """AI Agent for pharmacovigilance and adverse event management."""
    
    def __init__(self):
        self.db = get_db_helper()
        self.agent_name = "Pharmacovigilance Agent"
        
        # MedDRA severity levels
        self.severity_levels = ["mild", "moderate", "severe", "life-threatening", "fatal"]
        
        # Common adverse event categories
        self.ae_categories = {
            "gastrointestinal": ["nausea", "vomiting", "diarrhea", "abdominal pain"],
            "neurological": ["headache", "dizziness", "seizure", "tremor"],
            "cardiovascular": ["chest pain", "palpitations", "hypertension", "hypotension"],
            "dermatological": ["rash", "itching", "urticaria", "angioedema"],
            "respiratory": ["dyspnea", "cough", "bronchospasm", "wheezing"],
            "hematological": ["anemia", "thrombocytopenia", "leukopenia", "bleeding"]
        }
        
        logger.info(f"{self.agent_name} initialized")
    
    def analyze_adverse_event(self, ae_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze adverse event and provide assessment.
        
        Args:
            ae_data: Adverse event data
            
        Returns:
            Analysis with severity assessment and recommendations
        """
        try:
            # Extract key information
            ae_id = ae_data.get("ae_id")
            medicine_id = ae_data.get("medicine_id")
            description = ae_data.get("description", "").lower()
            patient_outcome = ae_data.get("patient_outcome", "recovered")
            
            # Assess severity based on description and outcome
            severity = self._assess_severity(description, patient_outcome)
            
            # Categorize the AE
            category = self._categorize_ae(description)
            
            # Assess causality (relationship to medicine)
            causality = self._assess_causality(ae_data)
            
            # Determine if serious (regulatory definition)
            is_serious = self._is_serious_ae(ae_data)
            
            # Regulatory reporting requirements
            reporting = self._determine_reporting_requirements(severity, is_serious)
            
            # Recommendations
            recommendations = self._generate_recommendations(severity, is_serious, causality)
            
            analysis = {
                "ae_id": ae_id,
                "medicine_id": medicine_id,
                "assessment": {
                    "severity": severity,
                    "category": category,
                    "causality": causality,
                    "is_serious": is_serious
                },
                "regulatory": reporting,
                "recommendations": recommendations,
                "analyzed_at": datetime.utcnow().isoformat(),
                "agent": self.agent_name
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing adverse event: {str(e)}")
            return {"error": str(e)}
    
    def _assess_severity(self, description: str, outcome: str) -> str:
        """Assess severity based on description and outcome."""
        # Fatal outcomes
        if outcome == "fatal" or "death" in description:
            return "fatal"
        
        # Life-threatening indicators
        life_threatening_terms = ["anaphylaxis", "cardiac arrest", "respiratory failure", "shock"]
        if any(term in description for term in life_threatening_terms):
            return "life-threatening"
        
        # Severe indicators
        severe_terms = ["hospitalization", "severe", "emergency", "intensive care"]
        if any(term in description for term in severe_terms):
            return "severe"
        
        # Moderate indicators
        moderate_terms = ["moderate", "persistent", "significant", "troublesome"]
        if any(term in description for term in moderate_terms):
            return "moderate"
        
        # Default to mild
        return "mild"
    
    def _categorize_ae(self, description: str) -> str:
        """Categorize adverse event by body system."""
        for category, keywords in self.ae_categories.items():
            if any(keyword in description for keyword in keywords):
                return category
        return "other"
    
    def _assess_causality(self, ae_data: Dict) -> str:
        """
        Assess causality using WHO-UMC scale.
        Certain, Probable, Possible, Unlikely, Unassessable
        """
        # Simplified causality assessment
        # In production, would use sophisticated algorithms
        
        time_to_onset = ae_data.get("time_to_onset_days", 0)
        concomitant_meds = ae_data.get("concomitant_medications", [])
        dechallenge = ae_data.get("dechallenge_result")  # Did AE resolve on stopping?
        rechallenge = ae_data.get("rechallenge_result")  # Did AE recur on restarting?
        
        # Scoring
        score = 0
        
        # Temporal relationship
        if 0 < time_to_onset <= 30:
            score += 2
        elif time_to_onset > 30:
            score += 1
        
        # Dechallenge
        if dechallenge == "positive":
            score += 2
        
        # Rechallenge
        if rechallenge == "positive":
            score += 3
        
        # Other causes
        if len(concomitant_meds) > 0:
            score -= 1
        
        # Determine causality
        if score >= 7:
            return "certain"
        elif score >= 5:
            return "probable"
        elif score >= 3:
            return "possible"
        elif score >= 1:
            return "unlikely"
        else:
            return "unassessable"
    
    def _is_serious_ae(self, ae_data: Dict) -> bool:
        """
        Determine if AE meets regulatory definition of serious.
        Serious: Results in death, life-threatening, hospitalization, 
        disability, congenital anomaly, or requires intervention
        """
        outcome = ae_data.get("patient_outcome", "").lower()
        description = ae_data.get("description", "").lower()
        
        serious_outcomes = ["fatal", "death", "hospitalization", "disability", "life-threatening"]
        serious_terms = ["hospital", "emergency", "admitted", "intensive care"]
        
        if any(term in outcome for term in serious_outcomes):
            return True
        
        if any(term in description for term in serious_terms):
            return True
        
        return False
    
    def _determine_reporting_requirements(self, severity: str, is_serious: bool) -> Dict:
        """Determine regulatory reporting requirements."""
        reporting = {
            "required": False,
            "timeframe": None,
            "authorities": []
        }
        
        if is_serious:
            reporting["required"] = True
            
            if severity in ["fatal", "life-threatening"]:
                reporting["timeframe"] = "7 calendar days (expedited)"
                reporting["authorities"] = ["FDA", "EMA", "Local Authority"]
            else:
                reporting["timeframe"] = "15 calendar days"
                reporting["authorities"] = ["FDA", "EMA"]
        else:
            reporting["required"] = True
            reporting["timeframe"] = "Periodic reporting (PSUR/PBRER)"
            reporting["authorities"] = ["FDA", "EMA"]
        
        return reporting
    
    def _generate_recommendations(self, severity: str, is_serious: bool, causality: str) -> List[str]:
        """Generate recommendations for AE management."""
        recommendations = []
        
        if is_serious:
            recommendations.append("IMMEDIATE: Notify medical safety team")
            recommendations.append("Complete detailed case investigation")
            recommendations.append("Submit expedited report to regulatory authorities")
        
        if causality in ["certain", "probable"]:
            recommendations.append("Update product labeling if pattern confirmed")
            recommendations.append("Consider risk mitigation measures")
        
        if severity in ["severe", "life-threatening", "fatal"]:
            recommendations.append("Conduct root cause analysis")
            recommendations.append("Review benefit-risk profile")
        
        recommendations.append("Monitor for similar cases (signal detection)")
        recommendations.append("Document in safety database")
        
        return recommendations
    
    def detect_signals(self, medicine_id: str, lookback_days: int = 90) -> Dict[str, Any]:
        """
        Detect safety signals for a medicine.
        Signal: Potential new safety concern
        
        Args:
            medicine_id: Medicine identifier
            lookback_days: Days to analyze
            
        Returns:
            Signal detection report
        """
        try:
            # Get all AEs for the medicine in the period
            # In production, would query adverse_events collection
            total_aes = 45  # Placeholder
            
            # Group by category
            ae_by_category = {
                "gastrointestinal": 15,
                "neurological": 12,
                "cardiovascular": 8,
                "dermatological": 6,
                "respiratory": 3,
                "other": 1
            }
            
            # Calculate expected rates (based on historical data)
            expected_rates = {
                "gastrointestinal": 10,
                "neurological": 10,
                "cardiovascular": 5,
                "dermatological": 5,
                "respiratory": 3,
                "other": 2
            }
            
            # Detect signals (observed > expected threshold)
            signals = []
            for category, observed in ae_by_category.items():
                expected = expected_rates.get(category, 0)
                
                if observed > expected * 1.5:  # 50% increase threshold
                    signals.append({
                        "category": category,
                        "observed_count": observed,
                        "expected_count": expected,
                        "ratio": round(observed / expected, 2) if expected > 0 else 0,
                        "significance": "high" if observed > expected * 2 else "moderate"
                    })
            
            # Get serious AE rate
            serious_count = 8  # Placeholder
            serious_rate = (serious_count / total_aes * 100) if total_aes > 0 else 0
            
            report = {
                "medicine_id": medicine_id,
                "analysis_period_days": lookback_days,
                "total_aes": total_aes,
                "serious_aes": serious_count,
                "serious_ae_rate": round(serious_rate, 2),
                "ae_distribution": ae_by_category,
                "signals_detected": len(signals),
                "signals": signals,
                "recommendation": "REVIEW REQUIRED" if len(signals) > 0 else "No significant signals",
                "next_steps": [
                    "Conduct detailed case review for signal categories",
                    "Compare with literature and competitor products",
                    "Consult medical experts for clinical assessment",
                    "Update Risk Management Plan if needed"
                ] if len(signals) > 0 else ["Continue routine monitoring"],
                "analyzed_at": datetime.utcnow().isoformat(),
                "agent": self.agent_name
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error detecting signals: {str(e)}")
            return {"error": str(e)}
    
    def suggest_meddra_code(self, description: str) -> Dict[str, Any]:
        """
        Suggest MedDRA (Medical Dictionary for Regulatory Activities) code.
        
        Args:
            description: AE description
            
        Returns:
            Suggested MedDRA codes
        """
        try:
            # Simplified MedDRA coding
            # In production, would use actual MedDRA dictionary and NLP
            
            description_lower = description.lower()
            
            # Common MedDRA terms (simplified)
            meddra_mapping = {
                "nausea": {"code": "10028813", "preferred_term": "Nausea"},
                "vomiting": {"code": "10047700", "preferred_term": "Vomiting"},
                "headache": {"code": "10019211", "preferred_term": "Headache"},
                "dizziness": {"code": "10013573", "preferred_term": "Dizziness"},
                "rash": {"code": "10037844", "preferred_term": "Rash"},
                "diarrhea": {"code": "10012735", "preferred_term": "Diarrhoea"},
                "chest pain": {"code": "10008479", "preferred_term": "Chest pain"}
            }
            
            suggestions = []
            for term, coding in meddra_mapping.items():
                if term in description_lower:
                    suggestions.append({
                        "meddra_code": coding["code"],
                        "preferred_term": coding["preferred_term"],
                        "confidence": "high"
                    })
            
            if not suggestions:
                suggestions.append({
                    "meddra_code": "10000000",
                    "preferred_term": "Adverse event NOS (Not Otherwise Specified)",
                    "confidence": "low",
                    "note": "Manual coding required"
                })
            
            result = {
                "description": description,
                "suggestions": suggestions,
                "recommendation": "Review with medical coder for final selection",
                "coded_at": datetime.utcnow().isoformat(),
                "agent": self.agent_name
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error suggesting MedDRA code: {str(e)}")
            return {"error": str(e)}
    
    def find_similar_cases(self, ae_id: str, query_vector: Optional[List[float]] = None, limit: int = 5) -> Dict[str, Any]:
        """
        Find similar adverse event cases using vector search.
        
        Args:
            ae_id: Adverse event ID
            query_vector: Pre-computed embedding (1536D)
            limit: Maximum number of results
            
        Returns:
            Similar cases for pattern analysis
        """
        try:
            if not query_vector:
                return {
                    "message": "Vector embedding required for similarity search",
                    "hint": "Use OpenAI API to generate embedding from AE description"
                }
            
            # Perform vector search
            results = self.db.vector_search_adverse_events(query_vector, limit)
            
            # Format results
            similar_cases = [
                {
                    "ae_id": r.get("ae_id"),
                    "medicine_id": r.get("medicine_id"),
                    "description": r.get("description"),
                    "severity": r.get("severity"),
                    "patient_outcome": r.get("patient_outcome"),
                    "report_date": r.get("report_date"),
                    "similarity_score": r.get("$similarity", 0)
                }
                for r in results
                if r.get("ae_id") != ae_id  # Exclude the query case itself
            ]
            
            # Pattern analysis
            if similar_cases:
                severity_distribution = {}
                for case in similar_cases:
                    sev = case.get("severity", "unknown")
                    severity_distribution[sev] = severity_distribution.get(sev, 0) + 1
            else:
                severity_distribution = {}
            
            result = {
                "query_ae_id": ae_id,
                "similar_cases_found": len(similar_cases),
                "cases": similar_cases,
                "pattern_analysis": {
                    "severity_distribution": severity_distribution,
                    "common_pattern": len(similar_cases) >= 3
                },
                "recommendation": "Investigate pattern" if len(similar_cases) >= 3 else "Isolated case",
                "searched_at": datetime.utcnow().isoformat(),
                "agent": self.agent_name
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error finding similar cases: {str(e)}")
            return {"error": str(e)}


# Main execution for testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    agent = PharmacovigilanceAgent()
    print(f"✅ {agent.agent_name} initialized successfully")
    
    # Test AE analysis
    # sample_ae = {
    #     "ae_id": "AE-2025-001",
    #     "medicine_id": "MED-001",
    #     "description": "Patient experienced severe nausea and vomiting",
    #     "patient_outcome": "recovered",
    #     "time_to_onset_days": 2
    # }
    # result = agent.analyze_adverse_event(sample_ae)
    # print(json.dumps(result, indent=2))
