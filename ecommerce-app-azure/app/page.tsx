'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { AIChatWidget } from '@/components/AIChatWidget'
import { 
  ShoppingCart, 
  Package, 
  Users, 
  TrendingUp,
  Star,
  AlertCircle,
  PackageX,
  ArrowRight
} from 'lucide-react'
import Link from 'next/link'

interface DashboardStats {
  pendingOrders: number
  lowStockProducts: number
  newCustomers: number
  recentReviews: number
}

export default function HomePage() {
  const [stats, setStats] = useState<DashboardStats>({
    pendingOrders: 0,
    lowStockProducts: 0,
    newCustomers: 0,
    recentReviews: 0
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Fetch dashboard stats
    const fetchStats = async () => {
      try {
        const response = await fetch('/api/dashboard/stats')
        if (response.ok) {
          const data = await response.json()
          setStats(data)
        }
      } catch (error) {
        console.error('Failed to fetch stats:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <ShoppingCart className="h-8 w-8 text-indigo-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  E-Commerce Azure AI
                </h1>
                <p className="text-sm text-gray-600">
                  Powered by Azure OpenAI & Azure AI Search
                </p>
              </div>
            </div>
            <Badge variant="outline" className="text-green-600 border-green-600">
              System Online
            </Badge>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium text-gray-600">
                  Pending Orders
                </CardTitle>
                <ShoppingCart className="h-5 w-5 text-blue-600" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-gray-900">
                {loading ? '...' : stats.pendingOrders}
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Awaiting processing
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium text-gray-600">
                  Low Stock Items
                </CardTitle>
                <Package className="h-5 w-5 text-orange-600" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-orange-600">
                {loading ? '...' : stats.lowStockProducts}
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Need restocking
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium text-gray-600">
                  New Customers
                </CardTitle>
                <Users className="h-5 w-5 text-purple-600" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-purple-600">
                {loading ? '...' : stats.newCustomers}
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Last 30 days
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium text-gray-600">
                  Recent Returns
                </CardTitle>
                <Star className="h-5 w-5 text-yellow-600" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-yellow-600">
                {loading ? '...' : stats.recentReviews}
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Last 7 days
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Tabs */}
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 lg:w-[600px]">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="orders">Orders</TabsTrigger>
            <TabsTrigger value="inventory">Inventory</TabsTrigger>
            <TabsTrigger value="customers">Customers</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Welcome to Azure E-Commerce AI</CardTitle>
                <CardDescription>
                  Intelligent order management powered by Azure OpenAI, Azure AI Search, and Azure File Share
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="border rounded-lg p-4">
                    <div className="flex items-start gap-3">
                      <ShoppingCart className="h-5 w-5 text-blue-600 mt-1" />
                      <div>
                        <h3 className="font-semibold mb-2">Order Management</h3>
                        <p className="text-sm text-gray-600">
                          Track orders stored in Azure Table Storage with AI-powered insights.
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="border rounded-lg p-4">
                    <div className="flex items-start gap-3">
                      <Package className="h-5 w-5 text-purple-600 mt-1" />
                      <div>
                        <h3 className="font-semibold mb-2">Azure AI Search</h3>
                        <p className="text-sm text-gray-600">
                          Search products with vector embeddings (text-embedding-3-large).
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="border rounded-lg p-4">
                    <div className="flex items-start gap-3">
                      <Users className="h-5 w-5 text-indigo-600 mt-1" />
                      <div>
                        <h3 className="font-semibold mb-2">GPT-4 Chat Assistant</h3>
                        <p className="text-sm text-gray-600">
                          Azure OpenAI GPT-4 for intelligent customer support.
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="border rounded-lg p-4 bg-gradient-to-br from-blue-50 to-purple-50 border-blue-200">
                    <div className="flex items-start gap-3">
                      <PackageX className="h-5 w-5 text-blue-600 mt-1" />
                      <div className="flex-1">
                        <h3 className="font-semibold mb-2 text-blue-900">Returns with RAG</h3>
                        <p className="text-sm text-gray-700 mb-3">
                          Policy documents in Azure File Share + vector search for returns.
                        </p>
                        <Link href="/returns">
                          <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
                            Go to Returns Portal
                            <ArrowRight className="h-3 w-3 ml-2" />
                          </Button>
                        </Link>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="border-t pt-4 mt-6">
                  <h3 className="font-semibold mb-3">Try asking the Azure AI:</h3>
                  <div className="space-y-2">
                    <div className="text-sm text-gray-700 bg-gray-50 p-3 rounded">
                      💬 "Show me all pending orders"
                    </div>
                    <div className="text-sm text-gray-700 bg-gray-50 p-3 rounded">
                      💬 "Which products are low in stock?"
                    </div>
                    <div className="text-sm text-gray-700 bg-gray-50 p-3 rounded">
                      💬 "Check return eligibility for order ORD-2024-001"
                    </div>
                    <div className="text-sm text-gray-700 bg-gray-50 p-3 rounded">
                      💬 "What's the return policy for defective items?"
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="orders">
            <Card>
              <CardHeader>
                <CardTitle>Order Management</CardTitle>
                <CardDescription>
                  Orders stored in Azure Table Storage
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Use the AI chat to query order information from Azure Table Storage.
                </p>
                <div className="mt-4 space-y-2">
                  <Button variant="outline" className="w-full justify-start">
                    <ShoppingCart className="mr-2 h-4 w-4" />
                    View All Orders
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    <TrendingUp className="mr-2 h-4 w-4" />
                    Sales Trends
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="inventory">
            <Card>
              <CardHeader>
                <CardTitle>Inventory with Azure AI Search</CardTitle>
                <CardDescription>
                  Search products using vector embeddings
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Product catalog indexed in Azure AI Search with text-embedding-3-large.
                </p>
                <div className="mt-4 space-y-2">
                  <Button variant="outline" className="w-full justify-start">
                    <Package className="mr-2 h-4 w-4" />
                    Search Products
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    <AlertCircle className="mr-2 h-4 w-4" />
                    Low Stock Alerts
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="customers">
            <Card>
              <CardHeader>
                <CardTitle>Customer Management</CardTitle>
                <CardDescription>
                  Customer data in Azure Table Storage
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  View customer profiles and purchase history from Azure tables.
                </p>
                <div className="mt-4 space-y-2">
                  <Button variant="outline" className="w-full justify-start">
                    <Users className="mr-2 h-4 w-4" />
                    Customer List
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    <Star className="mr-2 h-4 w-4" />
                    Recent Returns
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>

      {/* AI Chat Widget */}
      <AIChatWidget />
    </div>
  )
}
