"""
Patent Analysis Agent
Handles patent search, analysis, and intellectual property management
"""

import os
from openai import OpenAI
from datetime import datetime
import json

class PatentAnalysisAgent:
    """Agent for patent analysis and IP management"""
    
    def __init__(self, db_helper):
        self.db = db_helper
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "gpt-4o"
        
    def search_patents(self, query: str, limit: int = 10) -> list:
        """Search patent documents using vector search"""
        try:
            # Generate embedding for query
            embedding_response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=query
            )
            query_vector = embedding_response.data[0].embedding
            
            # Vector search in patent_documents collection
            results = self.db.vector_search(
                'patent_documents',
                query_vector,
                limit=limit
            )
            
            return results
            
        except Exception as e:
            return []
    
    def analyze_patent_landscape(self, technology_area: str) -> dict:
        """Analyze patent landscape for a technology area"""
        try:
            patents = self.search_patents(technology_area, limit=50)
            
            prompt = f"""
            Analyze the patent landscape for: {technology_area}
            
            Found {len(patents)} related patents
            
            Sample Patents:
            {json.dumps(patents[:10], indent=2)}
            
            Provide:
            1. Key players and assignees
            2. Technology trends
            3. Patent clusters
            4. White spaces (patentability opportunities)
            5. Competitive intelligence
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a patent landscape analyst."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return {
                "technology_area": technology_area,
                "patents_found": len(patents),
                "analysis": response.choices[0].message.content,
                "analyzed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def check_patentability(self, invention_description: str) -> dict:
        """Check patentability of an invention"""
        try:
            # Search for similar patents
            similar_patents = self.search_patents(invention_description, limit=20)
            
            prompt = f"""
            Assess patentability of this invention:
            
            Description: {invention_description}
            
            Found {len(similar_patents)} similar patents:
            {json.dumps(similar_patents[:5], indent=2)}
            
            Evaluate:
            1. Novelty (is it new?)
            2. Non-obviousness
            3. Prior art concerns
            4. Patentability score (0-100)
            5. Recommendations
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a patent examiner and IP attorney."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return {
                "invention": invention_description,
                "similar_patents_found": len(similar_patents),
                "assessment": response.choices[0].message.content,
                "assessed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def generate_patent_draft(self, invention_data: dict) -> str:
        """Generate draft patent application"""
        try:
            prompt = f"""
            Generate a patent application draft:
            
            Invention Details:
            {json.dumps(invention_data, indent=2)}
            
            Include standard sections:
            1. Title
            2. Technical Field
            3. Background
            4. Summary of Invention
            5. Detailed Description
            6. Claims (independent and dependent)
            7. Abstract
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a patent attorney drafting patent applications."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error generating patent draft: {str(e)}"
