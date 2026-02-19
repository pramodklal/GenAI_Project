# ==============================================================================
# Upload PDF Files to Azure File Share
# ==============================================================================

param(
    [string]$StorageConnectionString = $env:AZURE_STORAGE_CONNECTION_STRING,
    [string]$FileShareName = $env:AZURE_FILE_SHARE_NAME,
    [string]$PdfFolder = "..\data\pdfs"
)

if (-not $StorageConnectionString) {
    Write-Host "Error: AZURE_STORAGE_CONNECTION_STRING not set" -ForegroundColor Red
    exit 1
}

if (-not $FileShareName) {
    $FileShareName = "ecommerce-policies"
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Upload PDFs to Azure File Share" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Extract storage account credentials
$StorageAccountName = [regex]::Match($StorageConnectionString, "AccountName=([^;]+)").Groups[1].Value
$StorageKey = [regex]::Match($StorageConnectionString, "AccountKey=([^;]+)").Groups[1].Value

Write-Host "Storage Account: $StorageAccountName" -ForegroundColor Green
Write-Host "File Share: $FileShareName" -ForegroundColor Green
Write-Host ""

# Check if PDF folder exists
if (-not (Test-Path $PdfFolder)) {
    Write-Host "Warning: PDF folder not found: $PdfFolder" -ForegroundColor Yellow
    Write-Host "No PDFs to upload" -ForegroundColor Yellow
    exit 0
}

# Get all PDF files
$pdfFiles = Get-ChildItem -Path $PdfFolder -Filter "*.pdf"

if ($pdfFiles.Count -eq 0) {
    Write-Host "No PDF files found in $PdfFolder" -ForegroundColor Yellow
    exit 0
}

Write-Host "Found $($pdfFiles.Count) PDF files to upload" -ForegroundColor Yellow
Write-Host ""

# Create policies directory in file share
Write-Host "Creating 'policies' directory in file share..." -ForegroundColor Yellow
az storage directory create `
    --share-name $FileShareName `
    --name "policies" `
    --account-name $StorageAccountName `
    --account-key $StorageKey 2>$null

# Upload each PDF
$count = 0
foreach ($pdf in $pdfFiles) {
    $count++
    Write-Host "[$count/$($pdfFiles.Count)] Uploading $($pdf.Name)..." -ForegroundColor Yellow
    
    az storage file upload `
        --share-name $FileShareName `
        --source $pdf.FullName `
        --path "policies/$($pdf.Name)" `
        --account-name $StorageAccountName `
        --account-key $StorageKey | Out-Null
    
    Write-Host "  ✓ $($pdf.Name) uploaded" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Upload Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "$count PDF files uploaded to Azure File Share" -ForegroundColor Green
Write-Host "Share: $FileShareName/policies/" -ForegroundColor Gray
