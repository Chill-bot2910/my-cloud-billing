import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Cloud Billing Cyberpunk", layout="wide", page_icon="⚡")

# --- 🌌 Cyberpunk Custom CSS ---
st.markdown("""
    <style>
    /* พื้นหลังสีน้ำเงินเข้ม-ดำ */
    .stApp {
        background-color: #0d1117;
        color: #e6edf3;
    }
    /* ปรับแต่งกล่อง Metric ให้มีขอบนีออน */
    div[data-testid="stMetric"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-left: 5px solid #00d4ff; /* เส้นสีฟ้านีออนด้านซ้าย */
        padding: 20px;
        border-radius: 8px;
        transition: 0.3s;
    }
    div[data-testid="stMetric"]:hover {
        border-color: #00d4ff;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.3);
    }
    /* หัวข้อ Title สีฟ้านีออน */
    h1 {
        color: #00d4ff;
        font-family: 'Courier New', Courier, monospace;
        text-transform: uppercase;
        letter-spacing: 2px;
        text-shadow: 2px 2px 10px rgba(0, 212, 255, 0.5);
    }
    /* ปรับแต่งปุ่ม Refresh */
    .stButton>button {
        background-color: #1f6feb;
        color: white;
        border: none;
        border-radius: 5px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #388bfd;
        box-shadow: 0 0 20px rgba(31, 111, 235, 0.6);
    }
    /* สไตล์สำหรับกล่อง Container */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #30363d !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Header ---
col_title, col_btn = st.columns([4, 1])
with col_title:
    st.title("⚡ CLOUD BILLING COMMAND")
    st.markdown(f"📡 **SYSTEM STATUS:** `STABLE` | 🗓️ **SNAPSHOT:** `{datetime.now().strftime('%d/%m/%Y %H:%M')}`")

with col_btn:
    st.write("##")
    if st.button("🔄 RE-SYNC SYSTEM", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.markdown("<hr style='border-color: #30363d;'>", unsafe_allow_html=True)

# 2. ดึงข้อมูล
sheet_id = "11_nlGeuVRskPtH8K3QZ2BtEOHAon5w7jl2w37GupWtI"
sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

try:
    df = pd.read_csv(sheet_url)
    df.columns = df.columns.str.strip()

    if not df.empty:
        latest = df.iloc[-1]
        total_thb = float(latest.get('Total Cost (THB)', 0))
        total_usd_val = float(latest.get('Total Cost (USD)', 0))
        ex_rate = float(latest.get('Exchange Rate', 32.72))
        gcp_usd = float(latest.get('gcp_usd', 0))
        do_usd = float(latest.get('do_usd', 5.21))
        val_tokens = latest.get('Gemini Tokens', 0)
        display_tokens = 0 if pd.isna(val_tokens) else val_tokens

        # --- 3. Neon Metrics Section ---
        m1, m2, m3 = st.columns(3)
        m1.metric("💳 TOTAL SPENT", f"฿{total_thb:,.2f}")
        m2.metric("🧠 GEMINI UNIT", f"${gcp_usd:,.2f}")
        m3.metric("🛰️ DO CLUSTER", f"${do_usd:,.2f}")

        st.write("##")

        # --- 4. Main Grid ---
        left_col, right_col = st.columns([2, 1])

        with left_col:
            with st.container(border=True):
                st.subheader("📊 Consumption Waveform")
                chart_df = df.copy().set_index('Date')
                # ใช้กราฟพื้นที่สีฟ้าเข้ม
                st.area_chart(chart_df['Total Cost (THB)'], color="#1f6feb")
                
                st.divider()
                
                st.subheader("🔋 Budget Power Grid ($15.00)")
                usage_percent = (total_usd_val / 15.0)
                # เลือกสีตามความวิกฤต
                bar_text = f"LOAD: {usage_percent*100:.1f}%"
                st.progress(min(usage_percent, 1.0), text=bar_text)

        with right_col:
            with st.container(border=True):
                st.subheader("💠 Resource Core")
                pie_df = pd.DataFrame({
                    "Source": ["Gemini (GCP)", "DigitalOcean"],
                    "Cost": [gcp_usd, do_usd]
                })
                # สีส้มนีออน และ ฟ้านีออน
                fig = px.pie(pie_df, values='Cost', names='Source', hole=0.7,
                             color_discrete_map={"Gemini (GCP)": "#FF9F00", "DigitalOcean": "#00D4FF"})
                
                # ตกแต่งกราฟให้เข้ากับ Dark Mode
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color="#e6edf3",
                    showlegend=False,
                    margin=dict(t=10, b=10, l=10, r=10)
                )
                st.plotly_chart(fig, use_container_width=True)

            with st.container(border=True):
                st.subheader("📡 Neural Forecast")
                day_of_month = datetime.now().day
                projected_thb = (total_thb / day_of_month) * 31
                st.metric("Estimated Monthly End", f"฿{projected_thb:,.2f}", 
                          delta=f"{(projected_thb - total_thb):,.2f} THB to go")

        # --- 5. Raw Data Stream ---
        with st.expander("💾 Access Database Log"):
            st.dataframe(df.sort_index(ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"🚫 SYSTEM ERROR: {e}")
