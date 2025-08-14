# rainbow_mbti.py
import streamlit as st
import random

st.set_page_config(page_title="🌈🦄🎈 MBTI 직업 추천 폭죽!", layout="wide")

# =========================
# 이모지 배경 생성 함수
# =========================
def floating_emoji_layer():
    EMOJIS = list("🦄🐯🐼🐸🐶🐱🐹🐵🐤🦊🦁🐰🦉") + \
             ["🌈","🎈","🍩","🍰","🧁","🍦","🍨","🍫","🍭","🍪","🍓","🍎","🍕","🌮","🍔","🍟",
              "✨","💫","🌟","💖","💎","🎆","🎇","🔥","🎉","🎊","🚀","🌸","🦋","💐"]
    spans = ""
    for i in range(80):
        e = random.choice(EMOJIS)
        left = random.randint(0, 100)
        duration = random.randint(12, 28)
        delay = random.randint(0, 18)
        size = random.randint(24, 60)
        spin = random.choice(["spin1","spin2","spin3"])
        spans += f"<span class='float {spin}' style='left:{left}vw; animation-duration:{duration}s; animation-delay:{delay}s; font-size:{size}px;'>{e}</span>"
    return spans

# =========================
# 배경 스타일 CSS
# =========================
bg_html = f"""
<style>
[data-testid="stAppViewContainer"] {{
  background: linear-gradient(120deg, #ff7af5, #ffd86b, #7af7ff, #a3ff7a);
  background-size: 300% 300%;
  animation: rainbowPulse 12s ease-in-out infinite;
}}
@keyframes rainbowPulse {{
  0% {{ background-position: 0% 50%; }}
  50% {{ background-position: 100% 50%; }}
  100% {{ background-position: 0% 50%; }}
}}
.rainbow-laser {{
  position: fixed; top: 10vh; left: -8vw; font-size: 68px; z-index: 1;
  animation: flyAcross 18s linear infinite;
  text-shadow: 0 0 10px #fff, 0 0 18px #ff66cc;
}}
.rainbow-laser::after {{
  content: " 🌈🌈🌈🌈🌈🌈🌈🌈🌈";
  font-size: 36px; margin-left: 10px;
  filter: drop-shadow(0 0 6px #fff);
}}
@keyframes flyAcross {{
  0%   {{ transform: translateX(0) translateY(0) rotate(0deg); }}
  50%  {{ transform: translateX(55vw) translateY(-6vh) rotate(-5deg); }}
  100% {{ transform: translateX(110vw) translateY(8vh) rotate(4deg); }}
}}
.emoji-sky {{
  position: fixed; inset: 0; overflow: hidden; pointer-events: none; z-index: 0;
}}
.float {{
  position: absolute; top: 110vh; 
  animation-name: floatUp; animation-timing-function: linear; animation-iteration-count: infinite;
  filter: drop-shadow(0 0 6px rgba(255,255,255,0.8));
}}
@keyframes floatUp {{
  0%   {{ transform: translateY(0) rotate(0deg); opacity: 0; }}
  5%   {{ opacity: 1; }}
  95%  {{ opacity: 1; }}
  100% {{ transform: translateY(-130vh) rotate(360deg); opacity: 0; }}
}}
.spin1 {{ animation-name: floatUp, wiggle1; animation-duration: inherit, 6s; animation-iteration-count: infinite, infinite; }}
@keyframes wiggle1 {{ 0%{{transform: translateY(0) rotate(0deg)}} 50%{{transform: translateY(-65vh) rotate(12deg)}} 100%{{transform: translateY(-130vh) rotate(0deg)}} }}
.spin2 {{ animation-name: floatUp, wiggle2; animation-duration: inherit, 7.5s; animation-iteration-count: infinite, infinite; }}
@keyframes wiggle2 {{ 0%{{transform: translateY(0) rotate(0deg)}} 50%{{transform: translateY(-65vh) rotate(-10deg)}} 100%{{transform: translateY(-130vh) rotate(0deg)}} }}
.spin3 {{ animation-name: floatUp, wiggle3; animation-duration: inherit, 9s; animation-iteration-count: infinite, infinite; }}
@keyframes wiggle3 {{ 0%{{transform: translateY(0) rotate(0deg)}} 50%{{transform: translateY(-65vh) rotate(6deg)}} 100%{{transform: translateY(-130vh) rotate(0deg)}} }}
.main-card {{
  background: rgba(255,255,255,0.86);
  border-radius: 28px; padding: 26px 28px;
  box-shadow: 0 18px 45px rgba(0,0,0,.18), inset 0 0 30px rgba(255,255,255,.6);
  backdrop-filter: blur(6px);
  position: relative; z-index: 2;
}}
.glow-title {{
  text-align:center; font-size: 42px; line-height:1.2; margin: 8px 0 18px;
  text-shadow: 0 0 10px #fff, 0 0 18px #ffd86b, 0 0 28px #ff7af5;
}}
</style>
<div class="rainbow-laser">🦄</div>
<div class="emoji-sky">
  {floating_emoji_layer()}
</div>
"""
st.markdown(bg_html, unsafe_allow_html=True)

# =========================
# 제목 및 설명
# =========================
st.markdown(
    "<div class='main-card'>"
    "<h1 class='glow-title'>💼✨🌈 MBTI 기반 직업 추천 🎯🔥🍩🍕🍰🦋🌟🚀</h1>"
    "<p style='text-align:center;'>🦄 무지개를 쏘는 동물과 🎈 풍선, 🍩 맛있는 간식이 화면 가득!<br>당신의 MBTI에 맞는 반짝반짝 직업 추천 💫💎🌟</p>",
    unsafe_allow_html=True
)

# =========================
# MBTI 직업 추천 데이터
# =========================
job_recommendations = {
    "INTJ": ["🔬 연구원", "📊 데이터 분석가", "🏢 전략 컨설턴트"],
    "ENTP": ["🚀 기업가", "🎯 광고 기획자", "⚖ 변호사"],
    "INFJ": ["💖 심리상담사", "✍ 작가", "🌱 사회복지사"],
    "ESTP": ["💼 세일즈 매니저", "🎉 이벤트 플래너", "🏆 스포츠 코치"]
}

# =========================
# 선택 UI
# =========================
mbti = st.selectbox("🌈 당신의 MBTI를 선택하세요", list(job_recommendations.keys()))

if mbti:
    st.subheader(f"✨ {mbti} 추천 직업")
    for job in job_recommendations[mbti]:
        st.write(f"➡️ {job}")
