"""
Research Publication Agent
Handles research paper analysis, literature search, and publication management
"""

import os
from openai import OpenAI
from datetime import datetime
import json

class ResearchPublicationAgent:
    """Agent for research publication management and analysis"""
    
    def __init__(self, db_helper):
        self.db = db_helper
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "gpt-4o"
        
    def search_related_papers(self, topic: str, limit: int = 10) -> list:
        """Search for related research papers using vector search"""
        try:
            # Generate embedding for topic
            embedding_response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=topic
            )
            query_vector = embedding_response.data[0].embedding
            
            # Vector search in research_papers collection
            results = self.db.vector_search(
                'research_papers',
                query_vector,
                limit=limit
            )
            
            return results
            
        except Exception as e:
            return []
    
    def summarize_paper(self, paper_id: str) -> dict:
        """Generate summary of a research paper"""
        try:
            paper = self.db.get_document_by_id('research_papers', paper_id)
            
            if not paper:
                return {"error": "Paper not found"}
            
            prompt = f"""
            Summarize this research paper:
            
            {json.dumps(paper, indent=2)}
            
            Provide:
            1. Key findings
            2. Methodology overview
            3. Significance and impact
            4. Limitations
            5. Future research directions
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a scientific literature analyst."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return {
                "paper_id": paper_id,
                "summary": response.choices[0].message.content,
                "summarized_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def generate_literature_review(self, topic: str) -> str:
        """Generate literature review for a topic"""
        try:
            # Search related papers
            related_papers = self.search_related_papers(topic, limit=20)
            
            prompt = f"""
            Generate a comprehensive literature review on: {topic}
            
            Based on these research papers:
            {json.dumps(related_papers[:10], indent=2)}
            
            Include:
            1. Introduction to the topic
            2. Current state of research
            3. Key findings from literature
            4. Research gaps
            5. Future directions
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a scientific literature review expert."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error generating review: {str(e)}"
    
    def identify_research_trends(self) -> dict:
        """Identify research trends from publication database"""
        try:
            # Get recent publications
            publications = self.db.query_documents('research_publications', {})
            
            prompt = f"""
            Analyze research trends from these publications:
            
            Total Publications: {len(publications)}
            
            Sample Data:
            {json.dumps(publications[:20], indent=2)}
            
            Identify:
            1. Emerging research areas
            2. Hot topics
            3. Research gaps
            4. Collaboration opportunities
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a research trend analyst."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return {
                "total_publications": len(publications),
                "trends": response.choices[0].message.content,
                "analyzed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e)}
