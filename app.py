import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Cloud Billing | Cute Itim", layout="wide", page_icon="🌸")

# --- 🎨 Cute Itim Custom CSS ---
st.markdown("""
<style>
/* ดึงฟอนต์ Itim จาก Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Itim&display=swap');

/* บังคับใช้ฟอนต์ Itim กับทุกส่วน */
html, body, [class*="css"], .stMarkdown, p, div, h1, h2, h3, h4, span, label, .stMetricValue {
    font-family: 'Itim', cursive !important;
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
    border-radius: 25px;
    box-shadow: 0 10px 20px rgba(0,0,0,0.03);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

/* เอฟเฟกต์ลอยตัวเมื่อเมาส์โดน */
div[data-testid="stMetric"]:hover {
    transform: translateY(-10px) scale(1.03);
    box-shadow: 0 15px 30px rgba(161, 140, 209, 0.15);
    border-color: #fbc2eb;
}

/* ตัวเลข Metric สีม่วงน้ำเงินละมุน */
div[data-testid="stMetricValue"] > div {
    color: #5a67d8 !important;
    font-size: 2.2rem !important;
}

/* หัวข้อ Title ไล่เฉดสีพาสเทล */
h1 {
    background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 3rem !important;
    font-weight: 700;
}

/* ปรับปรุง Progress Bar */
.stProgress > div > div > div > div {
    background-image: linear-gradient(to right, #a18cd1, #fbc2eb);
    border-radius: 20px;
}
</style>
""", unsafe_allow_html=True)

# --- 2. Header & Timezone Fix (BKK) ---
now_th = datetime.utcnow() + timedelta(hours=7)

col_t, col_b = st.columns([4, 1])
with col_t:
    st.title("Cloud Billing Dashboard")
    st.markdown(f"🌸 **สถานะระบบ:** ปกติเรียบร้อยดี  |  🕒 **อัปเดตเมื่อ:** {now_th.strftime('%H:%M:%S')} น.")
with col_b:
    st.write("##")
    if st.button("🔄 ดึงข้อมูลใหม่", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.markdown("---")

# --- 3. ดึงข้อมูลจาก Google Sheets ---
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

        # --- 4. Metric Grid (5 กล่องพร้อม Emoji) ---
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
                # ใช้สีพาสเทลชมพูอมม่วงให้น่ารัก
                st.area_chart(chart_df['Total Cost (THB)'], color="#fbc2eb")
                
                st.divider()
                st.subheader("🏁 เป้าหมายงบประมาณ ($15.00)")
                usage_p = (total_usd_val / 15.0)
                st.progress(min(usage_p, 1.0), text=f"ใช้วงเงินไปแล้ว: {usage_p*100:.1f}%")

        with r_col:
            with st.container(border=True):
                st.subheader("🍰 สัดส่วนค่าใช้จ่าย")
                pie_df = pd.DataFrame({
                    "ค่าย": ["GCP", "DigitalOcean"],
                    "ค่าใช้จ่าย": [gcp_usd, do_usd]
                })
                fig = px.pie(pie_df, values='ค่าใช้จ่าย', names='ค่าย', hole=0.6,
                             color_discrete_sequence=["#a18cd1", "#fbc2eb"])
                fig.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), font=dict(family="Itim"))
                st.plotly_chart(fig, use_container_width=True)

            with st.container(border=True):
                st.subheader("🔮 ทำนายยอดสิ้นเดือน")
                day = now_th.day
                projected = (total_thb / day) * 31
                st.metric("คาดการณ์ยอดรวม", f"฿{projected:,.2f}", delta=f"฿{projected - total_thb:,.2f}")

        # --- 6. Table ---
        with st.expander("📄 ดูประวัติย้อนหลังทั้งหมด"):
            st.dataframe(df.sort_index(ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"อุ๊ย! เกิดข้อผิดพลาดบางอย่าง: {e}")
