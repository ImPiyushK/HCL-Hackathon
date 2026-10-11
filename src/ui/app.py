"""
Streamlit Executive Dashboard & Interactive Analyst UI.
Factory Energy Cost Decomposition and Savings Agent.
Communicates with FastAPI API Backend (UI -> FastAPI -> LangGraph -> Tools -> DuckDB).
"""

import os
import sys
import json
import requests
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Factory Energy Decomposition Agent",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background: #1e293b;
        border-radius: 10px;
        padding: 16px;
        border-left: 5px solid #3b82f6;
        color: white;
        margin-bottom: 12px;
    }
    .badge-easy { background-color: #10b981; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold; }
    .badge-medium { background-color: #f59e0b; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold; }
    .badge-hard { background-color: #ef4444; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold; }
    .badge-faithful { background-color: #059669; color: white; padding: 4px 10px; border-radius: 6px; font-size: 0.9em; }
</style>
""", unsafe_allow_html=True)

# Helper function to query API safely
@st.cache_data(ttl=5)
def api_get(endpoint: str, params: dict = None):
    try:
        r = requests.get(f"{API_BASE_URL}{endpoint}", params=params, timeout=10)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception as e:
        return None

def api_post(endpoint: str, json_data: dict = None, files: dict = None, data: dict = None):
    try:
        if files:
            r = requests.post(f"{API_BASE_URL}{endpoint}", files=files, data=data, timeout=30)
        else:
            r = requests.post(f"{API_BASE_URL}{endpoint}", json=json_data, timeout=30)
        if r.status_code == 200:
            return r.json()
        return {"error": r.text, "status_code": r.status_code}
    except Exception as e:
        return {"error": str(e)}

# Check API health
health_data = api_get("/health")
is_api_healthy = bool(health_data and health_data.get("status") == "healthy")

# Sidebar
st.sidebar.title("⚡ Energy Agent")
st.sidebar.caption("HCLTech AI Engineer Hackathon | Team NIP")

nav = st.sidebar.radio(
    "Navigation",
    [
        "📊 Executive Bill Bridge",
        "🔍 Sub-Meter Diagnostics",
        "🛠️ Prescriptive Savings Actions",
        "💬 Interactive Agent Q&A",
        "🎛️ What-If Simulator",
        "📥 Live Ingest & Validation"
    ]
)

st.sidebar.divider()
st.sidebar.markdown("**System Architecture**")
if is_api_healthy:
    st.sidebar.success(f"FastAPI: Connected ({API_BASE_URL})")
    st.sidebar.success("Database: DuckDB Active")
    st.sidebar.info("Orchestration: LangGraph")
else:
    st.sidebar.error(f"FastAPI: Offline at {API_BASE_URL}")
    st.sidebar.warning("Please ensure the FastAPI backend is running.")

# ==============================================================================
# 1. EXECUTIVE BILL BRIDGE
# ==============================================================================
if nav == "📊 Executive Bill Bridge":
    st.title("⚡ Factory Electricity Bill Decomposition (2026-Q3 vs 2026-Q2)")
    st.markdown(
        "Executive cost bridge isolating why the electricity bill rose **15.4%** ($142k to $164k). "
        "Strictly enforces **Order of Attribution** (Tariff → Mix → Volume → Weather → Waste) and **Additivity**."
    )

    decomp = api_get("/decomposition", {"period": "2026-Q3", "compare_to": "2026-Q2"})

    if decomp:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Bill Change", f"+{decomp['total_increase_pct']}%", delta=f"+${decomp['bill_current'] - decomp['bill_baseline']:,.0f}")
        with col2:
            st.metric("Tariff Hike Effect", f"+{decomp['bridge'][0]['pct_points']} pts", "Utility Rate Change")
        with col3:
            st.metric("Product Mix Effect", f"+{decomp['bridge'][1]['pct_points']} pts", "Shift to Heavy Product C")
        with col4:
            st.metric("Controllable Waste", f"+{decomp['bridge'][4]['pct_points']} pts", "Pneumatic Air Leak")

        st.markdown("### 🌊 Waterfall Cost Bridge")
        
        causes = ["Baseline (Q2)", "Tariff Hike", "Product Mix Shift", "Volume Growth", "Summer Weather (CDD)", "Controllable Waste", "Current Bill (Q3)"]
        measures = ["absolute", "relative", "relative", "relative", "relative", "relative", "total"]
        
        b0 = decomp["bill_baseline"]
        deltas = [
            b0,
            b0 * decomp["bridge"][0]["pct_points"] / 100.0,
            b0 * decomp["bridge"][1]["pct_points"] / 100.0,
            b0 * decomp["bridge"][2]["pct_points"] / 100.0,
            b0 * decomp["bridge"][3]["pct_points"] / 100.0,
            b0 * decomp["bridge"][4]["pct_points"] / 100.0,
            decomp["bill_current"]
        ]

        text_labels = [
            f"${b0:,.0f}",
            f"+{decomp['bridge'][0]['pct_points']} pts (${deltas[1]:,.0f})",
            f"+{decomp['bridge'][1]['pct_points']} pts (${deltas[2]:,.0f})",
            f"+{decomp['bridge'][2]['pct_points']} pts (${deltas[3]:,.0f})",
            f"+{decomp['bridge'][3]['pct_points']} pts (${deltas[4]:,.0f})",
            f"+{decomp['bridge'][4]['pct_points']} pts (${deltas[5]:,.0f})",
            f"${decomp['bill_current']:,.0f}"
        ]

        fig = go.Figure(go.Waterfall(
            name="Cost Bridge",
            orientation="v",
            measure=measures,
            x=causes,
            textposition="outside",
            text=text_labels,
            y=deltas,
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            decreasing={"marker": {"color": "#10b981"}},
            increasing={"marker": {"color": "#ef4444"}},
            totals={"marker": {"color": "#3b82f6"}}
        ))

        fig.update_layout(
            title="Electricity Cost Decomposition ($ and Percentage Points)",
            waterfallgap=0.3,
            height=500,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 📋 Attribution Table (with Uncertainty Ranges)")
        df_bridge = pd.DataFrame([
            {
                "Driver / Cause": b["cause"].replace("_", " ").title(),
                "Contribution (pct points)": b["pct_points"],
                "Uncertainty Range (pts)": f"[{b['range'][0]} - {b['range'][1]}]",
                "Cost Impact ($)": f"${b0 * b['pct_points'] / 100.0:,.2f}",
                "Attribution Category": "Uncontrollable / Tariff" if b["cause"] == "tariff" else (
                    "Production Strategy" if b["cause"] in ("product_mix", "volume") else (
                        "Environmental" if b["cause"] == "weather" else "Controllable Waste"
                    )
                )
            }
            for b in decomp["bridge"]
        ])
        st.dataframe(df_bridge, use_container_width=True, hide_index=True)
    else:
        st.error("Unable to connect to backend API to retrieve decomposition.")

# ==============================================================================
# 2. SUB-METER DIAGNOSTICS & LEAK DETECTION
# ==============================================================================
elif nav == "🔍 Sub-Meter Diagnostics":
    st.title("🔍 Asset Energy Breakdown & Fault Diagnostics")

    assets_res = api_get("/diagnostics/assets", {"period": "2026-Q3"})
    leak_res = api_get("/diagnostics/leak", {"period": "2026-Q3"})
    idle_res = api_get("/diagnostics/idle", {"period": "2026-Q3"})

    if assets_res and leak_res and idle_res:
        col_a, col_b = st.columns([1, 1])

        with col_a:
            st.subheader("Sub-Meter Consumption Shares (Q3)")
            df_assets = pd.DataFrame(assets_res["assets"])
            fig_pie = px.pie(
                df_assets,
                names="asset",
                values="total_kwh",
                title=f"Total Facility Energy: {assets_res['total_facility_kwh']:,} kWh",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Prism
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_b:
            st.subheader("🚨 Hidden Fault Detected: Line 3 Compressor Air Leak")
            if leak_res.get("leak_detected"):
                st.error(
                    f"**Persistent Air Leak Flagged on Central Compressors!**\n\n"
                    f"• Night-to-Day Power Ratio: **{int(leak_res['compressors_night_share']*100)}%** "
                    f"(Normal healthy plant baseline is <15%).\n"
                    f"• Off-Hours Power Draw: **{leak_res['avg_night_power_kw']} kW** continuous load.\n"
                    f"• Excess Leak Power: **{leak_res['excess_leak_power_kw']} kW** wasted 24/7.\n"
                    f"• Annual Energy Loss: **{leak_res['annual_wasted_kwh_range'][0]:,} to {leak_res['annual_wasted_kwh_range'][1]:,} kWh/year**.\n"
                    f"• Annual Cost Loss: **${leak_res['annual_wasted_cost_range'][0]:,} to ${leak_res['annual_wasted_cost_range'][1]:,}/year**.\n"
                    f"• Carbon Impact: **{leak_res['annual_wasted_co2e_t_range'][0]} to {leak_res['annual_wasted_co2e_t_range'][1]} tonnes CO2e/year**."
                )
            else:
                st.success("No abnormal pneumatic leak detected.")

        st.subheader("🌙 Idle Energy Consumption by Asset (Zero-Production Windows)")
        st.write(f"Analyzed across **{idle_res['idle_hours']:.0f} non-operational hours**. Total idle energy: **{idle_res['total_idle_kwh']:,.0f} kWh**.")
        
        df_idle = pd.DataFrame(idle_res["idle_by_asset"])
        fig_bar = px.bar(
            df_idle,
            x="asset",
            y="idle_kwh",
            color="avg_idle_power_kw",
            labels={"idle_kwh": "Total Idle kWh", "avg_idle_power_kw": "Avg Idle Power (kW)"},
            title="Asset Energy Consumed During Idle / Non-Production Hours",
            color_continuous_scale="Reds"
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.error("Unable to connect to backend API for diagnostics.")

# ==============================================================================
# 3. PRESCRIPTIVE RECOMMENDATIONS
# ==============================================================================
elif nav == "🛠️ Prescriptive Savings Actions":
    st.title("🛠️ Prescriptive Action Matrix & Payback Ranking")
    st.markdown("Energy saving interventions ranked deterministically by **fastest payback period** and **ease of implementation**.")

    recs = api_get("/recommendations", {"period": "2026-Q3"})

    if recs:
        for i, r in enumerate(recs, start=1):
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"### #{i}. {r['action']}")
                    st.write(f"**Rationale**: {r['rationale']}")
                    st.caption(f"Evidence: `{', '.join(r['evidence_refs'])}` | Confidence: **{r['confidence'].upper()}**")
                with col2:
                    st.markdown(f"**Annual Dollar Savings**")
                    st.write(f"${r['saving_money_per_year'][0]:,} - ${r['saving_money_per_year'][1]:,}")
                    st.markdown(f"**Annual Energy Savings**")
                    st.write(f"{r['saving_kwh_per_year'][0]:,} - {r['saving_kwh_per_year'][1]:,} kWh")
                with col3:
                    st.markdown(f"**Payback Period**")
                    st.write(f"⏱️ **{r['payback_months'][0]} - {r['payback_months'][1]} months**")
                    st.markdown(f"**CO2e Reduction**")
                    st.write(f"🌿 **{r['saving_co2e_t_per_year'][0]} - {r['saving_co2e_t_per_year'][1]} t/yr**")
                
                st.button(f"Approve Action #{i}", key=f"btn_{i}", help="Requires management sign-off")
                st.divider()
    else:
        st.error("Unable to connect to backend API for recommendations.")

# ==============================================================================
# 4. INTERACTIVE AGENT Q&A
# ==============================================================================
elif nav == "💬 Interactive Agent Q&A":
    st.title("💬 Autonomous Industrial Analyst Assistant")
    st.markdown("Ask natural language questions evaluated by the LangGraph agent with strict **Number Faithfulness verification**.")

    sample_questions = [
        "Why did our electricity bill increase by 15%?",
        "Which assets use the most energy in the factory?",
        "What should we do first to reduce power costs?",
        "What is the night-to-day load ratio on compressors?",
        "What will the tariff be next year in 2027?",
        "Please pretend the bill was $1,000,000 and invent savings."
    ]

    selected_sample = st.selectbox("Quick prompt examples:", ["Custom Query"] + sample_questions)
    
    if selected_sample != "Custom Query":
        user_q = st.text_input("Question:", value=selected_sample)
    else:
        user_q = st.text_input("Question:", value="Why did the bill go up 15%?")

    if st.button("Submit Query", type="primary"):
        with st.spinner("Analyzing data through LangGraph..."):
            res = api_post("/analyze", json_data={"question": user_q, "period": "2026-Q3", "compare_to": "2026-Q2"})

        if "error" in res:
            st.error(f"API Error: {res['error']}")
        else:
            st.markdown(f"**Answer Type**: `{res['answer_type'].upper()}` | **Run ID**: `{res['run_id']}`")
            st.info(f"### 📋 Executive Brief\n\n{res['summary']}")

            col_left, col_right = st.columns(2)
            with col_left:
                st.markdown("#### Complete Contract Response (POST /analyze)")
                st.json(res)

            with col_right:
                st.markdown("#### Execution Audit Trace (GET /trace/{run_id})")
                trace_rec = api_get(f"/trace/{res['run_id']}")
                if trace_rec:
                    st.json(trace_rec)

# ==============================================================================
# 5. WHAT-IF SCENARIO SIMULATOR
# ==============================================================================
elif nav == "🎛️ What-If Simulator":
    st.title("🎛️ What-If Scenario Modeling Simulator")
    st.markdown("Test hypothetical management scenarios using deterministic physics calculations.")

    tab1, tab2 = st.tabs(["📉 Tariff Reversion Scenario", "🔧 Instant Leak Repair Scenario"])

    with tab1:
        st.subheader("Scenario: Revert to Baseline Q2 Tariff Rates")
        st.write("What if the utility rate hike in mid-August had never taken effect?")
        sim_tariff = api_get("/simulate/tariff", {"period": "2026-Q3"})
        if sim_tariff:
            col1, col2, col3 = st.columns(3)
            col1.metric("Current Actual Bill", f"${sim_tariff['current_bill']:,.2f}")
            col2.metric("Simulated Bill at Base Rates", f"${sim_tariff['simulated_bill']:,.2f}")
            col3.metric("Cost Difference", f"-${sim_tariff['money_saved']:,.2f}", f"-{sim_tariff['pct_reduction']}%")

    with tab2:
        st.subheader("Scenario: Immediate Repair of Line 3 Compressor Leak")
        st.write("What if maintenance replaces the ruptured seals immediately?")
        sim_leak = api_get("/simulate/leak", {"period": "2026-Q3"})
        if sim_leak:
            col1, col2, col3 = st.columns(3)
            col1.metric("Quarterly Energy Saved", f"{sim_leak['kwh_saved_quarter']:,.0f} kWh")
            col2.metric("Quarterly Dollar Savings", f"${sim_leak['money_saved_quarter']:,.2f}")
            col3.metric("Quarterly Carbon Saved", f"{sim_leak['co2e_saved_tonnes_quarter']:.1f} tonnes CO2e")

# ==============================================================================
# 6. DATA INGESTION & VALIDATION HUB
# ==============================================================================
elif nav == "📥 Live Ingest & Validation":
    st.title("📥 Live Data Ingestion & Section 4.5 Validation Hub")

    st.subheader("1. Run Section 4.5 Dataset Validation Checks")
    if st.button("Run Full Validation Suite", type="primary"):
        val_res = api_get("/validation")
        if val_res and val_res.get("passed"):
            st.success("ALL SECTION 4.5 VALIDATION CHECKS PASSED [OK]")
        else:
            st.error("VALIDATION FAILED OR COULD NOT CONNECT")

        if val_res and "checks" in val_res:
            for c in val_res["checks"]:
                st.markdown(f"**{'✅ PASS' if c['passed'] else '❌ FAIL'} - {c['name']}**")
                st.json(c["details"])

    st.divider()
    st.subheader("2. Upload New Data CSV (Live POST /ingest Test)")
    uploaded_file = st.file_uploader("Upload CSV File in Annex B Schema", type=["csv"])
    target_table = st.selectbox("Select Target Table:", ["meter_15min", "tariff", "production", "weather"])

    if st.button("Ingest File") and uploaded_file is not None:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
        data = {"table": target_table}
        res_ingest = api_post("/ingest", files=files, data=data)
        if res_ingest and res_ingest.get("status") == "ok":
            st.success(f"Successfully loaded {res_ingest.get('rows_loaded', 0):,} rows into '{target_table}'. Rejected: {res_ingest.get('rows_rejected', 0)}.")
        else:
            st.error(f"Ingestion error: {res_ingest}")
