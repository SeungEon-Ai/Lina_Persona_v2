# 라이나생명 페르소나 챗봇 에이전트

## 로컬 실행
```bash
pip install -r requirements.txt
# .streamlit/secrets.toml 에 OPENAI_API_KEY 입력
streamlit run streamlit_app.py
```

## Streamlit Cloud 배포
1. GitHub에 push
2. share.streamlit.io → New app → 레포 선택
3. Settings → Secrets → OPENAI_API_KEY = "sk-..." 입력
4. Deploy
