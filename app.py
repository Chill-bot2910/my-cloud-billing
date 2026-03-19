import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Cloud Billing | Soft Minimal", layout="wide", page_icon="☁️")

# --- 🎨 Soft Minimal Custom CSS ---
st.markdown("""
<style>
/* พื้นหลังนุ่มนวล */
.stApp {
    background-color: #fcfcfd;
}

/* กล่อง Metric พร้อม Shadow และ Hover Effect */
div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #f0f2f6;
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    transition: all 0.3s ease-in-out;
}

/* เอฟเฟกต์ลอยขึ้นเมื่อเมาส์โดน */
div[data-testid="stMetric"]:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.06);
    border-color: #d1d5db;
}

/* ตัวเลข Metric */
div[data-testid="stMetricValue"] > div {
    color: #111827 !important;
    font-size: 1.8rem !important;
    font-weight: 700 !important;
}

/* หัวข้อ Title ไล่เฉดสี */
h1 {
    background: linear-gradient(90deg, #8e2de2 0%, #4a00e0 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
}

/* ปรับแต่งส่วน Container อื่นๆ */
[data-testid="stVerticalBlockBorderWrapper"] {
    transition: all 0.3s ease;
    border-radius: 16px !important;
}
</style>
""", unsafe_allow_html=True)

# --- 2. Header & Timezone Fix (GMT+7) ---
now_th = datetime.utcnow() + timedelta(hours=7)

col_t, col_b = st.columns([4, 1])
with col_t:
    st.title("Cloud Billing Dashboard")
    st.markdown(f"✨ **Status:** Operational  |  🕒 **Updated:** {now_th.strftime('%H:%M:%S')} (ICT)")
with col_b:
    st.write("##")
    if st.button("🔄 Sync Now", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.markdown("---")

# --- 3. ดึงข้อมูล ---
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
        do_usd = float(latest.get('do_usd', 0))
        val_tokens = latest.get('Gemini Tokens', 0)
        display_tokens = 0 if pd.isna(val_tokens) else val_tokens

        # --- 4. Metric Grid พร้อม Emoji ---
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("💰 Total Spent", f"฿{total_thb:,.2f}")
        m2.metric("🧠 Gemini (GCP)", f"${gcp_usd:,.2f}")
        m3.metric("💧 DigitalOcean", f"${do_usd:,.2f}")
        m4.metric("📊 Tokens Used", f"{display_tokens:,.0f}")
        m5.metric("💹 EX Rate", f"{ex_rate:.2f}")

        st.write("##")

        # --- 5. Main Content Area ---
        l_col, r_col = st.columns([2, 1])

        with l_col:
            with st.container(border=True):
                st.subheader("📈 Spending Trend")
                chart_df = df.copy().set_index('Date')
                st.area_chart(chart_df['Total Cost (THB)'], color="#8e2de2")
                
                st.divider()
                st.subheader("🏁 Budget Tracker ($15.00)")
                usage_p = (total_usd_val / 15.0)
                st.progress(min(usage_p, 1.0), text=f"Used: {usage_p*100:.1f}%")

        with r_col:
            with st.container(border=True):
                st.subheader("🍰 Cost Split")
                pie_df = pd.DataFrame({
                    "Source": ["GCP", "DigitalOcean"],
                    "Cost": [gcp_usd, do_usd]
                })
                fig = px.pie(pie_df, values='Cost', names='Source', hole=0.6,
                             color_discrete_sequence=["#8e2de2", "#00d2ff"])
                fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig, use_container_width=True)

            with st.container(border=True):
                st.subheader("🔮 Forecast")
                day = now_th.day
                projected = (total_thb / day) * 31
                st.metric("Estimated Total", f"฿{projected:,.2f}", delta=f"฿{projected - total_thb:,.2f}")

        # --- 6. Table ---
        with st.expander("📄 Full History"):
            st.dataframe(df.sort_index(ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")
