"""
Regulatory Compliance Page
Document management, adverse event reporting, and audit trails
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from database.astra_helper import AstraDBHelper
from mcp_servers.compliance_mcp import ComplianceMCPServer

# Page configuration
st.set_page_config(
    page_title="Regulatory Compliance",
    page_icon="📜",
    layout="wide"
)

# Initialize
if 'db_helper' not in st.session_state:
    st.session_state.db_helper = AstraDBHelper()
if 'compliance_mcp' not in st.session_state:
    st.session_state.compliance_mcp = ComplianceMCPServer()

# Header
st.title("📜 Regulatory Compliance Management")
st.markdown("FDA, EMA, GMP compliance monitoring and adverse event reporting")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Regulatory Documents", "⚠️ Adverse Events", "📊 Audit Reports", "🔍 Search SOPs", "✅ GMP Validation"])

with tab1:
    st.markdown("### Regulatory Documents Management")
    
    # Document status overview
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        docs = list(st.session_state.db_helper.regulatory_documents.find({}, limit=500))
        
        active_docs = sum(1 for d in docs if d.get("status") == "active")
        expired_docs = sum(1 for d in docs if d.get("status") == "expired")
        
        # Expiring soon (60 days)
        expiry_date = datetime.utcnow() + timedelta(days=60)
        expiring_soon = sum(1 for d in docs 
                          if d.get("status") == "active" and 
                          d.get("expiry_date") and 
                          datetime.fromisoformat(d.get("expiry_date").replace('Z', '+00:00')) <= expiry_date)
        
        with col1:
            st.metric("Total Documents", len(docs))
        with col2:
            st.metric("Active", active_docs)
        with col3:
            st.metric("Expiring Soon", expiring_soon, delta_color="inverse")
        with col4:
            st.metric("Expired", expired_docs, delta_color="inverse")
        
        st.markdown("---")
        
        # Expiring documents
        st.markdown("### 📅 Expiring Documents (Next 60 Days)")
        
        result = st.session_state.compliance_mcp.call_endpoint("get_expiring_documents", {"days": 60})
        
        if result.get("status") == "success":
            expiring = result.get("data", [])
            
            if expiring:
                st.warning(f"⚠️ {len(expiring)} documents expiring in the next 60 days")
                
                df = pd.DataFrame([{
                    "Document ID": d.get("document_id", "N/A"),
                    "Type": d.get("document_type", "N/A"),
                    "Title": d.get("title", "N/A"),
                    "Regulatory Body": d.get("regulatory_body", "N/A"),
                    "Expiry Date": d.get("expiry_date", "N/A")[:10],
                    "Days Until Expiry": d.get("days_until_expiry", 0),
                    "Urgency": d.get("urgency_level", "N/A")
                } for d in expiring])
                
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.success("✅ No documents expiring in the next 60 days")
        
        # All documents
        st.markdown("---")
        st.markdown("### 📚 All Regulatory Documents")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            doc_type_filter = st.selectbox("Type", ["All", "license", "certificate", "approval"])
        with col2:
            reg_body_filter = st.selectbox("Regulatory Body", ["All", "FDA", "EMA", "ISO", "WHO", "DEA"])
        with col3:
            status_filter = st.selectbox("Status", ["All", "active", "expired"])
        
        # Apply filters
        filtered_docs = docs
        if doc_type_filter != "All":
            filtered_docs = [d for d in filtered_docs if d.get("document_type") == doc_type_filter]
        if reg_body_filter != "All":
            filtered_docs = [d for d in filtered_docs if reg_body_filter in d.get("regulatory_body", "")]
        if status_filter != "All":
            filtered_docs = [d for d in filtered_docs if d.get("status") == status_filter]
        
        if filtered_docs:
            doc_df = pd.DataFrame([{
                "Document ID": d.get("document_id", "N/A"),
                "Type": d.get("document_type", "N/A"),
                "Title": d.get("title", "N/A"),
                "Regulatory Body": d.get("regulatory_body", "N/A"),
                "Issue Date": d.get("issue_date", "N/A")[:10],
                "Expiry Date": d.get("expiry_date", "N/A")[:10],
                "Status": d.get("status", "N/A")
            } for d in filtered_docs])
            
            st.dataframe(doc_df, use_container_width=True, hide_index=True)
        else:
            st.info("No documents found matching the criteria")
    
    except Exception as e:
        st.error(f"Error loading documents: {str(e)}")

with tab2:
    st.markdown("### Adverse Event Reporting (Pharmacovigilance)")
    
    # AE statistics
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        aes = list(st.session_state.db_helper.adverse_events.find({}, limit=500))
        
        # Recent AEs (30 days)
        recent_date = datetime.utcnow() - timedelta(days=30)
        recent_aes = [ae for ae in aes 
                     if ae.get("report_date") and 
                     datetime.fromisoformat(ae.get("report_date").replace('Z', '+00:00')) >= recent_date]
        
        # Severity counts
        serious_aes = sum(1 for ae in aes if ae.get("severity") in ["serious", "fatal"])
        moderate_aes = sum(1 for ae in aes if ae.get("severity") == "moderate")
        mild_aes = sum(1 for ae in aes if ae.get("severity") == "mild")
        
        with col1:
            st.metric("Total AEs", len(aes))
        with col2:
            st.metric("Recent (30d)", len(recent_aes))
        with col3:
            st.metric("Serious/Fatal", serious_aes, delta_color="inverse")
        with col4:
            st.metric("Moderate", moderate_aes)
        
        st.markdown("---")
        
        # Submit new AE
        st.markdown("### ➕ Report New Adverse Event")
        st.info("🤖 AI-powered causality assessment and severity classification")
        
        with st.form("ae_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                ae_id = st.text_input("AE ID*", placeholder="AE-YYYY-XXX")
                
                medicines = list(st.session_state.db_helper.medicines.find({"status": "active"}, limit=100))
                medicine_options = {m.get("medicine_id"): m.get("name") for m in medicines}
                
                medicine_id = st.selectbox(
                    "Medicine*",
                    options=list(medicine_options.keys()),
                    format_func=lambda x: f"{x} - {medicine_options.get(x, 'N/A')}"
                )
                
                report_date = st.date_input("Report Date*", value=datetime.now())
                patient_age = st.number_input("Patient Age*", min_value=0, max_value=120, value=50)
                patient_gender = st.selectbox("Patient Gender*", ["Male", "Female", "Other"])
            
            with col2:
                description = st.text_area("AE Description*", placeholder="Detailed description of the adverse event...", height=100)
                patient_outcome = st.selectbox(
                    "Patient Outcome*",
                    ["recovered", "recovering", "not_recovered", "fatal", "unknown"]
                )
                reported_by = st.text_input("Reported By*", placeholder="e.g., Dr. John Smith - Hospital Name")
            
            submitted = st.form_submit_button("🤖 Submit AE (AI Analysis)", use_container_width=True)
            
            if submitted:
                if not all([ae_id, medicine_id, report_date, patient_age, patient_gender, description, patient_outcome, reported_by]):
                    st.error("Please fill in all required fields marked with *")
                else:
                    try:
                        with st.spinner("Submitting AE and running pharmacovigilance analysis..."):
                            result = st.session_state.compliance_mcp.call_endpoint(
                                "submit_adverse_event",
                                {
                                    "ae_id": ae_id,
                                    "medicine_id": medicine_id,
                                    "report_date": report_date.isoformat(),
                                    "patient_age": patient_age,
                                    "patient_gender": patient_gender,
                                    "description": description,
                                    "patient_outcome": patient_outcome,
                                    "reported_by": reported_by
                                }
                            )
                            
                            if result.get("status") == "success":
                                data = result.get("data", {})
                                pv_analysis = data.get("pharmacovigilance_analysis", {})
                                
                                st.success(f"✅ Adverse event {ae_id} reported successfully!")
                                
                                # Show PV analysis
                                if pv_analysis:
                                    st.markdown("### 🤖 Pharmacovigilance Analysis")
                                    
                                    col1, col2, col3 = st.columns(3)
                                    
                                    with col1:
                                        severity = pv_analysis.get("severity", "unknown")
                                        if severity in ["serious", "fatal"]:
                                            st.error(f"**Severity:** 🔴 {severity.upper()}")
                                        elif severity == "moderate":
                                            st.warning(f"**Severity:** 🟡 {severity.upper()}")
                                        else:
                                            st.info(f"**Severity:** 🔵 {severity.upper()}")
                                    
                                    with col2:
                                        causality = pv_analysis.get("causality", "unknown")
                                        st.write(f"**Causality:** {causality.upper()}")
                                        st.write(f"**WHO-UMC Scale:** {pv_analysis.get('who_umc_scale', 'N/A')}")
                                    
                                    with col3:
                                        st.write(f"**Reporting Timeline:** {pv_analysis.get('reporting_timeline', 'N/A')}")
                                        st.write(f"**Regulatory Action:** {pv_analysis.get('regulatory_action_required', 'N/A')}")
                                    
                                    if pv_analysis.get("recommendations"):
                                        st.markdown("**Recommendations:**")
                                        for rec in pv_analysis.get("recommendations", []):
                                            st.info(rec)
                                
                                st.balloons()
                            else:
                                st.error(f"Error: {result.get('message')}")
                    except Exception as e:
                        st.error(f"Error submitting AE: {str(e)}")
        
        # Recent AEs
        st.markdown("---")
        st.markdown("### 📊 Recent Adverse Events")
        
        if aes:
            ae_df = pd.DataFrame([{
                "AE ID": ae.get("ae_id", "N/A"),
                "Medicine": ae.get("medicine_id", "N/A"),
                "Report Date": ae.get("report_date", "N/A")[:10],
                "Age": ae.get("patient_age", "N/A"),
                "Gender": ae.get("patient_gender", "N/A"),
                "Severity": ae.get("severity", "N/A"),
                "Causality": ae.get("causality", "N/A"),
                "Outcome": ae.get("patient_outcome", "N/A")
            } for ae in aes[:50]])  # Show last 50
            
            st.dataframe(ae_df, use_container_width=True, hide_index=True)
            
            # Severity distribution chart
            st.markdown("---")
            st.markdown("### Severity Distribution")
            
            severity_counts = {}
            for ae in aes:
                severity = ae.get("severity", "unknown")
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            fig = px.pie(
                names=list(severity_counts.keys()),
                values=list(severity_counts.values()),
                title="Adverse Events by Severity",
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.RdYlGn_r
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No adverse events reported")
    
    except Exception as e:
        st.error(f"Error loading adverse events: {str(e)}")

with tab3:
    st.markdown("### Audit Trail Reports (21 CFR Part 11 Compliance)")
    
    try:
        # Generate audit report
        col1, col2 = st.columns([3, 1])
        with col1:
            days_back = st.slider("Report Period (days)", 7, 90, 30)
        with col2:
            if st.button("📊 Generate Report", use_container_width=True):
                with st.spinner("Generating audit report..."):
                    result = st.session_state.compliance_mcp.call_endpoint(
                        "generate_audit_report",
                        {"days": days_back}
                    )
                    
                    if result.get("status") == "success":
                        report = result.get("data", {})
                        
                        st.success("✅ Audit report generated")
                        
                        # Report summary
                        st.markdown("---")
                        st.markdown("### 📊 Audit Report Summary")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Total Actions", report.get("total_actions", 0))
                        with col2:
                            st.metric("Unique Users", report.get("unique_users", 0))
                        with col3:
                            st.metric("Batch Approvals", report.get("batch_approvals", 0))
                        with col4:
                            st.metric("Data Modifications", report.get("data_modifications", 0))
                        
                        # Action breakdown
                        if report.get("action_breakdown"):
                            st.markdown("---")
                            st.markdown("### Action Breakdown")
                            
                            breakdown = report.get("action_breakdown", {})
                            breakdown_df = pd.DataFrame([
                                {"Action Type": k, "Count": v}
                                for k, v in breakdown.items()
                            ])
                            
                            fig = px.bar(
                                breakdown_df,
                                x="Action Type",
                                y="Count",
                                title="Actions by Type"
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # Critical actions
                        if report.get("critical_actions"):
                            st.markdown("---")
                            st.markdown("### ⚠️ Critical Actions")
                            
                            critical_df = pd.DataFrame([{
                                "Timestamp": a.get("timestamp", "N/A")[:19].replace("T", " "),
                                "Action": a.get("action", "N/A"),
                                "Entity": a.get("entity_type", "N/A"),
                                "Entity ID": a.get("entity_id", "N/A"),
                                "User": a.get("performed_by", "N/A")
                            } for a in report.get("critical_actions", [])])
                            
                            st.dataframe(critical_df, use_container_width=True, hide_index=True)
                        
                        # Compliance status
                        st.markdown("---")
                        st.markdown("### ✅ Compliance Status")
                        st.success(report.get("compliance_status", "N/A"))
        
        # Recent audit logs
        st.markdown("---")
        st.markdown("### Recent Audit Logs")
        
        logs = list(st.session_state.db_helper.audit_logs.find({}, limit=100))
        
        if logs:
            log_df = pd.DataFrame([{
                "Timestamp": log.get("timestamp", "N/A")[:19].replace("T", " "),
                "Action": log.get("action", "N/A"),
                "Entity Type": log.get("entity_type", "N/A"),
                "Entity ID": log.get("entity_id", "N/A"),
                "User": log.get("performed_by", "N/A"),
                "IP Address": log.get("ip_address", "N/A")
            } for log in logs])
            
            st.dataframe(log_df, use_container_width=True, hide_index=True)
        else:
            st.info("No audit logs available")
    
    except Exception as e:
        st.error(f"Error generating audit report: {str(e)}")

with tab4:
    st.markdown("### 🔍 Search Standard Operating Procedures (SOPs)")
    st.info("🤖 AI-powered vector search across SOP documents")
    
    search_query = st.text_input("Search Query", placeholder="e.g., dissolution testing procedure")
    top_k = st.slider("Number of Results", 1, 10, 5)
    
    if st.button("🔍 Search SOPs", use_container_width=True):
        if search_query:
            with st.spinner("Searching SOP documents..."):
                try:
                    result = st.session_state.compliance_mcp.call_endpoint(
                        "search_regulations",
                        {
                            "query": search_query,
                            "top_k": top_k
                        }
                    )
                    
                    if result.get("status") == "success":
                        sops = result.get("data", [])
                        
                        if sops:
                            st.success(f"✅ Found {len(sops)} relevant SOPs")
                            
                            for idx, sop in enumerate(sops, 1):
                                with st.expander(f"#{idx} - {sop.get('sop_number')} - {sop.get('title')} (Relevance: {sop.get('similarity_score', 0):.2%})"):
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        st.write(f"**SOP ID:** {sop.get('sop_id', 'N/A')}")
                                        st.write(f"**SOP Number:** {sop.get('sop_number', 'N/A')}")
                                        st.write(f"**Title:** {sop.get('title', 'N/A')}")
                                        st.write(f"**Category:** {sop.get('category', 'N/A')}")
                                    
                                    with col2:
                                        st.write(f"**Version:** {sop.get('version', 'N/A')}")
                                        st.write(f"**Effective Date:** {sop.get('effective_date', 'N/A')[:10]}")
                                        st.write(f"**Review Date:** {sop.get('review_date', 'N/A')[:10]}")
                                        st.write(f"**Approved By:** {sop.get('approved_by', 'N/A')}")
                                    
                                    st.markdown("**Summary:**")
                                    st.write(sop.get('summary', 'N/A'))
                        else:
                            st.info("No relevant SOPs found")
                    else:
                        st.error(f"Error: {result.get('message')}")
                except Exception as e:
                    st.error(f"Error searching SOPs: {str(e)}")
        else:
            st.warning("Please enter a search query")

with tab5:
    st.markdown("### GMP Compliance Validation")
    
    # Get batches for validation
    batches = list(st.session_state.db_helper.manufacturing_batches.find({}, limit=100))
    
    if batches:
        batch_options = {b.get("batch_id"): b.get("batch_number") for b in batches}
        
        selected_batch = st.selectbox(
            "Select Batch for GMP Validation",
            options=list(batch_options.keys()),
            format_func=lambda x: f"{x} - {batch_options.get(x, 'N/A')}"
        )
        
        if st.button("✅ Validate GMP Compliance", use_container_width=True):
            with st.spinner("Running GMP compliance validation..."):
                try:
                    result = st.session_state.compliance_mcp.call_endpoint(
                        "validate_gmp_compliance",
                        {"batch_id": selected_batch}
                    )
                    
                    if result.get("status") == "success":
                        validation = result.get("data", {})
                        
                        # Overall compliance
                        compliant = validation.get("gmp_compliant", False)
                        if compliant:
                            st.success("✅ **GMP COMPLIANT**")
                        else:
                            st.error("❌ **NOT GMP COMPLIANT**")
                        
                        # Compliance checks
                        st.markdown("---")
                        st.markdown("### Compliance Checks")
                        
                        checks = validation.get("compliance_checks", {})
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Documentation:** {'✅' if checks.get('documentation_complete') else '❌'}")
                            st.write(f"**Quality Tests:** {'✅' if checks.get('quality_tests_passed') else '❌'}")
                            st.write(f"**Equipment Calibrated:** {'✅' if checks.get('equipment_calibrated') else '❌'}")
                        
                        with col2:
                            st.write(f"**Material Traceability:** {'✅' if checks.get('material_traceability') else '❌'}")
                            st.write(f"**Audit Trail:** {'✅' if checks.get('audit_trail_complete') else '❌'}")
                            st.write(f"**Regulatory Approval:** {'✅' if checks.get('regulatory_approval') else '❌'}")
                        
                        # Issues
                        if validation.get("issues"):
                            st.markdown("---")
                            st.markdown("### ⚠️ Compliance Issues")
                            
                            for issue in validation.get("issues", []):
                                st.error(f"• {issue}")
                        
                        # Recommendations
                        if validation.get("recommendations"):
                            st.markdown("---")
                            st.markdown("### 📋 Recommendations")
                            
                            for rec in validation.get("recommendations", []):
                                st.info(f"• {rec}")
                    else:
                        st.error(f"Error: {result.get('message')}")
                except Exception as e:
                    st.error(f"Error validating GMP compliance: {str(e)}")
    else:
        st.info("No batches available for GMP validation")

# Footer
st.markdown("---")
st.markdown("📜 Regulatory Compliance | [Back to Dashboard](../app.py)")
