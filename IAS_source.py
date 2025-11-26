import streamlit as st
import pandas as pd
import numpy as np
import datetime
import altair as alt

# ==========================================
# 1. CẤU HÌNH & CSS
# ==========================================
st.set_page_config(layout="wide", page_title="Hệ thống IAS")

st.markdown("""
<style>
/* Cấu trúc trang */
div.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
    padding-left: 3rem;
    padding-right: 3rem;
}

/* Selectbox Styling */
.stSelectbox label {
    font-weight: bold;
    color: #4CAF50;
    font-size: 1.1rem !important; 
}
div[data-testid="stSelectbox"] div[role="combobox"] {
    border: 1px solid #fafafa;
    border-radius: 0.5rem;
}
div[data-testid="stSelectbox"] div[role="combobox"]:hover {
    border-color: #4CAF50 !important; 
    cursor: pointer;
}
div[data-testid="stSelectbox"] div[role="combobox"]:focus-within {
    border-color: #4CAF50 !important;
    box-shadow: 0 0 0 0.2rem rgba(76, 175, 80, 0.25) !important;
}
div[data-testid="stSelectbox"] svg { fill: #fafafa !important; }

/* DataFrame Styling */
.stDataFrame { border: 1px solid #fafafa; }
.stButton button { border: 1px solid #4CAF50; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. KHỞI TẠO CƠ SỞ DỮ LIỆU GIẢ LẬP (SESSION STATE)
# ==========================================

def init_db():
    # 1. Bảng Học sinh
    if 'df_students' not in st.session_state:
        data_hs = {
            'MaHS': ['HS001', 'HS002', 'HS003', 'HS004', 'HS005'],
            'Họ và tên': ['Nguyễn Văn A', 'Trần Thị B', 'Lê Văn C', 'Phạm Thị D', 'Hoàng Văn E'],
            'Ngày sinh': ['2008-01-15', '2008-05-20', '2008-11-02', '2008-03-10', '2008-08-18'],
            'Lớp': ['11A1', '11A1', '11A2', '11A2', '11A3'],
            'Điểm Tích cực': [15, 10, 8, 20, 5],
            'Điểm Vi phạm': [5, 20, 8, 2, 10],
            'Điểm Hạnh kiểm': [100, 80, 90, 108, 85] # 90 + 15 - 5 = 100
        }
        st.session_state['df_students'] = pd.DataFrame(data_hs)

    # 2. Bảng Vi Phạm (Danh mục)
    if 'df_violations' not in st.session_state:
        data_vp = {
            'MaVP': ['VP01', 'VP02', 'VP03'],
            'Tên Vi phạm': ['Đi học muộn', 'Không làm bài tập', 'Mất trật tự'],
            'Điểm trừ': [2, 5, 3]
        }
        st.session_state['df_violations'] = pd.DataFrame(data_vp)

    # 3. Bảng Tích cực (Danh mục)
    if 'df_achievements' not in st.session_state:
        data_tc = {
            'MaTC': ['TC01', 'TC02', 'TC03'],
            'Tên Tích cực': ['Phát biểu xây dựng bài', 'Đạt điểm 10', 'Giúp đỡ bạn bè'],
            'Điểm cộng': [2, 5, 3]
        }
        st.session_state['df_achievements'] = pd.DataFrame(data_tc)

    # 4. Bảng Nhật ký Hành vi (Liên kết)
    if 'df_logs' not in st.session_state:
        # Tạo dữ liệu mẫu cho tuần hiện tại
        today = datetime.date.today()
        data_logs = {
            'Ngày': [today, today, today - datetime.timedelta(days=1)],
            'MaHS': ['HS001', 'HS002', 'HS001'],
            'Loại': ['Tích cực', 'Vi phạm', 'Tích cực'], # Helper col
            'Mã Hành vi': ['TC01', 'VP01', 'TC02'], # MaVP hoặc MaTC
            'Ghi chú': ['Rất hăng hái', 'Vào lớp trễ 5p', 'Bài kiểm tra tốt']
        }
        st.session_state['df_logs'] = pd.DataFrame(data_logs)
        # Đảm bảo cột Ngày là kiểu datetime
        st.session_state['df_logs']['Ngày'] = pd.to_datetime(st.session_state['df_logs']['Ngày']).dt.date

init_db()

# Biến điều hướng trang
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'dashboard' # Mặc định vào dashboard
if 'selected_student_id' not in st.session_state:
    st.session_state['selected_student_id'] = None

# ==========================================
# 3. LOGIC TRANG 1: QUẢN LÝ DỮ LIỆU (DATA TABLE)
# ==========================================

def render_data_management_page():
    st.title("📂 BẢNG DỮ LIỆU HỆ THỐNG")
    
    # Chia layout: Bên trái chọn bảng/tuần, Bên phải hiển thị dữ liệu
    col_ctrl, col_data = st.columns([1, 4])
    
    with col_ctrl:
        st.subheader("Cấu hình")
        # Chọn bảng để xem
        table_option = st.radio(
            "Chọn Bảng Dữ liệu:",
            ["👨‍🎓 Học sinh", "📝 Nhật ký Hành vi", "⚠️ Danh mục Vi phạm", "🏆 Danh mục Tích cực"]
        )
        
        st.markdown("---")
        
        # Nếu đang xem Nhật ký, hiện bộ lọc thời gian
        if table_option == "📝 Nhật ký Hành vi":
            st.info("Bộ lọc Thời gian")
            view_mode = st.selectbox("Chế độ xem:", ["Tuần", "Tháng"])
            
            if view_mode == "Tuần":
                # Chọn tuần (Giả lập số tuần trong năm)
                current_week = datetime.date.today().isocalendar()[1]
                selected_week = st.number_input("Chọn Tuần:", min_value=1, max_value=52, value=current_week)
                st.caption(f"Đang xem dữ liệu Tuần {selected_week}")
            else:
                selected_month = st.number_input("Chọn Tháng:", min_value=1, max_value=12, value=datetime.date.today().month)

    with col_data:
        # --- HIỂN THỊ BẢNG HỌC SINH ---
        if table_option == "👨‍🎓 Học sinh":
            st.subheader("Danh sách Học sinh (Master Data)")
            
            # Sử dụng data_editor để có thể chọn dòng
            edited_df = st.data_editor(
                st.session_state['df_students'],
                key="editor_students",
                num_rows="dynamic",
                use_container_width=True,
                # Cấu hình chọn dòng (Selection)
                on_change=None,
            )
            
            # Phần CHUYỂN TRANG: Chọn học sinh để phân tích
            st.markdown("### 🚀 Tác vụ")
            
            # Tạo danh sách chọn nhanh từ bảng
            student_options = dict(zip(st.session_state['df_students']['MaHS'], st.session_state['df_students']['Họ và tên']))
            
            # Hộp chọn để nhảy sang trang phân tích
            col_sel, col_btn = st.columns([3, 1])
            with col_sel:
                target_ma_hs = st.selectbox(
                    "Chọn Học sinh để Phân tích chi tiết:",
                    options=list(student_options.keys()),
                    format_func=lambda x: f"{student_options[x]} ({x})"
                )
            with col_btn:
                st.write("") # Spacer
                st.write("") 
                if st.button("Phân tích Ngay ▶️", type="primary"):
                    # CẬP NHẬT TRẠNG THÁI ĐỂ CHUYỂN TRANG
                    st.session_state['selected_student_id'] = target_ma_hs
                    st.session_state['current_page'] = 'dashboard'
                    st.rerun()

        # --- HIỂN THỊ NHẬT KÝ HÀNH VI ---
        elif table_option == "📝 Nhật ký Hành vi":
            st.subheader("Nhật ký Hành vi Chi tiết")
            # Ở đây có thể thêm logic lọc theo Tuần/Tháng dựa trên input bên trái
            # Demo hiển thị toàn bộ
            st.data_editor(st.session_state['df_logs'], num_rows="dynamic", use_container_width=True)

        # --- CÁC BẢNG DANH MỤC KHÁC ---
        elif table_option == "⚠️ Danh mục Vi phạm":
            st.subheader("Danh mục Lỗi Vi phạm")
            st.data_editor(st.session_state['df_violations'], num_rows="dynamic", use_container_width=True)
            
        elif table_option == "🏆 Danh mục Tích cực":
            st.subheader("Danh mục Thành tích")
            st.data_editor(st.session_state['df_achievements'], num_rows="dynamic", use_container_width=True)

# ==========================================
# 4. LOGIC TRANG 2: DASHBOARD IAS (NHƯ CŨ NHƯNG LIÊN KẾT DB)
# ==========================================

# --- Các hàm phụ trợ cũ ---
def calculate_score(df):
    score = df['Điểm Hạnh kiểm'].mean().round(1)
    return score

# Hàm tạo dữ liệu giả lập (Vẫn giữ để vẽ biểu đồ cho đẹp, nhưng lấy tên thật)
def generate_behavior_data_mock(student_name):
    N = 50 
    dates = pd.date_range(end=datetime.date.today(), periods=N, freq='D')
    
    # Logic giả lập dựa trên tên (để demo sự khác biệt)
    if "Nguyễn Văn A" in student_name:
        violation_trend = np.linspace(15, 2, N)
        positive_trend = np.linspace(5, 15, N)
    elif "Trần Thị B" in student_name:
        violation_trend = np.linspace(5, 20, N)
        positive_trend = np.linspace(10, 2, N)
    else:
        violation_trend = np.full(N, 8) + np.random.normal(0, 2, N)
        positive_trend = np.full(N, 8) + np.random.normal(0, 2, N)
        
    violation_data = np.clip(violation_trend + np.random.normal(0, 2, N), 0, 30).round(1)
    positive_data = np.clip(positive_trend + np.random.normal(0, 2, N), 0, 20).round(1)

    base_score = 90
    conduct_score = np.clip(base_score + positive_data - violation_data, 0, 110)

    data = {
        'Ngày': dates,
        'Điểm Vi phạm': violation_data,
        'Điểm Tích cực': positive_data,
        'Điểm Hạnh kiểm': conduct_score
    }
    df = pd.DataFrame(data)
    df = df.set_index('Ngày')
    return df

def display_core_analysis(data_df, selected_freq):
    # (Logic vẽ biểu đồ y như cũ - rút gọn cho đỡ dài dòng)
    cols_to_resample = ['Điểm Vi phạm', 'Điểm Tích cực', 'Điểm Hạnh kiểm']
    if selected_freq == "Ngày (Day)":
        chart_data = data_df[cols_to_resample]
        freq_label = "Ngày"
    elif selected_freq == "Tuần (Week)":
        chart_data = data_df[cols_to_resample].resample('W').mean()
        freq_label = "Tuần"
    elif selected_freq == "Tháng (Month)":
        chart_data = data_df[cols_to_resample].resample('M').mean()
        freq_label = "Tháng"

    current_date = data_df.index.max() 
    
    # Tính điểm ngày hiện tại
    data_current_day = data_df[data_df.index == current_date]
    score_current_day = calculate_score(data_current_day)
    
    mean_score = score_current_day 
    
    if mean_score >= 90:
        behavior_class = "A - Tốt"; color = "#4CAF50"
    elif mean_score >= 80:
        behavior_class = "B - Khá"; color = "#FF9800"
    else:
        behavior_class = "C - Cần Cải Thiện"; color = "#FF4B4B"
        
    st.markdown(f"**Xếp loại Hạnh kiểm:** <span style='color:{color}; font-size:24px;'>**{behavior_class}**</span>", unsafe_allow_html=True)
    st.metric(label=f"Điểm Hạnh kiểm ({freq_label} Hiện tại)", value=f"{mean_score}")
    
    # BIỂU ĐỒ ALTAIR
    st.subheader(f"Biểu đồ Xu hướng ({freq_label})")
    chart_data_long = chart_data.reset_index().melt('Ngày', var_name='Loại Điểm', value_name='Điểm số')
    selection = alt.selection_point(fields=['Loại Điểm'], bind='legend', empty=False)

    chart = alt.Chart(chart_data_long).mark_line(point=True, strokeWidth=3).encode(
        x=alt.X('Ngày:T', title=None, axis=alt.Axis(format="%d/%m")), 
        y=alt.Y('Điểm số:Q', title=None, scale=alt.Scale(zero=False)),
        color=alt.Color('Loại Điểm:N',
            scale=alt.Scale(domain=['Điểm Vi phạm', 'Điểm Tích cực', 'Điểm Hạnh kiểm'], range=['#FF4B4B', '#2E8B57', '#1E90FF']),
            legend=alt.Legend(title="Chú thích (Click để ẨN/HIỆN)", orient="bottom")
        ),
        opacity=alt.condition(selection, alt.value(0.05), alt.value(1)),
        tooltip=['Ngày:T', 'Loại Điểm', 'Điểm số']
    ).add_params(selection).interactive()
    st.altair_chart(chart, use_container_width=True)

def render_ias_dashboard_page():
    st.title("💡 PHÂN TÍCH HÀNH VI CÁ NHÂN (IAS)")
    
    # Lấy danh sách học sinh TỪ DATABASE (Session State)
    df_students = st.session_state['df_students']
    # Tạo list format: "Nguyễn Văn A (HS001)"
    student_options_list = df_students.apply(lambda x: f"{x['Họ và tên']} ({x['MaHS']})", axis=1).tolist()
    
    # Xử lý Logic chọn học sinh (Nếu được chuyển từ trang Data sang)
    default_index = 0
    if st.session_state['selected_student_id']:
        # Tìm index của học sinh được chọn
        ma_hs_target = st.session_state['selected_student_id']
        # Tìm trong cột MaHS
        found_row = df_students[df_students['MaHS'] == ma_hs_target]
        if not found_row.empty:
            target_string = f"{found_row.iloc[0]['Họ và tên']} ({found_row.iloc[0]['MaHS']})"
            if target_string in student_options_list:
                default_index = student_options_list.index(target_string)
    
    col1, col2, col3 = st.columns([2, 3, 2.5])

    with col1:
        st.header("1. Hồ sơ")
        # Selectbox chọn học sinh (Đã đồng bộ)
        selected_student_str = st.selectbox(
            "Học sinh:",
            student_options_list,
            index=default_index
        )
        
        # Reset trạng thái chọn sau khi đã load xong (để người dùng có thể chọn người khác)
        st.session_state['selected_student_id'] = None 
        
        if st.button("Tải/Cập nhật Dữ liệu"):
            st.session_state['data_loaded'] = True
            st.session_state['current_student_name'] = selected_student_str
            st.success(f"Đang phân tích: {selected_student_str}")

        st.markdown("---")
        if 'data_loaded' in st.session_state and st.session_state['data_loaded']:
            # Lấy thông tin chi tiết từ DB để hiển thị
            ma_hs_dang_chon = selected_student_str.split('(')[1].replace(')', '')
            info = df_students[df_students['MaHS'] == ma_hs_dang_chon].iloc[0]
            
            st.markdown(f"**Họ tên:** {info['Họ và tên']}")
            st.markdown(f"**Lớp:** {info['Lớp']}")
            st.markdown(f"**Ngày sinh:** {info['Ngày sinh']}")
            
            # Hiển thị bảng thu gọn
            st.caption("Dữ liệu tóm tắt từ DB:")
            st.dataframe(info.to_frame().T, hide_index=True)

    with col2:
        st.header("2. Phân tích Cốt lõi")
        selected_freq = st.selectbox("Tần suất:", ["Ngày (Day)", "Tuần (Week)", "Tháng (Month)"])
        
        if 'data_loaded' in st.session_state and st.session_state['data_loaded']:
            with st.container(height=550, border=False):
                # Sử dụng hàm giả lập biểu đồ (do dữ liệu thật cần nhập nhiều mới vẽ đẹp)
                # Nhưng logic dựa trên tên học sinh đã chọn
                data_chart = generate_behavior_data_mock(st.session_state['current_student_name'])
                display_core_analysis(data_chart, selected_freq)
        else:
            st.info("👈 Nhấn nút Tải dữ liệu.")

    with col3:
        st.header("3. Đề xuất")
        if 'data_loaded' in st.session_state and st.session_state['data_loaded']:
            with st.container(height=550, border=False):
                st.info("Dựa trên dữ liệu 50 ngày gần nhất...")
                st.warning("🤖 AI: Cần cải thiện điểm vi phạm vào cuối tuần.")

# ==========================================
# 5. ĐIỀU HƯỚNG CHÍNH (SIDEBAR NAVIGATION)
# ==========================================

# Tạo Sidebar để chuyển trang
with st.sidebar:
    st.title("MENU HỆ THỐNG")
    
    # Dùng radio button làm menu
    page_selection = st.radio(
        "Chọn chức năng:",
        ["💡 Phân tích IAS", "📂 Quản lý Dữ liệu"],
        index=0 if st.session_state['current_page'] == 'dashboard' else 1
    )
    
    st.markdown("---")
    st.info("Hệ thống Demo KHKT 2025")

# Xử lý hiển thị trang dựa trên lựa chọn
if page_selection == "💡 Phân tích IAS":
    render_ias_dashboard_page()
elif page_selection == "📂 Quản lý Dữ liệu":
    render_data_management_page()
