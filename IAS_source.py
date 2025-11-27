import streamlit as st
import pandas as pd
import numpy as np
import datetime
import random
import os
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

import os

def init_db():
    # 1. Bảng Học sinh (Master)
    if 'df_students_master' not in st.session_state:
        try:
            st.session_state['df_students_master'] = pd.read_csv("students_master.csv")
        except FileNotFoundError:
            data_hs = {
                'MaHS': ['HS001', 'HS002', 'HS003', 'HS004', 'HS005'],
                'Họ và tên': ['Nguyễn Văn A', 'Trần Thị B', 'Lê Văn C', 'Phạm Thị D', 'Hoàng Văn E'],
                'Ngày sinh': ['2008-01-15', '2008-05-20', '2008-11-02', '2008-03-10', '2008-08-18'],
                'Lớp': ['11A1', '11A1', '11A2', '11A2', '11A3']
            }
            st.session_state['df_students_master'] = pd.DataFrame(data_hs)
            st.session_state['df_students_master'].to_csv("students_master.csv", index=False)

    # 2. Danh mục Vi phạm
    if 'df_violations' not in st.session_state:
        try:
            st.session_state['df_violations'] = pd.read_csv("violations.csv")
        except FileNotFoundError:
            data_vp = {
                'Tên Vi phạm': ['Đi học muộn', 'Không làm bài tập', 'Mất trật tự', 'Không trực nhật', 'Quên vở'],
                'Điểm': [2, 5, 3, 5, 2]
            }
            st.session_state['df_violations'] = pd.DataFrame(data_vp)
            st.session_state['df_violations'].to_csv("violations.csv", index=False)

    # 3. Danh mục Hoạt động
    if 'df_achievements' not in st.session_state:
        try:
            st.session_state['df_achievements'] = pd.read_csv("achievements.csv")
        except FileNotFoundError:
            data_tc = {
                'Tên Hoạt động': ['Phát biểu bài', 'Đạt điểm 10', 'Giúp đỡ bạn bè', 'Tham gia CLB', 'Làm việc nhóm tốt'],
                'Điểm': [2, 5, 3, 5, 5]
            }
            st.session_state['df_achievements'] = pd.DataFrame(data_tc)
            st.session_state['df_achievements'].to_csv("achievements.csv", index=False)

    # 4. Nhật ký Hành vi
    if 'df_logs' not in st.session_state:
        try:
            st.session_state['df_logs'] = pd.read_csv("logs.csv", parse_dates=['Ngày'])
        except FileNotFoundError:
            logs_data = [
                {'STT': 1, 'Ngày': pd.to_datetime('2025-01-02'), 'MaHS': 'HS001', 'Loại': 'Hoạt động', 'Nội dung': 'Phát biểu bài', 'Điểm': 5, 'Tuần': 1},
                {'STT': 2, 'Ngày': pd.to_datetime('2025-01-03'), 'MaHS': 'HS002', 'Loại': 'Vi phạm', 'Nội dung': 'Đi học muộn', 'Điểm': 2, 'Tuần': 1},
                {'STT': 3, 'Ngày': pd.to_datetime('2025-01-16'), 'MaHS': 'HS001', 'Loại': 'Vi phạm', 'Nội dung': 'Quên vở', 'Điểm': 2, 'Tuần': 3},
                {'STT': 4, 'Ngày': pd.to_datetime('2025-01-16'), 'MaHS': 'HS001', 'Loại': 'Vi phạm', 'Nội dung': 'Không làm bài tập', 'Điểm': 5, 'Tuần': 3},
                {'STT': 5, 'Ngày': pd.to_datetime('2025-01-17'), 'MaHS': 'HS001', 'Loại': 'Vi phạm', 'Nội dung': 'Đi học muộn', 'Điểm': 2, 'Tuần': 3},
                {'STT': 6, 'Ngày': pd.to_datetime('2025-01-18'), 'MaHS': 'HS001', 'Loại': 'Vi phạm', 'Nội dung': 'Không trực nhật', 'Điểm': 5, 'Tuần': 3},
                {'STT': 7, 'Ngày': pd.to_datetime('2025-01-16'), 'MaHS': 'HS001', 'Loại': 'Hoạt động', 'Nội dung': 'Đạt điểm 10', 'Điểm': 5, 'Tuần': 3},
                {'STT': 8, 'Ngày': pd.to_datetime('2025-01-17'), 'MaHS': 'HS001', 'Loại': 'Hoạt động', 'Nội dung': 'Giúp đỡ bạn bè', 'Điểm': 3, 'Tuần': 3},
                {'STT': 9, 'Ngày': pd.to_datetime('2025-01-18'), 'MaHS': 'HS001', 'Loại': 'Hoạt động', 'Nội dung': 'Tham gia CLB', 'Điểm': 5, 'Tuần': 3}
            ]
            st.session_state['df_logs'] = pd.DataFrame(logs_data)
            st.session_state['df_logs'].to_csv("logs.csv", index=False)

    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = 'dashboard'
    if 'selected_student_id' not in st.session_state:
        st.session_state['selected_student_id'] = None
        

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
            
            # Logic Cập nhật Session State khi sửa/xóa dưới bảng

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
def build_behavior_dataset(ma_hs, week_selected):
    df_logs = st.session_state['df_logs'].copy()
    
    # 1. Chuẩn bị DataFrame logs
    df_logs['Ngày'] = pd.to_datetime(df_logs['Ngày'], errors='coerce') 
    df_logs = df_logs.dropna(subset=['Ngày'])
    df_logs = df_logs[df_logs['MaHS'] == ma_hs].copy()
    
    # 2. Tạo 7 ngày trong tuần được chọn
    try:
        # Tìm ngày đầu tiên của tuần (Giả sử năm 2025)
        first_day_of_week = pd.to_datetime(f'2025-W{week_selected}-1', format='%G-W%V-%u')
    except ValueError:
        return pd.DataFrame() 

    week_dates = pd.date_range(first_day_of_week, periods=7, freq='D')
    
    # Khởi tạo dataset 7 ngày với điểm mặc định
    dataset = pd.DataFrame({'Ngày': week_dates})
    dataset['Điểm Vi phạm'] = 0.0
    dataset['Điểm Hoạt động'] = 0.0
    dataset['Điểm Hạnh kiểm'] = 90.0 # Mặc định 90

    # 3. Lọc nhật ký và tổng hợp
    logs_week = df_logs[df_logs['Tuần'] == week_selected]

    if not logs_week.empty:
        daily_scores = logs_week.groupby(['Ngày', 'Loại'])['Điểm'].sum().unstack(fill_value=0).reset_index()

        # Đảm bảo có cả hai cột 'Vi phạm' và 'Hoạt động'
        for col in ['Vi phạm', 'Hoạt động']:
            if col not in daily_scores.columns:
                daily_scores[col] = 0

        # Đổi tên cột để merge an toàn
        daily_scores = daily_scores.rename(columns={'Vi phạm': 'Điểm Vi phạm_new', 'Hoạt động': 'Điểm Hoạt động_new'})
        
        # 4. Merge daily_scores vào dataset 7 ngày (Left Join để giữ 7 ngày)
        dataset = dataset.merge(daily_scores[['Ngày', 'Điểm Vi phạm_new', 'Điểm Hoạt động_new']], 
                                on='Ngày', 
                                how='left')
        
        # Cập nhật Điểm và Tính Hạnh kiểm
        dataset['Điểm Vi phạm_new'] = dataset['Điểm Vi phạm_new'].fillna(0)
        dataset['Điểm Hoạt động_new'] = dataset['Điểm Hoạt động_new'].fillna(0)
        
        # Ghi đè điểm Vi phạm/Hoạt động mặc định (0) bằng điểm mới
        dataset['Điểm Vi phạm'] = dataset['Điểm Vi phạm_new']
        dataset['Điểm Hoạt động'] = dataset['Điểm Hoạt động_new']
        dataset['Điểm Hạnh kiểm'] = 90 + dataset['Điểm Hoạt động'] - dataset['Điểm Vi phạm']
        
        # Xóa các cột tạm thời
        dataset = dataset.drop(columns=['Điểm Vi phạm_new', 'Điểm Hoạt động_new'])

    # 5. Đặt index kiểu Datetime cho Altair/Resample
    dataset = dataset.set_index('Ngày')

    return dataset

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

def display_core_analysis(data_df, selected_freq, week_selected=None):
    cols = ['Điểm Vi phạm', 'Điểm Hoạt động', 'Điểm Hạnh kiểm']

    if data_df.empty:
        st.info("⛔ Không có dữ liệu trong tuần này.")
        return

    df_plot = data_df.copy()
    df_plot = df_plot.sort_index()

    # 1. Xử lý tần suất hiển thị (Aggregation)
    if selected_freq == "Ngày (Day)":
        chart_data = df_plot[cols] 
        x_label = "Ngày"
        x_type = 'T' 
    elif selected_freq == "Tuần (Week)":
        # Aggregate theo tuần và reset index, sau đó đổi tên cột
        chart_data = df_plot[cols].groupby(df_plot.index.isocalendar().week).mean()
        chart_data = chart_data.reset_index() # Cột mới tên là 'week' (từ isocalendar())
        chart_data.rename(columns={'week': 'Ngày'}, inplace=True) # Đổi tên thành 'Ngày' để melt dễ dàng
        
        # Format index sau khi đổi tên
        chart_data['Ngày'] = chart_data['Ngày'].apply(lambda w: f"Tuần {w}")
        chart_data = chart_data.set_index('Ngày') # Đặt lại index là chuỗi 'Tuần x'

        x_label = "Tuần"
        x_type = 'N' # Nominal
    else:  # Tháng
        chart_data = df_plot[cols].resample('M').mean()
        chart_data.index = chart_data.index.strftime('%m/%Y')
        x_label = "Tháng"
        x_type = 'N' # Nominal

    # 2. Tính toán và Hiển thị Score / Xếp loại
    if chart_data.empty:
        st.info("⛔ Không có dữ liệu để phân tích trong khoảng thời gian này.")
        return
        
    # FIX: Dùng average (mean) của Hạnh kiểm để tính Xếp loại.
    current_score = chart_data['Điểm Hạnh kiểm'].mean().round(1) 

    if current_score >= 90:
        behavior_class, color = "A - Tốt", "#4CAF50"
    elif current_score >= 80:
        behavior_class, color = "B - Khá", "#FF9800"
    else:
        behavior_class, color = "C - Cần Cải Thiện", "#FF4B4B"

    st.markdown(
        f"**Xếp loại Hạnh kiểm:** <span style='color:{color}; font-size:24px;'>{behavior_class}</span>",
        unsafe_allow_html=True
    )
    st.metric(label=f"Điểm Hạnh kiểm ({x_label} hiện tại)", value=f"{current_score:.1f}")

    # 3. Biểu đồ Altair
    # Luôn reset index để cột Ngày/Tuần/Tháng xuất hiện với tên là 'Ngày'
    chart_data_long = chart_data.reset_index().melt(
        # FIX: Dùng tên cột index mới là 'Ngày'
        'Ngày', 
        var_name='Loại Điểm', 
        value_name='Điểm số'
    )
    
    # Mã hóa trục X
    if x_type == 'T':
        x_encoding = alt.X('Ngày:T', title=x_label) 
    else:
        x_encoding = alt.X('Ngày:N', title=x_label, sort=None) 
        chart_data_long['Ngày'] = chart_data_long['Ngày'].astype(str) 

    selection = alt.selection_point(fields=['Loại Điểm'], bind='legend')
    
    chart = (
        alt.Chart(chart_data_long)
        .mark_line(point=True, strokeWidth=3)
        .encode(
            x=x_encoding,
            y=alt.Y('Điểm số:Q', title=None),
            color='Loại Điểm:N',
            opacity=alt.condition(selection, alt.value(1), alt.value(0.2)),
            tooltip=['Ngày:N', 'Loại Điểm', 'Điểm số:Q']
        )
        .add_params(selection)
        .interactive()
    )
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

    col1, col2, col3 = st.columns([2,3,2.5])
    with col1:
        st.header("1. Hồ sơ")
        selected_student_str = st.selectbox("Học sinh:", student_options_list, index=default_index)
        ma_hs = selected_student_str.split('(')[1].replace(')', '')
        st.session_state['selected_student_id'] = ma_hs

        week_selected = st.number_input("Chọn Tuần (Năm 2025):", min_value=1, max_value=52, value=3)

        info = df_students[df_students['MaHS'] == ma_hs].iloc[0]
        st.markdown(f"**Họ tên:** {info['Họ và tên']}"); st.markdown(f"**Lớp:** {info['Lớp']}"); st.markdown(f"**Ngày sinh:** {info['Ngày sinh']}")

    with col2:
        st.header("2. Phân tích Cốt lõi")
        selected_freq = st.selectbox("Tần suất:", ["Ngày (Day)", "Tuần (Week)", "Tháng (Month)"])
        data_chart = build_behavior_dataset(ma_hs, week_selected)
        display_core_analysis(data_chart, selected_freq, week_selected=week_selected)

    with col3:
        st.header("3. Đề xuất")
        if not data_chart.empty:
            suggestions = [
                "Học sinh đang có xu hướng hoạt động tốt, nên tăng cường giao nhiệm vụ nhóm.",
                "Nên khuyến khích học sinh tham gia các hoạt động ngoại khóa để phát triển kỹ năng mềm.",
                "Học sinh có dấu hiệu giảm vi phạm, cần tiếp tục duy trì nề nếp hiện tại.",
                "Khuyến nghị giáo viên trao đổi thêm để hỗ trợ học sinh phát huy điểm mạnh.",
                "Học sinh đang có tiến bộ tích cực, nên khen thưởng nhỏ để thúc đẩy thêm động lực.",
                "Nên khuyến khích học sinh tham gia CLB hoặc đội nhóm để giao tiếp nhiều hơn.",
                "Học sinh có chỉ số hành vi ổn định, đề xuất tăng cường các hoạt động trải nghiệm.",
                "Dấu hiệu cho thấy học sinh có thể đảm nhận một vai trò trong nhóm học tập.",
                "Học sinh nên cân bằng giữa học tập và sinh hoạt để duy trì phong độ."
            ]
            ai_suggestion = random.choice(suggestions)
            st.success(f"🤖 AI: Đề xuất: {ai_suggestion} (Dự kiến tương lai)")


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









