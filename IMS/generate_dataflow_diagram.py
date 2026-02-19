"""
AI Agentic Incident Resolution System - Data Flow Diagram Generator
Creates a comprehensive data flow diagram PDF
"""

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, black, white
from datetime import datetime

# Color scheme
PRIMARY = HexColor('#2C3E50')
ACCENT = HexColor('#3498DB')
SUCCESS = HexColor('#2ECC71')
WARNING = HexColor('#E74C3C')
INFO = HexColor('#9B59B6')
BG_LIGHT = HexColor('#ECF0F1')

def draw_rounded_rect(c, x, y, width, height, radius, fill_color, stroke_color=None):
    """Draw rounded rectangle"""
    c.setFillColor(fill_color)
    if stroke_color:
        c.setStrokeColor(stroke_color)
        c.setLineWidth(2)
    else:
        c.setStrokeColor(fill_color)
    
    c.roundRect(x, y, width, height, radius, fill=1, stroke=1)

def draw_data_node(c, x, y, width, height, title, icon, color, data_type):
    """Draw a data processing node"""
    draw_rounded_rect(c, x, y, width, height, 10, color, PRIMARY)
    
    # Icon
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(white)
    c.drawString(x + 10, y + height - 25, icon)
    
    # Title
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x + 40, y + height - 22, title)
    
    # Data type
    c.setFont("Helvetica", 9)
    c.setFillColor(BG_LIGHT)
    c.drawString(x + 10, y + 10, data_type)

def draw_flow_arrow(c, x1, y1, x2, y2, color, label, data_format):
    """Draw data flow arrow with label"""
    c.setStrokeColor(color)
    c.setLineWidth(2)
    
    # Dashed line for data flow
    c.setDash(6, 3)
    c.line(x1, y1, x2, y2)
    c.setDash()  # Reset to solid
    
    # Arrowhead
    arrow_size = 8
    c.setFillColor(color)
    if x2 > x1:  # Right
        c.polygon([(x2, y2), (x2-arrow_size, y2-arrow_size/2), (x2-arrow_size, y2+arrow_size/2)], fill=1)
    elif x2 < x1:  # Left
        c.polygon([(x2, y2), (x2+arrow_size, y2-arrow_size/2), (x2+arrow_size, y2+arrow_size/2)], fill=1)
    elif y2 > y1:  # Up
        c.polygon([(x2, y2), (x2-arrow_size/2, y2-arrow_size), (x2+arrow_size/2, y2-arrow_size)], fill=1)
    else:  # Down
        c.polygon([(x2, y2), (x2-arrow_size/2, y2+arrow_size), (x2+arrow_size/2, y2+arrow_size)], fill=1)
    
    # Label box
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2
    
    c.setFillColor(white)
    c.roundRect(mid_x - 35, mid_y - 15, 70, 30, 5, fill=1, stroke=1)
    
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(color)
    c.drawCentredString(mid_x, mid_y + 5, label)
    
    c.setFont("Helvetica", 7)
    c.setFillColor(PRIMARY)
    c.drawCentredString(mid_x, mid_y - 5, data_format)

def create_dataflow_diagram():
    """Generate data flow diagram PDF"""
    
    print("🔄 Creating Data Flow Diagram PDF...")
    print("=" * 80)
    
    filename = "Incident_Resolution_DataFlow.pdf"
    c = canvas.Canvas(filename, pagesize=landscape(A4))
    width, height = landscape(A4)
    
    # Title page
    c.setFillColor(ACCENT)
    c.rect(0, 0, width, height, fill=1)
    
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(width/2, height/2 + 50, "AI Agentic Incident Resolution")
    
    c.setFont("Helvetica", 24)
    c.drawCentredString(width/2, height/2, "Data Flow Diagram")
    
    c.setFont("Helvetica", 14)
    c.drawCentredString(width/2, height/2 - 50, f"Generated: {datetime.now().strftime('%B %d, %Y')}")
    
    c.setFont("Helvetica-Oblique", 12)
    c.drawCentredString(width/2, 50, "End-to-End Data Processing Flow")
    
    # Page 2: Complete Data Flow
    c.showPage()
    
    # Header
    c.setFillColor(PRIMARY)
    c.rect(0, height - 60, width, 60, fill=1)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(40, height - 40, "🔄 Complete Data Flow - Incident to Resolution")
    
    # Background
    c.setFillColor(BG_LIGHT)
    c.rect(0, 0, width, height - 60, fill=1)
    
    # Step 1: Monitoring Alert
    draw_data_node(c, 60, height - 150, 150, 60, "Dynatrace Alert", "📊", WARNING, "Alert Data")
    
    # Step 2: Incident Creation
    draw_data_node(c, 60, height - 270, 150, 60, "ServiceNow", "🎫", SUCCESS, "Incident Ticket")
    
    # Step 3: AI Intake
    draw_data_node(c, 280, height - 210, 150, 60, "AI Orchestrator", "🎯", ACCENT, "JSON Payload")
    
    # Step 4: Analysis
    draw_data_node(c, 500, height - 150, 150, 60, "Incident Analyzer", "🔍", INFO, "Structured Data")
    
    # Step 5: Vector Search
    draw_data_node(c, 500, height - 270, 150, 60, "Vector DB Query", "🗄️", PRIMARY, "Embeddings")
    
    # Step 6: Resolution Generation
    draw_data_node(c, 720, height - 210, 150, 60, "Resolution Agent", "✨", SUCCESS, "Action Plan")
    
    # Step 7: Execution
    draw_data_node(c, 500, height - 390, 150, 60, "Execution Agent", "⚡", WARNING, "Commands")
    
    # Step 8: Update
    draw_data_node(c, 280, height - 390, 150, 60, "Update Ticket", "📝", SUCCESS, "Resolution Data")
    
    # Step 9: Knowledge Base
    draw_data_node(c, 60, height - 390, 150, 60, "Update KB", "💾", PRIMARY, "Document")
    
    # Data flows
    flows = [
        (135, height - 150, 135, height - 210, WARNING, "Alert Trigger", "JSON"),
        (210, height - 240, 280, height - 190, ACCENT, "Incident Data", "REST API"),
        (430, height - 180, 500, height - 180, INFO, "Parse Details", "Structured"),
        (575, height - 210, 575, height - 270, PRIMARY, "Search Similar", "Vector"),
        (650, height - 240, 720, height - 190, SUCCESS, "Match Results", "Ranked List"),
        (795, height - 210, 795, height - 300, WARNING, "Action Steps", "Sequence"),
        (720, height - 360, 650, height - 360, SUCCESS, "Execution Log", "Status"),
        (500, height - 360, 430, height - 360, ACCENT, "Completion", "Results"),
        (280, height - 360, 210, height - 360, SUCCESS, "Resolution", "Summary"),
        (135, height - 330, 135, height - 390, PRIMARY, "Store KB", "Markdown"),
    ]
    
    for x1, y1, x2, y2, color, label, format in flows:
        draw_flow_arrow(c, x1, y1, x2, y2, color, label, format)
    
    # Data format legend
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(PRIMARY)
    c.drawString(50, 100, "📋 Data Formats:")
    
    c.setFont("Helvetica", 10)
    formats = [
        "• JSON: Structured incident data",
        "• REST API: HTTP requests/responses",
        "• Vector: Embedding representations",
        "• Markdown: Human-readable documentation",
    ]
    
    y_pos = 80
    for fmt in formats:
        c.drawString(50, y_pos, fmt)
        y_pos -= 15
    
    c.drawString(400, 100, "🔄 Flow Types:")
    flow_types = [
        "→ Solid Arrow: Primary data flow",
        "⇢ Dashed Arrow: Query/Response",
        "↻ Bidirectional: Data exchange"
    ]
    
    y_pos = 80
    for ft in flow_types:
        c.drawString(400, y_pos, ft)
        y_pos -= 15
    
    # Page 3: Detailed Data Structures
    c.showPage()
    
    # Header
    c.setFillColor(PRIMARY)
    c.rect(0, height - 60, width, 60, fill=1)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(40, height - 40, "📊 Data Structures & Schemas")
    
    # Background
    c.setFillColor(BG_LIGHT)
    c.rect(0, 0, width, height - 60, fill=1)
    
    # Data structure boxes
    data_structures = [
        {
            'title': "1. Dynatrace Alert",
            'color': WARNING,
            'fields': [
                "alert_id: string",
                "severity: enum(LOW|MEDIUM|HIGH|CRITICAL)",
                "timestamp: datetime",
                "entity_name: string",
                "problem_title: string",
                "problem_details: text",
                "affected_services: array",
                "metrics: object"
            ]
        },
        {
            'title': "2. ServiceNow Incident",
            'color': SUCCESS,
            'fields': [
                "incident_number: string",
                "short_description: string",
                "description: text",
                "priority: int(1-5)",
                "urgency: int(1-3)",
                "impact: int(1-3)",
                "assigned_to: string",
                "state: enum",
                "category: string"
            ]
        },
        {
            'title': "3. Vector DB Embedding",
            'color': PRIMARY,
            'fields': [
                "incident_id: uuid",
                "embedding_vector: float[1536]",
                "metadata: object",
                "  - incident_type: string",
                "  - resolution_success: boolean",
                "  - resolution_time: int",
                "similarity_score: float",
                "indexed_at: datetime"
            ]
        },
        {
            'title': "4. Resolution Plan",
            'color': SUCCESS,
            'fields': [
                "plan_id: uuid",
                "incident_id: string",
                "resolution_steps: array",
                "  - step_number: int",
                "  - action: string",
                "  - command: string",
                "  - expected_result: string",
                "confidence_score: float",
                "estimated_time: int",
                "rollback_plan: array"
            ]
        }
    ]
    
    x_start = 50
    y_start = height - 120
    box_width = 220
    box_height = 200
    spacing = 15
    
    for idx, ds in enumerate(data_structures):
        row = idx // 2
        col = idx % 2
        
        x = x_start + col * (box_width + spacing) + (col * 300)
        y = y_start - row * (box_height + spacing + 40)
        
        # Box
        c.setFillColor(white)
        c.setStrokeColor(ds['color'])
        c.setLineWidth(3)
        c.roundRect(x, y, box_width, box_height, 10, fill=1, stroke=1)
        
        # Title
        c.setFillColor(ds['color'])
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x + 10, y + box_height - 20, ds['title'])
        
        # Fields
        c.setFont("Courier", 8)
        c.setFillColor(PRIMARY)
        y_pos = y + box_height - 45
        for field in ds['fields']:
            c.drawString(x + 10, y_pos, field)
            y_pos -= 12
    
    # Footer notes
    c.setFont("Helvetica", 10)
    c.setFillColor(PRIMARY)
    c.drawString(50, 60, "💡 All data structures use JSON format for interoperability")
    c.drawString(50, 45, "🔒 Sensitive data is encrypted in transit and at rest")
    c.drawString(50, 30, "📏 Vector embeddings use 1536 dimensions (OpenAI compatible)")
    
    # Page 4: Data Processing Pipeline
    c.showPage()
    
    # Header
    c.setFillColor(PRIMARY)
    c.rect(0, height - 60, width, 60, fill=1)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(40, height - 40, "⚙️ Data Processing Pipeline")
    
    # Background
    c.setFillColor(BG_LIGHT)
    c.rect(0, 0, width, height - 60, fill=1)
    
    # Pipeline stages
    stages = [
        ("1. Ingestion", "📥", height - 130, [
            "Receive Dynatrace webhook",
            "Validate payload structure",
            "Extract critical fields",
            "Normalize data format"
        ]),
        ("2. Enrichment", "🔍", height - 240, [
            "Query ServiceNow for context",
            "Fetch related incidents",
            "Add environmental data",
            "Correlation analysis"
        ]),
        ("3. Vectorization", "🧮", height - 350, [
            "Generate text embeddings",
            "Convert to 1536-d vector",
            "Calculate similarity scores",
            "Rank matching incidents"
        ]),
        ("4. AI Processing", "🤖", height - 460, [
            "LLM analyzes incident",
            "Generates resolution plan",
            "Validates against history",
            "Calculates confidence score"
        ])
    ]
    
    x_pos = 80
    for idx, (title, icon, y, steps) in enumerate(stages):
        # Stage box
        box_width = 180
        box_height = 90
        
        c.setFillColor(white)
        c.setStrokeColor(ACCENT)
        c.setLineWidth(2)
        c.roundRect(x_pos, y, box_width, box_height, 10, fill=1, stroke=1)
        
        # Title
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(ACCENT)
        c.drawString(x_pos + 10, y + box_height - 20, f"{icon} {title}")
        
        # Steps
        c.setFont("Helvetica", 8)
        c.setFillColor(PRIMARY)
        y_step = y + box_height - 40
        for step in steps:
            c.drawString(x_pos + 10, y_step, f"• {step}")
            y_step -= 12
        
        # Arrow to next stage
        if idx < len(stages) - 1:
            arrow_y = y + box_height / 2
            c.setStrokeColor(SUCCESS)
            c.setLineWidth(3)
            c.line(x_pos + box_width, arrow_y, x_pos + box_width + 30, arrow_y)
            c.setFillColor(SUCCESS)
            c.polygon([
                (x_pos + box_width + 30, arrow_y),
                (x_pos + box_width + 22, arrow_y - 5),
                (x_pos + box_width + 22, arrow_y + 5)
            ], fill=1)
        
        x_pos += box_width + 30
    
    # Output section
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(SUCCESS)
    c.drawString(750, height - 265, "📤 Output")
    
    c.setFont("Helvetica", 10)
    c.setFillColor(PRIMARY)
    outputs = [
        "✓ Resolution plan JSON",
        "✓ Confidence score: 0-100%",
        "✓ Execution commands",
        "✓ Expected results",
        "✓ Rollback procedure"
    ]
    
    y_pos = height - 290
    for output in outputs:
        c.drawString(750, y_pos, output)
        y_pos -= 18
    
    # Performance metrics
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(PRIMARY)
    c.drawString(50, 100, "⏱️ Performance Metrics:")
    
    c.setFont("Helvetica", 10)
    metrics = [
        "• Average processing time: 3-5 seconds",
        "• Vector search latency: <500ms",
        "• LLM response time: 2-3 seconds",
        "• End-to-end resolution: <60 seconds",
        "• Throughput: 100+ incidents/minute"
    ]
    
    y_pos = 80
    for metric in metrics:
        c.drawString(50, y_pos, metric)
        y_pos -= 15
    
    c.drawString(450, 100, "📈 Data Volume:")
    volumes = [
        "• Incidents processed: ~10,000/day",
        "• Vector database size: 500K+ embeddings",
        "• Knowledge base: 50,000+ documents",
        "• Success rate: 85%+ auto-resolution"
    ]
    
    y_pos = 80
    for volume in volumes:
        c.drawString(450, y_pos, volume)
        y_pos -= 15
    
    # Save PDF
    c.save()
    
    print("\n" + "=" * 80)
    print(f"✅ Data Flow Diagram PDF created successfully!")
    print(f"📄 File: {filename}")
    print(f"📊 Pages: 4")
    print("=" * 80)
    print("\n📋 Contents:")
    print("  Page 1: Title & Overview")
    print("  Page 2: Complete End-to-End Data Flow")
    print("  Page 3: Data Structures & Schemas")
    print("  Page 4: Data Processing Pipeline")
    print()
    
    return filename

if __name__ == "__main__":
    try:
        print("=" * 80)
        print("AI AGENTIC INCIDENT RESOLUTION - DATA FLOW DIAGRAM")
        print("=" * 80)
        print()
        
        filename = create_dataflow_diagram()
        
        print("🎉 Done! Open the PDF to view the data flow diagram.")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()