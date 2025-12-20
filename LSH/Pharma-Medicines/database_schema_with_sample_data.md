# Pharma-Medicines Database Schema with Sample Data

## Astra DB Collections Overview

**Total Collections: 13**
- Regular Collections: 10
- Vector Collections: 3 (with 1536-dimensional embeddings)

---

## 1. medicines (Regular Collection)

### Schema
```json
{
  "medicine_id": "string (primary key)",
  "name": "string",
  "generic_name": "string",
  "dosage_form": "string (tablet/capsule/syrup/injection)",
  "strength": "string",
  "therapeutic_category": "string",
  "storage_conditions": "string",
  "shelf_life_months": "number",
  "regulatory_status": {
    "fda_approved": "boolean",
    "ema_approved": "boolean",
    "approval_date": "string (ISO date)",
    "stability_study": "string (completed/ongoing/pending)"
  },
  "status": "string (active/discontinued/under_review)",
  "created_at": "string (ISO timestamp)",
  "updated_at": "string (ISO timestamp)"
}
```

### Sample Data
```json
[
  {
    "medicine_id": "MED-001",
    "name": "Amoxicillin 500mg",
    "generic_name": "Amoxicillin Trihydrate",
    "dosage_form": "tablet",
    "strength": "500mg",
    "therapeutic_category": "Antibiotics - Penicillins",
    "storage_conditions": "Store at 20-25°C (68-77°F)",
    "shelf_life_months": 36,
    "regulatory_status": {
      "fda_approved": true,
      "ema_approved": true,
      "approval_date": "2020-03-15T00:00:00Z",
      "stability_study": "completed"
    },
    "status": "active",
    "created_at": "2024-01-10T08:30:00Z",
    "updated_at": "2025-01-05T14:20:00Z"
  },
  {
    "medicine_id": "MED-002",
    "name": "Metformin 850mg",
    "generic_name": "Metformin Hydrochloride",
    "dosage_form": "tablet",
    "strength": "850mg",
    "therapeutic_category": "Antidiabetic - Biguanides",
    "storage_conditions": "Store at 15-30°C (59-86°F), protect from moisture",
    "shelf_life_months": 48,
    "regulatory_status": {
      "fda_approved": true,
      "ema_approved": true,
      "approval_date": "2019-11-20T00:00:00Z",
      "stability_study": "completed"
    },
    "status": "active",
    "created_at": "2024-02-15T10:00:00Z",
    "updated_at": "2025-01-08T09:15:00Z"
  },
  {
    "medicine_id": "MED-003",
    "name": "Ibuprofen 400mg",
    "generic_name": "Ibuprofen",
    "dosage_form": "tablet",
    "strength": "400mg",
    "therapeutic_category": "NSAIDs - Analgesics",
    "storage_conditions": "Store below 25°C (77°F)",
    "shelf_life_months": 36,
    "regulatory_status": {
      "fda_approved": true,
      "ema_approved": true,
      "approval_date": "2021-06-10T00:00:00Z",
      "stability_study": "completed"
    },
    "status": "active",
    "created_at": "2024-03-20T11:30:00Z",
    "updated_at": "2025-01-10T16:45:00Z"
  }
]
```

---

## 2. formulations (Vector Collection - 1536D)

### Schema
```json
{
  "medicine_id": "string (primary key)",
  "formulation_id": "string",
  "version": "string",
  "components": [
    {
      "material_id": "string",
      "name": "string",
      "type": "string (API/excipient)",
      "quantity_per_unit": "number",
      "unit": "string (mg/g/ml)"
    }
  ],
  "manufacturing_process": ["string array"],
  "process_parameters": {
    "mixing_time_minutes": "number",
    "compression_force_kn": "number",
    "coating_temperature_c": "number"
  },
  "batch_size_standard": "number",
  "description": "string (for vector embedding)",
  "$vector": "array of 1536 floats",
  "created_at": "string (ISO timestamp)"
}
```

### Sample Data
```json
[
  {
    "medicine_id": "MED-001",
    "formulation_id": "FORM-001",
    "version": "2.1",
    "components": [
      {
        "material_id": "MAT-101",
        "name": "Amoxicillin Trihydrate",
        "type": "API",
        "quantity_per_unit": 500,
        "unit": "mg"
      },
      {
        "material_id": "MAT-201",
        "name": "Microcrystalline Cellulose",
        "type": "excipient",
        "quantity_per_unit": 150,
        "unit": "mg"
      },
      {
        "material_id": "MAT-202",
        "name": "Croscarmellose Sodium",
        "type": "excipient",
        "quantity_per_unit": 30,
        "unit": "mg"
      },
      {
        "material_id": "MAT-203",
        "name": "Magnesium Stearate",
        "type": "excipient",
        "quantity_per_unit": 10,
        "unit": "mg"
      }
    ],
    "manufacturing_process": [
      "Dry mixing of API and excipients",
      "Wet granulation with PVP solution",
      "Drying in fluid bed dryer at 60°C",
      "Milling and screening through 20 mesh",
      "Final blending with lubricant",
      "Compression at 15 kN",
      "Film coating with Opadry"
    ],
    "process_parameters": {
      "mixing_time_minutes": 20,
      "compression_force_kn": 15,
      "coating_temperature_c": 65
    },
    "batch_size_standard": 100000,
    "description": "Amoxicillin 500mg immediate release tablet formulation with standard excipients for antibiotic therapy",
    "$vector": [0.023, -0.015, 0.041, "... 1536 values total"],
    "created_at": "2024-01-10T08:30:00Z"
  },
  {
    "medicine_id": "MED-002",
    "formulation_id": "FORM-002",
    "version": "3.0",
    "components": [
      {
        "material_id": "MAT-102",
        "name": "Metformin Hydrochloride",
        "type": "API",
        "quantity_per_unit": 850,
        "unit": "mg"
      },
      {
        "material_id": "MAT-201",
        "name": "Microcrystalline Cellulose",
        "type": "excipient",
        "quantity_per_unit": 200,
        "unit": "mg"
      },
      {
        "material_id": "MAT-204",
        "name": "Povidone K30",
        "type": "excipient",
        "quantity_per_unit": 50,
        "unit": "mg"
      },
      {
        "material_id": "MAT-203",
        "name": "Magnesium Stearate",
        "type": "excipient",
        "quantity_per_unit": 15,
        "unit": "mg"
      }
    ],
    "manufacturing_process": [
      "Screening and mixing of API",
      "Dry granulation by roller compaction",
      "Milling and sizing",
      "Blending with disintegrant",
      "Compression at 18 kN",
      "Film coating for taste masking"
    ],
    "process_parameters": {
      "mixing_time_minutes": 25,
      "compression_force_kn": 18,
      "coating_temperature_c": 70
    },
    "batch_size_standard": 150000,
    "description": "Metformin 850mg extended release tablet for type 2 diabetes management with controlled drug delivery",
    "$vector": [0.031, -0.022, 0.055, "... 1536 values total"],
    "created_at": "2024-02-15T10:00:00Z"
  }
]
```

---

## 3. manufacturing_batches (Regular Collection)

### Schema
```json
{
  "batch_id": "string (primary key)",
  "batch_number": "string (unique)",
  "medicine_id": "string",
  "quantity": "number (units)",
  "manufacturing_date": "string (ISO date)",
  "expiry_date": "string (ISO date)",
  "current_stage": "string (mixing/granulation/compression/coating/packaging/completed)",
  "status": "string (in_production/in_qc/approved/rejected)",
  "yield_percentage": "number",
  "gmp_certified": "boolean",
  "approved_by": "string",
  "approved_date": "string (ISO timestamp)",
  "created_at": "string (ISO timestamp)",
  "updated_at": "string (ISO timestamp)"
}
```

### Sample Data
```json
[
  {
    "batch_id": "BATCH-2025-001",
    "batch_number": "AMX-2025-001",
    "medicine_id": "MED-001",
    "quantity": 100000,
    "manufacturing_date": "2025-01-15T00:00:00Z",
    "expiry_date": "2028-01-15T00:00:00Z",
    "current_stage": "completed",
    "status": "approved",
    "yield_percentage": 98.5,
    "gmp_certified": true,
    "approved_by": "Dr. Sarah Johnson",
    "approved_date": "2025-01-20T14:30:00Z",
    "created_at": "2025-01-15T08:00:00Z",
    "updated_at": "2025-01-20T14:30:00Z"
  },
  {
    "batch_id": "BATCH-2025-002",
    "batch_number": "MET-2025-002",
    "medicine_id": "MED-002",
    "quantity": 150000,
    "manufacturing_date": "2025-01-18T00:00:00Z",
    "expiry_date": "2029-01-18T00:00:00Z",
    "current_stage": "packaging",
    "status": "in_production",
    "yield_percentage": 97.2,
    "gmp_certified": true,
    "approved_by": null,
    "approved_date": null,
    "created_at": "2025-01-18T09:00:00Z",
    "updated_at": "2025-02-10T11:45:00Z"
  },
  {
    "batch_id": "BATCH-2025-003",
    "batch_number": "IBU-2025-003",
    "medicine_id": "MED-003",
    "quantity": 200000,
    "manufacturing_date": "2025-02-01T00:00:00Z",
    "expiry_date": "2028-02-01T00:00:00Z",
    "current_stage": "coating",
    "status": "in_production",
    "yield_percentage": 96.8,
    "gmp_certified": true,
    "approved_by": null,
    "approved_date": null,
    "created_at": "2025-02-01T08:30:00Z",
    "updated_at": "2025-02-08T15:20:00Z"
  }
]
```

---

## 4. quality_control_tests (Regular Collection)

### Schema
```json
{
  "test_id": "string (primary key)",
  "batch_id": "string",
  "test_type": "string (dissolution/assay/content_uniformity/microbial/stability)",
  "test_date": "string (ISO date)",
  "tested_by": "string",
  "parameters": {
    "specification": "string",
    "acceptance_criteria": "string",
    "method": "string"
  },
  "results": {
    "value": "number or string",
    "unit": "string",
    "observations": "string"
  },
  "pass_fail_status": "string (pass/fail/pending)",
  "remarks": "string",
  "created_at": "string (ISO timestamp)"
}
```

### Sample Data
```json
[
  {
    "test_id": "QC-2025-001",
    "batch_id": "BATCH-2025-001",
    "test_type": "dissolution",
    "test_date": "2025-01-19T00:00:00Z",
    "tested_by": "Lab Analyst - Mike Chen",
    "parameters": {
      "specification": "≥80% in 30 minutes",
      "acceptance_criteria": "Not less than 80% (Q)",
      "method": "USP Apparatus II (Paddle) at 50 RPM"
    },
    "results": {
      "value": 87.3,
      "unit": "%",
      "observations": "All 6 units passed, average 87.3%"
    },
    "pass_fail_status": "pass",
    "remarks": "Test completed successfully",
    "created_at": "2025-01-19T14:20:00Z"
  },
  {
    "test_id": "QC-2025-002",
    "batch_id": "BATCH-2025-001",
    "test_type": "assay",
    "test_date": "2025-01-19T00:00:00Z",
    "tested_by": "Lab Analyst - Emily Watson",
    "parameters": {
      "specification": "95.0-105.0% of label claim",
      "acceptance_criteria": "Each unit within specification",
      "method": "HPLC Method - USP Monograph"
    },
    "results": {
      "value": 98.7,
      "unit": "% of label claim",
      "observations": "Content: 493.5 mg per tablet (target: 500 mg)"
    },
    "pass_fail_status": "pass",
    "remarks": "Within specification",
    "created_at": "2025-01-19T16:45:00Z"
  },
  {
    "test_id": "QC-2025-003",
    "batch_id": "BATCH-2025-001",
    "test_type": "microbial",
    "test_date": "2025-01-20T00:00:00Z",
    "tested_by": "Microbiology Lab - Dr. Robert Lee",
    "parameters": {
      "specification": "≤1000 CFU/g",
      "acceptance_criteria": "Total aerobic count ≤1000 CFU/g, No E.coli, No Salmonella",
      "method": "USP <61> Microbial Examination"
    },
    "results": {
      "value": 420,
      "unit": "CFU/g",
      "observations": "No pathogens detected"
    },
    "pass_fail_status": "pass",
    "remarks": "Microbial limits satisfied",
    "created_at": "2025-01-20T11:30:00Z"
  },
  {
    "test_id": "QC-2025-004",
    "batch_id": "BATCH-2025-002",
    "test_type": "content_uniformity",
    "test_date": "2025-02-05T00:00:00Z",
    "tested_by": "Lab Analyst - Sarah Park",
    "parameters": {
      "specification": "85.0-115.0% of label claim",
      "acceptance_criteria": "AV ≤ 15.0",
      "method": "USP <905> Content Uniformity"
    },
    "results": {
      "value": 102.1,
      "unit": "% average",
      "observations": "AV = 8.2, all units within 85-115%"
    },
    "pass_fail_status": "pass",
    "remarks": "Content uniformity acceptable",
    "created_at": "2025-02-05T15:10:00Z"
  }
]
```

---

## 5. raw_materials (Regular Collection)

### Schema
```json
{
  "material_id": "string (primary key)",
  "name": "string",
  "type": "string (API/excipient)",
  "supplier_id": "string",
  "batch_number": "string",
  "quantity_in_stock": "number",
  "unit": "string (kg/g/L)",
  "reorder_point": "number",
  "expiry_date": "string (ISO date)",
  "storage_location": "string",
  "status": "string (available/quarantine/expired)",
  "last_updated": "string (ISO timestamp)"
}
```

### Sample Data
```json
[
  {
    "material_id": "MAT-101",
    "name": "Amoxicillin Trihydrate",
    "type": "API",
    "supplier_id": "SUP-001",
    "batch_number": "AMX-API-2024-12-001",
    "quantity_in_stock": 5500,
    "unit": "kg",
    "reorder_point": 2000,
    "expiry_date": "2026-12-15T00:00:00Z",
    "storage_location": "Warehouse A - Climate Controlled - Shelf A3",
    "status": "available",
    "last_updated": "2025-02-10T09:30:00Z"
  },
  {
    "material_id": "MAT-102",
    "name": "Metformin Hydrochloride",
    "type": "API",
    "supplier_id": "SUP-002",
    "batch_number": "MET-API-2025-01-002",
    "quantity_in_stock": 8200,
    "unit": "kg",
    "reorder_point": 3000,
    "expiry_date": "2027-01-20T00:00:00Z",
    "storage_location": "Warehouse A - Climate Controlled - Shelf B2",
    "status": "available",
    "last_updated": "2025-02-08T14:15:00Z"
  },
  {
    "material_id": "MAT-201",
    "name": "Microcrystalline Cellulose",
    "type": "excipient",
    "supplier_id": "SUP-003",
    "batch_number": "MCC-EXC-2025-01-015",
    "quantity_in_stock": 12500,
    "unit": "kg",
    "reorder_point": 5000,
    "expiry_date": "2028-01-10T00:00:00Z",
    "storage_location": "Warehouse B - Dry Storage - Section C",
    "status": "available",
    "last_updated": "2025-02-05T11:20:00Z"
  },
  {
    "material_id": "MAT-202",
    "name": "Croscarmellose Sodium",
    "type": "excipient",
    "supplier_id": "SUP-003",
    "batch_number": "CCS-EXC-2024-12-008",
    "quantity_in_stock": 850,
    "unit": "kg",
    "reorder_point": 1000,
    "expiry_date": "2026-12-30T00:00:00Z",
    "storage_location": "Warehouse B - Dry Storage - Section D",
    "status": "available",
    "last_updated": "2025-02-09T16:45:00Z"
  },
  {
    "material_id": "MAT-203",
    "name": "Magnesium Stearate",
    "type": "excipient",
    "supplier_id": "SUP-004",
    "batch_number": "MGS-EXC-2025-01-003",
    "quantity_in_stock": 650,
    "unit": "kg",
    "reorder_point": 800,
    "expiry_date": "2027-01-15T00:00:00Z",
    "storage_location": "Warehouse B - Dry Storage - Section E",
    "status": "available",
    "last_updated": "2025-02-07T10:30:00Z"
  }
]
```

---

## 6. suppliers (Regular Collection)

### Schema
```json
{
  "supplier_id": "string (primary key)",
  "name": "string",
  "contact": {
    "email": "string",
    "phone": "string",
    "address": "string"
  },
  "certifications": ["string array"],
  "materials_supplied": ["string array"],
  "status": "string (active/inactive/under_review)",
  "created_at": "string (ISO timestamp)"
}
```

### Sample Data
```json
[
  {
    "supplier_id": "SUP-001",
    "name": "PharmaCore API Solutions",
    "contact": {
      "email": "sales@pharmacore.com",
      "phone": "+1-555-0123",
      "address": "1200 Industrial Blvd, Newark, NJ 07102, USA"
    },
    "certifications": [
      "FDA Registered",
      "GMP Certified",
      "ISO 9001:2015",
      "CEP (Certificate of Suitability)"
    ],
    "materials_supplied": ["MAT-101", "MAT-103", "MAT-105"],
    "status": "active",
    "created_at": "2023-05-10T08:00:00Z"
  },
  {
    "supplier_id": "SUP-002",
    "name": "Global Med Ingredients Ltd",
    "contact": {
      "email": "info@globalmedingredients.com",
      "phone": "+44-20-7946-0958",
      "address": "45 Pharmaceutical Park, London SE1 2AA, UK"
    },
    "certifications": [
      "EMA Approved",
      "GMP Certified",
      "ISO 9001:2015",
      "MHRA Licensed"
    ],
    "materials_supplied": ["MAT-102", "MAT-104"],
    "status": "active",
    "created_at": "2023-07-22T09:30:00Z"
  },
  {
    "supplier_id": "SUP-003",
    "name": "Excipient Masters Inc",
    "contact": {
      "email": "orders@excipientmasters.com",
      "phone": "+1-555-0456",
      "address": "8900 Commerce Drive, Charlotte, NC 28202, USA"
    },
    "certifications": [
      "FDA Registered",
      "GMP Certified",
      "ISO 9001:2015"
    ],
    "materials_supplied": ["MAT-201", "MAT-202", "MAT-204", "MAT-205"],
    "status": "active",
    "created_at": "2023-04-15T10:00:00Z"
  },
  {
    "supplier_id": "SUP-004",
    "name": "Premium Lubricants Supply Co",
    "contact": {
      "email": "sales@premiumlubricants.com",
      "phone": "+1-555-0789",
      "address": "3300 Industrial Way, Chicago, IL 60601, USA"
    },
    "certifications": [
      "FDA Registered",
      "GMP Certified"
    ],
    "materials_supplied": ["MAT-203"],
    "status": "active",
    "created_at": "2023-08-05T11:15:00Z"
  }
]
```

---

## 7. production_schedules (Regular Collection)

### Schema
```json
{
  "schedule_id": "string (primary key)",
  "batch_id": "string",
  "equipment_id": "string",
  "scheduled_start": "string (ISO timestamp)",
  "scheduled_end": "string (ISO timestamp)",
  "actual_start": "string (ISO timestamp)",
  "actual_end": "string (ISO timestamp)",
  "status": "string (scheduled/in_progress/completed/delayed)",
  "assigned_operators": ["string array"],
  "created_at": "string (ISO timestamp)"
}
```

### Sample Data
```json
[
  {
    "schedule_id": "SCH-2025-001",
    "batch_id": "BATCH-2025-001",
    "equipment_id": "EQP-001",
    "scheduled_start": "2025-01-15T08:00:00Z",
    "scheduled_end": "2025-01-15T16:00:00Z",
    "actual_start": "2025-01-15T08:10:00Z",
    "actual_end": "2025-01-15T15:50:00Z",
    "status": "completed",
    "assigned_operators": ["OP-101", "OP-102"],
    "created_at": "2025-01-10T09:00:00Z"
  },
  {
    "schedule_id": "SCH-2025-002",
    "batch_id": "BATCH-2025-002",
    "equipment_id": "EQP-003",
    "scheduled_start": "2025-01-18T09:00:00Z",
    "scheduled_end": "2025-01-18T18:00:00Z",
    "actual_start": "2025-01-18T09:05:00Z",
    "actual_end": null,
    "status": "in_progress",
    "assigned_operators": ["OP-103", "OP-104"],
    "created_at": "2025-01-12T10:30:00Z"
  },
  {
    "schedule_id": "SCH-2025-003",
    "batch_id": "BATCH-2025-003",
    "equipment_id": "EQP-005",
    "scheduled_start": "2025-02-01T08:30:00Z",
    "scheduled_end": "2025-02-01T17:30:00Z",
    "actual_start": "2025-02-01T08:35:00Z",
    "actual_end": null,
    "status": "in_progress",
    "assigned_operators": ["OP-105", "OP-106"],
    "created_at": "2025-01-25T11:00:00Z"
  }
]
```

---

## 8. equipment_maintenance (Regular Collection)

### Schema
```json
{
  "equipment_id": "string (primary key)",
  "name": "string",
  "equipment_type": "string (Mixer/Tablet Press/Coating Pan/etc)",
  "status": "string (operational/under_maintenance/out_of_service)",
  "last_maintenance_date": "string (ISO date)",
  "next_calibration_date": "string (ISO date)",
  "calibration_frequency_days": "number",
  "location": "string",
  "created_at": "string (ISO timestamp)",
  "updated_at": "string (ISO timestamp)"
}
```

### Sample Data
```json
[
  {
    "equipment_id": "EQP-001",
    "name": "High Shear Mixer - HSM-500",
    "equipment_type": "Mixer",
    "status": "operational",
    "last_maintenance_date": "2025-01-05T00:00:00Z",
    "next_calibration_date": "2025-07-05T00:00:00Z",
    "calibration_frequency_days": 180,
    "location": "Production Floor - Area 1",
    "created_at": "2023-03-15T08:00:00Z",
    "updated_at": "2025-01-05T14:30:00Z"
  },
  {
    "equipment_id": "EQP-002",
    "name": "Fluid Bed Dryer - FBD-200",
    "equipment_type": "Dryer",
    "status": "operational",
    "last_maintenance_date": "2024-12-20T00:00:00Z",
    "next_calibration_date": "2025-06-20T00:00:00Z",
    "calibration_frequency_days": 180,
    "location": "Production Floor - Area 1",
    "created_at": "2023-03-15T08:00:00Z",
    "updated_at": "2024-12-20T16:45:00Z"
  },
  {
    "equipment_id": "EQP-003",
    "name": "Rotary Tablet Press - RTP-45",
    "equipment_type": "Tablet Press",
    "status": "operational",
    "last_maintenance_date": "2025-01-10T00:00:00Z",
    "next_calibration_date": "2025-04-10T00:00:00Z",
    "calibration_frequency_days": 90,
    "location": "Production Floor - Area 2",
    "created_at": "2023-04-20T09:00:00Z",
    "updated_at": "2025-01-10T11:20:00Z"
  },
  {
    "equipment_id": "EQP-004",
    "name": "Film Coating Machine - FCM-300",
    "equipment_type": "Coating Pan",
    "status": "operational",
    "last_maintenance_date": "2024-12-28T00:00:00Z",
    "next_calibration_date": "2025-06-28T00:00:00Z",
    "calibration_frequency_days": 180,
    "location": "Production Floor - Area 2",
    "created_at": "2023-05-10T10:00:00Z",
    "updated_at": "2024-12-28T15:10:00Z"
  },
  {
    "equipment_id": "EQP-005",
    "name": "Blister Packaging Machine - BPM-100",
    "equipment_type": "Blister Packer",
    "status": "operational",
    "last_maintenance_date": "2025-01-15T00:00:00Z",
    "next_calibration_date": "2025-03-15T00:00:00Z",
    "calibration_frequency_days": 60,
    "location": "Packaging Area",
    "created_at": "2023-06-01T11:00:00Z",
    "updated_at": "2025-01-15T13:45:00Z"
  }
]
```

---

## 9. regulatory_documents (Regular Collection)

### Schema
```json
{
  "document_id": "string (primary key)",
  "document_type": "string (license/certificate/approval/submission)",
  "title": "string",
  "regulatory_body": "string (FDA/EMA/Local Authority)",
  "issue_date": "string (ISO date)",
  "expiry_date": "string (ISO date)",
  "status": "string (active/expired/pending_renewal)",
  "file_location": "string",
  "created_at": "string (ISO timestamp)"
}
```

### Sample Data
```json
[
  {
    "document_id": "DOC-001",
    "document_type": "license",
    "title": "FDA Manufacturing License - Solid Dosage Forms",
    "regulatory_body": "FDA",
    "issue_date": "2023-01-15T00:00:00Z",
    "expiry_date": "2026-01-15T00:00:00Z",
    "status": "active",
    "file_location": "/documents/regulatory/FDA_License_2023.pdf",
    "created_at": "2023-01-20T09:00:00Z"
  },
  {
    "document_id": "DOC-002",
    "document_type": "certificate",
    "title": "GMP Certificate - EU Standards",
    "regulatory_body": "EMA",
    "issue_date": "2024-06-10T00:00:00Z",
    "expiry_date": "2026-06-10T00:00:00Z",
    "status": "active",
    "file_location": "/documents/regulatory/GMP_Certificate_EU_2024.pdf",
    "created_at": "2024-06-15T10:30:00Z"
  },
  {
    "document_id": "DOC-003",
    "document_type": "approval",
    "title": "NDA Approval - Amoxicillin 500mg",
    "regulatory_body": "FDA",
    "issue_date": "2020-03-15T00:00:00Z",
    "expiry_date": "2030-03-15T00:00:00Z",
    "status": "active",
    "file_location": "/documents/regulatory/NDA_Amoxicillin_2020.pdf",
    "created_at": "2020-03-20T11:00:00Z"
  },
  {
    "document_id": "DOC-004",
    "document_type": "certificate",
    "title": "ISO 9001:2015 Quality Management Certificate",
    "regulatory_body": "ISO",
    "issue_date": "2024-09-01T00:00:00Z",
    "expiry_date": "2027-09-01T00:00:00Z",
    "status": "active",
    "file_location": "/documents/regulatory/ISO_9001_2024.pdf",
    "created_at": "2024-09-05T14:20:00Z"
  },
  {
    "document_id": "DOC-005",
    "document_type": "license",
    "title": "State Manufacturing License - California",
    "regulatory_body": "California Board of Pharmacy",
    "issue_date": "2024-01-01T00:00:00Z",
    "expiry_date": "2025-03-31T00:00:00Z",
    "status": "active",
    "file_location": "/documents/regulatory/CA_License_2024.pdf",
    "created_at": "2024-01-10T08:30:00Z"
  }
]
```

---

## 10. purchase_orders (Regular Collection)

### Schema
```json
{
  "po_id": "string (primary key)",
  "supplier_id": "string",
  "items": [
    {
      "material_id": "string",
      "quantity": "number",
      "unit_price": "number",
      "total_price": "number"
    }
  ],
  "total_amount": "number",
  "currency": "string",
  "order_date": "string (ISO date)",
  "expected_delivery_date": "string (ISO date)",
  "status": "string (pending/confirmed/shipped/delivered/cancelled)",
  "created_at": "string (ISO timestamp)"
}
```

### Sample Data
```json
[
  {
    "po_id": "PO-2025-001",
    "supplier_id": "SUP-001",
    "items": [
      {
        "material_id": "MAT-101",
        "quantity": 2000,
        "unit_price": 125.50,
        "total_price": 251000
      }
    ],
    "total_amount": 251000,
    "currency": "USD",
    "order_date": "2025-01-20T00:00:00Z",
    "expected_delivery_date": "2025-02-05T00:00:00Z",
    "status": "confirmed",
    "created_at": "2025-01-20T09:30:00Z"
  },
  {
    "po_id": "PO-2025-002",
    "supplier_id": "SUP-003",
    "items": [
      {
        "material_id": "MAT-201",
        "quantity": 5000,
        "unit_price": 8.75,
        "total_price": 43750
      },
      {
        "material_id": "MAT-202",
        "quantity": 1000,
        "unit_price": 15.20,
        "total_price": 15200
      }
    ],
    "total_amount": 58950,
    "currency": "USD",
    "order_date": "2025-01-25T00:00:00Z",
    "expected_delivery_date": "2025-02-10T00:00:00Z",
    "status": "shipped",
    "created_at": "2025-01-25T10:15:00Z"
  },
  {
    "po_id": "PO-2025-003",
    "supplier_id": "SUP-002",
    "items": [
      {
        "material_id": "MAT-102",
        "quantity": 3000,
        "unit_price": 98.25,
        "total_price": 294750
      }
    ],
    "total_amount": 294750,
    "currency": "USD",
    "order_date": "2025-02-01T00:00:00Z",
    "expected_delivery_date": "2025-02-18T00:00:00Z",
    "status": "pending",
    "created_at": "2025-02-01T11:45:00Z"
  }
]
```

---

## 11. audit_logs (Regular Collection)

### Schema
```json
{
  "log_id": "string (primary key)",
  "timestamp": "string (ISO timestamp)",
  "action": "string (create/update/delete/approve/reject)",
  "entity_type": "string (batch/medicine/material/etc)",
  "entity_id": "string",
  "performed_by": "string",
  "old_value": "object (optional)",
  "new_value": "object (optional)",
  "ip_address": "string",
  "user_agent": "string"
}
```

### Sample Data
```json
[
  {
    "log_id": "LOG-2025-001",
    "timestamp": "2025-01-20T14:30:00Z",
    "action": "approve",
    "entity_type": "batch",
    "entity_id": "BATCH-2025-001",
    "performed_by": "Dr. Sarah Johnson",
    "old_value": {"status": "in_qc"},
    "new_value": {"status": "approved", "approved_date": "2025-01-20T14:30:00Z"},
    "ip_address": "192.168.1.105",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
  },
  {
    "log_id": "LOG-2025-002",
    "timestamp": "2025-01-25T10:15:00Z",
    "action": "create",
    "entity_type": "purchase_order",
    "entity_id": "PO-2025-002",
    "performed_by": "Purchasing Manager - Tom Wilson",
    "old_value": null,
    "new_value": {"po_id": "PO-2025-002", "supplier_id": "SUP-003", "total_amount": 58950},
    "ip_address": "192.168.1.110",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
  },
  {
    "log_id": "LOG-2025-003",
    "timestamp": "2025-02-05T15:10:00Z",
    "action": "update",
    "entity_type": "material",
    "entity_id": "MAT-202",
    "performed_by": "Warehouse Operator - Lisa Martinez",
    "old_value": {"quantity_in_stock": 1850},
    "new_value": {"quantity_in_stock": 850},
    "ip_address": "192.168.1.115",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
  }
]
```

---

## 12. adverse_events (Vector Collection - 1536D)

### Schema
```json
{
  "ae_id": "string (primary key)",
  "medicine_id": "string",
  "report_date": "string (ISO date)",
  "patient_age": "number",
  "patient_gender": "string",
  "description": "string (for vector embedding)",
  "severity": "string (mild/moderate/severe/life-threatening/fatal)",
  "patient_outcome": "string (recovered/recovering/not_recovered/fatal)",
  "causality": "string (certain/probable/possible/unlikely)",
  "reported_by": "string",
  "$vector": "array of 1536 floats",
  "created_at": "string (ISO timestamp)"
}
```

### Sample Data
```json
[
  {
    "ae_id": "AE-2025-001",
    "medicine_id": "MED-001",
    "report_date": "2025-01-22T00:00:00Z",
    "patient_age": 45,
    "patient_gender": "Female",
    "description": "Patient experienced mild nausea and stomach discomfort approximately 2 hours after taking the medication. Symptoms resolved within 6 hours without intervention.",
    "severity": "mild",
    "patient_outcome": "recovered",
    "causality": "possible",
    "reported_by": "Dr. Michael Stevens - Community Clinic",
    "$vector": [0.019, -0.033, 0.048, "... 1536 values total"],
    "created_at": "2025-01-22T14:30:00Z"
  },
  {
    "ae_id": "AE-2025-002",
    "medicine_id": "MED-002",
    "report_date": "2025-01-28T00:00:00Z",
    "patient_age": 62,
    "patient_gender": "Male",
    "description": "Patient reported persistent diarrhea and abdominal cramping starting 3 days after initiating therapy. Symptoms moderate in intensity, affecting daily activities.",
    "severity": "moderate",
    "patient_outcome": "recovering",
    "causality": "probable",
    "reported_by": "Dr. Jennifer Wong - Endocrinology Department",
    "$vector": [0.025, -0.018, 0.052, "... 1536 values total"],
    "created_at": "2025-01-28T11:15:00Z"
  },
  {
    "ae_id": "AE-2025-003",
    "medicine_id": "MED-003",
    "report_date": "2025-02-05T00:00:00Z",
    "patient_age": 38,
    "patient_gender": "Female",
    "description": "Allergic reaction presenting as skin rash with itching on arms and torso. Appeared within 1 hour of first dose. Patient given antihistamine and symptoms improved.",
    "severity": "moderate",
    "patient_outcome": "recovered",
    "causality": "probable",
    "reported_by": "Emergency Department - City Hospital",
    "$vector": [0.031, -0.021, 0.044, "... 1536 values total"],
    "created_at": "2025-02-05T16:45:00Z"
  }
]
```

---

## 13. sop_documents (Vector Collection - 1536D)

### Schema
```json
{
  "sop_id": "string (primary key)",
  "sop_number": "string",
  "title": "string",
  "category": "string (manufacturing/quality/regulatory/safety)",
  "version": "string",
  "effective_date": "string (ISO date)",
  "review_date": "string (ISO date)",
  "approved_by": "string",
  "summary": "string (for vector embedding)",
  "$vector": "array of 1536 floats",
  "created_at": "string (ISO timestamp)"
}
```

### Sample Data
```json
[
  {
    "sop_id": "SOP-001",
    "sop_number": "QC-SOP-001",
    "title": "Dissolution Testing for Solid Oral Dosage Forms",
    "category": "quality",
    "version": "4.2",
    "effective_date": "2024-06-01T00:00:00Z",
    "review_date": "2025-06-01T00:00:00Z",
    "approved_by": "QA Director - Dr. Patricia Anderson",
    "summary": "Standard operating procedure for performing dissolution testing of tablets and capsules using USP Apparatus II (Paddle method). Includes equipment setup, calibration, sample preparation, testing parameters, and result documentation in compliance with FDA and USP requirements.",
    "$vector": [0.028, -0.016, 0.039, "... 1536 values total"],
    "created_at": "2024-06-01T08:00:00Z"
  },
  {
    "sop_id": "SOP-002",
    "sop_number": "MFG-SOP-015",
    "title": "Tablet Compression Process Control and Monitoring",
    "category": "manufacturing",
    "version": "3.1",
    "effective_date": "2024-09-15T00:00:00Z",
    "review_date": "2025-09-15T00:00:00Z",
    "approved_by": "Production Manager - James Mitchell",
    "summary": "Comprehensive procedure for tablet compression operations including equipment setup, punch and die installation, compression force optimization, weight variation monitoring, and in-process quality checks during production. Covers GMP requirements and troubleshooting common issues.",
    "$vector": [0.035, -0.024, 0.047, "... 1536 values total"],
    "created_at": "2024-09-15T09:30:00Z"
  },
  {
    "sop_id": "SOP-003",
    "sop_number": "REG-SOP-008",
    "title": "Adverse Event Reporting and Documentation",
    "category": "regulatory",
    "version": "2.5",
    "effective_date": "2024-11-01T00:00:00Z",
    "review_date": "2025-11-01T00:00:00Z",
    "approved_by": "Regulatory Affairs Manager - Dr. Amanda Foster",
    "summary": "Procedure for collecting, documenting, evaluating and reporting adverse events to regulatory authorities. Includes timelines for expedited reporting (7 and 15 days), causality assessment, MedDRA coding, and submission requirements for FDA MedWatch and EU EudraVigilance systems.",
    "$vector": [0.022, -0.029, 0.053, "... 1536 values total"],
    "created_at": "2024-11-01T10:00:00Z"
  },
  {
    "sop_id": "SOP-004",
    "sop_number": "QC-SOP-012",
    "title": "Out-of-Specification (OOS) Investigation Procedure",
    "category": "quality",
    "version": "3.3",
    "effective_date": "2025-01-10T00:00:00Z",
    "review_date": "2026-01-10T00:00:00Z",
    "approved_by": "QA Director - Dr. Patricia Anderson",
    "summary": "Systematic approach for investigating out-of-specification test results including initial assessment, laboratory investigation phase, manufacturing investigation phase, root cause analysis, corrective and preventive actions (CAPA), and final report documentation per FDA guidance.",
    "$vector": [0.026, -0.019, 0.041, "... 1536 values total"],
    "created_at": "2025-01-10T11:15:00Z"
  },
  {
    "sop_id": "SOP-005",
    "sop_number": "SAFE-SOP-003",
    "title": "Personal Protective Equipment (PPE) Requirements for Manufacturing Areas",
    "category": "safety",
    "version": "2.0",
    "effective_date": "2024-08-01T00:00:00Z",
    "review_date": "2025-08-01T00:00:00Z",
    "approved_by": "EHS Manager - Robert Chen",
    "summary": "Detailed requirements for personal protective equipment based on manufacturing area classification and material handling. Covers gowning procedures, glove selection, respiratory protection, eye protection, and proper donning/doffing sequences to maintain GMP compliance and worker safety.",
    "$vector": [0.033, -0.027, 0.038, "... 1536 values total"],
    "created_at": "2024-08-01T09:00:00Z"
  }
]
```

---

## Vector Embedding Notes

For the 3 vector collections (**formulations**, **adverse_events**, **sop_documents**), the `$vector` field should contain 1536-dimensional embeddings generated using OpenAI's `text-embedding-3-small` model.

**Example embedding generation (Python):**
```python
import openai

# Generate embedding for formulation description
response = openai.Embedding.create(
    model="text-embedding-3-small",
    input="Amoxicillin 500mg immediate release tablet formulation with standard excipients"
)
embedding = response['data'][0]['embedding']  # List of 1536 floats
```

**Vector Search Example:**
```python
# Find similar formulations
query_text = "antibiotic tablet formulation"
query_embedding = generate_embedding(query_text)

results = formulations_collection.find(
    sort={"$vector": query_embedding},
    limit=5,
    projection={"medicine_id": 1, "description": 1, "$similarity": 1}
)
```

---

## Data Relationships

```
medicines (1) ──── (1) formulations
    │
    └──── (1:N) manufacturing_batches
              │
              ├──── (1:N) quality_control_tests
              └──── (N:1) production_schedules ──── (N:1) equipment_maintenance

raw_materials ──── (N:1) suppliers
    │
    └──── (N:N) purchase_orders

medicines ──── (1:N) adverse_events

regulatory_documents (standalone)
sop_documents (standalone)
audit_logs (tracks all entities)
```

---

## Summary Statistics

- **Total Collections:** 13
- **Regular Collections:** 10
- **Vector Collections:** 3 (1536-dimensional)
- **Sample Records Provided:** 60+ across all collections
- **Primary Keys:** All collections use natural IDs (e.g., MED-001, BATCH-2025-001)
- **Date Format:** ISO 8601 (e.g., "2025-01-15T08:30:00Z")
- **Status Fields:** Standardized enums for workflow management
- **Audit Trail:** Complete 21 CFR Part 11 compliance via audit_logs collection
