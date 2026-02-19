'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Upload, FileText, CheckCircle2, AlertCircle, RefreshCw, Search, Database } from 'lucide-react'

const CSV_FILES = [
  { value: 'ecommerce-customers', label: 'Customers' },
  { value: 'ecommerce-orders', label: 'Orders' },
  { value: 'ecommerce-products', label: 'Products' },
  { value: 'ecommerce-inventory', label: 'Inventory' },
  { value: 'ecommerce-returns', label: 'Returns' },
]

export default function AdminPage() {
  const [selectedCsvType, setSelectedCsvType] = useState('')
  const [csvFile, setCsvFile] = useState<File | null>(null)
  const [pdfFile, setPdfFile] = useState<File | null>(null)
  const [csvUploading, setCsvUploading] = useState(false)
  const [pdfUploading, setPdfUploading] = useState(false)
  const [csvStatus, setCsvStatus] = useState<{ type: 'success' | 'error'; message: string } | null>(null)
  const [pdfStatus, setPdfStatus] = useState<{ type: 'success' | 'error'; message: string } | null>(null)
  const [uploadedPdfs, setUploadedPdfs] = useState<string[]>([])
  const [loadingPdfs, setLoadingPdfs] = useState(false)
  const [indexedDocuments, setIndexedDocuments] = useState<any[]>([])
  const [loadingDocuments, setLoadingDocuments] = useState(false)
  const [selectedDocument, setSelectedDocument] = useState<any>(null)

  // Load uploaded PDFs and indexed documents on mount
  useEffect(() => {
    loadUploadedPdfs()
    loadIndexedDocuments()
  }, [])

  const loadUploadedPdfs = async () => {
    setLoadingPdfs(true)
    try {
      const response = await fetch('/api/admin/list-pdfs')
      const result = await response.json()
      if (response.ok) {
        setUploadedPdfs(result.files || [])
      }
    } catch (error) {
      console.error('Failed to load PDFs:', error)
    } finally {
      setLoadingPdfs(false)
    }
  }

  const loadIndexedDocuments = async () => {
    setLoadingDocuments(true)
    try {
      const response = await fetch('/api/admin/search-documents')
      const result = await response.json()
      if (response.ok) {
        setIndexedDocuments(result.documents || [])
      }
    } catch (error) {
      console.error('Failed to load indexed documents:', error)
    } finally {
      setLoadingDocuments(false)
    }
  }

  const handleCsvUpload = async () => {
    if (!selectedCsvType || !csvFile) {
      setCsvStatus({ type: 'error', message: 'Please select a CSV type and file' })
      return
    }

    setCsvUploading(true)
    setCsvStatus(null)

    try {
      const formData = new FormData()
      formData.append('file', csvFile)
      formData.append('type', selectedCsvType)

      const response = await fetch('/api/admin/upload-csv', {
        method: 'POST',
        body: formData,
      })

      const result = await response.json()

      if (!response.ok) {
        throw new Error(result.error || 'Upload failed')
      }

      setCsvStatus({
        type: 'success',
        message: `Successfully uploaded ${result.count} ${selectedCsvType} records to Azure AI Search`,
      })
      setCsvFile(null)
      setSelectedCsvType('')
      // Reset file input
      const fileInput = document.getElementById('csv-file-input') as HTMLInputElement
      if (fileInput) fileInput.value = ''
    } catch (error: any) {
      setCsvStatus({
        type: 'error',
        message: error.message || 'Failed to upload CSV file',
      })
    } finally {
      setCsvUploading(false)
    }
  }

  const handlePdfUpload = async () => {
    if (!pdfFile) {
      setPdfStatus({ type: 'error', message: 'Please select a PDF file' })
      return
    }

    setPdfUploading(true)
    setPdfStatus(null)

    try {
      const formData = new FormData()
      formData.append('file', pdfFile)

      const response = await fetch('/api/admin/upload-pdf', {
        method: 'POST',
        body: formData,
      })

      const result = await response.json()

      if (!response.ok) {
        throw new Error(result.error || 'Upload failed')
      }

      const successMessage = result.chunks
        ? `Successfully processed ${pdfFile.name}: ${result.chunks} chunks created${result.numPages ? ` from ${result.numPages} pages` : ''}, ${result.indexed || 0} indexed in Azure AI Search${result.embeddingsGenerated ? ` with ${result.embeddingsGenerated} vector embeddings` : ''}`
        : `Successfully uploaded ${pdfFile.name} to Azure File Share`

      setPdfStatus({
        type: 'success',
        message: successMessage,
      })
      setPdfFile(null)
      // Reset file input
      const fileInput = document.getElementById('pdf-file-input') as HTMLInputElement
      if (fileInput) fileInput.value = ''
      
      // Reload the PDF list
      loadUploadedPdfs()
    } catch (error: any) {
      setPdfStatus({
        type: 'error',
        message: error.message || 'Failed to upload PDF file',
      })
    } finally {
      setPdfUploading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Admin Panel</h1>
          <p className="text-gray-600 mt-2">
            Upload CSV files to Azure AI Search and PDF files to Azure File Share
          </p>
        </div>

        <div className="space-y-6">
          {/* CSV Upload Section */}
          <Card className="p-6">
            <div className="flex items-center gap-2 mb-4">
              <FileText className="w-6 h-6 text-blue-600" />
              <h2 className="text-xl font-semibold text-gray-900">Upload CSV to Azure AI Search</h2>
            </div>

            <div className="space-y-4">
              <div>
                <label htmlFor="csv-type-select" className="block text-sm font-medium text-gray-700 mb-2">
                  Select Data Type
                </label>
                <select
                  id="csv-type-select"
                  value={selectedCsvType}
                  onChange={(e) => setSelectedCsvType(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  disabled={csvUploading}
                >
                  <option value="">-- Select CSV Type --</option>
                  {CSV_FILES.map((csv) => (
                    <option key={csv.value} value={csv.value}>
                      {csv.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="csv-file-input" className="block text-sm font-medium text-gray-700 mb-2">
                  Choose CSV File
                </label>
                <input
                  id="csv-file-input"
                  type="file"
                  accept=".csv"
                  onChange={(e) => setCsvFile(e.target.files?.[0] || null)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                  disabled={csvUploading}
                />
              </div>

              {csvFile && (
                <div className="text-sm text-gray-600">
                  Selected: <span className="font-medium">{csvFile.name}</span> ({(csvFile.size / 1024).toFixed(2)} KB)
                </div>
              )}

              {csvStatus && (
                <div
                  className={`flex items-start gap-2 p-4 rounded-lg ${
                    csvStatus.type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'
                  }`}
                >
                  {csvStatus.type === 'success' ? (
                    <CheckCircle2 className="w-5 h-5 mt-0.5 flex-shrink-0" />
                  ) : (
                    <AlertCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />
                  )}
                  <span className="text-sm">{csvStatus.message}</span>
                </div>
              )}

              <Button
                onClick={handleCsvUpload}
                disabled={!selectedCsvType || !csvFile || csvUploading}
                className="w-full"
              >
                {csvUploading ? (
                  <>
                    <span className="animate-spin mr-2">⏳</span>
                    Uploading...
                  </>
                ) : (
                  <>
                    <Upload className="w-4 h-4 mr-2" />
                    Upload CSV to Azure AI Search
                  </>
                )}
              </Button>
            </div>
          </Card>

          {/* PDF Upload Section */}
          <Card className="p-6">
            <div className="flex items-center gap-2 mb-4">
              <FileText className="w-6 h-6 text-purple-600" />
              <h2 className="text-xl font-semibold text-gray-900">Upload PDF to Azure File Share</h2>
            </div>

            <div className="space-y-4">
              <div>
                <label htmlFor="pdf-file-input" className="block text-sm font-medium text-gray-700 mb-2">
                  Choose PDF File
                </label>
                <input
                  id="pdf-file-input"
                  type="file"
                  accept=".pdf"
                  onChange={(e) => setPdfFile(e.target.files?.[0] || null)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-purple-50 file:text-purple-700 hover:file:bg-purple-100"
                  disabled={pdfUploading}
                />
              </div>

              {pdfFile && (
                <div className="text-sm text-gray-600">
                  Selected: <span className="font-medium">{pdfFile.name}</span> ({(pdfFile.size / 1024).toFixed(2)} KB)
                </div>
              )}

              {pdfStatus && (
                <div
                  className={`flex items-start gap-2 p-4 rounded-lg ${
                    pdfStatus.type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'
                  }`}
                >
                  {pdfStatus.type === 'success' ? (
                    <CheckCircle2 className="w-5 h-5 mt-0.5 flex-shrink-0" />
                  ) : (
                    <AlertCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />
                  )}
                  <span className="text-sm">{pdfStatus.message}</span>
                </div>
              )}

              <Button
                onClick={handlePdfUpload}
                disabled={!pdfFile || pdfUploading}
                className="w-full bg-purple-600 hover:bg-purple-700"
              >
                {pdfUploading ? (
                  <>
                    <span className="animate-spin mr-2">⏳</span>
                    Uploading...
                  </>
                ) : (
                  <>
                    <Upload className="w-4 h-4 mr-2" />
                    Upload PDF to Azure File Share
                  </>
                )}
              </Button>
            </div>
          </Card>

          {/* Uploaded PDFs List Section */}
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <FileText className="w-6 h-6 text-green-600" />
                <h2 className="text-xl font-semibold text-gray-900">Uploaded PDFs</h2>
              </div>
              <Button
                onClick={loadUploadedPdfs}
                disabled={loadingPdfs}
                variant="outline"
                size="sm"
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${loadingPdfs ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </div>

            {loadingPdfs ? (
              <div className="text-center py-8 text-gray-500">
                <div className="animate-spin inline-block w-8 h-8 border-4 border-gray-300 border-t-blue-600 rounded-full"></div>
                <p className="mt-2">Loading PDFs...</p>
              </div>
            ) : uploadedPdfs.length > 0 ? (
              <div className="space-y-2">
                <p className="text-sm text-gray-600 mb-3">
                  Location: <span className="font-mono font-medium">ecommerce-pdfs/pdfs/</span>
                </p>
                <div className="max-h-96 overflow-y-auto">
                  <ul className="space-y-2">
                    {uploadedPdfs.map((fileName, index) => (
                      <li
                        key={index}
                        className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                      >
                        <FileText className="w-5 h-5 text-purple-600 flex-shrink-0" />
                        <span className="font-medium text-gray-900 flex-1">{fileName}</span>
                        <span className="text-xs text-gray-500 bg-white px-2 py-1 rounded">PDF</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <FileText className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                <p>No PDFs uploaded yet</p>
                <p className="text-sm mt-1">Upload a PDF file to get started</p>
              </div>
            )}
          </Card>

          {/* Azure AI Search Indexed Documents Section */}
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Database className="w-6 h-6 text-blue-600" />
                <h2 className="text-xl font-semibold text-gray-900">Azure AI Search Index</h2>
              </div>
              <Button
                onClick={loadIndexedDocuments}
                disabled={loadingDocuments}
                variant="outline"
                size="sm"
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${loadingDocuments ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </div>

            {loadingDocuments ? (
              <div className="text-center py-8 text-gray-500">
                <div className="animate-spin inline-block w-8 h-8 border-4 border-gray-300 border-t-blue-600 rounded-full"></div>
                <p className="mt-2">Loading indexed documents...</p>
              </div>
            ) : indexedDocuments.length > 0 ? (
              <div className="space-y-3">
                <p className="text-sm text-gray-600 mb-3">
                  Index: <span className="font-mono font-medium">ecommerce-documents-index</span>
                  <span className="ml-4 text-gray-500">({indexedDocuments.length} documents)</span>
                </p>
                <div className="space-y-3 max-h-[600px] overflow-y-auto">
                  {indexedDocuments.map((doc: any) => (
                    <div
                      key={doc.id}
                      className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors bg-white"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center gap-2 flex-wrap">
                          <Search className="w-5 h-5 text-blue-600 flex-shrink-0" />
                          <h3 className="font-semibold text-gray-900">{doc.fileName || 'Untitled'}</h3>
                          <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                            {doc.fileType?.toUpperCase() || 'DOC'}
                          </span>
                          {doc.chunkIndex !== undefined && (
                            <span className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded">
                              Chunk {doc.chunkIndex + 1}/{doc.totalChunks}
                            </span>
                          )}
                        </div>
                        <Button
                          onClick={() => setSelectedDocument(selectedDocument?.id === doc.id ? null : doc)}
                          variant="ghost"
                          size="sm"
                          className="text-xs"
                        >
                          {selectedDocument?.id === doc.id ? 'Hide Details' : 'View Details'}
                        </Button>
                      </div>

                      <div className="grid grid-cols-2 gap-2 text-sm mb-3">
                        <div>
                          <span className="text-gray-500">Document ID:</span>
                          <p className="font-mono text-xs break-all">{doc.id}</p>
                        </div>
                        <div>
                          <span className="text-gray-500">Upload Date:</span>
                          <p className="text-gray-900">
                            {doc.uploadDate ? new Date(doc.uploadDate).toLocaleString() : 'N/A'}
                          </p>
                        </div>
                        {doc.numPages && (
                          <div>
                            <span className="text-gray-500">Pages:</span>
                            <p className="text-gray-900">{doc.numPages}</p>
                          </div>
                        )}
                        {doc.estimatedTokens && (
                          <div>
                            <span className="text-gray-500">Est. Tokens:</span>
                            <p className="text-gray-900">{doc.estimatedTokens}</p>
                          </div>
                        )}
                        {doc.fileSize && (
                          <div>
                            <span className="text-gray-500">File Size:</span>
                            <p className="text-gray-900">{(doc.fileSize / 1024).toFixed(2)} KB</p>
                          </div>
                        )}
                        {doc.fileUrl && (
                          <div className="col-span-2">
                            <span className="text-gray-500">File URL:</span>
                            <p className="font-mono text-xs break-all text-blue-600">
                              <a href={doc.fileUrl} target="_blank" rel="noopener noreferrer" className="hover:underline">
                                {doc.fileUrl}
                              </a>
                            </p>
                          </div>
                        )}
                      </div>

                      {selectedDocument?.id === doc.id && (
                        <div className="mt-3 pt-3 border-t border-gray-200">
                          <div className="mb-2">
                            <span className="text-sm font-medium text-gray-700">Indexed Content:</span>
                          </div>
                          <div className="bg-gray-50 p-3 rounded text-sm text-gray-800 max-h-64 overflow-y-auto">
                            {doc.content || 'No content available'}
                          </div>
                          {doc.contentVector && (
                            <div className="mt-2">
                              <span className="text-xs text-green-600 flex items-center gap-1">
                                <CheckCircle2 className="w-3 h-3" />
                                Vector embeddings generated ({doc.contentVector.length} dimensions)
                              </span>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Database className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                <p>No documents indexed yet</p>
                <p className="text-sm mt-1">Upload a PDF to index it in Azure AI Search</p>
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  )
}
