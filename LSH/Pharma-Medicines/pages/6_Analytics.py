"""
Analytics Dashboard
Production KPIs, quality metrics, compliance analytics
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from database.astra_helper import AstraDBHelper

# Page configuration
st.set_page_config(
    page_title="Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# Initialize
if 'db_helper' not in st.session_state:
    st.session_state.db_helper = AstraDBHelper()

# Header
st.title("📊 Analytics Dashboard")
st.markdown("Production KPIs, Quality Metrics, and Compliance Analytics")

# Date range selector
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=90))
with col2:
    end_date = st.date_input("End Date", value=datetime.now())
with col3:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🏭 Production Analytics", "✅ Quality Metrics", "📋 Compliance Dashboard", "📈 Trends & Insights"])

with tab1:
    st.markdown("### Production Performance Metrics")
    
    try:
        db = st.session_state.db_helper
        
        # Fetch batches in date range
        batches = list(db.manufacturing_batches.find({
            "manufacturing_date": {
                "$gte": start_date.isoformat(),
                "$lte": end_date.isoformat()
            }
        }, limit=1000))
        
        if batches:
            # Key metrics
            col1, col2, col3, col4, col5 = st.columns(5)
            
            total_batches = len(batches)
            approved_batches = sum(1 for b in batches if b.get("status") == "approved")
            rejected_batches = sum(1 for b in batches if b.get("status") == "rejected")
            in_production = sum(1 for b in batches if b.get("status") == "in_production")
            
            # Average yield
            yields = [b.get("yield_percentage", 0) for b in batches if b.get("yield_percentage")]
            avg_yield = sum(yields) / len(yields) if yields else 0
            
            with col1:
                st.metric("Total Batches", total_batches)
            with col2:
                st.metric("Approved", approved_batches)
            with col3:
                st.metric("Rejected", rejected_batches, delta_color="inverse")
            with col4:
                st.metric("In Production", in_production)
            with col5:
                st.metric("Avg Yield", f"{avg_yield:.1f}%", delta=f"{avg_yield - 95:.1f}%")
            
            st.markdown("---")
            
            # Production over time
            st.markdown("### 📈 Production Volume Over Time")
            
            # Group by manufacturing date
            batch_dates = {}
            for batch in batches:
                date = batch.get("manufacturing_date", "")[:10]
                if date:
                    batch_dates[date] = batch_dates.get(date, 0) + 1
            
            if batch_dates:
                dates_df = pd.DataFrame([
                    {"Date": k, "Batches": v}
                    for k, v in sorted(batch_dates.items())
                ])
                
                fig = px.line(
                    dates_df,
                    x="Date",
                    y="Batches",
                    title="Daily Batch Production",
                    markers=True
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Batch status distribution
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Batch Status Distribution")
                
                status_counts = {}
                for batch in batches:
                    status = batch.get("status", "unknown")
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                fig = px.pie(
                    names=list(status_counts.keys()),
                    values=list(status_counts.values()),
                    title="Batches by Status",
                    hole=0.4,
                    color_discrete_sequence=px.colors.sequential.RdYlGn
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("### Yield Distribution")
                
                fig = px.histogram(
                    x=yields,
                    nbins=20,
                    title="Batch Yield Distribution",
                    labels={"x": "Yield (%)", "y": "Count"}
                )
                
                fig.add_vline(x=95, line_dash="dash", line_color="red", annotation_text="Target: 95%")
                fig.add_vline(x=avg_yield, line_dash="dash", line_color="green", annotation_text=f"Avg: {avg_yield:.1f}%")
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Production by medicine
            st.markdown("---")
            st.markdown("### 📊 Production by Medicine")
            
            medicine_counts = {}
            for batch in batches:
                med_id = batch.get("medicine_id", "Unknown")
                medicine_counts[med_id] = medicine_counts.get(med_id, 0) + 1
            
            med_df = pd.DataFrame([
                {"Medicine": k, "Batches": v}
                for k, v in sorted(medicine_counts.items(), key=lambda x: x[1], reverse=True)
            ])
            
            fig = px.bar(
                med_df,
                x="Medicine",
                y="Batches",
                title="Batches Produced by Medicine"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Equipment utilization
            st.markdown("---")
            st.markdown("### 🔧 Equipment Utilization")
            
            schedules = list(db.production_schedules.find({}, limit=1000))
            
            if schedules:
                equipment_usage = {}
                for schedule in schedules:
                    equip_id = schedule.get("equipment_id", "Unknown")
                    equipment_usage[equip_id] = equipment_usage.get(equip_id, 0) + 1
                
                equip_df = pd.DataFrame([
                    {"Equipment": k, "Uses": v}
                    for k, v in sorted(equipment_usage.items(), key=lambda x: x[1], reverse=True)
                ])
                
                fig = px.bar(
                    equip_df,
                    x="Equipment",
                    y="Uses",
                    title="Equipment Utilization",
                    color="Uses",
                    color_continuous_scale="Blues"
                )
                
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No production data available for the selected date range")
    
    except Exception as e:
        st.error(f"Error loading production analytics: {str(e)}")

with tab2:
    st.markdown("### Quality Control Metrics")
    
    try:
        db = st.session_state.db_helper
        
        # Fetch QC tests in date range
        tests = list(db.quality_control_tests.find({
            "test_date": {
                "$gte": start_date.isoformat(),
                "$lte": end_date.isoformat()
            }
        }, limit=1000))
        
        if tests:
            # Key metrics
            col1, col2, col3, col4, col5 = st.columns(5)
            
            total_tests = len(tests)
            passed_tests = sum(1 for t in tests if t.get("pass_fail_status") == "pass")
            failed_tests = sum(1 for t in tests if t.get("pass_fail_status") == "fail")
            pending_tests = sum(1 for t in tests if t.get("pass_fail_status") == "pending")
            pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
            
            with col1:
                st.metric("Total Tests", total_tests)
            with col2:
                st.metric("Passed", passed_tests)
            with col3:
                st.metric("Failed", failed_tests, delta_color="inverse")
            with col4:
                st.metric("Pending", pending_tests)
            with col5:
                st.metric("Pass Rate", f"{pass_rate:.1f}%", delta=f"{pass_rate - 95:.1f}%")
            
            st.markdown("---")
            
            # Pass rate gauge
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### QC Pass Rate Gauge")
                
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=pass_rate,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Overall Pass Rate (%)"},
                    delta={'reference': 95},
                    gauge={
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "#10b981"},
                        'steps': [
                            {'range': [0, 80], 'color': "#fee2e2"},
                            {'range': [80, 95], 'color': "#fef3c7"},
                            {'range': [95, 100], 'color': "#d1fae5"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 95
                        }
                    }
                ))
                
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("### Test Type Distribution")
                
                test_type_counts = {}
                for test in tests:
                    test_type = test.get("test_type", "unknown")
                    test_type_counts[test_type] = test_type_counts.get(test_type, 0) + 1
                
                fig = px.pie(
                    names=list(test_type_counts.keys()),
                    values=list(test_type_counts.values()),
                    title="Tests by Type",
                    hole=0.4
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Pass rate by test type
            st.markdown("---")
            st.markdown("### 📊 Pass Rate by Test Type")
            
            test_type_stats = {}
            for test in tests:
                test_type = test.get("test_type", "unknown")
                if test_type not in test_type_stats:
                    test_type_stats[test_type] = {"total": 0, "passed": 0}
                
                test_type_stats[test_type]["total"] += 1
                if test.get("pass_fail_status") == "pass":
                    test_type_stats[test_type]["passed"] += 1
            
            type_df = pd.DataFrame([{
                "Test Type": k,
                "Total": v["total"],
                "Passed": v["passed"],
                "Pass Rate": (v["passed"] / v["total"] * 100) if v["total"] > 0 else 0
            } for k, v in test_type_stats.items()])
            
            fig = px.bar(
                type_df,
                x="Test Type",
                y="Pass Rate",
                title="Pass Rate by Test Type (%)",
                color="Pass Rate",
                color_continuous_scale="RdYlGn",
                range_color=[0, 100]
            )
            
            fig.add_hline(y=95, line_dash="dash", line_color="red", annotation_text="Target: 95%")
            
            st.plotly_chart(fig, use_container_width=True)
            
            # OOS trends
            st.markdown("---")
            st.markdown("### ⚠️ Out-of-Specification Trends")
            
            oos_tests = [t for t in tests if t.get("pass_fail_status") == "fail"]
            
            if oos_tests:
                st.warning(f"⚠️ {len(oos_tests)} OOS cases detected")
                
                oos_by_date = {}
                for test in oos_tests:
                    date = test.get("test_date", "")[:10]
                    if date:
                        oos_by_date[date] = oos_by_date.get(date, 0) + 1
                
                oos_df = pd.DataFrame([
                    {"Date": k, "OOS Count": v}
                    for k, v in sorted(oos_by_date.items())
                ])
                
                fig = px.line(
                    oos_df,
                    x="Date",
                    y="OOS Count",
                    title="OOS Cases Over Time",
                    markers=True
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.success("✅ No OOS cases in the selected period")
        else:
            st.info("No QC test data available for the selected date range")
    
    except Exception as e:
        st.error(f"Error loading quality metrics: {str(e)}")

with tab3:
    st.markdown("### Compliance Dashboard")
    
    try:
        db = st.session_state.db_helper
        
        # Regulatory documents status
        st.markdown("### 📜 Regulatory Documents Status")
        
        docs = list(db.regulatory_documents.find({}, limit=500))
        
        col1, col2, col3, col4 = st.columns(4)
        
        active_docs = sum(1 for d in docs if d.get("status") == "active")
        expired_docs = sum(1 for d in docs if d.get("status") == "expired")
        
        # Expiring soon
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
        
        # Document types
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Documents by Type")
            
            doc_type_counts = {}
            for doc in docs:
                doc_type = doc.get("document_type", "unknown")
                doc_type_counts[doc_type] = doc_type_counts.get(doc_type, 0) + 1
            
            fig = px.bar(
                x=list(doc_type_counts.keys()),
                y=list(doc_type_counts.values()),
                labels={"x": "Document Type", "y": "Count"},
                title="Document Distribution"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Documents by Regulatory Body")
            
            reg_body_counts = {}
            for doc in docs:
                bodies = doc.get("regulatory_body", "Unknown").split("|")
                for body in bodies:
                    body = body.strip()
                    reg_body_counts[body] = reg_body_counts.get(body, 0) + 1
            
            fig = px.pie(
                names=list(reg_body_counts.keys()),
                values=list(reg_body_counts.values()),
                title="Regulatory Body Distribution",
                hole=0.4
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Adverse events
        st.markdown("---")
        st.markdown("### ⚠️ Pharmacovigilance Metrics")
        
        aes = list(db.adverse_events.find({}, limit=500))
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_aes = len(aes)
        serious_aes = sum(1 for ae in aes if ae.get("severity") in ["serious", "fatal"])
        moderate_aes = sum(1 for ae in aes if ae.get("severity") == "moderate")
        mild_aes = sum(1 for ae in aes if ae.get("severity") == "mild")
        
        with col1:
            st.metric("Total AEs", total_aes)
        with col2:
            st.metric("Serious/Fatal", serious_aes, delta_color="inverse")
        with col3:
            st.metric("Moderate", moderate_aes)
        with col4:
            st.metric("Mild", mild_aes)
        
        # AE trends
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### AEs by Severity")
            
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
        
        with col2:
            st.markdown("### AEs by Medicine")
            
            med_ae_counts = {}
            for ae in aes:
                med_id = ae.get("medicine_id", "Unknown")
                med_ae_counts[med_id] = med_ae_counts.get(med_id, 0) + 1
            
            # Top 5
            top_meds = sorted(med_ae_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            fig = px.bar(
                x=[m[0] for m in top_meds],
                y=[m[1] for m in top_meds],
                labels={"x": "Medicine", "y": "AE Count"},
                title="Top 5 Medicines by AE Count"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Audit trail metrics
        st.markdown("---")
        st.markdown("### 📊 Audit Trail Metrics (21 CFR Part 11)")
        
        logs = list(db.audit_logs.find({}, limit=1000))
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_actions = len(logs)
        unique_users = len(set(log.get("performed_by", "Unknown") for log in logs))
        batch_approvals = sum(1 for log in logs if log.get("action") == "approve")
        data_modifications = sum(1 for log in logs if log.get("action") == "update")
        
        with col1:
            st.metric("Total Actions", total_actions)
        with col2:
            st.metric("Unique Users", unique_users)
        with col3:
            st.metric("Batch Approvals", batch_approvals)
        with col4:
            st.metric("Data Modifications", data_modifications)
        
        # Action breakdown
        st.markdown("### Actions Breakdown")
        
        action_counts = {}
        for log in logs:
            action = log.get("action", "unknown")
            action_counts[action] = action_counts.get(action, 0) + 1
        
        fig = px.pie(
            names=list(action_counts.keys()),
            values=list(action_counts.values()),
            title="Audit Actions Distribution",
            hole=0.4
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error loading compliance dashboard: {str(e)}")

with tab4:
    st.markdown("### 📈 Trends & Insights")
    
    try:
        db = st.session_state.db_helper
        
        # Multi-metric dashboard
        st.markdown("### 📊 Key Performance Indicators Over Time")
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("Batch Production Trend", "QC Pass Rate Trend", 
                          "Inventory Levels", "Compliance Score"),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Batch production trend (simplified)
        batches = list(db.manufacturing_batches.find({}, limit=500))
        batch_dates = {}
        for batch in batches:
            date = batch.get("manufacturing_date", "")[:7]  # YYYY-MM
            if date:
                batch_dates[date] = batch_dates.get(date, 0) + 1
        
        fig.add_trace(
            go.Scatter(
                x=list(sorted(batch_dates.keys())),
                y=[batch_dates[k] for k in sorted(batch_dates.keys())],
                mode='lines+markers',
                name='Batches'
            ),
            row=1, col=1
        )
        
        # QC pass rate trend (simplified)
        tests = list(db.quality_control_tests.find({}, limit=500))
        test_dates = {}
        for test in tests:
            date = test.get("test_date", "")[:7]  # YYYY-MM
            if date:
                if date not in test_dates:
                    test_dates[date] = {"total": 0, "passed": 0}
                test_dates[date]["total"] += 1
                if test.get("pass_fail_status") == "pass":
                    test_dates[date]["passed"] += 1
        
        pass_rates = {k: (v["passed"] / v["total"] * 100) if v["total"] > 0 else 0 
                     for k, v in test_dates.items()}
        
        fig.add_trace(
            go.Scatter(
                x=list(sorted(pass_rates.keys())),
                y=[pass_rates[k] for k in sorted(pass_rates.keys())],
                mode='lines+markers',
                name='Pass Rate %'
            ),
            row=1, col=2
        )
        
        # Inventory levels
        materials = list(db.raw_materials.find({}, limit=500))
        api_stock = sum(m.get("quantity_in_stock", 0) for m in materials if m.get("type") == "API")
        excipient_stock = sum(m.get("quantity_in_stock", 0) for m in materials if m.get("type") == "excipient")
        
        fig.add_trace(
            go.Bar(
                x=["APIs", "Excipients"],
                y=[api_stock, excipient_stock],
                name='Stock Level'
            ),
            row=2, col=1
        )
        
        # Compliance score (simplified)
        docs = list(db.regulatory_documents.find({}, limit=500))
        active_docs = sum(1 for d in docs if d.get("status") == "active")
        compliance_score = (active_docs / len(docs) * 100) if docs else 0
        
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=compliance_score,
                title={'text': "Compliance Score"},
                gauge={'axis': {'range': [None, 100]},
                       'bar': {'color': "darkblue"},
                       'threshold': {'line': {'color': "red", 'width': 4},
                                   'thickness': 0.75, 'value': 90}}
            ),
            row=2, col=2
        )
        
        fig.update_layout(height=600, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Insights
        st.markdown("---")
        st.markdown("### 💡 AI-Generated Insights")
        
        insights = []
        
        # Production insights
        if batches:
            recent_batches = [b for b in batches if b.get("status") == "approved"]
            if recent_batches:
                avg_yield = sum(b.get("yield_percentage", 0) for b in recent_batches) / len(recent_batches)
                if avg_yield >= 95:
                    insights.append(("success", f"✅ Production yield is excellent at {avg_yield:.1f}% (target: 95%)"))
                else:
                    insights.append(("warning", f"⚠️ Production yield at {avg_yield:.1f}% is below target (95%). Consider process optimization."))
        
        # Quality insights
        if tests:
            pass_rate = (sum(1 for t in tests if t.get("pass_fail_status") == "pass") / len(tests) * 100)
            if pass_rate >= 95:
                insights.append(("success", f"✅ QC pass rate is excellent at {pass_rate:.1f}%"))
            else:
                insights.append(("warning", f"⚠️ QC pass rate at {pass_rate:.1f}% needs improvement"))
        
        # Inventory insights
        low_stock_count = sum(1 for m in materials if m.get("quantity_in_stock", 0) <= m.get("reorder_point", 0))
        if low_stock_count > 0:
            insights.append(("error", f"🔴 {low_stock_count} materials below reorder point. Place orders immediately."))
        else:
            insights.append(("success", "✅ All materials adequately stocked"))
        
        # Compliance insights
        if docs:
            expiry_date = datetime.utcnow() + timedelta(days=60)
            expiring_docs = sum(1 for d in docs 
                              if d.get("status") == "active" and 
                              d.get("expiry_date") and 
                              datetime.fromisoformat(d.get("expiry_date").replace('Z', '+00:00')) <= expiry_date)
            
            if expiring_docs > 0:
                insights.append(("warning", f"⚠️ {expiring_docs} regulatory documents expiring in 60 days. Schedule renewals."))
            else:
                insights.append(("success", "✅ All regulatory documents are current"))
        
        # Display insights
        for insight_type, message in insights:
            if insight_type == "success":
                st.success(message)
            elif insight_type == "warning":
                st.warning(message)
            else:
                st.error(message)
    
    except Exception as e:
        st.error(f"Error generating trends: {str(e)}")

# Footer
st.markdown("---")
st.markdown("📊 Analytics Dashboard | [Back to Dashboard](../app.py)")
