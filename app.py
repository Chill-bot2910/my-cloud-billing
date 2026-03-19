import streamlit as st
import pandas as pd
from datetime import datetime

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Cloud Billing Dashboard", layout="wide")
st.title("📊 My Cloud Billing Dashboard")
st.markdown("---")

# 2. ลิงก์ Google Sheet
sheet_id = "11_nlGeuVRskPtH8K3QZ2BtEOHAon5w7jl2w37GupWtI"
sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

try:
    df = pd.read_csv(sheet_url)
    df.columns = df.columns.str.strip()

    if df.empty:
        st.warning("⚠️ ยังไม่มีข้อมูลใน Sheet ครับ")
    else:
        # 3. เตรียมข้อมูล
        latest = df.iloc[-1]
        total_thb = float(latest['Total Cost (THB)'])
        total_usd = float(latest['Total Cost (USD)'])
        status = latest['Status']
        
        # --- [Logic: พยากรณ์ยอดสิ้นเดือน] ---
        now = datetime.now()
        day_now = now.day  # วันนี้วันที่เท่าไหร่
        days_in_month = 31 # เดือนมีนาคมมี 31 วัน
        
        # คำนวณค่าเฉลี่ยต่อวันแล้วคูณจำนวนวันทั้งเดือน
        projected_thb = (total_thb / day_now) * days_in_month
        budget_limit = 1000  # สมมติงบไว้ที่ 1000 บาท (แก้เลขนี้ได้ตามใจชอบครับ)
        # ----------------------------------

        # 4. แสดงผล Metric (เพิ่มเป็น 4 คอลัมน์)
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("💰 ยอดสะสม (บาท)", f"฿{total_thb:,.2f}", delta="ยอดใช้จริง")
        
        with col2:
            st.metric("💵 ยอดสะสม (USD)", f"${total_usd:,.2f}")
            
        with col3:
            # กล่องพยากรณ์ (Forecast)
            diff = projected_thb - budget_limit
            st.metric(
                "🔮 คาดการณ์สิ้นเดือน", 
                f"฿{projected_thb:,.0f}", 
                delta=f"{diff:,.0f} จากงบ ฿{budget_limit}",
                delta_color="inverse" if projected_thb > budget_limit else "normal"
            )

        with col4:
            if "ปกติ" in status:
                st.metric("🖥️ สถานะ", "✅ OK", delta=status)
            else:
                st.metric("🖥️ สถานะ", "⚠️ ALERT", delta=status, delta_color="inverse")

        st.markdown("---")

        # 5. กราฟและตาราง
        tab1, tab2 = st.tabs(["📈 เทรนด์ค่าใช้จ่าย", "🔍 ข้อมูลดิบ"])
        with tab1:
            if 'Date' in df.columns:
                st.area_chart(df.set_index('Date')['Total Cost (THB)'])
        with tab2:
            st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"❌ Error: {e}")
