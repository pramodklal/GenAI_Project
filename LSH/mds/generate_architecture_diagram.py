"""
AI Agentic Incident Resolution System - Architecture Diagram Generator
Creates a comprehensive architecture diagram PDF
"""

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle
from datetime import datetime

# Color scheme
PRIMARY = HexColor('#2C3E50')      # Dark blue-gray
ACCENT = HexColor('#3498DB')       # Bright blue
SUCCESS = HexColor('#2ECC71')      # Green
WARNING = HexColor('#E74C3C')      # Red
DYNATRACE = HexColor('#1496FF')    # Dynatrace blue
SERVICENOW = HexColor('#62D84E')   # ServiceNow green
AWS = HexColor('#FF9900')          # AWS orange
BEDROCK = HexColor('#8B4513')      # Bedrock brown
BG_LIGHT = HexColor('#ECF0F1')     # Light gray

def draw_rounded_rect(c, x, y, width, height, radius, fill_color, stroke_color=None):
    """Draw rounded rectangle"""
    c.setFillColor(fill_color)
    if stroke_color:
        c.setStrokeColor(stroke_color)
        c.setLineWidth(2)
    else:
        c.setStrokeColor(fill_color)
    
    c.roundRect(x, y, width, height, radius, fill=1, stroke=1)

def draw_component_box(c, x, y, width, height, title, icon, color, details=None):
    """Draw a component box with title and details"""
    # Main box
    draw_rounded_rect(c, x, y, width, height, 10, color, PRIMARY)
    
    # Title area
    draw_rounded_rect(c, x, y + height - 40, width, 40, 10, PRIMARY)
    
    # Icon
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(white)
    c.drawString(x + 10, y + height - 28, icon)
    
    # Title
    c.setFont("Helvetica-Bold", 14)
    c.drawString(x + 45, y + height - 25, title)
    
    # Details
    if details:
        c.setFont("Helvetica", 9)
        c.setFillColor(PRIMARY)
        y_pos = y + height - 55
        for detail in details:
            c.drawString(x + 10, y_pos, f"• {detail}")
            y_pos -= 15

def draw_arrow(c, x1, y1, x2, y2, color, label=None):
    """Draw arrow between components"""
    c.setStrokeColor(color)
    c.setLineWidth(3)
    c.line(x1, y1, x2, y2)
    
    # Arrowhead using path
    arrow_size = 10
    c.setFillColor(color)
    c.setStrokeColor(color)
    
    p = c.beginPath()
    if x2 > x1:  # Right arrow
        p.moveTo(x2, y2)
        p.lineTo(x2-arrow_size, y2-arrow_size/2)
        p.lineTo(x2-arrow_size, y2+arrow_size/2)
        p.close()
    elif x2 < x1:  # Left arrow
        p.moveTo(x2, y2)
        p.lineTo(x2+arrow_size, y2-arrow_size/2)
        p.lineTo(x2+arrow_size, y2+arrow_size/2)
        p.close()
    elif y2 > y1:  # Up arrow
        p.moveTo(x2, y2)
        p.lineTo(x2-arrow_size/2, y2-arrow_size)
        p.lineTo(x2+arrow_size/2, y2-arrow_size)
        p.close()
    else:  # Down arrow
        p.moveTo(x2, y2)
        p.lineTo(x2-arrow_size/2, y2+arrow_size)
        p.lineTo(x2+arrow_size/2, y2+arrow_size)
        p.close()
    
    c.drawPath(p, fill=1, stroke=1)
    
    # Label
    if label:
        c.setFont("Helvetica", 9)
        c.setFillColor(color)
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        c.drawString(mid_x + 5, mid_y + 5, label)

def create_architecture_diagram():
    """Generate architecture diagram PDF"""
    
    print("🏗️ Creating Architecture Diagram PDF...")
    print("=" * 80)
    
    filename = "Incident_Resolution_Architecture.pdf"
    c = canvas.Canvas(filename, pagesize=landscape(A4))
    width, height = landscape(A4)
    
    # Title page
    c.setFillColor(PRIMARY)
    c.rect(0, 0, width, height, fill=1)
    
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(width/2, height/2 + 50, "AI Agentic Incident Resolution System")
    
    c.setFont("Helvetica", 24)
    c.drawCentredString(width/2, height/2, "Architecture Diagram")
    
    c.setFont("Helvetica", 14)
    c.drawCentredString(width/2, height/2 - 50, f"Generated: {datetime.now().strftime('%B %d, %Y')}")
    
    c.setFont("Helvetica-Oblique", 12)
    c.drawCentredString(width/2, 50, "Automated Incident Detection → Analysis → Resolution")
    
    # Page 2: High-Level Architecture
    c.showPage()
    
    # Header
    c.setFillColor(PRIMARY)
    c.rect(0, height - 60, width, 60, fill=1)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(40, height - 40, "🏗️ High-Level Architecture")
    
    # Background
    c.setFillColor(BG_LIGHT)
    c.rect(0, 0, width, height - 60, fill=1)
    
    # Layer 1: Monitoring (Top Left)
    draw_component_box(
        c, 40, height - 140, 200, 80,
        "Dynatrace", "📊",
        DYNATRACE,
        [
            "Infrastructure Monitor",
            "Real-time Alerting"
        ]
    )
    
    # Layer 2: Incident Management (Middle Left)
    draw_component_box(
        c, 40, height - 250, 200, 80,
        "ServiceNow", "🎫",
        SERVICENOW,
        [
            "Incident Creation",
            "Ticket Management"
        ]
    )
    
    # Layer 3: AI Processing (Center)
    draw_component_box(
        c, 280, height - 310, 260, 190,
        "AWS Bedrock", "🧠",
        AWS,
        [
            "LLM Models (Claude)",
            "Incident Analysis",
            "Resolution Generation",
            "Agentic AI System",
            "Multi-agent Workflow"
        ]
    )
    
    # Layer 4: Knowledge Base (Top Right)
    draw_component_box(
        c, 580, height - 140, 200, 80,
        "Vector Database", "🗄️",
        BEDROCK,
        [
            "Historical Incidents",
            "Semantic Search"
        ]
    )
    
    # Layer 5: Documentation (Middle Right)
    draw_component_box(
        c, 580, height - 250, 200, 80,
        "Documentation", "📝",
        SUCCESS,
        [
            "Resolution Docs",
            "Best Practices"
        ]
    )
    
    # Arrows - Flow
    # Dynatrace to ServiceNow
    draw_arrow(c, 140, height - 140, 140, height - 170, WARNING, "Alert")
    
    # ServiceNow to AI
    draw_arrow(c, 240, height - 210, 280, height - 230, ACCENT, "Incident")
    
    # AI to Vector DB
    draw_arrow(c, 540, height - 180, 580, height - 110, SUCCESS, "Query")
    
    # Vector DB to AI
    draw_arrow(c, 580, height - 120, 540, height - 190, SUCCESS, "Results")
    
    # AI to Documentation
    draw_arrow(c, 540, height - 240, 580, height - 220, PRIMARY, "Update")
    
    # AI back to ServiceNow
    draw_arrow(c, 280, height - 220, 240, height - 200, SUCCESS, "Fix")
    
    # Legend
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(PRIMARY)
    c.drawString(40, 90, "📋 Workflow:")
    
    c.setFont("Helvetica", 9)
    c.setFillColor(PRIMARY)
    legend_items = [
        "1. Dynatrace detects issue → Triggers alert",
        "2. ServiceNow creates incident ticket",
        "3. AWS Bedrock AI analyzes incident",
        "4. Vector DB searches similar past cases",
        "5. AI generates & executes resolution",
        "6. Documentation updated with new knowledge"
    ]
    
    y_pos = 72
    col1_x = 40
    col2_x = 420
    for idx, item in enumerate(legend_items):
        if idx < 3:
            c.drawString(col1_x, y_pos - (idx * 12), item)
        else:
            c.drawString(col2_x, y_pos - ((idx - 3) * 12), item)
    
    # Page 3: Detailed Component Architecture
    c.showPage()
    
    # Header
    c.setFillColor(PRIMARY)
    c.rect(0, height - 60, width, 60, fill=1)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(40, height - 40, "🔍 Detailed Component Architecture")
    
    # Background
    c.setFillColor(BG_LIGHT)
    c.rect(0, 0, width, height - 60, fill=1)
    
    # AI Agent System (Center large box)
    c.setFillColor(white)
    c.setStrokeColor(PRIMARY)
    c.setLineWidth(3)
    c.roundRect(150, height - 480, 540, 360, 15, fill=1, stroke=1)
    
    c.setFillColor(PRIMARY)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(170, height - 140, "🤖 Agentic AI System")
    
    # Sub-components
    agents = [
        ("Incident Analyzer", "🔍", 170, height - 200, [
            "Parse incident details",
            "Extract key info"
        ]),
        ("Resolution Searcher", "🔎", 360, height - 200, [
            "Query vector database",
            "Find similar cases"
        ]),
        ("Resolution Generator", "✨", 550, height - 200, [
            "Generate solutions",
            "Adapt resolutions"
        ]),
        ("Execution Agent", "⚡", 170, height - 330, [
            "Execute steps",
            "Monitor progress"
        ]),
        ("Orchestrator", "🎯", 360, height - 330, [
            "Coordinate agents",
            "Manage workflow"
        ]),
        ("Logger", "📝", 550, height - 330, [
            "Track events",
            "Store results"
        ])
    ]
    
    for name, icon, x, y, details in agents:
        draw_component_box(c, x, y, 170, 100, name, icon, ACCENT, details)
    
    # Integration points
    integrations = [
        ("API Gateway", 40, height - 240, AWS),
        ("Event Bus", 40, height - 340, SUCCESS),
        ("Monitoring", 720, height - 240, WARNING),
        ("Logging", 720, height - 340, PRIMARY)
    ]
    
    for name, x, y, color in integrations:
        draw_rounded_rect(c, x, y, 100, 50, 8, color)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(x + 50, y + 20, name)
    
    # Connection arrows
    draw_arrow(c, 140, height - 215, 170, height - 180, ACCENT, "Input")
    draw_arrow(c, 690, height - 215, 720, height - 215, WARNING, "Metrics")
    
    # Footer notes
    c.setFont("Helvetica", 10)
    c.setFillColor(PRIMARY)
    notes = [
        "• All agents communicate through the Orchestrator",
        "• Vector DB provides semantic search for similar incidents",
        "• AWS Bedrock hosts LLM models (Claude Sonnet, GPT-4)",
        "• Real-time monitoring tracks agent performance"
    ]
    
    y_pos = 60
    for note in notes:
        c.drawString(50, y_pos, note)
        y_pos -= 15
    
    # Page 4: Technology Stack
    c.showPage()
    
    # Header
    c.setFillColor(PRIMARY)
    c.rect(0, height - 60, width, 60, fill=1)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(40, height - 40, "🛠️ Technology Stack")
    
    # Background
    c.setFillColor(BG_LIGHT)
    c.rect(0, 0, width, height - 60, fill=1)
    
    # Stack layers
    stacks = [
        {
            'title': "Monitoring",
            'color': DYNATRACE,
            'items': [
                "Dynatrace APM",
                "Log Analytics"
            ]
        },
        {
            'title': "ITSM",
            'color': SERVICENOW,
            'items': [
                "ServiceNow ITSM",
                "REST API"
            ]
        },
        {
            'title': "AI/ML",
            'color': AWS,
            'items': [
                "AWS Bedrock",
                "LangChain"
            ]
        },
        {
            'title': "Data Storage",
            'color': BEDROCK,
            'items': [
                "OpenSearch Vector",
                "RDS PostgreSQL"
            ]
        },
        {
            'title': "Infrastructure",
            'color': PRIMARY,
            'items': [
                "AWS Lambda",
                "API Gateway"
            ]
        },
        {
            'title': "Security",
            'color': WARNING,
            'items': [
                "IAM Roles",
                "CloudWatch"
            ]
        }
    ]
    
    x_start = 50
    y_start = height - 100
    box_width = 130
    box_height = 90
    spacing = 20
    
    for idx, stack in enumerate(stacks):
        row = idx // 3
        col = idx % 3
        
        x = x_start + col * (box_width + spacing)
        y = y_start - row * (box_height + spacing + 20)
        
        draw_component_box(
            c, x, y, box_width, box_height,
            stack['title'], "🔧",
            stack['color'],
            stack['items']
        )
    
    # Key features - 3 columns
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(PRIMARY)
    c.drawString(50, 100, "✨ Key Features:")
    
    c.setFont("Helvetica", 9)
    features = [
        ["✓ Serverless scalable", "✓ Real-time processing"],
        ["✓ Vector search AI", "✓ Multi-agent system"],
        ["✓ Auto resolution", "✓ Continuous learning"]
    ]
    
    y_pos = 82
    for row in features:
        x_positions = [50, 250, 450]
        for idx, feature in enumerate(row + [""]):
            if feature and idx < len(x_positions):
                c.drawString(x_positions[idx], y_pos, feature)
        y_pos -= 14
    
    # Save PDF
    c.save()
    
    print("\n" + "=" * 80)
    print(f"✅ Architecture Diagram PDF created successfully!")
    print(f"📄 File: {filename}")
    print(f"📊 Pages: 4")
    print("=" * 80)
    print("\n📋 Contents:")
    print("  Page 1: Title & Overview")
    print("  Page 2: High-Level Architecture")
    print("  Page 3: Detailed Component Architecture")
    print("  Page 4: Technology Stack")
    print()
    
    return filename

if __name__ == "__main__":
    try:
        print("=" * 80)
        print("AI AGENTIC INCIDENT RESOLUTION - ARCHITECTURE DIAGRAM")
        print("=" * 80)
        print()
        
        filename = create_architecture_diagram()
        
        print("🎉 Done! Open the PDF to view the architecture diagram.")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()