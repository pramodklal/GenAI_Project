# Create CSV Indexes in Azure AI Search
# This script creates indexes for customers, orders, products, inventory, and returns

# Load environment variables from .env.local
$envFile = Join-Path $PSScriptRoot "..\.env.local"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]*)\s*=\s*(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
}

$searchEndpoint = $env:AZURE_SEARCH_ENDPOINT
$searchApiKey = $env:AZURE_SEARCH_API_KEY

if (-not $searchEndpoint -or -not $searchApiKey) {
    Write-Error "AZURE_SEARCH_ENDPOINT or AZURE_SEARCH_API_KEY not found in .env.local"
    exit 1
}

Write-Host "Creating CSV indexes..." -ForegroundColor Cyan
Write-Host "Search Service: $searchEndpoint" -ForegroundColor Gray

# Define indexes
$indexes = @(
    @{
        name = "ecommerce-customers-index"
        fields = @(
            @{ name = "id"; type = "Edm.String"; key = $true; searchable = $false }
            @{ name = "customer_id"; type = "Edm.String"; searchable = $true; filterable = $true }
            @{ name = "email"; type = "Edm.String"; searchable = $true; filterable = $true }
            @{ name = "name"; type = "Edm.String"; searchable = $true }
            @{ name = "phone"; type = "Edm.String"; searchable = $true }
            @{ name = "address_street"; type = "Edm.String"; searchable = $true }
            @{ name = "address_city"; type = "Edm.String"; searchable = $true; filterable = $true }
            @{ name = "address_state"; type = "Edm.String"; searchable = $true; filterable = $true }
            @{ name = "address_zip"; type = "Edm.String"; searchable = $true; filterable = $true }
            @{ name = "total_orders"; type = "Edm.Int32"; searchable = $false; filterable = $true; sortable = $true }
            @{ name = "total_returns"; type = "Edm.Int32"; searchable = $false; filterable = $true; sortable = $true }
            @{ name = "return_rate"; type = "Edm.Double"; searchable = $false; filterable = $true; sortable = $true }
            @{ name = "created_at"; type = "Edm.String"; searchable = $false; filterable = $true }
            @{ name = "last_order_date"; type = "Edm.String"; searchable = $false; filterable = $true }
        )
    },
    @{
        name = "ecommerce-orders-index"
        fields = @(
            @{ name = "id"; type = "Edm.String"; key = $true; searchable = $false }
            @{ name = "order_id"; type = "Edm.String"; searchable = $true; filterable = $true }
            @{ name = "customer_id"; type = "Edm.String"; searchable = $true; filterable = $true }
            @{ name = "order_date"; type = "Edm.String"; searchable = $false; filterable = $true }
            @{ name = "status"; type = "Edm.String"; searchable = $true; filterable = $true }
            @{ name = "total_amount"; type = "Edm.Double"; searchable = $false; filterable = $true; sortable = $true }
            @{ name = "shipping_street"; type = "Edm.String"; searchable = $true }
            @{ name = "shipping_city"; type = "Edm.String"; searchable = $true; filterable = $true }
            @{ name = "shipping_state"; type = "Edm.String"; searchable = $true; filterable = $true }
            @{ name = "shipping_zip"; type = "Edm.String"; searchable = $true; filterable = $true }
            @{ name = "delivery_date"; type = "Edm.String"; searchable = $false; filterable = $true }
            @{ name = "can_return"; type = "Edm.String"; searchable = $false; filterable = $true }
            @{ name = "return_deadline"; type = "Edm.String"; searchable = $false; filterable = $true }
            @{ name = "return_window_days"; type = "Edm.Int32"; searchable = $false; filterable = $true }
            @{ name = "created_at"; type = "Edm.String"; searchable = $false; filterable = $true }
            @{ name = "updated_at"; type = "Edm.String"; searchable = $false; filterable = $true }
        )
    },
    @{
        name = "ecommerce-products-index"
        fields = @(
            @{ name = "id"; type = "Edm.String"; key = $true; searchable = $false }
            @{ name = "product_id"; type = "Edm.String"; searchable = $true; filterable = $true }
            @{ name = "name"; type = "Edm.String"; searchable = $true }
            @{ name = "category"; type = "Edm.String"; searchable = $true; filterable = $true }
            @{ name = "price"; type = "Edm.Double"; searchable = $false; filterable = $true; sortable = $true }
            @{ name = "description"; type = "Edm.String"; searchable = $true }
            @{ name = "stock_quantity"; type = "Edm.Int32"; searchable = $false; filterable = $true; sortable = $true }
            @{ name = "reorder_level"; type = "Edm.Int32"; searchable = $false; filterable = $true }
            @{ name = "return_eligible"; type = "Edm.String"; searchable = $false; filterable = $true }
            @{ name = "return_window_days"; type = "Edm.Int32"; searchable = $false; filterable = $true }
            @{ name = "return_policy"; type = "Edm.String"; searchable = $true }
            @{ name = "warranty_months"; type = "Edm.Int32"; searchable = $false; filterable = $true }
            @{ name = "created_at"; type = "Edm.String"; searchable = $false; filterable = $true }
            @{ name = "updated_at"; type = "Edm.String"; searchable = $false; filterable = $true }
        )
    },
    @{
        name = "ecommerce-inventory-index"
        fields = @(
            @{ name = "id"; type = "Edm.String"; key = $true; searchable = $false }
            @{ name = "product_id"; type = "Edm.String"; searchable = $true; filterable = $true }
            @{ name = "location"; type = "Edm.String"; searchable = $true; filterable = $true }
            @{ name = "quantity_available"; type = "Edm.Int32"; searchable = $false; filterable = $true; sortable = $true }
            @{ name = "quantity_reserved"; type = "Edm.Int32"; searchable = $false; filterable = $true; sortable = $true }
            @{ name = "quantity_returned"; type = "Edm.Int32"; searchable = $false; filterable = $true; sortable = $true }
            @{ name = "last_restock_date"; type = "Edm.String"; searchable = $false; filterable = $true }
            @{ name = "next_restock_date"; type = "Edm.String"; searchable = $false; filterable = $true }
            @{ name = "reorder_level"; type = "Edm.Int32"; searchable = $false; filterable = $true }
            @{ name = "updated_at"; type = "Edm.String"; searchable = $false; filterable = $true }
        )
    },
    @{
        name = "ecommerce-returns-index"
        fields = @(
            @{ name = "id"; type = "Edm.String"; key = $true; searchable = $false }
            @{ name = "return_id"; type = "Edm.String"; searchable = $true; filterable = $true }
            @{ name = "order_id"; type = "Edm.String"; searchable = $true; filterable = $true }
            @{ name = "customer_id"; type = "Edm.String"; searchable = $true; filterable = $true }
            @{ name = "rma_number"; type = "Edm.String"; searchable = $true; filterable = $true }
            @{ name = "return_date"; type = "Edm.String"; searchable = $false; filterable = $true }
            @{ name = "status"; type = "Edm.String"; searchable = $true; filterable = $true }
            @{ name = "reason"; type = "Edm.String"; searchable = $true; filterable = $true }
            @{ name = "reason_details"; type = "Edm.String"; searchable = $true }
            @{ name = "refund_amount"; type = "Edm.Double"; searchable = $false; filterable = $true; sortable = $true }
            @{ name = "refund_method"; type = "Edm.String"; searchable = $true; filterable = $true }
            @{ name = "processing_notes"; type = "Edm.String"; searchable = $true }
            @{ name = "created_at"; type = "Edm.String"; searchable = $false; filterable = $true }
            @{ name = "updated_at"; type = "Edm.String"; searchable = $false; filterable = $true }
        )
    }
)

$headers = @{
    "Content-Type" = "application/json"
    "api-key" = $searchApiKey
}

foreach ($index in $indexes) {
    $indexName = $index.name
    Write-Host ""
    Write-Host "Creating index: $indexName" -ForegroundColor Yellow
    
    $indexDefinition = @{
        name = $indexName
        fields = $index.fields
    } | ConvertTo-Json -Depth 10
    
    $uri = "$searchEndpoint/indexes?api-version=2023-11-01"
    
    try {
        $response = Invoke-RestMethod -Uri $uri -Method Post -Headers $headers -Body $indexDefinition
        Write-Host "[SUCCESS] Index $indexName created!" -ForegroundColor Green
    } catch {
        if ($_.Exception.Response.StatusCode -eq 'Conflict') {
            Write-Host "[WARNING] Index $indexName already exists" -ForegroundColor Yellow
        } else {
            Write-Host "[ERROR] Failed to create $indexName" -ForegroundColor Red
            Write-Host $_.Exception.Message -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Cyan
