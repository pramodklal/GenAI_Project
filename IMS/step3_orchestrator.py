"""
Step 3: AI Orchestrator
AWS Lambda function to orchestrate incident processing workflow
Receives incident data, validates, and routes to analyzer
"""

import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
from jsonschema import validate, ValidationError
from config import AWSConfig, ERROR_MESSAGES, SUCCESS_MESSAGES
from utils.logger import get_logger
from utils.aws_clients import AWSClients

logger = get_logger(__name__)

# JSON Schema for incident data validation
INCIDENT_SCHEMA = {
    "type": "object",
    "properties": {
        "incident_id": {"type": "string"},
        "priority": {"type": "integer", "minimum": 1, "maximum": 4},
        "category": {"type": "string", "enum": ["Performance", "Availability", "Network", "Security"]},
        "description": {"type": "string", "minLength": 10},
        "affected_systems": {"type": "array", "items": {"type": "string"}},
        "timestamp": {"type": "string"},
        "severity": {"type": "string", "enum": ["Critical", "High", "Medium", "Low"]},
        "source": {"type": "string"}
    },
    "required": ["incident_id", "priority", "category", "description", "timestamp"]
}

class IncidentOrchestrator:
    """
    Orchestrates the incident processing workflow
    """
    
    def __init__(self):
        self.aws_clients = AWSClients()
        self.logger = logger
    
    def validate_incident_data(self, incident_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate incident data against schema
        
        Args:
            incident_data: Raw incident data from webhook
            
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            validate(instance=incident_data, schema=INCIDENT_SCHEMA)
            self.logger.info("Incident data validation successful", 
                           incident_id=incident_data.get('incident_id'))
            return True, None
        except ValidationError as e:
            error_msg = f"Validation failed: {e.message}"
            self.logger.error(error_msg, incident_id=incident_data.get('incident_id'))
            return False, error_msg
    
    def extract_metadata(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and enrich incident metadata
        
        Args:
            incident_data: Validated incident data
            
        Returns:
            dict: Enhanced metadata
        """
        metadata = {
            'incident_id': incident_data['incident_id'],
            'priority': incident_data['priority'],
            'priority_label': {1: 'Critical', 2: 'High', 3: 'Medium', 4: 'Low'}.get(incident_data['priority']),
            'category': incident_data['category'],
            'description': incident_data['description'],
            'affected_systems': incident_data.get('affected_systems', []),
            'severity': incident_data.get('severity', 'Medium'),
            'source': incident_data.get('source', 'Unknown'),
            'timestamp': incident_data['timestamp'],
            'received_at': datetime.utcnow().isoformat(),
            'processing_stage': 'orchestration',
            'pilot_project': True
        }
        
        self.logger.info("Metadata extracted", incident_id=metadata['incident_id'], 
                        category=metadata['category'], priority=metadata['priority_label'])
        
        return metadata
    
    def initialize_context(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initialize processing context for the incident
        
        Args:
            metadata: Incident metadata
            
        Returns:
            dict: Processing context
        """
        context = {
            'incident_metadata': metadata,
            'workflow': {
                'step': 3,
                'stage': 'orchestration',
                'next_step': 'analysis',
                'started_at': datetime.utcnow().isoformat()
            },
            'configuration': {
                'similarity_threshold': AWSConfig.OPENSEARCH_SIMILARITY_THRESHOLD,
                'top_k_similar': AWSConfig.OPENSEARCH_TOP_K,
                'max_tokens': AWSConfig.BEDROCK_MAX_TOKENS,
                'model_id': AWSConfig.BEDROCK_MODEL_ID
            },
            'pilot_metadata': {
                'is_pilot': True,
                'manual_execution_required': True,
                'feedback_collection': True
            }
        }
        
        return context
    
    def route_to_analyzer(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route incident to analyzer (Step 4)
        
        Args:
            context: Processing context
            
        Returns:
            dict: Routing result
        """
        try:
            # In AWS Lambda, this would invoke the analyzer Lambda function
            # For now, we'll prepare the payload
            
            payload = {
                'action': 'analyze_incident',
                'context': context,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self.logger.info("Routing to analyzer", 
                           incident_id=context['incident_metadata']['incident_id'])
            
            # Here you would invoke the analyzer Lambda:
            # lambda_client = self.aws_clients.get_lambda()
            # response = lambda_client.invoke(
            #     FunctionName='incident-analyzer',
            #     InvocationType='Event',  # Async
            #     Payload=json.dumps(payload)
            # )
            
            return {
                'status': 'routed',
                'next_function': 'incident-analyzer',
                'payload': payload
            }
            
        except Exception as e:
            self.logger.error(f"Failed to route to analyzer: {str(e)}", 
                            incident_id=context['incident_metadata']['incident_id'])
            raise
    
    def process_incident(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing function - orchestrates the incident workflow
        
        Args:
            event: Lambda event containing incident data
            
        Returns:
            dict: Processing result
        """
        start_time = time.time()
        
        try:
            # Extract incident data from event
            if 'body' in event:
                incident_data = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
            else:
                incident_data = event
            
            self.logger.info("Starting incident orchestration", 
                           incident_id=incident_data.get('incident_id'))
            
            # Step 1: Validate incident data
            is_valid, error_msg = self.validate_incident_data(incident_data)
            if not is_valid:
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'error': ERROR_MESSAGES['invalid_incident'],
                        'details': error_msg
                    })
                }
            
            # Step 2: Extract metadata
            metadata = self.extract_metadata(incident_data)
            
            # Step 3: Initialize context
            context = self.initialize_context(metadata)
            
            # Step 4: Route to analyzer
            routing_result = self.route_to_analyzer(context)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Log metrics
            self.logger.log_incident_processing(
                incident_id=metadata['incident_id'],
                stage='orchestration',
                duration=processing_time,
                success=True
            )
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': SUCCESS_MESSAGES['analysis_complete'],
                    'incident_id': metadata['incident_id'],
                    'processing_time_seconds': round(processing_time, 2),
                    'next_step': 'analysis',
                    'context': context,
                    'routing_result': routing_result
                })
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            incident_id = incident_data.get('incident_id', 'unknown')
            
            self.logger.log_incident_processing(
                incident_id=incident_id,
                stage='orchestration',
                duration=processing_time,
                success=False
            )
            
            self.logger.error(f"Orchestration failed: {str(e)}", incident_id=incident_id)
            
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': 'Internal processing error',
                    'details': str(e),
                    'incident_id': incident_id
                })
            }

def lambda_handler(event, context):
    """
    AWS Lambda handler function
    
    Args:
        event: Lambda event (API Gateway request or direct invocation)
        context: Lambda context object
        
    Returns:
        dict: HTTP response
    """
    orchestrator = IncidentOrchestrator()
    return orchestrator.process_incident(event)

# For local testing
if __name__ == '__main__':
    # Sample incident data for testing
    sample_incident = {
        'incident_id': 'INC0012345',
        'priority': 1,
        'category': 'Performance',
        'description': 'High CPU usage (95%) detected on production server web-prod-01. Application response time degraded from 200ms to 2500ms.',
        'affected_systems': ['web-prod-01', 'app-server-cluster'],
        'timestamp': '2026-01-08T10:30:00Z',
        'severity': 'Critical',
        'source': 'Dynatrace'
    }
    
    orchestrator = IncidentOrchestrator()
    result = orchestrator.process_incident(sample_incident)
    print(json.dumps(result, indent=2))
