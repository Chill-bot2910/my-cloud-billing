import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Cloud Billing Dashboard", layout="wide")
st.title("📊 My Cloud Billing Dashboard")
st.markdown(f"_Last Updated: {datetime.now().strftime('%d/%m/%Y %H:%M')}_")
st.markdown("---")

# 2. ดึงข้อมูลจาก Google Sheets
sheet_id = "11_nlGeuVRskPtH8K3QZ2BtEOHAon5w7jl2w37GupWtI"
sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

try:
    df = pd.read_csv(sheet_url)
    df.columns = df.columns.str.strip()

    if df.empty:
        st.warning("⚠️ ยังไม่มีข้อมูลในระบบ")
    else:
        # 3. เตรียมข้อมูลแถวล่าสุด (ต้องอยู่ในบล็อก else นี้ทั้งหมด)
        latest = df.iloc[-1]
        
        # ดึงค่าตัวเลขต่างๆ (ใส่ค่า 0 กันเหนียวไว้ถ้าหาคอลัมน์ไม่เจอ)
        total_thb = float(latest.get('Total Cost (THB)', 0))
        total_usd = float(latest.get('Total Cost (USD)', 0))
        # ดึงยอดแยกของแต่ละค่าย (ถ้าคุณส่งมาจาก n8n แล้ว)
        gcp_usd = float(latest.get('gcp_usd', 0)) 
        do_usd = float(latest.get('do_usd', 5.21)) # 5.21 คือค่าคงที่ถ้ายังไม่ได้ส่งจาก n8n
        
        ex_rate = float(latest.get('Exchange Rate', 35.0))
        status = latest.get('Status', 'N/A')

        # 4. แสดงผล 4 กล่องไฮไลท์ (Metrics)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💰 ยอดรวม (บาท)", f"฿{total_thb:,.2f}")
        with col2:
            st.metric("🤖 Gemini Cost", f"${gcp_usd:,.2f}")
        with col3:
            if 'Gemini Tokens' in df.columns:
                tokens = latest['Gemini Tokens']
                st.metric("📊 Token Usage", f"{tokens:,.0f}", delta="Tokens")
            else:
                st.metric("📊 Token Usage", "N/A")
        with col4:
            st.metric("💹 Rate", f"{ex_rate:.2f}")

        st.markdown("---")

        # 5. กราฟวงกลมและแนวโน้ม
        left_col, right_col = st.columns([2, 1])

        with left_col:
            st.subheader("📈 แนวโน้มค่าใช้จ่ายรายวัน (THB)")
            if 'Date' in df.columns:
                chart_data = df.copy()
                chart_data = chart_data.set_index('Date')
                st.area_chart(chart_data['Total Cost (THB)'])

        with right_col:
            st.subheader("🍰 Expense Distribution")
            pie_df = pd.DataFrame({
                "Source": ["Gemini API", "DigitalOcean"],
                "Cost": [gcp_usd, do_usd]
            })
            fig = px.pie(pie_df, values='Cost', names='Source', hole=0.4,
                         color_discrete_sequence=['#4285F4', '#008bcf'])
            st.plotly_chart(fig, use_container_width=True)

        # 6. ตารางข้อมูลดิบ
        with st.expander("🔍 ดูประวัติการใช้งานทั้งหมด"):
            st.dataframe(df.sort_index(ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"❌ เกิดข้อผิดพลาด: {e}")
