import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Cloud Billing | Soft Itim", layout="wide", page_icon="🌸")

# --- 🎨 Smooth Minimal Itim CSS ---
st.markdown("""
<style>
/* ดึงฟอนต์ Itim */
@import url('https://fonts.googleapis.com/css2?family=Itim&display=swap');

/* บังคับใช้ฟอนต์ Itim ทุกจุด */
html, body, [class*="css"], .stMarkdown, p, div, h1, h2, h3, h4, span, label, .stMetricValue {
    font-family: 'Itim', cursive !important;
}

.stApp {
    background-color: #fcfcfd;
}

/* กล่อง Metric - ปรับเงาให้นวลและ Hover เบาๆ */
div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #f0f2f6;
    padding: 20px;
    border-radius: 20px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.02);
    transition: all 0.4s ease; /* ปรับให้สมูทขึ้น */
}

/* Hover แบบเบาๆ ไม่กระโชกโฮกฮาก */
div[data-testid="stMetric"]:hover {
    transform: translateY(-3px); /* ลอยขึ้นแค่นิดเดียว */
    box-shadow: 0 8px 15px rgba(161, 140, 209, 0.1);
    border-color: #fbc2eb;
}

/* ตัวเลข Metric */
div[data-testid="stMetricValue"] > div {
    color: #5a67d8 !important;
    font-size: 1.8rem !important;
}

/* หัวข้อ Title */
h1 {
    background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.5rem !important;
}

/* แก้บั๊กตัวหนังสือทับกันใน Expander */
.stExpander {
    border: none !important;
    box-shadow: none !important;
    background-color: transparent !important;
}

/* ปรับแต่งปุ่ม Sync ให้ดูเรียบง่าย */
.stButton>button {
    border-radius: 10px;
    border: 1px solid #e2e8f0;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)

# --- 2. Header & Timezone (GMT+7) ---
now_th = datetime.utcnow() + timedelta(hours=7)

col_t, col_b = st.columns([4, 1])
with col_t:
    st.title("Cloud Billing Dashboard")
    st.markdown(f"🌸 **สถานะระบบ:** ทำงานปกติ  |  🕒 **อัปเดต:** {now_th.strftime('%H:%M:%S')} น.")
with col_b:
    st.write("##")
    if st.button("🔄 ดึงข้อมูลใหม่", use_container_width=True):
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
        m1.metric("💰 ยอดรวมทั้งหมด", f"฿{total_thb:,.2f}")
        m2.metric("🧠 Gemini (GCP)", f"${gcp_usd:,.2f}")
        m3.metric("💧 DigitalOcean", f"${do_usd:,.2f}")
        m4.metric("📊 ใช้โทเคน", f"{display_tokens:,.0f}")
        m5.metric("💹 เรทเงินบาท", f"{ex_rate:.2f}")

        st.write("##")

        # --- 5. Main Area ---
        l_col, r_col = st.columns([2, 1])

        with l_col:
            with st.container(border=True):
                st.subheader("📈 แนวโน้มการใช้งาน")
                chart_df = df.copy().set_index('Date')
                st.area_chart(chart_df['Total Cost (THB)'], color="#fbc2eb")
                
                st.divider()
                st.subheader("🏁 เป้าหมายงบประมาณ ($15.00)")
                usage_p = (total_usd_val / 15.0)
                
                # --- Dynamic Progress Bar Color Logic ---
                # เปลี่ยนสีตาม % การใช้งาน
                if usage_p < 0.5:
                    bar_color = "#84fab0" # เขียวพาสเทล
                elif usage_p < 0.8:
                    bar_color = "#f6d365" # เหลืองพาสเทล
                else:
                    bar_color = "#fbc2eb" # ชมพูพาสเทล (Alert)
                
                st.markdown(f"""
                    <style>
                        .stProgress > div > div > div > div {{
                            background-color: {bar_color} !important;
                        }}
                    </style>""", unsafe_allow_html=True)
                
                st.progress(min(usage_p, 1.0), text=f"ใช้วงเงินไปแล้ว: {usage_p*100:.1f}%")

        with r_col:
            with st.container(border=True):
                st.subheader("🍰 สัดส่วนค่ายใช้จ่าย")
                pie_df = pd.DataFrame({"ค่าย": ["GCP", "DO"], "ค่า": [gcp_usd, do_usd]})
                fig = px.pie(pie_df, values='ค่า', names='ค่าย', hole=0.6,
                             color_discrete_sequence=["#a18cd1", "#fbc2eb"])
                fig.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), font=dict(family="Itim"))
                st.plotly_chart(fig, use_container_width=True)

            with st.container(border=True):
                st.subheader("🔮 ทำนายสิ้นเดือน")
                day = now_th.day
                projected = (total_thb / day) * 31
                st.metric("คาดการณ์รวม", f"฿{projected:,.2f}", delta=f"฿{projected - total_thb:,.2f}")

        # --- 6. Table (Fix text overlapping) ---
        st.write("##")
        with st.expander("📄 ดูประวัติย้อนหลัง"):
            st.dataframe(df.sort_index(ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")
