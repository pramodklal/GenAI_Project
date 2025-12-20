# Pharma Manufacturing - Solution Design Document

**Version:** 1.0.0  
**Date:** December 18, 2025  
**Author:** AI Architecture Team  

---

## 📋 **EXECUTIVE SUMMARY**

This document outlines the comprehensive solution design for a **Pharmaceutical Manufacturing Management System** leveraging AI agents, MCP (Model Context Protocol) servers, and Astra DB Serverless for real-time quality control, regulatory compliance, and production optimization.

### **Key Objectives:**
- ✅ **Quality Assurance:** Automated QC analysis with AI-powered OOS detection
- ✅ **Regulatory Compliance:** FDA/EMA validation with 21 CFR Part 11 compliance
- ✅ **Production Optimization:** AI-driven batch scheduling and yield prediction
- ✅ **Supply Chain Intelligence:** Demand forecasting and supplier performance analysis
- ✅ **Pharmacovigilance:** Adverse event monitoring with vector-based pattern detection
- ✅ **Equipment Management:** Predictive maintenance and OEE tracking

---

## 🏗️ **SYSTEM ARCHITECTURE**

### **4-Layer Architecture:**

```
┌─────────────────────────────────────────────────────────────┐
│          LAYER 1: Streamlit UI (6 Pages)                    │
│  💊 Medicine Catalog | 🏭 Batch Production | 🔬 QC           │
│  📋 Compliance | 📦 Inventory | 📊 Analytics                │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│          LAYER 2: AI Agent Layer (6 Agents)                 │
│  Quality Control | Regulatory | Production Optimization     │
│  Supply Chain | Pharmacovigilance | Equipment Maintenance   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│          LAYER 3: MCP Server Layer (5 Servers)              │
│  Medicine MCP | Quality Control MCP | Production MCP        │
│  Compliance MCP | Inventory MCP                             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│          LAYER 4: Astra DB (13 Collections)                 │
│  10 Regular Collections + 3 Vector Collections (1536D)      │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 **DATA MODEL (ASTRA DB COLLECTIONS)**

### **REGULAR COLLECTIONS (10)**

#### **1. medicines**
Primary collection for medicine master data.

**Schema:**
```json
{
  "medicine_id": "uuid",
  "name": "string",
  "generic_name": "string",
  "dosage_form": "string (tablet/capsule/injection/syrup)",
  "strength": "string (e.g., 500mg)",
  "category": "string (antibiotic/analgesic/antihypertensive)",
  "indications": "array<string>",
  "contraindications": "array<string>",
  "storage_conditions": "string",
  "shelf_life_months": "int",
  "status": "string (active/discontinued/under_development)"
}
```

**Sample Data:**
```json
{
  "medicine_id": "medicine_123",
  "name": "Amoxicillin 500mg",
  "generic_name": "Amoxicillin",
  "dosage_form": "tablet",
  "strength": "500mg",
  "category": "antibiotic",
  "indications": ["bacterial_infections", "pneumonia"],
  "storage_conditions": "15-25°C, protected from moisture",
  "shelf_life_months": 36,
  "status": "active"
}
```

---

#### **2. manufacturing_batches**
Tracks all batch production lifecycle.

**Schema:**
```json
{
  "batch_id": "uuid",
  "medicine_id": "uuid",
  "batch_number": "string (unique)",
  "quantity": "int",
  "manufacturing_date": "date",
  "expiry_date": "date",
  "stage": "string (mixing/granulation/compression/coating/packaging/completed)",
  "status": "string (in_progress/qc_pending/approved/rejected)",
  "yield_percentage": "float",
  "assigned_equipment": "array<string>",
  "assigned_staff": "array<string>",
  "created_at": "timestamp"
}
```

---

#### **3. raw_materials**
Inventory management for APIs and excipients.

**Schema:**
```json
{
  "material_id": "uuid",
  "material_name": "string",
  "material_code": "string (unique)",
  "category": "string (API/excipient/packaging)",
  "quantity_on_hand": "float",
  "unit_of_measure": "string (kg/liters/units)",
  "reorder_level": "float",
  "expiry_date": "date",
  "storage_location": "string",
  "supplier_id": "uuid",
  "last_updated": "timestamp"
}
```

---

#### **4. quality_control_tests**
QC test results for batch release decisions.

**Schema:**
```json
{
  "test_id": "uuid",
  "batch_id": "uuid",
  "test_type": "string (dissolution/assay/microbial/stability/appearance)",
  "test_date": "date",
  "parameters": {
    "specification": "string",
    "acceptance_criteria": "string"
  },
  "results": {
    "value": "float/string",
    "unit": "string",
    "interpretation": "string"
  },
  "pass_fail_status": "string (pass/fail/pending)",
  "tested_by": "string",
  "approved_by": "string",
  "remarks": "string"
}
```

**Sample Data:**
```json
{
  "test_id": "test_001",
  "batch_id": "BATCH-2025-001",
  "test_type": "dissolution",
  "test_date": "2025-12-21",
  "parameters": {
    "specification": "≥80% in 30 minutes",
    "acceptance_criteria": "≥75%"
  },
  "results": {
    "value": 87.3,
    "unit": "%",
    "interpretation": "Meets specification"
  },
  "pass_fail_status": "pass",
  "tested_by": "QC_Analyst_007",
  "approved_by": "QA_Manager_001"
}
```

---

#### **5. suppliers**
Supplier master with performance tracking.

**Schema:**
```json
{
  "supplier_id": "uuid",
  "supplier_name": "string",
  "contact_person": "string",
  "email": "string",
  "phone": "string",
  "address": "object",
  "certifications": ["GMP", "ISO_9001", "ISO_14001"],
  "rating": "float (1-5)",
  "status": "string (active/inactive/blacklisted)",
  "last_audit_date": "date",
  "on_time_delivery_rate": "float (%)"
}
```

---

#### **6. production_schedules**
Production planning and equipment allocation.

**Schema:**
```json
{
  "schedule_id": "uuid",
  "batch_id": "uuid",
  "medicine_id": "uuid",
  "scheduled_date": "date",
  "equipment_ids": "array<string>",
  "assigned_staff": "array<string>",
  "estimated_duration_hours": "float",
  "priority": "string (high/medium/low)",
  "status": "string (scheduled/in_progress/completed/delayed)"
}
```

---

#### **7. equipment_maintenance**
Equipment tracking and OEE calculation.

**Schema:**
```json
{
  "equipment_id": "uuid",
  "equipment_name": "string",
  "equipment_type": "string (reactor/mixer/tablet_press/coating_machine/packaging_line)",
  "location": "string",
  "last_maintenance_date": "date",
  "next_maintenance_date": "date",
  "calibration_due_date": "date",
  "status": "string (operational/under_maintenance/breakdown)",
  "oee_score": "float (%)",
  "total_runtime_hours": "float",
  "downtime_hours": "float"
}
```

---

#### **8. regulatory_documents**
Compliance document repository.

**Schema:**
```json
{
  "document_id": "uuid",
  "document_type": "string (DMF/CTD/stability_study/GMP_certificate)",
  "medicine_id": "uuid (nullable)",
  "title": "string",
  "document_number": "string",
  "issue_date": "date",
  "expiry_date": "date",
  "regulatory_authority": "string (FDA/EMA/WHO)",
  "file_url": "string",
  "status": "string (active/expired/under_review)"
}
```

---

#### **9. purchase_orders**
Purchase order management.

**Schema:**
```json
{
  "po_id": "uuid",
  "supplier_id": "uuid",
  "order_date": "date",
  "expected_delivery_date": "date",
  "status": "string (pending/shipped/received/cancelled)",
  "items": [
    {
      "material_id": "uuid",
      "quantity": "float",
      "unit_price": "float"
    }
  ],
  "total_amount": "float"
}
```

---

#### **10. audit_logs**
Complete audit trail for GMP/21 CFR Part 11 compliance.

**Schema:**
```json
{
  "log_id": "uuid",
  "timestamp": "timestamp",
  "user_id": "string",
  "action": "string (create/update/delete/approve/reject)",
  "entity_type": "string (batch/test/document/material)",
  "entity_id": "uuid",
  "old_value": "json (nullable)",
  "new_value": "json",
  "ip_address": "string",
  "compliance_category": "string (GMP/21_CFR_Part_11)"
}
```

---

### **VECTOR COLLECTIONS (3)**

All vector collections use **OpenAI text-embedding-3-small (1536 dimensions)**.

#### **11. formulations (Vector)**
Drug formulations with semantic search capability.

**Schema:**
```json
{
  "formulation_id": "uuid",
  "medicine_id": "uuid",
  "formulation_name": "string",
  "ingredients": [
    {
      "ingredient_name": "string",
      "ratio": "string"
    }
  ],
  "manufacturing_process": "string (detailed text)",
  "$vector": "array<float>[1536]"
}
```

**Use Cases:**
- Find similar formulations for comparative analysis
- Identify alternative ingredients for substitution
- Quality comparison with historical batches

---

#### **12. adverse_events (Vector)**
Pharmacovigilance with pattern detection.

**Schema:**
```json
{
  "ae_id": "uuid",
  "medicine_id": "uuid",
  "patient_age": "int",
  "gender": "string",
  "event_description": "string (detailed narrative)",
  "severity": "string (mild/moderate/severe/life_threatening)",
  "reporter_type": "string (healthcare_professional/consumer)",
  "report_date": "date",
  "meddra_code": "string",
  "$vector": "array<float>[1536]"
}
```

**Use Cases:**
- Signal detection (identify unusual patterns)
- Find similar adverse event cases
- Automated MedDRA coding suggestions

---

#### **13. sop_documents (Vector)**
Standard Operating Procedures with semantic search.

**Schema:**
```json
{
  "sop_id": "uuid",
  "sop_number": "string",
  "title": "string",
  "department": "string (production/QC/QA/warehouse)",
  "content_text": "string (full SOP content)",
  "version": "string",
  "effective_date": "date",
  "$vector": "array<float>[1536]"
}
```

**Use Cases:**
- Semantic search: "How to handle OOS results?"
- Find relevant procedures by natural language query
- Training material recommendations

---

## 🤖 **AI AGENTS (6 Specialized Agents)**

### **1. Quality Control Agent**
**File:** `src/agents/quality_control_agent.py`

**Responsibilities:**
- Automated analysis of QC test results
- Out-of-Specification (OOS) detection
- Certificate of Analysis (COA) generation
- Batch release recommendations

**Key Methods:**
```python
def analyze_test_results(batch_id: str) -> dict
def detect_oos(test_results: list) -> list
def generate_coa(batch_id: str) -> dict
def recommend_batch_decision(batch_id: str) -> str  # approve/reject/retest
```

---

### **2. Regulatory Compliance Agent**
**File:** `src/agents/regulatory_compliance_agent.py`

**Responsibilities:**
- FDA/EMA compliance validation
- Document expiry tracking
- Audit trail generation
- Vector search for similar regulatory cases

**Key Methods:**
```python
def validate_batch_compliance(batch_id: str) -> dict
def check_document_expiry(days: int) -> list
def generate_audit_report(start_date: str, end_date: str) -> dict
def search_regulations(query: str) -> list  # vector search
```

---

### **3. Production Optimization Agent**
**File:** `src/agents/production_optimization_agent.py`

**Responsibilities:**
- Batch scheduling optimization
- Resource allocation (equipment, materials)
- Yield prediction
- Bottleneck identification

**Key Methods:**
```python
def optimize_batch_schedule(week: str) -> dict
def calculate_material_requirements(batch_id: str) -> dict
def predict_yield(batch_id: str) -> float
def identify_bottlenecks() -> list
```

---

### **4. Supply Chain Agent**
**File:** `src/agents/supply_chain_agent.py`

**Responsibilities:**
- Demand forecasting
- Supplier performance analysis
- Reorder point calculations
- Expiry date management

**Key Methods:**
```python
def forecast_demand(material_id: str, period: str) -> dict
def analyze_supplier_performance(supplier_id: str) -> dict
def calculate_reorder_points(material_id: str) -> float
def get_expiring_materials(days: int) -> list
```

---

### **5. Pharmacovigilance Agent**
**File:** `src/agents/pharmacovigilance_agent.py`

**Responsibilities:**
- Adverse event monitoring
- Signal detection (pattern analysis)
- MedDRA coding suggestions
- Vector search for similar cases

**Key Methods:**
```python
def analyze_adverse_event(ae_data: dict) -> dict
def detect_signals(medicine_id: str) -> list
def suggest_meddra_code(description: str) -> str
def find_similar_cases(ae_id: str, limit: int) -> list  # vector
```

---

### **6. Equipment Maintenance Agent**
**File:** `src/agents/equipment_maintenance_agent.py`

**Responsibilities:**
- Predictive maintenance scheduling
- Equipment downtime analysis
- Calibration tracking
- OEE (Overall Equipment Effectiveness) calculation

**Key Methods:**
```python
def schedule_maintenance(equipment_id: str) -> dict
def calculate_oee(equipment_id: str) -> float
def track_calibrations() -> list
def analyze_downtime(equipment_id: str, period: str) -> dict
```

---

## 🔌 **MCP SERVERS (5 Servers)**

All MCP servers extend **`MCPServerBase`** abstract class.

### **1. Medicine Management MCP**
**File:** `src/mcp_servers/medicine_mcp.py`

**Endpoints (6):**
```python
get_medicine_details(medicine_id: str) -> dict
search_medicines(name: str, category: str) -> list
get_formulation_info(medicine_id: str) -> dict
get_similar_formulations(medicine_id: str, limit: int) -> list  # vector
create_medicine(medicine_data: dict) -> str
update_medicine_status(medicine_id: str, status: str) -> bool
```

---

### **2. Quality Control MCP**
**File:** `src/mcp_servers/quality_control_mcp.py`

**Endpoints (6):**
```python
submit_qc_test(batch_id: str, test_data: dict) -> str
get_qc_results(batch_id: str) -> list
validate_batch_quality(batch_id: str) -> dict
get_oos_investigations(batch_id: str) -> list
approve_batch(batch_id: str, approver_id: str) -> bool
generate_coa(batch_id: str) -> dict
```

---

### **3. Production MCP**
**File:** `src/mcp_servers/production_mcp.py`

**Endpoints (6):**
```python
create_batch(product_id: str, quantity: int, schedule_date: str) -> str
get_batch_status(batch_id: str) -> dict
update_batch_stage(batch_id: str, stage: str) -> bool
get_production_schedule(date_range: tuple) -> list
allocate_equipment(batch_id: str, equipment_id: str) -> bool
calculate_material_requirements(batch_id: str) -> dict
```

---

### **4. Compliance MCP**
**File:** `src/mcp_servers/compliance_mcp.py`

**Endpoints (6):**
```python
check_regulatory_compliance(batch_id: str) -> dict
get_expiring_documents(days: int) -> list
submit_adverse_event(ae_data: dict) -> str
generate_audit_report(start_date: str, end_date: str) -> dict
search_regulations(query: str) -> list  # vector search
validate_gmp_compliance(facility_id: str) -> dict
```

---

### **5. Inventory MCP**
**File:** `src/mcp_servers/inventory_mcp.py`

**Endpoints (6):**
```python
get_material_inventory(material_id: str) -> dict
check_low_stock_items(threshold: float) -> list
create_purchase_order(supplier_id: str, items: list) -> str
update_material_quantity(material_id: str, quantity: float, transaction_type: str) -> bool
get_expiring_materials(days: int) -> list
forecast_material_demand(material_id: str, period: str) -> dict
```

---

## 🖥️ **STREAMLIT UI (6 Pages)**

### **1. Landing Page (app.py)**
- Real-time metrics dashboard
- Batches in production: 12
- Pending QC: 5
- Low stock alerts: 3 materials
- Compliance status: ✅ 98.7%

### **2. 💊 Medicine Catalog**
- Browse all medicines with filters
- Search by name, category, indication
- Vector search: "Find similar antibiotic formulations"
- View formulation details with ingredient breakdown

### **3. 🏭 Batch Production**
- Create new batch with material validation
- Real-time batch tracking (mixing → granulation → compression → coating → packaging)
- Equipment allocation interface
- Yield tracking and historical comparison

### **4. 🔬 Quality Control**
- Submit test results (dissolution, assay, microbial, stability)
- QC dashboard with pass/fail rates
- OOS investigation workflow
- COA generation and download

### **5. 📋 Regulatory & Compliance**
- Document repository with expiry alerts
- Adverse event reporting form
- Audit trail viewer with filters
- Compliance checklist (FDA/EMA/GMP)

### **6. 📊 Analytics Dashboard**
- Production KPIs (OEE, yield, cycle time)
- Quality metrics (right-first-time rate)
- Inventory trends (consumption patterns)
- Supplier performance scorecards

---

## 🔍 **VECTOR SEARCH USE CASES**

### **1. Similar Formulations**
**Query:** "Find formulations similar to Amoxicillin 500mg"

**Result:**
```json
[
  {"name": "Amoxicillin 250mg", "similarity": 0.892},
  {"name": "Ampicillin 500mg", "similarity": 0.847},
  {"name": "Cephalexin 500mg", "similarity": 0.721}
]
```

### **2. Adverse Event Pattern Detection**
**Query:** "Severe allergic reactions to beta-lactam antibiotics"

**Result:** Identifies 15 similar cases with similarity > 0.75

### **3. SOP Semantic Search**
**Query:** "How to handle out of specification results?"

**Result:** Returns relevant SOPs (QC-SOP-015, QC-SOP-027, QA-SOP-003)

---

## 🔐 **COMPLIANCE & SECURITY**

### **21 CFR Part 11 Compliance:**
- ✅ Electronic signatures for batch approvals
- ✅ Complete audit trail in `audit_logs` collection
- ✅ User access controls (RBAC)
- ✅ Data integrity (Astra DB encryption)

### **GMP (Good Manufacturing Practice):**
- ✅ Batch record completeness checks
- ✅ Equipment calibration tracking
- ✅ Material traceability
- ✅ Deviation management

---

## 📈 **PERFORMANCE METRICS**

| Metric | Target | Measurement |
|--------|--------|-------------|
| Batch Release Time | < 48 hours | From completion to approval |
| QC Test Turnaround | < 24 hours | From sample to result |
| OOS Detection Rate | 100% | AI-powered automated detection |
| Compliance Score | > 95% | Based on FDA/EMA audits |
| Equipment OEE | > 85% | Overall Equipment Effectiveness |
| Supplier On-Time Delivery | > 90% | Measured per supplier |

---

## 🚀 **DEPLOYMENT ARCHITECTURE**

```
┌─────────────────────────────────────────────────────┐
│  Streamlit Cloud / Azure App Service                │
│  (UI Layer - Port 8501)                             │
└─────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────┐
│  Python Application Server                          │
│  (AI Agents + MCP Servers)                          │
└─────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────┐
│  Astra DB Serverless (DataStax)                     │
│  (13 Collections - Global Distribution)             │
└─────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────┐
│  OpenAI API (Embeddings)                            │
│  (text-embedding-3-small - 1536D)                   │
└─────────────────────────────────────────────────────┘
```

---

## 📦 **TECHNOLOGY STACK**

| Component | Technology |
|-----------|-----------|
| **Database** | Astra DB Serverless (DataStax) |
| **Python SDK** | astrapy 2.1.0 |
| **UI Framework** | Streamlit |
| **AI/Embeddings** | OpenAI (text-embedding-3-small) |
| **MCP Protocol** | Custom MCPServerBase |
| **Logging** | Python logging + audit_logs collection |
| **Authentication** | Streamlit auth (future: OAuth2) |

---

## 🛠️ **DEVELOPMENT ROADMAP**

### **Phase 1: Foundation (Weeks 1-2)** ✅
- ✅ Astra DB setup (13 collections)
- ✅ MCPServerBase implementation
- ✅ Basic Streamlit UI structure
- ✅ Sample data generation

### **Phase 2: Core Features (Weeks 3-4)**
- [ ] Implement all 6 AI agents
- [ ] Build all 5 MCP servers
- [ ] Integrate vector search
- [ ] Complete UI pages

### **Phase 3: Quality & Compliance (Weeks 5-6)**
- [ ] QC workflow implementation
- [ ] Regulatory compliance validation
- [ ] Audit trail testing
- [ ] 21 CFR Part 11 compliance

### **Phase 4: Testing & Optimization (Weeks 7-8)**
- [ ] End-to-end testing
- [ ] Performance optimization
- [ ] Security audit
- [ ] User acceptance testing

### **Phase 5: Deployment (Week 9)**
- [ ] Production deployment
- [ ] User training
- [ ] Documentation finalization
- [ ] Go-live

---

## 📞 **SUPPORT & MAINTENANCE**

**Contact:** pharma-support@healthcare-digital.com  
**Documentation:** [GitHub Wiki](https://github.com/pharma-manufacturing/wiki)  
**Issue Tracking:** [GitHub Issues](https://github.com/pharma-manufacturing/issues)

---

## 📄 **APPENDIX**

### **A. Sample Queries**

**Get Medicine Details:**
```python
mcp = MedicineMCP()
result = mcp.call_endpoint("get_medicine_details", {"medicine_id": "medicine_123"})
```

**Create Batch:**
```python
mcp = ProductionMCP()
result = mcp.call_endpoint("create_batch", {
    "product_id": "medicine_123",
    "quantity": 10000,
    "schedule_date": "2025-12-20"
})
```

**Vector Search Similar Formulations:**
```python
mcp = MedicineMCP()
result = mcp.call_endpoint("get_similar_formulations", {
    "medicine_id": "medicine_123",
    "limit": 5
})
```

---

**Document Version History:**
- v1.0.0 (2025-12-18): Initial solution design

**Status:** ✅ Ready for Implementation
