# ==============================================================================
# Import Sample Data to Azure Table Storage
# ==============================================================================

param(
    [string]$StorageConnectionString = $env:AZURE_TABLES_CONNECTION_STRING,
    [string]$DataFolder = "..\data"
)

if (-not $StorageConnectionString) {
    Write-Host "Error: AZURE_TABLES_CONNECTION_STRING not set" -ForegroundColor Red
    Write-Host "Please set the environment variable or provide via parameter" -ForegroundColor Yellow
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Import Data to Azure Tables" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Azure CLI is installed
if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Azure CLI not found" -ForegroundColor Red
    exit 1
}

# Extract storage account name from connection string
$StorageAccountName = [regex]::Match($StorageConnectionString, "AccountName=([^;]+)").Groups[1].Value
$StorageKey = [regex]::Match($StorageConnectionString, "AccountKey=([^;]+)").Groups[1].Value

Write-Host "Storage Account: $StorageAccountName" -ForegroundColor Green
Write-Host ""

# Import Products
Write-Host "Importing products..." -ForegroundColor Yellow
$productsFile = Join-Path $DataFolder "ecommerce-products.csv"
if (Test-Path $productsFile) {
    $products = Import-Csv $productsFile
    $count = 0
    foreach ($product in $products) {
        $entity = @{
            PartitionKey = "PRODUCT"
            RowKey = $product.product_id
        }
        foreach ($key in $product.PSObject.Properties.Name) {
            $entity[$key] = $product.$key
        }
        
        $jsonEntity = $entity | ConvertTo-Json -Compress
        az storage entity insert --table-name "products" --entity $jsonEntity --account-name $StorageAccountName --account-key $StorageKey | Out-Null
        $count++
        Write-Progress -Activity "Importing Products" -Status "$count products imported" -PercentComplete (($count / $products.Count) * 100)
    }
    Write-Host "✓ $count products imported" -ForegroundColor Green
} else {
    Write-Host "⚠ Products file not found: $productsFile" -ForegroundColor Yellow
}
Write-Host ""

# Import Orders
Write-Host "Importing orders..." -ForegroundColor Yellow
$ordersFile = Join-Path $DataFolder "ecommerce-orders.csv"
if (Test-Path $ordersFile) {
    $orders = Import-Csv $ordersFile
    $count = 0
    foreach ($order in $orders) {
        $entity = @{
            PartitionKey = "ORDER"
            RowKey = $order.order_id
        }
        foreach ($key in $order.PSObject.Properties.Name) {
            $entity[$key] = $order.$key
        }
        
        $jsonEntity = $entity | ConvertTo-Json -Compress
        az storage entity insert --table-name "orders" --entity $jsonEntity --account-name $StorageAccountName --account-key $StorageKey | Out-Null
        $count++
        Write-Progress -Activity "Importing Orders" -Status "$count orders imported" -PercentComplete (($count / $orders.Count) * 100)
    }
    Write-Host "✓ $count orders imported" -ForegroundColor Green
} else {
    Write-Host "⚠ Orders file not found: $ordersFile" -ForegroundColor Yellow
}
Write-Host ""

# Import Customers
Write-Host "Importing customers..." -ForegroundColor Yellow
$customersFile = Join-Path $DataFolder "ecommerce-customers.csv"
if (Test-Path $customersFile) {
    $customers = Import-Csv $customersFile
    $count = 0
    foreach ($customer in $customers) {
        $entity = @{
            PartitionKey = "CUSTOMER"
            RowKey = $customer.customer_id
        }
        foreach ($key in $customer.PSObject.Properties.Name) {
            $entity[$key] = $customer.$key
        }
        
        $jsonEntity = $entity | ConvertTo-Json -Compress
        az storage entity insert --table-name "customers" --entity $jsonEntity --account-name $StorageAccountName --account-key $StorageKey | Out-Null
        $count++
        Write-Progress -Activity "Importing Customers" -Status "$count customers imported" -PercentComplete (($count / $customers.Count) * 100)
    }
    Write-Host "✓ $count customers imported" -ForegroundColor Green
} else {
    Write-Host "⚠ Customers file not found: $customersFile" -ForegroundColor Yellow
}
Write-Host ""

# Import Returns
Write-Host "Importing returns..." -ForegroundColor Yellow
$returnsFile = Join-Path $DataFolder "ecommerce-returns.csv"
if (Test-Path $returnsFile) {
    $returns = Import-Csv $returnsFile
    $count = 0
    foreach ($return in $returns) {
        $entity = @{
            PartitionKey = "RETURN"
            RowKey = $return.return_id
        }
        foreach ($key in $return.PSObject.Properties.Name) {
            $entity[$key] = $return.$key
        }
        
        $jsonEntity = $entity | ConvertTo-Json -Compress
        az storage entity insert --table-name "returns" --entity $jsonEntity --account-name $StorageAccountName --account-key $StorageKey | Out-Null
        $count++
        Write-Progress -Activity "Importing Returns" -Status "$count returns imported" -PercentComplete (($count / $returns.Count) * 100)
    }
    Write-Host "✓ $count returns imported" -ForegroundColor Green
} else {
    Write-Host "⚠ Returns file not found: $returnsFile" -ForegroundColor Yellow
}
Write-Host ""

# Import Inventory
Write-Host "Importing inventory..." -ForegroundColor Yellow
$inventoryFile = Join-Path $DataFolder "ecommerce-inventory.csv"
if (Test-Path $inventoryFile) {
    $inventory = Import-Csv $inventoryFile
    $count = 0
    foreach ($item in $inventory) {
        $entity = @{
            PartitionKey = $item.product_id
            RowKey = $item.location
        }
        foreach ($key in $item.PSObject.Properties.Name) {
            $entity[$key] = $item.$key
        }
        
        $jsonEntity = $entity | ConvertTo-Json -Compress
        az storage entity insert --table-name "inventory" --entity $jsonEntity --account-name $StorageAccountName --account-key $StorageKey | Out-Null
        $count++
        Write-Progress -Activity "Importing Inventory" -Status "$count inventory records imported" -PercentComplete (($count / $inventory.Count) * 100)
    }
    Write-Host "✓ $count inventory records imported" -ForegroundColor Green
} else {
    Write-Host "⚠ Inventory file not found: $inventoryFile" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Import Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
