# AGENT.md
# 바이브코딩용 개발 지시서

## 1. 개발 목표
Python Streamlit 기반 주간업무보고 MVP를 구현한다.

이 프로젝트는 3시간 안에 동작하는 결과물을 만드는 것이 목표다.  
복잡한 구조보다 단순하고 실행 가능한 코드를 우선한다.

---

## 2. 반드시 지킬 원칙

## 2.1 인증/인가 제외
로그인, 회원가입, 권한 관리는 구현하지 않는다.

직원은 화면에서 선택하는 방식으로 처리한다.

## 2.2 Python 중심
주 코드는 Python으로 작성한다.

사용 기술:
- Streamlit
- PostgreSQL
- pandas
- openpyxl
- psycopg2 또는 SQLAlchemy
- python-dotenv

## 2.3 Excel 다운로드만 구현
Word 다운로드는 구현하지 않는다.

보고서 다운로드는 반드시 `.xlsx` 파일로 한다.

## 2.4 기간 자동 계산
사용자가 보고 기간을 직접 입력하지 않도록 한다.

오늘 날짜를 기준으로:
- 시작일: 해당 주 수요일
- 종료일: 다음 주 화요일

예:
- 금요일에 작성해도 그 주 수요일~다음 주 화요일로 저장한다.

## 2.5 취합 단위는 셀
보고서 조회와 다운로드는 부서보다 셀 단위를 우선한다.

예:
- IT개발부 > 여신
- IT개발부 > 수신
- IT개발부 > 퇴직연금
- IT개발부 > 카드

---

## 3. 구현해야 할 화면

## 3.1 주간업무 작성
필수 기능:
- 현재 주간 기간 표시
- 직원 선택
- SR 제목 입력
- 진행률 입력
- SR 개발내용 입력
- 업무 항목 여러 개 추가
- 저장

주의:
- 한 직원은 같은 기간에 보고서를 1개만 작성한다.
- 이미 작성한 경우 기존 보고서를 업데이트하거나 삭제 후 재저장한다.

---

## 3.2 셀별 보고서 조회
필수 기능:
- 부서 선택
- 셀 선택
- 기간 선택 또는 현재 기간 자동 선택
- 보고서 조회
- Excel 다운로드

조회 결과 컬럼:
- 보고기간 시작일
- 보고기간 종료일
- 부서
- 셀
- 직번
- 이름
- SR 제목
- 진행률
- SR 개발내용
- 작성일시

---

## 3.3 미작성자 확인
필수 기능:
- 현재 기간 기준
- 부서 선택
- 셀 선택
- 보고서 미작성자 조회
- Excel 다운로드

미작성 기준:
- employees에는 존재
- weekly_reports에는 해당 week_start/week_end 데이터 없음

---

## 3.4 기준정보 조회
필수 기능:
- 직원 목록 조회
- 부서/셀 확인

MVP에서는 직원 추가/수정 화면은 생략해도 된다.

---

## 4. DB 테이블

다음 테이블을 만든다.

1. departments
2. cells
3. employees
4. weekly_reports
5. weekly_report_items
6. weekly_notifications

---

## 5. 주요 함수

## 5.1 date_service.py

```python
def get_week_range(base_date: date) -> tuple[date, date]:
    """기준일이 속한 보고 기간의 수요일과 다음 주 화요일을 반환한다."""
```

## 5.2 employee_service.py

```python
def get_departments():
    pass

def get_cells_by_department(department_id: int):
    pass

def get_employees(department_id: int | None = None, cell_id: int | None = None):
    pass
```

## 5.3 report_service.py

```python
def save_weekly_report(employee_id: int, week_start: date, week_end: date, items: list[dict]):
    pass

def get_reports_by_cell(week_start: date, week_end: date, department_id: int, cell_id: int):
    pass

def get_not_submitted_employees(week_start: date, week_end: date, department_id: int, cell_id: int):
    pass
```

## 5.4 excel_service.py

```python
def dataframe_to_excel_bytes(df):
    pass
```

---

## 6. SQL 작성 기준

## 6.1 보고서 조회 SQL
보고서 조회는 employees, departments, cells, weekly_reports, weekly_report_items를 조인한다.

## 6.2 미작성자 조회 SQL
LEFT JOIN을 사용한다.

```sql
SELECT e.*
FROM employees e
LEFT JOIN weekly_reports wr
  ON e.id = wr.employee_id
 AND wr.week_start = :week_start
 AND wr.week_end = :week_end
WHERE wr.id IS NULL
  AND e.department_id = :department_id
  AND e.cell_id = :cell_id
  AND e.is_active = true;
```

---

## 7. UI 구현 규칙

## 7.1 전체 레이아웃
Streamlit sidebar를 사용한다.

메뉴:
- 주간업무 작성
- 셀별 보고서 조회
- 미작성자 확인
- 기준정보 조회

## 7.2 입력 폼
`st.form`을 사용한다.

## 7.3 표 출력
`st.dataframe`을 사용한다.

## 7.4 다운로드
`st.download_button`을 사용한다.

---

## 8. 더미 데이터 기준

## 8.1 부서
- IT개발부
- IT기획부
- 디지털개발부

## 8.2 IT개발부 셀
- 여신
- 수신
- 퇴직연금
- 카드

## 8.3 직번
- 영문 + 숫자 조합 7자리
- 예: ITA1023

---

## 9. 알림 구현 기준

MVP에서는 실제 알림 발송을 구현하지 않는다.

대신 화요일 오전 9시 기준으로 실행할 수 있는 Python 스크립트를 만든다.

파일:
```text
jobs/check_not_submitted.py
```

역할:
1. 현재 주간 기간 계산
2. 미작성자 조회
3. weekly_notifications에 저장
4. 콘솔에 미작성자 출력

---

## 10. 실행 명령 예시

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 11. 금지 사항

- 로그인 구현하지 말 것
- Supabase Auth 구현하지 말 것
- Word 다운로드 구현하지 말 것
- React/Next.js로 만들지 말 것
- 복잡한 관리자 권한 만들지 말 것
- 처음부터 완벽한 디자인을 만들려고 하지 말 것

---

## 12. 완료 기준

다음이 되면 완료로 본다.

- Streamlit 앱 실행 가능
- 직원 선택 가능
- 주간업무 저장 가능
- 셀별 보고서 조회 가능
- Excel 다운로드 가능
- 미작성자 조회 가능
