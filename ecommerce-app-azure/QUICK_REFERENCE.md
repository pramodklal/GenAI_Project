# Azure E-Commerce App - Quick Reference

## 🚀 Quick Start Commands

```powershell
# 1. Navigate to project
cd D:\GenAI_Project_2025\AWSECOMM\ecommerce-app-azure

# 2. Install dependencies
npm install

# 3. Setup Azure resources (one-time)
.\scripts\setup-azure-resources.ps1

# 4. Configure environment
copy .env.example .env.local
# Edit .env.local with Azure credentials

# 5. Import data
.\scripts\import-data-to-tables.ps1
.\scripts\upload-pdfs-to-fileshare.ps1

# 6. Run development server
npm run dev
```

## 📁 Project Structure

```
ecommerce-app-azure/
├── app/
│   ├── api/                    # API Routes
│   │   ├── chat/              # Azure OpenAI GPT-4 chat
│   │   ├── products/          # Product search (AI Search)
│   │   ├── orders/            # Order management (Tables)
│   │   ├── returns/           # Return requests with RAG
│   │   └── dashboard/stats/   # Dashboard statistics
│   ├── page.tsx               # Homepage
│   ├── layout.tsx             # Root layout
│   └── globals.css            # Styles
├── components/
│   ├── AIChatWidget.tsx       # AI chat widget
│   └── ui/                    # UI components
├── lib/
│   ├── azure/
│   │   ├── openai.ts          # Azure OpenAI client
│   │   ├── search.ts          # Azure AI Search client
│   │   ├── storage.ts         # Azure File Share client
│   │   └── tables.ts          # Azure Table Storage client
│   └── utils.ts               # Utilities
├── scripts/
│   ├── setup-azure-resources.ps1
│   ├── import-data-to-tables.ps1
│   └── upload-pdfs-to-fileshare.ps1
└── data/                      # Sample CSV and PDF files
```

## 🔑 Key Technologies

| Component | Technology |
|-----------|-----------|
| **AI Chat** | Azure OpenAI GPT-4 |
| **Embeddings** | text-embedding-3-large |
| **Search** | Azure AI Search (vector + keyword) |
| **Database** | Azure Table Storage |
| **File Storage** | Azure File Share |
| **Frontend** | Next.js 14 + TypeScript |
| **UI** | Tailwind CSS + Radix UI |

## 🌐 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Azure OpenAI chat |
| `/api/products` | GET | Search products (AI Search) |
| `/api/orders` | GET/POST | Order management |
| `/api/returns` | GET/POST | Return requests (RAG) |
| `/api/dashboard/stats` | GET | Dashboard statistics |

## 💡 Example Queries for AI Chat

```
"Show me all pending orders"
"Which products are low in stock?"
"What's the return policy for defective items?"
"Check return eligibility for order ORD-2024-001"
"Can I return an item after 30 days?"
"Track order ORD-2024-005"
```

## 🔧 Environment Variables

### Required Variables

```env
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large

# Azure AI Search
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_API_KEY=your_key
AZURE_SEARCH_INDEX_NAME=ecommerce-products

# Azure Storage
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;...
AZURE_FILE_SHARE_NAME=ecommerce-policies
AZURE_TABLES_CONNECTION_STRING=DefaultEndpointsProtocol=https;...
```

## 📊 Azure Resources Created

| Resource | Type | Purpose |
|----------|------|---------|
| Resource Group | Container | Holds all resources |
| Storage Account | Storage | Tables + File Share |
| OpenAI Service | Cognitive Services | GPT-4 + Embeddings |
| AI Search | Search | Vector + keyword search |
| File Share | Storage | Policy PDFs |
| Tables | Storage | Products, orders, customers |

## 💰 Estimated Monthly Costs

| Service | Tier | Cost |
|---------|------|------|
| Azure OpenAI | Standard | $10-20 |
| Azure AI Search | Basic | $75 |
| Azure Storage | Standard | $5 |
| **Total** | | **~$90-100/month** |

## 🐛 Common Issues & Fixes

### Issue: 401 Unauthorized (OpenAI)
```powershell
# Check API key
echo $env:AZURE_OPENAI_API_KEY
# Verify deployment names match .env.local
```

### Issue: Empty Tables
```powershell
# Re-import data
.\scripts\import-data-to-tables.ps1
```

### Issue: Search Not Working
```powershell
# Verify search service
az search service show --name your-search --resource-group ecommerce-rg
```

### Issue: Port in Use
```powershell
# Use different port
$env:PORT=3001
npm run dev
```

## 📚 Documentation

- **[README.md](README.md)** - Project overview
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Detailed setup instructions
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture (if available)

## 🧪 Testing

```powershell
# Test chat API
curl -X POST http://localhost:3000/api/chat `
  -H "Content-Type: application/json" `
  -d '{"message": "What is your return policy?"}'

# Test products search
curl http://localhost:3000/api/products?q=headphones

# Test dashboard
curl http://localhost:3000/api/dashboard/stats
```

## 📞 Support

For help:
1. Check [SETUP_GUIDE.md](SETUP_GUIDE.md)
2. Review Azure Portal logs
3. Verify environment variables
4. Check Azure service status

---

**Built with Azure AI Services** ☁️
