# E-Commerce Application Architecture - Azure Edition

## System Overview

This document describes the architecture of the Azure-based e-commerce application featuring AI-powered return management, intelligent search, and automated policy verification.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Next.js 14 Frontend                         │
│                     (localhost:3000)                            │
│  ┌──────────┬──────────┬──────────┬──────────┬─────────────┐  │
│  │Dashboard │ Products │  Orders  │ Returns  │ AI Chat     │  │
│  │  Stats   │ Catalog  │  Track   │ Portal   │ Widget      │  │
│  └──────────┴──────────┴──────────┴──────────┴─────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTPS
                            ├──────────────┬──────────────┐
                            ▼              ▼              ▼
                    ┌──────────────┬──────────────┬──────────────┐
                    │  API Routes  │              │              │
                    │ /api/chat    │  /api/orders │ /api/returns │
                    │ /api/products│ /api/stats   │              │
                    └──────┬───────┴──────┬───────┴──────┬───────┘
                           │              │              │
         ┌─────────────────┼──────────────┼──────────────┼─────┐
         │                 │              │              │     │
         ▼                 ▼              ▼              ▼     │
┌─────────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────▼─────┐
│ Azure OpenAI    │ │Azure AI Search│ │Azure Storage │ │Azure Tables│
│                 │ │               │ │              │ │            │
│ • GPT-4         │ │• Vector Search│ │• File Share  │ │• Products  │
│ • text-embed-   │ │• Keyword      │ │  (PDFs)      │ │• Orders    │
│   3-large       │ │  Search       │ │• Blob Storage│ │• Customers │
│ • Completions   │ │• Hybrid       │ │              │ │• Returns   │
│ • Streaming     │ │  Queries      │ │              │ │• Inventory │
└─────────────────┘ └──────────────┘ └──────────────┘ └────────────┘
```

## Technology Stack

### Frontend Layer
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Radix UI (shadcn/ui)
- **Icons**: Lucide React
- **State Management**: React Hooks

### API Layer
- **Runtime**: Next.js API Routes (Edge Functions)
- **Authentication**: NextAuth.js (optional)
- **Validation**: Zod schemas
- **Date Handling**: date-fns

### Azure Services Layer

#### 1. Azure OpenAI Service
- **Model**: GPT-4 (Turbo 2024-04-09)
- **Embedding Model**: text-embedding-3-large
- **Purpose**: 
  - Chat completions for customer support
  - Text embeddings for vector search
  - Policy interpretation and RAG
- **API Version**: 2024-02-15-preview
- **SDK**: `openai` npm package with Azure endpoint

#### 2. Azure AI Search
- **Tier**: Basic (or Standard S1 for production)
- **Index**: `ecommerce-products`
- **Features**:
  - Vector search (3072 dimensions for text-embedding-3-large)
  - Keyword search
  - Hybrid queries
  - Semantic ranking
- **SDK**: `@azure/search-documents`

#### 3. Azure Storage Account

**File Share**:
- Share Name: `ecommerce-policies`
- Structure:
  ```
  ecommerce-policies/
  └── policies/
      ├── return_policy.pdf
      ├── shipping_policy.pdf
      ├── warranty_policy.pdf
      └── product_catalog.pdf
  ```
- **SDK**: `@azure/storage-file-share`

**Table Storage**:
- Tables:
  - `products` - Product catalog
  - `orders` - Customer orders
  - `customers` - Customer profiles
  - `returns` - Return requests
  - `inventory` - Inventory tracking
- **SDK**: `@azure/data-tables`

## Data Models

### Table Storage Schema

#### Products Table
```typescript
{
  partitionKey: "PRODUCT",
  rowKey: "PROD-001",
  product_id: "PROD-001",
  name: "Wireless Bluetooth Headphones",
  category: "Electronics",
  price: 79.99,
  description: "Premium noise-canceling...",
  stock_quantity: 150,
  return_eligible: true,
  return_window_days: 30,
  warranty_months: 12
}
```

#### Orders Table
```typescript
{
  partitionKey: "ORDER",
  rowKey: "ORD-2024-001",
  order_id: "ORD-2024-001",
  customer_id: "CUST-123",
  order_date: "2024-01-15T14:30:00Z",
  status: "delivered",
  total_amount: 159.98,
  items: "[{product_id, quantity, price}]",
  shipping_address: "{street, city, state, zip}"
}
```

#### Customers Table
```typescript
{
  partitionKey: "CUSTOMER",
  rowKey: "CUST-123",
  customer_id: "CUST-123",
  email: "john.doe@example.com",
  name: "John Doe",
  total_orders: 15,
  total_returns: 2
}
```

#### Returns Table
```typescript
{
  partitionKey: "RETURN",
  rowKey: "RET-2024-0001",
  return_id: "RET-2024-0001",
  order_id: "ORD-2024-001",
  customer_id: "CUST-123",
  status: "pending",
  reason: "defective",
  refund_amount: 79.99,
  restocking_fee: 0
}
```

### Azure AI Search Index Schema

```json
{
  "name": "ecommerce-products",
  "fields": [
    {"name": "id", "type": "Edm.String", "key": true},
    {"name": "product_id", "type": "Edm.String", "searchable": true},
    {"name": "name", "type": "Edm.String", "searchable": true},
    {"name": "category", "type": "Edm.String", "filterable": true},
    {"name": "description", "type": "Edm.String", "searchable": true},
    {"name": "content", "type": "Edm.String", "searchable": true},
    {"name": "contentVector", "type": "Collection(Edm.Single)", 
     "searchable": true, "dimensions": 3072}
  ]
}
```

## Key Features Implementation

### 1. AI-Powered Chat Widget

**File**: `components/AIChatWidget.tsx`

**Flow**:
```
User Message
    ↓
POST /api/chat
    ↓
Extract intent (order query, policy question, etc.)
    ↓
[If policy query] → Vector search in Azure AI Search
    ↓
Build context from search results + order data
    ↓
Azure OpenAI GPT-4 completion
    ↓
Stream response to user
```

**Technologies**:
- Azure OpenAI GPT-4 for completions
- Azure AI Search for RAG context
- Streaming responses for real-time experience

### 2. Intelligent Return Management

**File**: `app/api/returns/route.ts`

**Flow**:
```
Return Request (order_id, reason)
    ↓
Fetch order from Azure Tables
    ↓
Vector search for relevant return policies
    ↓
Build eligibility prompt with:
  - Order details
  - Delivery date
  - Return policy context
    ↓
Azure OpenAI GPT-4 eligibility analysis
    ↓
Parse JSON response:
  - eligible: boolean
  - refundAmount: number
  - restockingFee: number
  - reason: string
    ↓
[If eligible] → Create return record in Azure Tables
    ↓
Return RMA number and details
```

**Key Logic**:
- 4-point eligibility check:
  1. Order delivered?
  2. Within return window?
  3. Product return-eligible?
  4. No existing return?
- AI-powered policy interpretation
- Automatic refund calculation

### 3. Vector Search for Products

**File**: `lib/azure/search.ts`

**Flow**:
```
User Search Query
    ↓
Generate embedding (text-embedding-3-large)
    ↓
Azure AI Search vector query
    ↓
Hybrid search (vector + keyword)
    ↓
Return top K results
```

**Features**:
- Semantic search with embeddings
- Hybrid ranking (vector + BM25)
- Category filtering
- Result ordering

### 4. Dashboard Statistics

**File**: `app/api/dashboard/stats/route.ts`

**Queries**:
```typescript
// Pending orders
filter: "status eq 'pending' or status eq 'processing'"

// Low stock products
filter: "stock_quantity lt 20"

// New customers (last 30 days)
filter: "created_at ge datetime'2026-01-15'"

// Recent returns (last 7 days)
filter: "created_at ge datetime'2026-02-08'"
```

## API Endpoints

### Chat API
```typescript
POST /api/chat
Body: { message: string }
Response: { response: string, timestamp: string }
```

### Products API
```typescript
GET /api/products?q=query&category=Electronics&limit=20
Response: { products: Product[], count: number }
```

### Orders API
```typescript
GET /api/orders?customer_id=CUST-123
Response: { orders: Order[], count: number }

POST /api/orders
Body: { customer_id, items, total_amount, shipping_address }
Response: { order: Order, message: string }
```

### Returns API
```typescript
GET /api/returns?order_id=ORD-2024-001
Response: { returns: Return[], count: number }

POST /api/returns
Body: { order_id, reason, items }
Response: { 
  eligible: boolean, 
  return?: Return, 
  rma_number?: string,
  message: string 
}
```

### Dashboard Stats API
```typescript
GET /api/dashboard/stats
Response: {
  pendingOrders: number,
  lowStockProducts: number,
  newCustomers: number,
  recentReviews: number
}
```

## Security Considerations

### 1. Authentication
- NextAuth.js for user sessions
- Azure AD integration (optional)
- JWT tokens for API authentication

### 2. Azure Service Security
- API keys stored in environment variables
- Managed Identity for production
- Private endpoints for enhanced security
- Network security groups

### 3. Data Protection
- HTTPS only
- Input validation with Zod
- SQL injection prevention (parameterized queries)
- XSS protection (React escaping)

### 4. Rate Limiting
- API rate limiting per user
- Azure API Management (optional)
- Request throttling

## Performance Optimization

### 1. Caching Strategy
- Next.js automatic static optimization
- API route caching
- Azure CDN for static assets

### 2. Database Optimization
- Efficient partition key design
- Indexed queries in Table Storage
- Vector search caching

### 3. API Optimization
- Parallel requests where possible
- Streaming responses for chat
- Lazy loading components

## Deployment Architecture

### Development
```
Local Machine (localhost:3000)
    ↓
Azure Services (eastus region)
```

### Production (Azure App Service)
```
Azure App Service (Node 18)
    ├── Application Insights (monitoring)
    ├── Azure CDN (static assets)
    └── Azure Services (same region)
```

### Production (Vercel)
```
Vercel Edge Functions
    ↓
Azure Services (eastus region)
```

## Cost Optimization

### Development
- Use Azure Free Tier where available
- Basic tier for AI Search
- Minimal OpenAI usage (caching)

### Production
- Monitor usage with Azure Cost Management
- Set budget alerts
- Use Reserved Instances for predictable workloads
- Optimize OpenAI token usage

## Monitoring & Logging

### Application Insights
- Request telemetry
- Dependency tracking
- Custom events

### Azure Monitor
- Resource health
- Performance metrics
- Alerts and notifications

### Logging Strategy
```typescript
console.log()     // Development
Application Insights // Production
```

## Future Enhancements

1. **Advanced RAG**: Fine-tuned embeddings for better policy matching
2. **Multi-language**: i18n support with Azure Translator
3. **Real-time Updates**: Azure SignalR for live order tracking
4. **Analytics**: Azure Synapse for data warehousing
5. **Mobile App**: React Native with same backend
6. **Recommendations**: ML-based product recommendations

---

**Architecture Version**: 1.0  
**Last Updated**: February 15, 2026  
**Maintained by**: Development Team
