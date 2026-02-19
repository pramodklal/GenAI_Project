# Technical Architecture - Hybrid RAG E-Commerce Chatbot

## High-Level Architecture Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        A[Web Browser] --> B[Next.js Frontend<br/>React 18 + TypeScript]
        B --> C[AI Chat Widget<br/>Component]
    end
    
    subgraph "Application Layer - Next.js 16"
        C --> D[API Route<br/>/api/chat]
        B --> E[Admin Panel UI]
        E --> F[/api/admin/upload-pdf]
        E --> G[/api/admin/upload-csv]
        B --> H[Dashboard API<br/>/api/dashboard/stats]
    end
    
    subgraph "Business Logic Layer"
        D --> I[Query Analyzer]
        I --> J[Keyword Detector]
        J --> K{Query Type?}
        K -->|Policy/FAQ| L[Vector Search Handler]
        K -->|Customer| M[Customer Handler]
        K -->|Product| N[Product Handler]
        K -->|Order| O[Order Handler]
        K -->|Return| P[Return Handler]
    end
    
    subgraph "Azure OpenAI Service - East US 2"
        Q[GPT-4o Deployment<br/>Global Standard<br/>50K TPM]
        R[text-embedding-3-large<br/>Global Standard<br/>150K TPM<br/>3072 dimensions]
    end
    
    subgraph "Azure AI Search Service"
        S[ecommerce-documents-index<br/>Vector + Keyword]
        T[ecommerce-customers-index<br/>Structured Data]
        U[ecommerce-products-index<br/>Full-Text Search]
        V[ecommerce-orders-index<br/>Filterable]
        W[ecommerce-inventory-index<br/>Filterable]
        X[ecommerce-returns-index<br/>Filterable]
    end
    
    subgraph "Azure Storage Account"
        Y[File Share<br/>ecommerce-pdfs<br/>PDF Storage]
    end
    
    subgraph "Data Processing Pipeline"
        F --> Z[PDF Text Extractor<br/>pdf2json]
        Z --> AA[Text Chunker<br/>tiktoken<br/>300 tokens/chunk]
        AA --> AB[Generate Embeddings]
        AB --> R
        R --> AC[Vector Data]
        AC --> S
        Z --> Y
        
        G --> AD[CSV Parser]
        AD --> AE[Data Transformer]
        AE --> AF{Index Type}
        AF -->|Customers| T
        AF -->|Products| U
        AF -->|Orders| V
        AF -->|Inventory| W
        AF -->|Returns| X
    end
    
    subgraph "RAG Context Retrieval"
        L --> AG[Generate Query Embedding]
        AG --> R
        R --> AH[Query Vector]
        AH --> S
        S --> AI[Vector Search<br/>HNSW Algorithm<br/>Cosine Similarity]
        
        M --> AJ[OData Filter Builder]
        AJ --> T
        T --> AK[Filter Search<br/>customer_id eq 'X']
        
        N --> AL[Full-Text Search]
        AL --> U
        U --> AM[Keyword Matching]
        
        O --> AN[Filter + Sort]
        AN --> V
        
        P --> AO[Filter + Sort]
        AO --> X
    end
    
    subgraph "Response Generation"
        AI --> AP[Context Aggregator]
        AK --> AP
        AM --> AP
        AP --> AQ[Build System Prompt]
        AQ --> AR[Generate Chat Completion]
        AR --> Q
        Q --> AS[AI Response]
        AS --> D
        D --> C
    end
    
    subgraph "Monitoring & Observability"
        AT[Azure Application Insights]
        D --> AT
        F --> AT
        G --> AT
        AT --> AU[Metrics Dashboard<br/>- Response Time<br/>- Token Usage<br/>- Error Rate<br/>- User Satisfaction]
    end
    
    style A fill:#e1f5ff
    style B fill:#bbdefb
    style C fill:#90caf9
    style D fill:#ffd54f
    style Q fill:#81c784
    style R fill:#81c784
    style S fill:#ba68c8
    style T fill:#ba68c8
    style U fill:#ba68c8
    style V fill:#ba68c8
    style W fill:#ba68c8
    style X fill:#ba68c8
    style Y fill:#ff8a65
    style AT fill:#ffb74d
```

## Detailed Component Architecture

```mermaid
graph LR
    subgraph "Frontend Components"
        A1[page.tsx<br/>Homepage] --> A2[AIChatWidget.tsx]
        A2 --> A3[UI Components<br/>Button, Card, Badge, Tabs]
        A1 --> A4[Dashboard Component]
    end
    
    subgraph "API Routes"
        B1[/api/chat/route.ts<br/>Main Chat Handler]
        B2[/api/admin/upload-pdf/route.ts]
        B3[/api/admin/upload-csv/route.ts]
        B4[/api/dashboard/stats/route.ts]
        B5[/api/products/route.ts]
        B6[/api/orders/route.ts]
        B7[/api/returns/route.ts]
    end
    
    subgraph "Azure Client Libraries"
        C1[lib/azure/openai.ts<br/>OpenAI Client Wrapper]
        C2[lib/azure/search.ts<br/>Search Client Manager]
        C3[lib/azure/storage.ts<br/>File Share Client]
        C4[lib/azure/tables.ts<br/>Legacy Table Storage]
    end
    
    subgraph "Utility Functions"
        D1[lib/utils/pdf-extraction.ts]
        D2[lib/utils/chunking.ts]
        D3[lib/utils.ts<br/>General Utilities]
    end
    
    A2 --> B1
    A4 --> B4
    A4 --> B5
    A4 --> B6
    A4 --> B7
    A1 --> B2
    A1 --> B3
    
    B1 --> C1
    B1 --> C2
    B2 --> D1
    B2 --> D2
    B2 --> C1
    B2 --> C2
    B2 --> C3
    B3 --> C2
    B4 --> C2
    B5 --> C2
    B6 --> C2
    B7 --> C2
    
    style A2 fill:#64b5f6
    style B1 fill:#ffd54f
    style C1 fill:#81c784
    style C2 fill:#ba68c8
    style C3 fill:#ff8a65
```

## Data Flow Diagram - Chat Request

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend<br/>(AIChatWidget)
    participant A as API Route<br/>/api/chat
    participant K as Keyword<br/>Detector
    participant S as Azure AI<br/>Search
    participant E as Azure OpenAI<br/>Embeddings
    participant G as Azure OpenAI<br/>GPT-4o
    participant L as Logs
    
    U->>F: Types question
    F->>A: POST /api/chat<br/>{ message: "query" }
    
    A->>L: Log request
    A->>K: Analyze query
    K->>A: Return keywords<br/>& category
    
    alt Policy/FAQ Query
        A->>E: Generate embedding<br/>text-embedding-3-large
        E->>A: Return vector [3072]
        A->>S: Vector search on<br/>documents-index
        S->>A: Return relevant docs<br/>(cosine similarity)
    else Customer Query
        A->>S: OData filter search<br/>on customers-index
        S->>A: Return matched customers
    else Product Query
        A->>S: Full-text search<br/>on products-index
        S->>A: Return products
    else Order/Return Query
        A->>S: Filter + sort search<br/>on orders/returns-index
        S->>A: Return records
    end
    
    A->>A: Build context<br/>(aggregate results)
    A->>A: Create system prompt<br/>+ context
    A->>G: Generate completion<br/>gpt-4o
    G->>A: Return AI response
    
    A->>L: Log tokens, time, method
    A->>F: Return { reply: "..." }
    F->>U: Display response
```

## Data Processing Pipeline - PDF Upload

```mermaid
flowchart TD
    A[Admin uploads PDF] --> B[Receive file in<br/>/api/admin/upload-pdf]
    B --> C{Valid PDF?}
    C -->|No| D[Return error 400]
    C -->|Yes| E[Extract text using<br/>pdf2json]
    
    E --> F[Parse PDF content]
    F --> G[Extract metadata<br/>title, pages, etc.]
    
    G --> H[Chunk text using<br/>tiktoken]
    H --> I[Create chunks<br/>300 tokens each<br/>50 token overlap]
    
    I --> J[Generate embeddings<br/>for each chunk]
    J --> K[Azure OpenAI<br/>text-embedding-3-large]
    K --> L[Receive vectors<br/>3072 dimensions]
    
    L --> M[Prepare documents<br/>with vectors]
    M --> N[Upload to Azure AI Search<br/>ecommerce-documents-index]
    
    G --> O[Upload original PDF<br/>to File Share]
    O --> P[Azure Storage<br/>ecommerce-pdfs]
    
    N --> Q[Index successfully]
    P --> Q
    Q --> R[Return success 200]
    
    style A fill:#e1f5ff
    style E fill:#fff59d
    style H fill:#fff59d
    style J fill:#a5d6a7
    style K fill:#81c784
    style N fill:#ba68c8
    style P fill:#ff8a65
    style R fill:#a5d6a7
```

## Infrastructure Architecture

```mermaid
graph TB
    subgraph "Azure Resource Group: ecommerce-chatbot-rg"
        subgraph "Compute"
            A[Azure App Service<br/>Next.js Deployment<br/>Node.js 18 Runtime]
        end
        
        subgraph "AI Services"
            B[Azure OpenAI Service<br/>pramo-mloh6paf-eastus2<br/>East US 2 Region]
            B1[GPT-4o Deployment<br/>Model: gpt-4o<br/>Version: 2024-11-20<br/>Type: Global Standard<br/>Capacity: 50K TPM]
            B2[Embedding Deployment<br/>Model: text-embedding-3-large<br/>Type: Global Standard<br/>Capacity: 150K TPM<br/>Dimensions: 3072]
            B --> B1
            B --> B2
        end
        
        subgraph "Search Service"
            C[Azure AI Search<br/>search-ecommerce-chatbot<br/>Standard S1 Tier]
            C1[6 Search Indexes<br/>Vector + Keyword + Filter]
            C --> C1
        end
        
        subgraph "Storage"
            D[Storage Account<br/>stecomchatbot]
            D1[File Share<br/>ecommerce-pdfs<br/>PDF Documents]
            D2[Table Storage<br/>Legacy Data]
            D --> D1
            D --> D2
        end
        
        subgraph "Monitoring"
            E[Application Insights<br/>Telemetry & Logging]
        end
        
        subgraph "Configuration"
            F[Key Vault<br/>Secrets Management<br/>API Keys]
        end
    end
    
    A --> B
    A --> C
    A --> D
    A --> E
    A --> F
    
    style A fill:#64b5f6
    style B fill:#81c784
    style B1 fill:#a5d6a7
    style B2 fill:#a5d6a7
    style C fill:#ba68c8
    style C1 fill:#ce93d8
    style D fill:#ff8a65
    style E fill:#ffb74d
    style F fill:#90a4ae
```

## Vector Search Architecture (HNSW)

```mermaid
graph TB
    subgraph "Vector Search Process"
        A[User Query:<br/>"What is return policy?"]
        A --> B[Generate Query Embedding<br/>Azure OpenAI API]
        B --> C[Query Vector<br/>[0.023, -0.145, 0.089, ...<br/>3072 dimensions]]
        
        C --> D[Azure AI Search<br/>HNSW Algorithm]
        
        subgraph "Document Embeddings"
            E1[Doc1 Vector<br/>return_policy.pdf chunk 1]
            E2[Doc2 Vector<br/>return_policy.pdf chunk 2]
            E3[Doc3 Vector<br/>shipping_policy.pdf chunk 1]
            E4[Doc4 Vector<br/>faq.pdf chunk 1]
            E5[Doc5 Vector<br/>terms.pdf chunk 1]
        end
        
        D --> F[Calculate Cosine Similarity<br/>Query vs All Docs]
        E1 --> F
        E2 --> F
        E3 --> F
        E4 --> F
        E5 --> F
        
        F --> G[Rank by Similarity Score]
        G --> H{Top K Results<br/>K=3}
        H --> I1[Doc1: Score 0.94]
        H --> I2[Doc2: Score 0.89]
        H --> I3[Doc4: Score 0.76]
        
        I1 --> J[Aggregate Context]
        I2 --> J
        I3 --> J
        J --> K[Send to GPT-4o]
    end
    
    style A fill:#e1f5ff
    style B fill:#81c784
    style C fill:#fff59d
    style D fill:#ba68c8
    style F fill:#ba68c8
    style K fill:#81c784
```

## Security Architecture

```mermaid
graph TB
    subgraph "Security Layers"
        A[HTTPS/TLS 1.3<br/>All Traffic Encrypted]
        
        subgraph "Authentication & Authorization"
            B[NextAuth.js<br/>User Authentication]
            C[Role-Based Access Control<br/>Admin vs User]
            D[Session Management]
        end
        
        subgraph "API Security"
            E[Rate Limiting<br/>20 req/min per IP]
            F[Input Validation<br/>& Sanitization]
            G[CORS Policy<br/>Allowed Origins]
        end
        
        subgraph "Azure Security"
            H[Azure Key Vault<br/>Secret Storage]
            I[Managed Identity<br/>Service-to-Service Auth]
            J[Azure AD Integration]
            K[Private Endpoints<br/>VNet Integration]
        end
        
        subgraph "Data Security"
            L[Encryption at Rest<br/>Azure Storage]
            M[Encryption in Transit<br/>TLS/SSL]
            N[Data Isolation<br/>Multi-tenant Support]
        end
        
        subgraph "Content Security"
            O[Azure Content Safety<br/>Input/Output Filtering]
            P[Prompt Injection Detection]
            Q[PII Redaction]
        end
    end
    
    A --> B
    A --> E
    B --> C
    C --> D
    E --> F
    F --> G
    G --> H
    H --> I
    I --> J
    J --> K
    K --> L
    L --> M
    M --> N
    N --> O
    O --> P
    P --> Q
    
    style A fill:#66bb6a
    style H fill:#ffb74d
    style O fill:#ef5350
```

## Hybrid RAG Strategy

```mermaid
graph TB
    A[User Query] --> B{Query Classification}
    
    B -->|Semantic<br/>Policy/FAQ| C[Vector Search Strategy]
    B -->|Exact Match<br/>Customer/ID| D[Filter Search Strategy]
    B -->|Keywords<br/>Product/Description| E[Full-Text Search Strategy]
    
    subgraph "Vector Search"
        C --> C1[Generate Embedding<br/>text-embedding-3-large]
        C1 --> C2[HNSW Vector Search<br/>Cosine Similarity]
        C2 --> C3[Semantic Results<br/>High Relevance]
    end
    
    subgraph "Filter Search"
        D --> D1[Build OData Filter<br/>customer_id eq 'X']
        D1 --> D2[Exact Match Query<br/>Azure AI Search]
        D2 --> D3[Structured Results<br/>100% Accurate]
    end
    
    subgraph "Full-Text Search"
        E --> E1[Tokenize Query<br/>Keyword Extraction]
        E1 --> E2[Full-Text Search<br/>Azure AI Search]
        E2 --> E3[Ranked Results<br/>TF-IDF Scoring]
    end
    
    C3 --> F[Context Aggregation]
    D3 --> F
    E3 --> F
    
    F --> G[Unified Context]
    G --> H[System Prompt<br/>+ Context + Query]
    H --> I[GPT-4o Generation]
    I --> J[Natural Language<br/>Response]
    
    style C fill:#ba68c8
    style D fill:#64b5f6
    style E fill:#ffd54f
    style I fill:#81c784
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Development Environment"
        A[Local Dev Server<br/>npm run dev<br/>localhost:3000]
        A --> B[.env.local<br/>Configuration]
    end
    
    subgraph "CI/CD Pipeline"
        C[GitHub Repository] --> D[GitHub Actions]
        D --> E[Run Tests<br/>Jest + Playwright]
        E --> F{Tests Pass?}
        F -->|No| G[Notify Developer]
        F -->|Yes| H[Build Next.js App<br/>npm run build]
        H --> I[Docker Image<br/>Production Build]
    end
    
    subgraph "Azure Deployment"
        I --> J[Azure Container Registry]
        J --> K[Azure App Service<br/>Linux Container]
        K --> L[Auto-Scale Rules<br/>2-10 Instances]
        K --> M[Health Checks<br/>/api/health]
    end
    
    subgraph "Azure Services"
        N[Azure OpenAI<br/>pramo-mloh6paf-eastus2]
        O[Azure AI Search<br/>search-ecommerce-chatbot]
        P[Azure Storage<br/>stecomchatbot]
        Q[Application Insights<br/>Monitoring]
    end
    
    K --> N
    K --> O
    K --> P
    K --> Q
    
    subgraph "Users"
        R[End Users] --> S[Azure Front Door<br/>CDN + WAF]
        S --> K
    end
    
    style A fill:#e1f5ff
    style I fill:#64b5f6
    style K fill:#64b5f6
    style N fill:#81c784
    style O fill:#ba68c8
    style P fill:#ff8a65
```

## Cost Optimization Architecture

```mermaid
graph TB
    A[User Request] --> B{Check Cache}
    B -->|Cache Hit| C[Return Cached Response<br/>$0 Cost]
    B -->|Cache Miss| D[Process Request]
    
    D --> E{Query Complexity}
    E -->|Simple| F[GPT-3.5-Turbo<br/>$0.0015/1K tokens<br/>10x Cheaper]
    E -->|Complex| G[GPT-4o<br/>$0.0025-0.01/1K tokens]
    
    F --> H[Generate Response]
    G --> H
    
    H --> I{Token Count}
    I -->|<500 tokens| J[Use max_tokens=500<br/>Lower Cost]
    I -->|>500 tokens| K[Truncate Context<br/>Optimize Tokens]
    
    J --> L[Cache Response<br/>Redis/Memory]
    K --> L
    
    L --> M[Monitor Usage]
    M --> N{Daily Limit?}
    N -->|<80%| O[Continue Normal]
    N -->|>80%| P[Rate Limiting<br/>Alert Admin]
    
    style C fill:#66bb6a
    style F fill:#66bb6a
    style L fill:#ffb74d
    style P fill:#ef5350
```

---

## Architecture Highlights

### Key Design Decisions

1. **Hybrid RAG Approach**
   - Vector Search (semantic) for unstructured data (PDFs)
   - Filter Search (exact match) for structured data (customers, orders)
   - Full-Text Search (keyword) for product catalogs
   - **Benefit**: Optimal accuracy for different query types

2. **Azure AI Search as Unified Platform**
   - Single service for all search types
   - 6 specialized indexes for different data types
   - Built-in vector search with HNSW algorithm
   - **Benefit**: Simplified architecture, reduced latency

3. **Global Standard Deployments**
   - GPT-4o: 50K TPM capacity
   - text-embedding-3-large: 150K TPM capacity
   - **Benefit**: High availability, global distribution

4. **Chunking Strategy**
   - 300 tokens per chunk with 50 token overlap
   - Preserves context across boundaries
   - **Benefit**: Better retrieval accuracy

5. **Fallback Mechanisms**
   - Vector search → Keyword search fallback
   - Multiple retry attempts with exponential backoff
   - **Benefit**: High reliability

### Performance Characteristics

| Component | Latency Target | Current Performance |
|-----------|---------------|---------------------|
| Azure AI Search | <100ms | 50-80ms |
| Vector Search | <200ms | 150-250ms |
| GPT-4o Completion | <2s | 0.8-1.5s |
| End-to-End Response | <3s | 1.2-2.8s |
| PDF Processing | <30s | 15-25s |

### Scalability Metrics

| Metric | Current | Target (Production) |
|--------|---------|---------------------|
| Concurrent Users | 10 | 1000 |
| Queries per Second | 5 | 100 |
| Documents Indexed | 50 PDFs | 10,000 PDFs |
| Storage Usage | 5 GB | 500 GB |
| Monthly Cost | $100 | $2,500 |

---

## Technology Stack Summary

### Frontend
- **Framework**: Next.js 16.1.6 (App Router)
- **UI Library**: React 18.3.0
- **Language**: TypeScript 5.x
- **Styling**: Tailwind CSS 3.x
- **Components**: shadcn/ui

### Backend
- **Runtime**: Node.js 18.x
- **API**: Next.js API Routes (REST)
- **Language**: TypeScript 5.x

### Azure Services
- **AI**: Azure OpenAI (GPT-4o, text-embedding-3-large)
- **Search**: Azure AI Search (Standard S1)
- **Storage**: Azure File Share, Table Storage
- **Monitoring**: Application Insights
- **Security**: Azure Key Vault

### Libraries & Tools
- **OpenAI SDK**: openai ^4.x
- **Azure SDK**: @azure/search-documents, @azure/storage-file-share
- **PDF Processing**: pdf2json
- **Tokenization**: tiktoken (gpt-4o encoding)
- **Testing**: Jest, Playwright

---

## How to Use This Architecture

1. **View in VS Code**: Install "Markdown Preview Mermaid Support" extension
2. **Export Diagrams**: Use "Markdown PDF" or screenshot the rendered diagrams
3. **Edit in Draw.io**: Copy Mermaid code to https://mermaid.live/ → Export SVG → Import to Draw.io
4. **Generate Images**: Use Mermaid CLI: `mmdc -i TECHNICAL_ARCHITECTURE.md -o architecture.png`

