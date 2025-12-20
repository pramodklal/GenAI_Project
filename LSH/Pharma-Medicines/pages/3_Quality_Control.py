"""
Quality Control Page
Submit QC tests, validate batches, and generate Certificates of Analysis
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from database.astra_helper import AstraDBHelper
from mcp_servers.quality_control_mcp import QualityControlMCPServer

# Page configuration
st.set_page_config(
    page_title="Quality Control",
    page_icon="✅",
    layout="wide"
)

# Initialize
if 'db_helper' not in st.session_state:
    st.session_state.db_helper = AstraDBHelper()
if 'qc_mcp' not in st.session_state:
    st.session_state.qc_mcp = QualityControlMCPServer()

# Header
st.title("✅ Quality Control Management")
st.markdown("Submit tests, validate batches, and generate Certificates of Analysis")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 QC Tests", "➕ Submit Test", "🔍 Batch Validation", "📄 Generate COA", "⚠️ OOS Investigations"])

with tab1:
    st.markdown("### Quality Control Test Results")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Status", ["All", "pass", "fail", "pending"])
    with col2:
        test_type_filter = st.selectbox(
            "Test Type",
            ["All", "dissolution", "assay", "microbial", "content_uniformity", "stability"]
        )
    with col3:
        batch_filter = st.text_input("Batch ID", placeholder="e.g., BATCH-2025-001")
    
    try:
        # Build query
        query = {}
        if status_filter != "All":
            query["pass_fail_status"] = status_filter
        if test_type_filter != "All":
            query["test_type"] = test_type_filter
        if batch_filter:
            query["batch_id"] = batch_filter
        
        # Fetch tests
        tests = list(st.session_state.db_helper.quality_control_tests.find(query, limit=100))
        
        if tests:
            st.success(f"Found {len(tests)} QC tests")
            
            # Create DataFrame
            df = pd.DataFrame([{
                "Test ID": t.get("test_id", "N/A"),
                "Batch ID": t.get("batch_id", "N/A"),
                "Test Type": t.get("test_type", "N/A"),
                "Test Date": t.get("test_date", "N/A")[:10],
                "Result": f"{t.get('result_value', 'N/A')} {t.get('result_unit', '')}",
                "Specification": t.get("specification", "N/A"),
                "Status": "✅ Pass" if t.get("pass_fail_status") == "pass" else "❌ Fail" if t.get("pass_fail_status") == "fail" else "⏳ Pending",
                "Tested By": t.get("tested_by", "N/A")
            } for t in tests])
            
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Test details
            st.markdown("---")
            st.markdown("### Test Details")
            
            selected_test = st.selectbox(
                "Select Test for Details",
                options=[t.get("test_id") for t in tests],
                format_func=lambda x: next((f"{t.get('test_id')} - {t.get('test_type')}" for t in tests if t.get("test_id") == x), x)
            )
            
            if selected_test:
                result = st.session_state.qc_mcp.call_endpoint(
                    "get_qc_results",
                    {"test_id": selected_test}
                )
                
                if result.get("status") == "success":
                    test = result.get("data", {})
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown("**Test Information**")
                        st.write(f"**Test ID:** {test.get('test_id', 'N/A')}")
                        st.write(f"**Batch ID:** {test.get('batch_id', 'N/A')}")
                        st.write(f"**Test Type:** {test.get('test_type', 'N/A').upper()}")
                        st.write(f"**Test Date:** {test.get('test_date', 'N/A')[:10]}")
                    
                    with col2:
                        st.markdown("**Specifications & Results**")
                        st.write(f"**Specification:** {test.get('specification', 'N/A')}")
                        st.write(f"**Acceptance:** {test.get('acceptance_criteria', 'N/A')}")
                        st.write(f"**Result:** {test.get('result_value', 'N/A')} {test.get('result_unit', '')}")
                        
                        status = test.get('pass_fail_status', 'pending')
                        if status == 'pass':
                            st.success("✅ PASS")
                        elif status == 'fail':
                            st.error("❌ FAIL")
                        else:
                            st.info("⏳ PENDING")
                    
                    with col3:
                        st.markdown("**Test Details**")
                        st.write(f"**Method:** {test.get('method', 'N/A')}")
                        st.write(f"**Tested By:** {test.get('tested_by', 'N/A')}")
                        st.write(f"**Observations:** {test.get('observations', 'N/A')}")
                        st.write(f"**Remarks:** {test.get('remarks', 'N/A')}")
                else:
                    st.error(f"Error: {result.get('message')}")
        else:
            st.info("No QC tests found matching the criteria")
    
    except Exception as e:
        st.error(f"Error loading QC tests: {str(e)}")

with tab2:
    st.markdown("### Submit New QC Test")
    st.info("🤖 AI-powered test analysis will automatically detect OOS conditions")
    
    with st.form("submit_test_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            test_id = st.text_input("Test ID*", placeholder="QC-YYYY-XXX")
            
            # Get batches for dropdown
            batches = list(st.session_state.db_helper.manufacturing_batches.find({}, limit=100))
            batch_options = {b.get("batch_id"): b.get("batch_number") for b in batches}
            
            batch_id = st.selectbox(
                "Batch ID*",
                options=list(batch_options.keys()),
                format_func=lambda x: f"{x} - {batch_options.get(x, 'N/A')}"
            )
            
            test_type = st.selectbox(
                "Test Type*",
                ["dissolution", "assay", "microbial", "content_uniformity", "stability"]
            )
            
            test_date = st.date_input("Test Date*", value=datetime.now())
            tested_by = st.text_input("Tested By*", placeholder="e.g., Lab Analyst - John Doe")
        
        with col2:
            specification = st.text_input("Specification*", placeholder="e.g., ≥80% in 30 minutes")
            acceptance_criteria = st.text_input("Acceptance Criteria*", placeholder="e.g., Not less than 80% (Q)")
            method = st.text_input("Method*", placeholder="e.g., USP Apparatus II")
            result_value = st.number_input("Result Value*", min_value=0.0, max_value=1000.0, value=0.0, step=0.1)
            result_unit = st.text_input("Result Unit*", placeholder="e.g., %, mg, CFU/g")
            observations = st.text_area("Observations", placeholder="Detailed observations...")
        
        submitted = st.form_submit_button("🔬 Submit Test (AI Analysis)", use_container_width=True)
        
        if submitted:
            if not all([test_id, batch_id, test_type, test_date, tested_by, specification, acceptance_criteria, method, result_value, result_unit]):
                st.error("Please fill in all required fields marked with *")
            else:
                try:
                    with st.spinner("Submitting test and running AI analysis..."):
                        result = st.session_state.qc_mcp.call_endpoint(
                            "submit_qc_test",
                            {
                                "test_id": test_id,
                                "batch_id": batch_id,
                                "test_type": test_type,
                                "test_date": test_date.isoformat(),
                                "tested_by": tested_by,
                                "specification": specification,
                                "acceptance_criteria": acceptance_criteria,
                                "method": method,
                                "result_value": result_value,
                                "result_unit": result_unit,
                                "observations": observations
                            }
                        )
                        
                        if result.get("status") == "success":
                            data = result.get("data", {})
                            ai_analysis = data.get("ai_analysis", {})
                            
                            st.success(f"✅ Test {test_id} submitted successfully!")
                            
                            # Show AI analysis
                            if ai_analysis:
                                st.markdown("### 🤖 AI Analysis Results")
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    pass_fail = ai_analysis.get("pass_fail_status", "unknown")
                                    if pass_fail == "pass":
                                        st.success(f"**Status:** ✅ {pass_fail.upper()}")
                                    else:
                                        st.error(f"**Status:** ❌ {pass_fail.upper()}")
                                    
                                    st.write(f"**Assessment:** {ai_analysis.get('assessment', 'N/A')}")
                                
                                with col2:
                                    if ai_analysis.get("oos_detected"):
                                        st.error("⚠️ OUT-OF-SPECIFICATION DETECTED")
                                        st.write(f"**Severity:** {ai_analysis.get('oos_severity', 'N/A')}")
                                    
                                    st.write(f"**Recommendation:** {ai_analysis.get('recommendation', 'N/A')}")
                            
                            st.balloons()
                        else:
                            st.error(f"Error: {result.get('message')}")
                except Exception as e:
                    st.error(f"Error submitting test: {str(e)}")

with tab3:
    st.markdown("### Batch Quality Validation")
    st.info("🤖 AI-powered comprehensive batch validation with quality metrics")
    
    # Get batches pending validation
    batches = list(st.session_state.db_helper.manufacturing_batches.find(
        {"status": {"$in": ["in_qc", "in_production"]}},
        limit=100
    ))
    
    if batches:
        batch_options = {b.get("batch_id"): b.get("batch_number") for b in batches}
        
        selected_batch = st.selectbox(
            "Select Batch for Validation",
            options=list(batch_options.keys()),
            format_func=lambda x: f"{x} - {batch_options.get(x, 'N/A')}"
        )
        
        if st.button("🔍 Validate Batch Quality (AI)", use_container_width=True):
            with st.spinner("Running comprehensive quality validation..."):
                result = st.session_state.qc_mcp.call_endpoint(
                    "validate_batch_quality",
                    {"batch_id": selected_batch}
                )
                
                if result.get("status") == "success":
                    validation = result.get("data", {})
                    
                    # Overall status
                    overall = validation.get("overall_status", "unknown")
                    if overall == "pass":
                        st.success(f"✅ **Overall Status:** {overall.upper()}")
                    else:
                        st.error(f"❌ **Overall Status:** {overall.upper()}")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Tests", validation.get("total_tests", 0))
                        st.metric("Tests Passed", validation.get("tests_passed", 0))
                    
                    with col2:
                        st.metric("Tests Failed", validation.get("tests_failed", 0))
                        st.metric("Pending Tests", validation.get("tests_pending", 0))
                    
                    with col3:
                        pass_rate = validation.get("pass_rate", 0)
                        st.metric("Pass Rate", f"{pass_rate:.1f}%")
                        
                        if validation.get("release_recommended"):
                            st.success("✅ Release Recommended")
                        else:
                            st.error("❌ Release NOT Recommended")
                    
                    # Test results
                    if validation.get("test_results"):
                        st.markdown("---")
                        st.markdown("### Test Results Summary")
                        
                        test_df = pd.DataFrame([{
                            "Test Type": t.get("test_type", "N/A"),
                            "Result": f"{t.get('result_value', 'N/A')} {t.get('result_unit', '')}",
                            "Status": "✅" if t.get("pass_fail_status") == "pass" else "❌"
                        } for t in validation.get("test_results", [])])
                        
                        st.dataframe(test_df, use_container_width=True, hide_index=True)
                    
                    # Recommendations
                    if validation.get("recommendations"):
                        st.markdown("---")
                        st.markdown("### 🤖 AI Recommendations")
                        for rec in validation.get("recommendations", []):
                            st.info(rec)
                else:
                    st.error(f"Error: {result.get('message')}")
    else:
        st.info("No batches pending validation")

with tab4:
    st.markdown("### Generate Certificate of Analysis (COA)")
    
    # Get approved batches
    approved_batches = list(st.session_state.db_helper.manufacturing_batches.find(
        {"status": "approved"},
        limit=100
    ))
    
    if approved_batches:
        batch_options = {b.get("batch_id"): b.get("batch_number") for b in approved_batches}
        
        selected_batch = st.selectbox(
            "Select Approved Batch",
            options=list(batch_options.keys()),
            format_func=lambda x: f"{x} - {batch_options.get(x, 'N/A')}",
            key="coa_batch"
        )
        
        if st.button("📄 Generate COA", use_container_width=True):
            with st.spinner("Generating Certificate of Analysis..."):
                result = st.session_state.qc_mcp.call_endpoint(
                    "generate_coa",
                    {"batch_id": selected_batch}
                )
                
                if result.get("status") == "success":
                    coa = result.get("data", {})
                    
                    st.success("✅ COA Generated Successfully")
                    
                    # COA Header
                    st.markdown("---")
                    st.markdown("## 📄 CERTIFICATE OF ANALYSIS")
                    st.markdown("---")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Batch Information**")
                        st.write(f"**Batch Number:** {coa.get('batch_number', 'N/A')}")
                        st.write(f"**Medicine:** {coa.get('medicine_id', 'N/A')}")
                        st.write(f"**Quantity:** {coa.get('quantity', 0):,} units")
                        st.write(f"**Manufacturing Date:** {coa.get('manufacturing_date', 'N/A')[:10]}")
                        st.write(f"**Expiry Date:** {coa.get('expiry_date', 'N/A')[:10]}")
                    
                    with col2:
                        st.markdown("**Approval Information**")
                        st.write(f"**Approved By:** {coa.get('approved_by', 'N/A')}")
                        st.write(f"**Approval Date:** {coa.get('approval_date', 'N/A')[:10]}")
                        st.write(f"**GMP Certified:** {'✅ Yes' if coa.get('gmp_certified') else '❌ No'}")
                        st.write(f"**COA Issue Date:** {coa.get('coa_issue_date', 'N/A')[:10]}")
                    
                    # Test Results
                    st.markdown("---")
                    st.markdown("**Test Results**")
                    
                    if coa.get("test_results"):
                        test_df = pd.DataFrame([{
                            "Test Type": t.get("test_type", "N/A").upper(),
                            "Specification": t.get("specification", "N/A"),
                            "Result": f"{t.get('result_value', 'N/A')} {t.get('result_unit', '')}",
                            "Method": t.get("method", "N/A"),
                            "Status": "✅ PASS" if t.get("pass_fail_status") == "pass" else "❌ FAIL"
                        } for t in coa.get("test_results", [])])
                        
                        st.dataframe(test_df, use_container_width=True, hide_index=True)
                    
                    # Conclusion
                    st.markdown("---")
                    st.markdown("**Conclusion**")
                    st.success(coa.get("conclusion", "N/A"))
                    
                    # Download option
                    st.markdown("---")
                    st.download_button(
                        label="📥 Download COA (JSON)",
                        data=str(coa),
                        file_name=f"COA_{coa.get('batch_number', 'batch')}.json",
                        mime="application/json"
                    )
                else:
                    st.error(f"Error: {result.get('message')}")
    else:
        st.info("No approved batches available for COA generation")

with tab5:
    st.markdown("### Out-of-Specification (OOS) Investigations")
    
    try:
        result = st.session_state.qc_mcp.call_endpoint("get_oos_investigations", {})
        
        if result.get("status") == "success":
            oos_cases = result.get("data", [])
            
            if oos_cases:
                st.warning(f"⚠️ {len(oos_cases)} OOS cases requiring investigation")
                
                # Create DataFrame
                df = pd.DataFrame([{
                    "Test ID": case.get("test_id", "N/A"),
                    "Batch ID": case.get("batch_id", "N/A"),
                    "Test Type": case.get("test_type", "N/A"),
                    "Result": f"{case.get('result_value', 'N/A')} {case.get('result_unit', '')}",
                    "Specification": case.get("specification", "N/A"),
                    "Deviation": case.get("deviation", "N/A"),
                    "Severity": case.get("severity", "N/A"),
                    "Test Date": case.get("test_date", "N/A")[:10]
                } for case in oos_cases])
                
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # OOS Details
                st.markdown("---")
                st.markdown("### OOS Investigation Details")
                
                selected_oos = st.selectbox(
                    "Select OOS Case",
                    options=range(len(oos_cases)),
                    format_func=lambda x: f"{oos_cases[x].get('test_id')} - {oos_cases[x].get('test_type')}"
                )
                
                if selected_oos is not None:
                    case = oos_cases[selected_oos]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**OOS Information**")
                        st.write(f"**Test ID:** {case.get('test_id', 'N/A')}")
                        st.write(f"**Batch ID:** {case.get('batch_id', 'N/A')}")
                        st.write(f"**Test Type:** {case.get('test_type', 'N/A')}")
                        st.write(f"**Result:** {case.get('result_value', 'N/A')} {case.get('result_unit', '')}")
                        st.write(f"**Specification:** {case.get('specification', 'N/A')}")
                    
                    with col2:
                        st.markdown("**Investigation Status**")
                        severity = case.get("severity", "unknown")
                        if severity == "critical":
                            st.error(f"**Severity:** 🔴 {severity.upper()}")
                        elif severity == "major":
                            st.warning(f"**Severity:** 🟡 {severity.upper()}")
                        else:
                            st.info(f"**Severity:** 🔵 {severity.upper()}")
                        
                        st.write(f"**Deviation:** {case.get('deviation', 'N/A')}")
                        st.write(f"**Recommendation:** {case.get('recommendation', 'N/A')}")
            else:
                st.success("✅ No OOS cases - All tests within specification")
        else:
            st.error(f"Error: {result.get('message')}")
    
    except Exception as e:
        st.error(f"Error loading OOS cases: {str(e)}")

# Footer
st.markdown("---")
st.markdown("✅ Quality Control | [Back to Dashboard](../app.py)")
