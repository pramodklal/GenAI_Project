import { NextResponse } from 'next/server'
import { searchProducts } from '@/lib/azure/search'
import { listProducts, getProduct } from '@/lib/azure/tables'

// GET /api/products - List all products or search
export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url)
    const query = searchParams.get('q')
    const category = searchParams.get('category')
    const limit = parseInt(searchParams.get('limit') || '20')

    if (query) {
      // Use Azure AI Search for text search
      const filter = category ? `category eq '${category}'` : undefined
      const result = await searchProducts(query, { top: limit, filter })
      
      return NextResponse.json({
        products: result.products,
        count: result.count,
      })
    } else {
      // List products from Table Storage
      const filter = category ? `category eq '${category}'` : undefined
      const products = await listProducts({ top: limit, filter })
      
      return NextResponse.json({
        products,
        count: products.length,
      })
    }
  } catch (error) {
    console.error('Products API Error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch products' },
      { status: 500 }
    )
  }
}

// GET /api/products/[id] - Get single product
export async function getProductById(productId: string) {
  try {
    const product = await getProduct(productId)
    
    if (!product) {
      return NextResponse.json(
        { error: 'Product not found' },
        { status: 404 }
      )
    }

    return NextResponse.json(product)
  } catch (error) {
    console.error('Get Product Error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch product' },
      { status: 500 }
    )
  }
}
