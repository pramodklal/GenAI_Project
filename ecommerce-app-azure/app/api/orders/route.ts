import { NextResponse } from 'next/server'
import { listOrders, getOrder, createOrder, updateOrder } from '@/lib/azure/tables'
import { v4 as uuidv4 } from 'uuid'

// GET /api/orders - List orders (optionally filter by customer)
export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url)
    const customerId = searchParams.get('customer_id')

    const orders = await listOrders(customerId || undefined)
    
    return NextResponse.json({
      orders,
      count: orders.length,
    })
  } catch (error) {
    console.error('Orders API Error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch orders' },
      { status: 500 }
    )
  }
}

// POST /api/orders - Create new order
export async function POST(request: Request) {
  try {
    const body = await request.json()

    const orderId = `ORD-${new Date().getFullYear()}-${Math.floor(Math.random() * 1000).toString().padStart(3, '0')}`

    const order = {
      order_id: orderId,
      customer_id: body.customer_id,
      order_date: new Date().toISOString(),
      status: 'pending',
      total_amount: body.total_amount,
      items: JSON.stringify(body.items), // Store as JSON string
      shipping_address: JSON.stringify(body.shipping_address),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }

    await createOrder(order)

    return NextResponse.json(
      { order, message: 'Order created successfully' },
      { status: 201 }
    )
  } catch (error) {
    console.error('Create Order Error:', error)
    return NextResponse.json(
      { error: 'Failed to create order' },
      { status: 500 }
    )
  }
}

// PATCH /api/orders/[id] - Update order
export async function PATCH(request: Request) {
  try {
    const { searchParams } = new URL(request.url)
    const orderId = searchParams.get('id')

    if (!orderId) {
      return NextResponse.json(
        { error: 'Order ID is required' },
        { status: 400 }
      )
    }

    const body = await request.json()
    const updates = {
      ...body,
      updated_at: new Date().toISOString(),
    }

    await updateOrder(orderId, updates)

    return NextResponse.json({
      message: 'Order updated successfully',
    })
  } catch (error) {
    console.error('Update Order Error:', error)
    return NextResponse.json(
      { error: 'Failed to update order' },
      { status: 500 }
    )
  }
}
