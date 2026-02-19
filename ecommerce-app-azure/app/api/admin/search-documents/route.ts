import { NextRequest, NextResponse } from 'next/server'
import { getSearchClient, INDEXES } from '@/lib/azure/search'

export async function GET(request: NextRequest) {
  try {
    const searchClient = getSearchClient(INDEXES.DOCUMENTS)
    
    // Search for all documents (using wildcard)
    const results = await searchClient.search('*', {
      top: 50,
      select: ['id', 'documentId', 'fileName', 'fileUrl', 'content', 'chunkIndex', 'totalChunks', 'numPages', 'uploadedAt', 'baseDocumentId'],
      includeTotalCount: true,
    })

    const documents = []
    for await (const result of results.results) {
      documents.push(result.document)
    }

    return NextResponse.json({
      success: true,
      indexName: INDEXES.DOCUMENTS,
      count: documents.length,
      totalCount: results.count,
      documents,
    })
  } catch (error: any) {
    console.error('Search Documents Error:', error)
    return NextResponse.json(
      { error: error.message || 'Failed to search documents' },
      { status: 500 }
    )
  }
}
