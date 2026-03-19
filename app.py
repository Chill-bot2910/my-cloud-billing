import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# 1. ตั้งค่าหน้าเว็บ (Minimal & Clean)
st.set_page_config(page_title="Cloud Billing | Minimal", layout="wide", page_icon="☁️")

# --- 🎨 Minimal Pastel Custom CSS ---
st.markdown("""
<style>
/* พื้นหลังสีขาวนวลสบายตา */
.stApp {
    background-color: #fcfcfd;
    color: #31333f;
}

/* กล่อง Metric แบบโค้งมนและมีเงาบางๆ (Soft Shadow) */
div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #f0f2f6;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.02);
}

/* ตัวเลข Metric สีเข้มชัดเจนแต่ไม่ปวดตา */
div[data-testid="stMetricValue"] > div {
    color: #1f2937 !important;
    font-family: 'Inter', sans-serif;
    font-size: 1.8rem !important;
    font-weight: 600 !important;
}

/* หัวข้อกล่องสีพาสเทล */
div[data-testid="stMetricLabel"] > div > p {
    color: #6b7280 !important;
    text-transform: none;
    letter-spacing: 0px;
    font-size: 0.95rem !important;
}

/* หัวข้อ Title แบบ Minimal Gradient */
h1 {
    background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 700;
}

/* ปุ่ม Refresh แบบพาสเทล */
.stButton>button {
    background-color: #f3f4f6;
    color: #374151;
    border: none;
    border-radius: 10px;
    transition: 0.2s;
}
.stButton>button:hover {
    background-color: #e5e7eb;
    color: #111827;
}

/* Progress Bar สีพาสเทล */
.stProgress > div > div > div > div {
    background-image: linear-gradient(to right, #a18cd1 0%, #fbc2eb 100%);
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# --- 2. Header ---
col_t, col_b = st.columns([4, 1])
with col_t:
    st.title("Cloud Billing Dashboard")
    st.markdown(f"✨ **Status:** Operational  |  🕒 **Updated:** {datetime.now().strftime('%H:%M')}")
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

        # --- 4. Metric Grid (5 กล่อง) ---
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Total Spent (THB)", f"฿{total_thb:,.2f}")
        m2.metric("Gemini (GCP)", f"${gcp_usd:,.2f}")
        m3.metric("DigitalOcean", f"${do_usd:,.2f}")
        m4.metric("Tokens Used", f"{display_tokens:,.0f}")
        m5.metric("Exchange Rate", f"{ex_rate:.2f}")

        st.write("##")

        # --- 5. Main Area ---
        l_col, r_col = st.columns([2, 1])

        with l_col:
            with st.container(border=True):
                st.subheader("📈 Monthly Trend")
                chart_df = df.copy().set_index('Date')
                # ใช้กราฟเส้นพาสเทลนุ่มๆ
                st.area_chart(chart_df['Total Cost (THB)'], color="#a18cd1")
                
                st.divider()
                st.subheader("🏷️ Budget Overview ($15.00)")
                usage_p = (total_usd_val / 15.0)
                st.progress(min(usage_p, 1.0), text=f"{usage_p*100:.1f}% of monthly budget used")

        with r_col:
            with st.container(border=True):
                st.subheader("🍰 Cost Split")
                pie_df = pd.DataFrame({
                    "Source": ["GCP", "DigitalOcean"],
                    "Cost": [gcp_usd, do_usd]
                })
                # สีพาสเทล: ม่วงอ่อน และ ฟ้าอ่อน
                fig = px.pie(pie_df, values='Cost', names='Source', hole=0.6,
                             color_discrete_sequence=["#a18cd1", "#84fab0"])
                fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig, use_container_width=True)

            with st.container(border=True):
                st.subheader("🔮 Forecast")
                day = datetime.now().day
                projected = (total_thb / day) * 31
                st.metric("Estimated Total", f"฿{projected:,.2f}")

        # --- 6. Logs ---
        with st.expander("📄 View History"):
            st.dataframe(df.sort_index(ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")
