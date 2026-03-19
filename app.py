# --- 🎨 Cute Itim Custom CSS ---
st.markdown("""
<style>
/* ดึงฟอนต์ Itim จาก Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Itim&display=swap');

/* บังคับใช้ฟอนต์ Itim กับทุกองค์ประกอบของ Streamlit */
html, body, [class*="css"], .stMarkdown, p, div, h1, h2, h3, h4, span, label {
    font-family: 'Itim', cursive !important;
}

/* พื้นหลังนุ่มนวล */
.stApp {
    background-color: #fcfcfd;
}

/* กล่อง Metric ปรับให้มนและมีเงาละมุนขึ้น */
div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #f0f2f6;
    padding: 22px;
    border-radius: 25px; /* มนกว่าเดิม */
    box-shadow: 0 10px 20px rgba(0,0,0,0.03);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

/* เอฟเฟกต์ลอยตัวแบบเด้งนุ่มๆ */
div[data-testid="stMetric"]:hover {
    transform: translateY(-10px) scale(1.03);
    box-shadow: 0 15px 30px rgba(161, 140, 209, 0.15);
    border-color: #fbc2eb;
}

/* ตัวเลข Metric */
div[data-testid="stMetricValue"] > div {
    color: #5a67d8 !important; /* สีน้ำเงินอมม่วงพาสเทล */
    font-size: 2.2rem !important;
}

/* หัวข้อ Title */
h1 {
    background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 3rem !important;
    padding-bottom: 10px;
}

/* ปรับแต่ง Progress Bar ให้เข้ากับธีม */
.stProgress > div > div > div > div {
    background-image: linear-gradient(to right, #a18cd1, #fbc2eb);
    border-radius: 20px;
}
</style>
""", unsafe_allow_html=True)
