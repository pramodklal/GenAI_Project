"""
Laboratory Experiment Agent
Handles lab experiment tracking, data analysis, and protocol management
"""

import os
from openai import OpenAI
from datetime import datetime
import json

class LabExperimentAgent:
    """Agent for laboratory experiment management and analysis"""
    
    def __init__(self, db_helper):
        self.db = db_helper
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "gpt-4o"
        
    def analyze_experiment_results(self, experiment_id: str) -> dict:
        """Analyze experiment results and provide insights"""
        try:
            experiment = self.db.get_document_by_id('lab_experiments', experiment_id)
            
            if not experiment:
                return {"error": "Experiment not found"}
            
            prompt = f"""
            Analyze these laboratory experiment results:
            
            {json.dumps(experiment, indent=2)}
            
            Provide:
            1. Results interpretation
            2. Statistical significance assessment
            3. Comparison with expected outcomes
            4. Anomalies or concerns
            5. Recommendations for follow-up
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a laboratory research scientist."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return {
                "experiment_id": experiment_id,
                "analysis": response.choices[0].message.content,
                "analyzed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def suggest_experiment_protocol(self, objective: str, compound: str) -> str:
        """Suggest experimental protocol based on objective"""
        try:
            prompt = f"""
            Design a laboratory experiment protocol:
            
            Objective: {objective}
            Compound/Subject: {compound}
            
            Provide detailed protocol including:
            1. Materials needed
            2. Step-by-step procedure
            3. Safety considerations
            4. Expected outcomes
            5. Data collection methods
            6. Analysis approach
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an experienced laboratory protocol designer."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error generating protocol: {str(e)}"
    
    def track_experiment_progress(self, project_id: str) -> dict:
        """Track all experiments for a research project"""
        try:
            experiments = self.db.query_documents(
                'lab_experiments',
                {'project_id': project_id}
            )
            
            status_summary = {}
            for exp in experiments:
                status = exp.get('status', 'Unknown')
                status_summary[status] = status_summary.get(status, 0) + 1
            
            return {
                "project_id": project_id,
                "total_experiments": len(experiments),
                "status_summary": status_summary,
                "experiments": experiments,
                "tracked_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def compare_experiments(self, experiment_ids: list) -> dict:
        """Compare results across multiple experiments"""
        try:
            experiments = []
            for exp_id in experiment_ids:
                exp = self.db.get_document_by_id('lab_experiments', exp_id)
                if exp:
                    experiments.append(exp)
            
            if not experiments:
                return {"error": "No experiments found"}
            
            prompt = f"""
            Compare these laboratory experiments:
            
            {json.dumps(experiments, indent=2)}
            
            Provide:
            1. Key similarities and differences
            2. Trend analysis
            3. Best performing conditions
            4. Insights for optimization
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a research data analyst."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return {
                "compared_experiments": len(experiments),
                "comparison": response.choices[0].message.content,
                "compared_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e)}
