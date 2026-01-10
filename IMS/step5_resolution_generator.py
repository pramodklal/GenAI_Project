"""
Step 5: Resolution Generator
Uses AWS Bedrock to generate resolution plans based on similar incidents
Creates comprehensive 4-section reports
"""

import json
import time
from datetime import datetime
from typing import Dict, Any, List
from config import AWSConfig, PromptTemplates, SUCCESS_MESSAGES, ERROR_MESSAGES
from utils.logger import get_logger
from utils.aws_clients import AWSClients
from utils.opensearch_client import get_opensearch_client

logger = get_logger(__name__)

class ResolutionGenerator:
    """
    Generates resolution plans using AWS Bedrock and similar incidents
    """
    
    def __init__(self):
        self.aws_clients = AWSClients()
        self.bedrock = self.aws_clients.get_bedrock_runtime()
        self.opensearch = get_opensearch_client()
        self.logger = logger
        self.model_id = AWSConfig.BEDROCK_MODEL_ID
    
    def query_similar_incidents(self, embedding: List[float], category: str) -> List[Dict[str, Any]]:
        """
        Query vector database for similar incidents
        
        Args:
            embedding: Incident embedding vector
            category: Incident category
            
        Returns:
            list: Top 5 similar incidents
        """
        try:
            self.logger.info("Querying vector database for similar incidents", category=category)
            
            similar_incidents = self.opensearch.query_similar_incidents(
                embedding=embedding,
                category=category,
                top_k=AWSConfig.OPENSEARCH_TOP_K
            )
            
            if not similar_incidents:
                self.logger.warning("No similar incidents found above threshold")
                return []
            
            self.logger.info(f"Found {len(similar_incidents)} similar incidents")
            return similar_incidents
            
        except Exception as e:
            self.logger.error(f"Failed to query similar incidents: {str(e)}")
            raise
    
    def format_similar_incidents(self, incidents: List[Dict[str, Any]]) -> str:
        """
        Format similar incidents for prompt
        
        Args:
            incidents: List of similar incidents
            
        Returns:
            str: Formatted incidents text
        """
        formatted = []
        for i, incident in enumerate(incidents, 1):
            formatted.append(f"""
Incident {i}:
- ID: {incident['incident_id']}
- Similarity Score: {incident['similarity_score']}
- Category: {incident['category']}
- Priority: {incident['priority']}
- Description: {incident['description']}
- Root Cause: {incident.get('root_cause', 'Not available')}
- Resolution: {incident.get('resolution', 'Not available')}
- Resolution Time: {incident.get('resolution_time_minutes', 'N/A')} minutes
""")
        
        return '\n'.join(formatted)
    
    def invoke_bedrock_for_resolution(self, incident_analysis: Dict[str, Any], 
                                     similar_incidents: List[Dict[str, Any]]) -> str:
        """
        Invoke Bedrock to generate resolution plan
        
        Args:
            incident_analysis: Analysis from Step 4
            similar_incidents: Similar incidents from vector DB
            
        Returns:
            str: Generated resolution plan
        """
        try:
            # Format similar incidents
            similar_incidents_text = self.format_similar_incidents(similar_incidents)
            
            # Build prompt
            prompt = PromptTemplates.RESOLUTION_GENERATION.format(
                incident_analysis=json.dumps(incident_analysis['analysis'], indent=2),
                similar_incidents=similar_incidents_text
            )
            
            self.logger.info("Generating resolution plan with Bedrock")
            
            # Invoke Bedrock
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": AWSConfig.BEDROCK_MAX_TOKENS,
                "temperature": AWSConfig.BEDROCK_TEMPERATURE
            }
            
            generation_start = time.time()
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            generation_time = time.time() - generation_start
            
            response_body = json.loads(response['body'].read())
            resolution_text = response_body['content'][0]['text']
            
            self.logger.info("Resolution plan generated", 
                           generation_time=round(generation_time, 2))
            
            # Log metric
            self.logger.log_metric(
                metric_name='ResolutionGenerationTime',
                value=generation_time,
                unit='Seconds'
            )
            
            return resolution_text
            
        except Exception as e:
            self.logger.error(f"Failed to generate resolution: {str(e)}")
            raise
    
    def parse_resolution_response(self, resolution_text: str) -> Dict[str, Any]:
        """
        Parse resolution response from Bedrock
        
        Args:
            resolution_text: Raw response from Bedrock
            
        Returns:
            dict: Structured resolution data
        """
        try:
            # Extract JSON from response
            if '```json' in resolution_text:
                resolution_text = resolution_text.split('```json')[1].split('```')[0].strip()
            elif '```' in resolution_text:
                resolution_text = resolution_text.split('```')[1].split('```')[0].strip()
            
            resolution_data = json.loads(resolution_text)
            return resolution_data
            
        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse JSON, using fallback: {str(e)}")
            
            # Fallback: return raw text structured
            return {
                'root_cause_analysis': {
                    'primary_cause': 'See full text',
                    'contributing_factors': []
                },
                'resolution_steps': [
                    {'step': 1, 'description': 'Review full resolution text', 'command': ''}
                ],
                'best_practices': ['Refer to full text'],
                'risk_assessment': {
                    'risk_level': 'Medium',
                    'confidence_score': 0.7
                },
                'estimated_resolution_time': 'Unknown',
                'full_text': resolution_text
            }
    
    def create_4_section_report(self, incident_id: str, 
                                incident_analysis: Dict[str, Any],
                                similar_incidents: List[Dict[str, Any]],
                                resolution_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create comprehensive 4-section report
        
        Args:
            incident_id: Incident ID
            incident_analysis: Analysis from Step 4
            similar_incidents: Similar incidents found
            resolution_data: Generated resolution
            
        Returns:
            dict: Complete 4-section report
        """
        report = {
            'incident_id': incident_id,
            'generated_at': datetime.utcnow().isoformat(),
            'pilot_project': True,
            
            # Section 1: Similar Past Incidents
            'section_1_similar_incidents': {
                'title': 'Similar Past Incidents',
                'count': len(similar_incidents),
                'incidents': [
                    {
                        'incident_id': inc['incident_id'],
                        'similarity_score': inc['similarity_score'],
                        'category': inc['category'],
                        'priority': inc['priority'],
                        'description': inc['description'][:200] + '...' if len(inc['description']) > 200 else inc['description'],
                        'resolution_time_minutes': inc.get('resolution_time_minutes', 'N/A')
                    }
                    for inc in similar_incidents
                ]
            },
            
            # Section 2: Root Cause Analysis
            'section_2_root_cause': {
                'title': 'Root Cause Analysis',
                'primary_cause': resolution_data.get('root_cause_analysis', {}).get('primary_cause', 'Unknown'),
                'contributing_factors': resolution_data.get('root_cause_analysis', {}).get('contributing_factors', []),
                'analysis_details': incident_analysis['analysis']
            },
            
            # Section 3: Resolution Steps
            'section_3_resolution_steps': {
                'title': 'Recommended Resolution Steps',
                'steps': resolution_data.get('resolution_steps', []),
                'best_practices': resolution_data.get('best_practices', []),
                'estimated_time': resolution_data.get('estimated_resolution_time', 'Unknown')
            },
            
            # Section 4: Metadata
            'section_4_metadata': {
                'title': 'Confidence Score & Metadata',
                'confidence_score': resolution_data.get('risk_assessment', {}).get('confidence_score', 0.0),
                'risk_level': resolution_data.get('risk_assessment', {}).get('risk_level', 'Medium'),
                'similar_incidents_count': len(similar_incidents),
                'model_used': self.model_id,
                'processing_metadata': incident_analysis['processing_metadata'],
                'manual_review_required': True,
                'pilot_phase': True
            }
        }
        
        return report
    
    def generate_resolution(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main function to generate complete resolution
        
        Args:
            analysis_result: Result from Step 4 (Incident Analyzer)
            
        Returns:
            dict: Complete resolution with 4-section report
        """
        start_time = time.time()
        
        try:
            incident_analysis = analysis_result['analysis']
            incident_id = incident_analysis['incident_id']
            
            self.logger.info("Starting resolution generation", incident_id=incident_id)
            
            # Step 1: Query similar incidents from vector DB
            similar_incidents = self.query_similar_incidents(
                embedding=incident_analysis['embeddings'],
                category=incident_analysis['classification']['primary_category']
            )
            
            if not similar_incidents:
                return {
                    'statusCode': 404,
                    'body': json.dumps({
                        'error': ERROR_MESSAGES['no_similar_incidents'],
                        'incident_id': incident_id
                    })
                }
            
            # Step 2: Generate resolution using Bedrock
            resolution_text = self.invoke_bedrock_for_resolution(
                incident_analysis=incident_analysis,
                similar_incidents=similar_incidents
            )
            
            # Step 3: Parse resolution
            resolution_data = self.parse_resolution_response(resolution_text)
            
            # Step 4: Create 4-section report
            report = self.create_4_section_report(
                incident_id=incident_id,
                incident_analysis=incident_analysis,
                similar_incidents=similar_incidents,
                resolution_data=resolution_data
            )
            
            processing_time = time.time() - start_time
            
            # Log metrics
            self.logger.log_incident_processing(
                incident_id=incident_id,
                stage='resolution_generation',
                duration=processing_time,
                success=True
            )
            
            # Log confidence score metric
            self.logger.log_metric(
                metric_name='ConfidenceScore',
                value=report['section_4_metadata']['confidence_score'],
                unit='None',
                IncidentID=incident_id
            )
            
            self.logger.info("Resolution generation completed", 
                           incident_id=incident_id,
                           processing_time=round(processing_time, 2),
                           confidence_score=report['section_4_metadata']['confidence_score'])
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': SUCCESS_MESSAGES['resolution_generated'],
                    'incident_id': incident_id,
                    'processing_time_seconds': round(processing_time, 2),
                    'report': report
                }, default=str)
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            incident_id = analysis_result.get('analysis', {}).get('incident_id', 'unknown')
            
            self.logger.log_incident_processing(
                incident_id=incident_id,
                stage='resolution_generation',
                duration=processing_time,
                success=False
            )
            
            self.logger.error(f"Resolution generation failed: {str(e)}", 
                            incident_id=incident_id)
            
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': 'Resolution generation failed',
                    'details': str(e),
                    'incident_id': incident_id
                })
            }

def lambda_handler(event, context):
    """AWS Lambda handler function"""
    generator = ResolutionGenerator()
    
    # Extract analysis result from event
    if 'body' in event:
        event_data = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
    else:
        event_data = event
    
    analysis_result = event_data.get('analysis', event_data)
    
    return generator.generate_resolution(analysis_result)

# For local testing
if __name__ == '__main__':
    print("Resolution Generator - Step 5")
    print("Note: Requires Step 4 output and OpenSearch connection")
