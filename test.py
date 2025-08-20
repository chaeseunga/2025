# streamlit_app.py
# --- Streamlit Sleep Optimizer — ‘Light & Caffeine Budget’ Edition ---
# Unique features:
# 1) Light Budget Planner: calculates personalized morning bright-light minutes and evening "dim hours" target
# 2) Caffeine Curfew & Nap Gate: computes last safe caffeine time + ideal nap window using a simple adenosine/caffeine model
# 3) Social Jetlag Minimizer: detects MSFsc, social jetlag, and gives a 7‑day micro‑shift plan
# 4) Two‑Process Simulation: visualizes Process S (sleep pressure) + Process C (circadian) to pick optimal sleep window today

import math
import numpy as np
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta, time
import plotly.graph_objects as go

st.set_page_config(page_title="Sleep Optimizer — Light & Caffeine Budget", page_icon="😴", layout="wide")
st.title("😴 Streamlit Sleep Optimizer — ‘Light & Caffeine Budget’ Edition")
st.caption("과학적 원리로 수면 루틴을 맞춤 추천합니다. (교육용/라이프스타일 가이드)")

# ----------------------------
# Helpers
# ----------------------------

def hm_to_minutes(hm: str, default="23:00"):
    try:
        h, m = map(int, hm.split(":"))
        return h * 60 + m
    except Exception:
        h, m = map(int, default.split(":"))
        return h * 60 + m


def minutes_to_hm(mins: int):
    mins = mins % (24 * 60)
    h = mins // 60
    m = mins % 60
    return f"{h:02d}:{m:02d}"


def circadian_phase_score(wake_min):
    """Rough chronotype index: earlier wake = more lark-like."""
    # Normalize 03:00-11:00 => 0..1
    wake_min = wake_min % (24*60)
    base = 3*60
    rng = 8*60
    return max(0, min(1, 1 - (wake_min - base)/rng))


def msf_corrected(work_bed, work_wake, free_bed, free_wake, workdays=5, freedays=2):
    """Mid-sleep on free days corrected for deficit (MSFsc). Simplified."""
    def mid(b, w):
        b, w = b % (24*60), w % (24*60)
        dur = (w - b) % (24*60)
        return (b + dur/2) % (24*60), dur
    m_work, d_work = mid(work_bed, work_wake)
    m_free, d_free = mid(free_bed, free_wake)
    sleep_need = (d_work*workdays + d_free*freedays)/(workdays+freedays)
    # Correct if free sleep >> need (oversleeping clues debt)
    correction = max(0, (d_free - sleep_need)/2)
    return (m_free - correction) % (24*60), m_work, m_free, d_work, d_free, sleep_need


def caffeine_cutoff(desired_bed_min, metabolism: str, total_mg: int):
    """Compute last safe caffeine time so that ~75% eliminated by bedtime.
    Half-life: fast=3.5h, normal=5h, slow=7h (simplified)."""
    hl = {"빠름":3.5, "보통":5.0, "느림":7.0}.get(metabolism, 5.0)
    # Need n half-lives to reach 25% remaining: (1/2)^n = 0.25 => n=2
    n = 2
    cutoff_hours = hl * n
    last_cup_time = desired_bed_min - int(cutoff_hours*60)
    # Safety bump if total dose is high
    if total_mg >= 200:
        last_cup_time -= 60
    return last_cup_time


def nap_gate(wake_min):
    """Nap gate: 6-8 hours after wake, 15–25 min or 90 min."""
    start = wake_min + 6*60
    end = wake_min + 8*60
    return start, end


def light_budget(wake_min, bed_min, chronotype_idx):
    """Return morning bright-light minutes and evening dim hours target."""
    # Longer morning light if later chronotype
    morning_min = int(20 + (1-chronotype_idx)*40)  # 20–60 min
    # Evening dim target: 1.5–3.0h before bed depending on chronotype
    dim_minutes = int(90 + (1-chronotype_idx)*60)
    return morning_min, dim_minutes


def two_process_sim(today_wake, today_bed_guess, caffeine_events, nap_events):
    """Very simplified two-process model (educational):
    - Process S increases while awake, decays during sleep
    - Process C: sine wave across 24h giving alertness windows
    Return time series for plotting.
    """
    dt = 10  # minutes
    tmins = np.arange(0, 24*60, dt)
    # Process C: shifted sine. Peak ~ 10:00 & 19:00, dip ~ 14:30 & 03:00
    phase_shift = 9*60
    C = 0.5 + 0.5*np.sin(2*np.pi*(tmins - phase_shift)/(24*60))

    # Process S parameters
    tau_wake = 14*60  # time constant building
    tau_sleep = 4*60  # decay constant

    S = np.zeros_like(tmins, dtype=float)
    asleep = np.zeros_like(tmins, dtype=bool)

    def in_sleep(t):
        # treat bed_guess as center; assume 90-min cycles; approximate 7.5h sleep
        bed = today_bed_guess
        wake = (today_bed_guess + int(7.5*60)) % (24*60)
        # handle wrap
        tm = t % (24*60)
        if bed < wake:
            return bed <= tm < wake
        else:
            return tm >= bed or tm < wake

    # Caffeine effect: temporary reduce S by small fraction for 2–4h depending on dose
    caffeine_effect = np.zeros_like(tmins, dtype=float)
    for t_event, mg in caffeine_events:
        dur = 120 + min(180, int(mg*1.5))  # 2h + scaled
        for i, t in enumerate(tmins):
            dtm = (t - t_event) % (24*60)
            if 0 <= dtm <= dur:
                caffeine_effect[i] += 0.07 * (mg/100) * (1 - dtm/dur)
    # Nap effect: drop S by portion during nap window
    nap_mask = np.zeros_like(tmins, dtype=bool)
    for nstart, nend in nap_events:
        for i, t in enumerate(tmins):
            tm = t % (24*60)
            if nstart < nend:
                nap_mask[i] |= (nstart <= tm < nend)
            else:
                nap_mask[i] |= (tm >= nstart or tm < nend)

    S_val = 0.4  # start pressure mid-level
    for i in range(len(tmins)):
        tm = tmins[i]
        if in_sleep(tm) or nap_mask[i]:
            asleep[i] = True
            # exponential decay
            S_val += (0 - S_val) * (dt/tau_sleep)
        else:
            # build toward 1.0
            S_val += (1.0 - S_val) * (dt/tau_wake)
        # caffeine lowers perceived S slightly
        S[i] = max(0, S_val - caffeine_effect[i])

    alertness = 0.6*C + 0.4*(1 - S)  # higher is better
    return tmins, S, C, alertness

# ----------------------------
# Inputs
# ----------------------------
with st.sidebar:
    st.header("입력")
    st.subheader("📅 평일 루틴")
    w_bed = hm_to_minutes(st.text_input("평일 취침 시각 (HH:MM)", "23:30"))
    w_wake = hm_to_minutes(st.text_input("평일 기상 시각 (HH:MM)", "07:00"))
    st.subheader("🗓️ 주말/자유일 루틴")
    f_bed = hm_to_minutes(st.text_input("자유일 취침 시각 (HH:MM)", "00:30"))
    f_wake = hm_to_minutes(st.text_input("자유일 기상 시각 (HH:MM)", "08:30"))

    st.subheader("☕ 카페인")
    caffeine_mg = st.slider("하루 총 카페인 섭취량 (mg)", 0, 600, 150, 25)
    metabolism = st.selectbox("카페인 대사 속도", ["빠름", "보통", "느림"], index=1)
    last_caffeine_time_user = st.text_input("마지막 카페인 섭취 시각(선택)", "15:00")

    st.subheader("😪 수면 목표")
    target_duration = st.slider("목표 수면 시간 (h)", 6.0, 9.0, 7.5, 0.5)

# Derived metrics
msfsc, mid_work, mid_free, d_work, d_free, need = msf_corrected(w_bed, w_wake, f_bed, f_wake)
chronotype_idx = circadian_phase_score(w_wake)
social_jetlag = abs(mid_work - msfsc)
sjl_hours = round(social_jetlag/60, 2)

# Recommend consistent bedtime aligned to MSFsc & duration
recommended_bed = int((msfsc - (target_duration*60)/2) % (24*60))
recommended_wake = int((recommended_bed + target_duration*60) % (24*60))

# Caffeine & naps & light
last_safe_caf = caffeine_cutoff(recommended_bed, metabolism, caffeine_mg)
nap_start, nap_end = nap_gate(w_wake)
m_light, dim_mins = light_budget(w_wake, w_bed, chronotype_idx)

# ----------------------------
# Header KPIs
# ----------------------------
k1, k2, k3, k4 = st.columns(4)
k1.metric("MSFsc (교정 자유일 중간수면)", minutes_to_hm(int(msfsc)))
k2.metric("사회적 시차(SJL)", f"{sjl_hours} h")
k3.metric("추천 취침", minutes_to_hm(recommended_bed))
k4.metric("추천 기상", minutes_to_hm(recommended_wake))

st.markdown("---")

# ----------------------------
# Unique Feature 1: Light Budget Planner
# ----------------------------
st.subheader("🌞 Light Budget Planner — ‘아침 밝게 / 밤엔 어둡게’")
colA, colB = st.columns(2)
with colA:
    st.write("**아침 ‘밝은 빛’ 노출 목표**")
    st.success(f"기상 후 1시간 내 야외 밝은 빛 {m_light}–{m_light+10}분")
    st.caption("만약 실내라면 멜라토닉 럭스 기준 충분한 밝기가 어려우므로 시간을 1.5–2배로 늘리세요.")
with colB:
    st.write("**저녁 ‘디밍(빛 줄이기)’ 목표**")
    st.info(f"취침 전 {int(dim_mins/60)}시간 {dim_mins%60:02.0f}분 동안 밝은 스크린/천장등 회피 → 간접 조명")
    st.caption("푸른빛(블루라이트) ↓, 화면 밝기 ↓, 나이트시프트/블루필터 사용 권장")

# ----------------------------
# Unique Feature 2: Caffeine Curfew & Nap Gate
# ----------------------------
st.subheader("☕ Caffeine Curfew & 😴 Nap Gate")
col1, col2, col3 = st.columns(3)
with col1:
    st.write("**권장 마지막 카페인 시각**")
    st.warning(f"{minutes_to_hm(last_safe_caf)} (대사속도 '{metabolism}', 2반감기 기준)")
with col2:
    st.write("**입력된 마지막 카페인**")
    last_user_min = hm_to_minutes(last_caffeine_time_user, default="15:00")
    delta = ((recommended_bed - last_user_min) % (24*60))/60
    if caffeine_mg==0:
        st.success("오늘은 카페인 섭취 없음 — 수면에 유리")
    elif delta < 6:
        st.error("취침까지 6시간 미만 — 수면 방해 가능성 ↑")
    else:
        st.success("취침까지 6시간 이상 — 비교적 안전")
with col3:
    st.write("**파워냅 게이트**")
    st.info(f"{minutes_to_hm(nap_start)}–{minutes_to_hm(nap_end)} (15–25분 또는 90분)")

# ----------------------------
# Unique Feature 3: Social Jetlag Minimizer (7‑day micro‑shift)
# ----------------------------
st.subheader("🧭 Social Jetlag Minimizer — 7일 미세 조정 플랜")
shift_needed = int(((recommended_bed - w_bed) % (24*60)))
if shift_needed > 12*60:
    shift_needed -= 24*60
step = max(-30, min(30, int(round(shift_needed/7/5)*5)))  # ±30분/일 제한, 5분 단위
plan = []
current_bed = w_bed
for d in range(7):
    current_bed = (current_bed + step) % (24*60)
    current_wake = (current_bed + target_duration*60) % (24*60)
    plan.append({"Day": d+1, "Bed": minutes_to_hm(int(current_bed)), "Wake": minutes_to_hm(int(current_wake))})

st.dataframe(pd.DataFrame(plan))

# ----------------------------
# Unique Feature 4: Two‑Process Simulation & Today’s Optimal Window
# ----------------------------
st.subheader("📈 두‑프로세스 시뮬레이션 (교육용 모델)")

# Build caffeine events (assume last dose time and total dose split)
if caffeine_mg > 0:
    doses = max(1, caffeine_mg // 100)
    spacing = 120
    last_dose = hm_to_minutes(last_caffeine_time_user, default="15:00")
    events = []
    for i in range(doses):
        t = (last_dose - i*spacing) % (24*60)
        events.append((t, min(150, caffeine_mg//doses)))
else:
    events = []

# Nap events (proposed 20 min inside gate)
nap_events = [(nap_start+20, nap_start+40)] if (nap_end - nap_start) >= 40 else []

# Simulate around today
_, S, C, A = two_process_sim(w_wake, recommended_bed, events, nap_events)
mins = np.arange(0, 24*60, 10)

fig = go.Figure()
fig.add_trace(go.Scatter(x=[minutes_to_hm(int(m)) for m in mins], y=S, name="Process S (sleep pressure)", mode="lines"))
fig.add_trace(go.Scatter(x=[minutes_to_hm(int(m)) for m in mins], y=C, name="Process C (circadian)", mode="lines"))
fig.add_trace(go.Scatter(x=[minutes_to_hm(int(m)) for m in mins], y=A, name="Alertness (higher better)", mode="lines"))
fig.update_layout(height=380, margin=dict(l=10,r=10,t=30,b=10), xaxis_title="시간", yaxis_title="정규화 지수 (0–1)")
st.plotly_chart(fig, use_container_width=True)

# Find optimal sleep start in next 24h: high S & low C crossing window
best_bed = recommended_bed
best_score = -1e9
for cand in range(0, 24*60, 10):
    # score: high S at bed, increasing C by wake time
    idx = cand//10
    wake_idx = (idx + int(target_duration*60)//10) % len(mins)
    score = (S[idx] - 0.5*C[idx]) + (C[wake_idx] - 0.5*S[wake_idx])
    if score > best_score:
        best_score = score
        best_bed = cand

st.markdown(
    f"**오늘의 최적 수면 창**: {minutes_to_hm(best_bed)} → {minutes_to_hm((best_bed + int(target_duration*60))%(24*60))}  ")

# ----------------------------
# Actionable Checklist
# ----------------------------
st.markdown("---")
st.subheader("✅ 오늘 실행 체크리스트")
st.markdown(
    f"- 기상 후 1시간 내 야외 빛 **{m_light}–{m_light+10}분**\n"
    f"- 취침 전 **{int(dim_mins/60)}시간 {dim_mins%60:02.0f}분** 디밍(간접등/낮은 조도)\n"
    f"- 마지막 카페인 **{minutes_to_hm(last_safe_caf)} 이전** (현재 입력: {minutes_to_hm(last_user_min)})\n"
    f"- 파워냅은 **{minutes_to_hm(nap_start)}–{minutes_to_hm(nap_end)}** 내 15–25분\n"
    f"- 7일 미세 조정: 매일 취침 시각 **{abs(step)}분 {'앞당기기' if step<0 else '늦추기'}**\n"
    f"- 목표 수면 시간 **{target_duration:.1f}h** 유지"
)

st.caption("면책: 본 앱은 연구/교육용 가이드이며 의학적 진단이나 치료를 대체하지 않습니다.")
