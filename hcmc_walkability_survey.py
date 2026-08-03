import streamlit as st
import os
import random
import pandas as pd
from datetime import datetime
import uuid
import requests

# ==========================================
# CẤU HÌNH DỮ LIỆU & GOOGLE SHEET WEBHOOK
# ==========================================
# ⚠️ THAY LINK WEBHOOK CỦA BẠN VÀO ĐÂY:
GOOGLE_SHEET_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzZHMKKFx4OSQnZ0nN5zTbqyNxKQ5KYQjO7J3caON6lBGuAcwm0gKhm8uuKh2L4DkKF/exec"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "responses.csv")

sub_image_dir = os.path.join(BASE_DIR, "images")
valid_extensions = ('.jpg', '.jpeg', '.png', '.webp')

if os.path.exists(sub_image_dir) and any(f.lower().endswith(valid_extensions) for f in os.listdir(sub_image_dir)):
    IMAGE_DIR = sub_image_dir
else:
    IMAGE_DIR = BASE_DIR

TOTAL_PAIRS_PER_SESSION = 20

st.set_page_config(
    page_title="Khảo Sát Đánh Giá Cảm Nhận Không Gian Đi Bộ TP.HCM",
    page_icon="🚶‍♂️",
    layout="centered"
)

# Custom CSS
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
# LƯU KẾT QUẢ VÀO GOOGLE SHEET & CSV LOCAL
# ==========================================
def save_response(dimension, img_a, img_b, chosen):
    payload = {
        "response_id": str(uuid.uuid4())[:8],
        "user_session_id": st.session_state.session_id,
        "age": st.session_state.user_age,
        "gender": st.session_state.user_gender,
        "walk_freq": st.session_state.user_walk_freq,
        "dimension": dimension,
        "image_a": img_a,
        "image_b": img_b,
        "chosen_image": chosen,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # 1. Bắn sang Google Sheets
    if GOOGLE_SHEET_WEBHOOK_URL and "THAY_LINK_CUA_BAN_VAO_DAY" not in GOOGLE_SHEET_WEBHOOK_URL:
        try:
            requests.post(GOOGLE_SHEET_WEBHOOK_URL, json=payload, timeout=5)
        except Exception:
            pass

    # 2. Lưu local dự phòng
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=list(payload.keys()))
        df.to_csv(CSV_FILE, index=False)

    new_data = pd.DataFrame([payload])
    new_data.to_csv(CSV_FILE, mode='a', header=False, index=False)


# ==========================================
# KHỞI TẠO BỘ NHỚ TẠM (SESSION STATE)
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
    images = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(valid_extensions)]
    if len(images) < 2:
        return None, None
    return random.sample(images, 2)


# ==========================================
# MÀN HÌNH 1: THÔNG TIN VÀ NHÂN KHẨU HỌC
# ==========================================
if st.session_state.step == 0:
    st.markdown("<h1 class='main-title'>Khảo Sát Đánh Giá Cảm Nhận Không Gian Đi Bộ tại TP.HCM</h1>",
                unsafe_allow_html=True)

    st.markdown("""
    <div class='greeting-box'>
        <p><b>Kính chào Thầy/Cô, Anh/Chị và các bạn!</b></p>
        <p>Nhóm nghiên cứu thuộc Trường Đại học Kinh tế TP.HCM (UEH) đang thực hiện đề tài về <b>chất lượng không gian đi bộ đô thị tại TP.HCM</b>. Mọi thông tin đóng góp của quý vị đều được bảo mật tuyệt đối và chỉ phục vụ mục đích nghiên cứu khoa học.</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("📋 Thông tin chung (Vui lòng chọn nhanh):")

    age = st.selectbox("1. Độ tuổi của bạn:",
                       ["18 – 24 tuổi", "25 – 39 tuổi", "40 – 59 tuổi", "Dưới 18 tuổi", "Từ 60 tuổi trở lên"])
    gender = st.selectbox("2. Giới tính:", ["Nam", "Nữ", "Khác / Không muốn tiết lộ"])
    walk_freq = st.selectbox("3. Tần suất đi bộ tại TP.HCM của bạn:",
                             ["Hằng ngày", "Vài lần / tuần", "Thỉnh thoảng", "Hiếm khi đi bộ"])

    st.write("---")
    if st.button("🚀 Bắt đầu Khảo sát (20 câu)", type="primary", use_container_width=True):
        st.session_state.user_age = age
        st.session_state.user_gender = gender
        st.session_state.user_walk_freq = walk_freq

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

    progress = st.session_state.current_count / TOTAL_PAIRS_PER_SESSION
    st.progress(progress)
    st.caption(f"Tiến độ: **Câu {st.session_state.current_count + 1} / {TOTAL_PAIRS_PER_SESSION}**")

    dimension = "An toàn hơn khi đi bộ" if st.session_state.current_count % 2 == 0 else "Thoải mái & Dễ chịu hơn"

    st.markdown(
        f"<h4 style='text-align: center; color: #1E3A8A; margin-bottom: 20px;'>Theo cảm nhận của bạn, góc phố nào cho cảm giác<br><u>{dimension.upper()}</u>?</h4>",
        unsafe_allow_html=True)

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
# MÀN HÌNH 3: HOÀN THÀNH
# ==========================================
elif st.session_state.step == 2:
    st.balloons()
    st.success("🎉 Trân trọng cảm ơn sự đóng góp quý báu của bạn!")
    st.write("Dữ liệu của bạn đã được ghi nhận thành công vào hệ thống nghiên cứu.")

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔄 Thực hiện thêm 1 lượt nữa", use_container_width=True):
            st.session_state.step = 0
            st.rerun()
    with col_b:
        if st.button("🛑 Hoàn tất", use_container_width=True):
            st.info("Kính chúc bạn nhiều sức khỏe! Bạn có thể đóng tab trình duyệt này.")