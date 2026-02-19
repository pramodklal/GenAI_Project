import { NextResponse } from 'next/server'
import { getSearchClient, INDEXES } from '@/lib/azure/search'

export async function GET() {
  try {
    // Get pending orders count from Azure AI Search
    const ordersClient = getSearchClient(INDEXES.ORDERS)
    const ordersResults = await ordersClient.search('*', {
      filter: "status eq 'Pending' or status eq 'Processing' or status eq 'pending' or status eq 'processing'",
      top: 0,
      includeTotalCount: true,
    })
    const pendingOrders = ordersResults.count || 0

    // Get low stock products (quantity_available < 20)
    const inventoryClient = getSearchClient(INDEXES.INVENTORY)
    const inventoryResults = await inventoryClient.search('*', {
      filter: 'quantity_available lt 20',
      top: 0,
      includeTotalCount: true,
    })
    const lowStockProducts = inventoryResults.count || 0

    // Get new customers from last 30 days
    const thirtyDaysAgo = new Date()
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30)
    const threshold = thirtyDaysAgo.toISOString().split('T')[0] // Format as YYYY-MM-DD

    const customersClient = getSearchClient(INDEXES.CUSTOMERS)
    const customersResults = await customersClient.search('*', {
      filter: `created_at ge '${threshold}'`,
      top: 0,
      includeTotalCount: true,
    })
    const newCustomers = customersResults.count || 0

    // Get recent returns count (last 7 days)
    const sevenDaysAgo = new Date()
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7)
    const returnThreshold = sevenDaysAgo.toISOString().split('T')[0] // Format as YYYY-MM-DD

    const returnsClient = getSearchClient(INDEXES.RETURNS)
    const returnsResults = await returnsClient.search('*', {
      filter: `return_date ge '${returnThreshold}'`,
      top: 0,
      includeTotalCount: true,
    })
    const recentReturns = returnsResults.count || 0

    return NextResponse.json({
      pendingOrders,
      lowStockProducts,
      newCustomers,
      recentReviews: recentReturns, // Using returns as a proxy for reviews
    })
  } catch (error) {
    console.error('Dashboard Stats Error:', error)
    return NextResponse.json(
      {
        pendingOrders: 0,
        lowStockProducts: 0,
        newCustomers: 0,
        recentReviews: 0,
      },
      { status: 200 }
    )
  }
}
