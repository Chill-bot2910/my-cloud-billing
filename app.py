import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Cloud Billing | Soft & Clean", layout="wide", page_icon="🌸")

# --- 🎨 Soft & Clean CSS (แก้ปัญหาการซ้อนทับอย่างเด็ดขาด) ---
st.markdown("""
<style>
/* ดึงฟอนต์ Itim */
@import url('https://fonts.googleapis.com/css2?family=Itim&display=swap');

/* ใช้ฟอนต์ Itim กับทุกที่ยกเว้น Icon */
html, body, [class*="css"], .stMarkdown, p, div:not([data-testid="stIcon"]), h1, h2, h3, h4, span, label, .stMetricValue {
    font-family: 'Itim', cursive !important;
}

.stApp {
    background-color: #fcfcfd;
}

/* กล่อง Metric - นุ่มนวลขึ้น */
div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #f0f2f6;
    padding: 20px;
    border-radius: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    transition: all 0.5s ease;
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.04);
}

/* ตัวเลข Metric */
div[data-testid="stMetricValue"] > div {
    color: #4A5568 !important;
    font-size: 1.8rem !important;
}

/* หัวข้อ Title ไล่สีพาสเทล */
h1 {
    background: linear-gradient(90deg, #a18cd1, #fbc2eb);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.5rem !important;
    font-weight: 700;
}

/* ปรับแต่ง Progress Bar */
.stProgress > div > div > div > div {
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# --- 2. Header & Timezone (GMT+7) ---
now_th = datetime.utcnow() + timedelta(hours=7)

col_t, col_b = st.columns([4, 1])
with col_t:
    st.title("Cloud Billing Dashboard")
    st.markdown(f"🌸 **สถานะ:** ปกติ  |  🕒 **อัปเดต:** {now_th.strftime('%H:%M:%S')} น.")
with col_b:
    st.write("##")
    if st.button("🔄 Sync Data", use_container_width=True):
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

        # --- 4. Metric Grid ---
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("💰 ยอดรวม", f"฿{total_thb:,.2f}")
        m2.metric("🧠 Gemini", f"${gcp_usd:,.2f}")
        m3.metric("💧 Server", f"${do_usd:,.2f}")
        m4.metric("📊 Tokens", f"{display_tokens:,.0f}")
        m5.metric("💹 Rate", f"{ex_rate:.2f}")

        st.write("##")

        # --- 5. Main Content Area ---
        l_col, m_col, r_col = st.columns([1.8, 0.7, 1])

        with l_col:
            with st.container(border=True):
                st.subheader("📈 แนวโน้มค่าใช้จ่าย")
                chart_df = df.copy().set_index('Date')
                st.area_chart(chart_df['Total Cost (THB)'], color="#a18cd1")
                
                st.divider()
                st.subheader("🏁 งบประมาณ ($15.00)")
                usage_p = (total_usd_val / 15.0)
                bar_color = "#84fab0" if usage_p < 0.5 else "#f6d365" if usage_p < 0.8 else "#fbc2eb"
                st.markdown(f"""<style>.stProgress > div > div > div > div {{ background-color: {bar_color} !important; }}</style>""", unsafe_allow_html=True)
                st.progress(min(usage_p, 1.0), text=f"ใช้ไปแล้ว: {usage_p*100:.1f}%")

        # --- ส่วนที่เพิ่ม: แถบสรุปยอดรวมรายเดือน ---
        with m_col:
            with st.container(border=True):
                st.subheader("🗓️ สรุปรายเดือน")
                st.metric("ยอดสะสม (THB)", f"฿{total_thb:,.2f}")
                st.metric("ยอดสะสม (USD)", f"${total_usd_val:,.2f}")
                st.write("---")
                # คำนวณค่าเฉลี่ยต่อวัน
                day_now = now_th.day
                avg_per_day = total_thb / day_now
                st.write(f"เฉลี่ยวันละ: **฿{avg_per_day:,.2f}**")
                st.write(f"ยอดเดือนนี้ (Proj): **฿{avg_per_day * 31:,.2f}**")

        with r_col:
            with st.container(border=True):
                st.subheader("🍰 สัดส่วนค่าย")
                pie_df = pd.DataFrame({"Source": ["GCP", "DO"], "Cost": [gcp_usd, do_usd]})
                fig = px.pie(pie_df, values='Cost', names='Source', hole=0.6,
                             color_discrete_sequence=["#a18cd1", "#fbc2eb"])
                fig.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), font=dict(family="Itim"))
                st.plotly_chart(fig, use_container_width=True)

            with st.container(border=True):
                st.subheader("🔮 ทำนายยอด")
                projected = (total_thb / now_th.day) * 31
                st.metric("สิ้นเดือนคาดว่า", f"฿{projected:,.2f}", delta=f"฿{projected - total_thb:,.2f}")

        # --- 6. Table (เปลี่ยนจาก Expander เป็น Header ปกติเพื่อแก้ปัญหาข้อความทับกัน) ---
        st.write("##")
        st.subheader("📄 ประวัติการใช้งาน")
        with st.container(border=True):
            st.dataframe(df.sort_index(ascending=False), use_container_width=True, height=300)

except Exception as e:
    st.error(f"Error: {e}")
