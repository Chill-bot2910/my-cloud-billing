import streamlit as st
import pandas as pd
from datetime import datetime

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
        # 3. เตรียมข้อมูลแถวล่าสุด
        latest = df.iloc[-1]
        total_thb = float(latest['Total Cost (THB)'])
        total_usd = float(latest['Total Cost (USD)'])
        status = latest['Status']
        
        # ดึงค่าเรทเงินบาท (ถ้ามีใน Sheet)
        ex_rate = float(latest['Exchange Rate']) if 'Exchange Rate' in df.columns else 35.0

        # 4. แสดงผล 4 กล่องไฮไลท์ (Metrics)
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("💰 ยอดรวม (บาท)", f"฿{total_thb:,.2f}")
        
        with col2:
            st.metric("💵 ยอดรวม (USD)", f"${total_usd:,.2f}")
            
        with col3:
            # แสดงเรทเงินบาทที่ดึงมาจาก n8n
            st.metric("💹 เรทเงินบาท", f"{ex_rate:.2f} THB", delta="Real-time API")

        with col4:
            if "ปกติ" in status:
                st.metric("🖥️ สถานะระบบ", "✅ ปกติ", delta_color="normal")
            else:
                st.metric("🖥️ สถานะระบบ", "⚠️ แจ้งเตือน", delta=status, delta_color="inverse")

        st.markdown("---")

        # 5. กราฟและรายละเอียด
        left_col, right_col = st.columns([2, 1])

        with left_col:
            st.subheader("📈 แนวโน้มค่าใช้จ่ายรายวัน (THB)")
            if 'Date' in df.columns:
                # ทำกราฟ Area Chart
                chart_data = df.copy()
                chart_data = chart_data.set_index('Date')
                st.area_chart(chart_data['Total Cost (THB)'])

        with right_col:
            st.subheader("📋 ข้อมูลล่าสุด")
            st.write(f"**วันที่:** {latest['Date']}")
            st.write(f"**บริการ:** {latest['Service Name']}")
            st.info("ระบบจะอัปเดตข้อมูลทุก 12 ชั่วโมงตามรอบของ n8n")

        # 6. ตารางข้อมูลดิบ
        with st.expander("🔍 ดูประวัติการใช้งานทั้งหมด"):
            st.dataframe(df.sort_index(ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"❌ เกิดข้อผิดพลาดในการโหลดข้อมูล: {e}")
