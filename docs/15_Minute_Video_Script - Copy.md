# 15-Minute YouTube Video Script
## Hybrid RAG E-Commerce Intelligence System with Azure OpenAI

---

## 🎬 VIDEO TIMELINE

| Time | Section | Visual |
|------|---------|--------|
| 0:00-0:45 | Hook & Introduction | Screen: Dashboard demo |
| 0:45-2:00 | Problem & Solution | Screen: Problem slides |
| 2:00-5:30 | Architecture Deep Dive | Screen: Architecture diagram |
| 5:30-8:30 | Technical Implementation | Screen: Code walkthrough |
| 8:30-11:30 | Live Demo | Screen: Live application |
| 11:30-13:30 | Azure Services & Cost | Screen: Azure Portal |
| 13:30-14:45 | Benefits & Use Cases | Screen: Metrics slides |
| 14:45-15:00 | Call to Action | Screen: GitHub repo |

---

## 📝 SCRIPT

### [0:00-0:45] HOOK & INTRODUCTION (45 seconds)

**[SCREEN: Show AI chat responding to query in real-time]**

> "What if you could ask your e-commerce system questions in plain English and get instant, accurate answers? Not from a basic chatbot, but from an AI that actually understands your data—your orders, products, policies, and inventory—all in one intelligent interface?"

**[SCREEN: Show multiple query examples appearing]**

> "In this video, I'll show you how I built a production-ready Hybrid RAG system using Azure OpenAI, GPT-4o, and Azure AI Search that responds in under 2 seconds, costs just 2 cents per query, and achieves 99% accuracy."

**[SCREEN: Your face/intro slide]**

> "I'm [Your Name], and by the end of this video, you'll understand exactly how this works and how to build it yourself. Let's dive in."

---

### [0:45-2:00] PROBLEM & SOLUTION (1 min 15 sec)

**[SCREEN: Problem statement slides]**

> "Here's the problem most e-commerce companies face:"

**[SCREEN: Show fragmented systems diagram]**

> "Data is scattered everywhere—products in catalogs, orders in databases, policies in PDF documents, inventory in spreadsheets. Customer service teams waste hours searching across multiple systems. Traditional search only does keyword matching, missing the context. And business users need technical teams to write SQL queries for simple questions."

**[SCREEN: Transition to solution]**

> "The solution? A Hybrid RAG system—that's Retrieval-Augmented Generation. Think of it as giving GPT-4 a photographic memory of your business data."

**[SCREEN: Show simple RAG diagram]**

> "Instead of making AI guess answers, we retrieve relevant data first, then generate intelligent responses. The 'hybrid' part means we use three different search strategies depending on the question—vector search for semantic understanding, filter search for precise lookups, and full-text search for keyword queries."

---

### [2:00-5:30] ARCHITECTURE DEEP DIVE (3 min 30 sec)

**[SCREEN: Show full architecture diagram]**

> "Let's break down the architecture. At the top, we have a Next.js 16 frontend with a real-time chat widget. When a user asks a question, it hits our API route that analyzes the query and decides which search strategy to use."

#### Three Search Strategies

**[SCREEN: Highlight Vector Search section]**

> "Strategy one: Vector Search. This is for semantic questions like 'show me comfortable running shoes' or 'what's your return policy?' We convert the question into a 3072-dimensional vector using Azure's text-embedding-3-large model, then search our documents index using HNSW algorithm to find semantically similar content. This is why it understands meaning, not just keywords."

**[SCREEN: Show vector visualization]**

> "For example, asking 'warranty information' will find relevant policy documents even if the word 'warranty' isn't explicitly in your question."

**[SCREEN: Highlight Filter Search section]**

> "Strategy two: Filter Search. This is for precise lookups—'show orders for customer C123' or 'track order #45678'. We extract the identifier and apply an exact filter. This returns results in under 200 milliseconds with 100% precision."

**[SCREEN: Highlight Full-Text Search section]**

> "Strategy three: Full-Text Search. This is for product browsing—'find wireless headphones under $100'. We use Lucene-based keyword search with facets for category, price range, and availability. This gives users that familiar e-commerce search experience with filtering."

**[SCREEN: Show Azure AI Search indexes]**

> "All three strategies query Azure AI Search, which manages six specialized indexes: documents-index with 850 PDFs for vector search, products-index with 500 SKUs, orders-index with 10,000 orders, customers-index, inventory-index for stock levels, and returns-index for return tracking."

**[SCREEN: Show Azure OpenAI section]**

> "After retrieving relevant data, we send it to Azure OpenAI's GPT-4o model. We're using the 2024-11-20 version with a 128K context window. The AI reads the retrieved context and generates a natural, accurate response that streams back to the user in real-time."

---

### [5:30-8:30] TECHNICAL IMPLEMENTATION (3 minutes)

**[SCREEN: Open VS Code - show project structure]**

> "Now let's look at the actual implementation. Here's the Next.js project structure. The API route is in app/api/chat/route.ts."

**[SCREEN: Open route.ts file]**

> "Here's the main chat endpoint. First, we detect the search strategy using simple keyword matching:"

```typescript
function detectSearchStrategy(query: string) {
  // Check for customer/order IDs → Filter Search
  if (/customer\s+[a-z0-9]+|order\s+#?\w+/i.test(query)) {
    return 'filter';
  }
  // Check for product search → Full-Text Search
  if (query.includes('find') || query.includes('under $')) {
    return 'fulltext';
  }
  // Default to Vector Search
  return 'vector';
}
```

**[SCREEN: Show search implementation]**

> "For vector search, we first generate an embedding:"

```typescript
const embedding = await openai.embeddings.create({
  model: "text-embedding-3-large",
  input: query
});
```

> "Then search Azure AI Search with that vector:"

```typescript
const results = await searchClient.search("", {
  vectorQueries: [{
    kind: 'vector',
    vector: embedding.data[0].embedding,
    kNearestNeighbors: 5,
    fields: ['contentVector']
  }]
});
```

**[SCREEN: Show prompt building]**

> "Once we have the relevant context, we build a structured prompt:"

```typescript
const systemPrompt = `You are an e-commerce assistant.
Here's the relevant data:
${context.map(r => r.content).join('\n\n')}

Answer the user's question based only on this data.`;
```

**[SCREEN: Show streaming response]**

> "Finally, we stream the GPT-4o response back to the client using Server-Sent Events:"

```typescript
const stream = await openai.chat.completions.create({
  model: "gpt-4o",
  messages: [{ role: "user", content: systemPrompt }],
  stream: true,
  temperature: 0.7,
  max_tokens: 1000
});

return new Response(streamToReadable(stream));
```

> "This gives users that ChatGPT-like experience where they see the response appear word by word."

---

### [8:30-11:30] LIVE DEMO (3 minutes)

**[SCREEN: Open the application at localhost:3000]**

> "Alright, let's see this in action. Here's the application running. I've got the chat widget open on the right."

#### Demo 1: Customer Order Query

**[TYPE: "Show me all orders for customer C12345"]**

> "Let's ask: 'Show me all orders for customer C12345'. Watch the response..."

**[SCREEN: Response appears streaming]**

> "Look at this—it detected the customer ID, used filter search, and found 12 orders in under 200 milliseconds. It's showing order numbers, amounts, statuses, and even tracking numbers. This query hit the orders-index directly."

#### Demo 2: Policy Question

**[TYPE: "Can I return opened electronics?"]**

> "Now a policy question: 'Can I return opened electronics?'"

**[SCREEN: Response streams in]**

> "This used vector search. It generated an embedding of my question, searched the documents-index containing 850 PDFs, found the relevant section of our return policy, and GPT-4o is now explaining it in natural language. Notice it's giving me specific conditions, what's accepted, what's not, and even the return process steps. The AI extracted all this from a 40-page PDF document."

#### Demo 3: Product Search

**[TYPE: "Find wireless headphones under $100 with noise cancellation"]**

> "One more: 'Find wireless headphones under $100 with noise cancellation'"

**[SCREEN: Results appear]**

> "Full-text search with facets. It's showing me 23 products that match, sorted by relevance. Each product has the price, rating, stock level, and key features. It even applied the price filter automatically. This is querying the products-index with category and price range facets."

**[SCREEN: Show response time in network tab]**

> "If I open the browser network tab, you can see the total response time: 1.8 seconds from query to complete response. That's embedding generation, search, and GPT-4o processing combined."

---

### [11:30-13:30] AZURE SERVICES & COST (2 minutes)

**[SCREEN: Switch to Azure Portal]**

> "Let's talk about the Azure services powering this. I'm in the Azure Portal now."

**[SCREEN: Show Azure OpenAI resource]**

> "First, Azure OpenAI Service. I've deployed two models: GPT-4o for response generation with 50,000 tokens per minute quota, and text-embedding-3-large for creating those 3072-dimensional vectors with 150,000 tokens per minute. The endpoint is in East US 2 for low latency."

**[SCREEN: Show Azure AI Search resource]**

> "Next, Azure AI Search. I'm using the Basic tier which costs $75 per month. Inside, I have six search indexes. The documents-index is vector-search enabled using HNSW algorithm for fast similarity matching. The other five indexes are for structured data with different filtering and faceting configurations."

**[SCREEN: Show Storage Account]**

> "In my Storage Account, I have an Azure File Share storing 850 PDF documents—product manuals, policies, FAQs. And Azure Table Storage holds the legacy CSV data—50,000 orders, 5,000 customers, and inventory records. Total storage: 25 gigabytes."

**[SCREEN: Show Application Insights]**

> "Application Insights tracks everything: request latency, token usage, search performance per index, and error rates. This is how I know my average response time is 1.8 seconds."

**[SCREEN: Show cost breakdown slide]**

> "Total monthly cost for 5,000 queries: Azure OpenAI runs about $44, AI Search is $75, Storage is $2, Application Insights is $11. That's $132 per month, or 2.7 cents per query. Compare that to the $2 cost of a human agent spending 5 minutes searching manually."

---

### [13:30-14:45] BENEFITS & USE CASES (1 min 15 sec)

**[SCREEN: Show benefits slides]**

> "Let's talk about the business impact. Customer service teams see 80% faster response times and 40% fewer escalations because the AI handles routine queries. Operations teams get real-time insights without needing SQL knowledge. And business users can ask questions in natural language—no dependency on technical teams."

**[SCREEN: Show metrics]**

> "Performance metrics: 99% accuracy on domain-specific queries, 1.8-second average response time, and the system scales to millions of queries without significant cost increase due to Azure's managed infrastructure."

**[SCREEN: Show use cases]**

> "While I built this for e-commerce, the architecture works for any industry. Healthcare can use it for patient records and medical policies. Finance for account inquiries and transaction history. Manufacturing for equipment manuals and parts inventory. Any business with scattered data can benefit from this unified intelligent interface."

---

### [14:45-15:00] CALL TO ACTION (15 seconds)

**[SCREEN: Show GitHub repository]**

> "The complete code is on GitHub—link in the description. I've included setup scripts that provision all the Azure resources automatically. Star the repo, try it yourself, and let me know in the comments what you build with it."

**[SCREEN: End screen with subscribe button]**

> "If you found this valuable, hit that subscribe button. I'm building more AI solutions with Azure and sharing everything I learn. Thanks for watching, and I'll see you in the next one!"

---

## 🎥 PRODUCTION NOTES

### Recording Setup

**Screen Recording:**
- Use OBS Studio or Camtasia
- 1920x1080 resolution, 60fps
- Capture: VS Code, Browser, Azure Portal

**Audio:**
- Use good microphone (Blue Yeti/Rode)
- Room with minimal echo
- Record separate audio track for easier editing

**Visuals to Prepare:**
1. Architecture diagram (from architecture_diagram.drawio)
2. Data flow diagram (from dataflow_diagram.drawio)
3. Problem statement slides
4. Cost breakdown slide
5. Benefits metrics slide
6. Use cases slide

### B-Roll Footage
- Azure Portal navigating between services
- Code scrolling through implementation files
- Network tab showing request timing
- Application Insights dashboard
- GitHub repository overview

### Editing Tips
- Add text overlays for key terms (RAG, Vector Search, HNSW)
- Zoom in on important code sections
- Use transitions between major sections
- Add subtle background music (low volume)
- Include closed captions for accessibility

### Thumbnail Ideas
- Split screen: "Before vs After" search interfaces
- "$0.02 per Query" in large text
- "99% Accuracy" with checkmark
- GPT-4o + Azure logos with architecture

### YouTube SEO

**Title Options:**
- "Building a Production Hybrid RAG System with Azure OpenAI & GPT-4o"
- "AI-Powered E-Commerce Search: Vector Search + Azure AI (Full Tutorial)"
- "Hybrid RAG Architecture Explained: From 0 to Production in 15 Minutes"

**Description Template:**
```
Learn how to build a production-ready Hybrid RAG (Retrieval-Augmented Generation) 
system using Azure OpenAI, GPT-4o, and Azure AI Search. This intelligent e-commerce 
assistant responds in under 2 seconds with 99% accuracy.

🔗 GitHub Repository: [YOUR-REPO-LINK]
🔗 Architecture Diagrams: [LINK]
🔗 Blog Post: [LINK]

📚 TIMESTAMPS:
0:00 - Introduction & Demo
0:45 - Problem Statement
2:00 - Architecture Overview
5:30 - Technical Implementation
8:30 - Live Demo
11:30 - Azure Services & Costs
13:30 - Benefits & Use Cases
14:45 - Resources & Next Steps

💡 KEY TECHNOLOGIES:
• Azure OpenAI (GPT-4o, text-embedding-3-large)
• Azure AI Search (Vector Search + HNSW)
• Next.js 16 (App Router)
• TypeScript
• Streaming SSE

📊 PERFORMANCE:
• Response Time: 1.8 seconds
• Accuracy: 99%+
• Cost: $0.027 per query
• Scale: 50K+ records + 850 documents

🔔 Subscribe for more AI + Azure tutorials!

#AzureOpenAI #GPT4o #HybridRAG #VectorSearch #AI #Azure #NextJS #MachineLearning
```

**Tags:**
Azure OpenAI, GPT-4, GPT-4o, Hybrid RAG, Vector Search, Azure AI Search, RAG tutorial, 
Retrieval Augmented Generation, LLM, AI Search, Semantic Search, Next.js, TypeScript, 
Azure Tutorial, AI Development, Enterprise AI, Production AI, Vector Database, 
HNSW Algorithm, E-commerce AI, Chatbot Development

---

## 📋 PRE-RECORDING CHECKLIST

### Code Preparation
- [ ] Clean up any API keys in environment variables
- [ ] Ensure all demo queries work perfectly
- [ ] Test streaming responses are smooth
- [ ] Verify all Azure resources are running
- [ ] Have sample data loaded in all indexes
- [ ] Clear browser history/cookies for clean demo

### Visual Assets
- [ ] Export diagrams as high-res PNG
- [ ] Create all slides in PowerPoint/Keynote
- [ ] Design custom thumbnail in Canva/Photoshop
- [ ] Prepare GitHub README for viewers
- [ ] Test screen recording software
- [ ] Set up good lighting for camera shots

### Script Preparation
- [ ] Practice reading script multiple times
- [ ] Time each section to ensure 15-minute target
- [ ] Mark sections where you'll code-switch
- [ ] Prepare smooth transitions
- [ ] Have water nearby for recording

### Azure Portal
- [ ] Clean up test resources
- [ ] Ensure pricing is visible
- [ ] Have metrics dashboard ready
- [ ] Test all portal navigation paths

---

## 🎬 POST-PRODUCTION

### Editing Checklist
- [ ] Cut out long pauses and mistakes
- [ ] Add text overlays for technical terms
- [ ] Include zoom-ins on code sections
- [ ] Add lower-thirds with your name/handle
- [ ] Include smooth music in background (20% volume)
- [ ] Add end screen with subscribe button
- [ ] Color grade for consistent look
- [ ] Export in 1080p60

### Before Publishing
- [ ] Upload unlisted first to test
- [ ] Add all timestamps in description
- [ ] Upload custom thumbnail
- [ ] Add to relevant playlists
- [ ] Set up end screens and cards
- [ ] Schedule or publish
- [ ] Share on LinkedIn, Twitter, Reddit

### Engagement
- [ ] Pin comment with GitHub link
- [ ] Respond to comments in first 24 hours
- [ ] Create follow-up content based on questions
- [ ] Cross-post to LinkedIn with insights
- [ ] Share in relevant Discord/Slack communities

---

**🎯 You're ready to record a professional 15-minute technical tutorial!**

This script is designed to be spoken naturally while showing the right visuals at the right time. Practice it a few times, adjust the pacing to your style, and remember: energy and enthusiasm matter as much as technical accuracy!

Good luck with your video! 🚀
