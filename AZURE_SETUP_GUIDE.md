# 🚀 Azure Setup Guide - E-commerce Hybrid RAG Chatbot

## 📦 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Upload Flow                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  PDF File Upload                                            │
│       │                                                     │
│       ├──> 1. Store in Azure File Share                    │
│       │       (Original PDF preserved)                      │
│       │                                                     │
│       ├──> 2. Extract & Chunk Text                         │
│       │       (500 words per chunk)                         │
│       │                                                     │
│       ├──> 3. Generate Embeddings                          │
│       │       (Azure OpenAI text-embedding-3-large)         │
│       │                                                     │
│       └──> 4. Index to Azure AI Search                     │
│               (Vector DB with hybrid search)                │
│                                                             │
│  CSV File Upload                                            │
│       │                                                     │
│       ├──> 1. Parse Rows                                   │
│       │       (Each row = 1 document)                       │
│       │                                                     │
│       ├──> 2. Generate Embeddings                          │
│       │       (Azure OpenAI)                                │
│       │                                                     │
│       └──> 3. Index to Azure AI Search                     │
│               (Vector DB)                                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                     Query Flow                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  User Query                                                 │
│       │                                                     │
│       ├──> 1. Analyze Intent (Azure OpenAI GPT-4)          │
│       │                                                     │
│       ├──> 2. Generate Query Embedding                     │
│       │                                                     │
│       ├──> 3. Hybrid Search                                │
│       │       • Keyword search                              │
│       │       • Vector similarity                           │
│       │       • Semantic ranking                            │
│       │                                                     │
│       ├──> 4. Retrieve Relevant Chunks                     │
│       │       (From Azure AI Search)                        │
│       │                                                     │
│       └──> 5. Generate Response (GPT-4)                    │
│               (Context-aware answer)                        │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Required Azure Resources

### 1. **Azure OpenAI Service**
- **Purpose**: Generate embeddings + GPT-4 chat completions
- **Models Needed**:
  - `text-embedding-3-large` (3072 dimensions)
  - `gpt-4` or `gpt-4-turbo`

### 2. **Azure AI Search**
- **Purpose**: Vector database with hybrid search
- **Tier**: Basic or Standard
- **Features Used**:
  - Vector search
  - Semantic ranking
  - Keyword search

### 3. **Azure Storage Account**
- **Purpose**: File Share for PDF storage
- **Components**:
  - **File Share Name**: `ecommerce-pdfs`
  - **Directory**: `pdfs/`
  - **Quota**: 100 GB (configurable)

---

## 📝 Step-by-Step Setup

### Step 1: Create Azure OpenAI Resource

```bash
# Login to Azure
az login

# Set your subscription
az account set --subscription "Your-Subscription-Name"

# Create resource group
az group create --name rg-ecommerce-chatbot --location eastus

# Create Azure OpenAI resource
az cognitiveservices account create \
  --name openai-ecommerce-chatbot \
  --resource-group rg-ecommerce-chatbot \
  --location eastus \
  --kind OpenAI \
  --sku S0
```

**Deploy Models**:
1. Go to Azure Portal → Azure OpenAI Studio
2. Deploy models:
   - Model: `text-embedding-3-large` → Deployment: `text-embedding-3-large`
   - Model: `gpt-4` → Deployment: `gpt-4`

**Get Credentials**:
```bash
# Get endpoint
az cognitiveservices account show \
  --name openai-ecommerce-chatbot \
  --resource-group rg-ecommerce-chatbot \
  --query "properties.endpoint" -o tsv

# Get API key
az cognitiveservices account keys list \
  --name openai-ecommerce-chatbot \
  --resource-group rg-ecommerce-chatbot \
  --query "key1" -o tsv
```

---

### Step 2: Create Azure AI Search

```bash
# Create Azure AI Search service
az search service create \
  --name search-ecommerce-chatbot \
  --resource-group rg-ecommerce-chatbot \
  --location eastus \
  --sku basic \
  --partition-count 1 \
  --replica-count 1

# Get admin key
az search admin-key show \
  --service-name search-ecommerce-chatbot \
  --resource-group rg-ecommerce-chatbot \
  --query "primaryKey" -o tsv
```

**Get Endpoint**:
```
https://search-ecommerce-chatbot.search.windows.net
```

---

### Step 3: Create Azure Storage Account + File Share

```bash
# Create storage account
az storage account create \
  --name stecomchatbot \
  --resource-group rg-ecommerce-chatbot \
  --location eastus \
  --sku Standard_LRS \
  --kind StorageV2

# Get connection string
az storage account show-connection-string \
  --name stecomchatbot \
  --resource-group rg-ecommerce-chatbot \
  --output tsv

# Create file share
az storage share create \
  --name ecommerce-pdfs \
  --account-name stecomchatbot \
  --quota 100
```

---

## 🔐 Configure Environment Variables

Create `.env.local` file:

```bash
cd ecommerce-chatbot-nextjs
cp .env.local.example .env.local
```

Edit `.env.local`:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://openai-ecommerce-chatbot.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-from-step-1
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Azure AI Search Configuration
AZURE_SEARCH_ENDPOINT=https://search-ecommerce-chatbot.search.windows.net
AZURE_SEARCH_API_KEY=your-search-key-from-step-2
AZURE_SEARCH_INDEX_NAME=ecommerce-knowledge-base

# Azure File Share Configuration (for PDF storage)
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=stecomchatbot;AccountKey=your-key;EndpointSuffix=core.windows.net
AZURE_FILE_SHARE_NAME=ecommerce-pdfs
```

---

## 🚀 Run the Application

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Open browser:
- **Main Chat**: http://localhost:3000
- **Admin Upload**: http://localhost:3000/admin

---

## 📤 Upload Data

### Option 1: Admin Interface (Recommended)

1. Navigate to http://localhost:3000/admin
2. Drag & drop or select files:
   - **CSV files**: Auto-parsed, each row indexed
   - **PDF files**: Stored in Azure File Share + chunked to Azure AI Search
3. Monitor upload status in real-time

### Option 2: Batch Script

```bash
# Index existing data files
node scripts/indexData.js
```

---

## 🔍 How It Works

### PDF Upload Process:

1. **User uploads PDF** via `/admin` interface
2. **File stored** in Azure File Share (`ecommerce-pdfs/pdfs/`)
3. **Text extracted** using `pdf-parse`
4. **Chunked** into 500-word segments (50-word overlap)
5. **Embeddings generated** via Azure OpenAI (text-embedding-3-large)
6. **Indexed to Azure AI Search** with:
   - Chunk content (searchable text)
   - Content vector (3072-dim embedding)
   - Metadata (file URL, chunk number, category)

### Query Process:

1. **User asks question** in chat interface
2. **Intent analyzed** by GPT-4 (order tracking? product search? policy?)
3. **Query embedding generated**
4. **Hybrid search** in Azure AI Search:
   - Keyword matching
   - Vector similarity (cosine)
   - Semantic ranking
5. **Top results retrieved** (relevant chunks)
6. **Response generated** by GPT-4 with context
7. **Answer displayed** to user

---

## 📊 Storage Breakdown

| Component | Purpose | Location | Size |
|-----------|---------|----------|------|
| **Original PDFs** | File archive | Azure File Share (`ecommerce-pdfs/pdfs/`) | Original size |
| **PDF Chunks** | Searchable text | Azure AI Search | Text only |
| **Embeddings** | Vector search | Azure AI Search | 3072-dim vectors |
| **CSV Data** | Structured records | Azure AI Search | Text + embeddings |

**Example**: 10 MB PDF file
- Azure File Share: 10 MB (original PDF)
- Azure AI Search: ~500 KB (text chunks + vectors)

---

## 🔒 Security Best Practices

1. **Never commit `.env.local`** (already in `.gitignore`)
2. **Use Azure Key Vault** for production credentials
3. **Enable RBAC** on Azure resources
4. **Restrict CORS** on Azure AI Search
5. **Use Managed Identity** for Azure services (production)

---

## 💰 Cost Estimation (Monthly)

| Service | Tier | Estimated Cost |
|---------|------|----------------|
| Azure OpenAI | Pay-as-you-go | $30-100 (depends on usage) |
| Azure AI Search | Basic | $75 |
| Azure Storage | Standard LRS | $2-5 (100 GB File Share) |
| **Total** | | **~$110-180/month** |

---

## 🐛 Troubleshooting

### Issue: "AZURE_STORAGE_CONNECTION_STRING not configured"
**Solution**: Verify `.env.local` has correct connection string from Step 3

### Issue: Search index not found
**Solution**: The index is auto-created on first upload. Upload any CSV/PDF file.

### Issue: Embeddings generation slow
**Solution**: 
- Check Azure OpenAI quota/limits
- Consider batch embedding for large files

### Issue: File Share quota exceeded
**Solution**:
```bash
# Increase quota to 200 GB
az storage share update \
  --name ecommerce-pdfs \
  --account-name stecomchatbot \
  --quota 200
```

---

## 📚 Additional Resources

- [Azure OpenAI Documentation](https://learn.microsoft.com/azure/ai-services/openai/)
- [Azure AI Search Vector Search](https://learn.microsoft.com/azure/search/vector-search-overview)
- [Azure File Share Documentation](https://learn.microsoft.com/azure/storage/files/)

---

## ✅ Verification Checklist

- [ ] Azure OpenAI resource created with models deployed
- [ ] Azure AI Search service created
- [ ] Azure Storage Account + File Share created
- [ ] `.env.local` configured with all credentials
- [ ] `npm install` completed successfully
- [ ] Application runs on http://localhost:3000
- [ ] Admin interface accessible at /admin
- [ ] Test PDF upload works
- [ ] Test CSV upload works
- [ ] Chat interface returns relevant answers

---

**Ready to deploy?** See `DEPLOYMENT.md` for production deployment guide.
