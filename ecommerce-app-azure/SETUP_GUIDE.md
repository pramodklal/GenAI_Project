# Azure E-Commerce Application - Setup Guide

Complete guide to set up and run the Azure-based e-commerce application.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Azure Resource Setup](#azure-resource-setup)
3. [Environment Configuration](#environment-configuration)
4. [Data Import](#data-import)
5. [Running the Application](#running-the-application)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- **Node.js 18+** and npm
- **Azure CLI** ([Install Guide](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli))
- **Azure Subscription** (with permissions to create resources)
- **PowerShell 7+** (for running setup scripts)

### Azure Services Required
- Azure OpenAI Service (with model deployment approval)
- Azure AI Search Service
- Azure Storage Account
- Appropriate RBAC permissions

---

## Azure Resource Setup

### Step 1: Login to Azure

```powershell
az login
```

Select your subscription:

```powershell
az account set --subscription "Your-Subscription-Name"
```

### Step 2: Run Automated Setup Script

Navigate to the project directory and run:

```powershell
cd D:\GenAI_Project_2025\AWSECOMM\ecommerce-app-azure
.\scripts\setup-azure-resources.ps1
```

This script will create:
- ✅ Resource Group
- ✅ Azure Storage Account (with File Share and Tables)
- ✅ Azure AI Search Service (Basic tier)
- ✅ Azure OpenAI Service
- ✅ GPT-4 deployment
- ✅ text-embedding-3-large deployment
- ✅ Search index for products

**Note**: The script may take 10-15 minutes to complete. Azure OpenAI requires approval which may take additional time.

### Step 3: Manual Azure Portal Configuration (Optional)

If you prefer manual setup or encounter issues:

#### Create Resource Group
```powershell
az group create --name ecommerce-rg --location eastus
```

#### Create Storage Account
```powershell
az storage account create \
  --name ecommercestorage1234 \
  --resource-group ecommerce-rg \
  --location eastus \
  --sku Standard_LRS
```

#### Create Azure OpenAI Service
1. Visit [Azure Portal](https://portal.azure.com)
2. Create new Azure OpenAI resource
3. Request access if not already approved
4. Deploy models:
   - **gpt-4** (for chat completions)
   - **text-embedding-3-large** (for embeddings)

#### Create Azure AI Search Service
```powershell
az search service create \
  --name ecommerce-search \
  --resource-group ecommerce-rg \
  --sku basic
```

---

## Environment Configuration

### Step 1: Copy Environment Template

```powershell
copy .env.example .env.local
```

### Step 2: Fill in Azure Credentials

Edit `.env.local` with values from the setup script output or Azure Portal:

```env
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Azure AI Search
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_API_KEY=your_search_admin_key
AZURE_SEARCH_INDEX_NAME=ecommerce-products

# Azure File Share
AZURE_STORAGE_ACCOUNT_NAME=your_storage_account
AZURE_STORAGE_ACCOUNT_KEY=your_storage_key
AZURE_FILE_SHARE_NAME=ecommerce-policies
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...

# Azure Table Storage
AZURE_TABLES_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...
AZURE_TABLE_PRODUCTS=products
AZURE_TABLE_ORDERS=orders
AZURE_TABLE_CUSTOMERS=customers
AZURE_TABLE_RETURNS=returns
AZURE_TABLE_INVENTORY=inventory

# NextAuth
NEXTAUTH_SECRET=generate_with_openssl_rand_base64_32
NEXTAUTH_URL=http://localhost:3000
```

### Step 3: Generate NextAuth Secret

```powershell
# Using PowerShell
$bytes = New-Object byte[] 32
[System.Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
[Convert]::ToBase64String($bytes)

# Or using OpenSSL
openssl rand -base64 32
```

---

## Data Import

### Step 1: Install Dependencies

```powershell
npm install
```

### Step 2: Import Sample Data to Tables

```powershell
.\scripts\import-data-to-tables.ps1
```

This imports:
- 15 products
- 15 orders
- 10 customers
- Sample returns
- Inventory records

### Step 3: Upload Policy PDFs to File Share

```powershell
.\scripts\upload-pdfs-to-fileshare.ps1
```

This uploads policy documents:
- return_policy.md → PDF
- shipping_policy.md → PDF
- warranty_policy.md → PDF
- product_catalog.md → PDF

**Note**: If PDF files don't exist, convert markdown files to PDF first:

```powershell
python ..\ecommerce-app\scripts\convert_md_to_pdf.py
```

### Step 4: Index Products in Azure AI Search

After importing data to tables, products should be indexed in AI Search. This happens automatically when:
- Products are created via API
- You can manually trigger indexing by accessing `/api/products`

---

## Running the Application

### Development Mode

```powershell
npm run dev
```

Application will start at: http://localhost:3000

### Production Build

```powershell
npm run build
npm start
```

### Available Commands

```powershell
npm run dev          # Start development server (hot reload)
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
npm run type-check   # TypeScript type checking
npm run format       # Format code with Prettier
```

---

## Testing the Application

### 1. Homepage Dashboard
Visit http://localhost:3000 to see:
- Statistics cards (orders, inventory, customers)
- Product tabs
- Overview of features

### 2. AI Chat Widget
Click the blue chat button in bottom-right:
- Ask about orders: "Show me pending orders"
- Ask about policies: "What's the return policy?"
- Check eligibility: "Can I return order ORD-2024-001?"

### 3. API Endpoints

Test API endpoints using curl or Postman:

```powershell
# Get dashboard stats
curl http://localhost:3000/api/dashboard/stats

# Search products
curl http://localhost:3000/api/products?q=headphones

# Chat with AI
curl -X POST http://localhost:3000/api/chat `
  -H "Content-Type: application/json" `
  -d '{"message": "What is your return policy?"}'

# List orders
curl http://localhost:3000/api/orders

# Create return request
curl -X POST http://localhost:3000/api/returns `
  -H "Content-Type: application/json" `
  -d '{"order_id": "ORD-2024-001", "reason": "defective"}'
```

---

## Troubleshooting

### Issue: Azure OpenAI Authentication Error

**Error**: `401 Unauthorized` or `Access denied`

**Solution**:
1. Verify `AZURE_OPENAI_API_KEY` in `.env.local`
2. Check if model deployments exist:
   ```powershell
   az cognitiveservices account deployment list \
     --name your-openai-service \
     --resource-group ecommerce-rg
   ```
3. Ensure API version is correct: `2024-02-15-preview`

### Issue: Azure AI Search Not Found

**Error**: `404 Not Found` for search endpoint

**Solution**:
1. Verify search service is created:
   ```powershell
   az search service show \
     --name your-search-service \
     --resource-group ecommerce-rg
   ```
2. Check if index exists (should be `ecommerce-products`)
3. Verify search admin key is correct

### Issue: Azure Table Storage Empty

**Error**: No data in tables or empty API responses

**Solution**:
1. Re-run import script:
   ```powershell
   .\scripts\import-data-to-tables.ps1
   ```
2. Verify connection string is correct
3. Check table names match environment variables

### Issue: File Share Upload Failed

**Error**: Cannot upload PDFs to Azure File Share

**Solution**:
1. Verify storage account key in connection string
2. Ensure file share `ecommerce-policies` exists
3. Check file permissions and sizes

### Issue: NPM Install Errors

**Error**: Package installation failures

**Solution**:
```powershell
# Clear npm cache
npm cache clean --force

# Delete node_modules and package-lock.json
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json

# Reinstall
npm install
```

### Issue: Port 3000 Already in Use

**Error**: `EADDRINUSE: address already in use :::3000`

**Solution**:
```powershell
# Use different port
$env:PORT=3001
npm run dev

# Or kill process on port 3000
Get-Process -Id (Get-NetTCPConnection -LocalPort 3000).OwningProcess | Stop-Process -Force
```

---

## Deployment to Production

### Deploy to Azure App Service

```powershell
# Create Web App
az webapp up \
  --name your-app-name \
  --resource-group ecommerce-rg \
  --runtime "NODE:18-lts" \
  --sku B1

# Configure environment variables
az webapp config appsettings set \
  --name your-app-name \
  --resource-group ecommerce-rg \
  --settings \
    AZURE_OPENAI_ENDPOINT="..." \
    AZURE_OPENAI_API_KEY="..." \
    [... all other env vars ...]
```

### Deploy to Vercel

```powershell
npm install -g vercel
vercel login
vercel --prod
```

Configure environment variables in Vercel dashboard.

---

## Cost Monitoring

Monitor your Azure costs:

```powershell
# View cost analysis
az consumption usage list \
  --start-date 2026-02-01 \
  --end-date 2026-02-28

# Set budget alert
az consumption budget create \
  --budget-name ecommerce-budget \
  --amount 100 \
  --time-grain Monthly \
  --start-date 2026-02-01 \
  --end-date 2026-12-31
```

---

## Support

For issues or questions:
1. Check logs in Azure Portal
2. Review [ARCHITECTURE.md](ARCHITECTURE.md)
3. Open GitHub issue
4. Contact support team

---

**Happy Building with Azure! 🚀**
