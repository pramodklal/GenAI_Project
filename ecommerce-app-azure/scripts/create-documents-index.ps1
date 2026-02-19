# Create Documents Index in Azure AI Search
# This script creates the ecommerce-documents-index with vector search support

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
$indexName = "ecommerce-documents-index"

if (-not $searchEndpoint -or -not $searchApiKey) {
    Write-Error "AZURE_SEARCH_ENDPOINT or AZURE_SEARCH_API_KEY not found in .env.local"
    exit 1
}

Write-Host "Creating index: $indexName" -ForegroundColor Cyan
Write-Host "Search Service: $searchEndpoint" -ForegroundColor Gray

$indexDefinition = @{
    name = $indexName
    fields = @(
        @{
            name = "id"
            type = "Edm.String"
            key = $true
            searchable = $false
            filterable = $true
            sortable = $false
        },
        @{
            name = "documentId"
            type = "Edm.String"
            searchable = $false
            filterable = $true
            sortable = $false
        },
        @{
            name = "fileName"
            type = "Edm.String"
            searchable = $true
            filterable = $true
            sortable = $true
        },
        @{
            name = "chunkIndex"
            type = "Edm.Int32"
            searchable = $false
            filterable = $true
            sortable = $true
        },
        @{
            name = "content"
            type = "Edm.String"
            searchable = $true
            filterable = $false
            sortable = $false
        },
        @{
            name = "contentVector"
            type = "Collection(Edm.Single)"
            searchable = $true
            filterable = $false
            sortable = $false
            dimensions = 3072
            vectorSearchProfile = "vector-profile"
        },
        @{
            name = "fileUrl"
            type = "Edm.String"
            searchable = $false
            filterable = $false
            sortable = $false
        },
        @{
            name = "uploadedAt"
            type = "Edm.DateTimeOffset"
            searchable = $false
            filterable = $true
            sortable = $true
        },
        @{
            name = "numPages"
            type = "Edm.Int32"
            searchable = $false
            filterable = $true
            sortable = $false
        },
        @{
            name = "totalChunks"
            type = "Edm.Int32"
            searchable = $false
            filterable = $true
            sortable = $false
        },
        @{
            name = "baseDocumentId"
            type = "Edm.String"
            searchable = $false
            filterable = $true
            sortable = $false
        }
    )
    vectorSearch = @{
        algorithms = @(
            @{
                name = "hnsw-algorithm"
                kind = "hnsw"
                hnswParameters = @{
                    metric = "cosine"
                    m = 4
                    efConstruction = 400
                    efSearch = 500
                }
            }
        )
        profiles = @(
            @{
                name = "vector-profile"
                algorithm = "hnsw-algorithm"
            }
        )
    }
} | ConvertTo-Json -Depth 10

$uri = "$searchEndpoint/indexes?api-version=2023-11-01"
$headers = @{
    "Content-Type" = "application/json"
    "api-key" = $searchApiKey
}

try {
    Write-Host "Sending request to create index..." -ForegroundColor Yellow
    $response = Invoke-RestMethod -Uri $uri -Method Post -Headers $headers -Body $indexDefinition
    Write-Host "[SUCCESS] Index created successfully!" -ForegroundColor Green
    Write-Host "Index name: $($response.name)" -ForegroundColor Green
} catch {
    if ($_.Exception.Response.StatusCode -eq 'Conflict') {
        Write-Host "[WARNING] Index already exists" -ForegroundColor Yellow
    } else {
        Write-Host "[ERROR] Error creating index:" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        if ($_.ErrorDetails) {
            Write-Host $_.ErrorDetails.Message -ForegroundColor Red
        }
        exit 1
    }
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Cyan
