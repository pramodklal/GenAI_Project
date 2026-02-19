"""
Drug Discovery Agent
Handles drug candidate analysis, molecular structure analysis, and discovery workflows
"""

import os
from openai import OpenAI
from datetime import datetime
import json

class DrugDiscoveryAgent:
    """Agent for drug discovery and candidate evaluation"""
    
    def __init__(self, db_helper):
        self.db = db_helper
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "gpt-4o"
        
    def analyze_drug_candidate(self, candidate_id: str) -> dict:
        """Analyze a drug candidate's properties and potential"""
        try:
            candidate = self.db.get_document_by_id('drug_candidates', candidate_id)
            
            if not candidate:
                return {"error": "Candidate not found"}
            
            prompt = f"""
            Analyze this drug candidate:
            
            {json.dumps(candidate, indent=2)}
            
            Provide comprehensive analysis including:
            1. Therapeutic potential
            2. Safety profile assessment
            3. Development challenges
            4. Competitive landscape
            5. Recommendations for next steps
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a pharmaceutical drug discovery expert."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return {
                "candidate_id": candidate_id,
                "analysis": response.choices[0].message.content,
                "analyzed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def search_similar_compounds(self, compound_name: str, limit: int = 10) -> list:
        """Search for similar compounds using vector search"""
        try:
            # Generate embedding for search
            embedding_response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=compound_name
            )
            query_vector = embedding_response.data[0].embedding
            
            # Vector search in molecular_structures collection
            results = self.db.vector_search(
                'molecular_structures',
                query_vector,
                limit=limit
            )
            
            return results
            
        except Exception as e:
            return []
    
    def evaluate_candidate_pipeline(self) -> dict:
        """Evaluate the entire drug candidate pipeline"""
        try:
            # Get all candidates by stage
            candidates = self.db.query_documents('drug_candidates', {})
            
            stages = {}
            for candidate in candidates:
                stage = candidate.get('development_stage', 'Unknown')
                if stage not in stages:
                    stages[stage] = []
                stages[stage].append(candidate)
            
            # AI analysis of pipeline
            prompt = f"""
            Analyze the drug discovery pipeline:
            
            Pipeline Summary:
            {json.dumps({stage: len(cands) for stage, cands in stages.items()}, indent=2)}
            
            Total Candidates: {len(candidates)}
            
            Provide:
            1. Pipeline health assessment
            2. Bottleneck identification
            3. Priority candidates
            4. Resource allocation recommendations
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a pharmaceutical pipeline strategist."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return {
                "pipeline_summary": stages,
                "total_candidates": len(candidates),
                "analysis": response.choices[0].message.content,
                "evaluated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def predict_success_probability(self, candidate_id: str) -> dict:
        """Predict development success probability"""
        try:
            candidate = self.db.get_document_by_id('drug_candidates', candidate_id)
            
            prompt = f"""
            Based on this drug candidate data, predict development success probability:
            
            {json.dumps(candidate, indent=2)}
            
            Consider:
            1. Preclinical data
            2. Target validation
            3. Safety profile
            4. Market need
            5. Development stage
            
            Provide probability estimate (0-100%) with reasoning.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a pharmaceutical success prediction expert."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return {
                "candidate_id": candidate_id,
                "prediction": response.choices[0].message.content,
                "predicted_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e)}
