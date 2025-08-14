import streamlit as st

# 🌟 앱 제목
st.markdown("<h1 style='text-align: center;'>💼✨🌈💖 MBTI 기반 진로 추천 🎯🔥🌸🦋🎆🌟🏆🚀🌍💫💐🌼🌺🎇💎🎁</h1>", unsafe_allow_html=True)

# 🌟 MBTI별 직업 데이터 (예시)
job_recommendations = {
    "INTJ": [
        "🔬📚💡 연구원 ✨🧠📊 데이터 분석가 🌌🎯💼 전략 컨설턴트",
        "💎🌍🚀 혁신 기술 전문가 💖🌟💼",
        "🎨🔥🏆 창의적 기획자 🦋🌸💫"
    ],
    "ENTP": [
        "🚀💡💎 기업가 🎯🌈✨ 광고 기획자 🦋🌼🔥 변호사",
        "🌍🎆🎇 글로벌 마케터 💼💐🌟",
        "🎁💫🎨 창의 컨텐츠 제작자 🌺🏆🌌"
    ],
    "INFJ": [
        "💖🦋🌸 심리상담사 🌈💫🌼 작가 📚🎨✨ 사회복지사",
        "💎💐🔥 인권 활동가 🌍🌟🏆",
        "🎆🌺🚀 꿈 설계자 🎯💼💖"
    ],
    "ESTP": [
        "⚡🔥💼 세일즈 매니저 🎯🚀💎 이벤트 플래너 🌸🏆🌟 스포츠 코치",
        "💫🌍🎆 여행 가이드 💖💼🌼",
        "🎇🌺🎨 활동가 🦋💐✨"
    ],
}

# 🌟 MBTI 선택
mbti_list = list(job_recommendations.keys())
selected_mbti = st.selectbox("🌈✨당신의 MBTI를 선택하세요💎🎯🌍🔥🌸💫🦋🎆🌟🏆🚀💼🎇💐🌺📚💖", mbti_list)

# 🌟 추천 직업 표시
if selected_mbti:
    st.markdown(f"<h2>✨🌈💎 {selected_mbti} 유형 추천 직업 🎯🔥🌸🦋🎆🌟🏆🚀🌍💫💐🌼🌺🎇💼💖</h2>", unsafe_allow_html=True)
    for job in job_recommendations[selected_mbti]:
        st.write(f"➡️ {job}")

# 🌟 참고 문구
st.caption("💬🌈✨💎🔥💖 이 추천은 일반적인 MBTI 성향을 기반으로 하며, 개인의 경험과 능력에 따라 적합도가 달라질 수 있습니다 🌟🏆🚀🌍💫💐🌼🌺🎇💼")
