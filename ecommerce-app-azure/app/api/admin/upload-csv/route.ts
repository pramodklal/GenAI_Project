import { NextRequest, NextResponse } from 'next/server'
import { getSearchClient, INDEXES } from '@/lib/azure/search'
import { v4 as uuidv4 } from 'uuid'

// Map CSV types to their corresponding Azure AI Search index names
const CSV_TYPE_TO_INDEX: Record<string, string> = {
  'ecommerce-customers': INDEXES.CUSTOMERS,
  'ecommerce-orders': INDEXES.ORDERS,
  'ecommerce-products': INDEXES.PRODUCTS,
  'ecommerce-inventory': INDEXES.INVENTORY,
  'ecommerce-returns': INDEXES.RETURNS,
}

// Parse CSV content
function parseCSV(content: string): any[] {
  const lines = content.trim().split('\n')
  if (lines.length < 2) return []

  const headers = lines[0].split(',').map(h => h.trim().replace(/^"|"$/g, ''))
  const records = []

  for (let i = 1; i < lines.length; i++) {
    const line = lines[i].trim()
    if (!line) continue

    // Handle quotes and commas in CSV
    const values: string[] = []
    let currentValue = ''
    let insideQuotes = false

    for (let j = 0; j < line.length; j++) {
      const char = line[j]
      
      if (char === '"') {
        insideQuotes = !insideQuotes
      } else if (char === ',' && !insideQuotes) {
        values.push(currentValue.trim().replace(/^"|"$/g, ''))
        currentValue = ''
      } else {
        currentValue += char
      }
    }
    values.push(currentValue.trim().replace(/^"|"$/g, ''))

    if (values.length === headers.length) {
      const record: any = {}
      headers.forEach((header, index) => {
        record[header] = values[index]
      })
      records.push(record)
    }
  }

  return records
}

// Transform records to match Azure AI Search schema
function transformRecords(records: any[], type: string): any[] {
  return records.map(record => {
    // Generate a unique ID for each record
    const id = record.id || record.ID || uuidv4()
    
    // Base document with required fields
    const doc: any = {
      id: String(id).replace(/[^a-zA-Z0-9_-]/g, '_'), // Azure Search ID restrictions
    }

    // Add all fields from the record - keep original field names (snake_case)
    Object.keys(record).forEach(key => {
      if (key.toLowerCase() !== 'id') {
        doc[key] = record[key]
      }
    })

    // Add type-specific transformations for numeric fields
    if (type === 'ecommerce-products') {
      if (doc.price) doc.price = parseFloat(doc.price) || 0
      if (doc.stock_quantity) doc.stock_quantity = parseInt(doc.stock_quantity) || 0
      if (doc.rating) doc.rating = parseFloat(doc.rating) || 0
      if (doc.reorder_level) doc.reorder_level = parseInt(doc.reorder_level) || 0
      if (doc.warranty_months) doc.warranty_months = parseInt(doc.warranty_months) || 0
      if (doc.return_window_days) doc.return_window_days = parseInt(doc.return_window_days) || 0
    } else if (type === 'ecommerce-orders') {
      if (doc.total_amount) doc.total_amount = parseFloat(doc.total_amount) || 0
      if (doc.return_window_days) doc.return_window_days = parseInt(doc.return_window_days) || 0
    } else if (type === 'ecommerce-customers') {
      if (doc.total_orders) doc.total_orders = parseInt(doc.total_orders) || 0
      if (doc.total_returns) doc.total_returns = parseInt(doc.total_returns) || 0
      if (doc.return_rate) doc.return_rate = parseFloat(doc.return_rate) || 0
    } else if (type === 'ecommerce-inventory') {
      if (doc.quantity_available) doc.quantity_available = parseInt(doc.quantity_available) || 0
      if (doc.quantity_reserved) doc.quantity_reserved = parseInt(doc.quantity_reserved) || 0
      if (doc.quantity_returned) doc.quantity_returned = parseInt(doc.quantity_returned) || 0
      if (doc.reorder_level) doc.reorder_level = parseInt(doc.reorder_level) || 0
    } else if (type === 'ecommerce-returns') {
      if (doc.refund_amount) doc.refund_amount = parseFloat(doc.refund_amount) || 0
    }

    return doc
  })
}

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const file = formData.get('file') as File
    const type = formData.get('type') as string

    if (!file) {
      return NextResponse.json(
        { error: 'No file provided' },
        { status: 400 }
      )
    }

    if (!type || !CSV_TYPE_TO_INDEX[type]) {
      return NextResponse.json(
        { error: 'Invalid CSV type provided' },
        { status: 400 }
      )
    }

    // Read file content
    const content = await file.text()
    
    // Parse CSV
    const records = parseCSV(content)
    
    if (records.length === 0) {
      return NextResponse.json(
        { error: 'No valid records found in CSV file' },
        { status: 400 }
      )
    }

    // Transform records for Azure AI Search
    const documents = transformRecords(records, type)

    // Get the appropriate search client for the index
    const indexName = CSV_TYPE_TO_INDEX[type]
    const searchClient = getSearchClient(indexName)

    // Upload documents to Azure AI Search in batches
    const batchSize = 100
    let uploadedCount = 0

    for (let i = 0; i < documents.length; i += batchSize) {
      const batch = documents.slice(i, i + batchSize)
      await searchClient.uploadDocuments(batch)
      uploadedCount += batch.length
    }

    return NextResponse.json({
      success: true,
      count: uploadedCount,
      type,
      indexName,
    })
  } catch (error: any) {
    console.error('CSV Upload Error:', error)
    return NextResponse.json(
      { error: error.message || 'Failed to upload CSV file' },
      { status: 500 }
    )
  }
}
