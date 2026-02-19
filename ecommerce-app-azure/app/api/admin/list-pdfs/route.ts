import { NextRequest, NextResponse } from 'next/server'
import { listFiles } from '@/lib/azure/storage'

export async function GET(request: NextRequest) {
  try {
    // List files in the 'pdfs' directory
    const files = await listFiles('pdfs')

    return NextResponse.json({
      success: true,
      fileShare: process.env.AZURE_FILE_SHARE_NAME || 'ecommerce-pdfs',
      directory: 'pdfs',
      files,
      count: files.length,
    })
  } catch (error: any) {
    console.error('List PDFs Error:', error)
    return NextResponse.json(
      { error: error.message || 'Failed to list PDF files' },
      { status: 500 }
    )
  }
}
