"""
Configuration file for AI Incident Resolution System - Phase 1 Pilot
Contains all AWS service configurations, API endpoints, and system parameters
"""

import os
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class AWSConfig:
    """AWS Service Configuration"""
    # AWS Region
    REGION = os.getenv('AWS_REGION', 'us-east-1')
    
    # AWS Bedrock Configuration
    BEDROCK_MODEL_ID = 'anthropic.claude-3-sonnet-20240229-v1:0'
    BEDROCK_MAX_TOKENS = 3000
    BEDROCK_TEMPERATURE = 0.7
    
    # Amazon OpenSearch Configuration
    OPENSEARCH_ENDPOINT = os.getenv('OPENSEARCH_ENDPOINT', 'https://your-opensearch-domain.us-east-1.es.amazonaws.com')
    OPENSEARCH_INDEX = 'incidents'
    OPENSEARCH_EMBEDDING_DIMENSION = 1536
    OPENSEARCH_SIMILARITY_THRESHOLD = 0.75
    OPENSEARCH_TOP_K = 5  # Top 5 similar incidents
    
    # S3 Configuration
    S3_BUCKET_RESOLUTIONS = os.getenv('S3_BUCKET_RESOLUTIONS', 'incident-resolutions-pilot')
    S3_BUCKET_KNOWLEDGE_BASE = os.getenv('S3_BUCKET_KNOWLEDGE_BASE', 'incident-knowledge-base')
    S3_BUCKET_LOGS = os.getenv('S3_BUCKET_LOGS', 'incident-logs')
    
    # Lambda Configuration
    LAMBDA_TIMEOUT = 30
    LAMBDA_MEMORY_SIZE = 512
    
    # CloudWatch Configuration
    CLOUDWATCH_NAMESPACE = 'IncidentResolution/Pilot'
    CLOUDWATCH_LOG_GROUP = '/aws/lambda/incident-resolution'
    
    # Secrets Manager
    SECRET_DYNATRACE_API_KEY = 'dynatrace-api-key'
    SECRET_SERVICENOW_OAUTH = 'servicenow-oauth'
    SECRET_OPENSEARCH_ADMIN = 'opensearch-admin'

@dataclass
class ServiceNowConfig:
    """ServiceNow Integration Configuration"""
    BASE_URL = os.getenv('SERVICENOW_URL', 'https://your-instance.service-now.com')
    API_VERSION = 'v1'
    INCIDENT_TABLE = 'incident'
    
    # OAuth2 Configuration
    CLIENT_ID = os.getenv('SERVICENOW_CLIENT_ID', '')
    CLIENT_SECRET = os.getenv('SERVICENOW_CLIENT_SECRET', '')
    
    # Incident Categories
    CATEGORIES = ['Performance', 'Availability', 'Network', 'Security']
    PRIORITIES = {1: 'Critical', 2: 'High', 3: 'Medium', 4: 'Low'}

@dataclass
class DynatraceConfig:
    """Dynatrace Integration Configuration"""
    BASE_URL = os.getenv('DYNATRACE_URL', 'https://your-tenant.live.dynatrace.com')
    API_TOKEN = os.getenv('DYNATRACE_API_TOKEN', '')
    
    # Alert Configuration
    ALERT_SEVERITY_LEVELS = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
    METRIC_TYPES = ['CPU', 'Memory', 'Disk', 'Network']

@dataclass
class PilotConfig:
    """Pilot Project Configuration"""
    # Timeline
    DURATION_DAYS = 30
    TARGET_TEST_CASES = 100
    
    # Performance Targets
    TARGET_RESPONSE_TIME_SECONDS = 3
    TARGET_ACCURACY_RATE = 0.85  # 85%
    TARGET_ENGINEER_SATISFACTION = 4.0  # 4/5
    TARGET_TIME_SAVINGS_PERCENT = 0.30  # 30%
    
    # Categories
    FOCUS_CATEGORIES = ['Performance', 'Availability']
    
    # Vector DB Configuration
    HISTORICAL_INCIDENTS_COUNT = 1000
    MIN_SIMILARITY_MATCHES = 3
    
    # Output Report Sections
    REPORT_SECTIONS = [
        'similar_incidents',
        'root_cause_analysis',
        'resolution_steps',
        'metadata'
    ]

@dataclass
class PromptTemplates:
    """AI Prompt Templates for Bedrock"""
    
    INCIDENT_ANALYSIS = """
Analyze this incident and extract key information:

Incident ID: {incident_id}
Priority: {priority}
Category: {category}
Description: {description}
Affected Systems: {affected_systems}
Timestamp: {timestamp}

Please extract and provide:
1. **Incident Type**: Classify as Performance, Availability, Network, or Security
2. **Primary Symptoms**: List the main observable issues
3. **Affected Components**: Identify servers, applications, or services involved
4. **Key Technical Terms**: Extract relevant technical keywords and error codes
5. **Severity Assessment**: Evaluate the impact level (Critical/High/Medium/Low)
6. **Time Criticality**: Assess if immediate action is required

Provide the analysis in JSON format.
"""

    RESOLUTION_GENERATION = """
Based on the incident analysis and similar past cases, generate a comprehensive resolution plan:

**Current Incident Analysis:**
{incident_analysis}

**Similar Past Incidents (Top 5 matches):**
{similar_incidents}

Please provide a detailed resolution plan with:

1. **Root Cause Analysis**:
   - Primary cause of the incident
   - Contributing factors
   - Why this incident occurred

2. **Resolution Steps** (numbered, detailed):
   - Step-by-step instructions
   - Specific commands to execute (with explanations)
   - Expected outcomes for each step
   - Verification steps
   - Rollback procedures if needed

3. **Best Practices**:
   - Prevention measures for future
   - Monitoring recommendations
   - Documentation to update

4. **Risk Assessment**:
   - Risk Level: Low/Medium/High
   - Confidence Score: 0.0 to 1.0 (how confident in this resolution)
   - Potential side effects
   - Dependencies to consider

5. **Estimated Resolution Time**: Provide time estimate

Provide the response in JSON format with clear sections.
"""

    EMBEDDING_GENERATION = """
Generate a concise semantic representation of this incident for similarity matching:

Incident: {description}
Category: {category}
Priority: {priority}
Symptoms: {symptoms}

Focus on technical details, error patterns, and key identifiers.
"""

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# API Gateway Configuration
API_GATEWAY_STAGE = 'prod'
API_RATE_LIMIT = 1000  # requests per minute

# Error Messages
ERROR_MESSAGES = {
    'invalid_incident': 'Invalid incident data format',
    'opensearch_connection': 'Failed to connect to OpenSearch',
    'bedrock_invocation': 'Failed to invoke Bedrock model',
    'no_similar_incidents': 'No similar incidents found in vector database',
    's3_upload_failed': 'Failed to upload to S3',
    'servicenow_api_error': 'ServiceNow API request failed'
}

# Success Messages
SUCCESS_MESSAGES = {
    'analysis_complete': 'Incident analysis completed successfully',
    'resolution_generated': 'Resolution plan generated successfully',
    'report_saved': 'Report saved to S3 successfully'
}
