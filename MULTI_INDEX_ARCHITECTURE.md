# 🗄️ Multi-Index Architecture - Azure AI Search

## 📊 **Architecture Overview**

Each CSV file type gets its own **isolated Azure AI Search index**:

```
┌──────────────────────────────────────────────────────────┐
│               CSV Files → Separate Indexes                │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  ecommerce-customers.csv  →  ecommerce-customers-index   │
│  ecommerce-orders.csv     →  ecommerce-orders-index      │
│  ecommerce-products.csv   →  ecommerce-products-index    │
│  ecommerce-inventory.csv  →  ecommerce-inventory-index   │
│  ecommerce-returns.csv    →  ecommerce-returns-index     │
│  *.pdf files              →  ecommerce-documents-index   │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

## ✅ **Benefits of Separate Indexes**

| Benefit | Description |
|---------|-------------|
| **Data Isolation** | Each data type is completely separate |
| **Independent Scaling** | Scale indexes individually based on load |
| **Security** | Apply different access controls per index |
| **Performance** | Faster searches within specific data types |
| **Maintenance** | Update/delete without affecting other data |
| **Clear Organization** | Each index has consistent schema |

## 🔧 **Environment Configuration**

Update your `.env.local`:

```env
# Azure AI Search - Multiple Indexes
AZURE_SEARCH_INDEX_CUSTOMERS=ecommerce-customers-index
AZURE_SEARCH_INDEX_ORDERS=ecommerce-orders-index
AZURE_SEARCH_INDEX_PRODUCTS=ecommerce-products-index
AZURE_SEARCH_INDEX_INVENTORY=ecommerce-inventory-index
AZURE_SEARCH_INDEX_RETURNS=ecommerce-returns-index
AZURE_SEARCH_INDEX_DOCUMENTS=ecommerce-documents-index
```

## 🚀 **How It Works**

### 1. **Automatic Index Detection**

When you upload a CSV file, the system automatically detects which index to use:

```typescript
// By filename
ecommerce-customers.csv → customers index
ecommerce-orders.csv    → orders index
ecommerce-products.csv  → products index

// By headers
customer_id, email      → customers index
order_id, order_date    → orders index
sku, price, stock       → products index
```

### 2. **Upload Flow**

```
Upload CSV File
     │
     ├──> Detect Index Type
     │    (from filename or headers)
     │
     ├──> Parse CSV Rows
     │
     ├──> Generate Embeddings
     │    (Azure OpenAI)
     │
     └──> Upload to Specific Index
          (e.g., orders-index)
```

### 3. **Search Flow**

The chat API searches across relevant indexes based on query intent:

```typescript
// User: "Where is my order?"
→ Search: orders + customers indexes

// User: "Show me laptops"
→ Search: products + inventory indexes

// User: "What's the return policy?"
→ Search: returns + documents indexes

// User: "General question"
→ Search: ALL indexes
```

## 📂 **Index Schema**

Each index has the same structure but different data:

```typescript
{
  id: string              // Unique document ID
  content: string         // Searchable text
  text_embedding: number[] // 3072-dim vector
  category: string        // customer/order/product/etc
  source_file: string     // Original filename
  content_type: string    // csv or pdf
  metadata: string        // JSON metadata
  created_at: DateTime    // Upload timestamp
}
```

## 🎯 **Usage Examples**

### Create All Indexes

```typescript
const azureSearch = new AzureSearchService()
await azureSearch.createAllIndexes()
// Creates all 6 indexes automatically
```

### Upload to Specific Index

```typescript
await azureSearch.uploadDocuments(documents, 'customers')
await azureSearch.uploadDocuments(documents, 'orders')
await azureSearch.uploadDocuments(documents, 'products')
```

### Search Specific Index

```typescript
// Search only customers
const results = await azureSearch.hybridSearch(query, 'customers', 5)

// Search multiple indexes
const results = await azureSearch.hybridSearchMultiple(
  query,
  ['orders', 'customers'],
  3
)

// Search ALL indexes
const results = await azureSearch.hybridSearchAll(query, 2)
```

### Get Statistics

```typescript
// Specific index
const stats = await azureSearch.getIndexStatistics('customers')

// All indexes
const allStats = await azureSearch.getAllIndexStatistics()
// Returns:
// {
//   totalDocuments: 150,
//   indexes: [
//     { indexType: 'customers', indexName: '...', documentCount: 50 },
//     { indexType: 'orders', indexName: '...', documentCount: 100 },
//     ...
//   ]
// }
```

## 📊 **Admin Dashboard**

The `/admin` page now shows:

- **6 Separate Cards**: Customers, Orders, Products, Inventory, Returns, Documents
- **Index Details Table**: All index names with document counts
- **Real-time Upload**: Auto-detects which index to use

## 🔍 **Index Auto-Detection**

### By Filename:
- Contains "customer" → `customers` index
- Contains "order" → `orders` index
- Contains "product" → `products` index
- Contains "inventory" or "stock" → `inventory` index
- Contains "return" → `returns` index

### By Headers:
- Has `customer_id`, `email` → `customers`
- Has `order_id`, `order_date` → `orders`
- Has `sku`, `price` → `products`
- Has `stock_quantity` → `inventory`
- Has `return_id`, `refund_amount` → `returns`

## 🔧 **Setup Instructions**

### 1. Install Dependencies

```bash
cd ecommerce-chatbot-nextjs
npm install
```

### 2. Configure Environment

Copy `.env.local.example` to `.env.local` and add your Azure credentials.

### 3. Create Indexes

The indexes are created automatically on first upload, or you can create them manually:

```bash
# Add this script to package.json
"create-indexes": "node scripts/createIndexes.js"
```

### 4. Upload Data

Navigate to `http://localhost:3000/admin` and drag-drop your CSV files:

- `ecommerce-customers.csv` → Customers index
- `ecommerce-orders.csv` → Orders index
- `ecommerce-products.csv` → Products index
- `ecommerce-inventory.csv` → Inventory index
- `ecommerce-returns.csv` → Returns index

## 💾 **Data Storage Summary**

| Component | Storage | Purpose |
|-----------|---------|---------|
| **CSV Data** | Azure AI Search (6 indexes) | Structured searchable data |
| **PDF Files** | Azure File Share | Original file storage |
| **PDF Chunks** | Azure AI Search (documents index) | Searchable text |
| **Embeddings** | Azure AI Search (all indexes) | Vector search |

## 🎯 **When to Use This Architecture**

✅ **Use Separate Indexes When:**
- Different data types with distinct schemas
- Need independent scaling
- Want data isolation
- Different security policies per data type
- Performance critical (faster targeted searches)

❌ **Use Single Index When:**
- All data has same schema
- Simple use case
- Small dataset (<10k documents)
- No need for isolation

## 🚀 **Performance Considerations**

- **Search Speed**: Faster (searches only relevant index)
- **Indexing Speed**: Same (parallel uploads possible)
- **Cost**: Slightly higher (6 indexes vs 1)
- **Maintenance**: More complex (manage 6 indexes)

## 📝 **Next Steps**

1. ✅ Multi-index architecture implemented
2. ✅ Auto-detection of CSV types
3. ✅ Intent-based multi-index search
4. ✅ Admin dashboard with per-index stats
5. ⏳ Test with real data
6. ⏳ Configure Azure resources
7. ⏳ Deploy to production

---

**Ready to upload your CSV files!** Each will automatically go to its appropriate index.
