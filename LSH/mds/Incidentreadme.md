# AI Agentic Incident Resolution System - Pilot Project (Phase 1)

## 📋 Overview
This pilot project implements an AI-powered incident analysis and resolution recommendation system using AWS services, Dynatrace monitoring, and ServiceNow integration. **Phase 1 focuses on AI-generated recommendations with manual review and execution** - no automated execution.

### **🎯 Pilot Objectives**
- Validate AI accuracy in incident analysis (target: 85%+)
- Measure time savings vs manual analysis (target: 30%+)
- Test semantic search with 1000+ historical incidents
- Collect engineer feedback for improvement
- Generate resolution recommendations in <3 seconds

---

## 🏗️ Architecture Components

### **⭐ Pilot Project** (5 Steps - Phase 1) - **CURRENT FOCUS**
- **Architecture Diagram**: [`incident_arch5.drawio`](incident_arch5.drawio)
- **Data Flow Diagram**: [`incident_dfd5.drawio`](incident_dfd5.drawio)
- **Focus**: Analysis & recommendation only (no auto-execution)
- **Duration**: 30 days with 50-100 test cases
- **Estimated Cost**: $225-460/month

### **Full System** (9 Steps - Future Phase 2)
- Architecture Diagram: [`incident_arch.drawio`](incident_arch.drawio)
- Data Flow Diagram: [`incident_dfd.drawio`](incident_dfd.drawio)
- Complete automated workflow including auto-execution
- Production cost: $865-1,620/month

---

## 🔄 Pilot Workflow (5 Steps)

### **1️⃣ Dynatrace Monitoring**
- Infrastructure & application performance monitoring
- Real-time alerting on anomalies
- Automatic alert generation
- Metrics: CPU, memory, disk, network

### **2️⃣ ServiceNow Incident Creation**
- Automatic ticket creation from Dynatrace alerts
- Priority assignment (P1/P2/P3/P4)
- Category classification (Performance/Availability/Network/Security)
- Incident details capture (description, affected systems, timestamps)

### **3️⃣ AI Orchestrator** (AWS Lambda + Step Functions)
- **Technology**: AWS Lambda (Python 3.11, 512MB)
- Receive incident data via API Gateway webhook
- Validate JSON schema
- Extract metadata (priority, category, description)
- Route to Incident Analyzer
- Initialize processing context

### **4️⃣ Incident Analyzer** (AWS Bedrock - Claude Sonnet 4.5)
- **Technology**: AWS Bedrock with Claude Sonnet 4.5 model
- **Processing Time**: ~2 seconds
- Parse incident description using NLP
- Extract entities (servers, applications, error codes)
- Classify incident type
- Identify severity level
- Generate keywords for search
- Create embeddings (1536-dimension vectors)

### **5️⃣ Resolution Generator** (AWS Bedrock - Claude Sonnet 4.5)
- **Technology**: AWS Bedrock with Claude Sonnet 4.5 model
- **Max Tokens**: 3000 per response
- Query Vector DB for top 5 similar incidents
- Analyze similar case patterns
- Identify root cause
- Generate step-by-step resolution plan
- Include best practices and commands
- Calculate confidence score (0-1 scale)

### **📋 Pilot Output - 4-Section Report**
1. **Similar Past Incidents** - Top 5 matches with similarity scores
2. **Root Cause Analysis** - Identified issues and contributing factors
3. **Recommended Resolution Steps** - Detailed instructions and commands
4. **Confidence Score & Risk Level** - AI confidence and risk assessment

### **👤 Manual Review & Execution**
- Engineer reviews AI recommendations
- Validates resolution plan
- **Manually executes steps** (no automation in pilot)
- Updates ServiceNow ticket with results
- Provides feedback on accuracy
- ⚠️ **No Auto-Execution in Pilot Phase**

---

## ☁️ AWS Technology Stack (Pilot Project)

### **Core Services - 8 Components**

#### **1. AWS Bedrock** (Primary AI/LLM Service)
- **Model**: Claude Sonnet 4.5 (anthropic.claude-3-sonnet-20240229-v1:0)
- **Purpose**: AI-powered incident analysis and resolution generation
- **Used In**:
  - Step 4: Incident Analyzer (~2s processing time)
  - Step 5: Resolution Generator (3000 max tokens)
- **Capabilities**: 
  - Natural language processing
  - Incident classification & entity extraction
  - Root cause identification
  - Resolution plan generation with confidence scoring
  - 1536-dimension embedding generation

#### **2. Amazon OpenSearch Service** (Vector Database)
- **Instance**: t3.small.search (pilot configuration)
- **Storage**: 10GB for 1000+ historical incidents
- **Purpose**: Semantic search for similar incidents
- **Configuration**:
  - k-NN (k-nearest neighbors) plugin enabled
  - Vector storage with 1536-dimension embeddings
  - Similarity threshold: 0.75+ for matches
  - HNSW algorithm for fast vector search
- **Index Structure**:
  ```json
  {
    "incident_id": "INC0012345",
    "embedding": [float[1536]],
    "description": "text",
    "resolution": "text",
    "category": "Performance/Availability",
    "priority": 1,
    "timestamp": "2025-12-15T10:30:00Z"
  }
  ```

#### **3. AWS Lambda** (Orchestration)
- **Runtime**: Python 3.11
- **Memory**: 512MB per function
- **Timeout**: 30 seconds
- **Functions**:
  - `incident-webhook-processor` - Receive webhooks from ServiceNow
  - `incident-orchestrator` - Step 3: Validate and route incidents
  - `incident-analyzer` - Step 4: Trigger Bedrock analysis
  - `vector-db-query` - Query OpenSearch for similar incidents
  - `resolution-generator` - Step 5: Generate resolution plans
  - `output-formatter` - Format 4-section reports

#### **4. Amazon S3** (Document Storage)
- **Buckets**:
  - `incident-resolutions-pilot/` - Historical resolution documents
  - `incident-knowledge-base/` - Best practices and runbooks
  - `incident-logs/` - Processing logs and audit trails
- **Features**: 
  - Versioning enabled for document tracking
  - Lifecycle policies (archive after 90 days)
  - 5GB storage for pilot phase

#### **5. Amazon API Gateway**
- **Type**: REST API
- **Purpose**: External system integration
- **Endpoints**:
  - `POST /incidents/webhook` - Receive Dynatrace/ServiceNow alerts
  - `GET /incidents/{id}` - Retrieve incident details
  - `POST /incidents/analyze` - Trigger AI analysis
  - `GET /resolutions/{id}` - Get resolution recommendations
- **Security**: 
  - API key authentication
  - Rate limiting: 1000 requests/minute
  - Request validation

#### **6. Amazon CloudWatch** (Logging/Monitoring)
- **Logs**: All Lambda executions, API Gateway requests
- **Custom Metrics**:
  - `ProcessingTime` - Incident analysis duration (target: <3s)
  - `AccuracyScore` - Engineer feedback ratings (target: 85%+)
  - `ConfidenceScore` - AI confidence levels
  - `SimilarityMatches` - Vector DB match counts
- **Dashboards**: Real-time pilot performance monitoring
- **Alarms**: 
  - Latency >5 seconds
  - Error rate >5%
  - API throttling events

#### **7. AWS Secrets Manager**
- **Stored Secrets** (5 total):
  - `dynatrace-api-key` - Dynatrace API authentication
  - `servicenow-oauth` - ServiceNow OAuth2 client credentials
  - `opensearch-admin` - OpenSearch admin username/password
  - `bedrock-api-key` - AWS Bedrock access credentials
  - `api-gateway-keys` - External system API keys
- **Features**: Automatic rotation, encryption at rest

#### **8. AWS IAM** (Security)
- **Roles**:
  - `BedrockExecutionRole` - Lambda → Bedrock invoke permissions
  - `OpenSearchAccessRole` - Lambda → OpenSearch query permissions
  - `S3ReadWriteRole` - Lambda → S3 read/write permissions
  - `SecretsManagerRole` - Lambda → Secrets Manager read permissions
- **Policies**: Least privilege principle, resource-based access

---

## 📊 Pilot Metrics & Success Criteria

### **Pilot Timeline**
- **Duration**: 30 days
- **Test Cases**: 50-100 incidents
- **Focus Categories**: Performance & Availability incidents
- **Team**: 5-10 engineers providing feedback

### **Key Performance Indicators (KPIs)**

#### **1. ⚡ Response Time**
- **Target**: <3 seconds (95th percentile)
- **Measurement**: Time from incident submission to recommendation generation
- **Current Baseline**: Manual analysis takes 15-30 minutes

#### **2. 🎓 Accuracy Rate**
- **Target**: 85%+ recommendations rated as "useful" or "very useful"
- **Measurement**: Engineer feedback ratings (1-5 scale)
- **Success Criteria**: 4+ average rating

#### **3. 💾 Vector DB Performance**
- **Target**: Find 5 similar incidents with 0.75+ similarity score
- **Measurement**: Similarity scores from OpenSearch k-NN search
- **Success Criteria**: 80%+ of incidents have 3+ relevant matches

#### **4. 🤝 Engineer Satisfaction**
- **Target**: Average satisfaction rating 4/5 or higher
- **Measurement**: Weekly feedback surveys
- **Questions**: Usefulness, time saved, confidence in recommendations

#### **5. ⏱️ Time Savings**
- **Target**: 30%+ reduction in incident analysis time
- **Measurement**: Compare AI-assisted vs manual analysis time
- **Expected Savings**: 10-15 minutes per incident

### **Success Criteria for Phase 2 Approval**
✅ Achieve 85%+ accuracy rate  
✅ Response time consistently <3 seconds  
✅ Engineer satisfaction 4/5+  
✅ Successfully process 50+ incidents  
✅ Positive ROI projection for production  

---

## 💰 Pilot Cost Estimation

### **Monthly Cost Breakdown** (30 days, 100 incidents)
| Service | Configuration | Monthly Cost |
|---------|--------------|--------------|
| **AWS Bedrock** | Claude Sonnet 4.5<br>~50K tokens/incident<br>100 incidents | $50 - $150 |
| **OpenSearch** | t3.small.search instance<br>10GB storage<br>1000 incidents | $150 - $250 |
| **S3** | 5GB storage<br>1000 PUT/GET requests | $5 - $10 |
| **API Gateway** | 10K requests<br>(1M free tier) | $0 - $10 |
| **Lambda** | 1000 invocations<br>512MB, avg 5s<br>(1M free tier) | $0 - $5 |
| **CloudWatch** | Logs (1GB)<br>Metrics (10 custom) | $10 - $20 |
| **Secrets Manager** | 5 secrets | $2 - $5 |
| **Data Transfer** | Minimal (within region) | $5 - $10 |
| **TOTAL** | | **$222 - $460/month** |

### **Production Phase** (Full automation, ~1000 incidents/month)
| Service | Configuration | Monthly Cost |
|---------|--------------|--------------|
| **AWS Bedrock** | 1000 incidents<br>~50K tokens each | $400 - $800 |
| **OpenSearch** | t3.medium.search<br>50GB storage<br>10K+ incidents | $300 - $500 |
| **S3** | 50GB storage<br>50K requests | $20 - $40 |
| **API Gateway** | 100K requests | $35 - $50 |
| **Lambda** | 10K invocations<br>Higher memory | $20 - $50 |
| **Step Functions** | Workflow orchestration | $25 - $50 |
| **DynamoDB** | State management | $25 - $50 |
| **CloudWatch** | 10GB logs, dashboards | $30 - $60 |
| **X-Ray** | Distributed tracing | $10 - $20 |
| **TOTAL** | | **$865 - $1,620/month** |

### **Cost Optimization Tips**
- Use Lambda reserved concurrency for predictable workloads
- Enable S3 Intelligent-Tiering for archival data
- Use OpenSearch Reserved Instances (save 30-50%)
- Implement request caching in API Gateway
- Monitor Bedrock token usage and optimize prompts

---

## 🚀 Implementation Steps

### **Phase 1: Pilot Project Setup (Weeks 1-4)**

#### **Week 1: AWS Infrastructure Setup**
1. **Create AWS Account & IAM Setup**
   ```bash
   # Configure AWS CLI
   aws configure
   
   # Create IAM roles
   aws iam create-role --role-name BedrockExecutionRole --assume-role-policy-document file://trust-policy.json
   ```

2. **Deploy OpenSearch Cluster**
   ```bash
   # Create OpenSearch domain
   aws opensearch create-domain \
     --domain-name incident-vector-db \
     --engine-version OpenSearch_2.11 \
     --cluster-config InstanceType=t3.small.search,InstanceCount=1 \
     --ebs-options EBSEnabled=true,VolumeType=gp3,VolumeSize=10
   ```

3. **Setup S3 Buckets**
   ```bash
   # Create buckets
   aws s3 mb s3://incident-resolutions-prod
   aws s3 mb s3://incident-knowledge-base
   
   # Enable versioning
   aws s3api put-bucket-versioning --bucket incident-resolutions-prod --versioning-configuration Status=Enabled
   ```

4. **Configure Secrets Manager**
   ```bash
   # Store Dynatrace API key
   aws secretsmanager create-secret \
     --name dynatrace-api-key \
     --secret-string '{"api_key":"your-dynatrace-key"}'
   
   # Store ServiceNow credentials
   aws secretsmanager create-secret \
     --name servicenow-oauth \
     --secret-string '{"client_id":"xxx","client_secret":"yyy"}'
   ```

#### **Week 2: Data Preparation**
5. **Collect Historical Incidents**
   - Export 1000+ incidents from ServiceNow
   - Include: incident number, description, resolution, category, priority
   - Format: JSON or CSV

6. **Generate Embeddings**
   ```python
   import boto3
   import json
   
   bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
   opensearch = boto3.client('opensearch')
   
   def generate_embedding(text):
       response = bedrock.invoke_model(
           modelId='amazon.titan-embed-text-v1',
           body=json.dumps({"inputText": text})
       )
       return json.loads(response['body'].read())['embedding']
   
   # Process incidents
   for incident in historical_incidents:
       embedding = generate_embedding(incident['description'])
       # Store in OpenSearch
   ```

7. **Load Data into OpenSearch**
   ```python
   from opensearchpy import OpenSearch
   
   # Create index with k-NN mapping
   index_body = {
       "settings": {
           "index.knn": True
       },
       "mappings": {
           "properties": {
               "incident_id": {"type": "keyword"},
               "embedding": {
                   "type": "knn_vector",
                   "dimension": 1536,
                   "method": {
                       "name": "hnsw",
                       "engine": "nmslib"
                   }
               },
               "description": {"type": "text"},
               "resolution": {"type": "text"}
           }
       }
   }
   
   client.indices.create(index="incidents", body=index_body)
   ```

#### **Week 3: AI Agent Development**
8. **Develop Incident Analyzer Agent**
   ```python
   import boto3
   
   bedrock_runtime = boto3.client('bedrock-runtime')
   
   def analyze_incident(incident_data):
       prompt = f"""
       Analyze this incident and extract key information:
       
       Incident: {incident_data['description']}
       Priority: {incident_data['priority']}
       
       Extract:
       1. Incident type (Performance/Availability/Security/Network)
       2. Primary symptoms
       3. Affected systems
       4. Key technical terms
       """
       
       response = bedrock_runtime.invoke_model(
           modelId='anthropic.claude-3-sonnet-20240229-v1:0',
           body=json.dumps({
               "anthropic_version": "bedrock-2023-05-31",
               "messages": [{"role": "user", "content": prompt}],
               "max_tokens": 2000
           })
       )
       
       return json.loads(response['body'].read())
   ```

9. **Develop Resolution Generator Agent**
   ```python
   def generate_resolution(incident_analysis, similar_incidents):
       prompt = f"""
       Based on this incident analysis and similar past cases, generate a resolution plan:
       
       Current Incident: {incident_analysis}
       
       Similar Past Incidents:
       {format_similar_incidents(similar_incidents)}
       
       Provide:
       1. Root cause analysis
       2. Step-by-step resolution instructions
       3. Expected outcomes for each step
       4. Risk level (Low/Medium/High)
       5. Confidence score (0-1)
       """
       
       response = bedrock_runtime.invoke_model(
           modelId='anthropic.claude-3-sonnet-20240229-v1:0',
           body=json.dumps({
               "anthropic_version": "bedrock-2023-05-31",
               "messages": [{"role": "user", "content": prompt}],
               "max_tokens": 3000
           })
       )
       
       return parse_resolution_response(response)
   ```

10. **Build Orchestrator**
    ```python
    class IncidentOrchestrator:
        def process_incident(self, incident_id):
            # Step 1: Fetch from ServiceNow
            incident = self.fetch_servicenow_incident(incident_id)
            
            # Step 2: Analyze
            analysis = self.analyze_incident(incident)
            
            # Step 3: Query vector DB
            similar = self.query_similar_incidents(analysis['embedding'])
            
            # Step 4: Generate resolution
            resolution = self.generate_resolution(analysis, similar)
            
            # Step 5: Format output
            return self.format_pilot_output(analysis, similar, resolution)
    ```

#### **Week 4: Integration & Testing**
11. **Setup API Gateway Endpoints**
    ```bash
    # Create REST API
    aws apigateway create-rest-api --name incident-resolution-api
    
    # Create webhook endpoint
    aws apigateway create-resource --rest-api-id xxx --parent-id root --path-part webhook
    ```

12. **Deploy Lambda Functions**
    ```bash
    # Package Lambda
    zip -r lambda.zip lambda_function.py requirements.txt
    
    # Deploy
    aws lambda create-function \
      --function-name incident-analyzer \
      --runtime python3.11 \
      --role arn:aws:iam::xxx:role/BedrockExecutionRole \
      --handler lambda_function.handler \
      --zip-file fileb://lambda.zip \
      --timeout 30 \
      --memory-size 512
    ```

13. **Configure Dynatrace → ServiceNow → AWS Integration**
    - Setup Dynatrace webhook to ServiceNow
    - Configure ServiceNow business rule to call AWS API Gateway
    - Test end-to-end alert flow

14. **Build Output Dashboard**
    - Create simple web UI (React/Vue) or use ServiceNow custom forms
    - Display 4-section report format:
      * Similar Past Incidents
      * Root Cause Analysis
      * Resolution Steps
      * Confidence Score & Metadata

---

### **Phase 2: Pilot Execution (Weeks 5-8)**

15. **Run 50-100 Test Cases**
    - Focus on Performance & Availability incidents
    - Collect engineer feedback on each recommendation
    - Track metrics:
      * Recommendation generation time (<3s target)
      * Accuracy rate (85%+ target)
      * Engineer satisfaction scores
      * Time saved vs manual analysis

16. **Monitor & Optimize**
    ```python
    # CloudWatch custom metrics
    cloudwatch = boto3.client('cloudwatch')
    
    cloudwatch.put_metric_data(
        Namespace='IncidentResolution/Pilot',
        MetricData=[
            {
                'MetricName': 'ProcessingTime',
                'Value': processing_time_seconds,
                'Unit': 'Seconds'
            },
            {
                'MetricName': 'AccuracyScore',
                'Value': accuracy_rating,
                'Unit': 'None'
            }
        ]
    )
    ```

17. **Collect Feedback & Iterate**
    - Weekly review meetings with engineers
    - Adjust prompts based on feedback
    - Fine-tune similarity thresholds
    - Update knowledge base with new resolutions

---

### **Phase 3: Production Rollout (Weeks 9-12)**

18. **Add Execution Agents (Steps 6-7)**
    - Implement automated command execution
    - Add approval workflows
    - Setup rollback mechanisms

19. **Add Monitoring Agents (Steps 8-9)**
    - Post-execution verification
    - Knowledge base auto-updating
    - Continuous learning pipeline

20. **Scale Infrastructure**
    - Upgrade OpenSearch to t3.medium
    - Increase Lambda concurrency limits
    - Enable multi-AZ deployment
    - Setup disaster recovery

---

## 📊 Success Metrics

### **Pilot Phase KPIs**
- ✅ **Recommendation Generation Time**: <3 seconds (95th percentile)
- ✅ **Accuracy Rate**: 85%+ recommendations rated as "useful" by engineers
- ✅ **Engineer Satisfaction**: Average rating 4/5 or higher
- ✅ **Time Savings**: 30%+ reduction in analysis time vs manual

### **Production Phase KPIs**
- 🎯 **MTTR Reduction**: 40%+ decrease in Mean Time To Resolution
- 🎯 **Auto-Resolution Rate**: 60%+ incidents resolved without human intervention
- 🎯 **False Positive Rate**: <5% incorrect recommendations
- 🎯 **System Uptime**: 99.9% availability

---

## 🔒 Security Considerations

1. **Data Encryption**
   - S3: Server-side encryption (SSE-S3)
   - OpenSearch: Encryption at rest enabled
   - Secrets Manager: Automatic rotation

2. **Network Security**
   - VPC deployment for OpenSearch
   - Private subnets for Lambda functions
   - Security groups with least privilege

3. **API Security**
   - API Gateway with OAuth2 authentication
   - Rate limiting and throttling
   - Request validation

4. **Audit Logging**
   - CloudTrail for all API calls
   - CloudWatch Logs for application logs
   - Compliance with SOC2/HIPAA requirements

---

## 📚 Additional Resources

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [OpenSearch Vector Search Guide](https://opensearch.org/docs/latest/search-plugins/knn/)
- [Dynatrace API Documentation](https://www.dynatrace.com/support/help/dynatrace-api)
- [ServiceNow REST API](https://developer.servicenow.com/dev.do)

---

## 🤝 Support & Maintenance

**Created by Code Insights @pramodklal**

For questions or issues, contact the DevOps team or raise a ticket in ServiceNow.
