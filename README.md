# 광주은행 주간업무보고

광주은행 주간업무보고를 위한 Streamlit 기반 MVP입니다.  
로컬 PostgreSQL로 개발할 수 있고, 무료 배포는 `Streamlit Community Cloud + Supabase Free` 조합을 기준으로 바로 올릴 수 있게 준비되어 있습니다.

## 로컬 실행

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

`.env`에는 아래 둘 중 하나만 맞추면 됩니다.

1. 개별 DB 환경변수 사용
2. 단일 `DATABASE_URL` 사용

예시:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=1234
```

또는

```env
DATABASE_URL=postgresql://user:password@host:5432/dbname?sslmode=require
```

## 더미 데이터 적재

스키마 생성과 더미 데이터 적재는 아래 명령으로 진행합니다.

```bash
python scripts/import_dummy_data.py
```

이 명령은 `sql/schema.sql`을 적용한 뒤, `weekly_report_dummy_db_data_cell_notification.xlsx` 내용을 DB에 넣습니다.

## 무료 배포 권장 조합

- 앱: `Streamlit Community Cloud`
- DB: `Supabase Free`

이 조합이면 별도 서버 비용 없이 MVP 시연이 가능합니다.

## Supabase 무료 DB 준비

1. [Supabase](https://supabase.com/)에서 새 프로젝트를 생성합니다.
2. 프로젝트 생성 후 `Project Settings > Database`에서 연결 정보를 확인합니다.
3. SQL Editor에서 [sql/schema.sql](/C:/Users/Aurumcampus/Desktop/report_pjt/sql/schema.sql)을 실행합니다.
4. 로컬에서 Supabase 연결 정보로 환경변수를 맞춘 뒤 아래 명령으로 더미 데이터를 적재합니다.

```bash
python scripts/import_dummy_data.py
```

## Streamlit Community Cloud 배포

1. GitHub 저장소를 Streamlit Community Cloud에 연결합니다.
2. `Main file path`를 `app.py`로 지정합니다.
3. 앱의 `Settings > Secrets`에 아래 예시 중 하나를 넣습니다.

### 방법 1. 단일 연결 문자열 사용

```toml
DATABASE_URL = "postgresql://postgres.xxxxx:password@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres?sslmode=require"
```

### 방법 2. 개별 키 사용

```toml
DB_HOST = "your-db-host"
DB_PORT = "5432"
DB_NAME = "postgres"
DB_USER = "your-db-user"
DB_PASSWORD = "your-db-password"
DB_SSLMODE = "require"
```

## 배포 시 주의사항

- `localhost` DB는 배포된 앱에서 접속되지 않습니다.
- 운영 또는 시연 배포 시에는 외부에서 접근 가능한 PostgreSQL이 필요합니다.
- `.env`는 GitHub에 올리지 않고, 배포 환경에서는 `Secrets`를 사용해야 합니다.
