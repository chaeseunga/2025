import streamlit as st
from PIL import Image
import requests
import io

# ------------------------------
# (1) 음식 데이터베이스 예시
# ------------------------------
# 실제로는 더 큰 DB 필요 (칼로리, 탄단지, 당류 등)
food_db = {
    "pizza": {"cal": 266, "carb": 33, "protein": 11, "fat": 10, "sugar": 3},
    "burger": {"cal": 295, "carb": 30, "protein": 17, "fat": 14, "sugar": 6},
    "apple": {"cal": 52, "carb": 14, "protein": 0.3, "fat": 0.2, "sugar": 10},
    "rice": {"cal": 130, "carb": 28, "protein": 2.7, "fat": 0.3, "sugar": 0}
}

# 하루 권장 섭취량 (성인 기준 간단 예시)
RDA = {
    "cal": 2000,
    "carb": 300,
    "protein": 50,
    "fat": 70,
    "sugar": 25
}

# ------------------------------
# (2) 음식 분류 (간단히 흉내내기)
# ------------------------------
# 실제로는 Hugging Face API나 ML 모델 필요
def classify_food(image: Image.Image):
    # 여기서는 예시로 "pizza" 반환
    return "pizza"

# ------------------------------
# (3) Streamlit UI
# ------------------------------
st.title("🍽️ 스마트 영양 분석 앱")
st.write("사진을 업로드하면 음식 칼로리와 영양소를 예측해줍니다.")

uploaded = st.file_uploader("음식 사진 업로드", type=["jpg", "jpeg", "png"])

if uploaded:
    img = Image.open(uploaded)
    st.image(img, caption="업로드된 음식", use_column_width=True)

    # 음식 분류
    food_name = classify_food(img)
    st.success(f"인식된 음식: **{food_name}**")

    # 양 입력
    portion = st.slider("섭취 양 (1인분 기준)", 0.5, 3.0, 1.0, 0.5)

    if food_name in food_db:
        nutri = {k: v * portion for k, v in food_db[food_name].items()}
        st.subheader("🍴 영양소 정보")
        st.write(f"- 칼로리: {nutri['cal']} kcal")
        st.write(f"- 탄수화물: {nutri['carb']} g")
        st.write(f"- 단백질: {nutri['protein']} g")
        st.write(f"- 지방: {nutri['fat']} g")
        st.write(f"- 당류: {nutri['sugar']} g")

        # 하루 권장 대비 계산
        st.subheader("📊 오늘 권장량 대비")
        for k in RDA:
            remain = RDA[k] - nutri[k]
            if remain > 0:
                st.info(f"✅ {k}를 {remain:.1f} g 더 섭취해도 됩니다.")
            else:
                st.warning(f"⚠️ {k}를 {-remain:.1f} g 초과했습니다. 줄이는 게 좋아요!")
    else:
        st.error("⚠️ 데이터베이스에 없는 음식입니다.")
