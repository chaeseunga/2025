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

# 학생용 쉬운 설명(왜 위험한가 · 증상 · 대신 어떻게)
HAZ_DETAILS = {
    frozenset({"bleach", "ammonia"}): {
        "why": "둘을 섞으면 ‘클로라민’ 같은 자극성 가스가 생겨 눈·코가 따갑고 기침·호흡곤란을 유발할 수 있음.",
        "symptoms": "눈·목 따가움, 기침, 메스꺼움, 숨 가쁨, 어지러움.",
        "instead": "하루에 하나만 사용하세요. 표백제를 썼다면 충분히 물로 헹군 뒤 환기시키고, 다른 날 암모니아 제품을 사용하세요.",
    },
    frozenset({"bleach", "acid"}): {
        "why": "섞이면 ‘염소 가스(Cl₂)’가 발생할 수 있음. 염소 가스는 호흡기에 매우 자극적임.",
        "symptoms": "눈물, 심한 기침, 가슴 답답, 호흡 곤란. 높은 농도는 폐 손상 위험.",
        "instead": "표백제와 식초·구연산·염산 계열은 절대 함께 쓰지 마세요. 필요한 경우 ‘다른 날’ 각각 따로 사용하고 충분히 헹군 뒤 환기하세요.",
    },
    frozenset({"bleach", "alcohol"}): {
        "why": "특정 조건에서 독성 부산물(예: 클로로포름)이 생길 수 있어 건강에 해로움.",
        "symptoms": "두통, 어지러움, 메스꺼움 등(노출 정도에 따라 다름).",
        "instead": "표백제를 쓴 날에는 알코올 기반 제품(소독용 알코올, 유리세정제 등)을 피하고, 서로 다른 날에 분리해 사용하세요.",
    },
    frozenset({"peroxide", "acid"}): {
        "why": "‘과초산’ 같은 강한 자극·부식성 물질이 생길 수 있음.",
        "symptoms": "피부·눈 자극, 호흡기 자극.",
        "instead": "과산화수소와 산성 제품은 함께 쓰지 말고, 각각 필요한 경우 제품별 안내대로 단독 사용하세요.",
    },
    frozenset({"baking_soda", "acid"}): {
        "why": "이산화탄소(CO₂)가 빠르게 발생. 밀폐 용기에서는 압력 상승으로 ‘펑’ 터질 위험.",
        "symptoms": "밀폐 상태에서 용기 파손·튀김 위험.",
        "instead": "밀폐 용기에서 섞지 마세요. 통풍 잘 되는 곳에서 소량만, 개방 용기에서만 반응 실험처럼 사용하세요.",
    },
    frozenset({"bleach", "quat"}): {
        "why": "상호 작용으로 효과가 떨어지거나 잔류 반응이 생길 수 있음.",
        "symptoms": "효과 저하, 표면 손상 가능.",
        "instead": "한 번에 하나의 제품만, 서로 다른 날 따로 사용하세요. 사용 후 물로 충분히 헹구기.",
    },
}

SURFACE_GUIDE = {
    "대리석/석재": {
        "권장": ["중성 세제", "미온수"],
        "주의": ["산(식초/구연산)", "표백제"],
        "메모": "석회질(탄산칼슘)이라 산에 약함. 반점·부식 위험.",
    },
    "목재": {
        "권장": ["중성·약알칼리 세제", "마른천", "국소 오염 시 소량 알코올"],
        "주의": ["과도한 수분", "강산/강알칼리"],
        "메모": "코팅 손상·변색 주의. 물기는 바로 닦기.",
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
    messages = []
    details = []
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
st.set_page_config(page_title="화학 안전 도우미(학생용)", page_icon="🧹")
st.title("🧹 화학 안전 도우미 (학생용)")

st.markdown(
    """
**무엇을 하나요?**  
- ❌ **섞으면 위험한 세제 조합**을 알려줘요.  
- 🧪 **희석(물에 타기) 계산**을 쉬운 예시와 함께 알려줘요.  
- 🏠 **표면별 안전 가이드**(대리석, 목재 등)를 보여줘요.  

**기본 원칙(학생용 요약)**  
1) 한 번에 **하나의 제품만** 사용하기  
2) **환기** 잘하기(창문 열고, 선풍기 켜고)  
3) 제품 **라벨**과 **혼합 금지** 확인하기  
4) 원액은 **물에 희석**해서 사용하기(필요 시)
"""
)

menu = st.sidebar.radio(
    "메뉴",
    ["혼합 안전 확인", "희석 계산기(쉬운 설명)", "표면별 가이드", "FAQ(학생용)"]
)

# -------------------------
# 1) 혼합 안전 확인
# -------------------------
if menu == "혼합 안전 확인":
    st.subheader("⚠️ 세제/성분 혼합 안전 확인")
    st.caption("예시 입력: `락스, 식초`  /  `과산화수소 6%, 구연산`  /  `암모니아 클리너`")
    raw = st.text_input("세제/성분 입력(쉼표로 구분)", "락스, 식초")
    if st.button("안전 체크"):
        items = [x.strip() for x in raw.split(",") if x.strip()]
        keys, messages, details = check_mixture(items)

        if keys:
            st.write("🔎 인식된 성분 키:", ", ".join(sorted(keys)) or "(알 수 없음)")
        if messages:
            for idx, m in enumerate(messages, 1):
                st.error(f"{idx}. {m}")
            # 상세 쉬운 설명
            st.markdown("### 💡 왜 위험할까요? / 대신 어떻게 할까요?")
            for d in details:
                if not d: 
                    continue
                with st.expander("상세 보기", expanded=False):
                    st.write("**왜 위험한가(쉬운 설명)**:", d["why"])
                    st.write("**몸에 나타날 수 있는 증상**:", d["symptoms"])
                    st.write("**대신 이렇게 사용하세요(안전 대안)**:", d["instead"])
            st.info("기본 수칙: 한 번에 하나의 제품만 사용 · 환기 · 장갑/마스크 착용 · 사용 후 물로 충분히 헹구기")
        else:
            st.success("치명적 혼합 금지 조합이 감지되지 않았습니다. 그래도 한 번에 하나의 제품만 사용하고, 환기를 충분히 해주세요.")

# -------------------------
# 2) 희석 계산기(쉬운 설명)
# -------------------------
elif menu == "희석 계산기(쉬운 설명)":
    st.subheader("🧪 희석 계산기 (C1V1 = C2V2)")
    st.markdown(
        """
**쉬운 말로 설명**  
- **C1**: 원액의 진하기(%) — 예: 락스 5%  
- **C2**: 만들고 싶은 진하기(%) — 예: 0.1% 소독액  
- **V2**: 만들고 싶은 양(부피) — 예: 1000 mL(=1L)  

👉 **원액은 얼마나? (V1)**, **물은 얼마나? (V2 - V1)** 를 계산해 줍니다.  
※ 항상 안전을 위해 제품 라벨 지침을 우선하세요.
"""
    )

    left, right = st.columns(2)
    with left:
        preset = st.selectbox(
            "빠른 예시 선택",
            [
                "직접 입력",
                "예시) 락스 5% → 0.1%, 최종 1000 mL",
                "예시) 과산화수소 3% → 0.5%, 최종 500 mL",
            ],
        )

    if preset == "예시) 락스 5% → 0.1%, 최종 1000 mL":
        c1, c2, v2 = 5.0, 0.1, 1000.0
    elif preset == "예시) 과산화수소 3% → 0.5%, 최종 500 mL":
        c1, c2, v2 = 3.0, 0.5, 500.0
    else:
        c1 = st.number_input("원액 농도 C1 (%)", value=5.0, min_value=0.0, step=0.1)
        c2 = st.number_input("목표 농도 C2 (%)", value=0.1, min_value=0.0, step=0.1)
        v2 = st.number_input("최종 부피 V2 (mL)", value=1000.0, min_value=0.0, step=50.0)

    if st.button("계산하기"):
        v1, solvent = dilution_calc(c1, c2, v2)
        if v1 is None:
            st.error("입력값을 확인하세요. (C1 > C2 > 0, V2 > 0)")
        else:
            st.success(f"원액 필요량 V1 ≈ **{v1:.1f} mL**")
            st.info(f"물(희석 용매) ≈ **{solvent:.1f} mL**")
            st.caption("팁: 원액을 물에 ‘조금씩’ 넣어가며 저으세요. 사용 후 환기·헹굼 필수!")

    with right:
        st.markdown("#### 학생용 한 줄 요약")
        st.write("원액이 진하면 조금만 넣고, 물을 많이 넣으면 진하기가 낮아져요!")
        st.write("예: 5% 락스 20mL + 물 980mL = 0.1% 소독액 1000mL")

# -------------------------
# 3) 표면별 가이드
# -------------------------
elif menu == "표면별 가이드":
    st.subheader("🏠 표면별 권장/주의 가이드")
    st.caption("표면(재질)에 따라 안전한 세제가 달라요. 모르면 ‘중성 세제 + 미온수’가 가장 안전합니다.")
    for surf, info in SURFACE_GUIDE.items():
        with st.expander(surf):
            st.write("✅ 권장:", ", ".join(info["권장"]))
            st.write("⚠️ 주의:", ", ".join(info["주의"]))
            st.caption(info["메모"])

# -------------------------
# 4) FAQ(학생용)
# -------------------------
elif menu == "FAQ(학생용)":
    st.subheader("❓ 자주 묻는 질문 (학생용 쉬운 설명)")
    with st.expander("염소 가스가 뭐예요? 왜 위험하죠?"):
        st.write(
            "- **염소 가스(Cl₂)**는 표백제(락스)와 산성 물질(식초 등)이 만나 생길 수 있는 자극성 기체예요.\n"
            "- 낮은 농도도 눈·코가 따갑고 기침이 나요. 높은 농도는 **호흡 곤란**과 **폐 손상**을 일으킬 수 있어 매우 위험해요."
        )
        st.info("예방법: 표백제와 산성 제품을 절대 함께 쓰지 않기 · 환기하기 · 한 번에 하나만 사용하기")
    with st.expander("이미 섞었고 냄새가 코를 찌를 때 어떻게 해요?"):
        st.write(
            "1) 즉시 사용을 멈추고 창문을 열어 **환기**하세요.\n"
            "2) 혼합물을 더 이상 건드리지 말고 자리를 벗어나세요.\n"
            "3) 증상이 심하면 보호자와 함께 **의료 상담**을 받으세요."
        )
    with st.expander("희석은 왜 해야 하나요?"):
        st.write(
            "강한 원액은 표면을 상하게 하거나 우리 몸에 자극을 줄 수 있어요. "
            "그래서 **물에 타서** 적절한 진하기로 **약하게** 만든 뒤 사용해요."
        )
    with st.expander("가장 안전한 기본 수칙은요?"):
        st.write(
            "- 한 번에 **하나의 제품만** 사용\n"
            "- **환기** 잘 하기\n"
            "- 사용 후 **물로 헹구기**\n"
            "- **라벨(혼합 금지)** 꼭 확인\n"
            "- 손 보호용 **장갑**·**마스크** 착용"
        )

st.divider()
st.caption("※ 이 앱은 생활 안전 학습용 안내입니다. 실제 사용 시에는 제품 라벨과 안전자료(SDS)를 우선하세요.")
