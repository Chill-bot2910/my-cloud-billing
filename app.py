import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Cloud Billing | Cute Minimal", layout="wide", page_icon="🌸")

# --- 🎨 Cute Minimal Custom CSS (เพิ่ม Font น่ารัก) ---
st.markdown("""
<style>
/* ดึงฟอนต์ Kanit จาก Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;600&display=swap');

/* ใช้ฟอนต์ Kanit กับทั้งแอป */
html, body, [class*="css"], .stMarkdown, p, div {
    font-family: 'Kanit', sans-serif !important;
}

/* พื้นหลังนุ่มนวล */
.stApp {
    background-color: #fcfcfd;
}

/* กล่อง Metric พร้อม Shadow และ Hover */
div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #f0f2f6;
    padding: 22px;
    border-radius: 20px; /* เพิ่มความโค้งมนให้น่ารักขึ้น */
    box-shadow: 0 4px 15px rgba(0,0,0,0.03);
    transition: all 0.3s ease-in-out;
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-7px) scale(1.02); /* ลอยและขยายเล็กน้อย */
    box-shadow: 0 10px 25px rgba(0,0,0,0.07);
    border-color: #e2e8f0;
}

/* ตัวเลข Metric (เน้นความกลมมน) */
div[data-testid="stMetricValue"] > div {
    color: #4a5568 !important;
    font-size: 2rem !important;
    font-weight: 600 !important;
}

/* หัวข้อ Title ไล่เฉดสีพาสเทล ม่วง-ชมพู */
h1 {
    background: linear-gradient(90deg, #a18cd1 0%, #fbc2eb 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 700;
    font-size: 2.5rem !important;
}

/* ปรับแต่งปุ่มให้น่ารัก */
.stButton>button {
    border-radius: 12px;
    border: 1px solid #fbc2eb;
    background-color: white;
    color: #a18cd1;
    font-weight: 600;
}
.stButton>button:hover {
    background-color: #fbc2eb;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# --- 2. Header & Timezone (GMT+7) ---
now_th = datetime.utcnow() + timedelta(hours=7)

col_t, col_b = st.columns([4, 1])
with col_t:
    st.title("Cloud Billing Dashboard")
    st.markdown(f"🌸 **Status:** Healthy  |  🕒 **Update:** {now_th.strftime('%H:%M:%S')} (BKK)")
with col_b:
    st.write("##")
    if st.button("🔄 Sync Now", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.markdown("---")

# --- 3. ข้อมูล & การแสดงผล (เหมือนเดิมแต่เปลี่ยนสไตล์) ---
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

        # --- 4. Metric Grid ---
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("💰 ยอดรวมทั้งหมด", f"฿{total_thb:,.2f}")
        m2.metric("🧠 จีมินาย (GCP)", f"${gcp_usd:,.2f}")
        m3.metric("💧 เซิร์ฟเวอร์ (DO)", f"${do_usd:,.2f}")
        m4.metric("📊 การใช้โทเคน", f"{display_tokens:,.0f}")
        m5.metric("💹 เรทเงินบาท", f"{ex_rate:.2f}")

        st.write("##")

        # --- 5. Main Content Area ---
        l_col, r_col = st.columns([2, 1])

        with l_col:
            with st.container(border=True):
                st.subheader("📈 แนวโน้มการใช้งาน")
                chart_df = df.copy().set_index('Date')
                st.area_chart(chart_df['Total Cost (THB)'], color="#fbc2eb")
                
                st.divider()
                st.subheader("🏁 เป้าหมายงบประมาณ ($15.00)")
                usage_p = (total_usd_val / 15.0)
                st.progress(min(usage_p, 1.0), text=f"ใช้วงเงินไปแล้ว: {usage_p*100:.1f}%")

        with r_col:
            with st.container(border=True):
                st.subheader("🍰 สัดส่วนค่าใช้จ่าย")
                pie_df = pd.DataFrame({
                    "Source": ["GCP", "DigitalOcean"],
                    "Cost": [gcp_usd, do_usd]
                })
                # สีพาสเทลม่วงและฟ้าอ่อน
                fig = px.pie(pie_df, values='Cost', names='Source', hole=0.6,
                             color_discrete_sequence=["#a18cd1", "#fbc2eb"])
                fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), font=dict(family="Kanit"))
                st.plotly_chart(fig, use_container_width=True)

            with st.container(border=True):
                st.subheader("🔮 ทำนายยอดสิ้นเดือน")
                day = now_th.day
                projected = (total_thb / day) * 31
                st.metric("คาดการณ์ยอดรวม", f"฿{projected:,.2f}", delta=f"฿{projected - total_thb:,.2f}")

except Exception as e:
    st.error(f"Error: {e}")
