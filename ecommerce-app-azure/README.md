# E-Commerce App - Azure Edition

AI-powered e-commerce platform using **Azure OpenAI** (GPT-4), **Azure AI Search**, **Azure File Share**, and **Azure Table Storage**.

## 🎯 Overview

Modern e-commerce application with intelligent return management powered by Azure services:
- **AI Model**: Azure OpenAI GPT-4 for chat and text-embedding-3-large for vector search
- **Search**: Azure AI Search with vector embeddings
- **Storage**: Azure File Share for policy PDFs, Azure Table Storage for structured data
- **Frontend**: Next.js 14 with TypeScript and Tailwind CSS

## 🏗️ Architecture

### Azure Services Used
- **Azure OpenAI**: GPT-4 chat completions + text-embedding-3-large embeddings
- **Azure AI Search**: Vector search for products and policy documents
- **Azure File Share**: PDF storage for return/shipping/warranty policies
- **Azure Table Storage**: Products, orders, customers, returns, inventory
- **Azure App Service** (optional): Hosting for production deployment

### Architecture Flow
```
Next.js Frontend (localhost:3000)
    ↓
API Routes (/api/chat, /api/products, /api/orders, /api/returns)
    ↓
Azure Services:
- Azure OpenAI (GPT-4 + Embeddings)
- Azure AI Search (Vector Search)
- Azure Table Storage (Data)
- Azure File Share (PDFs)
```

## 📁 Project Structure

```
ecommerce-app-azure/
├── app/
│   ├── api/
│   │   ├── chat/route.ts           # Azure OpenAI GPT-4 chat
│   │   ├── products/route.ts       # Product search (AI Search)
│   │   ├── orders/route.ts         # Order management (Tables)
│   │   ├── returns/route.ts        # Return requests with RAG
│   │   └── dashboard/
│   │       └── stats/route.ts      # Dashboard statistics
│   ├── page.tsx                    # Homepage
│   ├── layout.tsx                  # Root layout
│   └── globals.css                 # Tailwind styles
│
├── components/
│   ├── AIChatWidget.tsx            # AI chat interface
│   └── ui/                         # Radix UI components
│
├── lib/
│   ├── azure/
│   │   ├── openai.ts               # Azure OpenAI client
│   │   ├── search.ts               # Azure AI Search client
│   │   ├── storage.ts              # Azure File Share client
│   │   └── tables.ts               # Azure Table Storage client
│   └── utils.ts                    # Utility functions
│
├── scripts/
│   ├── setup-azure-resources.ps1   # Create Azure resources
│   ├── import-data-to-tables.ps1   # Import CSV data
│   └── upload-pdfs-to-fileshare.ps1# Upload policy PDFs
│
├── data/                           # Sample data (CSV files & PDFs)
├── .env.example                    # Environment template
├── package.json                    # Dependencies
└── README.md                       # This file
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Azure subscription
- Azure CLI installed and logged in

### 1. Install Dependencies

```powershell
cd D:\GenAI_Project_2025\AWSECOMM\ecommerce-app-azure
npm install
```

### 2. Set Up Azure Resources

Run the setup script to create all Azure resources:

```powershell
.\scripts\setup-azure-resources.ps1
```

This creates:
- Azure Resource Group
- Azure OpenAI Service (with GPT-4 and text-embedding-3-large)
- Azure AI Search Service
- Azure Storage Account (File Share + Tables)

### 3. Configure Environment Variables

Copy `.env.example` to `.env.local`:

```powershell
copy .env.example .env.local
```

Edit `.env.local` with your Azure credentials:

```env
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large

# Azure AI Search
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_API_KEY=your_search_key
AZURE_SEARCH_INDEX_NAME=ecommerce-products

# Azure Storage
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;...
AZURE_FILE_SHARE_NAME=ecommerce-policies
AZURE_TABLES_CONNECTION_STRING=DefaultEndpointsProtocol=https;...
```

### 4. Import Sample Data

```powershell
# Import products, orders, customers to Azure Tables
.\scripts\import-data-to-tables.ps1

# Upload policy PDFs to Azure File Share
.\scripts\upload-pdfs-to-fileshare.ps1
```

### 5. Run Development Server

```powershell
npm run dev
```

Visit http://localhost:3000

## ✨ Features

### 🤖 Azure OpenAI Integration
- **GPT-4** chat completions for intelligent customer support
- **text-embedding-3-large** for vector embeddings
- Streaming responses for real-time chat experience

### 🔍 Azure AI Search
- Vector search for semantic product discovery
- Hybrid search combining keyword + vector search
- Auto-indexing with embeddings

### 📄 Azure File Share
- Store policy documents (return policy, warranty, shipping)
- Easy PDF upload and retrieval
- Integrated with vector search for RAG

### 💾 Azure Table Storage
- NoSQL storage for products, orders, customers, returns
- Fast queries with partition and row keys
- Cost-effective alternative to Cosmos DB

### 🎯 Intelligent Return Management
- AI-powered eligibility checking
- RAG-based policy verification using Azure AI Search
- Automatic refund calculation with restocking fees
- RMA number generation

## 💰 Cost Estimate

### Monthly Costs (Light Usage)
- **Azure OpenAI**: ~$10-20 (GPT-4 chat + embeddings)
- **Azure AI Search**: ~$75 (Basic tier) or ~$250 (Standard S1)
- **Azure Storage**: ~$5 (File Share + Tables)
- **Azure App Service**: ~$0 (Free tier) or ~$13 (B1 Basic)

**Total**: ~$90-300/month depending on tier selection

### Cost Optimization Tips
- Use Azure OpenAI responsibly (caching, prompt optimization)
- Start with Basic tier for AI Search
- Use Free tier App Service for development
- Monitor usage with Azure Cost Management

## 🛠️ Development

### Available Scripts

```powershell
npm run dev       # Start development server
npm run build     # Build for production
npm run start     # Start production server
npm run lint      # Run ESLint
npm run type-check # TypeScript type checking
```

### API Endpoints

- `POST /api/chat` - Azure OpenAI GPT-4 chat
- `GET /api/products` - Search products (AI Search)
- `GET /api/orders` - List orders (Table Storage)
- `POST /api/orders` - Create order
- `GET /api/returns` - List returns
- `POST /api/returns` - Create return request (with AI eligibility)
- `GET /api/dashboard/stats` - Dashboard statistics

## 📚 Documentation

- **SETUP_GUIDE.md**: Detailed setup instructions for Azure resources
- **ARCHITECTURE.md**: System architecture and design decisions
- **API_REFERENCE.md**: API endpoint documentation

## 🚢 Deployment

### Deploy to Azure App Service

```powershell
# Login to Azure
az login

# Create Web App
az webapp up --name your-app-name --resource-group your-rg --runtime "NODE:18-lts"

# Configure environment variables
az webapp config appsettings set --name your-app-name --resource-group your-rg --settings @appsettings.json
```

### Deploy to Vercel

```powershell
npm install -g vercel
vercel deploy --prod
```

## 🔒 Security

- All Azure credentials stored in `.env.local` (never committed)
- Use Azure Managed Identity in production
- Enable Azure Private Endpoints for enhanced security
- Implement Azure API Management for rate limiting

## 📝 License

MIT License - see LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please read CONTRIBUTING.md first.

## 📧 Support

For issues or questions, please open a GitHub issue.

---

**Built with** ❤️ **using Azure AI Services**
