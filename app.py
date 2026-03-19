import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Cloud Billing Dashboard", layout="wide")
st.title("📊 My Cloud Billing Dashboard")
st.markdown(f"_Last Updated: {datetime.now().strftime('%d/%m/%Y %H:%M')}_")
st.markdown("---")

# 2. ดึงข้อมูล
sheet_id = "11_nlGeuVRskPtH8K3QZ2BtEOHAon5w7jl2w37GupWtI"
sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

try:
    df = pd.read_csv(sheet_url)
    df.columns = df.columns.str.strip()

    if not df.empty:
        latest = df.iloc[-1]
        
        # ดึงค่าตัวเลข (ถ้าไม่มีให้เป็น 0)
        total_thb = float(latest.get('Total Cost (THB)', 0))
        ex_rate = float(latest.get('Exchange Rate', 32.72))
        gcp_usd = float(latest.get('gcp_usd', 0))
        do_usd = float(latest.get('do_usd', 5.21))
        tokens = latest.get('Gemini Tokens', 0)

        # --- 3. ส่วนทำนายยอดสิ้นเดือน (Forecast) ---
        day_of_month = datetime.now().day
        days_in_month = 31 # ประมาณการ
        projected_usd = (total_thb / day_of_month) * days_in_month / ex_rate

        # --- 4. แสดง Metrics ---
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💰 ยอดรวม (บาท)", f"฿{total_thb:,.2f}")
        col2.metric("🤖 Gemini Cost", f"${gcp_usd:,.2f}")
        col3.metric("📊 Token Usage", f"{tokens:,.0f}" if not pd.isna(tokens) else "0")
        col4.metric("💹 Rate (THB/USD)", f"{ex_rate:.2f}")

        st.markdown("---")

        # --- 5. กราฟวงกลมแยกค่าย ---
        left_col, right_col = st.columns([2, 1])
        
        with left_col:
            st.subheader("📈 แนวโน้มค่าใช้จ่ายรายวัน (THB)")
            chart_df = df.copy().set_index('Date')
            st.area_chart(chart_df['Total Cost (THB)'])

        with right_col:
            st.subheader("🍰 Expense Distribution")
            pie_df = pd.DataFrame({
                "Source": ["Google (Gemini)", "DigitalOcean"],
                "Cost": [gcp_usd, do_usd]
            })
            fig = px.pie(pie_df, values='Cost', names='Source', hole=0.4, 
                         color_discrete_sequence=['#4285F4', '#008bcf'])
            st.plotly_chart(fig, use_container_width=True)

        # --- 6. Forecast Section ---
        st.success(f"💡 **Forecast:** สิ้นเดือนนี้คาดว่าคุณจะมียอดรวมประมาณ **${ Davison_usd:,.2f}** (ประมาณ **฿{projected_usd * ex_rate:,.2f}**)")

except Exception as e:
    st.error(f"❌ Error: {e}")
