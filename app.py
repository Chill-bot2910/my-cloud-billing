import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Cloud Billing | Vibrant 6", layout="wide", page_icon="🌸")

# --- 🎨 Vibrant Itim Custom CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Itim&display=swap');

/* ใช้ฟอนต์ Itim ทุกจุด ยกเว้น Icon */
html, body, [class*="css"], .stMarkdown, p, div:not([data-testid="stIcon"]), h1, h2, h3, h4, span, label, .stMetricValue {
    font-family: 'Itim', cursive !important;
}

.stApp {
    background-color: #fcfcfd;
}

/* กล่อง Metric - ปรับแต่งสีตัวเลขแยกตามคอลัมน์ (1-6) */
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

/* --- 🌈 กำหนดสีตัวเลขแยก 6 กล่อง --- */
div[data-testid="column"]:nth-child(1) div[data-testid="stMetricValue"] > div { color: #8e44ad !important; } /* ม่วง: ยอดรวม */
div[data-testid="column"]:nth-child(2) div[data-testid="stMetricValue"] > div { color: #e91e63 !important; } /* ชมพู: Gemini */
div[data-testid="column"]:nth-child(3) div[data-testid="stMetricValue"] > div { color: #00bcd4 !important; } /* ฟ้า: Server */
div[data-testid="column"]:nth-child(4) div[data-testid="stMetricValue"] > div { color: #27ae60 !important; } /* เขียว: Tokens */
div[data-testid="column"]:nth-child(5) div[data-testid="stMetricValue"] > div { color: #f39c12 !important; } /* ส้ม: Rate */
div[data-testid="column"]:nth-child(6) div[data-testid="stMetricValue"] > div { color: #ff5722 !important; } /* แดงส้ม: คาดการณ์ */

div[data-testid="stMetricValue"] > div {
    font-size: 1.8rem !important;
    font-weight: 700 !important;
}

/* หัวข้อ Title */
h1 {
    background: linear-gradient(90deg, #6a11cb, #fbc2eb);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.8rem !important;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# --- 2. Header & Timezone ---
now_th = datetime.utcnow() + timedelta(hours=7)

col_t, col_b = st.columns([4, 1])
with col_t:
    st.title("Cloud Billing Center")
    st.markdown(f"🌸 **สถานะ:** ปกติ  |  🕒 **อัปเดต:** {now_th.strftime('%H:%M:%S')} น.")
with col_b:
    st.write("##")
    if st.button("🔄 Sync ข้อมูล", use_container_width=True):
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
        
        # คำนวณคาดการณ์
        day_now = now_th.day
        projected = (total_thb / day_now) * 31

        # --- 4. Metric Grid (6 กล่อง 6 สี) ---
        m1, m2, m3, m4, m5, m6 = st.columns(6)
        m1.metric("💰 ยอดรวม (บาท)", f"฿{total_thb:,.2f}")
        m2.metric("🧠 Gemini ($)", f"${gcp_usd:,.2f}")
        m3.metric("💧 Server ($)", f"${do_usd:,.2f}")
        m4.metric("📊 Tokens", f"{display_tokens:,.0f}")
        m5.metric("💹 EX Rate", f"{ex_rate:.2f}")
        m6.metric("🔮 คาดการณ์สิ้นเดือน", f"฿{projected:,.2f}")

        st.write("##")

        # --- 5. Main Area ---
        l_col, r_col = st.columns([2, 1])

        with l_col:
            with st.container(border=True):
                st.subheader("📈 แนวโน้มค่าใช้จ่าย")
                chart_df = df.copy().set_index('Date')
                st.area_chart(chart_df['Total Cost (THB)'], color="#a18cd1")
                
                st.divider()
                st.subheader("🏁 งบประมาณ ($15.00)")
                usage_p = (total_usd_val / 15.0)
                bar_color = "#4ade80" if usage_p < 0.5 else "#facc15" if usage_p < 0.8 else "#fbc2eb"
                st.markdown(f"""<style>.stProgress > div > div > div > div {{ background-color: {bar_color} !important; }}</style>""", unsafe_allow_html=True)
                st.progress(min(usage_p, 1.0), text=f"ใช้วงเงินไปแล้ว: {usage_p*100:.1f}%")

        with r_col:
            with st.container(border=True):
                st.subheader("🍰 สัดส่วนค่าใช้จ่าย")
                pie_df = pd.DataFrame({"Source": ["GCP", "DO"], "Cost": [gcp_usd, do_usd]})
                fig = px.pie(pie_df, values='Cost', names='Source', hole=0.6,
                             color_discrete_sequence=["#8e44ad", "#00bcd4"])
                fig.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), font=dict(family="Itim"))
                st.plotly_chart(fig, use_container_width=True)
            
            # ย้ายสรุปรายวันมาไว้ในกล่องเล็กข้างล่าง
            with st.container(border=True):
                st.subheader("🗓️ สรุปวันนี้")
                avg_day = total_thb / day_now
                st.write(f"เฉลี่ยวันละ: **฿{avg_day:,.2f}**")
                st.write(f"เหลืออีก: **{31 - day_now} วัน**")

        # --- 6. Table (ลบ Expander ออกถาวร แก้บั๊กตัวหนังสือซ้อน) ---
        st.write("##")
        st.subheader("📄 รายละเอียดประวัติการใช้งาน")
        st.dataframe(df.sort_index(ascending=False), use_container_width=True, height=350)

except Exception as e:
    st.error(f"Error: {e}")
