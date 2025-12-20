"""
Clinical Trial Management Agent
Handles clinical trial operations, participant management, and protocol compliance
"""

import os
from openai import OpenAI
from datetime import datetime
import json

class ClinicalTrialAgent:
    """Agent for managing clinical trials and participant data"""
    
    def __init__(self, db_helper):
        self.db = db_helper
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "gpt-4o"
        
    def analyze_trial_data(self, trial_id: str) -> dict:
        """Analyze clinical trial data and provide insights"""
        try:
            # Get trial data
            trial = self.db.get_document_by_id('clinical_trials', trial_id)
            
            if not trial:
                return {"error": "Trial not found"}
            
            # Get participants
            participants = self.db.query_documents(
                'trial_participants',
                {'trial_id': trial_id}
            )
            
            # Analyze with AI
            prompt = f"""
            Analyze this clinical trial data:
            
            Trial: {json.dumps(trial, indent=2)}
            Participants: {len(participants)}
            
            Provide:
            1. Trial progress assessment
            2. Participant enrollment status
            3. Safety concerns (if any)
            4. Recommendations
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a clinical trial analysis expert."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return {
                "trial_id": trial_id,
                "analysis": response.choices[0].message.content,
                "participant_count": len(participants),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def check_protocol_compliance(self, trial_id: str) -> dict:
        """Check trial protocol compliance"""
        try:
            trial = self.db.get_document_by_id('clinical_trials', trial_id)
            participants = self.db.query_documents('trial_participants', {'trial_id': trial_id})
            
            issues = []
            
            # Check participant criteria
            if 'eligibility_criteria' in trial:
                for participant in participants:
                    # Check age, health status, etc.
                    pass
            
            # Check timeline compliance
            if 'planned_duration_months' in trial and 'start_date' in trial:
                # Calculate if trial is on schedule
                pass
            
            return {
                "trial_id": trial_id,
                "compliant": len(issues) == 0,
                "issues": issues,
                "checked_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def generate_trial_report(self, trial_id: str) -> str:
        """Generate comprehensive trial report"""
        try:
            trial = self.db.get_document_by_id('clinical_trials', trial_id)
            participants = self.db.query_documents('trial_participants', {'trial_id': trial_id})
            
            prompt = f"""
            Generate a comprehensive clinical trial report:
            
            Trial Information:
            {json.dumps(trial, indent=2)}
            
            Total Participants: {len(participants)}
            
            Include:
            1. Executive Summary
            2. Trial Overview
            3. Participant Demographics
            4. Safety Profile
            5. Efficacy Results (if available)
            6. Conclusion and Next Steps
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a clinical research report writer."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error generating report: {str(e)}"
