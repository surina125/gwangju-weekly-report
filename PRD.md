# PRD.md
# 주간업무보고 웹사이트 PRD

## 1. 프로젝트 개요

### 1.1 목적
직원들이 매주 주간업무보고를 작성하고, 관리자가 부서 및 셀 단위로 보고서를 취합하여 엑셀로 다운로드할 수 있는 간단한 웹사이트를 만든다.

### 1.2 개발 목표
3시간 안에 동작 가능한 MVP를 만드는 것을 목표로 한다.

### 1.3 핵심 방향
- 인증/인가 기능은 제외한다.
- 주 코드는 Python으로 작성한다.
- 화면은 Streamlit으로 구현한다.
- DB는 PostgreSQL을 사용한다.
- 보고서 다운로드는 Word가 아닌 Excel만 지원한다.
- 주간업무 기간은 직접 입력하지 않고 자동 계산한다.
- 취합 기준은 부서가 아니라 셀 단위로 한다.
- 매주 화요일 오전 9시에 이번 주 보고서 미작성자를 확인할 수 있도록 한다.

---

## 2. 기술 스택

| 구분 | 기술 |
|---|---|
| Front / Web | Streamlit |
| Backend | Python |
| DB | PostgreSQL |
| DB 연결 | psycopg2 또는 SQLAlchemy |
| Excel 처리 | pandas, openpyxl |
| 환경변수 | python-dotenv |
| 스케줄링 | schedule 또는 cron |
| 실행 방식 | 로컬 실행 우선 |

---

## 3. 사용자 역할

### 3.1 직원
- 본인의 주간업무보고를 작성한다.
- SR 제목, 진행률, SR 개발내용을 여러 건 입력할 수 있다.

### 3.2 관리자
- 부서/셀/기간 기준으로 주간업무보고를 조회한다.
- 셀 단위로 보고서를 취합한다.
- 엑셀 파일로 다운로드한다.
- 미작성자 목록을 확인한다.

---

## 4. 주간업무 기간 정책

### 4.1 기간 고정 규칙
주간업무보고의 기간은 항상 수요일부터 다음 주 화요일까지다.

예시:

| 기준일 | 보고 기간 |
|---|---|
| 2026-05-13 수요일 | 2026-05-13 ~ 2026-05-19 |
| 2026-05-15 금요일 | 2026-05-13 ~ 2026-05-19 |
| 2026-05-19 화요일 | 2026-05-13 ~ 2026-05-19 |
| 2026-05-20 수요일 | 2026-05-20 ~ 2026-05-26 |

### 4.2 기간 계산 방식
사용자가 날짜를 입력하지 않는다.

시스템은 오늘 날짜를 기준으로 해당 주의 수요일을 `week_start`, 다음 주 화요일을 `week_end`로 자동 계산한다.

---

## 5. 주요 기능

## 5.1 직원 관리

### 기능 설명
직원의 기본 정보를 관리한다.

### 입력 정보
- 직번
- 이름
- 부서
- 셀

### 직번 규칙
- 영문 + 숫자 조합
- 총 7자리
- 예시: `A1023B7`, `IT001A2`

### 부서 예시
- IT개발부
- IT기획부
- 디지털개발부

### 셀 예시
IT개발부 하위 셀:
- 여신
- 수신
- 퇴직연금
- 카드

그 외 부서도 셀을 가질 수 있다.

---

## 5.2 주간업무보고 작성

### 기능 설명
직원이 이번 주 주간업무보고를 작성한다.

### 기본 정보
- 직번
- 이름
- 기간: 자동 표시
- 부서
- 셀

### 업무 내용
업무 내용은 리스트 형태로 여러 건 입력할 수 있다.

각 항목은 다음 값을 가진다.

| 항목 | 설명 |
|---|---|
| SR 제목 | 업무 또는 SR 제목 |
| 진행률 | 0~100 숫자 |
| SR 개발내용 | 상세 개발 내용 |

### 화면 예시
```text
[이번 주 보고 기간]
2026-05-13 ~ 2026-05-19

[직원 선택]
직번 / 이름

[업무 항목]
SR 제목
진행률
SR 개발내용

[+ 업무 추가]
[저장]
```

---

## 5.3 셀 단위 보고서 조회

### 기능 설명
관리자는 특정 기간의 특정 셀 보고서를 한 화면에서 조회한다.

### 조회 조건
- 기간
- 부서
- 셀

### 조회 결과
- 직번
- 이름
- 부서
- 셀
- SR 제목
- 진행률
- SR 개발내용
- 작성일시

---

## 5.4 Excel 다운로드

### 기능 설명
조회된 보고서를 Excel 파일로 다운로드한다.

### 다운로드 기준
- 부서 단위보다 셀 단위 다운로드를 우선한다.
- 예: `IT개발부_여신_주간업무보고_20260513_20260519.xlsx`

### Excel 컬럼
| 컬럼명 |
|---|
| 보고기간 시작일 |
| 보고기간 종료일 |
| 부서 |
| 셀 |
| 직번 |
| 이름 |
| SR 제목 |
| 진행률 |
| SR 개발내용 |
| 작성일시 |

### Excel 다운로드 정책
- Word 다운로드는 MVP에서 제외한다.
- Excel만 지원한다.
- Streamlit의 `st.download_button`을 사용한다.
- pandas DataFrame을 openpyxl 기반 xlsx로 변환한다.

---

## 5.5 미작성자 확인

### 기능 설명
이번 주 주간업무보고를 작성하지 않은 직원을 확인한다.

### 기준
- 현재 주간업무 기간 기준
- 직원 목록에는 있으나 `weekly_reports`에 해당 기간 보고서가 없는 직원

### 조회 조건
- 부서
- 셀
- 기간

### 조회 결과
- 직번
- 이름
- 부서
- 셀
- 보고기간
- 작성상태: 미작성

---

## 5.6 화요일 오전 9시 알림 기준

### 기능 설명
매주 화요일 오전 9시에 이번 주 보고서 미작성자를 확인하고 알림 대상 목록을 만든다.

### MVP 범위
3시간 MVP에서는 실제 카카오톡/메일 발송은 제외한다.

대신 다음 중 하나로 구현한다.
- Streamlit 화면에 미작성자 목록 표시
- 미작성자 목록 Excel 다운로드
- 콘솔 로그 출력
- 알림 대상 테이블에 저장

### 향후 확장
- 이메일 발송
- 사내 메신저 발송
- 카카오워크/Slack Webhook 연동
- Windows 작업 스케줄러 또는 Linux cron 연동

---

## 6. DB 설계

## 6.1 ERD 개요

```text
departments
  └── cells
        └── employees
              └── weekly_reports
                    └── weekly_report_items

weekly_notifications
```

---

## 6.2 departments

부서 정보를 저장한다.

| 컬럼명 | 타입 | 설명 |
|---|---|---|
| id | SERIAL PK | 부서 ID |
| department_name | VARCHAR(100) | 부서명 |
| created_at | TIMESTAMP | 생성일시 |

예시:
- IT개발부
- IT기획부
- 디지털개발부

---

## 6.3 cells

셀 정보를 저장한다.

| 컬럼명 | 타입 | 설명 |
|---|---|---|
| id | SERIAL PK | 셀 ID |
| department_id | INTEGER FK | 부서 ID |
| cell_name | VARCHAR(100) | 셀명 |
| created_at | TIMESTAMP | 생성일시 |

예시:
- 여신
- 수신
- 퇴직연금
- 카드

---

## 6.4 employees

직원 정보를 저장한다.

| 컬럼명 | 타입 | 설명 |
|---|---|---|
| id | SERIAL PK | 직원 ID |
| emp_no | VARCHAR(7) UNIQUE | 직번 |
| employee_name | VARCHAR(50) | 이름 |
| department_id | INTEGER FK | 부서 ID |
| cell_id | INTEGER FK | 셀 ID |
| is_active | BOOLEAN | 재직 여부 |
| created_at | TIMESTAMP | 생성일시 |

### 제약조건
- `emp_no`는 7자리
- 영문과 숫자를 포함한다.

---

## 6.5 weekly_reports

직원별 주간업무보고의 헤더 정보를 저장한다.

| 컬럼명 | 타입 | 설명 |
|---|---|---|
| id | SERIAL PK | 보고서 ID |
| employee_id | INTEGER FK | 직원 ID |
| week_start | DATE | 보고 시작일, 수요일 |
| week_end | DATE | 보고 종료일, 다음 주 화요일 |
| submitted_at | TIMESTAMP | 제출일시 |
| created_at | TIMESTAMP | 생성일시 |
| updated_at | TIMESTAMP | 수정일시 |

### 제약조건
직원은 동일 기간에 하나의 보고서만 작성한다.

```sql
UNIQUE(employee_id, week_start, week_end)
```

---

## 6.6 weekly_report_items

보고서 안의 업무 항목을 저장한다.

| 컬럼명 | 타입 | 설명 |
|---|---|---|
| id | SERIAL PK | 항목 ID |
| report_id | INTEGER FK | 보고서 ID |
| sr_title | VARCHAR(200) | SR 제목 |
| progress | INTEGER | 진행률 |
| dev_content | TEXT | SR 개발내용 |
| sort_order | INTEGER | 표시 순서 |
| created_at | TIMESTAMP | 생성일시 |

### 제약조건
- `progress`는 0 이상 100 이하

---

## 6.7 weekly_notifications

화요일 9시 미작성 알림 대상을 저장한다.

| 컬럼명 | 타입 | 설명 |
|---|---|---|
| id | SERIAL PK | 알림 ID |
| employee_id | INTEGER FK | 직원 ID |
| week_start | DATE | 보고 시작일 |
| week_end | DATE | 보고 종료일 |
| notification_type | VARCHAR(50) | 알림 종류 |
| status | VARCHAR(20) | 상태 |
| checked_at | TIMESTAMP | 확인일시 |

### notification_type 예시
- `NOT_SUBMITTED`

### status 예시
- `PENDING`
- `DONE`

---

## 7. MVP 화면 설계

## 7.1 사이드바 메뉴
```text
- 주간업무 작성
- 셀별 보고서 조회
- 미작성자 확인
- 기준정보 관리
```

---

## 7.2 주간업무 작성 화면

### 구성
- 이번 주 기간 자동 표시
- 직원 선택
- SR 업무 항목 입력
- 업무 항목 추가 버튼
- 저장 버튼

### 저장 로직
1. 직원 선택
2. 현재 날짜 기준 주간 기간 계산
3. `weekly_reports`에 헤더 저장
4. `weekly_report_items`에 업무 항목 저장

---

## 7.3 셀별 보고서 조회 화면

### 구성
- 기간 선택
- 부서 선택
- 셀 선택
- 조회 버튼
- 결과 테이블
- Excel 다운로드 버튼

---

## 7.4 미작성자 확인 화면

### 구성
- 기간 자동 표시
- 부서 선택
- 셀 선택
- 미작성자 조회 버튼
- 결과 테이블
- Excel 다운로드 버튼

---

## 7.5 기준정보 관리 화면

### MVP 기준
간단하게 직원 목록만 조회한다.

추가/수정은 DB 또는 엑셀 업로드로 처리해도 된다.

---

## 8. 파일 구조

```text
weekly-report-app/
├── app.py
├── db.py
├── services/
│   ├── date_service.py
│   ├── report_service.py
│   ├── employee_service.py
│   └── excel_service.py
├── jobs/
│   └── check_not_submitted.py
├── sql/
│   ├── schema.sql
│   └── seed.sql
├── data/
│   └── dummy_data.xlsx
├── requirements.txt
├── .env
├── PRD.md
├── AGENT.md
└── DESIGN.md
```

---

## 9. 개발 우선순위

## 1순위
- DB 테이블 생성
- 더미 직원 데이터 입력
- 현재 주간 기간 자동 계산
- 주간업무 작성
- 셀별 보고서 조회
- Excel 다운로드

## 2순위
- 미작성자 조회
- 미작성자 Excel 다운로드
- weekly_notifications 저장

## 3순위
- 실제 알림 발송
- 로그인/권한
- 관리자 화면 고도화
- 배포

---

## 10. 제외 범위

3시간 MVP에서는 다음 기능을 제외한다.

- 로그인
- 권한 관리
- Supabase Auth
- Word 다운로드
- 실제 메신저 알림
- 결재 기능
- 첨부파일
- 댓글
- 승인/반려
- 복잡한 관리자 권한

---

## 11. 성공 기준

다음이 가능하면 MVP 성공으로 본다.

1. 직원별 주간업무보고를 입력할 수 있다.
2. 기간이 자동으로 수요일~화요일로 계산된다.
3. 부서와 셀 기준으로 보고서를 조회할 수 있다.
4. 셀 단위 보고서를 Excel로 다운로드할 수 있다.
5. 이번 주 미작성자를 조회할 수 있다.
