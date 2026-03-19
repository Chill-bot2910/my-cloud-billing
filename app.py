import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Cloud Billing | Vibrant Pastel", layout="wide", page_icon="🌸")

# --- 🎨 Vibrant Pastel Custom CSS ---
st.markdown("""
<style>
/* ดึงฟอนต์ Itim */
@import url('https://fonts.googleapis.com/css2?family=Itim&display=swap');

/* บังคับใช้ฟอนต์ Itim ทุกจุด (ยกเว้นไอคอนระบบ) */
html, body, [class*="css"], .stMarkdown, p, div:not([data-testid="stIcon"]), h1, h2, h3, h4, span, label, .stMetricValue {
    font-family: 'Itim', cursive !important;
}

.stApp {
    background-color: #fcfcfd;
}

/* กล่อง Metric - ปรับแต่งเงาและสีตัวเลขแยกกล่อง */
div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #f0f2f6;
    padding: 20px;
    border-radius: 20px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    transition: all 0.4s ease;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.06);
}

/* --- 🌈 กำหนดสีตัวเลขแยกตามกล่อง (5 สี) --- */
/* กล่องที่ 1: ยอดรวม (สีม่วงพาสเทล) */
div[data-testid="column"]:nth-child(1) div[data-testid="stMetricValue"] > div { color: #8e44ad !important; }
/* กล่องที่ 2: Gemini (สีชมพูพาสเทล) */
div[data-testid="column"]:nth-child(2) div[data-testid="stMetricValue"] > div { color: #e91e63 !important; }
/* กล่องที่ 3: DigitalOcean (สีฟ้าน้ำทะเล) */
div[data-testid="column"]:nth-child(3) div[data-testid="stMetricValue"] > div { color: #00bcd4 !important; }
/* กล่องที่ 4: Tokens (สีเขียวพาสเทล) */
div[data-testid="column"]:nth-child(4) div[data-testid="stMetricValue"] > div { color: #27ae60 !important; }
/* กล่องที่ 5: อัตราแลกเปลี่ยน (สีส้มทอง) */
div[data-testid="column"]:nth-child(5) div[data-testid="stMetricValue"] > div { color: #f39c12 !important; }

div[data-testid="stMetricValue"] > div {
    font-size: 2.2rem !important;
    font-weight: 700 !important;
}

/* หัวข้อ Title */
h1 {
    background: linear-gradient(90deg, #6a11cb, #fbc2eb);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.8rem !important;
}
</style>
""", unsafe_allow_html=True)

# --- 2. Header & Timezone (GMT+7) ---
now_th = datetime.utcnow() + timedelta(hours=7)

col_t, col_b = st.columns([4, 1])
with col_t:
    st.title("Cloud Billing Center")
    st.markdown(f"🌸 **สถานะระบบ:** ปกติ  |  🕒 **เวลาอัปเดต:** {now_th.strftime('%H:%M:%S')} น.")
with col_b:
    st.write("##")
    if st.button("🔄 Sync ข้อมูลใหม่", use_container_width=True):
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

        # --- 4. Metric Grid (5 สี พร้อมชื่อชัดเจน) ---
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("💰 ยอดรวมทั้งหมด (บาท)", f"฿{total_thb:,.2f}")
        m2.metric("🧠 ค่าใช้จ่าย Gemini", f"${gcp_usd:,.2f}")
        m3.metric("💧 DigitalOcean", f"${do_usd:,.2f}")
        m4.metric("📊 จำนวนโทเคนที่ใช้", f"{display_tokens:,.0f}")
        m5.metric("💹 อัตราแลกเปลี่ยน", f"{ex_rate:.2f}")

        st.write("##")

        # --- 5. Content Area ---
        l_col, m_col, r_col = st.columns([1.8, 0.7, 1])

        with l_col:
            with st.container(border=True):
                st.subheader("📈 กราฟแนวโน้มค่าใช้จ่าย")
                chart_df = df.copy().set_index('Date')
                st.area_chart(chart_df['Total Cost (THB)'], color="#a18cd1")
                
                st.divider()
                st.subheader("🏁 สถานะงบประมาณ ($15.00)")
                usage_p = (total_usd_val / 15.0)
                bar_color = "#4ade80" if usage_p < 0.5 else "#facc15" if usage_p < 0.8 else "#f87171"
                st.markdown(f"""<style>.stProgress > div > div > div > div {{ background-color: {bar_color} !important; }}</style>""", unsafe_allow_html=True)
                st.progress(min(usage_p, 1.0), text=f"ใช้ไปแล้ว: {usage_p*100:.1f}%")

        with m_col:
            with st.container(border=True):
                st.subheader("🗓️ สรุปรายเดือน")
                st.markdown(f"รวม (บาท): <h2 style='color:#8e44ad; font-family:Itim;'>฿{total_thb:,.2f}</h2>", unsafe_allow_html=True)
                st.markdown(f"รวม (USD): <h3 style='color:#00bcd4; font-family:Itim;'>${total_usd_val:,.2f}</h3>", unsafe_allow_html=True)
                st.write("---")
                avg_day = total_thb / now_th.day
                st.write(f"เฉลี่ยวันละ: **฿{avg_day:,.2f}**")
                st.markdown(f"คาดการณ์สิ้นเดือน: <b style='color:#e91e63;'>฿{avg_day * 31:,.2f}</b>", unsafe_allow_html=True)

        with r_col:
            with st.container(border=True):
                st.subheader("🍰 สัดส่วนค่าย")
                pie_df = pd.DataFrame({"Source": ["GCP", "DO"], "Cost": [gcp_usd, do_usd]})
                fig = px.pie(pie_df, values='Cost', names='Source', hole=0.6,
                             color_discrete_sequence=["#8e44ad", "#00bcd4"])
                fig.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), font=dict(family="Itim"))
                st.plotly_chart(fig, use_container_width=True)

        # --- 6. ประวัติการใช้งาน (แบบ Container ปกติ อ่านง่าย ไม่ทับกันแน่นอน) ---
        st.write("##")
        st.subheader("📄 รายละเอียดประวัติการใช้งาน")
        st.dataframe(df.sort_index(ascending=False), use_container_width=True, height=350)

except Exception as e:
    st.error(f"Error: {e}")
