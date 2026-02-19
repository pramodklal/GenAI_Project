import { NextRequest, NextResponse } from 'next/server'
import { uploadFile } from '@/lib/azure/storage'
import { getSearchClient, INDEXES, createDocumentsIndex } from '@/lib/azure/search'
import { generateEmbeddings } from '@/lib/azure/openai'
import { extractTextFromPDF, cleanPDFText } from '@/lib/utils/pdf-extraction'
import { chunkByTokens, createChunkMetadata } from '@/lib/utils/chunking'
import { v4 as uuidv4 } from 'uuid'

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const file = formData.get('file') as File

    if (!file) {
      return NextResponse.json(
        { error: 'No file provided' },
        { status: 400 }
      )
    }

    if (!file.name.endsWith('.pdf')) {
      return NextResponse.json(
        { error: 'Only PDF files are allowed' },
        { status: 400 }
      )
    }

    console.log(`Processing PDF: ${file.name}`)

    // Convert file to buffer
    const arrayBuffer = await file.arrayBuffer()
    const buffer = Buffer.from(arrayBuffer)

    // Step 1: Upload to Azure File Share
    console.log('Uploading to Azure File Share...')
    const fileUrl = await uploadFile(file.name, buffer, 'pdfs')

    // Step 2: Extract text from PDF
    console.log('Extracting text from PDF...')
    let extractedText = ''
    let numPages = 0
    
    try {
      const pdfData = await extractTextFromPDF(buffer)
      extractedText = cleanPDFText(pdfData.text)
      numPages = pdfData.numPages
      console.log(`Extracted ${extractedText.length} characters from ${numPages} pages`)
    } catch (extractError) {
      console.error('PDF text extraction failed:', extractError)
      return NextResponse.json(
        { error: 'Failed to extract text from PDF. The file may be corrupted or password-protected.' },
        { status: 400 }
      )
    }

    if (!extractedText || extractedText.length < 10) {
      return NextResponse.json(
        { error: 'No text content found in PDF. The file may be image-based or empty.' },
        { status: 400 }
      )
    }

    // Step 3: Chunk the text
    console.log('Chunking text...')
    const chunks = chunkByTokens(extractedText, 500, 50) // 500 tokens per chunk, 50 token overlap
    console.log(`Created ${chunks.length} chunks`)

    if (chunks.length === 0) {
      return NextResponse.json(
        { error: 'Failed to create text chunks from PDF content' },
        { status: 500 }
      )
    }

    // Step 4: Generate document ID
    const baseDocumentId = uuidv4().replace(/[^a-zA-Z0-9_-]/g, '_')

    // Step 5: Create search documents with embeddings
    console.log('Generating embeddings and preparing documents...')
    const searchDocuments = []
    let embeddingsGenerated = 0

    for (const chunk of chunks) {
      const metadata = createChunkMetadata(
        chunk,
        chunks.length,
        file.name,
        fileUrl,
        baseDocumentId
      )

      const searchDoc: any = {
        id: metadata.chunkId,
        documentId: baseDocumentId,
        fileName: file.name,
        fileUrl: fileUrl,
        content: chunk.text,
        chunkIndex: chunk.index,
        totalChunks: chunks.length,
        numPages: numPages,
        uploadedAt: new Date().toISOString(),
        baseDocumentId: baseDocumentId,
      }

      // Try to generate embeddings (optional - won't fail if OpenAI is unavailable)
      try {
        const [embedding] = await generateEmbeddings(chunk.text)
        searchDoc.contentVector = embedding
        embeddingsGenerated++
      } catch (embeddingError) {
        console.warn(`Could not generate embedding for chunk ${chunk.index}:`, embeddingError)
        // Continue without embeddings for this chunk
      }

      searchDocuments.push(searchDoc)
    }

    console.log(`Generated ${embeddingsGenerated}/${chunks.length} embeddings`)

    // Step 6: Ensure documents index exists
    console.log('Ensuring documents index exists...')
    try {
      await createDocumentsIndex()
    } catch (indexCreationError) {
      console.error('Failed to create/verify index:', indexCreationError)
      // Continue anyway, the index might already exist
    }

    // Step 7: Upload all chunks to Azure AI Search
    console.log('Uploading chunks to Azure AI Search...')
    let indexedCount = 0
    
    try {
      const searchClient = getSearchClient(INDEXES.DOCUMENTS)
      
      // Upload in batches of 100 (Azure AI Search batch limit)
      const batchSize = 100
      for (let i = 0; i < searchDocuments.length; i += batchSize) {
        const batch = searchDocuments.slice(i, i + batchSize)
        await searchClient.uploadDocuments(batch)
        indexedCount += batch.length
        console.log(`Uploaded batch: ${indexedCount}/${searchDocuments.length} chunks`)
      }
    } catch (searchError) {
      console.error('Failed to index in Azure AI Search:', searchError)
      // File is still uploaded to File Share, but not searchable
      return NextResponse.json({
        success: true,
        warning: 'PDF uploaded to File Share but failed to index in Azure AI Search',
        fileName: file.name,
        fileUrl: fileUrl,
        chunks: chunks.length,
        indexed: 0,
      })
    }

    console.log(`Successfully processed ${file.name}`)

    return NextResponse.json({
      success: true,
      fileName: file.name,
      fileUrl: fileUrl,
      baseDocumentId: baseDocumentId,
      numPages: numPages,
      chunks: chunks.length,
      indexed: indexedCount,
      embeddingsGenerated: embeddingsGenerated,
      message: `PDF processed: ${chunks.length} chunks created and ${indexedCount} indexed in Azure AI Search`,
    })
  } catch (error: any) {
    console.error('PDF Upload Error:', error)
    return NextResponse.json(
      { error: error.message || 'Failed to upload PDF file' },
      { status: 500 }
    )
  }
}
