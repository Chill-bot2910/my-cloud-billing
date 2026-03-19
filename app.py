import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# 1. ตั้งค่าหน้าเว็บ (บรรทัดแรกสุดเสมอ)
st.set_page_config(page_title="Cloud Billing Dashboard", layout="wide")

# --- วางตรงนี้ครับ ---
col_title, col_btn = st.columns([4, 1])

with col_title:
    st.title("📊 My Cloud Billing Dashboard")

with col_btn:
    st.write("##") # ปรับระยะให้ปุ่มลงมาตรงกับชื่อ Title
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear() 
        st.rerun()
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
        
        # ดึงค่าตัวเลข (ใส่ค่า 0 กันเหนียวถ้าหาคอลัมน์ไม่เจอ)
        total_thb = float(latest.get('Total Cost (THB)', 0))
        ex_rate = float(latest.get('Exchange Rate', 32.72))
        gcp_usd = float(latest.get('gcp_usd', 0))
        do_usd = float(latest.get('do_usd', 5.21))
        
        # จัดการค่า nan สำหรับ Token
        val_tokens = latest.get('Gemini Tokens', 0)
        display_tokens = 0 if pd.isna(val_tokens) else val_tokens

        # 4. แสดงผล Metrics พร้อมสีสัน
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("💰 ยอดรวม (บาท)", f"฿{total_thb:,.2f}")
        
        with col2:
            # ใช้ delta เพื่อแสดงสี (ส้ม/แดง ในทางเทคนิคคือสีแจ้งเตือน แต่เราเน้นให้ต่าง)
            st.metric("🟠 Gemini ($)", f"${gcp_usd:,.2f}", delta="GCP", delta_color="off")
            
        with col3:
            # DigitalOcean ใช้สีฟ้า (Normal)
            st.metric("🔵 DigitalOcean ($)", f"${do_usd:,.2f}", delta="DO", delta_color="normal")
            
        with col4:
            st.metric("📊 Tokens", f"{display_tokens:,.0f}")

        with col5:
            st.metric("💹 Rate", f"{ex_rate:.2f}")

        st.markdown("---")

        # --- 4.5 ส่วนแสดง Progress Bar (แถบพลังงบประมาณ) ---
        st.markdown("### 📊 Budget Usage Status")
        
        # 1. ดึงค่ายอด USD ล่าสุดจาก Dataframe (ป้องกัน Error: not defined)
        total_usd_val = float(latest.get('Total Cost (USD)', 0))
        
        # 2. ตั้งค่า Budget (ให้ตรงกับ n8n ของ Choo คือ 15)
        budget_limit = 15.0  
        usage_percent = (total_usd_val / budget_limit)
        
        # 3. แสดงแถบ Progress และข้อความเตือน
        if usage_percent > 1.0:
            st.error(f"🔴 **OVER BUDGET!** ใช้เงินเกินงบไปแล้ว {usage_percent*100:.1f}%")
            st.progress(1.0) 
        elif usage_percent >= 0.8:
            st.warning(f"🟡 **WARNING:** ใช้ไปแล้ว {usage_percent*100:.1f}% (ใกล้เต็มงบ ${budget_limit})")
            st.progress(min(usage_percent, 1.0))
        else:
            st.info(f"🔵 **SAFE:** ใช้ไปแล้ว {usage_percent*100:.1f}% ของงบ ${budget_limit}")
            st.progress(min(usage_percent, 1.0))

        # 5. กราฟวงกลมแยกสีส้ม-ฟ้า (แบบชัดเจน)
        left_col, right_col = st.columns([2, 1])
        
        with left_col:
            st.subheader("📈 แนวโน้มค่าใช้จ่ายรายวัน (THB)")
            chart_df = df.copy().set_index('Date')
            st.area_chart(chart_df['Total Cost (THB)'])

        with right_col:
            st.subheader("🍰 Expense Distribution")
            pie_df = pd.DataFrame({
                "Source": ["Gemini (GCP)", "DigitalOcean"],
                "Cost": [gcp_usd, do_usd]
            })
            # กำหนดสี Hex Code: ส้ม (#FF9900) และ ฟ้า (#008bcf)
            fig = px.pie(pie_df, values='Cost', names='Source', hole=0.4,
                         color_discrete_map={
                             "Gemini (GCP)": "#FF9900", 
                             "DigitalOcean": "#008bcf"
                         })
            fig.update_traces(textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)

        # 6. Forecast (ทำนายยอดสิ้นเดือน)
        day_of_month = datetime.now().day
        days_in_month = 31
        projected_thb = (total_thb / day_of_month) * days_in_month
        
        st.markdown("---")
        st.success(f"💡 **Forecast:** จากการใช้งานเฉลี่ย คาดว่าสิ้นเดือนนี้ Choo จะมียอดรวมประมาณ **฿{projected_thb:,.2f}** (ประมาณ **${projected_thb / ex_rate:,.2f}**)")

        # 7. ตารางข้อมูลดิบ
        with st.expander("🔍 ดูประวัติการใช้งานทั้งหมด"):
            st.dataframe(df.sort_index(ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"❌ เกิดข้อผิดพลาด: {e}")
