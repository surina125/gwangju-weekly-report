from __future__ import annotations

from datetime import date

import pandas as pd
from sqlalchemy import text

from db import get_engine, read_sql


def get_report_periods() -> pd.DataFrame:
    query = """
        SELECT DISTINCT week_start, week_end
        FROM weekly_reports
        ORDER BY week_start DESC, week_end DESC
    """
    return read_sql(query)


def get_report_summary_metrics(
    week_start: date,
    week_end: date,
    department_id: int | None = None,
    cell_id: int | None = None,
) -> dict[str, int | float]:
    query = """
        SELECT
            COUNT(DISTINCT e.employee_id) AS total_employees,
            COUNT(DISTINCT CASE WHEN wr.status = '작성완료' THEN e.employee_id END) AS submitted_employees,
            COUNT(DISTINCT CASE WHEN wr.report_id IS NULL OR wr.status = '미작성' THEN e.employee_id END) AS not_submitted_employees,
            COALESCE(AVG(wri.progress), 0) AS avg_progress
        FROM employees e
        LEFT JOIN weekly_reports wr
          ON wr.employee_id = e.employee_id
         AND wr.week_start = :week_start
         AND wr.week_end = :week_end
        LEFT JOIN weekly_report_items wri ON wri.report_id = wr.report_id
        WHERE e.is_active = TRUE
    """
    params: dict[str, object] = {"week_start": week_start, "week_end": week_end}

    if department_id is not None:
        query += "\n  AND e.department_id = :department_id"
        params["department_id"] = department_id

    if cell_id is not None:
        query += "\n  AND e.cell_id = :cell_id"
        params["cell_id"] = cell_id

    frame = read_sql(query, params)
    row = frame.iloc[0]
    total = int(row["total_employees"] or 0)
    submitted = int(row["submitted_employees"] or 0)
    not_submitted = int(row["not_submitted_employees"] or 0)
    avg_progress = float(row["avg_progress"] or 0)
    completion_rate = round((submitted / total) * 100, 1) if total else 0.0
    return {
        "total_employees": total,
        "submitted_employees": submitted,
        "not_submitted_employees": not_submitted,
        "avg_progress": round(avg_progress, 1),
        "completion_rate": completion_rate,
    }


def get_submission_chart_data(
    week_start: date,
    week_end: date,
    department_id: int | None = None,
) -> pd.DataFrame:
    query = """
        SELECT
            c.cell_name AS cell_name,
            COUNT(DISTINCT e.employee_id) AS total_employees,
            COUNT(DISTINCT CASE WHEN wr.status = '작성완료' THEN e.employee_id END) AS submitted_employees
        FROM cells c
        JOIN employees e ON e.cell_id = c.cell_id
        LEFT JOIN weekly_reports wr
          ON wr.employee_id = e.employee_id
         AND wr.week_start = :week_start
         AND wr.week_end = :week_end
        WHERE e.is_active = TRUE
    """
    params: dict[str, object] = {"week_start": week_start, "week_end": week_end}
    if department_id is not None:
        query += "\n  AND e.department_id = :department_id"
        params["department_id"] = department_id

    query += """
        GROUP BY c.cell_name, c.cell_id
        ORDER BY c.cell_id
    """
    frame = read_sql(query, params)
    if not frame.empty:
        frame["미제출"] = frame["total_employees"] - frame["submitted_employees"]
        frame = frame.rename(
            columns={
                "cell_name": "셀",
                "submitted_employees": "제출",
                "total_employees": "대상",
            }
        )
    return frame


def get_progress_chart_data(
    week_start: date,
    week_end: date,
    department_id: int | None = None,
    cell_id: int | None = None,
) -> pd.DataFrame:
    query = """
        SELECT
            c.cell_name AS cell_name,
            COALESCE(AVG(wri.progress), 0) AS avg_progress
        FROM weekly_reports wr
        JOIN employees e ON e.employee_id = wr.employee_id
        JOIN cells c ON c.cell_id = e.cell_id
        LEFT JOIN weekly_report_items wri ON wri.report_id = wr.report_id
        WHERE wr.week_start = :week_start
          AND wr.week_end = :week_end
    """
    params: dict[str, object] = {"week_start": week_start, "week_end": week_end}

    if department_id is not None:
        query += "\n  AND e.department_id = :department_id"
        params["department_id"] = department_id

    if cell_id is not None:
        query += "\n  AND e.cell_id = :cell_id"
        params["cell_id"] = cell_id

    query += """
        GROUP BY c.cell_name, c.cell_id
        ORDER BY c.cell_id
    """
    frame = read_sql(query, params)
    if not frame.empty:
        frame = frame.rename(columns={"cell_name": "셀", "avg_progress": "평균 진행률"})
    return frame


def get_weekly_trend_chart_data() -> pd.DataFrame:
    query = """
        SELECT
            wr.week_start AS week_start,
            COUNT(DISTINCT CASE WHEN wr.status = '작성완료' THEN wr.employee_id END) AS submitted_employees,
            COALESCE(AVG(wri.progress), 0) AS avg_progress
        FROM weekly_reports wr
        LEFT JOIN weekly_report_items wri ON wri.report_id = wr.report_id
        GROUP BY wr.week_start
        ORDER BY wr.week_start
    """
    frame = read_sql(query)
    if not frame.empty:
        frame["week_label"] = pd.to_datetime(frame["week_start"]).dt.strftime("%Y-%m-%d")
        frame = frame.rename(
            columns={
                "submitted_employees": "제출 인원",
                "avg_progress": "평균 진행률",
            }
        )
    return frame


def get_employee_report_items(employee_id: int, week_start: date, week_end: date) -> pd.DataFrame:
    query = """
        SELECT
            wr.week_start AS "보고기간 시작일",
            wr.week_end AS "보고기간 종료일",
            wri.sr_title AS "SR 제목",
            wri.progress AS "진행률",
            wri.sr_dev_content AS "SR 개발내용",
            wr.submitted_at AS "작성일시"
        FROM weekly_reports wr
        LEFT JOIN weekly_report_items wri ON wri.report_id = wr.report_id
        WHERE wr.employee_id = :employee_id
          AND wr.week_start = :week_start
          AND wr.week_end = :week_end
        ORDER BY wri.sort_order, wri.item_id
    """
    return read_sql(
        query,
        {
            "employee_id": employee_id,
            "week_start": week_start,
            "week_end": week_end,
        },
    )


def save_weekly_report(
    employee_id: int,
    week_start: date,
    week_end: date,
    items: list[dict[str, object]],
) -> int:
    cleaned_items: list[dict[str, object]] = []
    for index, item in enumerate(items, start=1):
        sr_title = str(item.get("sr_title", "")).strip()
        sr_dev_content = str(item.get("sr_dev_content", "")).strip()
        progress = int(item.get("progress", 0))

        if not sr_title or not sr_dev_content:
            continue

        if not 0 <= progress <= 100:
            raise ValueError("진행률은 0부터 100 사이여야 합니다.")

        cleaned_items.append(
            {
                "sr_title": sr_title,
                "progress": progress,
                "sr_dev_content": sr_dev_content,
                "sort_order": index,
            }
        )

    if not cleaned_items:
        raise ValueError("최소 1개의 업무 항목을 입력해야 합니다.")

    with get_engine().begin() as connection:
        existing_report_id = connection.execute(
            text(
                """
                SELECT report_id
                FROM weekly_reports
                WHERE employee_id = :employee_id
                  AND week_start = :week_start
                  AND week_end = :week_end
                """
            ),
            {
                "employee_id": employee_id,
                "week_start": week_start,
                "week_end": week_end,
            },
        ).scalar_one_or_none()

        if existing_report_id is None:
            report_id = connection.execute(
                text("SELECT COALESCE(MAX(report_id), 0) + 1 FROM weekly_reports")
            ).scalar_one()
            connection.execute(
                text(
                    """
                    INSERT INTO weekly_reports (
                        report_id,
                        employee_id,
                        week_start,
                        week_end,
                        status,
                        submitted_at,
                        updated_at
                    )
                    VALUES (
                        :report_id,
                        :employee_id,
                        :week_start,
                        :week_end,
                        '작성완료',
                        CURRENT_TIMESTAMP,
                        CURRENT_TIMESTAMP
                    )
                    """
                ),
                {
                    "report_id": report_id,
                    "employee_id": employee_id,
                    "week_start": week_start,
                    "week_end": week_end,
                },
            )
        else:
            report_id = existing_report_id
            connection.execute(
                text(
                    """
                    UPDATE weekly_reports
                    SET status = '작성완료',
                        submitted_at = CURRENT_TIMESTAMP,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE report_id = :report_id
                    """
                ),
                {"report_id": report_id},
            )
            connection.execute(
                text("DELETE FROM weekly_report_items WHERE report_id = :report_id"),
                {"report_id": report_id},
            )

        next_item_id = connection.execute(
            text("SELECT COALESCE(MAX(item_id), 0) + 1 FROM weekly_report_items")
        ).scalar_one()

        for offset, item in enumerate(cleaned_items):
            connection.execute(
                text(
                    """
                    INSERT INTO weekly_report_items (
                        item_id,
                        report_id,
                        sr_title,
                        progress,
                        sr_dev_content,
                        sort_order
                    )
                    VALUES (
                        :item_id,
                        :report_id,
                        :sr_title,
                        :progress,
                        :sr_dev_content,
                        :sort_order
                    )
                    """
                ),
                {
                    "item_id": next_item_id + offset,
                    "report_id": report_id,
                    "sr_title": item["sr_title"],
                    "progress": item["progress"],
                    "sr_dev_content": item["sr_dev_content"],
                    "sort_order": item["sort_order"],
                },
            )

    return int(report_id)


def create_not_submitted_notifications(
    week_start: date,
    week_end: date,
    department_id: int | None = None,
    cell_id: int | None = None,
) -> int:
    targets = get_not_submitted_employees(
        week_start=week_start,
        week_end=week_end,
        department_id=department_id,
        cell_id=cell_id,
    )

    if targets.empty:
        return 0

    employee_query = """
        SELECT employee_id, emp_no
        FROM employees
    """
    employee_conditions: list[str] = []
    employee_params: dict[str, object] = {}

    if department_id is not None:
        employee_conditions.append("department_id = :department_id")
        employee_params["department_id"] = department_id

    if cell_id is not None:
        employee_conditions.append("cell_id = :cell_id")
        employee_params["cell_id"] = cell_id

    if employee_conditions:
        employee_query += "\nWHERE " + " AND ".join(employee_conditions)

    employee_ids = read_sql(employee_query, employee_params)
    emp_map = dict(zip(employee_ids["emp_no"], employee_ids["employee_id"]))

    delete_query = """
        DELETE FROM weekly_notifications
        WHERE week_start = :week_start
          AND week_end = :week_end
          AND notification_type = 'NOT_SUBMITTED'
    """
    delete_conditions: list[str] = []
    delete_params: dict[str, object] = {"week_start": week_start, "week_end": week_end}

    if department_id is not None:
        delete_conditions.append(
            "employee_id IN (SELECT employee_id FROM employees WHERE department_id = :department_id)"
        )
        delete_params["department_id"] = department_id

    if cell_id is not None:
        delete_conditions.append("employee_id IN (SELECT employee_id FROM employees WHERE cell_id = :cell_id)")
        delete_params["cell_id"] = cell_id

    if delete_conditions:
        delete_query += "\n  AND " + "\n  AND ".join(delete_conditions)

    with get_engine().begin() as connection:
        connection.execute(text(delete_query), delete_params)

        next_notification_id = connection.execute(
            text("SELECT COALESCE(MAX(notification_id), 0) + 1 FROM weekly_notifications")
        ).scalar_one()

        created = 0
        for offset, row in enumerate(targets.itertuples(index=False)):
            employee_id = emp_map[row.직번]
            message = f"{row.이름}님, 이번 주 주간업무보고가 아직 미작성 상태입니다."
            connection.execute(
                text(
                    """
                    INSERT INTO weekly_notifications (
                        notification_id,
                        employee_id,
                        week_start,
                        week_end,
                        check_time,
                        notification_type,
                        target_status,
                        message,
                        sent_yn,
                        checked_at
                    )
                    VALUES (
                        :notification_id,
                        :employee_id,
                        :week_start,
                        :week_end,
                        '매주 화요일 09:00',
                        'NOT_SUBMITTED',
                        '미작성',
                        :message,
                        'N',
                        CURRENT_TIMESTAMP
                    )
                    """
                ),
                {
                    "notification_id": next_notification_id + offset,
                    "employee_id": employee_id,
                    "week_start": week_start,
                    "week_end": week_end,
                    "message": message,
                },
            )
            created += 1

    return created


def get_reports_by_cell(
    week_start: date,
    week_end: date,
    department_id: int | None = None,
    cell_id: int | None = None,
) -> pd.DataFrame:
    query = """
        SELECT
            wr.week_start AS "보고기간 시작일",
            wr.week_end AS "보고기간 종료일",
            d.department_name AS "부서",
            c.cell_name AS "셀",
            e.emp_no AS "직번",
            e.employee_name AS "이름",
            wri.sr_title AS "SR 제목",
            wri.progress AS "진행률",
            wri.sr_dev_content AS "SR 개발내용",
            wr.submitted_at AS "작성일시"
        FROM weekly_reports wr
        JOIN employees e ON e.employee_id = wr.employee_id
        JOIN departments d ON d.department_id = e.department_id
        JOIN cells c ON c.cell_id = e.cell_id
        LEFT JOIN weekly_report_items wri ON wri.report_id = wr.report_id
        WHERE wr.week_start = :week_start
          AND wr.week_end = :week_end
    """
    params: dict[str, object] = {"week_start": week_start, "week_end": week_end}

    if department_id is not None:
        query += "\n  AND e.department_id = :department_id"
        params["department_id"] = department_id

    if cell_id is not None:
        query += "\n  AND e.cell_id = :cell_id"
        params["cell_id"] = cell_id

    query += "\nORDER BY d.department_id, c.cell_id, e.employee_id, wri.item_id"
    return read_sql(query, params)


def get_not_submitted_employees(
    week_start: date,
    week_end: date,
    department_id: int | None = None,
    cell_id: int | None = None,
) -> pd.DataFrame:
    query = """
        SELECT
            wr.week_start AS "보고기간 시작일",
            wr.week_end AS "보고기간 종료일",
            d.department_name AS "부서",
            c.cell_name AS "셀",
            e.emp_no AS "직번",
            e.employee_name AS "이름",
            COALESCE(wr.status, '미작성') AS "작성상태"
        FROM employees e
        JOIN departments d ON d.department_id = e.department_id
        JOIN cells c ON c.cell_id = e.cell_id
        LEFT JOIN weekly_reports wr
          ON wr.employee_id = e.employee_id
         AND wr.week_start = :week_start
         AND wr.week_end = :week_end
        WHERE e.is_active = TRUE
          AND (wr.report_id IS NULL OR wr.status = '미작성')
    """
    params: dict[str, object] = {"week_start": week_start, "week_end": week_end}

    if department_id is not None:
        query += "\n  AND e.department_id = :department_id"
        params["department_id"] = department_id

    if cell_id is not None:
        query += "\n  AND e.cell_id = :cell_id"
        params["cell_id"] = cell_id

    query += "\nORDER BY d.department_id, c.cell_id, e.employee_id"
    result = read_sql(query, params)

    if result.empty:
        return result

    result["보고기간 시작일"] = result["보고기간 시작일"].fillna(pd.Timestamp(week_start))
    result["보고기간 종료일"] = result["보고기간 종료일"].fillna(pd.Timestamp(week_end))
    return result
