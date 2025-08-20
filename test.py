# chem_safety_app.py
# 실행: streamlit run chem_safety_app.py

import streamlit as st

# =========================
# 데이터(키워드/규칙/설명)
# =========================
ALIASES = {
    "bleach": {"표백제", "락스", "차아염소산나트륨", "sodium hypochlorite", "hypochlorite"},
    "ammonia": {"암모니아", "ammonia", "nh3"},
    "acid": {"식초", "초산", "acetic acid", "구연산", "citric acid", "염산", "hydrochloric acid", "hcl", "황산", "sulfuric acid"},
    "peroxide": {"과산화수소", "hydrogen peroxide", "h2o2"},
    "alcohol": {"에탄올", "ethanol", "ipa", "isopropyl alcohol", "이소프로필알코올", "소독용 알코올"},
    "quat": {"벤잘코늄염화물", "benzalkonium chloride", "quat", "4급 암모늄염", "quaternary ammonium"},
    "baking_soda": {"베이킹소다", "탄산수소나트륨", "sodium bicarbonate"},
}

# 위험 조합 규칙(핵심 경고 메시지)
HAZARDOUS_RULES = {
    frozenset({"bleach", "ammonia"}): "‘표백제+암모니아’ 혼합은 매우 위험합니다.",
    frozenset({"bleach", "acid"}): "‘표백제+산(식초/구연산/염산 등)’ 혼합은 매우 위험합니다.",
    frozenset({"bleach", "alcohol"}): "‘표백제+알코올’ 혼합은 위험합니다.",
    frozenset({"peroxide", "acid"}): "‘과산화수소+산’ 혼합은 위험합니다.",
    frozenset({"baking_soda", "acid"}): "‘베이킹소다+산’은 밀폐 용기에서 위험할 수 있습니다.",
    frozenset({"bleach", "quat"}): "‘표백제+4급암모늄(소독제)’ 혼합은 피하세요.",
}

# 쉬운 설명(왜 위험한가 · 증상 · 안전 대안)
HAZ_DETAILS = {
    frozenset({"bleach", "ammonia"}): {
        "why": "섞으면 ‘클로라민’ 같은 자극성 가스가 생겨 눈·코 자극과 기침, 호흡곤란을 일으킬 수 있습니다.",
        "symptoms": "눈·목 따가움, 기침, 메스꺼움, 숨 가쁨, 어지러움.",
        "instead": "한 번에 하나만 사용하세요. 표백제를 썼다면 충분히 물로 헹구고 환기한 뒤, 다른 날 암모니아 제품을 사용하세요.",
    },
    frozenset({"bleach", "acid"}): {
        "why": "섞이면 ‘염소 가스(Cl₂)’가 생길 수 있습니다. 호흡기에 매우 자극적입니다.",
        "symptoms": "눈물, 심한 기침, 가슴 답답, 호흡 곤란(높은 농도는 폐 손상 위험).",
        "instead": "표백제와 식초·구연산·염산 계열은 절대 함께 쓰지 마세요. 필요하면 다른 날 따로 사용하고 사용 후 충분히 헹군 뒤 환기하세요.",
    },
    frozenset({"bleach", "alcohol"}): {
        "why": "특정 조건에서 독성 부산물(예: 클로로포름)이 생길 수 있습니다.",
        "symptoms": "두통, 어지러움, 메스꺼움 등(노출 정도에 따라 다름).",
        "instead": "표백제 사용하는 날에는 알코올 제품(소독용 알코올, 유리세정제 등)을 피하고, 서로 다른 날에 분리해 사용하세요.",
    },
    frozenset({"peroxide", "acid"}): {
        "why": "‘과초산’ 같은 강한 자극·부식성 물질이 생길 수 있습니다.",
        "symptoms": "피부·눈 자극, 호흡기 자극.",
        "instead": "과산화수소와 산성 제품은 함께 쓰지 말고, 각각 제품 안내대로 단독 사용하세요.",
    },
    frozenset({"baking_soda", "acid"}): {
        "why": "이산화탄소(CO₂)가 빠르게 발생합니다. 밀폐 용기에서는 압력이 올라 ‘펑’ 튈 수 있습니다.",
        "symptoms": "밀폐 상태에서 용기 파손·튀김 위험.",
        "instead": "밀폐 용기에서 섞지 마세요. 통풍되는 곳에서 소량만, 개방 용기에서만 사용하세요.",
    },
    frozenset({"bleach", "quat"}): {
        "why": "상호 작용으로 효과가 떨어지거나 잔류 반응이 생길 수 있습니다.",
        "symptoms": "살균 효과 저하, 표면 손상 가능.",
        "instead": "한 번에 하나의 제품만 사용하고, 사용 후 물로 충분히 헹구세요.",
    },
}

SURFACE_GUIDE = {
    "대리석/석재": {
        "권장": ["중성 세제", "미온수"],
        "주의": ["산(식초/구연산)", "표백제"],
        "메모": "석회질(탄산칼슘)이라 산에 약합니다. 반점·부식 위험.",
    },
    "목재": {
        "권장": ["중성·약알칼리 세제", "마른천", "국소 오염 시 소량 알코올"],
        "주의": ["과도한 수분", "강산/강알칼리"],
        "메모": "코팅 손상·변색 주의. 물기는 바로 닦아주세요.",
    },
    "스테인리스": {
        "권장": ["중성 세제", "짧은 시간 희석 표백제(이후 즉시 헹굼)"],
        "주의": ["염산 등 강산", "장시간 표백제 접촉"],
        "메모": "사용 후 물로 충분히 헹구면 얼룩·부식 예방.",
    },
    "유리/타일": {
        "권장": ["중성 세제", "희석 산(비누때 제거)", "알코올"],
        "주의": ["환기 부족 상태에서 암모니아 과다 사용"],
        "메모": "금속 부품 접촉 시 부식 주의, 환기 필수.",
    },
}

# =========================
# 유틸 함수
# =========================
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
    messages, details = [], []
    klist = list(keys)
    for i in range(len(klist)):
        for j in range(i+1, len(klist)):
            combo = frozenset({klist[i], klist[j]})
            if combo in HAZARDOUS_RULES:
                messages.append(HAZARDOUS_RULES[combo])
                details.append(HAZ_DETAILS.get(combo))
    return keys, messages, details

def dilution_calc(c1, c2, v2):
    # c1, c2: %, v2: mL(또는 같은 단위)
    if c1 <= 0 or c2 <= 0 or v2 <= 0 or c2 >= c1:
        return None, None
    v1 = (c2 * v2) / c1
    solvent = v2 - v1
    return v1, solvent

# =========================
# Streamlit UI
# =========================
st.set_page_config(page_title="화학 안전 도우미", page_icon="🧹")
st.title("🧹 화학 안전 도우미")

st.markdown(
    """
**무엇을 하나요?**  
- ❌ 섞이면 위험한 세제 조합을 알려줍니다.  
- 🧪 물에 얼마나 타야 하는지(희석) 간단히 계산해 줍니다.  
- 🏠 표면(대리석·목재·스테인리스 등)에 맞는 사용 가이드를 제공합니다.  

**기본 수칙**  
1) 한 번에 **하나의 제품만** 사용  
2) **환기** 꼭 하기(창문 열기/선풍기)  
3) 제품 **라벨**의 ‘혼합 금지’ 문구 확인  
4) 필요하면 원액을 **물에 희석**해서 사용
"""
)

menu = st.sidebar.radio(
    "메뉴",
    ["혼합 안전 확인", "희석 계산", "표면별 가이드", "자주 묻는 질문"]
)

# -------------------------
# 1) 혼합 안전 확인
# -------------------------
if menu == "혼합 안전 확인":
    st.subheader("⚠️ 세제/성분 혼합 안전 확인")
    st.caption("예시: `락스, 식초` / `과산화수소 6%, 구연산` / `암모니아 클리너`")
    raw = st.text_input("세제/성분 입력(쉼표로 구분)", "락스, 식초")
    if st.button("안전 체크"):
        items = [x.strip() for x in raw.split(",") if x.strip()]
        keys, messages, details = check_mixture(items)

        if keys:
            st.write("🔎 인식된 성분 키:", ", ".join(sorted(keys)) or "(알 수 없음)")
        if messages:
            for idx, m in enumerate(messages, 1):
                st.error(f"{idx}. {m}")
            st.markdown("### 왜 위험할까요? / 대신 어떻게 할까요?")
            for d in details:
                if not d:
                    continue
                with st.expander("상세 보기", expanded=False):
                    st.write("• **이유**:", d["why"])
                    st.write("• **증상**:", d["symptoms"])
                    st.write("• **대신 이렇게**:", d["instead"])
            st.info("기본 수칙: 한 번에 하나의 제품만 사용 · 환기 · 장갑/마스크 착
