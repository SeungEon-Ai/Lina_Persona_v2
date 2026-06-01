"""
라이나생명 다이렉트 암보험·치아보험 페르소나 챗봇
Streamlit Cloud 배포용
"""

import json, os
import streamlit as st
from openai import OpenAI

# ── 설정 ──────────────────────────────────────────────────────────────────────
PAGE_TITLE = "라이나생명 페르소나 에이전트"
JSON_PATH  = os.path.join(os.path.dirname(__file__), "personas_lina.json")
MODEL      = "gpt-4o-mini"

PRODUCT_KNOWLEDGE = """
[라이나생명 다이렉트 암보험]
- 상품명: (무)라이나다이렉트암보험(갱신형) / 가입 20~50세 / 10년만기 갱신형 / 최대 100세
- 일반암 진단비 1,000~5,000만원(최초1회), 유방암·전립선암 일반암과 동일 보장
- 유사암(갑상선암·피부암·제자리암·경계성종양) 별도 보장
- 특약: 7대 고액암 진단비, 비급여 표적항암약물 치료비, 항암방사선·약물 치료비, 암 생활비
- 계약일로부터 90일 이후 암보장 개시 / 갱신 시 보험료 인상 가능

[라이나생명 다이렉트 치아보험]
- 상품명: (무)THE건강한치아보험V(갱신형) / 가입 0~70세
- 주계약: 충전치료, 크라운, 스케일링(연1회), 신경치료, 영구치 발거
- 특약: 임플란트(영구치 발거 후), 브릿지(연간 3개 한도), 틀니(연1회), 재식립 임플란트
- 가입 후 91일째부터 보장 개시 / 보철치료 2년 이내 발거 시 50% 지급
"""

AGE_COLORS = {
    "30대": "#1a6fa8",
    "40대": "#1a7a32",
    "50대": "#a05c00",
    "60대": "#a82020",
}
PRODUCT_COLORS = {
    "암보험":       "#a82020",
    "치아보험":     "#1a6fa8",
    "암보험+치아보험": "#6b30a8",
}

# ── 페르소나 로드 ──────────────────────────────────────────────────────────────
@st.cache_data
def load_personas():
    with open(JSON_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return {p["id"]: p for p in data}

# ── 시스템 프롬프트 ────────────────────────────────────────────────────────────
def build_system_prompt(p):
    pain     = ", ".join(p.get("pain_points", []))
    channels = ", ".join(p.get("info_channel", []))
    return f"""당신은 아래 페르소나를 완벽하게 연기하는 챗봇입니다.
라이나생명 기획자·마케터의 질문에 이 인물의 실제 보험 경험, 감정, 불안, 니즈를 생생하게 표현하세요.

{PRODUCT_KNOWLEDGE}

[페르소나]
- 이름: {p['name']} ({p['age']}세, {p['gender']})
- 직업: {p['occupation']} / 월소득: {p['income_monthly']}
- 가족: {p['family_status']} / 거주: {p['residence']}
- 관심 상품: {p.get('target_product','')}
- 건강 고민: {p.get('health_concern','')}
- 보험 현황: {p.get('insurance_status','')}
- 상품 관심 계기: {p.get('product_interest_reason','')}
- 핵심 궁금증: {p.get('key_question','')}
- 가입 망설임: {p.get('decision_barrier','')}
- 주요 고민: {pain}
- 정보 채널: {channels}
- 디지털 리터러시: {p['digital_literacy']}
- 한마디: "{p.get('quote','')}"

[행동 지침]
1. 항상 1인칭으로 대답하고 스스로를 {p['name']}으로 소개하세요.
2. {p['age']}세 {p['gender']}성의 자연스러운 말투와 감정을 구사하세요.
3. 라이나 암보험·치아보험 보장 내용(갱신, 대기기간, 특약 등)을 이 인물 시각에서 언급하세요.
4. 완벽한 소비자처럼 굴지 말고 불안·귀찮음·오해·망설임을 드러내세요.
5. 모르는 건 "그건 잘 모르겠어요, 상담사한테 물어봐야 할 것 같아요"로 답하세요.
6. 답변은 3~5문장 이내로 간결하게 유지하세요."""

# ── 페이지 설정 ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
[data-testid="stSidebar"] { min-width: 320px; max-width: 320px; }
.persona-card {
    background: #ffffff;
    border: 1px solid #e4e4e0;
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 8px;
    cursor: pointer;
    transition: border-color .15s;
}
.persona-card:hover { border-color: #aaa; }
.badge {
    display: inline-block;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 20px;
    margin-right: 4px;
}
.chat-meta {
    font-size: 12px;
    color: #999;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid #f0f0eb;
}
</style>
""", unsafe_allow_html=True)

# ── API 키 확인 ───────────────────────────────────────────────────────────────
api_key = st.secrets.get("OPENAI_API_KEY", "")
if not api_key:
    st.error("⚠️ Streamlit Cloud → Settings → Secrets에 OPENAI_API_KEY를 등록하세요.")
    st.stop()

client   = OpenAI(api_key=api_key)
PERSONAS = load_personas()

# ── 사이드바: 페르소나 선택 ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"### {PAGE_TITLE}")
    st.caption(f"다이렉트 암보험·치아보험 · {len(PERSONAS)}명")
    st.divider()

    selected_id = st.session_state.get("selected_id", None)

    for age in [30, 40, 50, 60]:
        age_label = f"{age}대"
        group = [p for p in PERSONAS.values() if p["age_group"] == age_label]
        if not group:
            continue

        color = AGE_COLORS[age_label]
        st.markdown(
            f'<span class="badge" style="background:{color}22;color:{color}">{age_label}</span>',
            unsafe_allow_html=True,
        )

        for p in group:
            prod       = p.get("target_product", "")
            prod_color = PRODUCT_COLORS.get(
                prod if prod in PRODUCT_COLORS else
                ("암보험" if "암" in prod else "치아보험"),
                "#666"
            )
            is_selected = selected_id == p["id"]
            border      = f"2px solid {color}" if is_selected else "1px solid #e4e4e0"

            st.markdown(f"""
            <div class="persona-card" style="border:{border}">
              <b style="font-size:14px">{p['name']}</b>
              <span style="font-size:12px;color:#999;margin-left:6px">{p['age']}세 · {p['gender']}</span><br>
              <span style="font-size:12px;color:#666">{p['occupation'][:22]}</span><br>
              <span class="badge" style="margin-top:6px;background:{prod_color}22;color:{prod_color};font-size:10px">{prod}</span>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"대화하기", key=f"btn_{p['id']}"):
                st.session_state.selected_id  = p["id"]
                st.session_state.messages     = []
                st.rerun()

# ── 메인 영역 ─────────────────────────────────────────────────────────────────
selected_id = st.session_state.get("selected_id", None)

if not selected_id:
    st.markdown("## 👈 왼쪽에서 페르소나를 선택하세요")
    st.caption("라이나생명 다이렉트 암보험·치아보험 잠재 고객 12명과 대화할 수 있습니다.")

    # 요약 카드
    cols = st.columns(4)
    for i, age in enumerate([30, 40, 50, 60]):
        age_label = f"{age}대"
        group     = [p for p in PERSONAS.values() if p["age_group"] == age_label]
        color     = AGE_COLORS[age_label]
        with cols[i]:
            st.markdown(f"""
            <div style="background:{color}11;border:1px solid {color}44;
                        border-radius:10px;padding:14px;text-align:center">
              <div style="font-size:20px;font-weight:700;color:{color}">{age}대</div>
              <div style="font-size:13px;color:#666;margin-top:4px">{len(group)}명</div>
            </div>
            """, unsafe_allow_html=True)
    st.stop()

# ── 채팅 화면 ─────────────────────────────────────────────────────────────────
p = PERSONAS[selected_id]
prod        = p.get("target_product", "")
age_color   = AGE_COLORS.get(p["age_group"], "#666")
prod_color  = PRODUCT_COLORS.get(
    prod if prod in PRODUCT_COLORS else
    ("암보험" if "암" in prod else "치아보험"),
    "#666"
)

# 헤더
col1, col2 = st.columns([6, 1])
with col1:
    st.markdown(
        f"### {p['name']} "
        f'<span style="font-size:14px;font-weight:400;color:#999">{p["age"]}세 · {p["gender"]} · {p["occupation"]}</span>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<span class="badge" style="background:{age_color}22;color:{age_color}">{p["age_group"]}</span>'
        f'<span class="badge" style="background:{prod_color}22;color:{prod_color}">{prod}</span>',
        unsafe_allow_html=True,
    )
with col2:
    if st.button("🗑️ 초기화"):
        st.session_state.messages = []
        st.rerun()

st.divider()

# 프로필 expander
with st.expander("📋 페르소나 프로필 보기"):
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**건강 고민**  \n{p.get('health_concern','')}")
        st.markdown(f"**보험 현황**  \n{p.get('insurance_status','')}")
        st.markdown(f"**관심 계기**  \n{p.get('product_interest_reason','')}")
        st.markdown(f"**핵심 궁금증**  \n{p.get('key_question','')}")
    with c2:
        st.markdown(f"**가입 망설임**  \n{p.get('decision_barrier','')}")
        st.markdown(f"**주요 고민**")
        for pt in p.get("pain_points", []):
            st.markdown(f"- {pt}")
        st.markdown(f"**정보 채널**  \n{', '.join(p.get('info_channel',[]))}")
        st.markdown(f"**디지털 리터러시**  \n{p.get('digital_literacy','')}")
    st.info(f'💬 "{p.get("quote","")}"')
    st.markdown(f"**기획 인사이트**  \n{p.get('persona_summary','')}")

# 추천 질문
if not st.session_state.get("messages"):
    st.markdown("**추천 질문**")
    suggestions = []
    if "암보험" in prod:
        suggestions += [
            "암보험 갱신되면 보험료 얼마나 올라요?",
            "갑상선암도 보장이 되나요?",
            "다이렉트로 가입하면 뭐가 다른가요?",
            "암 진단받으면 바로 보험금 나오나요?",
        ]
    if "치아" in prod:
        suggestions += [
            "임플란트는 가입하자마자 보장되나요?",
            "스케일링도 보험 적용이 되나요?",
            "91일 대기기간이면 지금 당장 치료받으면 안 되나요?",
        ]
    suggestions.append("보험 가입할 때 가장 고민됐던 점이 뭐예요?")

    cols = st.columns(min(len(suggestions), 3))
    for i, s in enumerate(suggestions):
        with cols[i % 3]:
            if st.button(s, key=f"sugg_{i}"):
                st.session_state.setdefault("messages", [])
                st.session_state.messages.append({"role": "user", "content": s})
                st.rerun()

# 대화 히스토리 렌더링
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    role  = msg["role"]
    label = "나 (기획자)" if role == "user" else p["name"]
    with st.chat_message(role):
        st.markdown(f"**{label}**")
        st.write(msg["content"])

# 입력창
user_input = st.chat_input(f"{p['name']}에게 질문하세요...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown("**나 (기획자)**")
        st.write(user_input)

    with st.chat_message("assistant"):
        st.markdown(f"**{p['name']}**")
        with st.spinner("입력 중..."):
            messages = [{"role": "system", "content": build_system_prompt(p)}]
            messages += st.session_state.messages[-10:]
            resp  = client.chat.completions.create(
                model=MODEL, messages=messages, temperature=0.9, max_tokens=400
            )
            reply = resp.choices[0].message.content.strip()
        st.write(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
