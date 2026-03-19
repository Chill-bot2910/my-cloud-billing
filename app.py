import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# 1. ตั้งค่าหน้าเว็บ (Cyberpunk Mode)
st.set_page_config(page_title="Cloud Billing Command Center", layout="wide", page_icon="⚡")

# --- 🌌 Advanced Cyberpunk Custom CSS ---
st.markdown("""
    <style>
    /* พื้นหลังหลักของระบบ */
    .stApp {
        background-color: #0d1117;
        color: #e6edf3;
    }
    
    /* กล่อง Metric แบบมีขอบนีออนและเงาเรืองแสง */
    div[data-testid="stMetric"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-left: 4px solid #00d4ff;
        padding: 20px;
        border-radius: 12px;
        transition: 0.3s ease-in-out;
    }
    div[data-testid="stMetric"]:hover {
        border-color: #00d4ff;
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.2);
        transform: translateY(-2px);
    }

    /* ตัวเลขเรืองแสงนีออน (Neon Glow Effect) */
    div[data-testid="stMetricValue"] > div {
        color: #00d4ff !important;
        text-shadow: 0 0 5px #00d4ff, 0 0 10px #00d4ff, 0 0 20px rgba(0, 212, 255, 0.5);
        font-family: 'Courier New', monospace;
        font-weight: 800 !important;
        font-size: 2rem !important;
    }

    /* หัวข้อกล่องแบบ Futuristic */
    div[data-testid="stMetricLabel"] > div > p {
        color: #8b949e !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-size: 0.85rem !important;
        font-weight: bold;
    }

    /* พาดหัว Title นีออน */
    h1 {
        color: #00d4ff;
        text-shadow: 2px 2px 15px rgba(0, 212, 255, 0.6);
        text-transform: uppercase;
        letter-spacing: 4px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* ตกแต่งปุ่ม Refresh ให้เข้ากับธีม */
    .stButton>button {
        background-color: #1f6feb;
        color: white;
        border: 1px solid #00d4ff;
        border-radius: 8px;
        font-weight: bold;
        text-transform: uppercase;
    }
    .stButton>button:hover {
        background-color: #00d4ff;
        color: #0d1117;
        box-shadow: 0 0 15px #00d4ff;
    }

    /* Progress Bar แบบเลเซอร์ */
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #00d4ff, #008bcf);
        box-shadow: 0 0 10px #00d4ff;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. Header & Control ---
col_title, col_btn = st.columns([4, 1])
with col_title:
    st.title("⚡ CLOUD COMMAND CENTER")
    st.markdown(f"📡 **SYSTEM STATUS:** `ACTIVE` | 🗓️ **TIMESTAMP:** `{datetime.now().strftime('%d/%m/%Y %H:%M')}`")

with col_btn:
    st.write("##")
    if st.button("🔄 RE-SYNC DATA", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.markdown("<hr style='border-color: #30363d;'>", unsafe_allow_html=True)

# --- 3. ดึงข้อมูลจาก Google Sheets ---
sheet_id = "11_nlGeuVRskPtH8K3QZ2BtEOHAon5w7jl2w37GupWtI"
sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

try:
    df = pd.read_csv(sheet_url)
    df.columns = df.columns.str.strip()

    if not df.empty:
        # เตรียมข้อมูลแถวล่าสุด
        latest = df.iloc[-1]
        total_thb = float(latest.get('Total Cost (THB)', 0))
        total_usd_val = float(latest.get('Total Cost (USD)', 0))
        ex_rate = float(latest.get('Exchange Rate', 32.72))
        gcp_usd = float(latest.get('gcp_usd', 0))
        do_usd = float(latest.get('do_usd', 0))
        val_tokens = latest.get('Gemini Tokens', 0)
        display_tokens = 0 if pd.isna(val_tokens) else val_tokens

        # --- 4. Neon Metrics Row (5 กล่องครบถ้วน) ---
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("💳 Total (THB)", f"฿{total_thb:,.2f}")
        m2.metric("🧠 Gemini ($)", f"${gcp_usd:,.2f}")
        m3.metric("🛰️ DO Cluster", f"${do_usd:,.2f}")
        m4.metric("📊 Tokens", f"{display_tokens:,.0f}")
        m5.metric("💹 EX Rate", f"{ex_rate:.2f}")

        st.write("##")

        # --- 5. Main Analysis Grid ---
        left_col, right_col = st.columns([2, 1])

        with left_col:
            with st.container(border=True):
                st.subheader("⚡ Consumption Waveform")
                chart_df = df.copy().set_index('Date')
                st.area_chart(chart_df['Total Cost (THB)'], color="#1f6feb")
                
                st.divider()
                
                st.subheader("🔋 Power Grid Status ($15.00 Limit)")
                budget_limit = 15.0
                usage_percent = (total_usd_val / budget_limit)
                status_text = f"CORE LOAD: {usage_percent*100:.1f}%"
                
                if usage_percent >= 1.0:
                    st.error(f"🚨 CRITICAL OVERLOAD: {status_text}")
                elif usage_percent >= 0.8:
                    st.warning(f"⚠️ HIGH LOAD WARNING: {status_text}")
                else:
                    st.info(f"✅ SYSTEM NOMINAL: {status_text}")
                
                st.progress(min(usage_percent, 1.0))

        with right_col:
            with st.container(border=True):
                st.subheader("💠 Resource Breakdown")
                pie_df = pd.DataFrame({
                    "Source": ["Gemini (GCP)", "DigitalOcean"],
                    "Cost": [gcp_usd, do_usd]
                })
                # ปรับแต่งสีพายให้นีออนส้ม-ฟ้า
                fig = px.pie(pie_df, values='Cost', names='Source', hole=0.7,
                             color_discrete_map={"Gemini (GCP)": "#FF9F00", "DigitalOcean": "#00D4FF"})
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color="#e6edf3",
                    showlegend=False,
                    margin=dict(t=10, b=10, l=10, r=10)
                )
                st.plotly_chart(fig, use_container_width=True)

            with st.container(border=True):
                st.subheader("🔮 Neural Forecast")
                day_of_month = datetime.now().day
                projected_thb = (total_thb / day_of_month) * 31
                st.metric("Estimated Monthly End", f"฿{projected_thb:,.2f}", 
                          delta=f"{(projected_thb - total_thb):,.2f} THB to go")

        # --- 6. Data Stream ---
        with st.expander("💾 ACCESS DATABASE LOG"):
            st.dataframe(df.sort_index(ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"🚫 SYSTEM BREACH / DATA ERROR: {e}")
