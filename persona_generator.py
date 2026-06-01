"""
암보험·치아보험 관심 소비자 페르소나 생성기
- GPT-4o-mini 사용
- 30/40/50/60대 각 3명, 총 12명
- 특정 보험사 브랜드 없음 — 일반 소비자 관점
- 이름·거주지·성별 중복 방지 + 자동 품질 검증
- 결과: personas_insurance.json + personas_insurance.md
"""

import os, json, time
from openai import OpenAI

# ────────────────────────────────────────────────
# 설정
# ────────────────────────────────────────────────
API_KEY     = os.getenv("OPENAI_API_KEY", "YOUR_API_KEY_HERE")
MODEL       = "gpt-4o-mini"
AGE_GROUPS  = [30, 40, 50, 60]
PER_GROUP   = 3
MAX_RETRY   = 3
OUTPUT_JSON = "personas_insurance.json"
OUTPUT_MD   = "personas_insurance.md"

# ────────────────────────────────────────────────
# 다양성 풀
# ────────────────────────────────────────────────
NAME_POOL = {
    "남": ["박준호", "이재원", "정성민", "최동욱", "한승훈",
           "오병철", "윤태양", "신현우", "임도현", "강민준"],
    "여": ["이수연", "박지영", "정미경", "최은지", "한혜진",
           "오소현", "윤아름", "신다은", "임지현", "강보람"],
}
RESIDENCE_POOL = [
    "서울 마포구", "서울 은평구", "서울 노원구", "서울 송파구",
    "서울 강서구", "경기 수원시", "경기 성남시", "경기 고양시",
    "경기 용인시", "인천 부평구", "부산 해운대구", "부산 남구",
    "대구 달서구", "대전 유성구", "광주 북구",
]
GENDER_PLAN = {
    30: ["남", "여", "여"],
    40: ["남", "여", "남"],
    50: ["남", "여", "남"],
    60: ["여", "남", "여"],
}

# ────────────────────────────────────────────────
# 상품 도메인 지식 — 브랜드 없는 일반 정보
# ────────────────────────────────────────────────
PRODUCT_KNOWLEDGE = """
=== 암보험 일반 상식 ===
- 주요 보장: 일반암 진단비(최초1회), 유사암(갑상선암·피부암·제자리암·경계성종양) 진단비
- 선택특약: 고액암 진단비, 표적항암약물 치료비, 항암방사선·약물 치료비, 암 생활비(매월)
- 갱신형 vs 비갱신형: 갱신형은 초기 보험료 낮지만 갱신 시 인상 / 비갱신형은 보험료 고정
- 보장개시일: 계약일로부터 통상 90일 이후 암 보장 시작
- 다이렉트(온라인) 가입: 설계사 수수료 없어 보험료 절감 가능
- 실손보험과 역할 차이: 실손은 치료비 일부 보전 / 암보험은 진단 시 목돈 지급

=== 치아보험 일반 상식 ===
- 주계약 보장: 충전(레진·아말감), 크라운, 스케일링(연1회), 신경치료, 영구치 발거
- 선택특약: 임플란트, 브릿지, 틀니, 재식립 임플란트
- 보장개시일: 가입 후 통상 90~91일부터 보장 시작 (즉시 치료받으면 보장 안 됨)
- 보철치료 주의: 가입 후 2년 이내 영구치 발거 시 보험금 50%만 지급하는 경우 많음
- 연간 한도: 보험사마다 상이 / 임플란트·브릿지는 연간 개수 제한 있음
- 나이 제한: 대부분 0세~60~70세까지 가입 가능
"""

# ────────────────────────────────────────────────
# 연령대별 페르소나 유형 설계
# ────────────────────────────────────────────────
PERSONA_CONFIGS = {
    30: [
        {
            "product": "암보험",
            "type_desc": "사회초년생 — 처음으로 암보험 필요성을 느끼기 시작한 직장인",
            "motivation": (
                "건강검진에서 이상 소견이 나왔거나 부모님이 암 진단을 받은 이후 "
                "처음으로 암보험 가입을 진지하게 고민하기 시작함. "
                "보험료 부담이 크지 않은 온라인 상품에 관심을 가지며 "
                "어떤 보장 항목을 우선순위로 봐야 할지 모르는 상태."
            ),
        },
        {
            "product": "암보험+치아보험",
            "type_desc": "결혼 준비 중인 여성 — 가족력으로 암보험, 잦은 치과 방문으로 치아보험 동시 고민",
            "motivation": (
                "어머니가 유방암 진단 이력이 있어 암보험은 필수라고 생각. "
                "치아가 좋지 않아 충전·크라운 치료를 자주 받아왔으며, "
                "결혼 전 보험을 정리하면서 두 상품을 함께 알아보는 중."
            ),
        },
        {
            "product": "치아보험",
            "type_desc": "맞벌이 부부 — 아이와 본인 모두 치과비 부담으로 치아보험 가입 검토",
            "motivation": (
                "아이 충치가 잦고 본인도 크라운 치료를 앞두고 있어 "
                "치과비가 한 달에 수십만 원씩 나오는 상황. "
                "가족 모두 가입 가능한 치아보험을 비교 중이며 "
                "스케일링·충전까지 보장되는 범위가 얼마나 되는지 궁금해함."
            ),
        },
    ],
    40: [
        {
            "product": "암보험",
            "type_desc": "자녀 교육비 부담 속 건강 걱정이 커진 직장인 남성",
            "motivation": (
                "주변 또래 지인이 대장암 진단을 받으면서 불안감이 급증. "
                "직장 단체보험만 있고 개인 암보험은 없는 상태. "
                "표적항암치료비 보장 여부와 갱신 시 보험료 인상 폭이 가장 걱정됨."
            ),
        },
        {
            "product": "암보험+치아보험",
            "type_desc": "프리랜서 여성 — 단체보험 없이 본인이 직접 건강보험을 챙겨야 하는 상황",
            "motivation": (
                "직장 단체보험이 없어 실손보험 외에는 보장이 없는 상태. "
                "최근 잇몸 치료로 치과비가 많이 나왔고 임플란트도 조만간 필요할 것 같아 "
                "암보험과 치아보험을 동시에 알아보고 있음. "
                "온라인 가입으로 보험료를 낮출 수 있다는 점에 끌림."
            ),
        },
        {
            "product": "암보험",
            "type_desc": "고소득 전문직 — 실손 외에 암 진단 시 소득 공백을 대비한 추가 보장 검토",
            "motivation": (
                "실손·종신보험이 이미 있지만 암 진단 시 치료 기간 동안 "
                "일을 못 하게 됐을 때 소득 공백이 걱정됨. "
                "암 생활비 특약과 고액암 진단비 보장에 관심이 많으며 "
                "여러 상품을 꼼꼼히 비교하고 합리적으로 결정하는 스타일."
            ),
        },
    ],
    50: [
        {
            "product": "암보험",
            "type_desc": "은퇴 준비 직장인 — 기존 갱신형 암보험 보험료 급등으로 더 저렴한 상품 탐색 중",
            "motivation": (
                "10년 전 가입한 갱신형 암보험이 갱신되면서 보험료가 거의 2배로 올랐음. "
                "보험료를 줄이면서도 위암·대장암·폐암 보장은 유지하고 싶어 "
                "온라인 다이렉트 상품을 비교 중. "
                "갱신형이라 또 오를까봐 비갱신형도 함께 검토 중."
            ),
        },
        {
            "product": "치아보험",
            "type_desc": "50대 여성 — 임플란트·브릿지 치료를 앞두고 치아보험 가입 시기 고민",
            "motivation": (
                "치과 의사에게 임플란트 2개와 브릿지 치료가 필요하다는 말을 들었음. "
                "예상 치료비가 400~500만 원이라 치아보험을 미리 가입하고 싶지만 "
                "대기 기간과 2년 이내 발거 시 50% 보장 조건 때문에 "
                "언제 가입해야 유리한지 헷갈려하고 있음."
            ),
        },
        {
            "product": "암보험",
            "type_desc": "퇴직 후 재취업 준비 중인 남성 — 단체보험 상실로 개인 암보험 필요성 절감",
            "motivation": (
                "작년 퇴직으로 직장 단체보험이 사라짐. "
                "소득이 줄어든 상황에서 보험료 부담을 최소화하면서도 "
                "암 보장은 유지하고 싶어 온라인 상품을 찾고 있음. "
                "50대에도 가입 가능한지, 갱신 시 보험료가 얼마나 오를지 확인이 필요함."
            ),
        },
    ],
    60: [
        {
            "product": "치아보험",
            "type_desc": "막 은퇴한 여성 — 치과 치료비 부담이 최우선 고민, 복잡한 가입 절차가 어려움",
            "motivation": (
                "은퇴 후 치과비가 부쩍 부담스러워졌음. "
                "틀니와 임플란트 치료를 앞두고 있어 치아보험 필요성을 절감. "
                "인터넷 검색은 어렵게 느껴져 지인 추천이나 전화 상담을 선호함."
            ),
        },
        {
            "product": "암보험",
            "type_desc": "건강 관리에 관심 많은 60대 남성 — 과거 암 치료 이력으로 보험 보강 필요",
            "motivation": (
                "수년 전 갑상선암 수술을 받고 완치 판정을 받았으나 재발 불안이 큼. "
                "기존 보험 보장이 부족하다고 느끼고 유사암 보장과 "
                "기존 병력이 있어도 가입 가능한 간편심사 상품에 관심."
            ),
        },
        {
            "product": "치아보험",
            "type_desc": "활동적인 60대 여성 — 손자녀와 본인 치아 건강을 함께 챙기고 싶어함",
            "motivation": (
                "손자 충치 치료비가 자주 발생하고 본인도 스케일링·잇몸 치료를 정기적으로 받음. "
                "영유아부터 가입 가능한 치아보험으로 손자와 함께 가입하고 싶어함. "
                "스케일링 보장 범위와 나이가 많아도 보험료가 너무 비싸지 않은지 궁금해함."
            ),
        },
    ],
}

# ────────────────────────────────────────────────
# 시스템 프롬프트
# ────────────────────────────────────────────────
SYSTEM_PROMPT = f"""당신은 보험 마케팅 및 소비자 리서치 전문가입니다.
암보험·치아보험에 관심 있는 한국 소비자의 현실적인 페르소나를 생성합니다.
특정 보험사 브랜드는 언급하지 않으며, 일반 소비자의 시각에서 작성합니다.
아래 상품 도메인 지식을 참고해 현실감 있는 인물을 만드세요.

{PRODUCT_KNOWLEDGE}

[생성 원칙]
- 반드시 순수 JSON만 출력. 마크다운 코드블록(```) 절대 금지.
- 특정 보험사 이름(라이나, 삼성, 한화 등) 언급 금지. 상품 유형(암보험, 치아보험)만 언급.
- 보험 도메인 지식(갱신, 대기기간, 특약 등)을 인물 상황에 자연스럽게 녹여낼 것.
- "완벽한 합리적 소비자"가 아닌 불안·오해·귀찮음·망설임이 있는 실제 인물을 묘사할 것.
- 직업·소득·가족 구성이 연령대와 자연스럽게 어울려야 함."""

# ────────────────────────────────────────────────
# 유저 프롬프트 템플릿
# ────────────────────────────────────────────────
USER_TEMPLATE = """암보험·치아보험에 관심 있는 소비자 페르소나 1명을 생성하세요.

[반드시 지켜야 할 조건]
- 이름: 반드시 "{name}" 사용
- 성별: 반드시 "{gender}"
- 나이: 반드시 {age_min}~{age_max}세 사이 정수
- 거주지: 반드시 "{residence}"
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
  "occupation": "직업 — 업종·직급 포함",
  "income_monthly": "월 소득 (예: 280만원)",
  "family_status": "가족 구성 (예: 기혼, 자녀 2명)",
  "residence": "{residence}",
  "target_product": "{product}",
  "health_concern": "현재 건강 걱정 또는 치료 경험 — 구체적으로 1~2문장",
  "insurance_status": "현재 보험 가입 현황 (예: 실손보험 가입, 암보험 없음)",
  "product_interest_reason": "이 보험에 관심 갖게 된 구체적 계기 1~2문장",
  "key_question": "보험에 대해 가장 궁금하거나 불안한 점 1문장",
  "decision_barrier": "가입을 망설이게 하는 현실적 장벽 1문장",
  "pain_points": [
    "이 보험과 직결된 구체적 고민 1",
    "구체적 고민 2",
    "구체적 고민 3"
  ],
  "info_channel": ["정보 탐색 채널 1", "채널 2"],
  "digital_literacy": "낮음 또는 보통 또는 높음",
  "quote": "보험 얘기할 때 이 사람이 실제로 할 법한 한마디 — 구어체",
  "persona_summary": "기획자·마케터를 위한 핵심 인사이트 2~3문장"
}}"""

# ────────────────────────────────────────────────
# 생성 함수
# ────────────────────────────────────────────────
def generate_persona(client, age, index, name, gender, residence):
    cfg    = PERSONA_CONFIGS[age][index]
    prompt = USER_TEMPLATE.format(
        persona_id = f"{age}_{index + 1}",
        age        = age,
        age_min    = age,
        age_max    = age + 9,
        name       = name,
        gender     = gender,
        residence  = residence,
        product    = cfg["product"],
        type_desc  = cfg["type_desc"],
        motivation = cfg["motivation"],
    )
    resp = client.chat.completions.create(
        model    = MODEL,
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt},
        ],
        temperature = 0.85,
        max_tokens  = 1000,
    )
    raw = resp.choices[0].message.content.strip()
    if "```" in raw:
        for part in raw.split("```"):
            part = part.strip().lstrip("json").strip()
            if part.startswith("{"):
                raw = part
                break
    return json.loads(raw.strip())

# ────────────────────────────────────────────────
# 품질 검증
# ────────────────────────────────────────────────
def validate(p, age, name, gender, residence):
    errors = []
    if p.get("name")      != name:      errors.append(f"이름 불일치: {p.get('name')}")
    if p.get("gender")    != gender:    errors.append(f"성별 불일치: {p.get('gender')}")
    if p.get("residence") != residence: errors.append(f"거주지 불일치: {p.get('residence')}")
    if not (age <= (p.get("age") or 0) <= age + 9):
        errors.append(f"나이 범위 오류: {p.get('age')}")
    required = ["occupation", "income_monthly", "family_status", "health_concern",
                "insurance_status", "product_interest_reason", "key_question",
                "decision_barrier", "pain_points", "quote", "persona_summary"]
    for f in required:
        if not p.get(f):
            errors.append(f"필드 누락: {f}")
    return errors

# ────────────────────────────────────────────────
# 마크다운 변환
# ────────────────────────────────────────────────
def to_markdown(p):
    pain = "\n".join(f"  - {pt}" for pt in p.get("pain_points", []))
    ch   = ", ".join(p.get("info_channel", []))
    return f"""---

## [{p['age_group']}] {p['name']} ({p['age']}세, {p['gender']}) · {p.get('target_product','')}

| 항목 | 내용 |
|------|------|
| 직업 | {p.get('occupation','')} |
| 월 소득 | {p.get('income_monthly','')} |
| 가족 | {p.get('family_status','')} |
| 거주지 | {p.get('residence','')} |
| 보험 현황 | {p.get('insurance_status','')} |
| 디지털 리터러시 | {p.get('digital_literacy','')} |

**건강 고민**
> {p.get('health_concern','')}

**관심 계기**
{p.get('product_interest_reason','')}

**가장 궁금한 점**
{p.get('key_question','')}

**가입 망설임**
{p.get('decision_barrier','')}

**주요 고민**
{pain}

**정보 탐색 채널** : {ch}

**한마디**
> "{p.get('quote','')}"

**기획 인사이트**
{p.get('persona_summary','')}
"""

# ────────────────────────────────────────────────
# 메인
# ────────────────────────────────────────────────
def main():
    client = OpenAI(api_key=API_KEY)

    used_names, used_res = set(), set()

    def pick_name(g):
        for n in NAME_POOL[g]:
            if n not in used_names:
                used_names.add(n); return n
        raise RuntimeError(f"{g} 이름 풀 부족")

    def pick_res():
        for r in RESIDENCE_POOL:
            if r not in used_res:
                used_res.add(r); return r
        raise RuntimeError("거주지 풀 부족")

    all_personas = []
    total = len(AGE_GROUPS) * PER_GROUP
    count = 0

    print("=" * 60)
    print(" 암보험·치아보험 소비자 페르소나 생성기")
    print(f" 모델: {MODEL}  |  총 {total}명")
    print("=" * 60)

    for age in AGE_GROUPS:
        print(f"\n── {age}대 ──")
        for i in range(PER_GROUP):
            count    += 1
            gender    = GENDER_PLAN[age][i]
            name      = pick_name(gender)
            residence = pick_res()
            cfg       = PERSONA_CONFIGS[age][i]

            print(f"  [{count:02d}/{total}] {name} ({gender}) | {cfg['product']} | {cfg['type_desc'][:22]}...")

            persona = None
            for attempt in range(1, MAX_RETRY + 1):
                try:
                    p    = generate_persona(client, age, i, name, gender, residence)
                    errs = validate(p, age, name, gender, residence)
                    if errs:
                        print(f"         ↳ 시도 {attempt} 검증 실패 → 강제 보정: {errs[0]}")
                        p["name"] = name; p["gender"] = gender
                        p["residence"] = residence; p["age_group"] = f"{age}대"
                        if not (age <= (p.get("age") or 0) <= age + 9):
                            p["age"] = age + 4
                    persona = p
                    print(f"         ✓ {p['name']} / {p.get('occupation','')[:24]}")
                    break
                except json.JSONDecodeError as e:
                    print(f"         ↳ 시도 {attempt} JSON 오류: {e}")
                except Exception as e:
                    print(f"         ↳ 시도 {attempt} 오류: {e}")
                time.sleep(1)

            if persona:
                all_personas.append(persona)
            else:
                print(f"         ✗ {MAX_RETRY}회 실패, 스킵")

            if count < total:
                time.sleep(0.5)

    print("\n" + "=" * 60)
    names = [p["name"] for p in all_personas]
    dup_n = {n for n in names if names.count(n) > 1}
    ress  = [p["residence"] for p in all_personas]
    dup_r = {r for r in ress if ress.count(r) > 1}
    print(f" 생성 완료 : {len(all_personas)} / {total}명")
    print(f" 이름 중복 : {dup_n if dup_n else '없음'}")
    print(f" 거주지 중복: {dup_r if dup_r else '없음'}")

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(all_personas, f, ensure_ascii=False, indent=2)
    print(f"\n ✓ JSON: {OUTPUT_JSON}")

    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write("# 암보험·치아보험 관심 소비자 페르소나\n\n")
        f.write(f"> 모델: {MODEL} | 30~60대 각 {PER_GROUP}명 | 총 {len(all_personas)}명\n")
        for age in AGE_GROUPS:
            group = [p for p in all_personas if p["age_group"] == f"{age}대"]
            if group:
                f.write(f"\n\n# {age}대\n")
                for p in group:
                    f.write(to_markdown(p))
    print(f" ✓ Markdown: {OUTPUT_MD}")
    print("\n 완료! → python streamlit_app.py 로 챗봇 실행")
    print("=" * 60)

if __name__ == "__main__":
    main()
