import { NextResponse } from 'next/server'
import { listReturns, getReturn, createReturn } from '@/lib/azure/tables'
import { getOrder } from '@/lib/azure/tables'
import { generateChatCompletion } from '@/lib/azure/openai'
import { vectorSearch } from '@/lib/azure/search'

// GET /api/returns - List returns
export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url)
    const orderId = searchParams.get('order_id')

    const returns = await listReturns(orderId || undefined)
    
    return NextResponse.json({
      returns,
      count: returns.length,
    })
  } catch (error) {
    console.error('Returns API Error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch returns' },
      { status: 500 }
    )
  }
}

// POST /api/returns - Create return request with AI eligibility check
export async function POST(request: Request) {
  try {
    const body = await request.json()
    const { order_id, reason, items } = body

    if (!order_id || !reason) {
      return NextResponse.json(
        { error: 'Order ID and reason are required' },
        { status: 400 }
      )
    }

    // Get order details
    const order = await getOrder(order_id)
    if (!order) {
      return NextResponse.json(
        { error: 'Order not found' },
        { status: 404 }
      )
    }

    // Check return eligibility using AI
    const eligibilityCheck = await checkReturnEligibility(order, reason)

    if (!eligibilityCheck.eligible) {
      return NextResponse.json({
        eligible: false,
        reason: eligibilityCheck.reason,
        message: eligibilityCheck.message,
      })
    }

    // Create return record
    const returnId = `RET-${new Date().getFullYear()}-${Math.floor(Math.random() * 10000).toString().padStart(4, '0')}`

    const returnData = {
      return_id: returnId,
      order_id,
      customer_id: order.customer_id,
      status: 'pending',
      reason,
      items: JSON.stringify(items || []),
      refund_amount: eligibilityCheck.refundAmount,
      restocking_fee: eligibilityCheck.restockingFee || 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }

    await createReturn(returnData)

    return NextResponse.json({
      eligible: true,
      return: returnData,
      message: 'Return request created successfully',
      rma_number: returnId,
    }, { status: 201 })
  } catch (error) {
    console.error('Create Return Error:', error)
    return NextResponse.json(
      { error: 'Failed to create return' },
      { status: 500 }
    )
  }
}

/**
 * Check return eligibility using Azure OpenAI and policy documents
 */
async function checkReturnEligibility(order: any, reason: string) {
  try {
    // Get return policy from vector search
    const policyDocs = await vectorSearch('return policy eligibility requirements', { top: 2 })
    const policyContext = policyDocs.map(doc => doc.content).join('\n\n')

    // Check basic eligibility criteria
    const orderDate = new Date(order.order_date)
    const deliveryDate = order.delivery_date ? new Date(order.delivery_date) : null
    const now = new Date()

    const daysSinceDelivery = deliveryDate 
      ? Math.floor((now.getTime() - deliveryDate.getTime()) / (1000 * 60 * 60 * 24))
      : null

    // Prepare context for AI
    const contextPrompt = `Analyze this return request for eligibility:

Order Information:
- Order ID: ${order.order_id || order.rowKey}
- Order Date: ${order.order_date}
- Delivery Date: ${order.delivery_date || 'Not delivered'}
- Days Since Delivery: ${daysSinceDelivery !== null ? daysSinceDelivery : 'N/A'}
- Order Status: ${order.status}
- Total Amount: $${order.total_amount}

Return Request:
- Reason: ${reason}

Return Policy:
${policyContext}

Determine:
1. Is this return eligible? (yes/no)
2. If not eligible, why?
3. If eligible, what is the refund amount? (consider restocking fees if applicable)
4. Any restocking fee amount?

Respond in JSON format:
{
  "eligible": true/false,
  "reason": "brief reason",
  "message": "customer-friendly explanation",
  "refundAmount": number,
  "restockingFee": number
}`

    const completion = await generateChatCompletion([
      { role: 'system', content: 'You are a return policy expert. Analyze return requests and provide eligibility decisions in JSON format.' },
      { role: 'user', content: contextPrompt },
    ], {
      temperature: 0.3,
      maxTokens: 500,
    })

    const responseText = completion.choices[0]?.message?.content || '{}'
    
    // Extract JSON from response
    const jsonMatch = responseText.match(/\{[\s\S]*\}/)
    if (jsonMatch) {
      const result = JSON.parse(jsonMatch[0])
      return result
    }

    // Fallback to basic check
    return {
      eligible: daysSinceDelivery !== null && daysSinceDelivery <= 30 && order.status === 'delivered',
      reason: daysSinceDelivery && daysSinceDelivery > 30 ? 'Return window expired' : 'Order not delivered',
      message: 'Based on standard policy, this return is ' + (daysSinceDelivery && daysSinceDelivery <= 30 ? 'eligible' : 'not eligible'),
      refundAmount: order.total_amount || 0,
      restockingFee: 0,
    }
  } catch (error) {
    console.error('Eligibility Check Error:', error)
    // Default to not eligible on error
    return {
      eligible: false,
      reason: 'Error processing request',
      message: 'Unable to process return eligibility at this time',
      refundAmount: 0,
      restockingFee: 0,
    }
  }
}
