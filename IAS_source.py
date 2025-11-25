import streamlit as st
import pandas as pd
import numpy as np
import datetime
import altair as alt

# --- CSS Tùy Chỉnh Nâng Cao ---
st.markdown("""
<style>
/* 1. Cấu trúc trang (Giữ nguyên) */
div.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    padding-left: 5rem;
    padding-right: 5rem;
}

/* 2. Tiêu đề Selectbox (Màu Xanh Lá, In đậm) */
.stSelectbox label {
    font-weight: bold;
    color: #4CAF50;
    font-size: 1.25rem !important; 
}

/* --- KHÔI PHỤC MÀU SẮC DỄ NHÌN --- */

/* Trạng thái BÌNH THƯỜNG: Viền Trắng Sáng (thay vì xám tối) */
div[data-testid="stSelectbox"] div[role="combobox"] {
    border: 1px solid #fafafa; /* Màu trắng sáng dễ nhìn */
    border-radius: 0.5rem;
    background-color: transparent; /* Hoặc để màu nền mặc định */
}

/* Trạng thái HOVER (Lia chuột): Viền Xanh Lá */
div[data-testid="stSelectbox"] div[role="combobox"]:hover {
    border-color: #4CAF50 !important; 
    cursor: pointer;
}

/* Trạng thái FOCUS (Đang chọn): Viền Xanh (Thay thế hoàn toàn màu Đỏ) */
div[data-testid="stSelectbox"] div[role="combobox"]:focus-within {
    border-color: #4CAF50 !important; /* Đổi màu đỏ thành xanh */
    box-shadow: 0 0 0 0.2rem rgba(76, 175, 80, 0.25) !important; /* Vầng sáng xanh */
}

/* Mũi tên sổ xuống: Màu trắng (hoặc xanh) cho dễ nhìn */
div[data-testid="stSelectbox"] svg {
    fill: #fafafa !important; 
}

/* --- CÁC PHẦN KHÁC --- */

/* Viền Bảng Dữ liệu: Cũng dùng màu trắng sáng cho đồng bộ */
.stDataFrame {
    border: 1px solid #fafafa; 
}

/* Nút bấm */
.stButton button {
    border: 1px solid #4CAF50;
}
</style>
""", unsafe_allow_html=True)

# --- Dữ liệu Mẫu Giả lập ---
student_list = ["Nguyễn Văn A (Mã 001)", "Trần Thị B (Mã 002)", "Lê Văn C (Mã 003)"]

# Hàm giả lập một tập dữ liệu hành vi mẫu
@st.cache_data
def generate_behavior_data(student_id):
    N = 50 # Số ngày theo dõi
    dates = pd.date_range(start='2025-10-01', periods=N, freq='D')
    
    # --- Logic Xu hướng Cụ thể cho từng học sinh ---
    
    if "Nguyễn Văn A" in student_id:
        # Xu hướng Tốt lên: Vi phạm giảm dần, Tích cực tăng dần
        violation_trend = np.linspace(15, 2, N)  # Vi phạm từ 15 điểm xuống 2 điểm
        positive_trend = np.linspace(5, 15, N)   # Tích cực từ 5 điểm lên 15 điểm
        
    elif "Trần Thị B" in student_id:
        # Xu hướng Đi xuống: Vi phạm tăng dần, Tích cực giảm
        violation_trend = np.linspace(5, 20, N)
        positive_trend = np.linspace(10, 2, N)
        
    else: # Lê Văn C
        # Ổn định
        violation_trend = np.full(N, 8) 
        positive_trend = np.full(N, 8)
        
    # Thêm nhiễu ngẫu nhiên (Noise) để dữ liệu trông tự nhiên hơn
    # np.clip để đảm bảo điểm không bị âm hoặc quá vô lý
    violation_data = np.clip(violation_trend + np.random.normal(0, 2, N), 0, 30).round(1)
    positive_data = np.clip(positive_trend + np.random.normal(0, 2, N), 0, 20).round(1)

    # --- CÔNG THỨC TÍNH ĐIỂM HẠNH KIỂM ---
    # Điểm Gốc = 90
    base_score = 90
    conduct_score = base_score + positive_data - violation_data
    
    # Giới hạn điểm hạnh kiểm (ví dụ: tối đa 100 hoặc 110 tùy quy định, ở đây tôi để thả nổi nhưng ko dưới 0)
    conduct_score = np.clip(conduct_score, 0, 100)

    data = {
        'Ngày': dates,
        'Điểm Vi phạm': violation_data,
        'Điểm Tích cực': positive_data,
        'Điểm Hạnh kiểm': conduct_score
    }
    df = pd.DataFrame(data)
    df = df.set_index('Ngày')
    return df

# --- Hàm Xử lý và Trực quan hóa ---
# Định nghĩa công thức tính điểm
def calculate_score(df):
    # Tính điểm trung bình dựa trên cột Điểm Hạnh kiểm
    score = df['Điểm Hạnh kiểm'].mean().round(1)
    return score

def display_core_analysis(data_df, selected_freq):
    # --- Logic Nhóm Dữ liệu ---
    # Chúng ta cần tính trung bình cho cả 3 cột dữ liệu mới
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
        
    # --- 1. Xác định mốc thời gian (GIỮ NGUYÊN) ---
    current_date = data_df.index.max() 
    first_day_of_current_month = current_date.replace(day=1)
    last_day_of_last_month = first_day_of_current_month - datetime.timedelta(days=1)
    
    # --- 2. Tìm Ngày Gốc (Base Day) ---
    data_before_current_month = data_df[data_df.index <= last_day_of_last_month]
    score_last_day = 0 
    last_day_found = None
    
    if not data_before_current_month.empty:
        last_day_in_last_month = data_before_current_month.index.max()
        data_base_day = data_df[data_df.index == last_day_in_last_month]
        score_last_day = calculate_score(data_base_day)
        last_day_found = last_day_in_last_month.strftime('%d/%m')
    else:
        st.error("Không tìm thấy dữ liệu tháng trước để so sánh!")
        
    # --- 3. Tính Điểm Ngày Hiện tại ---
    data_current_day = data_df[data_df.index == current_date]
    score_current_day = calculate_score(data_current_day)
    
    # --- 4. Tính toán sự Chênh lệch ---
    delta_score = (score_current_day - score_last_day).round(1)
    mean_score = score_current_day 
    
    # Phân loại Hành vi (Cập nhật theo thang điểm 90)
    if mean_score >= 90:
        behavior_class = "A - Tốt"
        color = "#4CAF50" # Xanh lá
    elif mean_score >= 80:
        behavior_class = "B - Khá"
        color = "#FF9800" # Cam
    else:
        behavior_class = "C - Cần Cải Thiện"
        color = "#FF4B4B" # Đỏ
        
    # --- 5. Cập nhật st.metric ---
    st.markdown(f"**Xếp loại Hạnh kiểm:** <span style='color:{color}; font-size:24px;'>**{behavior_class}**</span>", 
                unsafe_allow_html=True)
    
    st.metric(label=f"Điểm Hạnh kiểm ({freq_label} Hiện tại)", 
              value=f"{mean_score}", 
              delta=f"{delta_score} điểm so với {last_day_found}", 
              delta_color="normal")
    
    st.markdown(f"*(Điểm gốc ngày {last_day_found}: {score_last_day})*")
    
    # --- 6. BIỂU ĐỒ 3 ĐƯỜNG MÀU (ALTAIR) ---
    st.subheader(f"Biểu đồ Xu hướng ({freq_label})")
    
    # Chuyển đổi dữ liệu sang dạng Long Format cho Altair
    chart_data_long = chart_data.reset_index().melt(
        'Ngày', var_name='Loại Điểm', value_name='Điểm số'
    )

    # 1. TẠO TƯƠNG TÁC (SELECTION)
    # bind='legend': Cho phép click vào chú thích để chọn
    selection = alt.selection_point(fields=['Loại Điểm'], bind='legend')

    # Vẽ biểu đồ Altair
    chart = alt.Chart(chart_data_long).mark_line(point=True, strokeWidth=3).encode(
        x=alt.X('Ngày:T', title=None, axis=alt.Axis(format="%d/%m")), 
        y=alt.Y('Điểm số:Q', title=None, scale=alt.Scale(zero=False)),
        
        # --- MÀU SẮC ---
        color=alt.Color('Loại Điểm:N',
            scale=alt.Scale(
                domain=['Điểm Vi phạm', 'Điểm Tích cực', 'Điểm Hạnh kiểm'],
                range=['#FF4B4B', '#2E8B57', '#1E90FF'] 
            ),
            # LƯU Ý: Không thêm tham số 'select' vào đây nữa
            legend=alt.Legend(title="Chú thích (Click để lọc)", orient="bottom")
        ),
        
        # 2. ĐIỀU KIỆN ẨN/HIỆN
        # Nếu được chọn (hoặc chưa chọn gì) -> Hiện rõ (1)
        # Nếu không được chọn -> Mờ đi (0.1)
        opacity=alt.condition(selection, alt.value(1), alt.value(0.1)),
        
        tooltip=[
            alt.Tooltip('Ngày:T', title='Thời gian', format='%d/%m/%Y'),
            alt.Tooltip('Loại Điểm:N'),
            alt.Tooltip('Điểm số:Q', format='.1f')
        ]
    ).add_params(
        selection # 3. THÊM TƯƠNG TÁC VÀO BIỂU ĐỒ
    ).interactive()
    
    st.altair_chart(chart, use_container_width=True)
    
# --- Hàm Dự đoán và Đề xuất ---
def display_recommendations(student_id):
    st.subheader("Dự đoán Xu hướng Tương lai")
    
    # 1. Logic Dự đoán Nguy cơ
    if "Nguyễn Văn A" in student_id:
        risk = "Thấp"
        pred_text = "Hành vi đang có xu hướng cải thiện mạnh mẽ. Nguy cơ thấp. Hệ thống dự đoán điểm số sẽ vượt 80 trong tháng tới."
        
    elif "Trần Thị B" in student_id:
        risk = "Trung bình"
        pred_text = "Cần theo dõi chặt chẽ chỉ số Tập trung. Xu hướng đang giảm nhẹ. Hệ thống dự đoán có thể xuất hiện hành vi kém tập trung 2-3 lần/tuần."
        
    else: # Lê Văn C
        risk = "Thấp-Trung bình"
        pred_text = "Hành vi ổn định, nhưng thiếu đột phá. Cần thúc đẩy thêm sự tương tác."

    st.markdown(f"**Nguy cơ Đánh giá:** <span style='color:orange;'>**{risk}**</span>", unsafe_allow_html=True)
    st.info(pred_text)
    
    st.markdown("---")
    
    # 2. Logic Đề xuất Cá nhân hóa
    st.subheader("Đề xuất Hành động (Nudging)")
    
    if "Trần Thị B" in student_id:
        st.warning("🚨 **Khuyến nghị khẩn cấp:** Cần phân bổ thời gian nghỉ ngơi hợp lý hơn để **cải thiện mức độ tập trung** vào giữa tháng.")
        st.markdown("*Gợi ý: Tăng thời gian nghỉ giữa giờ học lên 5 phút.*")
    elif "Nguyễn Văn A" in student_id:
        st.success("✅ **Khuyến nghị:** Duy trì các hoạt động tương tác nhóm tích cực để **giữ vững phong độ** hiện tại.")
        st.markdown("*Gợi ý: Tham gia thêm 1 dự án ngoại khóa.*")
    else:
        st.info("💡 **Khuyến nghị:** Tạo thêm cơ hội tham gia các hoạt động cần **sự chủ động** để thúc đẩy Tương tác Tích cực.")
        st.markdown("*Gợi ý: Đăng ký làm trưởng nhóm cho dự án sắp tới.*")
        
# Thiết lập Tiêu đề và Cấu trúc
st.set_page_config(layout="wide")

st.title("💡 HỆ THỐNG ĐÁNH GIÁ HÀNH VI CÁ NHÂN (IAS)")
st.caption("Demo dành cho Ban Giám khảo Cuộc thi KHKT")

# Thiết lập Cấu trúc 3 cột chính
col1, col2, col3 = st.columns([2, 3, 2.5])

# Nội dung cho cột 1
with col1:
    st.header("1. Dữ liệu Đầu vào")
    
    # Widget tương tác 1: Chọn Đối tượng
    selected_student = st.selectbox(
        "Chọn Đối tượng Phân tích",
        student_list,
        index=0 # Chọn học sinh đầu tiên mặc định
    )
    
    # Widget tương tác 2: Nút Tải dữ liệu giả lập
    if st.button("Tải Dữ liệu Hành vi Mẫu"):
        st.session_state['data_loaded'] = True
        st.session_state['current_student'] = selected_student
        st.success(f"Đã tải dữ liệu của **{selected_student}**.")

    st.markdown("---")
    
    # Hiển thị dữ liệu khi đã được tải
    if 'data_loaded' in st.session_state and st.session_state['data_loaded']:
        st.subheader("Bảng Dữ liệu Đã Chọn")
        
        # Gọi hàm giả lập dữ liệu
        data_df = generate_behavior_data(st.session_state['current_student'])
        
        # Hiển thị 5 dòng dữ liệu đầu tiên
        st.dataframe(data_df) 
        st.markdown(f"*(Tổng cộng {len(data_df)} số ngày theo dõi, đánh giá)*")
    else:
        st.info("Vui lòng chọn đối tượng và nhấn nút 'Tải Dữ liệu Mẫu'.")
            
# Nội dung cho cột 2
with col2:
    st.header("2. Phân tích Hành vi Cốt lõi")
    
    # 1. Thanh chọn Tần suất 
    selected_freq = st.selectbox(
        label="Xu hướng theo Tần suất:",
        options=["Ngày (Day)", "Tuần (Week)", "Tháng (Month)"],
        index=0
    )
    
    # Chỉ hiển thị phân tích khi dữ liệu đã được tải
    if 'data_loaded' in st.session_state and st.session_state['data_loaded']:
        with st.container(height=550, border=False):
            # Lấy dữ liệu đã tải
            data_df = generate_behavior_data(st.session_state['current_student'])
            
            # Gọi hàm xử lý và hiển thị theo tần suất đã chọn
            display_core_analysis(data_df, selected_freq) 
        
    else:
        st.warning("👈 Vui lòng tải dữ liệu mẫu ở cột bên trái để xem kết quả phân tích.")
    
# Nội dung cho cột 3
with col3:
    st.header("3. Đề xuất & Dự đoán")
    
    if 'data_loaded' in st.session_state and st.session_state['data_loaded']:
        with st.container(height=550, border=False):
            # Lấy tên học sinh hiện tại
            current_student = st.session_state['current_student']
            
            # Gọi hàm hiển thị dự đoán và đề xuất
            display_recommendations(current_student)
            
    else:
        st.warning("👈 Vui lòng tải dữ liệu mẫu để xem đề xuất cá nhân hóa.")

# Phần Footer đơn giản

st.sidebar.success("IAS Demo sẵn sàng.")


