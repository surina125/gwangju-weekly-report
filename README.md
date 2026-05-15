# 광주은행 주간업무보고

Streamlit 기반 주간업무보고 서비스입니다.

## 로컬 실행

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Community Cloud 배포

1. 이 폴더를 GitHub 저장소에 업로드합니다.
2. Streamlit Community Cloud에서 저장소를 선택합니다.
3. Main file path는 `app.py`로 지정합니다.
4. 앱 Settings의 Secrets에 아래 값을 등록합니다.

```toml
DB_HOST = "your-db-host"
DB_PORT = "5432"
DB_NAME = "your-db-name"
DB_USER = "your-db-user"
DB_PASSWORD = "your-db-password"
DB_SSLMODE = "require"
```
