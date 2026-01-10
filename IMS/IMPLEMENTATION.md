# AI Incident Resolution System - Phase 1 Implementation

## 📁 Project Structure

```
Incidentv/
├── config.py                      # Configuration and settings
├── requirements.txt               # Python dependencies
│
├── utils/                         # Utility modules
│   ├── __init__.py
│   ├── logger.py                  # Structured logging with CloudWatch
│   ├── aws_clients.py             # AWS service client factory
│   └── opensearch_client.py       # OpenSearch vector DB client
│
├── step3_orchestrator.py          # Step 3: AI Orchestrator (Lambda)
├── step4_analyzer.py              # Step 4: Incident Analyzer (Bedrock)
├── step5_resolution_generator.py  # Step 5: Resolution Generator (Bedrock)
│
├── load_historical_data.py        # Load 1000+ incidents into vector DB
├── test_pipeline.py               # End-to-end pipeline testing
│
├── incident_arch5.drawio          # Pilot architecture diagram
├── incident_dfd5.drawio           # Pilot data flow diagram
└── Incidentreadme.md              # Project documentation
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd Incidentv
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file:

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# OpenSearch Configuration
OPENSEARCH_ENDPOINT=https://your-opensearch-domain.us-east-1.es.amazonaws.com

# S3 Buckets
S3_BUCKET_RESOLUTIONS=incident-resolutions-pilot
S3_BUCKET_KNOWLEDGE_BASE=incident-knowledge-base
S3_BUCKET_LOGS=incident-logs

# ServiceNow Configuration
SERVICENOW_URL=https://your-instance.service-now.com
SERVICENOW_CLIENT_ID=your_client_id
SERVICENOW_CLIENT_SECRET=your_client_secret

# Dynatrace Configuration
DYNATRACE_URL=https://your-tenant.live.dynatrace.com
DYNATRACE_API_TOKEN=your_api_token

# Logging
LOG_LEVEL=INFO
```

### 3. Load Historical Data

```bash
python load_historical_data.py
```

This will:
- Create OpenSearch index with k-NN mapping
- Generate 1000 sample historical incidents
- Load data with embeddings into vector database
- Verify data load

### 4. Run End-to-End Test

```bash
python test_pipeline.py
```

This tests the complete workflow:
- Step 3: Orchestrator validates and routes incident
- Step 4: Analyzer extracts entities and creates embeddings
- Step 5: Generator queries similar incidents and creates resolution

## 📝 Script Descriptions

### Core Components

#### `config.py`
- AWS service configurations (Bedrock, OpenSearch, S3, Lambda)
- Prompt templates for AI analysis and resolution generation
- Pilot project settings (targets, thresholds, metrics)
- Error and success messages

#### `utils/logger.py`
- Structured logging with JSON format
- CloudWatch Logs integration
- Custom metric logging to CloudWatch
- Incident processing metrics tracking

#### `utils/aws_clients.py`
- Singleton factory for AWS service clients
- Bedrock Runtime, S3, Secrets Manager, CloudWatch clients
- Secret retrieval from AWS Secrets Manager

#### `utils/opensearch_client.py`
- OpenSearch connection with AWS authentication
- Index creation with k-NN vector mapping
- Semantic search using cosine similarity
- Bulk indexing for historical data

### Processing Pipeline

#### `step3_orchestrator.py` - AI Orchestrator
**Purpose**: Receive and validate incident data, route to analyzer

**Key Functions**:
- `validate_incident_data()` - JSON schema validation
- `extract_metadata()` - Extract and enrich incident metadata
- `initialize_context()` - Create processing context
- `route_to_analyzer()` - Route to Step 4

**Input**: Raw incident from Dynatrace/ServiceNow webhook
**Output**: Validated context for analysis

#### `step4_analyzer.py` - Incident Analyzer
**Purpose**: Analyze incidents using AWS Bedrock Claude Sonnet 4.5

**Key Functions**:
- `parse_description()` - NLP analysis of incident
- `extract_entities()` - Extract technical entities
- `classify_incident_type()` - Categorize incident
- `generate_embeddings()` - Create 1536-dimension vectors

**Input**: Processing context from Step 3
**Output**: Analysis with embeddings

**Processing Time**: ~2 seconds

#### `step5_resolution_generator.py` - Resolution Generator
**Purpose**: Generate resolution plans using similar incidents

**Key Functions**:
- `query_similar_incidents()` - Query vector DB (top 5 matches)
- `invoke_bedrock_for_resolution()` - Generate resolution with AI
- `create_4_section_report()` - Format comprehensive report

**Input**: Analysis from Step 4
**Output**: 4-section resolution report

**Sections**:
1. Similar Past Incidents (with similarity scores)
2. Root Cause Analysis
3. Recommended Resolution Steps
4. Confidence Score & Metadata

### Data Management

#### `load_historical_data.py`
**Purpose**: Load historical incidents into vector database

**Features**:
- Generates 1000 sample incidents (Performance & Availability categories)
- Creates embeddings for each incident
- Bulk indexes into OpenSearch
- Verifies data load with test query

**Usage**:
```bash
python load_historical_data.py
```

### Testing

#### `test_pipeline.py`
**Purpose**: End-to-end pipeline testing

**Test Cases**:
- Critical performance issue (high CPU)
- High priority availability issue (connection pool)
- Critical memory leak scenario

**Validates**:
- Processing time <3 seconds target
- Successful 4-section report generation
- Confidence score calculation
- Similar incident matching

**Usage**:
```bash
python test_pipeline.py
```

**Output**: `pipeline_test_results.json`

## 📊 Key Metrics Tracked

All scripts log metrics to CloudWatch:

1. **ProcessingTime** - Total incident processing duration
2. **AnalysisTime** - Step 4 analysis duration
3. **ResolutionGenerationTime** - Step 5 generation duration
4. **VectorSearchTime** - OpenSearch query duration
5. **ConfidenceScore** - AI confidence in resolution

## 🔧 AWS Services Required

Ensure these services are configured:

1. **AWS Bedrock** - Claude Sonnet 4.5 model access
2. **Amazon OpenSearch** - t3.small.search domain
3. **AWS Lambda** - Python 3.11 runtime
4. **Amazon S3** - 3 buckets (resolutions, knowledge, logs)
5. **Amazon CloudWatch** - Logs and custom metrics
6. **AWS Secrets Manager** - API credentials
7. **AWS IAM** - Service roles and policies

## 🎯 Expected Results

### Performance Targets (Phase 1 Pilot)

- **Response Time**: <3 seconds (95th percentile) ✓
- **Accuracy Rate**: 85%+ useful recommendations ⏳
- **Similar Incidents**: 3-5 matches with 0.75+ similarity ✓
- **Confidence Score**: 0.0-1.0 scale ✓

### Sample Output

```json
{
  "incident_id": "INC0012345",
  "section_1_similar_incidents": {
    "count": 5,
    "incidents": [
      {
        "incident_id": "INC0010234",
        "similarity_score": 0.94,
        "description": "High CPU usage on web-prod-02..."
      }
    ]
  },
  "section_2_root_cause": {
    "primary_cause": "Memory leak in Java application causing excessive GC",
    "contributing_factors": ["Inadequate heap size", "Memory leak in caching layer"]
  },
  "section_3_resolution_steps": {
    "steps": [
      {
        "step": 1,
        "description": "Identify memory leak source",
        "command": "jmap -histo:live <pid>"
      }
    ]
  },
  "section_4_metadata": {
    "confidence_score": 0.91,
    "risk_level": "Low",
    "manual_review_required": true
  }
}
```

## 🐛 Troubleshooting

### Common Issues

1. **OpenSearch Connection Failed**
   - Check OPENSEARCH_ENDPOINT in .env
   - Verify AWS credentials have OpenSearch access
   - Ensure security group allows connection

2. **Bedrock Access Denied**
   - Enable Claude Sonnet 4.5 model in AWS Bedrock console
   - Verify IAM role has bedrock:InvokeModel permission

3. **No Similar Incidents Found**
   - Run `load_historical_data.py` first
   - Verify OpenSearch index has data
   - Check similarity threshold (0.75 may be too high)

4. **Processing Time >3 seconds**
   - Check AWS region latency
   - Optimize Bedrock prompts
   - Use Lambda with higher memory (1024MB)

## 📖 Next Steps

After successful Phase 1 pilot:

1. **Collect Feedback** - Engineer ratings and comments
2. **Tune Prompts** - Improve accuracy based on feedback
3. **Adjust Thresholds** - Optimize similarity matching
4. **Phase 2 Planning** - Add automated execution (Steps 6-9)

## 🤝 Support

For issues or questions:
- Review logs in CloudWatch Logs: `/aws/lambda/incident-resolution`
- Check pilot metrics in CloudWatch dashboard
- Refer to [Incidentreadme.md](Incidentreadme.md) for detailed documentation

**Created by Code Insights @pramodklal**
