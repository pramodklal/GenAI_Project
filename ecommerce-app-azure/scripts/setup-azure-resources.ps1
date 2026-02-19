# ==============================================================================
# Azure E-Commerce Setup Script
# Creates all necessary Azure resources for the e-commerce application
# ==============================================================================

param(
    [string]$ResourceGroupName = "ecommerce-rg",
    [string]$Location = "eastus",
    [string]$StorageAccountName = "ecommercestorage$(Get-Random -Maximum 9999)",
    [string]$SearchServiceName = "ecommerce-search-$(Get-Random -Maximum 9999)",
    [string]$OpenAIServiceName = "ecommerce-openai-$(Get-Random -Maximum 9999)"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Azure E-Commerce Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if logged in to Azure
Write-Host "Checking Azure login..." -ForegroundColor Yellow
$account = az account show 2>$null | ConvertFrom-Json
if (-not $account) {
    Write-Host "Not logged in to Azure. Running 'az login'..." -ForegroundColor Red
    az login
}

Write-Host "Logged in as: $($account.user.name)" -ForegroundColor Green
Write-Host "Subscription: $($account.name)" -ForegroundColor Green
Write-Host ""

# Create Resource Group
Write-Host "Creating Resource Group: $ResourceGroupName" -ForegroundColor Yellow
az group create --name $ResourceGroupName --location $Location
Write-Host "✓ Resource Group created" -ForegroundColor Green
Write-Host ""

# Create Storage Account
Write-Host "Creating Storage Account: $StorageAccountName" -ForegroundColor Yellow
az storage account create `
    --name $StorageAccountName `
    --resource-group $ResourceGroupName `
    --location $Location `
    --sku Standard_LRS `
    --kind StorageV2

Write-Host "✓ Storage Account created" -ForegroundColor Green

# Get Storage Connection String
$storageKey = az storage account keys list --resource-group $ResourceGroupName --account-name $StorageAccountName --query "[0].value" -o tsv
$storageConnectionString = "DefaultEndpointsProtocol=https;AccountName=$StorageAccountName;AccountKey=$storageKey;EndpointSuffix=core.windows.net"

Write-Host "Storage Connection String saved" -ForegroundColor Green
Write-Host ""

# Create File Share
Write-Host "Creating File Share: ecommerce-policies" -ForegroundColor Yellow
az storage share create `
    --name "ecommerce-policies" `
    --account-name $StorageAccountName `
    --account-key $storageKey

Write-Host "✓ File Share created" -ForegroundColor Green
Write-Host ""

# Create Tables
Write-Host "Creating Azure Tables..." -ForegroundColor Yellow
$tables = @("products", "orders", "customers", "returns", "inventory")
foreach ($table in $tables) {
    az storage table create --name $table --account-name $StorageAccountName --account-key $storageKey
    Write-Host "  ✓ Table '$table' created" -ForegroundColor Green
}
Write-Host ""

# Create Azure AI Search Service
Write-Host "Creating Azure AI Search Service: $SearchServiceName" -ForegroundColor Yellow
Write-Host "(This may take a few minutes...)" -ForegroundColor Gray
az search service create `
    --name $SearchServiceName `
    --resource-group $ResourceGroupName `
    --location $Location `
    --sku basic

Write-Host "✓ Azure AI Search Service created" -ForegroundColor Green

# Get Search Admin Key
$searchKey = az search admin-key show --resource-group $ResourceGroupName --service-name $SearchServiceName --query "primaryKey" -o tsv
$searchEndpoint = "https://$SearchServiceName.search.windows.net"

Write-Host "Search Endpoint: $searchEndpoint" -ForegroundColor Green
Write-Host ""

# Create Azure OpenAI Service
Write-Host "Creating Azure OpenAI Service: $OpenAIServiceName" -ForegroundColor Yellow
Write-Host "(This requires approval and may take time...)" -ForegroundColor Gray
az cognitiveservices account create `
    --name $OpenAIServiceName `
    --resource-group $ResourceGroupName `
    --location $Location `
    --kind OpenAI `
    --sku S0 `
    --yes

Write-Host "✓ Azure OpenAI Service created" -ForegroundColor Green

# Get OpenAI Key and Endpoint
$openAIKey = az cognitiveservices account keys list --name $OpenAIServiceName --resource-group $ResourceGroupName --query "key1" -o tsv
$openAIEndpoint = az cognitiveservices account show --name $OpenAIServiceName --resource-group $ResourceGroupName --query "properties.endpoint" -o tsv

Write-Host "OpenAI Endpoint: $openAIEndpoint" -ForegroundColor Green
Write-Host ""

# Deploy GPT-4 Model
Write-Host "Deploying GPT-4 model..." -ForegroundColor Yellow
az cognitiveservices account deployment create `
    --name $OpenAIServiceName `
    --resource-group $ResourceGroupName `
    --deployment-name "gpt-4" `
    --model-name "gpt-4" `
    --model-version "turbo-2024-04-09" `
    --model-format OpenAI `
    --sku-capacity 10 `
    --sku-name "Standard"

Write-Host "✓ GPT-4 model deployed" -ForegroundColor Green
Write-Host ""

# Deploy Embedding Model
Write-Host "Deploying text-embedding-3-large model..." -ForegroundColor Yellow
az cognitiveservices account deployment create `
    --name $OpenAIServiceName `
    --resource-group $ResourceGroupName `
    --deployment-name "text-embedding-3-large" `
    --model-name "text-embedding-3-large" `
    --model-version "1" `
    --model-format OpenAI `
    --sku-capacity 10 `
    --sku-name "Standard"

Write-Host "✓ Embedding model deployed" -ForegroundColor Green
Write-Host ""

# Create Search Index
Write-Host "Creating AI Search Index: ecommerce-products..." -ForegroundColor Yellow
$indexSchema = @"
{
  "name": "ecommerce-products",
  "fields": [
    {"name": "id", "type": "Edm.String", "key": true, "searchable": false},
    {"name": "product_id", "type": "Edm.String", "searchable": true, "filterable": true},
    {"name": "name", "type": "Edm.String", "searchable": true},
    {"name": "category", "type": "Edm.String", "searchable": true, "filterable": true},
    {"name": "description", "type": "Edm.String", "searchable": true},
    {"name": "content", "type": "Edm.String", "searchable": true},
    {"name": "contentVector", "type": "Collection(Edm.Single)", "searchable": true, "dimensions": 3072}
  ]
}
"@

$indexSchema | Out-File -FilePath "temp_index.json" -Encoding UTF8
az search index create --service-name $SearchServiceName --name "ecommerce-products" --body @temp_index.json
Remove-Item "temp_index.json"

Write-Host "✓ Search Index created" -ForegroundColor Green
Write-Host ""

# Output Environment Variables
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Add these to your .env.local file:" -ForegroundColor Yellow
Write-Host ""
Write-Host "# Azure OpenAI" -ForegroundColor Gray
Write-Host "AZURE_OPENAI_ENDPOINT=$openAIEndpoint"
Write-Host "AZURE_OPENAI_API_KEY=$openAIKey"
Write-Host "AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4"
Write-Host "AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large"
Write-Host "AZURE_OPENAI_API_VERSION=2024-02-15-preview"
Write-Host ""
Write-Host "# Azure AI Search" -ForegroundColor Gray
Write-Host "AZURE_SEARCH_ENDPOINT=$searchEndpoint"
Write-Host "AZURE_SEARCH_API_KEY=$searchKey"
Write-Host "AZURE_SEARCH_INDEX_NAME=ecommerce-products"
Write-Host ""
Write-Host "# Azure Storage" -ForegroundColor Gray
Write-Host "AZURE_STORAGE_ACCOUNT_NAME=$StorageAccountName"
Write-Host "AZURE_STORAGE_ACCOUNT_KEY=$storageKey"
Write-Host "AZURE_FILE_SHARE_NAME=ecommerce-policies"
Write-Host "AZURE_STORAGE_CONNECTION_STRING=$storageConnectionString"
Write-Host ""
Write-Host "# Azure Tables" -ForegroundColor Gray
Write-Host "AZURE_TABLES_CONNECTION_STRING=$storageConnectionString"
Write-Host "AZURE_TABLE_PRODUCTS=products"
Write-Host "AZURE_TABLE_ORDERS=orders"
Write-Host "AZURE_TABLE_CUSTOMERS=customers"
Write-Host "AZURE_TABLE_RETURNS=returns"
Write-Host "AZURE_TABLE_INVENTORY=inventory"
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Copy the above values to .env.local" -ForegroundColor White
Write-Host "2. Run: .\scripts\import-data-to-tables.ps1" -ForegroundColor White
Write-Host "3. Run: .\scripts\upload-pdfs-to-fileshare.ps1" -ForegroundColor White
Write-Host "4. Run: npm run dev" -ForegroundColor White
Write-Host ""
