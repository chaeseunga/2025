# chem_safety_app_v2.py
# 실행: streamlit run chem_safety_app_v2.py

import streamlit as st
import itertools
import re

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

HAZARDOUS_RULES = {
    frozenset({"bleach", "ammonia"}): ("☠️ 독성 가스", "‘표백제+암모니아’ 혼합은 매우 위험합니다."),
    frozenset({"bleach", "acid"}): ("🫁 염소 가스", "‘표백제+산(식초/구연산/염산 등)’ 혼합은 매우 위험합니다."),
    frozenset({"bleach", "alcohol"}): ("🧠 신경 독성", "‘표백제+알코올’ 혼합은 위험합니다."),
    frozenset({"peroxide", "acid"}): ("🧯 부식성", "‘과산화수소+산’ 혼합은 위험합니다."),
    frozenset({"baking_soda", "acid"}): ("💥 압력 폭발", "‘베이킹소다+산’은 밀폐 용기에서 위험할 수 있습니다."),
    frozenset({"bleach", "quat"}): ("⚠️ 효과 저하", "‘표백제+4급암모늄(소독제)’ 혼합은 피하세요."),
}

HAZ_DETAILS = {
    frozenset({"bleach", "ammonia"}): {
        "why": "섞으면 ‘클로라민’ 같은 가스가 생겨 눈·코 자극, 기침, 호흡곤란을 일으킵니다.",
        "symptoms": "눈·목 따가움, 기침, 메스꺼움, 숨 가쁨.",
        "instead": "한 번에 하나만 사용하세요. 표백제를 썼다면 물로 헹구고 환기 후 다른 날 암모니아 제품을 사용하세요.",
    },
    frozenset({"bleach", "acid"}): {
        "why": "섞이면 ‘염소 가스(Cl₂)’가 생겨 호흡기에 심한 자극을 줍니다.",
        "symptoms": "눈물, 기침, 가슴 답답, 호흡 곤란.",
        "instead": "표백제와 산 계열은 절대 함께 쓰지 마세요. 필요하면 다른 날 따로 사용하세요.",
    },
    frozenset({"bleach", "alcohol"}): {
        "why": "특정 조건에서 독성 부산물(클로로포름 등)이 생길 수 있습니다.",
        "symptoms": "두통, 어지러움, 메스꺼움.",
        "instead": "표백제를 쓰는 날엔 알코올 제품은 피하세요.",
    },
    frozenset({"peroxide", "acid"}): {
        "why": "‘과초산’ 같은 강한 자극·부식성 물질이 생길 수 있습니다.",
        "symptoms": "피부·눈 자극, 호흡기 자극.",
        "instead": "과산화수소와 산성 제품은 함께 쓰지 말고 각각 단독으로만 사용하세요.",
    },
    frozenset({"baking_soda", "acid"}): {
        "why": "이산화탄소(CO₂)가 급격히 발생해 밀폐 용기에선 압력 폭발 위험이 있습니다.",
        "symptoms": "밀폐 상태에서 용기 파손·튀김 위험.",
        "instead": "밀폐 용기에서 섞지 말고, 통풍되는 곳에서 개방 용기만 사용하세요.",
    },
    frozenset({"bleach", "quat"}): {
        "why": "효과가 떨어지거나 잔류 반응이 생길 수 있습니다.",
        "symptoms": "살균 효과 저하, 표면 손상.",
        "instead": "한 번에 하나의 제품만 사용하고 사용 후 충분히 헹구세요.",
    },
}

SURFACE_GUIDE = {
    "대리석/석재": {
        "권장": ["중성 세제", "미온수"],
        "주의": ["산(식초/구연산)", "표백제"],
        "메모": "석회질이라 산에 약합니다. 반점·부식 위험.",
    },
    "목재": {
        "권장": ["중성·약알칼리 세제", "마른천", "소량 알코올"],
        "주의": ["과도한 수분", "강산/강알칼리"],
        "메모": "코팅 손상·변색 주의. 물기는 바로 닦아주세요.",
    },
    "스테인리스": {
        "권장": ["중성 세제", "짧게 희석 표백제(이후 헹굼)"],
        "주의": ["강산", "장시간 표백제 접촉"],
        "메모": "사용 후 충분히 헹구면 얼룩·부식 예방.",
    },
    "유리/타일": {
        "권장": ["중성 세제", "희석 산(비누때 제거)", "알코올"],
        "주의": ["환기 부족 시 암모니아 과다 사용"],
        "메모": "금속 부품 부식 주의, 환기 필수.",
    },
}

# =========================
# 함수
# =========================
def normalize_token(token: str) -> set:
    """입력값에서 해당하는 키워드 집합 반환"""
    token = token.strip().lower()
    hits = set()
    for key, variants in ALIASES.items():
        for v in variants:
            if re.search(rf"\b{re.escape(v.lower())}\b", token):
                hits.add(key)
    if token in ALIASES.keys():
        hits.add(token)
    return hits

def check_mixture(items: list):
    """2개, 3개 조합 모두 체크"""
    keys = set()
    for raw in items:
        keys |= normalize_token(raw)
    messages, details = [], []
    for r in (2, 3):
        for combo in itertools.combinations(keys, r):
            combo_set = frozenset(combo)
            if combo_set in HAZARDOUS_RULES:
                cat, msg = HAZARDOUS_RULES[combo_set]
                messages.append((cat, msg))
                details.append(HAZ_DETAILS.get(combo_set))
    return keys, messages, details

def dilution_calc(c1, c2, v2):
    if c1 <= 0 or c2 <= 0 or v2 <= 0 or c2 >= c1:
        return None, None
    v1 = (c2 * v2) / c1
    solvent = v2 - v1
    return v1, solvent

# =========================
# UI
# =========================
st.set_page_config(page_title="클린메이트", page_icon="🧹")
st.title("🧹 클린메이트")

menu = st.sidebar.radio("메뉴", ["혼합 안전 확인", "희석 계산", "표면별 가이드"])

# -------------------------
# 혼합 안전 확인
# -------------------------
if menu == "혼합 안전 확인":
    st.subheader("⚠️ 세제/성분 혼합 안전 확인")

    all_options = sorted({v for s in ALIASES.values() for v in s})
    selected = st.multiselect("세제/성분 선택", options=all_options, default=["락스", "식초"])

    if st.button("확인하기"):
        keys, messages, details = check_mixture(selected)

        if keys:
            st.info("인식된 성분: " + ", ".join(sorted(keys)) or "(없음)")
        if messages:
            for idx, (cat, m) in enumerate(messages, 1):
                st.error(f"{idx}. {cat} → {m}")
            st.markdown("### 상세 설명")
            for d in details:
                if not d:
                    continue
                with st.expander("자세히 보기"):
                    st.write("• **이유**:", d["why"])
                    st.write("• **증상**:", d["symptoms"])
                    st.write("• **대신 이렇게 사용하세요**:", d["instead"])
        else:
            st.success("특별히 위험한 조합은 감지되지 않았습니다. 그래도 제품은 하나씩만 사용하세요.")

# -------------------------
# 희석 계산
# -------------------------
elif menu == "희석 계산":
    st.subheader("🧪 희석 계산기")
    st.caption("예: 락스 5% 원액으로 0.1% 소독액 1L 만들기")

    c1 = st.number_input("원액 농도 C1 (%)", value=5.0, step=0.1)
    c2 = st.number_input("목표 농도 C2 (%)", value=0.1, step=0.1)
    v2 = st.number_input("최종 부피 V2 (mL)", value=1000.0, step=50.0)

    if st.button("계산하기"):
        v1, solvent = dilution_calc(c1, c2, v2)
        if v1 is None:
            st.error("입력값을 확인하세요. (C1 > C2 > 0, V2 > 0)")
        else:
            st.metric("필요한 원액 (mL)", f"{v1:.1f}")
            st.metric("필요한 물 (mL)", f"{solvent:.1f}")
            st.caption("원액을 물에 조금씩 넣어 섞어주세요. 사용 후 환기·헹굼 필수!")

# -------------------------
# 표면별 가이드
# -------------------------
elif menu == "표면별 가이드":
    st.subheader("🏠 표면별 가이드")
    for surf, info in SURFACE_GUIDE.items():
        with st.expander(surf):
            st.write("✅ 권장:", ", ".join(info["권장"]))
            st.write("⚠️ 주의:", ", ".join(info["주의"]))
            st.caption(info["메모"])

st.divider()
st.caption("※ 이 앱은 생활 안전 참고용 가이드입니다. 실제 사용 시에는 제품 라벨과 안전 지침을 꼭 확인하세요.")
