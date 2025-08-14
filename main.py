import streamlit as st

# 제목
st.title("💼 MBTI 기반 진로 추천 웹앱")

# MBTI별 직업 데이터
job_recommendations = {
    "INTJ": ["연구원", "데이터 분석가", "전략 컨설턴트"],
    "ENTP": ["기업가", "광고 기획자", "변호사"],
    "INFJ": ["심리상담사", "작가", "사회복지사"],
    "ESTP": ["세일즈 매니저", "이벤트 플래너", "스포츠 코치"],
    # ... 나머지 MBTI 추가
}

# MBTI 선택
mbti_list = list(job_recommendations.keys())
selected_mbti = st.selectbox("당신의 MBTI를 선택하세요", mbti_list)

# 추천 직업 표시
if selected_mbti:
    st.subheader(f"✨ {selected_mbti} 유형 추천 직업")
    for job in job_recommendations[selected_mbti]:
        st.write(f"- {job}")

# 참고 설명
st.caption("※ 직업 추천은 일반적인 성향을 기반으로 하며, 개인의 경험과 능력에 따라 적합도가 달라질 수 있습니다.")

