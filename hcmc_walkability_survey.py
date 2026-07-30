import streamlit as st
import os
import random
import pandas as pd
from datetime import datetime
import uuid

# ==========================================
# CẤU HÌNH ĐƯỜNG DẪN & SỐ CÂU
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "images")
CSV_FILE = os.path.join(BASE_DIR, "responses.csv")

TOTAL_PAIRS_PER_SESSION = 20  # 20 câu/lượt khảo sát (~1 - 1.5 phút)

st.set_page_config(
    page_title="Khảo Sát Đánh Giá Cảm Nhận Không Gian Đi Bộ tại TP.HCM",
    page_icon="🚶‍♂️",
    layout="centered"
)

# Custom CSS cho giao diện nhã nhặn, chuẩn học thuật
st.markdown("""
    <style>
    .main-title {
        color: #1E3A8A;
        font-weight: 700;
        text-align: center;
        font-size: 1.8rem;
        margin-bottom: 20px;
        line-height: 1.3;
    }
    .greeting-box {
        background-color: #F8FAFC;
        border-left: 4px solid #1E3A8A;
        padding: 15px 20px;
        border-radius: 4px;
        margin-bottom: 20px;
        color: #334155;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    </style>
""", unsafe_allow_html=True)


# ==========================================
# XỬ LÝ LƯU KẾT QUẢ VÀO CSV
# ==========================================
def init_csv():
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=[
            "response_id", "user_session_id", "dimension",
            "image_a", "image_b", "chosen_image", "timestamp"
        ])
        df.to_csv(CSV_FILE, index=False)


def save_response(dimension, img_a, img_b, chosen):
    init_csv()
    new_data = pd.DataFrame([{
        "response_id": str(uuid.uuid4())[:8],
        "user_session_id": st.session_state.session_id,
        "dimension": dimension,
        "image_a": img_a,
        "image_b": img_b,
        "chosen_image": chosen,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }])
    new_data.to_csv(CSV_FILE, mode='a', header=False, index=False)


# ==========================================
# BỘ NHỚ TẠM (SESSION STATE)
# ==========================================
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]

if "step" not in st.session_state:
    st.session_state.step = 0

if "current_count" not in st.session_state:
    st.session_state.current_count = 0

if "pair" not in st.session_state:
    st.session_state.pair = None


# ==========================================
# BỐC CẶP ẢNH NGẪU NHIÊN
# ==========================================
def get_random_pair():
    if not os.path.exists(IMAGE_DIR):
        return None, None
    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp')
    images = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(valid_extensions)]

    if len(images) < 2:
        return None, None

    img_a, img_b = random.sample(images, 2)
    return img_a, img_b


# ==========================================
# MÀN HÌNH 1: MÀN HÌNH CHÀO LỄ PHÉP & TRANG TRỌNG
# ==========================================
if st.session_state.step == 0:
    st.markdown("<h1 class='main-title'>Khảo Sát Đánh Giá Cảm Nhận Không Gian Đi Bộ tại TP.HCM</h1>",
                unsafe_allow_html=True)

    st.markdown("""
    <div class='greeting-box'>
        <p><b>Kính chào Thầy/Cô, Anh/Chị và các bạn!</b></p>
        <p>Nhóm nghiên cứu thuộc Trường Đại học Kinh tế TP.HCM (UEH) xin trân trọng gửi lời chào và lời chúc sức khỏe đến quý Thầy/Cô, Anh/Chị cùng các bạn.</p>
        <p>Hiện tại, nhóm đang thực hiện đề tài nghiên cứu về <b>chất lượng môi trường vi khí hậu và cảm nhận không gian đi bộ đô thị tại TP.HCM</b>. Những đánh giá thực tế từ quý vị sẽ là nguồn dữ liệu khoa học vô cùng quý giá, giúp nhóm đề xuất các giải pháp quy hoạch vỉa hè thân thiện, an toàn và nâng cao chất lượng sống cho cộng đồng.</p>
        <hr style='border: 0.5px solid #CBD5E1; margin: 12px 0;'>
        <p><b>📌 Hướng dẫn đóng góp ý kiến:</b></p>
        <ul>
            <li>Khảo sát bao gồm <b>20 lượt so sánh cặp hình ảnh</b> thực tế trên các tuyến đường TP.HCM.</li>
            <li>Ở mỗi câu, xin vui lòng bấm/chạm chọn góc phố mang lại cho quý vị cảm giác <b>An toàn hơn</b> hoặc <b>Thoải mái hơn</b> khi đi bộ.</li>
            <li><b>Thời gian thực hiện:</b> Khoảng <b>1 đến 1.5 phút</b>.</li>
        </ul>
        <p><i>Kính mong nhận được sự hỗ trợ và đóng góp quý báu từ quý Thầy/Cô, Anh/Chị và các bạn!</i></p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚀 Bắt đầu Khảo sát", type="primary", use_container_width=True):
        st.session_state.step = 1
        st.session_state.current_count = 0
        st.session_state.pair = get_random_pair()
        st.rerun()

# ==========================================
# MÀN HÌNH 2: SO SÁNH CẶP (PAIRWISE CHOICE)
# ==========================================
elif st.session_state.step == 1:
    img_a, img_b = st.session_state.pair

    if not img_a or not img_b:
        st.error(f"❌ Không tìm thấy đủ ảnh trong thư mục: `{IMAGE_DIR}`")
        st.stop()

    # Progress bar
    progress = st.session_state.current_count / TOTAL_PAIRS_PER_SESSION
    st.progress(progress)
    st.caption(f"Tiến độ hoàn thành: **Câu {st.session_state.current_count + 1} / {TOTAL_PAIRS_PER_SESSION}**")

    # Xen kẽ 2 tiêu chí đánh giá
    dimension = "An toàn hơn khi đi bộ" if st.session_state.current_count % 2 == 0 else "Thoải mái & Dễ chịu hơn"

    st.markdown(
        f"<h4 style='text-align: center; color: #1E3A8A; margin-bottom: 20px;'>Theo cảm nhận của bạn, góc phố nào cho cảm giác<br><u>{dimension.upper()}</u>?</h4>",
        unsafe_allow_html=True)

    # Hiển thị 2 ảnh
    col1, col2 = st.columns(2)

    with col1:
        st.image(os.path.join(IMAGE_DIR, img_a), use_container_width=True)
        if st.button("👈 Chọn Góc A", key="btn_a", use_container_width=True):
            save_response(dimension, img_a, img_b, chosen=img_a)
            st.session_state.current_count += 1
            if st.session_state.current_count >= TOTAL_PAIRS_PER_SESSION:
                st.session_state.step = 2
            else:
                st.session_state.pair = get_random_pair()
            st.rerun()

    with col2:
        st.image(os.path.join(IMAGE_DIR, img_b), use_container_width=True)
        if st.button("👉 Chọn Góc B", key="btn_b", use_container_width=True):
            save_response(dimension, img_a, img_b, chosen=img_b)
            st.session_state.current_count += 1
            if st.session_state.current_count >= TOTAL_PAIRS_PER_SESSION:
                st.session_state.step = 2
            else:
                st.session_state.pair = get_random_pair()
            st.rerun()

# ==========================================
# MÀN HÌNH 3: HOÀN THÀNH & CẢM ƠN
# ==========================================
elif st.session_state.step == 2:
    st.balloons()
    st.success("🎉 Trân trọng cảm ơn sự đóng góp quý báu của Thầy/Cô, Anh/Chị và các bạn!")
    st.write(
        "Những ý kiến đánh giá này là nguồn dữ liệu vô cùng ý nghĩa giúp nhóm nghiên cứu hoàn thiện đề tài và đóng góp cho sự phát triển của không gian đi bộ đô thị.")

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔄 Thực hiện thêm 1 lượt nữa", use_container_width=True):
            st.session_state.step = 1
            st.session_state.current_count = 0
            st.session_state.pair = get_random_pair()
            st.rerun()
    with col_b:
        if st.button("🛑 Hoàn tất", use_container_width=True):
            st.info("Kính chúc Thầy/Cô, Anh/Chị và các bạn nhiều sức khỏe! Quý vị có thể đóng tab trình duyệt này.")