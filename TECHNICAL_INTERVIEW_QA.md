# Technical Interview Questions & Answers
## Hybrid RAG E-Commerce Chatbot with Azure

---

## 1. Project Overview Questions

### Q1: Can you explain what this project does?
**Answer:** This is a Hybrid RAG (Retrieval Augmented Generation) e-commerce chatbot built with Next.js and Azure services. It allows customers to ask questions about products, orders, returns, and policies. The system retrieves relevant context from multiple data sources (structured CSV data and unstructured PDF documents) and uses Azure OpenAI GPT-4o to generate natural, helpful responses.

**Key Features:**
- Real-time product, customer, and order queries
- PDF document upload and semantic search
- Multi-index Azure AI Search integration
- Dashboard with real-time statistics
- Vector search for policy/FAQ questions
- Filter-based queries for structured data

---

### Q2: Why is it called "Hybrid RAG"?
**Answer:** It's "Hybrid" because it combines three different retrieval strategies:

1. **Vector Search (Semantic)** - Uses embeddings (text-embedding-3-large) to find semantically similar content in PDF documents
2. **Keyword Search (Full-text)** - Traditional text search on product names, descriptions, customer data
3. **Filter-Based Queries (Structured)** - SQL-like filters for precise matching (e.g., `address_state eq 'NV'`, `status eq 'Pending'`)

This hybrid approach provides:
- Better accuracy for semantic questions
- Fast exact matches for structured queries
- Flexibility to handle various query types

---

## 2. Azure Architecture Questions

### Q3: What Azure services are used in this project?
**Answer:**

1. **Azure OpenAI Service**
   - GPT-4o for chat completions
   - text-embedding-3-large for embeddings (3072 dimensions)
   - Endpoint: `https://pramo-mloh6paf-eastus2.cognitiveservices.azure.com/`

2. **Azure AI Search**
   - 6 indexes: documents, customers, orders, products, inventory, returns
   - Vector search with HNSW algorithm
   - Full-text search capabilities
   - OData filter support

3. **Azure File Share**
   - PDF storage (ecommerce-pdfs share)
   - Storage account: stecomchatbot

4. **Azure Table Storage** (legacy, now using AI Search)
   - Originally for structured data
   - Migrated to AI Search for unified querying

---

### Q4: How did you design the Azure AI Search indexes?
**Answer:** I created 6 specialized indexes:

**1. Documents Index (ecommerce-documents-index)**
- Fields: id, documentId, baseDocumentId, title, content, uploadedAt
- Vector field: contentVector (3072 dimensions)
- Purpose: PDF chunks with embeddings for semantic search

**2. Customers Index**
- Fields: id, customer_id, email, name, phone, address_*
- Searchable: name, email
- Filterable: customer_id, address_state

**3. Orders Index**
- Fields: id, order_id, customer_id, status, total_amount, order_date
- Filterable: status, order_date
- Purpose: Order tracking and status queries

**4. Products Index**
- Fields: id, product_id, name, description, price, category
- Searchable: name, description, category
- Purpose: Product search and recommendations

**5. Inventory Index**
- Fields: id, product_id, quantity, warehouse_location
- Filterable: quantity (for low stock alerts)

**6. Returns Index**
- Fields: id, return_id, order_id, status, return_date, refund_amount
- Filterable: status, return_date

---

### Q5: Why did you choose Azure AI Search over other databases?
**Answer:**

**Advantages:**
1. **Unified Platform** - Combines vector search, full-text search, and filtering in one service
2. **Vector Search Support** - Native support for embeddings with HNSW algorithm
3. **Scalability** - Auto-scales based on load, handles millions of documents
4. **Rich Query Language** - OData filters, faceted search, suggester support
5. **Azure Integration** - Works seamlessly with Azure OpenAI, Storage, and other services
6. **Low Latency** - Optimized for real-time queries (<100ms for most searches)

**vs. Traditional Databases:**
- PostgreSQL with pgvector: Requires manual optimization, slower vector search
- MongoDB: Good for documents but lacks advanced search features
- SQL Server: Not optimized for vector search

**vs. Vector Databases:**
- Pinecone/Weaviate: Great for vectors but poor at structured queries
- Azure AI Search: Best of both worlds

---

## 3. Technical Implementation Questions

### Q6: Walk me through the chat flow when a user asks a question.
**Answer:**

```
1. User Input → POST /api/chat
   ↓
2. Keyword Detection
   - Match question to categories (policy, customer, order, product, return)
   ↓
3. Context Retrieval (Parallel if needed)
   ├─ Policy Query → Vector Search or Keyword Search on documents index
   ├─ Customer Query → Filter search on customers index
   ├─ Order Query → Filter/keyword search on orders index
   ├─ Product Query → Keyword search on products index
   └─ Return Query → Keyword search on returns index
   ↓
4. Build System Prompt
   - Include retrieved context as JSON
   - Add instructions for AI assistant role
   ↓
5. Call Azure OpenAI GPT-4o
   - Temperature: 0.7
   - Max tokens: 800
   ↓
6. Return Response to Frontend
   - Display in chat widget
```

**Code Location:** `app/api/chat/route.ts`

---

### Q7: How do you handle PDF uploads and indexing?
**Answer:**

**Step-by-step process:**

1. **File Upload** (`POST /api/admin/upload-pdf`)
   - Receive PDF file from admin panel
   - Validate file type and size

2. **Text Extraction** (`lib/utils/pdf-extraction.ts`)
   - Use pdf2json library (switched from pdf-parse due to Next.js compatibility)
   - Extract text from all pages
   - Extract metadata (title, author, page count)

3. **Chunking** (`lib/utils/chunking.ts`)
   - Split text into chunks (max 500 tokens)
   - Use tiktoken for accurate token counting
   - Add overlap (50 tokens) to preserve context
   - Each chunk gets unique ID: `${baseDocumentId}-chunk-${index}`

4. **Generate Embeddings** (`lib/azure/openai.ts`)
   - Call Azure OpenAI text-embedding-3-large
   - Returns 3072-dimensional vectors per chunk
   - Batch processing for efficiency

5. **Upload to Azure File Share** (`lib/azure/storage.ts`)
   - Store original PDF in stecomchatbot/ecommerce-pdfs
   - Preserve for future reference/re-indexing

6. **Index in Azure AI Search** (`lib/azure/search.ts`)
   - Upload chunks with embeddings to ecommerce-documents-index
   - Fields: id, documentId, baseDocumentId, title, content, contentVector, uploadedAt

**Challenge Faced:** pdf-parse had debug code that caused ENOENT errors in Next.js. Switched to pdf2json which uses event-based API.

---

### Q8: Explain the vector search implementation.
**Answer:**

**Configuration:**

```typescript
// Index definition
{
  name: "ecommerce-documents-index",
  fields: [
    { name: "contentVector", type: "Collection(Edm.Single)", 
      vectorSearchDimensions: 3072, vectorSearchProfileName: "vector-profile" }
  ],
  vectorSearch: {
    algorithms: [{
      name: "hnsw-algorithm",
      kind: "hnsw",
      hnswParameters: { 
        metric: "cosine", 
        m: 4, 
        efConstruction: 400, 
        efSearch: 500 
      }
    }],
    profiles: [{
      name: "vector-profile",
      algorithmConfigurationName: "hnsw-algorithm"
    }]
  }
}
```

**Search Process:**

```typescript
async function vectorSearch(query: string, options?: { top?: number }) {
  // 1. Generate query embedding
  const [embedding] = await generateEmbeddings(query) // 3072 dimensions
  
  // 2. Perform vector search
  const results = await client.search('*', {
    vectorSearchOptions: {
      queries: [{
        kind: 'vector',
        vector: embedding,
        kNearestNeighborsCount: options?.top || 5,
        fields: ['contentVector']
      }]
    }
  })
  
  // 3. Return documents sorted by similarity
  return results.results.map(r => r.document)
}
```

**Key Parameters:**
- **HNSW (Hierarchical Navigable Small World)** - Graph-based algorithm for fast ANN search
- **Cosine similarity** - Measures angle between vectors (0-1, higher = more similar)
- **M parameter (4)** - Max connections per node (balance between accuracy and memory)
- **efConstruction (400)** - Build-time parameter (higher = better recall)
- **efSearch (500)** - Query-time parameter (higher = better accuracy, slower)

---

### Q9: How do you handle CSV uploads and data transformation?
**Answer:**

**CSV Upload Process** (`app/api/admin/upload-csv/route.ts`):

1. **Parse CSV**
   ```typescript
   const parseCSV = (csvContent: string): Record<string, any>[] => {
     const lines = csvContent.trim().split('\n')
     const headers = lines[0].split(',').map(h => h.trim().replace(/^"|"$/g, ''))
     
     return lines.slice(1).map(line => {
       const values = line.split(',').map(v => v.trim().replace(/^"|"$/g, ''))
       const record: Record<string, any> = { id: crypto.randomUUID() }
       headers.forEach((header, i) => { record[header] = values[i] })
       return record
     })
   }
   ```

2. **Type-Specific Transformations**
   ```typescript
   const transformRecords = (records: any[], type: string) => {
     return records.map(record => {
       const transformed = { ...record }
       
       // Convert numeric fields
       if (type === 'products') {
         transformed.price = parseFloat(record.price) || 0
         transformed.rating = parseFloat(record.rating) || 0
       }
       
       if (type === 'inventory') {
         transformed.quantity = parseInt(record.quantity) || 0
         transformed.reorder_point = parseInt(record.reorder_point) || 0
       }
       
       // Preserve snake_case field names (NOT camelCase)
       // This matches the actual CSV structure
       return transformed
     })
   }
   ```

3. **Batch Index Upload**
   ```typescript
   const client = getSearchClient(indexName)
   await client.uploadDocuments(transformedRecords)
   ```

**Important:** Initially tried camelCase conversion but it caused schema mismatches. Now preserves original CSV field names (snake_case).

---

### Q10: What was your biggest technical challenge?
**Answer:**

**Challenge:** Azure OpenAI deployment configuration and client initialization errors.

**Problems Encountered:**

1. **Wrong Endpoint** - Using `https://pkAzureOpen.openai.azure.com` when actual was `https://pramo-mloh6paf-eastus2.cognitiveservices.azure.com/`

2. **Wrong API Key** - Multiple Azure OpenAI resources, used wrong key

3. **Deployment Name Mismatch** - Configured `gpt-4` but actual deployment was `gpt-4o`

4. **Client Initialization Error** - Passing `deployment` parameter in AzureOpenAI constructor (invalid)
   ```typescript
   // WRONG
   new AzureOpenAI({ 
     endpoint, 
     apiKey, 
     deployment: 'gpt-4o' // ❌ Invalid parameter
   })
   
   // CORRECT
   new AzureOpenAI({ endpoint, apiKey })
   // Pass deployment as 'model' in API calls
   azureOpenAI.chat.completions.create({ model: 'gpt-4o', ... })
   ```

5. **Global Standard Deployment Delay** - text-embedding-3-large showed "Succeeded" but took 10+ minutes to become available

**Resolution Steps:**
1. Listed all Azure OpenAI resources in portal
2. Verified deployments in Azure AI Studio
3. Tested each deployment via REST API
4. Fixed client initialization code
5. Added fallback to keyword search when vector search fails
6. Added comprehensive error logging

**Lesson Learned:** Always verify actual resource configurations in Azure Portal/AI Studio, don't assume based on config files.

---

## 4. Code Quality & Best Practices Questions

### Q11: How did you structure the codebase?
**Answer:**

```
ecommerce-app-azure/
├── app/                          # Next.js App Router
│   ├── api/                      # API Routes
│   │   ├── chat/route.ts         # Chatbot endpoint
│   │   ├── admin/                # Admin endpoints
│   │   │   ├── upload-pdf/route.ts
│   │   │   └── upload-csv/route.ts
│   │   └── dashboard/stats/route.ts
│   ├── page.tsx                  # Homepage
│   └── layout.tsx                # Root layout
├── components/
│   ├── AIChatWidget.tsx          # Chat UI component
│   └── ui/                       # Reusable UI components
├── lib/
│   ├── azure/                    # Azure service clients
│   │   ├── openai.ts             # Azure OpenAI wrapper
│   │   ├── search.ts             # Azure AI Search wrapper
│   │   ├── storage.ts            # Azure File Share client
│   │   └── tables.ts             # Azure Table Storage (legacy)
│   └── utils/
│       ├── pdf-extraction.ts     # PDF text extraction
│       └── chunking.ts           # Text chunking with tiktoken
├── scripts/                      # PowerShell automation
│   ├── create-documents-index.ps1
│   ├── create-csv-indexes.ps1
│   └── upload-pdfs-to-fileshare.ps1
└── data/                         # CSV datasets
    ├── ecommerce-customers.csv
    ├── ecommerce-orders.csv
    └── pdfs/
```

**Design Principles:**
1. **Separation of Concerns** - Azure clients isolated in `lib/azure/`
2. **Reusable Components** - UI components in `components/ui/`
3. **Type Safety** - TypeScript throughout
4. **Environment Variables** - All secrets in `.env.local`
5. **Error Handling** - Try-catch with fallbacks
6. **Logging** - Console logs for debugging

---

### Q12: How do you handle errors and edge cases?
**Answer:**

**1. API Route Error Handling**
```typescript
export async function POST(request: Request) {
  try {
    const { message } = await request.json()
    
    // Validation
    if (!message || typeof message !== 'string') {
      return NextResponse.json({ error: 'Message is required' }, { status: 400 })
    }
    
    // Process...
    
  } catch (error) {
    console.error('Chat API Error:', error)
    return NextResponse.json(
      { error: 'Failed to process chat message' }, 
      { status: 500 }
    )
  }
}
```

**2. Fallback for Vector Search**
```typescript
try {
  const policyDocs = await vectorSearch(message, { top: 3 })
  contextInfo = policyDocs.map(doc => doc.content).join('\n\n')
} catch (error) {
  // Fallback to keyword search if embeddings unavailable
  const documentsClient = getSearchClient(INDEXES.DOCUMENTS)
  const docResults = await documentsClient.search(message, { top: 3 })
  // ... use keyword results
}
```

**3. Empty Results Handling**
```typescript
if (products.length > 0) {
  contextInfo += `\n\nRelevant Products:\n${JSON.stringify(products, null, 2)}`
} else {
  // GPT-4o will indicate no products found
}
```

**4. Environment Variable Validation**
```typescript
if (!process.env.AZURE_OPENAI_ENDPOINT) {
  throw new Error('AZURE_OPENAI_ENDPOINT is not defined')
}
```

**5. Client-Side Error Display**
```typescript
// Frontend shows user-friendly message
catch (error) {
  setMessages(prev => [...prev, { 
    role: 'assistant', 
    content: 'Sorry, I encountered an error. Please try again.' 
  }])
}
```

---

## 5. Performance & Scalability Questions

### Q13: How would you optimize this system for production?
**Answer:**

**Current Performance:**
- Average response time: 1-3 seconds
- Azure AI Search queries: <100ms
- OpenAI API calls: 500-1500ms

**Optimization Strategies:**

**1. Caching Layer**
```typescript
// Redis cache for common queries
const cacheKey = `search:${message.toLowerCase()}`
const cached = await redis.get(cacheKey)
if (cached) return JSON.parse(cached)

// Cache for 5 minutes
await redis.setex(cacheKey, 300, JSON.stringify(results))
```

**2. Streaming Responses**
```typescript
// Already implemented in lib/azure/openai.ts
export async function* streamChatCompletion(messages) {
  const stream = await azureOpenAI.chat.completions.create({
    model: 'gpt-4o',
    messages,
    stream: true // Enable streaming
  })
  
  for await (const chunk of stream) {
    yield chunk.choices[0]?.delta?.content
  }
}
```

**3. Index Optimization**
```typescript
// Add suggester for autocomplete
{
  suggesters: [{
    name: "product-suggester",
    sourceFields: ["name", "category"]
  }]
}

// Selective field retrieval
await searchClient.search(query, {
  select: ['product_id', 'name', 'price'], // Don't fetch all fields
  top: 10
})
```

**4. Connection Pooling**
```typescript
// Reuse Azure clients (singleton pattern)
let searchClientInstance: SearchClient
export function getSearchClient(indexName: string) {
  if (!searchClientInstance) {
    searchClientInstance = new SearchClient(endpoint, indexName, credential)
  }
  return searchClientInstance
}
```

**5. Batch Processing**
```typescript
// Upload documents in batches of 1000
const BATCH_SIZE = 1000
for (let i = 0; i < documents.length; i += BATCH_SIZE) {
  const batch = documents.slice(i, i + BATCH_SIZE)
  await client.uploadDocuments(batch)
}
```

**6. CDN for Static Assets**
- Host Next.js static files on Azure CDN
- Reduce server load for images, CSS, JS

**7. Azure AI Search Tiers**
- Development: Basic tier ($75/month)
- Production: Standard S1 ($250/month) for better performance
- Enterprise: S3 for high-volume applications

---

### Q14: How would you handle 1000 concurrent users?
**Answer:**

**Architecture Changes:**

**1. Horizontal Scaling**
- Deploy Next.js app to Azure App Service with auto-scaling
- Rule: Scale out when CPU > 70% or Memory > 80%
- Max instances: 10

**2. Azure AI Search Scaling**
- Upgrade to Standard S2 or S3 tier
- Add replicas for read performance (3-4 replicas)
- Partitions for data volume (1-2 partitions sufficient)

**3. Rate Limiting**
```typescript
import rateLimit from 'express-rate-limit'

const limiter = rateLimit({
  windowMs: 1 * 60 * 1000, // 1 minute
  max: 20, // 20 requests per minute per IP
  message: 'Too many requests, please try again later'
})

export default limiter
```

**4. Queue System for PDF Processing**
```typescript
// Azure Queue Storage or Service Bus
// Move PDF processing to background job
await queueClient.sendMessage(JSON.stringify({
  type: 'pdf-upload',
  fileUrl: pdfUrl,
  userId: req.userId
}))

// Worker processes queue asynchronously
```

**5. Database Connection Pooling**
```typescript
const pool = new Pool({
  max: 20, // Max connections
  idleTimeoutMillis: 30000
})
```

**6. Monitoring & Alerts**
- Azure Application Insights for monitoring
- Alert on API latency > 3s
- Alert on error rate > 5%
- Track token usage and costs

**Cost Estimation for 1000 concurrent users:**
- Azure App Service (Premium P2v2): ~$200/month
- Azure AI Search (Standard S2): ~$500/month
- Azure OpenAI (50K TPM): ~$1000-2000/month (varies by usage)
- Azure Storage: ~$50/month
- **Total: ~$1750-2750/month**

---

## 6. Security Questions

### Q15: How do you secure this application?
**Answer:**

**Current Security Measures:**

**1. API Key Protection**
```typescript
// .env.local (not committed to git)
AZURE_OPENAI_API_KEY=***
AZURE_SEARCH_API_KEY=***

// .gitignore includes .env.local
```

**2. Input Validation**
```typescript
// Sanitize user input
const sanitized = message.trim().substring(0, 500) // Max 500 chars

// Prevent SQL/NoSQL injection in filters
const safeState = stateMatch[1].toUpperCase().replace(/[^A-Z]/g, '')
filter: `address_state eq '${safeState}'`
```

**3. CORS Configuration**
```typescript
// next.config.js
module.exports = {
  async headers() {
    return [{
      source: '/api/:path*',
      headers: [
        { key: 'Access-Control-Allow-Origin', value: 'https://yourdomain.com' },
        { key: 'Access-Control-Allow-Methods', value: 'POST, GET, OPTIONS' }
      ]
    }]
  }
}
```

**Production Enhancements Needed:**

**1. Authentication & Authorization**
```typescript
import { getServerSession } from 'next-auth'

export async function POST(request: Request) {
  const session = await getServerSession()
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }
  
  // Admin endpoints require admin role
  if (request.url.includes('/admin/') && session.user.role !== 'admin') {
    return NextResponse.json({ error: 'Forbidden' }, { status: 403 })
  }
}
```

**2. Rate Limiting (per user)**
```typescript
const userRateLimit = new Map<string, { count: number, resetTime: number }>()

function checkRateLimit(userId: string): boolean {
  const now = Date.now()
  const userLimit = userRateLimit.get(userId)
  
  if (!userLimit || now > userLimit.resetTime) {
    userRateLimit.set(userId, { count: 1, resetTime: now + 60000 })
    return true
  }
  
  if (userLimit.count >= 20) return false
  
  userLimit.count++
  return true
}
```

**3. Azure Key Vault Integration**
```typescript
import { SecretClient } from '@azure/keyvault-secrets'

const client = new SecretClient(vaultUrl, credential)
const secret = await client.getSecret('AZURE-OPENAI-KEY')
const apiKey = secret.value
```

**4. Content Safety Filtering**
```typescript
// Azure OpenAI already has DefaultV2 content filter
// Additional custom filtering:
const bannedWords = ['inappropriate', 'sensitive']
if (bannedWords.some(word => message.toLowerCase().includes(word))) {
  return NextResponse.json({ 
    error: 'Message contains inappropriate content' 
  }, { status: 400 })
}
```

**5. HTTPS Only**
```typescript
// Azure App Service - force HTTPS
if (request.headers.get('x-forwarded-proto') !== 'https') {
  return NextResponse.redirect(`https://${request.headers.get('host')}${request.url}`)
}
```

**6. Data Encryption**
- Azure Storage: Encryption at rest (automatic)
- Azure AI Search: TLS 1.2+ for data in transit
- Azure OpenAI: API calls over HTTPS

---

## 7. Troubleshooting Scenarios

### Q16: User reports chatbot is slow. How do you debug?
**Answer:**

**Step 1: Check Application Insights**
```
- Navigate to Azure Portal → Application Insights
- Look at "Performance" tab
- Identify slow operations:
  - API response times
  - Azure AI Search query duration
  - OpenAI API latency
```

**Step 2: Check Terminal Logs**
```
=== CHATBOT DEBUG ===
User Question: what is the price of laptops
Context Retrieved: YES
Context Length: 2341 characters
Azure AI Search query time: 89ms  ← Fast
OpenAI API call time: 2341ms      ← Slow! (should be ~500-800ms)
```

**Step 3: Investigate OpenAI**
- Check if quota is exceeded (429 errors)
- Verify TPM (tokens per minute) limit
- Reduce max_tokens if response too long

**Step 4: Optimize Context**
```typescript
// Before: Sending too much context
contextInfo = JSON.stringify(products, null, 2) // 5000+ chars

// After: Send only required fields
contextInfo = products.map(p => ({
  name: p.name,
  price: p.price,
  id: p.product_id
}))
```

**Step 5: Add Caching**
```typescript
const cacheKey = `products:${query}`
const cached = cache.get(cacheKey)
if (cached) return cached // Instant response
```

---

### Q17: Vector search returns irrelevant results. How do you improve it?
**Answer:**

**Problem Analysis:**

1. **Check Embedding Quality**
```typescript
// Test embedding generation
const text = "What is the return policy?"
const [embedding] = await generateEmbeddings(text)
console.log('Embedding dimensions:', embedding.length) // Should be 3072
console.log('Sample values:', embedding.slice(0, 5))
```

2. **Verify Index Configuration**
```powershell
# Check vector search settings
Invoke-RestMethod -Uri "$searchEndpoint/indexes/ecommerce-documents-index?api-version=2023-11-01" -Headers @{"api-key"=$apiKey} | ConvertTo-Json -Depth 10
```

**Solutions:**

**1. Improve Chunking**
```typescript
// Before: Large chunks (1000 tokens)
const chunks = chunkByTokens(text, 1000, 100)

// After: Smaller, focused chunks (300 tokens)
const chunks = chunkByTokens(text, 300, 50)
// Better semantic coherence per chunk
```

**2. Add Metadata Filtering**
```typescript
// Combine vector search with filters
const results = await client.search('*', {
  vectorSearchOptions: {
    queries: [{
      kind: 'vector',
      vector: embedding,
      kNearestNeighborsCount: 10
    }]
  },
  filter: "document_type eq 'policy'", // Only search policies
  top: 3
})
```

**3. Tune HNSW Parameters**
```typescript
// Increase accuracy (slower but better results)
hnswParameters: {
  metric: "cosine",
  m: 6,              // Increase from 4
  efConstruction: 600, // Increase from 400
  efSearch: 800      // Increase from 500
}
```

**4. Rerank Results**
```typescript
// Hybrid: Vector + keyword scoring
const vectorResults = await vectorSearch(query)
const keywordResults = await keywordSearch(query)

// Combine with weights
const combined = mergeResults(vectorResults, keywordResults, {
  vectorWeight: 0.7,
  keywordWeight: 0.3
})
```

**5. Query Expansion**
```typescript
// Expand user query with synonyms
const expandedQuery = await expandQuery("cheap laptop")
// Returns: "affordable laptop, inexpensive computer, budget notebook"
const results = await vectorSearch(expandedQuery)
```

---

## 8. Advanced Topics

### Q18: How would you implement multi-tenant support?
**Answer:**

**Architecture:**

```typescript
// Tenant isolation at index level
function getIndexName(tenantId: string, baseIndex: string): string {
  return `${tenantId}-${baseIndex}` // e.g., "tenant1-ecommerce-products-index"
}

// Chat endpoint with tenant
export async function POST(request: Request) {
  const tenantId = request.headers.get('X-Tenant-ID')
  if (!tenantId) return NextResponse.json({ error: 'Missing tenant' }, { status: 400 })
  
  const productsIndex = getIndexName(tenantId, 'products')
  const client = getSearchClient(productsIndex)
  
  // Query tenant-specific index
  const results = await client.search(message)
}
```

**Tenant Provisioning:**
```typescript
async function provisionTenant(tenantId: string) {
  const baseIndexes = ['products', 'orders', 'customers', 'documents']
  
  for (const baseIndex of baseIndexes) {
    const indexName = getIndexName(tenantId, baseIndex)
    await createIndex(indexName)
  }
  
  // Create tenant-specific storage container
  await createStorageContainer(`${tenantId}-pdfs`)
}
```

**Cost Optimization:**
- Use shared Azure AI Search service
- Separate indexes per tenant
- Tenant-specific Azure OpenAI deployments for high-volume tenants
- Shared deployment for small tenants

---

### Q19: How would you implement A/B testing for different prompts?
**Answer:**

```typescript
// Prompt variants
const PROMPTS = {
  A: `You are a helpful e-commerce assistant. Be concise and professional.`,
  B: `You are a friendly shopping companion. Use a warm, conversational tone with emojis.`,
  C: `You are an expert product consultant. Provide detailed technical information.`
}

// Assign variant based on user ID
function getPromptVariant(userId: string): string {
  const hash = hashCode(userId)
  const variant = ['A', 'B', 'C'][hash % 3]
  return PROMPTS[variant]
}

// Track metrics
interface ChatMetrics {
  userId: string
  promptVariant: string
  userSatisfaction: number // 1-5 rating
  responseTime: number
  followUpQuestions: number
}

// Log to analytics
await logMetrics({
  userId: session.userId,
  promptVariant: variant,
  userSatisfaction: rating,
  responseTime: endTime - startTime,
  followUpQuestions: conversationLength
})

// Analysis query
SELECT 
  promptVariant,
  AVG(userSatisfaction) as avg_satisfaction,
  AVG(responseTime) as avg_response_time,
  AVG(followUpQuestions) as avg_follow_ups
FROM ChatMetrics
GROUP BY promptVariant
```

---

### Q20: Explain your monitoring and observability strategy.
**Answer:**

**1. Azure Application Insights Integration**
```typescript
import { ApplicationInsights } from '@microsoft/applicationinsights-web'

const appInsights = new ApplicationInsights({
  config: {
    connectionString: process.env.APPLICATIONINSIGHTS_CONNECTION_STRING
  }
})

appInsights.loadAppInsights()

// Track custom events
appInsights.trackEvent({
  name: 'ChatbotQuery',
  properties: {
    question: message,
    retrievalMethod: 'vector-search',
    responseTime: duration,
    tokensUsed: completionTokens
  }
})
```

**2. Logging Strategy**
```typescript
// Structured logging
console.log(JSON.stringify({
  timestamp: new Date().toISOString(),
  level: 'INFO',
  service: 'chatbot-api',
  endpoint: '/api/chat',
  userId: session.userId,
  question: message,
  contextRetrieved: !!contextInfo,
  contextLength: contextInfo?.length,
  openaiTokens: completion.usage?.total_tokens,
  responseTime: duration
}))
```

**3. Metrics Dashboard**
```
Key Metrics:
- Chat requests per minute
- Average response time (target: <2s)
- Azure AI Search query latency (target: <100ms)
- OpenAI API latency (target: <1s)
- Error rate (target: <1%)
- User satisfaction (from ratings)
- Token usage and cost
```

**4. Alerts**
```
Critical Alerts:
- Error rate > 5% (5 min window)
- API latency > 5s (10 consecutive requests)
- OpenAI API 429 errors (rate limit)
- Azure AI Search unavailable

Warning Alerts:
- Response time > 3s (average over 5 min)
- Daily token usage > 80% of quota
- Storage usage > 80% capacity
```

**5. Tracing**
```typescript
import { trace, context } from '@opentelemetry/api'

const tracer = trace.getTracer('chatbot-service')

const span = tracer.startSpan('process_chat_request')
span.setAttribute('user.question', message)

try {
  const searchSpan = tracer.startSpan('azure_search_query', { parent: span })
  const results = await searchClient.search(message)
  searchSpan.end()
  
  const openaiSpan = tracer.startSpan('openai_completion', { parent: span })
  const completion = await generateChatCompletion(messages)
  openaiSpan.end()
} finally {
  span.end()
}
```

---

## 9. Cost Optimization

### Q21: How do you estimate and optimize Azure costs?
**Answer:**

**Current Monthly Cost Breakdown:**

1. **Azure OpenAI**
   - GPT-4o: $0.0025/1K input tokens, $0.01/1K output tokens
   - text-embedding-3-large: $0.00013/1K tokens
   - Estimate: 1M tokens/month = $3-5

2. **Azure AI Search**
   - Standard S1: $250/month (50 GB storage, 3000 queries/second)
   - Development: Basic tier $75/month

3. **Azure Storage**
   - File Share: $0.06/GB/month
   - 10 GB = $0.60/month

4. **Azure App Service**
   - Basic B1: $13.14/month
   - Standard S1: $69.35/month

**Total Development Cost: ~$90-100/month**
**Total Production Cost: ~$350-400/month**

**Optimization Strategies:**

1. **Token Optimization**
```typescript
// Reduce context sent to GPT-4o
const summarizedContext = products.map(p => 
  `${p.name}: $${p.price}` // Strip unnecessary fields
).join(', ')

// Use lower max_tokens
await generateChatCompletion(messages, { maxTokens: 500 }) // Instead of 1000
```

2. **Caching**
```typescript
// Cache common queries to avoid repeated OpenAI calls
const cached = await redis.get(`chat:${messageHash}`)
if (cached) return cached // Saves $0.0025 per request
```

3. **Smart Routing**
```typescript
// Use GPT-3.5-turbo for simple queries (10x cheaper)
const isSimpleQuery = message.split(' ').length < 10
const model = isSimpleQuery ? 'gpt-35-turbo' : 'gpt-4o'
```

4. **Batch Operations**
```typescript
// Generate embeddings in batches (same cost, faster)
const embeddings = await generateEmbeddings([text1, text2, text3]) // 1 API call instead of 3
```

5. **Index Tier Selection**
```typescript
// Use Basic tier for dev/staging
// Use Standard S1 only for production
// Don't over-provision replicas/partitions
```

**Cost Monitoring:**
```typescript
// Track token usage
let totalTokensUsed = 0
completion.usage && (totalTokensUsed += completion.usage.total_tokens)

// Alert when approaching limits
if (totalTokensUsed > DAILY_TOKEN_LIMIT * 0.8) {
  await sendAlert('Token usage at 80% of daily limit')
}
```

---

## 10. Future Enhancements

### Q22: What improvements would you add?
**Answer:**

**Short-term (1-3 months):**

1. **Conversation History**
```typescript
// Store chat history per user
interface ChatHistory {
  userId: string
  messages: Array<{ role: string, content: string, timestamp: Date }>
}

// Include recent context in prompts
const recentHistory = await getChatHistory(userId, limit: 5)
const messages = [...recentHistory, { role: 'user', content: message }]
```

2. **User Feedback Loop**
```typescript
// Thumbs up/down on responses
<button onClick={() => rateChatResponse(messageId, 'positive')}>👍</button>

// Store feedback in database
// Use to improve prompts and retrieval
```

3. **Product Recommendations**
```typescript
// Collaborative filtering based on user history
const similarUsers = await findSimilarUsers(userId)
const recommended = await getPopularProducts(similarUsers)
```

4. **Multi-language Support**
```typescript
// Detect language
const language = detectLanguage(message) // 'en', 'es', 'fr'

// Translate query
const translatedQuery = await translate(message, 'en')

// Search in English
const results = await search(translatedQuery)

// Translate response back
const translatedResponse = await translate(response, language)
```

**Long-term (6-12 months):**

1. **Voice Interface**
- Azure Speech-to-Text for voice input
- Text-to-Speech for audio responses

2. **Image Search**
- Azure Computer Vision for product images
- Visual similarity search

3. **Personalization Engine**
- User profile: preferences, purchase history
- Personalized product recommendations
- Custom pricing/offers

4. **Analytics Dashboard**
- Most asked questions
- Popular products
- Conversion funnel tracking
- User satisfaction trends

5. **Advanced RAG Techniques**
- HyDE (Hypothetical Document Embeddings)
- Query decomposition for complex questions
- Multi-hop reasoning across documents

---

## 11. Testing & Accuracy Verification

### Q23: How do you verify that chatbot responses are accurate?
**Answer:**

**Multi-Layer Verification Strategy:**

**1. Manual Testing Checklist**
```typescript
// Test cases for different query types
const testCases = [
  // Customer queries
  { query: "what is email of CUST-003", expected: "sarah.miller@email.com" },
  { query: "customers in Nevada", expectedCount: ">0", expectedField: "address_state: NV" },
  
  // Product queries
  { query: "price of Wireless Bluetooth Headphones", expected: "$79.99" },
  { query: "laptop under $1000", expectedType: "product list" },
  
  // Order queries
  { query: "pending orders", expectedFilter: "status eq 'Pending'" },
  { query: "orders by CUST-001", expectedCustomer: "CUST-001" },
  
  // Policy queries (PDF content)
  { query: "international shipping policy", expectedSource: "shipping_policy.pdf" },
  { query: "return policy", expectedKeywords: ["return", "refund", "days"] }
]
```

**2. Automated Testing Framework**
```typescript
// Integration test example
describe('Chatbot API', () => {
  it('should return accurate customer email', async () => {
    const response = await fetch('/api/chat', {
      method: 'POST',
      body: JSON.stringify({ message: 'what is email of CUST-003' })
    })
    
    const data = await response.json()
    expect(data.reply).toContain('sarah.miller@email.com')
  })
  
  it('should retrieve correct product price', async () => {
    const response = await fetch('/api/chat', {
      method: 'POST',
      body: JSON.stringify({ message: 'price of Wireless Bluetooth Headphones' })
    })
    
    const data = await response.json()
    expect(data.reply).toMatch(/\$79\.99/)
  })
})
```

**3. Context Verification**
```typescript
// Add debug mode to see what context was retrieved
export async function POST(request: Request) {
  const { message, debugMode } = await request.json()
  
  // ... retrieve context ...
  
  if (debugMode) {
    return NextResponse.json({
      reply: aiResponse,
      debug: {
        contextRetrieved: contextInfo,
        searchMethod: 'vector-search',
        documentsFound: documents.length,
        searchQuery: message,
        indexUsed: 'ecommerce-documents-index'
      }
    })
  }
}
```

**4. Ground Truth Comparison**
```typescript
// Compare against known correct answers
interface GroundTruth {
  question: string
  correctAnswer: string
  acceptableVariations: string[]
}

const groundTruth: GroundTruth[] = [
  {
    question: "what is email of CUST-003",
    correctAnswer: "sarah.miller@email.com",
    acceptableVariations: ["sarah.miller@email.com", "The email is sarah.miller@email.com"]
  }
]

function verifyAccuracy(response: string, groundTruth: GroundTruth): boolean {
  return groundTruth.acceptableVariations.some(variation => 
    response.toLowerCase().includes(variation.toLowerCase())
  )
}
```

**5. Hallucination Detection**
```typescript
// Check if response contains information NOT in context
function detectHallucination(response: string, context: string): boolean {
  // Extract factual claims (prices, emails, dates, IDs)
  const responseFacts = extractFacts(response)
  
  // Verify each fact exists in context
  for (const fact of responseFacts) {
    if (!context.includes(fact)) {
      console.warn('Potential hallucination detected:', fact)
      return true
    }
  }
  
  return false
}
```

---

### Q24: What metrics do you use to measure chatbot quality?
**Answer:**

**1. Accuracy Metrics**

```typescript
// Exact Match Accuracy
const exactMatchAccuracy = correctAnswers / totalQuestions
// Example: 45/50 = 90%

// Semantic Similarity (using embeddings)
async function calculateSemanticSimilarity(predicted: string, expected: string): Promise<number> {
  const [predEmbedding] = await generateEmbeddings(predicted)
  const [expEmbedding] = await generateEmbeddings(expected)
  
  // Cosine similarity
  const similarity = cosineSimilarity(predEmbedding, expEmbedding)
  return similarity // 0-1, higher is better
}

// F1 Score for information retrieval
interface RetrievalMetrics {
  precision: number // Relevant retrieved / Total retrieved
  recall: number    // Relevant retrieved / Total relevant
  f1Score: number   // 2 * (precision * recall) / (precision + recall)
}

function calculateF1(retrieved: string[], relevant: string[]): RetrievalMetrics {
  const retrievedSet = new Set(retrieved)
  const relevantSet = new Set(relevant)
  
  const truePositives = retrieved.filter(r => relevantSet.has(r)).length
  const precision = truePositives / retrieved.length
  const recall = truePositives / relevant.length
  const f1Score = 2 * (precision * recall) / (precision + recall)
  
  return { precision, recall, f1Score }
}
```

**2. Response Quality Metrics**

```typescript
interface QualityMetrics {
  // User satisfaction (1-5 stars)
  avgRating: number
  
  // Did the answer help?
  resolutionRate: number // % of queries that didn't need follow-up
  
  // Response completeness
  avgResponseLength: number // Characters
  
  // Latency
  avgResponseTime: number // Milliseconds
  
  // Error rate
  errorRate: number // % of failed requests
  
  // Fallback rate
  fallbackRate: number // % using keyword search instead of vector
}

// Track in database
async function trackMetrics(interaction: ChatInteraction) {
  await db.insert('chat_metrics', {
    timestamp: new Date(),
    userId: interaction.userId,
    question: interaction.question,
    responseTime: interaction.responseTime,
    tokensUsed: interaction.tokensUsed,
    searchMethod: interaction.searchMethod,
    userRating: null, // Set when user rates
    resolved: null    // Set if user asks follow-up
  })
}
```

**3. Retrieval Metrics**

```typescript
// Context relevance
const contextRelevanceScore = await evaluateContextRelevance(question, retrievedContext)

async function evaluateContextRelevance(question: string, context: string): Promise<number> {
  // Use GPT-4o as judge
  const prompt = `
    Question: ${question}
    Context: ${context}
    
    Rate the relevance of the context to answering the question on a scale of 1-10.
    Only output the number.
  `
  
  const response = await generateChatCompletion([
    { role: 'user', content: prompt }
  ], { maxTokens: 5 })
  
  return parseInt(response) / 10 // Normalize to 0-1
}

// Search quality metrics
interface SearchMetrics {
  averageSearchTime: number     // ms
  vectorSearchSuccessRate: number // % of times vector search works
  avgDocumentsRetrieved: number   // How many docs per query
  avgContextLength: number        // Characters of context
}
```

**4. Business Metrics**

```typescript
interface BusinessMetrics {
  // Engagement
  dailyActiveUsers: number
  avgQueriesPerUser: number
  sessionDuration: number // minutes
  
  // Conversion
  chatToOrderRate: number // % of chat users who placed orders
  avgOrderValueAfterChat: number // $
  
  // Efficiency
  chatReductionInSupportTickets: number // %
  avgHandlingTime: number // Seconds per query
  
  // Cost
  costPerQuery: number // $ (OpenAI tokens + infrastructure)
  costPerConversion: number // $
}
```

**5. A/B Testing Metrics**

```typescript
// Compare different configurations
interface ABTestResults {
  variant: 'A' | 'B'
  
  // Accuracy
  accuracy: number
  
  // User satisfaction
  avgRating: number
  thumbsUpRate: number
  
  // Performance
  avgResponseTime: number
  
  // Business impact
  conversionRate: number
}

// Example: Test vector search vs keyword search
const results = {
  vectorSearch: { accuracy: 0.92, avgRating: 4.5, responseTime: 1200 },
  keywordSearch: { accuracy: 0.78, avgRating: 3.9, responseTime: 300 }
}
// Decision: Use vector search (better accuracy) with caching to improve speed
```

---

### Q25: How do you test the RAG pipeline end-to-end?
**Answer:**

**End-to-End Testing Strategy:**

**1. Data Preparation**
```typescript
// Create test dataset with known answers
const testDataset = [
  {
    id: 'test-001',
    question: 'What is the return policy?',
    expectedSource: 'return_policy.pdf',
    expectedAnswer: 'Returns accepted within 30 days',
    category: 'policy'
  },
  {
    id: 'test-002',
    question: 'How many laptops are in stock?',
    expectedSource: 'inventory-index',
    expectedQuery: "category eq 'Laptop'",
    category: 'inventory'
  }
]
```

**2. Test Each Component**

```typescript
// Test 1: Document Upload & Chunking
describe('PDF Processing', () => {
  it('should extract text correctly', async () => {
    const pdfBuffer = await readFile('test-policy.pdf')
    const text = await extractTextFromPDF(pdfBuffer)
    expect(text).toContain('return policy')
    expect(text.length).toBeGreaterThan(100)
  })
  
  it('should chunk text appropriately', () => {
    const text = "Lorem ipsum...".repeat(1000)
    const chunks = chunkByTokens(text, 300, 50)
    
    expect(chunks.length).toBeGreaterThan(1)
    expect(chunks[0].length).toBeLessThanOrEqual(300 * 4) // ~4 chars per token
  })
})

// Test 2: Embedding Generation
describe('Embeddings', () => {
  it('should generate correct dimensions', async () => {
    const [embedding] = await generateEmbeddings('test text')
    expect(embedding.length).toBe(3072)
  })
  
  it('should handle batch embedding', async () => {
    const embeddings = await generateEmbeddings(['text1', 'text2', 'text3'])
    expect(embeddings.length).toBe(3)
  })
})

// Test 3: Vector Search
describe('Vector Search', () => {
  it('should return relevant documents', async () => {
    const results = await vectorSearch('return policy')
    
    expect(results.length).toBeGreaterThan(0)
    expect(results[0].content).toContain('return')
  })
  
  it('should rank by relevance', async () => {
    const results = await vectorSearch('laptop price')
    
    // First result should be more relevant than last
    const firstRelevance = results[0].score
    const lastRelevance = results[results.length - 1].score
    expect(firstRelevance).toBeGreaterThan(lastRelevance)
  })
})

// Test 4: Chat Completion
describe('Chat Completion', () => {
  it('should answer with correct context', async () => {
    const messages = [
      { role: 'system', content: 'You are a helpful assistant.' },
      { role: 'user', content: 'What is 2+2?' }
    ]
    
    const response = await generateChatCompletion(messages)
    expect(response).toContain('4')
  })
})

// Test 5: Full Pipeline
describe('End-to-End Chat', () => {
  it('should answer product question correctly', async () => {
    const response = await fetch('/api/chat', {
      method: 'POST',
      body: JSON.stringify({ message: 'price of Wireless Bluetooth Headphones' })
    })
    
    const data = await response.json()
    expect(response.status).toBe(200)
    expect(data.reply).toMatch(/\$79\.99/)
  })
  
  it('should answer policy question from PDF', async () => {
    const response = await fetch('/api/chat', {
      method: 'POST',
      body: JSON.stringify({ message: 'What is the return policy?' })
    })
    
    const data = await response.json()
    expect(data.reply).toContain('return')
    expect(data.reply).toContain('30 days')
  })
})
```

**3. Integration Testing**

```typescript
// Test Azure services integration
describe('Azure Integration', () => {
  it('should connect to Azure OpenAI', async () => {
    const response = await fetch(`${process.env.AZURE_OPENAI_ENDPOINT}/openai/deployments/gpt-4o/chat/completions?api-version=2024-02-15-preview`, {
      method: 'POST',
      headers: {
        'api-key': process.env.AZURE_OPENAI_API_KEY!,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        messages: [{ role: 'user', content: 'test' }]
      })
    })
    
    expect(response.status).toBe(200)
  })
  
  it('should query Azure AI Search', async () => {
    const client = getSearchClient('ecommerce-products-index')
    const results = await client.search('laptop')
    
    expect(results.results.length).toBeGreaterThan(0)
  })
})
```

**4. Load Testing**

```typescript
// Simulate concurrent users
import { check } from 'k6'
import http from 'k6/http'

export const options = {
  stages: [
    { duration: '30s', target: 10 },  // Ramp up to 10 users
    { duration: '1m', target: 50 },   // Ramp up to 50 users
    { duration: '30s', target: 0 },   // Ramp down
  ],
}

export default function () {
  const payload = JSON.stringify({
    message: 'What products do you have?'
  })
  
  const response = http.post('http://localhost:3000/api/chat', payload, {
    headers: { 'Content-Type': 'application/json' },
  })
  
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 3s': (r) => r.timings.duration < 3000,
  })
}
```

**5. Monitoring in Production**

```typescript
// Continuous testing in production
async function runSyntheticTests() {
  const tests = [
    { query: 'price of laptop', expectedPattern: /\$[\d,]+/ },
    { query: 'return policy', expectedKeywords: ['return', 'refund'] }
  ]
  
  for (const test of tests) {
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        body: JSON.stringify({ message: test.query })
      })
      
      const data = await response.json()
      
      // Log if response doesn't match expected
      if (!test.expectedPattern.test(data.reply)) {
        await logAlert({
          type: 'synthetic-test-failure',
          test: test.query,
          response: data.reply
        })
      }
    } catch (error) {
      await logAlert({ type: 'synthetic-test-error', error })
    }
  }
}

// Run every 5 minutes
setInterval(runSyntheticTests, 5 * 60 * 1000)
```

---

### Q26: How do you handle and test edge cases?
**Answer:**

**Common Edge Cases & Solutions:**

**1. Empty or Invalid Input**
```typescript
// Test empty message
it('should handle empty message', async () => {
  const response = await fetch('/api/chat', {
    method: 'POST',
    body: JSON.stringify({ message: '' })
  })
  
  expect(response.status).toBe(400)
  expect(await response.json()).toEqual({ error: 'Message is required' })
})

// Implementation
if (!message || message.trim().length === 0) {
  return NextResponse.json({ error: 'Message is required' }, { status: 400 })
}
```

**2. Very Long Messages**
```typescript
// Test message exceeding token limit
it('should handle very long messages', async () => {
  const longMessage = 'word '.repeat(10000) // ~40KB
  
  const response = await fetch('/api/chat', {
    method: 'POST',
    body: JSON.stringify({ message: longMessage })
  })
  
  // Should truncate or reject
  expect(response.status).toBe(400)
})

// Implementation
const MAX_MESSAGE_LENGTH = 1000
if (message.length > MAX_MESSAGE_LENGTH) {
  return NextResponse.json({ 
    error: `Message too long. Maximum ${MAX_MESSAGE_LENGTH} characters.` 
  }, { status: 400 })
}
```

**3. No Results Found**
```typescript
// Test query with no matching documents
it('should handle no results gracefully', async () => {
  const response = await fetch('/api/chat', {
    method: 'POST',
    body: JSON.stringify({ message: 'xyzabc123nonexistent' })
  })
  
  const data = await response.json()
  expect(data.reply).toContain('no information') // or similar
})

// Implementation
if (searchResults.length === 0) {
  contextInfo = "No relevant information found in the database."
  // GPT-4o will respond appropriately
}
```

**4. Multiple Matching Categories**
```typescript
// Query matches both products and orders
// Example: "laptop order status"
it('should handle multi-intent queries', async () => {
  const response = await fetch('/api/chat', {
    method: 'POST',
    body: JSON.stringify({ message: 'laptop order status' })
  })
  
  const data = await response.json()
  // Should address both aspects
  expect(data.reply).toMatch(/laptop/)
  expect(data.reply).toMatch(/order|status/)
})

// Implementation: Retrieve context from multiple sources
const isProductQuery = /product|price|laptop/i.test(message)
const isOrderQuery = /order|status|pending/i.test(message)

if (isProductQuery && isOrderQuery) {
  // Retrieve both
  const products = await searchProducts(message)
  const orders = await searchOrders(message)
  contextInfo = { products, orders }
}
```

**5. Special Characters & Injection**
```typescript
// Test SQL/NoSQL injection attempts
it('should sanitize malicious input', async () => {
  const maliciousInputs = [
    "'; DROP TABLE customers; --",
    "<script>alert('xss')</script>",
    "../../etc/passwd"
  ]
  
  for (const input of maliciousInputs) {
    const response = await fetch('/api/chat', {
      method: 'POST',
      body: JSON.stringify({ message: input })
    })
    
    // Should not execute, just treat as text
    expect(response.status).toBe(200)
  }
})

// Implementation
const sanitized = message
  .replace(/[<>]/g, '') // Remove HTML
  .replace(/['";]/g, '') // Remove quotes
  .trim()
```

**6. Concurrent Requests**
```typescript
// Test multiple requests from same user
it('should handle concurrent requests', async () => {
  const requests = Array(10).fill(null).map(() => 
    fetch('/api/chat', {
      method: 'POST',
      body: JSON.stringify({ message: 'test' })
    })
  )
  
  const responses = await Promise.all(requests)
  
  // All should succeed
  responses.forEach(r => expect(r.status).toBe(200))
})
```

**7. Service Outages**
```typescript
// Test Azure service unavailability
it('should handle Azure AI Search outage', async () => {
  // Mock search client to throw error
  jest.spyOn(searchClient, 'search').mockRejectedValue(new Error('Service unavailable'))
  
  const response = await fetch('/api/chat', {
    method: 'POST',
    body: JSON.stringify({ message: 'test query' })
  })
  
  const data = await response.json()
  // Should fall back gracefully
  expect(response.status).toBe(200)
  expect(data.reply).toContain('temporarily') // Or similar graceful message
})

// Implementation with retry
async function searchWithRetry(query: string, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await searchClient.search(query)
    } catch (error) {
      if (i === maxRetries - 1) {
        // Last attempt failed, return empty results
        return { results: [] }
      }
      await sleep(1000 * (i + 1)) // Exponential backoff
    }
  }
}
```

**8. Token Limits**
```typescript
// Test context exceeding token limit
it('should handle large context', async () => {
  // Retrieve 100 products (would exceed token limit)
  const products = await searchClient.search('*', { top: 100 })
  
  // Should truncate context to fit within limit
  const contextInfo = truncateContext(products, 4000) // Max 4K tokens for context
  
  expect(countTokens(contextInfo)).toBeLessThan(4000)
})

// Implementation
import { encode } from 'gpt-tokenizer'

function truncateContext(data: any[], maxTokens: number): string {
  let context = JSON.stringify(data, null, 2)
  let tokens = encode(context).length
  
  while (tokens > maxTokens && data.length > 0) {
    data.pop() // Remove last item
    context = JSON.stringify(data, null, 2)
    tokens = encode(context).length
  }
  
  return context
}
```

---

### Q27: How do you implement a regression testing suite?
**Answer:**

**Regression Testing Framework:**

**1. Golden Dataset**
```typescript
// Store known good question-answer pairs
const goldenDataset = [
  {
    id: 'reg-001',
    question: 'What is email of CUST-003?',
    expectedAnswer: 'sarah.miller@email.com',
    lastVerified: '2026-02-15',
    tags: ['customer', 'lookup']
  },
  {
    id: 'reg-002',
    question: 'Price of Wireless Bluetooth Headphones',
    expectedAnswer: '$79.99',
    lastVerified: '2026-02-15',
    tags: ['product', 'price']
  },
  {
    id: 'reg-003',
    question: 'What is the return policy?',
    expectedKeywords: ['return', '30 days', 'refund'],
    minimumSimilarity: 0.85,
    lastVerified: '2026-02-15',
    tags: ['policy', 'pdf']
  }
]
```

**2. Automated Regression Tests**
```typescript
describe('Regression Tests', () => {
  goldenDataset.forEach(testCase => {
    it(`should answer: ${testCase.question}`, async () => {
      const response = await fetch('/api/chat', {
        method: 'POST',
        body: JSON.stringify({ message: testCase.question })
      })
      
      const data = await response.json()
      
      if (testCase.expectedAnswer) {
        // Exact match
        expect(data.reply).toContain(testCase.expectedAnswer)
      } else if (testCase.expectedKeywords) {
        // All keywords present
        testCase.expectedKeywords.forEach(keyword => {
          expect(data.reply.toLowerCase()).toContain(keyword.toLowerCase())
        })
      }
    })
  })
})
```

**3. CI/CD Integration**
```yaml
# .github/workflows/regression-tests.yml
name: Regression Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Node.js
      uses: actions/setup-node@v2
      with:
        node-version: '18'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run regression tests
      env:
        AZURE_OPENAI_ENDPOINT: ${{ secrets.AZURE_OPENAI_ENDPOINT }}
        AZURE_OPENAI_API_KEY: ${{ secrets.AZURE_OPENAI_API_KEY }}
      run: npm run test:regression
    
    - name: Upload test results
      if: always()
      uses: actions/upload-artifact@v2
      with:
        name: test-results
        path: test-results/
```

**4. Performance Regression Detection**
```typescript
// Track response times over time
interface PerformanceBaseline {
  testId: string
  avgResponseTime: number
  maxResponseTime: number
  timestamp: string
}

const performanceBaselines: PerformanceBaseline[] = [
  { testId: 'customer-lookup', avgResponseTime: 800, maxResponseTime: 2000, timestamp: '2026-02-01' },
  { testId: 'product-search', avgResponseTime: 1200, maxResponseTime: 3000, timestamp: '2026-02-01' }
]

describe('Performance Regression', () => {
  it('should not exceed baseline response times', async () => {
    for (const baseline of performanceBaselines) {
      const testCase = goldenDataset.find(t => t.id === baseline.testId)
      
      const startTime = Date.now()
      await fetch('/api/chat', {
        method: 'POST',
        body: JSON.stringify({ message: testCase.question })
      })
      const responseTime = Date.now() - startTime
      
      expect(responseTime).toBeLessThan(baseline.maxResponseTime)
      
      // Alert if 20% slower than average
      if (responseTime > baseline.avgResponseTime * 1.2) {
        console.warn(`Performance degradation detected: ${testCase.id}`)
      }
    }
  })
})
```

**5. Version Comparison**
```typescript
// Compare responses between versions
async function compareVersions(question: string) {
  // Current version
  const currentResponse = await fetch('http://localhost:3000/api/chat', {
    method: 'POST',
    body: JSON.stringify({ message: question })
  })
  const currentData = await currentResponse.json()
  
  // Production version
  const prodResponse = await fetch('https://prod.example.com/api/chat', {
    method: 'POST',
    body: JSON.stringify({ message: question })
  })
  const prodData = await prodResponse.json()
  
  // Calculate similarity
  const similarity = await calculateSemanticSimilarity(
    currentData.reply,
    prodData.reply
  )
  
  if (similarity < 0.8) {
    console.warn(`Significant response change detected for: ${question}`)
    console.log('Production:', prodData.reply)
    console.log('Current:', currentData.reply)
  }
}
```

---

### Q28: What tools do you use for debugging chatbot issues?
**Answer:**

**Debugging Toolkit:**

**1. Built-in Debug Mode**
```typescript
// app/api/chat/route.ts
export async function POST(request: Request) {
  const { message, debug = false } = await request.json()
  
  const debugInfo: any = {
    timestamp: new Date().toISOString(),
    question: message,
    steps: []
  }
  
  // Track each step
  debugInfo.steps.push({ step: 'keyword-detection', result: detectedKeywords })
  
  // Context retrieval
  const startSearch = Date.now()
  const searchResults = await vectorSearch(message)
  const searchTime = Date.now() - startSearch
  
  debugInfo.steps.push({
    step: 'vector-search',
    duration: searchTime,
    resultsCount: searchResults.length,
    topResults: searchResults.slice(0, 3).map(r => ({
      title: r.title,
      score: r.score
    }))
  })
  
  // OpenAI call
  const startOpenAI = Date.now()
  const completion = await generateChatCompletion(messages)
  const openAITime = Date.now() - startOpenAI
  
  debugInfo.steps.push({
    step: 'openai-completion',
    duration: openAITime,
    tokensUsed: completion.usage
  })
  
  if (debug) {
    return NextResponse.json({
      reply: completion.content,
      debug: debugInfo
    })
  }
  
  return NextResponse.json({ reply: completion.content })
}
```

**2. Console Logging Strategy**
```typescript
// Structured logging
console.log(JSON.stringify({
  level: 'INFO',
  service: 'chatbot',
  event: 'chat-request',
  userId: session.userId,
  question: message,
  timestamp: new Date().toISOString()
}))

console.log(JSON.stringify({
  level: 'DEBUG',
  service: 'azure-search',
  event: 'search-results',
  query: message,
  resultsCount: results.length,
  duration: searchDuration,
  timestamp: new Date().toISOString()
}))

// Error logging with context
console.error(JSON.stringify({
  level: 'ERROR',
  service: 'chatbot',
  event: 'chat-error',
  error: error.message,
  stack: error.stack,
  context: { message, userId: session.userId },
  timestamp: new Date().toISOString()
}))
```

**3. Azure Application Insights**
```typescript
import { TelemetryClient } from 'applicationinsights'

const telemetry = new TelemetryClient(process.env.APPLICATIONINSIGHTS_CONNECTION_STRING)

// Track custom events
telemetry.trackEvent({
  name: 'ChatbotQuery',
  properties: {
    question: message,
    category: detectedCategory,
    searchMethod: 'vector-search'
  },
  measurements: {
    responseTime: duration,
    tokensUsed: completion.usage.total_tokens,
    contextLength: contextInfo.length
  }
})

// Track dependencies (Azure services)
telemetry.trackDependency({
  target: 'Azure AI Search',
  name: 'vector-search',
  data: message,
  duration: searchDuration,
  resultCode: 200,
  success: true
})
```

**4. Request Tracing**
```typescript
// Add correlation ID to track request flow
import { v4 as uuidv4 } from 'uuid'

export async function POST(request: Request) {
  const correlationId = request.headers.get('X-Correlation-ID') || uuidv4()
  
  console.log(`[${correlationId}] Chat request received`)
  
  try {
    console.log(`[${correlationId}] Starting vector search`)
    const results = await vectorSearch(message)
    console.log(`[${correlationId}] Vector search completed: ${results.length} results`)
    
    console.log(`[${correlationId}] Calling OpenAI`)
    const completion = await generateChatCompletion(messages)
    console.log(`[${correlationId}] OpenAI response received`)
    
    return NextResponse.json({ reply: completion.content })
  } catch (error) {
    console.error(`[${correlationId}] Error:`, error)
    throw error
  }
}
```

**5. PowerShell Debugging Scripts**
```powershell
# Test individual Azure services
$endpoint = "https://pramo-mloh6paf-eastus2.cognitiveservices.azure.com/"
$apiKey = $env:AZURE_OPENAI_API_KEY
$headers = @{"api-key" = $apiKey; "Content-Type" = "application/json"}

# Test GPT-4o
Write-Host "Testing GPT-4o..." -ForegroundColor Cyan
$response = Invoke-RestMethod `
  -Uri "$($endpoint)openai/deployments/gpt-4o/chat/completions?api-version=2024-02-15-preview" `
  -Method Post `
  -Headers $headers `
  -Body '{"messages":[{"role":"user","content":"test"}]}'

Write-Host "Response: $($response.choices[0].message.content)" -ForegroundColor Green

# Test embeddings
Write-Host "`nTesting text-embedding-3-large..." -ForegroundColor Cyan
$embResponse = Invoke-RestMethod `
  -Uri "$($endpoint)openai/deployments/text-embedding-3-large/embeddings?api-version=2024-02-15-preview" `
  -Method Post `
  -Headers $headers `
  -Body '{"input":"test query"}'

Write-Host "Embedding dimensions: $($embResponse.data[0].embedding.Count)" -ForegroundColor Green
```

**6. Browser DevTools Network Tab**
```typescript
// Add request/response interceptor in frontend
useEffect(() => {
  const originalFetch = window.fetch
  
  window.fetch = async (...args) => {
    console.log('[Fetch]', args[0])
    const response = await originalFetch(...args)
    console.log('[Response]', response.status, await response.clone().json())
    return response
  }
  
  return () => { window.fetch = originalFetch }
}, [])
```

**7. Database Query Inspection**
```typescript
// Log actual Azure AI Search queries
const client = getSearchClient('ecommerce-products-index')

// Log query
console.log('Azure AI Search Query:', {
  searchText: message,
  filter: filter,
  select: ['product_id', 'name', 'price'],
  top: 10
})

const results = await client.search(message, {
  filter,
  select: ['product_id', 'name', 'price'],
  top: 10
})

// Log results
console.log('Search Results:', {
  count: results.results.length,
  results: results.results.map(r => r.document)
})
```

---

## Summary

This document covers the key technical aspects of the Hybrid RAG E-commerce Chatbot project:

✅ **Architecture & Design Decisions** (Q1-Q5)
✅ **Azure Services Integration** (Q3-Q5)
✅ **RAG Implementation** - Vector, Keyword, Filter-based (Q6-Q10)
✅ **Code Structure & Best Practices** (Q11-Q12)
✅ **Performance Optimization** (Q13-Q14)
✅ **Security Considerations** (Q15)
✅ **Troubleshooting Scenarios** (Q16-Q17)
✅ **Advanced Topics** - Multi-tenancy, A/B Testing, Monitoring (Q18-Q20)
✅ **Cost Management** (Q21)
✅ **Future Enhancements** (Q22)
✅ **Testing & Accuracy Verification** (Q23-Q28) ⭐ NEW

### Testing & Quality Assurance Coverage:
- **Q23:** How to verify chatbot response accuracy
  - Manual testing checklist, automated testing framework, context verification
  - Ground truth comparison, hallucination detection
  
- **Q24:** Quality metrics and measurement
  - Accuracy metrics (exact match, semantic similarity, F1 score)
  - Response quality metrics (user satisfaction, resolution rate, latency)
  - Retrieval metrics (context relevance, search quality)
  - Business metrics (engagement, conversion, cost per query)
  
- **Q25:** End-to-end RAG pipeline testing
  - Component testing (PDF processing, embeddings, vector search)
  - Integration testing with Azure services
  - Load testing with k6
  - Synthetic monitoring in production
  
- **Q26:** Edge case handling and testing
  - Empty/invalid input, very long messages, no results
  - Multi-intent queries, special characters, concurrent requests
  - Service outages, token limits
  
- **Q27:** Regression testing suite
  - Golden dataset creation, automated regression tests
  - CI/CD integration with GitHub Actions
  - Performance regression detection
  - Version comparison between environments
  
- **Q28:** Debugging tools and techniques
  - Built-in debug mode, structured logging
  - Azure Application Insights integration
  - Request tracing with correlation IDs
  - PowerShell debugging scripts, browser DevTools

**Key Takeaways:**
1. **Hybrid RAG** combines multiple retrieval strategies for better accuracy
2. **Azure AI Search** provides unified platform for vector + keyword + filter queries
3. **Proper error handling** and fallbacks ensure reliability
4. **Testing at multiple levels** - unit, integration, end-to-end, regression
5. **Monitoring and logging** are crucial for production systems
6. **Quality metrics** track accuracy, performance, and business impact
7. **Cost optimization** through caching, smart routing, and token management
8. **Debugging tools** enable quick issue identification and resolution

**Interview Tips:**
- **Be specific** about Azure service configurations (show you know deployment types, TPM limits, index schemas)
- **Explain trade-offs** in design decisions (vector vs keyword, accuracy vs speed, cost vs performance)
- **Show understanding** of both theory (RAG, embeddings, HNSW) and practice (Azure APIs, error handling)
- **Demonstrate problem-solving** with real troubleshooting examples (deployment propagation, fallback strategies)
- **Quantify impact** (response times <2s, accuracy 90%+, cost $350/month, token optimization saves 30%)
- **Discuss testing** strategies to verify accuracy (golden datasets, regression tests, A/B testing)
- **Mention observability** (Application Insights, structured logging, correlation IDs)
- **Talk about quality** metrics (F1 score, semantic similarity, user satisfaction)

**Common Interview Questions This Covers:**
- "How do you ensure your chatbot gives accurate answers?" → Q23-Q24
- "Walk me through your testing strategy" → Q25-Q27
- "How do you debug production issues?" → Q28
- "What happens when Azure services go down?" → Q26 (service outages)
- "How do you measure chatbot quality?" → Q24
- "How do you prevent hallucinations?" → Q23
- "What's your CI/CD pipeline?" → Q27
- "How do you handle edge cases?" → Q26

---

**Project Repository:** D:\GenAI_Project_2025\HybridRAGAzure
**Tech Stack:** Next.js 16, TypeScript, Azure OpenAI, Azure AI Search, React 18
**Deployment:** Azure App Service (Production-ready)
