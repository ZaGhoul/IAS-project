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
                {'STT': 3, 'Ngày': pd.to_datetime('2025-01-16'), 'MaHS': 'HS001', 'Loại': 'Vi phạm', 'Nội dung': 'Quên vở', 'Điểm': 2, 'Tuần': 3}
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
    
    # ===================
    # Bảng dữ liệu + Bộ lọc tuần
    # ===================
    with col_ctrl:
        st.subheader("Cấu hình")
        table_option = st.radio(
            "Chọn Bảng Dữ liệu:",
            ["👨‍🎓 Học sinh", "📝 Nhật ký Hành vi", "⚠️ Danh mục Vi phạm", "🏆 Danh mục Hoạt động"]
        )
        st.markdown("---")
        
        selected_week = 3
        if table_option in ["👨‍🎓 Học sinh", "📝 Nhật ký Hành vi"]:
            st.info("Bộ lọc Thời gian")
            selected_week = st.number_input("Chọn Tuần (Năm 2025):", min_value=1, max_value=52, value=3)
            st.caption(f"Dữ liệu Tuần {selected_week}")
            st.session_state['selected_week'] = selected_week

    with col_data:
        # ===================
        # A. Bảng Học sinh
        # ===================
        if table_option == "👨‍🎓 Học sinh":
            st.subheader(f"Danh sách Học sinh & Điểm Tuần {selected_week}")
            df_students = st.session_state['df_students_master'].copy()
            df_logs = st.session_state['df_logs']

            # Tính điểm tuần
            logs_week = df_logs[df_logs['Tuần'] == selected_week]
            scores = logs_week.groupby(['MaHS', 'Loại'])['Điểm'].sum().unstack(fill_value=0)
            if not scores.empty:
                for col in ['Hoạt động', 'Vi phạm']:
                    if col not in scores.columns: scores[col] = 0
                df_students = df_students.merge(scores, on='MaHS', how='left').fillna(0)
            else:
                df_students['Hoạt động'] = 0
                df_students['Vi phạm'] = 0

            df_students['Hạnh kiểm'] = 90 + df_students['Hoạt động'] - df_students['Vi phạm']

            st.dataframe(
                df_students, use_container_width=True, hide_index=True,
                column_config={
                    "Hạnh kiểm": st.column_config.ProgressColumn("Hạnh kiểm", format="%d", min_value=0, max_value=120)
                }
            )

            # ===================
            # B. Bảng Nhật ký Hành vi
            # ===================
            elif table_option == "📝 Nhật ký Hành vi":
                st.subheader(f"📝 Quản lý Nhật ký Hành vi Tuần {selected_week}")
                df_logs = st.session_state['df_logs'].copy()
            
                # --- Thêm nhật ký mới ---
                st.markdown("##### ➕ Thêm Nhật ký Mới")
                df_students = st.session_state['df_students_master']
                hs_dict = dict(zip(df_students['MaHS'], df_students['Họ và tên']))
                new_mahs = st.selectbox("Học sinh", list(hs_dict.keys()), format_func=lambda x: f"{hs_dict[x]} ({x})")
                new_type = st.selectbox("Loại hành vi", ["Vi phạm", "Hoạt động"])
                content_source = st.session_state['df_violations'] if new_type=='Vi phạm' else st.session_state['df_achievements']
                content_col = 'Tên Vi phạm' if new_type=='Vi phạm' else 'Tên Hoạt động'
                new_content = st.selectbox("Nội dung chi tiết", content_source[content_col].tolist())
                auto_score = int(content_source.loc[content_source[content_col]==new_content, 'Điểm'].values[0])
                new_score = st.number_input("Điểm", value=auto_score)
                new_date = st.date_input("Ngày", datetime.date.today())
                new_week = new_date.isocalendar()[1]
            
                if st.button("💾 Lưu vào CSDL"):
                    # Tạo STT
                    next_stt = df_logs['STT'].max() + 1 if not df_logs.empty else 1
                    new_row = {
                        'STT': next_stt,
                        'Ngày': pd.Timestamp(new_date),
                        'MaHS': str(new_mahs),
                        'Loại': str(new_type),
                        'Nội dung': str(new_content),
                        'Điểm': float(new_score),
                        'Tuần': int(new_week)
                    }
                    df_logs = pd.concat([df_logs, pd.DataFrame([new_row])], ignore_index=True)
                    st.session_state['df_logs'] = df_logs
                    # Lưu ra CSV để reload không mất
                    df_logs.to_csv("logs.csv", index=False)
                    st.success("Đã thêm mới thành công!")
                    st.experimental_rerun()
            
                # --- Hiển thị bảng nhật ký ---
                logs_week = df_logs[df_logs['Tuần'] == selected_week].copy()
            
                # ---- Fix kiểu dữ liệu cho Streamlit ----
                logs_week['STT'] = logs_week['STT'].astype(int)
                logs_week['MaHS'] = logs_week['MaHS'].astype(str)
                logs_week['Loại'] = logs_week['Loại'].astype(str)
                logs_week['Nội dung'] = logs_week['Nội dung'].astype(str)
                logs_week['Điểm'] = logs_week['Điểm'].fillna(0).astype(float)
                logs_week['Tuần'] = logs_week['Tuần'].astype(int)
                logs_week['Ngày'] = pd.to_datetime(logs_week['Ngày']).dt.strftime('%Y-%m-%d')
            
                st.dataframe(logs_week, use_container_width=True)


        # ===================
        # C. Danh mục Vi phạm / Hoạt động
        # ===================
        elif table_option == "⚠️ Danh mục Vi phạm":
            st.subheader("Quản lý Danh mục Vi phạm")
            edited_vp = st.data_editor(st.session_state['df_violations'], num_rows="dynamic", use_container_width=True)
            if not edited_vp.equals(st.session_state['df_violations']):
                st.session_state['df_violations'] = edited_vp
                st.experimental_rerun()

        elif table_option == "🏆 Danh mục Hoạt động":
            st.subheader("Quản lý Danh mục Hoạt động")
            edited_tc = st.data_editor(st.session_state['df_achievements'], num_rows="dynamic", use_container_width=True)
            if not edited_tc.equals(st.session_state['df_achievements']):
                st.session_state['df_achievements'] = edited_tc
                st.experimental_rerun()


# ==========================================
# 4. LOGIC TRANG 2: DASHBOARD IAS
# ==========================================
def build_behavior_dataset(ma_hs, week_selected=None):
    logs_df = st.session_state['df_logs'].copy()
    logs_df = logs_df[logs_df['MaHS'] == ma_hs]

    if logs_df.empty:
        # Không có nhật ký, tạo DataFrame trống với index theo tuần nếu cần
        start_date = pd.Timestamp('2025-01-01')
        end_date = pd.Timestamp('2025-12-31')
        date_index = pd.date_range(start_date, end_date)
        df = pd.DataFrame(index=date_index, columns=['Điểm Vi phạm', 'Điểm Hoạt động', 'Điểm Hạnh kiểm'])
        df.fillna(0, inplace=True)
        df['Điểm Hạnh kiểm'] = 90
        return df

    # Đặt cột Ngày làm index
    logs_df['Ngày'] = pd.to_datetime(logs_df['Ngày'])
    logs_df.set_index('Ngày', inplace=True)
    logs_df.sort_index(inplace=True)

    # Lấy dải ngày cần vẽ
    if week_selected:
        week_dates = pd.date_range(
            start=logs_df.index.min().normalize(),
            end=logs_df.index.max().normalize()
        )
        # Chỉ lấy tuần được chọn
        week_dates = [d for d in week_dates if d.isocalendar().week == week_selected]
        if not week_dates:
            week_dates = pd.date_range(start=logs_df.index.min(), end=logs_df.index.max())
    else:
        week_dates = pd.date_range(start=logs_df.index.min(), end=logs_df.index.max())

    df = pd.DataFrame(index=week_dates, columns=['Điểm Vi phạm', 'Điểm Hoạt động', 'Điểm Hạnh kiểm'])
    df.fillna(0, inplace=True)
    df['Điểm Hạnh kiểm'] = 90  # mặc định 90

    for d in week_dates:
        day_logs = logs_df[logs_df.index == d]
        if not day_logs.empty:
            vi_pham = day_logs[day_logs['Loại'] == 'Vi phạm']['Điểm'].sum()
            hoat_dong = day_logs[day_logs['Loại'] == 'Hoạt động']['Điểm'].sum()
            df.at[d, 'Điểm Vi phạm'] = vi_pham
            df.at[d, 'Điểm Hoạt động'] = hoat_dong
            df.at[d, 'Điểm Hạnh kiểm'] = 90 - vi_pham + hoat_dong

    return df

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
    """
    Hiển thị biểu đồ hành vi học sinh.
    - data_df: DataFrame có index là Ngày, các cột: Điểm Vi phạm, Điểm Hoạt động, Điểm Hạnh kiểm
    - selected_freq: "Ngày (Day)", "Tuần (Week)", "Tháng (Month)"
    - week_selected: số tuần nếu muốn lọc tuần cụ thể
    """
    cols = ['Điểm Vi phạm', 'Điểm Hoạt động', 'Điểm Hạnh kiểm']

    if data_df.empty:
        st.info("⛔ Không có dữ liệu trong tuần này.")
        return

    chart_data = data_df.copy()

    # --- Lọc tuần nếu có ---
    if week_selected is not None:
        # Lấy đầu và cuối tuần
        first_day_of_week = pd.to_datetime(f'2025-01-01') + pd.to_timedelta((week_selected-1)*7, unit='D')
        last_day_of_week = first_day_of_week + pd.Timedelta(days=6)
        # Lọc các ngày trong tuần đó
        all_days = pd.date_range(start=first_day_of_week, end=last_day_of_week)
        chart_data = chart_data.reindex(all_days, fill_value=0)
        chart_data.index.name = 'Ngày'
        # Nếu ngày không có log, điểm hạnh kiểm = 90
        chart_data['Điểm Hạnh kiểm'] = chart_data['Điểm Hạnh kiểm'].replace(0, 90)
    else:
        chart_data.index.name = 'Ngày'
        chart_data['Điểm Hạnh kiểm'] = chart_data['Điểm Hạnh kiểm'].replace(0, 90)

    # --- Resample nếu tần suất là Tuần/Tháng ---
    if selected_freq == "Tuần (Week)":
        chart_data = chart_data.resample('D').asfreq()  # đảm bảo tất cả ngày có
        freq_label = f"Tuần {week_selected}"
    elif selected_freq == "Tháng (Month)":
        chart_data = chart_data.resample('M').mean()
        freq_label = chart_data.index.max().strftime("%B %Y")
    else:
        freq_label = "Ngày"

    # --- Lấy ngày cuối cùng để xếp loại ---
    current_day = chart_data.index.max()
    mean_score = chart_data.loc[current_day, 'Điểm Hạnh kiểm']

    if mean_score >= 90:
        behavior_class = "A - Tốt"; color = "#4CAF50"
    elif mean_score >= 80:
        behavior_class = "B - Khá"; color = "#FF9800"
    else:
        behavior_class = "C - Cần Cải Thiện"; color = "#FF4B4B"

    st.markdown(f"**Xếp loại Hạnh kiểm:** <span style='color:{color}; font-size:24px;'>**{behavior_class}**</span>", unsafe_allow_html=True)
    st.metric(label=f"Điểm Hạnh kiểm ({freq_label} hiện tại)", value=f"{mean_score}")

    # --- Chuẩn bị dữ liệu dài để vẽ Altair ---
    chart_data_reset = chart_data.reset_index()
    chart_data_long = chart_data_reset.melt(
        id_vars='Ngày',
        value_vars=cols,
        var_name='Loại Điểm',
        value_name='Điểm số'
    )

    selection = alt.selection_point(fields=['Loại Điểm'], bind='legend')
    chart = (
        alt.Chart(chart_data_long)
        .mark_line(point=True, strokeWidth=3)
        .encode(
            x=alt.X('Ngày:T', title=None, axis=alt.Axis(format="%d/%m")),
            y=alt.Y('Điểm số:Q', title=None),
            color='Loại Điểm:N',
            opacity=alt.condition(selection, alt.value(1), alt.value(0.2)),
            tooltip=['Ngày:T', 'Loại Điểm', 'Điểm số']
        )
        .add_params(selection)
        .interactive()
    )
    st.subheader(f"Biểu đồ Xu hướng ({freq_label})")
    st.altair_chart(chart, use_container_width=True)



def render_ias_dashboard_page():
    st.title("💡 PHÂN TÍCH HÀNH VI CÁ NHÂN (IAS)")
    
    df_students = st.session_state['df_students_master']
    student_options_list = df_students.apply(lambda x: f"{x['Họ và tên']} ({x['MaHS']})", axis=1).tolist()
    default_index = 0

    # --- Lấy học sinh đã chọn trước đó ---
    if st.session_state.get('selected_student_id'):
        ma_hs_target = st.session_state['selected_student_id']
        found_row = df_students[df_students['MaHS'] == ma_hs_target]
        if not found_row.empty:
            target_string = f"{found_row.iloc[0]['Họ và tên']} ({found_row.iloc[0]['MaHS']})"
            if target_string in student_options_list:
                default_index = student_options_list.index(target_string)

    col1, col2, col3 = st.columns([2,3,2.5])

    # --- Cột 1: Hồ sơ ---
    with col1:
        st.header("1. Hồ sơ")
        selected_student_str = st.selectbox("Học sinh:", student_options_list, index=default_index)
        ma_hs = selected_student_str.split('(')[1].replace(')', '')
        st.session_state['selected_student_id'] = ma_hs

        week_selected = st.number_input("Chọn Tuần (Năm 2025):", min_value=1, max_value=52, value=3)

        info = df_students[df_students['MaHS'] == ma_hs].iloc[0]
        st.markdown(f"**Họ tên:** {info['Họ và tên']}")
        st.markdown(f"**Lớp:** {info['Lớp']}")
        st.markdown(f"**Ngày sinh:** {info['Ngày sinh']}")

    # --- Cột 2: Phân tích cốt lõi ---
    with col2:
        st.header("2. Phân tích Cốt lõi")
        selected_freq = st.selectbox("Tần suất:", ["Ngày (Day)", "Tuần (Week)", "Tháng (Month)"])
        # Lấy dữ liệu build_behavior_dataset mới
        data_chart = build_behavior_dataset(ma_hs, week_selected)
        display_core_analysis(data_chart, selected_freq, week_selected=week_selected)

    # --- Cột 3: Đề xuất ---
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








