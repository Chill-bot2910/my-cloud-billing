import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Cloud Billing Pro", layout="wide", page_icon="📊")

# --- 🎨 Custom CSS สำหรับพื้นหลังและสไตล์ ---
st.markdown("""
    <style>
    /* เปลี่ยนสีพื้นหลังของทั้งหน้า */
    .stApp {
        background-color: #f8f9fa;
    }
    /* ปรับแต่งกล่อง Container ให้ดูนูนและสะอาด */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e9ecef;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    /* หัวข้อใหญ่ */
    h1 {
        color: #1c2e4a;
        font-weight: 800;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Header ---
col_title, col_btn = st.columns([4, 1])
with col_title:
    st.title("📊 Cloud Billing Command Center")
    st.markdown(f"🗓️ **Snapshot:** `{datetime.now().strftime('%d/%m/%Y %H:%M')}`")

with col_btn:
    st.write("##")
    if st.button("🔄 Sync Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.markdown("---")

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

        # --- 3. Metrics Section (3 กล่องหลักที่ดูสะอาดตา) ---
        m1, m2, m3 = st.columns(3)
        m1.metric("💰 Total Spending", f"฿{total_thb:,.2f}")
        m2.metric("🤖 Gemini Usage", f"${gcp_usd:,.2f}")
        m3.metric("💧 Server (DO)", f"${do_usd:,.2f}")

        st.write("##")

        # --- 4. Main Dashboard Area ---
        left_col, right_col = st.columns([2, 1])

        with left_col:
            # ใช้ st.expander หรือ Container ในการจัดกลุ่ม
            with st.container(border=True):
                st.subheader("📈 Consumption Trend (THB)")
                chart_df = df.copy().set_index('Date')
                st.area_chart(chart_df['Total Cost (THB)'], color="#4A90E2")
                
                st.divider()
                
                st.subheader("🏁 Budget Progress ($15.00)")
                usage_percent = (total_usd_val / 15.0)
                bar_color = "blue" if usage_percent < 0.8 else "orange" if usage_percent < 1.0 else "red"
                st.progress(min(usage_percent, 1.0), text=f"Used: {usage_percent*100:.1f}%")

        with right_col:
            with st.container(border=True):
                st.subheader("🍰 Cost Breakdown")
                pie_df = pd.DataFrame({
                    "Source": ["Gemini (GCP)", "DigitalOcean"],
                    "Cost": [gcp_usd, do_usd]
                })
                fig = px.pie(pie_df, values='Cost', names='Source', hole=0.6,
                             color_discrete_map={"Gemini (GCP)": "#FF9900", "DigitalOcean": "#008bcf"})
                fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig, use_container_width=True)

            with st.container(border=True):
                st.subheader("🔮 Smart Forecast")
                day_of_month = datetime.now().day
                projected_thb = (total_thb / day_of_month) * 31
                st.metric("Estimated End of Month", f"฿{projected_thb:,.2f}", 
                          delta=f"{(projected_thb - total_thb):,.2f} more")

        # --- 5. Data Table ---
        with st.expander("📄 View Full Billing History"):
            st.dataframe(df.sort_index(ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"❌ Error loading data: {e}")
