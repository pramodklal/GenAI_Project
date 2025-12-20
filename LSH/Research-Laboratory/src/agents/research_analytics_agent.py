"""
Research Analytics Agent
Handles data analytics, reporting, and insights across research operations
"""

import os
from openai import OpenAI
from datetime import datetime
import json

class ResearchAnalyticsAgent:
    """Agent for research data analytics and reporting"""
    
    def __init__(self, db_helper):
        self.db = db_helper
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "gpt-4o"
        
    def generate_research_dashboard(self) -> dict:
        """Generate comprehensive research dashboard metrics"""
        try:
            # Collect metrics from all collections
            projects = self.db.query_documents('research_projects', {})
            trials = self.db.query_documents('clinical_trials', {})
            candidates = self.db.query_documents('drug_candidates', {})
            experiments = self.db.query_documents('lab_experiments', {})
            publications = self.db.query_documents('research_publications', {})
            
            metrics = {
                "research_projects": {
                    "total": len(projects),
                    "active": len([p for p in projects if p.get('status') == 'Active']),
                    "completed": len([p for p in projects if p.get('status') == 'Completed'])
                },
                "clinical_trials": {
                    "total": len(trials),
                    "ongoing": len([t for t in trials if t.get('status') == 'Ongoing']),
                    "recruiting": len([t for t in trials if t.get('status') == 'Recruiting'])
                },
                "drug_candidates": {
                    "total": len(candidates),
                    "by_stage": {}
                },
                "lab_experiments": {
                    "total": len(experiments),
                    "completed": len([e for e in experiments if e.get('status') == 'Completed'])
                },
                "publications": {
                    "total": len(publications)
                }
            }
            
            # Analyze drug candidate stages
            for candidate in candidates:
                stage = candidate.get('development_stage', 'Unknown')
                metrics["drug_candidates"]["by_stage"][stage] = \
                    metrics["drug_candidates"]["by_stage"].get(stage, 0) + 1
            
            return metrics
            
        except Exception as e:
            return {"error": str(e)}
    
    def generate_executive_report(self) -> str:
        """Generate executive summary report"""
        try:
            dashboard = self.generate_research_dashboard()
            
            prompt = f"""
            Generate an executive summary report for research operations:
            
            Metrics:
            {json.dumps(dashboard, indent=2)}
            
            Include:
            1. Executive Summary (key highlights)
            2. Research Portfolio Overview
            3. Clinical Trial Progress
            4. Drug Development Pipeline
            5. Research Output (publications)
            6. Key Achievements
            7. Challenges and Risks
            8. Strategic Recommendations
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a research operations executive reporting specialist."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error generating report: {str(e)}"
    
    def predict_project_timeline(self, project_id: str) -> dict:
        """Predict project completion timeline"""
        try:
            project = self.db.get_document_by_id('research_projects', project_id)
            experiments = self.db.query_documents('lab_experiments', {'project_id': project_id})
            
            prompt = f"""
            Predict project timeline and completion:
            
            Project Data:
            {json.dumps(project, indent=2)}
            
            Experiments: {len(experiments)} total
            Completed: {len([e for e in experiments if e.get('status') == 'Completed'])}
            
            Provide:
            1. Expected completion date
            2. Current progress percentage
            3. Timeline risks
            4. Acceleration opportunities
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a research project timeline analyst."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return {
                "project_id": project_id,
                "prediction": response.choices[0].message.content,
                "predicted_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def identify_bottlenecks(self) -> dict:
        """Identify operational bottlenecks across research activities"""
        try:
            dashboard = self.generate_research_dashboard()
            
            prompt = f"""
            Identify operational bottlenecks in research operations:
            
            Current State:
            {json.dumps(dashboard, indent=2)}
            
            Analyze:
            1. Resource constraints
            2. Process inefficiencies
            3. Timeline delays
            4. Capacity issues
            5. Priority recommendations
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an operations efficiency consultant."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return {
                "analysis": response.choices[0].message.content,
                "analyzed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e)}
