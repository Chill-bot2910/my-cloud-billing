import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Cloud Billing | Dashboard", layout="wide", page_icon="🌸")

# --- 🎨 Smooth Pastel Custom CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Itim&display=swap');
html, body, [class*="css"], .stMarkdown, p, div:not([data-testid="stIcon"]), h1, h2, h3, h4, span, label, .stMetricValue {
    font-family: 'Itim', cursive !important;
}
.stApp { background-color: #fcfcfd; }
div[data-testid="stMetric"] {
    background: white; border: 1px solid #f0f2f6; padding: 20px; border-radius: 20px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.03); transition: all 0.4s ease;
}
div[data-testid="stMetric"]:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(0,0,0,0.06); }
div[data-testid="column"]:nth-child(1) div[data-testid="stMetricValue"] > div { color: #7c4dff !important; } /* ยอดรวม */
div[data-testid="column"]:nth-child(2) div[data-testid="stMetricValue"] > div { color: #f06292 !important; } /* Gemini */
div[data-testid="column"]:nth-child(3) div[data-testid="stMetricValue"] > div { color: #00acc1 !important; } /* DO */
div[data-testid="column"]:nth-child(4) div[data-testid="stMetricValue"] > div { color: #43a047 !important; } /* Tokens */
div[data-testid="column"]:nth-child(5) div[data-testid="stMetricValue"] > div { color: #fb8c00 !important; } /* Exchange */

div[data-testid="stMetricValue"] > div { font-size: 2rem !important; font-weight: 700 !important; }
h1 { background: linear-gradient(90deg, #6a11cb, #fbc2eb); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.8rem !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. Header & Timezone ---
now_th = datetime.utcnow() + timedelta(hours=7)
col_t, col_b = st.columns([4, 1])
with col_t:
    st.title("ระบบติดตามค่าใช้จ่าย Cloud")
    st.markdown(f"🌸 **สถานะ:** เชื่อมต่อข้อมูลสำเร็จ | 🕒 **อัปเดตล่าสุด:** {now_th.strftime('%H:%M:%S')} น.")
with col_b:
    st.write("##")
    if st.button("🔄 อัปเดตข้อมูล", use_container_width=True):
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
        # ดึงแถวล่าสุดที่ n8n เพิ่งบันทึกเข้าไป
        latest = df.iloc[-1]
        
        # ดึงค่าตามชื่อคอลัมน์ใน Sheet
        total_thb = float(latest.get('Total Cost (THB)', 0))
        total_usd_val = float(latest.get('Total Cost (USD)', 0))
        gcp_usd = float(latest.get('gcp_usd', 0))
        do_usd = float(latest.get('do_usd', 0))
        # สำหรับ Gemini USD ถ้าใน n8n ยังไม่ได้แยกคอลัมน์ เราจะใช้ค่า gcp_usd ไปก่อน
        # หรือถ้า n8n บันทึกแยกมาแล้ว ให้เปลี่ยนชื่อตรงนี้ครับ
        gemini_usd = float(latest.get('gemini_usd', gcp_usd)) 
        display_tokens = float(latest.get('Gemini Tokens', 0))
        ex_rate = float(latest.get('Exchange Rate', 35.0))

        # --- 4. Metric Grid (5 กล่อง) ---
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("💰 ยอดรวมทั้งหมด (บาท)", f"฿{total_thb:,.2f}")
        m2.metric("🧠 ค่าใช้จ่าย Gemini (USD)", f"${gemini_usd:,.2f}")
        m3.metric("💧 ค่าใช้จ่ายเซิร์ฟเวอร์ (USD)", f"${do_usd:,.2f}")
        m4.metric("📊 จำนวนโทเคนที่ใช้งาน", f"{display_tokens:,.0f}")
        m5.metric("💹 อัตราแลกเปลี่ยนปัจจุบัน", f"{ex_rate:.2f}")

        st.write("##")

        # --- 5. Main Content Area ---
        l_col, m_col, r_col = st.columns([1.6, 1.0, 1.0])
        
        with l_col:
            with st.container(border=True):
                st.subheader("📈 แนวโน้มค่าใช้จ่ายรายวัน")
                # ใช้คอลัมน์ Date เป็นแกน X
                if 'Date' in df.columns:
                    chart_df = df.copy()
                    st.area_chart(chart_df.set_index('Date')['Total Cost (THB)'], color="#7c4dff")
                
                st.divider()
                st.subheader("🏁 สถานะงบประมาณ ($15.00)")
                usage_p = (total_usd_val / 15.0)
                bar_color = "#4ade80" if usage_p < 0.5 else "#facc15" if usage_p < 0.8 else "#f87171"
                st.markdown(f"<style>.stProgress > div > div > div > div {{ background-color: {bar_color} !important; }}</style>", unsafe_allow_html=True)
                st.progress(min(usage_p, 1.0), text=f"ใช้วงเงินไปแล้ว: {usage_p*100:.1f}%")

        with m_col:
            with st.container(border=True):
                st.subheader("🗓️ สรุปภาพรวมเดือนนี้")
                st.markdown(f"**ยอดรวมสะสม:** <h2 style='color:#7c4dff; font-family:Itim;'>฿{total_thb:,.2f}</h2>", unsafe_allow_html=True)
                st.markdown(f"**คิดเป็นเงินดอลลาร์:** <h3 style='color:#00acc1; font-family:Itim;'>${total_usd_val:,.2f}</h3>", unsafe_allow_html=True)
                st.write("---")
                day_now = now_th.day
                avg_per_day = total_thb / day_now if day_now > 0 else 0
                st.write(f"🔹 ค่าใช้จ่ายเฉลี่ยต่อวัน: **฿{avg_per_day:,.2f}**")
                st.markdown(f"**ประมาณการยอดสิ้นเดือน:** <h3 style='color:#f06292; font-family:Itim;'>฿{avg_per_day * 30:,.2f}</h3>", unsafe_allow_html=True)

        with r_col:
            with st.container(border=True):
                st.subheader("🍰 สัดส่วนค่าใช้จ่าย")
                pie_df = pd.DataFrame({"Source": ["GCP/Gemini", "DigitalOcean"], "Cost": [gcp_usd, do_usd]})
                fig = px.pie(pie_df, values='Cost', names='Source', hole=0.6, color_discrete_sequence=["#7c4dff", "#f06292"])
                fig.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20), font=dict(family="Itim"))
                st.plotly_chart(fig, use_container_width=True)

        # --- 6. Table ประวัติ ---
        st.write("##")
        st.subheader("📄 ประวัติการบันทึกข้อมูลย้อนหลัง")
        st.dataframe(df.sort_index(ascending=False), use_container_width=True, height=350)

except Exception as e:
    st.error(f"อุ๊ย! เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")
