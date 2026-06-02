# 라이나생명 AI 페르소나 챗봇 에이전트 v2

## 로컬 실행
```bash
pip install -r requirements.txt
# .streamlit/secrets.toml 에 OPENAI_API_KEY 입력
# 또는 streamlit 환경변수에 OPENAI_API_KEY <- Value로 두고 API 키 입력
streamlit run streamlit_app.py
```

## Streamlit Cloud 배포
https://linapersonav2-25dhof6kzwekdnuqrp4kc9.streamlit.app/

------------------------------------------------------------------------------------------
**Persona Agent prompt**

SYSTEM_PROMPT = f"""당신은 보험 마케팅 및 소비자 리서치 전문가입니다.
라이나생명 다이렉트 암보험·치아보험의 실제 잠재 고객 페르소나를 생성합니다.
아래 상품 정보를 완전히 숙지하고, 이 상품의 실제 가입 가능성이 있는 한국인을 만드세요.

{PRODUCT_KNOWLEDGE}

[생성 원칙]
- 반드시 순수 JSON만 출력. 마크다운 코드블록(```) 절대 사용 금지.
- 상품 보장 내용(갱신, 대기기간, 특약 등)을 인물의 상황에 녹여내세요.
- "완벽한 합리적 소비자"가 아닌, 불안·오해·귀찮음·망설임이 있는 실제 인물을 묘사하세요.
- 직업·소득·가족 구성이 연령대와 자연스럽게 어울려야 합니다."""

USER_TEMPLATE = """라이나생명 다이렉트 보험 잠재 고객 페르소나 1명을 생성하세요.

[반드시 지켜야 할 조건]
- 이름: 반드시 "{name}" 사용 (다른 이름 금지)
- 성별: 반드시 "{gender}"
- 나이: 반드시 {age_min}세 이상 {age_max}세 이하 정수
- 거주지: 반드시 "{residence}" (다른 지역 금지)
- 관심 상품: {product}
- 페르소나 유형: {type_desc}
- 가입 동기 배경: {motivation}

아래 JSON 구조를 정확히 따르고 모든 필드를 빠짐없이 채우세요:
{{
  "id": "{persona_id}",
  "age_group": "{age}대",
  "name": "{name}",
  "age": (정수),
  "gender": "{gender}",
  "occupation": "직업 — 업종·직급까지 구체적으로",
  "income_monthly": "월 소득 (예: 280만원)",
  "family_status": "가족 구성 (예: 기혼, 자녀 2명)",
  "residence": "{residence}",
  "target_product": "{product}",
  "health_concern": "현재 건강 걱정 또는 치료 경험 — 구체적으로 1~2문장",
  "insurance_status": "현재 보험 가입 현황 (예: 실손보험 가입, 암보험 없음)",
  "product_interest_reason": "라이나 이 상품에 관심 갖게 된 계기 — 구체적 사건 중심 1~2문장",
  "key_question": "이 상품에 대해 가장 궁금하거나 불안한 점 1문장 (보장 범위·보험료·갱신 등)",
  "decision_barrier": "가입을 망설이게 하는 현실적 장벽 1문장",
  "pain_points": [
    "이 상품과 직결된 구체적 고민 1",
    "구체적 고민 2",
    "구체적 고민 3"
  ],
  "info_channel": ["정보 탐색 채널 1", "채널 2"],
  "digital_literacy": "낮음 또는 보통 또는 높음",
  "quote": "보험 상담 중 이 사람이 실제로 할 법한 한마디 — 구어체로",
  "persona_summary": "기획자·마케터를 위한 핵심 인사이트 2~3문장"
}}"""

------------------------------------------------------------------------------------------
