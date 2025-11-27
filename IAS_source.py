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
.stSelectbox label { font-weight: bold; color: #4CAF50; font-size: 1.1rem !important; }
div[data-testid="stSelectbox"] div[role="combobox"] { border: 1px solid #fafafa; border-radius: 0.5rem; }
div[data-testid="stSelectbox"] div[role="combobox"]:hover { border-color: #4CAF50 !important; cursor: pointer; }
div[data-testid="stSelectbox"] div[role="combobox"]:focus-within { border-color: #4CAF50 !important; box-shadow: 0 0 0 0.2rem rgba(76, 175, 80, 0.25) !important; }
div[data-testid="stSelectbox"] svg { fill: #fafafa !important; }

/* DataFrame Styling */
.stDataFrame { border: 1px solid #fafafa; }
.stButton button { border: 1px solid #4CAF50; }

/* Form nhập liệu styling */
div[data-testid="stExpander"] {
    border: 1px solid #333;
    border-radius: 8px;
    background-color: #0e1117;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. KHỞI TẠO CƠ SỞ DỮ LIỆU
# ==========================================

def init_db():
    # 1. Bảng Học sinh (Master)
    if 'df_students_master' not in st.session_state:
        data_hs = {
            'MaHS': ['HS001', 'HS002', 'HS003', 'HS004', 'HS005'],
            'Họ và tên': ['Nguyễn Văn A', 'Trần Thị B', 'Lê Văn C', 'Phạm Thị D', 'Hoàng Văn E'],
            'Ngày sinh': ['2008-01-15', '2008-05-20', '2008-11-02', '2008-03-10', '2008-08-18'],
            'Lớp': ['11A1', '11A1', '11A2', '11A2', '11A3']
        }
        st.session_state['df_students_master'] = pd.DataFrame(data_hs)

    # 2. Bảng Danh mục Vi Phạm
    if 'df_violations' not in st.session_state:
        data_vp = {
            'Tên Vi phạm': ['Đi học muộn', 'Không làm bài tập', 'Mất trật tự', 'Không trực nhật', 'Quên vở'],
            'Điểm': [2, 5, 3, 5, 2]
        }
        st.session_state['df_violations'] = pd.DataFrame(data_vp)

    # 3. Bảng Danh mục Hoạt động
    if 'df_achievements' not in st.session_state:
        data_tc = {
            'Tên Hoạt động': ['Phát biểu bài', 'Đạt điểm 10', 'Giúp đỡ bạn bè', 'Tham gia CLB', 'Làm việc nhóm tốt'],
            'Điểm': [2, 5, 3, 5, 5]
        }
        st.session_state['df_achievements'] = pd.DataFrame(data_tc)

    # 4. Bảng Nhật ký Hành vi
    if 'df_logs' not in st.session_state:
        # Khởi tạo rỗng hoặc có mẫu, có cột STT
        logs_data = [
            {'STT': 1, 'Ngày': datetime.date(2025, 1, 2), 'MaHS': 'HS001', 'Loại': 'Hoạt động', 'Nội dung': 'Phát biểu bài', 'Điểm': 5, 'Tuần': 1},
            {'STT': 2, 'Ngày': datetime.date(2025, 1, 3), 'MaHS': 'HS002', 'Loại': 'Vi phạm', 'Nội dung': 'Đi học muộn', 'Điểm': 2, 'Tuần': 1},
            {'STT': 3, 'Ngày': datetime.date(2025, 1, 16), 'MaHS': 'HS001', 'Loại': 'Vi phạm', 'Nội dung': 'Quên vở', 'Điểm': 2, 'Tuần': 3}
        ]
        st.session_state['df_logs'] = pd.DataFrame(logs_data)

    if 'current_page' not in st.session_state: st.session_state['current_page'] = 'dashboard'
    if 'selected_student_id' not in st.session_state: st.session_state['selected_student_id'] = None

init_db()

# ==========================================
# 3. LOGIC TRANG 1: QUẢN LÝ DỮ LIỆU (NÂNG CẤP)
# ==========================================

def render_data_management_page():
    st.title("📂 QUẢN LÝ CƠ SỞ DỮ LIỆU")
    
    col_ctrl, col_data = st.columns([1.2, 4])
    
    with col_ctrl:
        st.subheader("Cấu hình")
        table_option = st.radio(
            "Chọn Bảng Dữ liệu:",
            ["👨‍🎓 Học sinh", "📝 Nhật ký Hành vi", "⚠️ Danh mục Vi phạm", "🏆 Danh mục Hoạt động"]
        )
        st.markdown("---")
        
        # Chỉ hiện bộ lọc thời gian cho Học sinh và Nhật ký
        selected_week = 3
        if table_option in ["👨‍🎓 Học sinh", "📝 Nhật ký Hành vi"]:
            st.info("Bộ lọc Thời gian")
            selected_week = st.number_input("Chọn Tuần (Năm 2025):", min_value=1, max_value=52, value=3)
            st.caption(f"Dữ liệu Tuần {selected_week}")

    with col_data:
        # ---------------------------------------------------------
        # A. BẢNG HỌC SINH (MASTER DATA)
        # ---------------------------------------------------------
        if table_option == "👨‍🎓 Học sinh":
            st.subheader(f"Danh sách Học sinh & Điểm Tuần {selected_week}")
            
            # Tính điểm (Logic cũ)
            df_display = st.session_state['df_students_master'].copy()
            df_logs = st.session_state['df_logs']
            df_logs_week = df_logs[df_logs['Tuần'] == selected_week]
            scores = df_logs_week.groupby(['MaHS', 'Loại'])['Điểm'].sum().unstack(fill_value=0)
            
            if not scores.empty:
                if 'Hoạt động' not in scores.columns: scores['Hoạt động'] = 0
                if 'Vi phạm' not in scores.columns: scores['Vi phạm'] = 0
                df_display = df_display.merge(scores, on='MaHS', how='left').fillna(0)
            else:
                df_display['Hoạt động'] = 0
                df_display['Vi phạm'] = 0
            df_display['Hạnh kiểm'] = 90 + df_display['Hoạt động'] - df_display['Vi phạm']
            
            # Hiển thị
            st.dataframe(
                df_display, use_container_width=True, hide_index=True,
                column_config={
                    "Hạnh kiểm": st.column_config.ProgressColumn("Hạnh kiểm", format="%d", min_value=0, max_value=120)
                }
            )
            
            # Form thêm học sinh (CRUD đơn giản)
            with st.expander("➕ Thêm/Sửa Học sinh"):
                st.info("Để sửa, hãy chỉnh trực tiếp ở bảng 'Danh mục' nếu cần (demo rút gọn).")

            # Chuyển trang Phân tích
            st.markdown("### 🚀 Tác vụ Phân tích")
            student_dict = dict(zip(df_display['MaHS'], df_display['Họ và tên']))
            c1, c2 = st.columns([3, 1])
            with c1:
                target_hs = st.selectbox("Chọn hồ sơ:", list(student_dict.keys()), format_func=lambda x: f"{student_dict[x]} ({x})")
            with c2:
                st.write("")
                st.write("")
                if st.button("Phân tích Ngay", type="primary"):
                    st.session_state['selected_student_id'] = target_hs
                    st.session_state['current_page'] = 'dashboard'
                    st.rerun()



        # ---------------------------------------------------------
        # B. BẢNG NHẬT KÝ HÀNH VI (CRUD NÂNG CAO - HEIDI STYLE)
        # ---------------------------------------------------------
        elif table_option == "📝 Nhật ký Hành vi":
            st.subheader("📝 Quản lý Nhật ký Hành vi")

            # --- 1. FORM NHẬP LIỆU THÔNG MINH (Thay thế cho việc nhập trực tiếp khó khăn) ---
            with st.container():
                st.markdown("##### ➕ Thêm Nhật ký Mới")
                
                # Lấy danh sách Học sinh cho Dropdown
                list_hs = st.session_state['df_students_master']
                hs_options = list_hs['MaHS'].tolist()
                hs_labels = list_hs['Họ và tên'].tolist()
                hs_dict = dict(zip(hs_options, hs_labels))
                
                c_form_1, c_form_2, c_form_3, c_form_4 = st.columns([2, 1.5, 2.5, 1])
                
                with c_form_1:
                    # Dropdown chọn Học sinh (Hiện cả Tên và Mã)
                    new_mahs = st.selectbox("Học sinh", hs_options, format_func=lambda x: f"{hs_dict[x]} ({x})")
                
                with c_form_2:
                    # Dropdown Loại
                    new_type = st.selectbox("Loại hành vi", ["Vi phạm", "Hoạt động"])
                
                with c_form_3:
                    # Dropdown Nội dung (Phụ thuộc vào Loại)
                    if new_type == "Vi phạm":
                        content_source = st.session_state['df_violations']
                        content_col = 'Tên Vi phạm'
                    else:
                        content_source = st.session_state['df_achievements']
                        content_col = 'Tên Hoạt động'
                        
                    content_options = content_source[content_col].tolist()
                    new_content = st.selectbox("Nội dung chi tiết", content_options)
                    
                    # Tự động lấy điểm tương ứng
                    auto_score = content_source.loc[content_source[content_col] == new_content, 'Điểm'].values[0]

                with c_form_4:
                    # Điểm (Tự động điền nhưng có thể sửa)
                    new_score = st.number_input("Điểm", value=int(auto_score))

                c_form_5, c_form_6 = st.columns([2, 6])
                with c_form_5:
                    new_date = st.date_input("Ngày", datetime.date.today())
                with c_form_6:
                    st.write("") 
                    st.write("") 
                    if st.button("💾 Lưu vào CSDL", type="primary"):
                        # Logic Auto-Increment STT
                        current_max_stt = 0
                        if not st.session_state['df_logs'].empty:
                            current_max_stt = st.session_state['df_logs']['STT'].max()
                        
                        new_row = {
                            'STT': current_max_stt + 1, # Tự tăng
                            'Ngày': new_date,
                            'MaHS': new_mahs,
                            'Loại': new_type,
                            'Nội dung': new_content,
                            'Điểm': new_score,
                            'Tuần': new_date.isocalendar()[1]
                        }
                        # Thêm vào DataFrame
                        st.session_state['df_logs'] = pd.concat([st.session_state['df_logs'], pd.DataFrame([new_row])], ignore_index=True)
                        st.success("Đã thêm mới thành công!")
                        st.rerun()

            st.markdown("---")

            # --- 2. HIỂN THỊ BẢNG DỮ LIỆU (Cho phép Xóa/Sửa nhẹ) ---
            st.markdown(f"**Dữ liệu Tuần {selected_week}** (Bạn có thể sửa trực tiếp Ngày/Điểm hoặc Xóa dòng)")
            
            # Lọc hiển thị nhưng vẫn giữ index gốc để update
            df_logs = st.session_state['df_logs']
            
            # Hiển thị bảng Editor
            edited_logs = st.data_editor(
                df_logs[df_logs['Tuần'] == selected_week], # Chỉ hiện tuần chọn
                num_rows="dynamic", # Cho phép thêm/xóa dòng
                use_container_width=True,
                key="log_editor",
                column_config={
                    "MaHS": st.column_config.TextColumn("Mã HS", disabled=True), # Khóa cột mã để tránh lỗi
                    "Loại": st.column_config.TextColumn("Loại", disabled=True),
                    "Nội dung": st.column_config.TextColumn("Nội dung", disabled=True),
                    "STT": st.column_config.NumberColumn("STT", disabled=True),
                }
            )
            
            # Logic Cập nhật lại Session State khi sửa/xóa dưới bảng
            # Lưu ý: Sửa trực tiếp trong filter view hơi phức tạp, ở đây demo hiển thị

        # ---------------------------------------------------------
        # C. BẢNG DANH MỤC (VI PHẠM / Hoạt động) - CRUD HOÀN CHỈNH
        # ---------------------------------------------------------
        elif table_option == "⚠️ Danh mục Vi phạm":
            st.subheader("Quản lý Danh mục Vi phạm")
            st.info("💡 Bảng này là bảng Tĩnh, dùng chung cho cả năm học.")
            
            edited_vp = st.data_editor(
                st.session_state['df_violations'],
                num_rows="dynamic", # Cho phép Thêm/Xóa dòng
                use_container_width=True,
                key="editor_vp"
            )
            # Cập nhật lại session state ngay lập tức nếu có thay đổi
            if not edited_vp.equals(st.session_state['df_violations']):
                st.session_state['df_violations'] = edited_vp
                st.rerun()

        elif table_option == "🏆 Danh mục Hoạt động":
            st.subheader("Quản lý Danh mục Hoạt động")
            st.info("💡 Bảng này là bảng Tĩnh, dùng chung cho cả năm học.")
            
            edited_tc = st.data_editor(
                st.session_state['df_achievements'],
                num_rows="dynamic",
                use_container_width=True,
                key="editor_tc"
            )
            if not edited_tc.equals(st.session_state['df_achievements']):
                st.session_state['df_achievements'] = edited_tc
                st.rerun()

# ==========================================
# 4. LOGIC TRANG 2: DASHBOARD IAS
# ==========================================

def calculate_score(df):
    score = df['Điểm Hạnh kiểm'].mean().round(1)
    return score

def generate_behavior_data_mock(student_name):
    # (Logic giả lập để vẽ biểu đồ đẹp)
    N = 50 
    dates = pd.date_range(end=datetime.date.today(), periods=N, freq='D')
    if "Nguyễn Văn A" in student_name:
        violation_trend = np.linspace(15, 2, N); positive_trend = np.linspace(5, 15, N)
    elif "Trần Thị B" in student_name:
        violation_trend = np.linspace(5, 20, N); positive_trend = np.linspace(10, 2, N)
    else:
        violation_trend = np.full(N, 8) + np.random.normal(0, 2, N); positive_trend = np.full(N, 8) + np.random.normal(0, 2, N)
    violation_data = np.clip(violation_trend + np.random.normal(0, 2, N), 0, 30).round(1)
    positive_data = np.clip(positive_trend + np.random.normal(0, 2, N), 0, 20).round(1)
    base_score = 90
    conduct_score = np.clip(base_score + positive_data - violation_data, 0, 100)
    data = {'Ngày': dates, 'Điểm Vi phạm': violation_data, 'Điểm Hoạt động': positive_data, 'Điểm Hạnh kiểm': conduct_score}
    df = pd.DataFrame(data)
    df = df.set_index('Ngày')
    return df

def display_core_analysis(data_df, selected_freq):
    cols_to_resample = ['Điểm Vi phạm', 'Điểm Hoạt động', 'Điểm Hạnh kiểm']
    if selected_freq == "Ngày (Day)": chart_data = data_df[cols_to_resample]; freq_label = "Ngày"
    elif selected_freq == "Tuần (Week)": chart_data = data_df[cols_to_resample].resample('W').mean(); freq_label = "Tuần"
    elif selected_freq == "Tháng (Month)": chart_data = data_df[cols_to_resample].resample('M').mean(); freq_label = "Tháng"

    current_date = data_df.index.max() 
    data_current_day = data_df[data_df.index == current_date]
    mean_score = calculate_score(data_current_day)
    
    if mean_score >= 90: behavior_class = "A - Tốt"; color = "#4CAF50"
    elif mean_score >= 80: behavior_class = "B - Khá"; color = "#FF9800"
    else: behavior_class = "C - Cần Cải Thiện"; color = "#FF4B4B"
        
    st.markdown(f"**Xếp loại Hạnh kiểm:** <span style='color:{color}; font-size:24px;'>**{behavior_class}**</span>", unsafe_allow_html=True)
    st.metric(label=f"Điểm Hạnh kiểm ({freq_label} Hiện tại)", value=f"{mean_score}")
    
    st.subheader(f"Biểu đồ Xu hướng ({freq_label})")
    chart_data_long = chart_data.reset_index().melt('Ngày', var_name='Loại Điểm', value_name='Điểm số')
    selection = alt.selection_point(fields=['Loại Điểm'], bind='legend', empty=true)
    chart = alt.Chart(chart_data_long).mark_line(point=True, strokeWidth=3).encode(
        x=alt.X('Ngày:T', title=None, axis=alt.Axis(format="%d/%m")), 
        y=alt.Y('Điểm số:Q', title=None, scale=alt.Scale(zero=False)),
        color=alt.Color('Loại Điểm:N', scale=alt.Scale(domain=['Điểm Vi phạm', 'Điểm Hoạt động', 'Điểm Hạnh kiểm'], range=['#FF4B4B', '#2E8B57', '#1E90FF']), legend=alt.Legend(title="Chú thích", orient="bottom")),
        opacity=alt.condition(selection | alt.datum.Loại_Điểm == None, alt.value(1), alt.value(0.05)), tooltip=['Ngày:T', 'Loại Điểm', 'Điểm số']
    ).add_params(selection).interactive()
    st.altair_chart(chart, use_container_width=True)

def render_ias_dashboard_page():
    st.title("💡 PHÂN TÍCH HÀNH VI CÁ NHÂN (IAS)")
    df_students = st.session_state['df_students_master']
    student_options_list = df_students.apply(lambda x: f"{x['Họ và tên']} ({x['MaHS']})", axis=1).tolist()
    default_index = 0
    if st.session_state['selected_student_id']:
        ma_hs_target = st.session_state['selected_student_id']
        found_row = df_students[df_students['MaHS'] == ma_hs_target]
        if not found_row.empty:
            target_string = f"{found_row.iloc[0]['Họ và tên']} ({found_row.iloc[0]['MaHS']})"
            if target_string in student_options_list: default_index = student_options_list.index(target_string)
    
    col1, col2, col3 = st.columns([2, 3, 2.5])
    with col1:
        st.header("1. Hồ sơ")
        selected_student_str = st.selectbox("Học sinh:", student_options_list, index=default_index)
        st.session_state['selected_student_id'] = None 
        if st.button("Cập nhật Dữ liệu"): st.session_state['data_loaded'] = True; st.session_state['current_student_name'] = selected_student_str
        st.markdown("---")
        if 'data_loaded' in st.session_state and st.session_state['data_loaded']:
            ma_hs = selected_student_str.split('(')[1].replace(')', '')
            info = df_students[df_students['MaHS'] == ma_hs].iloc[0]
            st.markdown(f"**Họ tên:** {info['Họ và tên']}"); st.markdown(f"**Lớp:** {info['Lớp']}"); st.markdown(f"**Ngày sinh:** {info['Ngày sinh']}")
    with col2:
        st.header("2. Phân tích Cốt lõi")
        selected_freq = st.selectbox("Tần suất:", ["Ngày (Day)", "Tuần (Week)", "Tháng (Month)"])
        if 'data_loaded' in st.session_state and st.session_state['data_loaded']:
            with st.container(height=550, border=False):
                data_chart = generate_behavior_data_mock(st.session_state['current_student_name'])
                display_core_analysis(data_chart, selected_freq)
        else: st.info("👈 Nhấn nút Cập nhật Dữ liệu.")
    with col3:
        st.header("3. Đề xuất")
        if 'data_loaded' in st.session_state and st.session_state['data_loaded']:
            with st.container(height=550, border=False):
                st.info("Dựa trên tần suất vi phạm và hoạt động"); st.success("🤖 AI: Học sinh đang có xu hướng Hoạt động.")

# ==========================================
# 5. ĐIỀU HƯỚNG CHÍNH
# ==========================================
def on_nav_change():
    if st.session_state['nav_radio'] == "💡 Phân tích IAS":
        st.session_state['current_page'] = 'dashboard'
    else:
        st.session_state['current_page'] = 'data_mgmt'

with st.sidebar:
    st.title("MENU HỆ THỐNG")
    st.radio(
        "Chọn chức năng:",
        ["💡 Phân tích IAS", "📂 Quản lý Dữ liệu"],
        key="nav_radio",
        on_change=on_nav_change
    )
    st.markdown("---")
    st.info("Demo KHKT 2025")

if st.session_state['current_page'] == 'dashboard': render_ias_dashboard_page()
else: render_data_management_page()






