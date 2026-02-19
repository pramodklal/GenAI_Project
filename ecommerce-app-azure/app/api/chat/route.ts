import { NextResponse } from 'next/server'
import { generateChatCompletion } from '@/lib/azure/openai'
import { vectorSearch, getSearchClient, INDEXES } from '@/lib/azure/search'

export async function POST(request: Request) {
  try {
    const { message } = await request.json()

    if (!message || typeof message !== 'string') {
      return NextResponse.json(
        { error: 'Message is required' },
        { status: 400 }
      )
    }

    // Check if query is about policies - use vector search on knowledge base
    const policyKeywords = ['policy', 'warranty', 'exchange', 'shipping', 'faq', 'guide']
    const isPolicyQuery = policyKeywords.some(keyword => 
      message.toLowerCase().includes(keyword)
    )

    let contextInfo = ''

    if (isPolicyQuery) {
      try {
        // Try vector search first (requires embeddings deployment)
        const policyDocs = await vectorSearch(message, { top: 3 })
        contextInfo = policyDocs
          .map(doc => doc.content)
          .join('\n\n')
        console.log('Policy context: Using vector search')
      } catch (error) {
        console.log('Vector search failed, falling back to keyword search:', error.message)
        // Fallback to keyword search if embeddings aren't available
        try {
          const documentsClient = getSearchClient(INDEXES.DOCUMENTS)
          const docResults = await documentsClient.search(message, {
            top: 3,
            searchMode: 'any',
          })
          
          const docs = []
          for await (const result of docResults.results) {
            docs.push(result.document)
          }
          
          contextInfo = docs
            .map(doc => doc.content || doc.text || JSON.stringify(doc))
            .join('\n\n')
          console.log('Policy context: Using keyword search fallback')
        } catch (fallbackError) {
          console.error('Keyword search also failed:', fallbackError)
          contextInfo = 'Unable to retrieve policy documents at this time.'
        }
      }
    }

    // Check if query is about orders
    const orderKeywords = ['order', 'track', 'status', 'delivery', 'pending']
    const isOrderQuery = orderKeywords.some(keyword => 
      message.toLowerCase().includes(keyword)
    )

    if (isOrderQuery) {
      // Extract order ID if present (format: ORD-XXXX-XXX)
      const orderIdMatch = message.match(/ORD-\d{4}-\d{3}/i)
      if (orderIdMatch) {
        // Search for specific order by ID
        const ordersClient = getSearchClient(INDEXES.ORDERS)
        const orderResults = await ordersClient.search('*', {
          filter: `order_id eq '${orderIdMatch[0]}'`,
          top: 1,
        })
        
        for await (const result of orderResults.results) {
          contextInfo += `\n\nOrder Information:\n${JSON.stringify(result.document, null, 2)}`
        }
      } else if (message.toLowerCase().includes('pending')) {
        // Get pending orders
        const ordersClient = getSearchClient(INDEXES.ORDERS)
        const ordersResults = await ordersClient.search('*', {
          filter: "status eq 'Pending' or status eq 'Processing'",
          top: 10,
          includeTotalCount: true,
        })
        
        const orders = []
        for await (const result of ordersResults.results) {
          orders.push(result.document)
        }
        
        contextInfo += `\n\nPending Orders (${ordersResults.count || 0} total):\n${JSON.stringify(orders, null, 2)}`
      }
    }

    // Check if query is about customers
    const customerKeywords = ['customer', 'email', 'phone', 'address', 'contact', 'name', 'state', 'city']
    const isCustomerQuery = customerKeywords.some(keyword => 
      message.toLowerCase().includes(keyword)
    )

    if (isCustomerQuery) {
      const customersClient = getSearchClient(INDEXES.CUSTOMERS)
      
      // Extract customer ID if present (format: CUST-XXX)
      const customerIdMatch = message.match(/CUST-\d{3}/i)
      if (customerIdMatch) {
        const customerResults = await customersClient.search('*', {
          filter: `customer_id eq '${customerIdMatch[0]}'`,
          top: 1,
        })
        
        for await (const result of customerResults.results) {
          contextInfo += `\n\nCustomer Information:\n${JSON.stringify(result.document, null, 2)}`
        }
      } else {
        // Check for state queries (e.g., "address_state is nv" or "state nv" or "in Nevada")
        const stateMatch = message.match(/(?:address_state|state)\s+(?:is\s+)?([a-z]{2})\b/i) || 
                          message.match(/\b(CA|NY|TX|FL|NV|WA|OR|IL|PA|OH)\b/i)
        
        if (stateMatch) {
          const state = stateMatch[1].toUpperCase()
          const customerResults = await customersClient.search('*', {
            filter: `address_state eq '${state}'`,
            top: 10,
            includeTotalCount: true,
          })
          
          const customers = []
          for await (const result of customerResults.results) {
            customers.push(result.document)
          }
          
          contextInfo += `\n\nCustomers in ${state} (${customerResults.count || 0} total):\n${JSON.stringify(customers, null, 2)}`
        } else {
          // General customer search
          const customerResults = await customersClient.search(message, {
            top: 5,
            searchMode: 'any',
          })
          
          const customers = []
          for await (const result of customerResults.results) {
            customers.push(result.document)
          }
          
          if (customers.length > 0) {
            contextInfo += `\n\nRelevant Customers:\n${JSON.stringify(customers, null, 2)}`
          }
        }
      }
    }

    // Check if query is about products
    const productKeywords = ['product', 'item', 'price', 'stock', 'inventory']
    const isProductQuery = productKeywords.some(keyword => 
      message.toLowerCase().includes(keyword)
    )

    if (isProductQuery) {
      // Use semantic search on products
      const productsClient = getSearchClient(INDEXES.PRODUCTS)
      const productResults = await productsClient.search(message, {
        top: 5,
        searchMode: 'any',
      })
      
      const products = []
      for await (const result of productResults.results) {
        products.push(result.document)
      }
      
      if (products.length > 0) {
        contextInfo += `\n\nRelevant Products:\n${JSON.stringify(products, null, 2)}`
      }
    }

    // Check if query is about returns
    const returnKeywords = ['return', 'refund', 'rma']
    const isReturnQuery = returnKeywords.some(keyword => 
      message.toLowerCase().includes(keyword)
    )

    if (isReturnQuery && !isPolicyQuery) {
      // Search returns data
      const returnsClient = getSearchClient(INDEXES.RETURNS)
      const returnResults = await returnsClient.search(message, {
        top: 5,
      })
      
      const returns = []
      for await (const result of returnResults.results) {
        returns.push(result.document)
      }
      
      if (returns.length > 0) {
        contextInfo += `\n\nReturn Information:\n${JSON.stringify(returns, null, 2)}`
      }
    }

    // Debug: Log context being sent to GPT-4o
    console.log('=== CHATBOT DEBUG ===')
    console.log('User Question:', message)
    console.log('Context Retrieved:', contextInfo ? 'YES' : 'NO')
    if (contextInfo) {
      console.log('Context Length:', contextInfo.length, 'characters')
      console.log('Context Preview:', contextInfo.substring(0, 200) + '...')
    }

    // System prompt for the AI assistant
    const systemPrompt = `You are an intelligent e-commerce AI assistant for an online retail platform. 
You help customers with:
- Order tracking and status updates
- Return and refund requests
- Product information and recommendations
- Shipping and delivery questions
- Policy clarifications (return policy, warranty, etc.)

Use the following context information when available:
${contextInfo}

Be helpful, professional, and concise. If you don't have specific information, guide the user on how to get it.
Always prioritize customer satisfaction and provide actionable next steps.`

    // Generate response using Azure OpenAI
    const completion = await generateChatCompletion([
      { role: 'system', content: systemPrompt },
      { role: 'user', content: message },
    ], {
      temperature: 0.7,
      maxTokens: 800,
    })

    const response = completion.choices[0]?.message?.content || 
      'I apologize, but I could not process your request at this time.'

    return NextResponse.json({
      response,
      timestamp: new Date().toISOString(),
    })
  } catch (error) {
    console.error('Chat API Error:', error)
    return NextResponse.json(
      { error: 'Failed to process chat message' },
      { status: 500 }
    )
  }
}
