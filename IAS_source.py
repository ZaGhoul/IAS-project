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
# 2. KHỞI TẠO CƠ SỞ DỮ LIỆU (DATA TUẦN 1-3)
# ==========================================

def init_db():
    # 1. Bảng Học sinh (Master Data - Thông tin tĩnh)
    if 'df_students_master' not in st.session_state:
        data_hs = {
            'MaHS': ['HS001', 'HS002', 'HS003', 'HS004', 'HS005'],
            'Họ và tên': ['Nguyễn Văn A', 'Trần Thị B', 'Lê Văn C', 'Phạm Thị D', 'Hoàng Văn E'],
            'Ngày sinh': ['2008-01-15', '2008-05-20', '2008-11-02', '2008-03-10', '2008-08-18'],
            'Lớp': ['11A1', '11A1', '11A2', '11A2', '11A3']
        }
        st.session_state['df_students_master'] = pd.DataFrame(data_hs)

    # 2. Bảng Nhật ký Hành vi (Dữ liệu Tuần 1, 2, 3)
    if 'df_logs' not in st.session_state:
        # Tạo dữ liệu giả lập cho 3 tuần đầu năm 2025
        # Tuần 1: 01/01 - 07/01 | Tuần 2: 08/01 - 14/01 | Tuần 3: 15/01 - 21/01
        
        logs_data = []
        students = ['HS001', 'HS002', 'HS003', 'HS004', 'HS005']
        
        # Hàm tạo log ngẫu nhiên
        def create_log(date_str, mahs, type_log, desc, point):
            return {
                'Ngày': pd.to_datetime(date_str).date(),
                'MaHS': mahs,
                'Loại': type_log,
                'Nội dung': desc,
                'Điểm': point,
                # Tính số tuần ISO
                'Tuần': pd.to_datetime(date_str).isocalendar()[1] 
            }

        # --- DỮ LIỆU TUẦN 1 ---
        logs_data.append(create_log('2025-01-02', 'HS001', 'Tích cực', 'Phát biểu bài', 5))
        logs_data.append(create_log('2025-01-03', 'HS002', 'Vi phạm', 'Đi học muộn', 2))
        logs_data.append(create_log('2025-01-05', 'HS001', 'Tích cực', 'Giúp bạn', 3))
        
        # --- DỮ LIỆU TUẦN 2 ---
        logs_data.append(create_log('2025-01-09', 'HS001', 'Tích cực', 'Điểm 10', 5))
        logs_data.append(create_log('2025-01-10', 'HS002', 'Vi phạm', 'Mất trật tự', 5))
        logs_data.append(create_log('2025-01-11', 'HS003', 'Tích cực', 'Tham gia CLB', 5))
        
        # --- DỮ LIỆU TUẦN 3 ---
        logs_data.append(create_log('2025-01-16', 'HS001', 'Vi phạm', 'Quên vở', 2)) # HS001 bị trừ điểm tuần này
        logs_data.append(create_log('2025-01-17', 'HS004', 'Tích cực', 'Làm việc nhóm tốt', 5))
        logs_data.append(create_log('2025-01-18', 'HS005', 'Vi phạm', 'Không trực nhật', 5))

        st.session_state['df_logs'] = pd.DataFrame(logs_data)

    # 3. Biến quản lý trang
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = 'dashboard' # Mặc định
    if 'selected_student_id' not in st.session_state:
        st.session_state['selected_student_id'] = None

init_db()

# ==========================================
# 3. LOGIC TRANG 1: QUẢN LÝ DỮ LIỆU
# ==========================================

def render_data_management_page():
    st.title("📂 BẢNG DỮ LIỆU HỆ THỐNG")
    
    col_ctrl, col_data = st.columns([1.2, 4])
    
    with col_ctrl:
        st.subheader("Cấu hình")
        # Chọn bảng
        table_option = st.radio(
            "Chọn Bảng Dữ liệu:",
            ["👨‍🎓 Học sinh", "📝 Nhật ký Hành vi", "⚠️ Danh mục Vi phạm", "🏆 Danh mục Tích cực"]
        )
        
        st.markdown("---")
        
        # --- BỘ LỌC THỜI GIAN (Áp dụng cho cả Bảng HS và Nhật ký) ---
        if table_option in ["👨‍🎓 Học sinh", "📝 Nhật ký Hành vi"]:
            st.info("Bộ lọc Thời gian")
            
            # Chọn Tuần (Mặc định Tuần 1-3)
            # Giả sử hôm nay đang ở Tuần 3
            selected_week = st.number_input("Chọn Tuần (Năm 2025):", min_value=1, max_value=52, value=3)
            
            st.caption(f"Đang hiển thị dữ liệu: **Tuần {selected_week}**")

    with col_data:
        # --- XỬ LÝ DỮ LIỆU HIỂN THỊ ---
        
        if table_option == "👨‍🎓 Học sinh":
            st.subheader(f"Danh sách Học sinh & Điểm Tuần {selected_week}")
            
            # 1. Lấy dữ liệu Master
            df_display = st.session_state['df_students_master'].copy()
            
            # 2. Tính toán điểm từ Nhật Ký dựa trên Tuần đã chọn
            df_logs = st.session_state['df_logs']
            df_logs_week = df_logs[df_logs['Tuần'] == selected_week]
            
            # Gom nhóm tính tổng điểm
            scores = df_logs_week.groupby(['MaHS', 'Loại'])['Điểm'].sum().unstack(fill_value=0)
            
            # Gộp vào bảng hiển thị (Merge)
            if not scores.empty:
                # Đảm bảo có đủ cột nếu tuần đó không có loại nào
                if 'Tích cực' not in scores.columns: scores['Tích cực'] = 0
                if 'Vi phạm' not in scores.columns: scores['Vi phạm'] = 0
                
                df_display = df_display.merge(scores, on='MaHS', how='left').fillna(0)
            else:
                df_display['Tích cực'] = 0
                df_display['Vi phạm'] = 0
                
            # Tính Hạnh kiểm (Công thức 90 + Tích cực - Vi phạm)
            df_display['Hạnh kiểm'] = 90 + df_display['Tích cực'] - df_display['Vi phạm']
            
            # Hiển thị bảng
            st.dataframe(
                df_display,
                use_container_width=True,
                column_config={
                    "Tích cực": st.column_config.NumberColumn("Điểm Tích cực", format="%d ⬆️"),
                    "Vi phạm": st.column_config.NumberColumn("Điểm Vi phạm", format="%d ⬇️"),
                    "Hạnh kiểm": st.column_config.ProgressColumn(
                        "Điểm Hạnh kiểm", format="%d", min_value=0, max_value=120
                    ),
                },
                hide_index=True
            )
            
            # --- CHUYỂN TRANG ---
            st.markdown("### 🚀 Tác vụ Phân tích")
            student_dict = dict(zip(df_display['MaHS'], df_display['Họ và tên']))
            
            c1, c2 = st.columns([3, 1])
            with c1:
                target_hs = st.selectbox("Chọn hồ sơ:", list(student_dict.keys()), format_func=lambda x: f"{student_dict[x]} ({x})")
            with c2:
                st.write("")
                st.write("")
                # Nút bấm chuyển trang
                if st.button("Phân tích Ngay ▶️", type="primary"):
                    st.session_state['selected_student_id'] = target_hs
                    st.session_state['current_page'] = 'dashboard' # Đặt trạng thái
                    st.rerun() # Bắt buộc tải lại trang ngay lập tức

        elif table_option == "📝 Nhật ký Hành vi":
            st.subheader(f"Nhật ký Chi tiết Tuần {selected_week}")
            # Lọc dữ liệu theo tuần
            df_logs = st.session_state['df_logs']
            filtered_logs = df_logs[df_logs['Tuần'] == selected_week]
            
            st.data_editor(filtered_logs, num_rows="dynamic", use_container_width=True)

        else:
            st.subheader("Dữ liệu Danh mục (Tĩnh)")
            st.info("Bảng danh mục không thay đổi theo tuần.")

# ==========================================
# 4. LOGIC TRANG 2: DASHBOARD IAS
# ==========================================

# Hàm tính điểm đơn giản
def calculate_score(df):
    score = df['Điểm Hạnh kiểm'].mean().round(1)
    return score

# Hàm giả lập dữ liệu biểu đồ dựa trên tên (để vẽ biểu đồ 50 ngày cho đẹp)
def generate_behavior_data_mock(student_name):
    N = 50 
    # Kết thúc tại ngày hiện tại
    dates = pd.date_range(end=datetime.date.today(), periods=N, freq='D')
    
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
    
    # Logic Hạnh kiểm = 90 + Tích cực - Vi phạm
    base_score = 90
    conduct_score = np.clip(base_score + positive_data - violation_data, 0, 120)

    data = {'Ngày': dates, 'Điểm Vi phạm': violation_data, 'Điểm Tích cực': positive_data, 'Điểm Hạnh kiểm': conduct_score}
    df = pd.DataFrame(data)
    df = df.set_index('Ngày')
    return df

def display_core_analysis(data_df, selected_freq):
    # Logic nhóm dữ liệu
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
    data_current_day = data_df[data_df.index == current_date]
    score_current_day = calculate_score(data_current_day)
    mean_score = score_current_day 
    
    if mean_score >= 90: behavior_class = "A - Tốt"; color = "#4CAF50"
    elif mean_score >= 80: behavior_class = "B - Khá"; color = "#FF9800"
    else: behavior_class = "C - Cần Cải Thiện"; color = "#FF4B4B"
        
    st.markdown(f"**Xếp loại Hạnh kiểm:** <span style='color:{color}; font-size:24px;'>**{behavior_class}**</span>", unsafe_allow_html=True)
    st.metric(label=f"Điểm Hạnh kiểm ({freq_label} Hiện tại)", value=f"{mean_score}")
    
    # Biểu đồ Altair (ẨN/HIỆN ĐỘC LẬP)
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
    
    # Lấy Master Data
    df_students = st.session_state['df_students_master']
    student_options_list = df_students.apply(lambda x: f"{x['Họ và tên']} ({x['MaHS']})", axis=1).tolist()
    
    # Logic Tự động chọn (Auto-select) khi chuyển từ trang Data
    default_index = 0
    if st.session_state['selected_student_id']:
        ma_hs_target = st.session_state['selected_student_id']
        found_row = df_students[df_students['MaHS'] == ma_hs_target]
        if not found_row.empty:
            target_string = f"{found_row.iloc[0]['Họ và tên']} ({found_row.iloc[0]['MaHS']})"
            if target_string in student_options_list:
                default_index = student_options_list.index(target_string)
    
    col1, col2, col3 = st.columns([2, 3, 2.5])

    with col1:
        st.header("1. Hồ sơ")
        selected_student_str = st.selectbox("Học sinh:", student_options_list, index=default_index)
        
        # Reset ID chọn để lần sau người dùng có thể tự chọn
        st.session_state['selected_student_id'] = None 
        
        if st.button("Cập nhật Dữ liệu"):
            st.session_state['data_loaded'] = True
            st.session_state['current_student_name'] = selected_student_str

        st.markdown("---")
        if 'data_loaded' in st.session_state and st.session_state['data_loaded']:
            ma_hs = selected_student_str.split('(')[1].replace(')', '')
            info = df_students[df_students['MaHS'] == ma_hs].iloc[0]
            st.markdown(f"**Họ tên:** {info['Họ và tên']}")
            st.markdown(f"**Lớp:** {info['Lớp']}")
            st.markdown(f"**Ngày sinh:** {info['Ngày sinh']}")

    with col2:
        st.header("2. Phân tích Cốt lõi")
        selected_freq = st.selectbox("Tần suất:", ["Ngày (Day)", "Tuần (Week)", "Tháng (Month)"])
        
        if 'data_loaded' in st.session_state and st.session_state['data_loaded']:
            with st.container(height=550, border=False):
                # Vẽ biểu đồ dựa trên tên học sinh đã chọn
                data_chart = generate_behavior_data_mock(st.session_state['current_student_name'])
                display_core_analysis(data_chart, selected_freq)
        else:
            st.info("👈 Nhấn nút Cập nhật Dữ liệu.")

    with col3:
        st.header("3. Đề xuất")
        if 'data_loaded' in st.session_state and st.session_state['data_loaded']:
            with st.container(height=550, border=False):
                st.info("Dựa trên dữ liệu 50 ngày gần nhất...")
                st.success("🤖 AI: Học sinh đang có xu hướng tích cực trong tuần này.")

# ==========================================
# 5. ĐIỀU HƯỚNG CHÍNH (SIDEBAR)
# ==========================================

with st.sidebar:
    st.title("MENU HỆ THỐNG")
    
    # QUAN TRỌNG: Cập nhật index của radio dựa trên session_state
    idx = 0 if st.session_state['current_page'] == 'dashboard' else 1
    
    page_selection = st.radio(
        "Chọn chức năng:",
        ["💡 Phân tích IAS", "📂 Quản lý Dữ liệu"],
        index=idx,
        key="nav_radio" # Đặt key để tránh lỗi duplicate
    )
    
    # Logic đồng bộ ngược lại: Nếu người dùng click radio, cập nhật session state
    if page_selection == "💡 Phân tích IAS":
        st.session_state['current_page'] = 'dashboard'
    else:
        st.session_state['current_page'] = 'data_mgmt'

    st.markdown("---")
    st.info("Demo KHKT 2025")

# Render Trang
if st.session_state['current_page'] == 'dashboard':
    render_ias_dashboard_page()
else:
    render_data_management_page()
