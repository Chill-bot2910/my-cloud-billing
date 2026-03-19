import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# 1. ตั้งค่าหน้าเว็บ (Modern Style: wide + centered title)
st.set_page_config(page_title="Cloud Billing Pro Dashboard", layout="wide", page_icon="📊")

# --- ส่วนหัว Dashboard แบบ Modern ---
with st.container():
    col_title, col_btn = st.columns([4, 1])
    with col_title:
        st.title("📊 My Cloud Billing Pro")
        st.markdown(f"**Last Updated:** `{datetime.now().strftime('%d/%m/%Y %H:%M')}`")
    with col_btn:
        st.write("##")
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    st.markdown("---")

# 2. ดึงข้อมูล (เหมือนเดิม)
sheet_id = "11_nlGeuVRskPtH8K3QZ2BtEOHAon5w7jl2w37GupWtI"
sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

try:
    df = pd.read_csv(sheet_url)
    df.columns = df.columns.str.strip()

    if df.empty:
        st.warning("⚠️ ยังไม่มีข้อมูลในระบบ")
    else:
        # 3. เตรียมข้อมูล
        latest = df.iloc[-1]
        total_thb = float(latest.get('Total Cost (THB)', 0))
        total_usd_val = float(latest.get('Total Cost (USD)', 0))
        ex_rate = float(latest.get('Exchange Rate', 32.72))
        gcp_usd = float(latest.get('gcp_usd', 0))
        do_usd = float(latest.get('do_usd', 5.21))
        val_tokens = latest.get('Gemini Tokens', 0)
        display_tokens = 0 if pd.isna(val_tokens) else val_tokens

        # --- 4. ส่วน KPIs Metrics (จัดกลุ่มใหม่ให้ Pro) ---
        st.subheader("🎯 Key Performance Indicators")
        kpi_col1, kpi_col2, kpi_col3 = st.columns(3)

        with kpi_col1:
            with st.container(border=True):
                st.metric("💰 ยอดรวม (บาท)", f"฿{total_thb:,.2f}", help="รวมค่าใช้จ่ายทุกค่าย")

        with kpi_col2:
            with st.container(border=True):
                col2_1, col2_2 = st.columns(2)
                col2_1.metric("🟠 Gemini ($)", f"${gcp_usd:,.2f}")
                col2_2.metric("🔵 DigitalOcean ($)", f"${do_usd:,.2f}")

        with kpi_col3:
            with st.container(border=True):
                col3_1, col3_2 = st.columns(2)
                col3_1.metric("📊 Tokens", f"{display_tokens:,.0f}")
                col3_2.metric("💹 Rate", f"{ex_rate:.2f}")

        st.markdown("---")

        # --- 5. ส่วน Progress Bar & กราฟ ---
        graph_col1, graph_col2 = st.columns([2, 1])

        with graph_col1:
            with st.container(border=True):
                st.subheader("📊 การใช้งานงบประมาณ ($15)")
                usage_percent = (total_usd_val / 15.0)
                
                # แสดง Progress Bar สีตามสถานะ
                if usage_percent > 1.0:
                    st.progress(1.0, text=f"🔴 เกินงบ! ({usage_percent*100:.1f}%)")
                elif usage_percent >= 0.8:
                    st.progress(usage_percent, text=f"🟡 ใกล้เต็ม! ({usage_percent*100:.1f}%)")
                else:
                    st.progress(usage_percent, text=f"🔵 ปกติ ({usage_percent*100:.1f}%)")

                st.write("##") # เว้นระยะ
                st.subheader("📈 แนวโน้มค่าใช้จ่ายรายวัน (THB)")
                chart_df = df.copy().set_index('Date')
                # ใช้กราฟพื้นที่สีฟ้าอ่อนให้ดูสบายตา
                st.area_chart(chart_df['Total Cost (THB)'], color="#008bcf")

        with graph_col2:
            with st.container(border=True):
                st.subheader("🍰 Expense Distribution")
                pie_df = pd.DataFrame({
                    "Source": ["Gemini (GCP)", "DigitalOcean"],
                    "Cost": [gcp_usd, do_usd]
                })
                fig = px.pie(pie_df, values='Cost', names='Source', hole=0.5,
                             color_discrete_map={
                                 "Gemini (GCP)": "#FF9900", 
                                 "DigitalOcean": "#008bcf"
                             })
                fig.update_traces(textinfo='percent+label', textposition='outside')
                # ปรับแต่ง Legend ให้ดู Modern
                fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
                st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # --- 6. ส่วน Forecast & ข้อมูลดิบ ---
        lower_col1, lower_col2 = st.columns([1, 1])

        with lower_col1:
            with st.container(border=True):
                st.subheader("💡 Choo's Pro Forecast")
                day_of_month = datetime.now().day
                projected_thb = (total_thb / day_of_month) * 31
                
                # แสดงข้อความทำนายแบบ Modern
                col_f1, col_f2 = st.columns(2)
                col_f1.metric("🔮 พยากรณ์สิ้นเดือน (บาท)", f"฿{projected_thb:,.2f}")
                col_f2.metric("🔮 พยากรณ์สิ้นเดือน ($)", f"${projected_thb / ex_rate:,.2f}")
                st.info(f"📅 เหลืออีก **{31 - day_of_month} วัน** จะหมดเดือนนี้")

        with lower_col2:
            with st.container(border=True):
                st.subheader("🔍 ประวัติการใช้งาน")
                st.dataframe(df.sort_index(ascending=False), use_container_width=True, height=200)

except Exception as e:
    st.error(f"❌ เกิดข้อผิดพลาด: {e}")
