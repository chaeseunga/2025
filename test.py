import streamlit as st

# ---------------------------
# 성분 키워드 사전
ALIASES = {
    "bleach": {"표백제", "락스", "차아염소산나트륨", "sodium hypochlorite", "hypochlorite"},
    "ammonia": {"암모니아", "ammonia", "NH3"},
    "acid": {"식초", "초산", "acetic acid", "구연산", "citric acid", "염산", "hydrochloric acid", "HCl", "황산", "sulfuric acid"},
    "peroxide": {"과산화수소", "hydrogen peroxide", "H2O2"},
    "alcohol": {"에탄올", "ethanol", "IPA", "isopropyl alcohol", "이소프로필알코올", "소독용 알코올"},
    "quat": {"벤잘코늄염화물", "benzalkonium chloride", "quat", "4급 암모늄염", "quaternary ammonium"},
    "baking_soda": {"베이킹소다", "탄산수소나트륨", "sodium bicarbonate"},
}

# 위험 조합 규칙
HAZARDOUS_RULES = {
    frozenset({"bleach", "ammonia"}):
        "⚠️ ‘표백제+암모니아’ → 클로라민/자극성 가스 발생 위험",
    frozenset({"bleach", "acid"}):
        "⚠️ ‘표백제+산(식초/구연산/염산 등)’ → 염소가스 발생 위험",
    frozenset({"bleach", "alcohol"}):
        "⚠️ ‘표백제+알코올’ → 독성 부산물(클로로포름 등) 위험",
    frozenset({"peroxide", "acid"}):
        "⚠️ ‘과산화수소+산’ → 과초산 생성, 강한 부식·자극 위험",
    frozenset({"baking_soda", "acid"}):
        "⚠️ ‘베이킹소다+산’ → CO₂ 발생, 밀폐 용기 내 폭발 위험",
    frozenset({"bleach", "quat"}):
        "⚠️ ‘표백제+4급암모늄 소독제’ → 상호 효과 저하 및 반응 우려",
}

# 표면별 가이드
SURFACE_GUIDE = {
    "대리석/석재": {
        "권장": ["중성 세제", "미온수"],
        "주의": ["산(식초/구연산)", "표백제"],
        "메모": "석회질 기반 → 산에 부식, 표백제도 권장하지 않음",
    },
    "목재": {
        "권장": ["중성·약알칼리 세제", "희석 알코올", "마른천"],
        "주의": ["과도한 수분", "강산/강알칼리"],
        "메모": "과도한 수분/강한 산·염기는 코팅 손상·변색",
    },
    "스테인리스": {
        "권장": ["중성 세제", "희석 표백제(짧게 후 헹굼)"],
        "주의": ["강산", "장시간 표백제"],
        "메모": "염소계·강산은 부식 유발 → 사용 후 즉시 헹굼",
    },
    "유리/타일": {
        "권장": ["중성 세제", "희석 산", "알코올"],
        "주의": ["암모니아 과다 사용"],
        "메모": "환기 필수, 금속 부품 부식 주의",
    },
}

# ---------------------------
# 함수 정의
def normalize_token(token: str) -> set:
    token = token.strip().lower()
    hits = set()
    for key, variants in ALIASES.items():
        for v in variants:
            if v.lower() in token:
                hits.add(key)
    if token in ALIASES.keys():
        hits.add(token)
    return hits

def check_mixture(items: list):
    keys = set()
    for raw in items:
        keys |= normalize_token(raw)
    messages = []
    for i in range(len(keys)):
        for j in range(i+1, len(keys)):
            combo = frozenset({list(keys)[i], list(keys)[j]})
            if combo in HAZARDOUS_RULES:
                messages.append(HAZARDOUS_RULES[combo])
    return keys, messages

def dilution_calc(c1, c2, v2):
    if c1 <= 0 or c2 <= 0 or v2 <= 0 or c2 >= c1:
        return None, None
    v1 = (c2 * v2) / c1
    solvent = v2 - v1
    return v1, solvent

# ---------------------------
# Streamlit UI
st.title("🧹 화학 안전 도우미")
st.write("실생활 청소/소독 시 필요한 **혼합 안전 체크, 희석 계산, 표면별 가이드** 제공")

menu = st.sidebar.radio("메뉴 선택", ["혼합 안전 확인", "희석 계산기", "표면별 가이드"])

# 1) 혼합 안전 확인
if menu == "혼합 안전 확인":
    st.subheader("⚠️ 세제/성분 혼합 안전 확인")
    raw = st.text_input("세제/성분 입력 (쉼표로 구분)", "락스, 식초")
    if st.button("안전 체크"):
        items = [x.strip() for x in raw.split(",") if x.strip()]
        keys, messages = check_mixture(items)
        if keys:
            st.write("인식된 성분 키:", ", ".join(keys))
        if messages:
            for m in messages:
                st.error(m)
        else:
            st.success("치명적 혼합 금지 조합 없음. 그래도 환기·보호장비 필수!")

# 2) 희석 계산기
elif menu == "희석 계산기":
    st.subheader("🧪 희석 계산기 (C1V1=C2V2)")
    c1 = st.number_input("원액 농도 C1 (%)", value=5.0)
    c2 = st.number_input("목표 농도 C2 (%)", value=0.1)
    v2 = st.number_input("최종 부피 V2 (mL)", value=1000.0)
    if st.button("계산하기"):
        v1, solvent = dilution_calc(c1, c2, v2)
        if v1:
            st.success(f"원액 필요량 V1 ≈ {v1:.1f} mL")
            st.info(f"희석 용매(물 등) ≈ {solvent:.1f} mL")
        else:
            st.error("입력값을 확인하세요. (C1 > C2 > 0, V2 > 0)")

# 3) 표면별 가이드
elif menu == "표면별 가이드":
    st.subheader("🏠 표면별 권장/주의 가이드")
    for surf, info in SURFACE_GUIDE.items():
        with st.expander(surf):
            st.write("✅ 권장:", ", ".join(info["권장"]))
            st.write("⚠️ 주의:", ", ".join(info["주의"]))
            st.caption(info["메모"])
