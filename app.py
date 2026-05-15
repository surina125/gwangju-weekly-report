from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

from db import MissingEnvironmentError, get_missing_env_vars, healthcheck
from services.auth_service import (
    authenticate_user,
    cleanup_legacy_seeded_employee_users,
    ensure_admin_user,
    ensure_auth_schema,
    register_user,
    username_from_emp_no,
    validate_emp_no,
)
from services.date_service import format_week_label, get_week_range
from services.employee_service import get_cells_by_department, get_departments, get_employees
from services.excel_service import dataframe_to_excel_bytes
from services.report_service import (
    get_employee_report_items,
    get_not_submitted_employees,
    get_report_periods,
    get_reports_by_cell,
    get_report_summary_metrics,
    get_submission_chart_data,
    get_progress_chart_data,
    get_weekly_trend_chart_data,
    save_weekly_report,
)
from services.word_service import build_report_docx


st.set_page_config(page_title="광주은행 주간업무보고", layout="wide")
BASE_DIR = Path(__file__).resolve().parent
SIGNATURE_IMAGE = BASE_DIR / "image" / "logo_transparent.png"
SYMBOL_IMAGE = BASE_DIR / "image" / "symbolmark.png"


CUSTOM_CSS = """
<style>
    :root {
        --bg-main: #f3f6f9;
        --bg-panel: rgba(255,255,255,0.9);
        --bg-sidebar-top: #0d2336;
        --bg-sidebar-bottom: #173d59;
        --line-soft: rgba(18, 50, 75, 0.10);
        --ink-strong: #102a43;
        --ink-mid: #486581;
        --ink-soft: #6b7f92;
        --brand: #0f5f8c;
        --brand-strong: #0b3f62;
        --brand-accent: #2fa1ca;
        --success: #1f7a59;
    }
    .stApp {
        background:
            radial-gradient(circle at 0% 0%, rgba(47, 161, 202, 0.12), transparent 28%),
            radial-gradient(circle at 100% 0%, rgba(15, 95, 140, 0.10), transparent 25%),
            linear-gradient(180deg, #f7fafc 0%, var(--bg-main) 100%);
    }
    .block-container {
        max-width: 1220px;
        padding-top: 0.85rem;
        padding-bottom: 1.2rem;
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--bg-sidebar-top) 0%, var(--bg-sidebar-bottom) 100%);
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    section[data-testid="stSidebar"] * {
        color: #f7fbff;
    }
    .app-shell {
        display: grid;
        gap: 1rem;
    }
    .hero-panel {
        padding: 1.5rem 1.6rem;
        border-radius: 24px;
        background:
            linear-gradient(135deg, rgba(9, 35, 56, 0.96) 0%, rgba(18, 74, 109, 0.94) 58%, rgba(28, 115, 153, 0.92) 100%);
        color: white;
        box-shadow: 0 30px 60px rgba(16, 42, 67, 0.18);
        position: relative;
        overflow: hidden;
        margin-bottom: 1rem;
    }
    .hero-panel.minimal {
        padding: 1.2rem 1.35rem;
        min-height: auto;
    }
    .hero-panel::after {
        content: "";
        position: absolute;
        right: -70px;
        top: -70px;
        width: 220px;
        height: 220px;
        border-radius: 999px;
        background: radial-gradient(circle, rgba(255,255,255,0.22) 0%, rgba(255,255,255,0.02) 70%);
    }
    .hero-kicker {
        font-size: 0.74rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        opacity: 0.75;
        margin-bottom: 0.45rem;
        font-weight: 700;
    }
    .hero-title {
        font-size: 1.85rem;
        line-height: 1.18;
        font-weight: 800;
        margin-bottom: 0.35rem;
        position: relative;
        z-index: 1;
    }
    .hero-body {
        font-size: 0.98rem;
        max-width: 760px;
        opacity: 0.92;
        position: relative;
        z-index: 1;
    }
    .brand-lockup {
        display: flex;
        align-items: center;
        gap: 0.85rem;
        position: relative;
        z-index: 1;
    }
    .brand-mark {
        width: 52px;
        height: 52px;
        border-radius: 16px;
        background:
            linear-gradient(145deg, rgba(255,255,255,0.18) 0%, rgba(255,255,255,0.06) 100%),
            linear-gradient(135deg, #2fa1ca 0%, #8be2ff 100%);
        box-shadow:
            inset 0 1px 0 rgba(255,255,255,0.22),
            0 10px 24px rgba(7, 30, 46, 0.22);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        font-weight: 800;
        color: white;
        letter-spacing: 0.08em;
    }
    .brand-copy {
        display: flex;
        flex-direction: column;
        gap: 0.1rem;
    }
    .brand-name {
        font-size: 1.55rem;
        line-height: 1.05;
        font-weight: 800;
        color: white;
    }
    .brand-tag {
        font-size: 0.86rem;
        color: rgba(255,255,255,0.78);
        letter-spacing: 0.04em;
    }
    .glass-card {
        background: var(--bg-panel);
        border: 1px solid var(--line-soft);
        border-radius: 22px;
        padding: 1.05rem 1.1rem 0.4rem 1.1rem;
        box-shadow: 0 14px 36px rgba(16, 42, 67, 0.07);
        backdrop-filter: blur(10px);
        margin-bottom: 1rem;
    }
    .glass-card.compact {
        padding: 0.8rem 0.9rem 0.15rem 0.9rem;
    }
    .section-label {
        color: var(--ink-soft);
        text-transform: uppercase;
        letter-spacing: 0.10em;
        font-size: 0.73rem;
        font-weight: 700;
        margin-bottom: 0.45rem;
    }
    .auth-grid {
        display: grid;
        grid-template-columns: 1.15fr 1fr;
        gap: 1rem;
        align-items: start;
    }
    .auth-note {
        background: rgba(255,255,255,0.14);
        border: 1px solid rgba(255,255,255,0.16);
        border-radius: 18px;
        padding: 1rem 1.1rem;
        margin-top: 1rem;
        max-width: 360px;
        position: relative;
        z-index: 1;
    }
    .auth-note strong {
        display: block;
        margin-bottom: 0.35rem;
        font-size: 0.9rem;
    }
    .auth-meta {
        color: var(--ink-soft);
        font-size: 0.88rem;
        line-height: 1.35;
    }
    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.88);
        border: 1px solid var(--line-soft);
        border-radius: 18px;
        padding: 0.8rem 1rem;
        box-shadow: 0 12px 26px rgba(16, 42, 67, 0.06);
    }
    div[data-testid="stDataFrame"] {
        border-radius: 18px;
        overflow: hidden;
        border: 1px solid var(--line-soft);
        background: white;
    }
    .stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {
        border-radius: 999px;
        border: none;
        font-weight: 700;
        padding: 0.62rem 1.15rem;
        background: linear-gradient(135deg, var(--brand) 0%, var(--brand-accent) 100%);
        color: white;
        box-shadow: 0 14px 26px rgba(15, 95, 140, 0.22);
    }
    .stTextInput label, .stSelectbox label, .stTextArea label, .stNumberInput label {
        color: var(--ink-mid);
        font-weight: 600;
    }
    .service-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.32rem 0.68rem;
        background: rgba(16, 42, 67, 0.07);
        border: 1px solid rgba(16, 42, 67, 0.08);
        border-radius: 999px;
        color: var(--ink-mid);
        font-size: 0.82rem;
        font-weight: 700;
        margin-right: 0.35rem;
        margin-top: 0.35rem;
    }
</style>
"""


def safe_date(value: object) -> date:
    if isinstance(value, pd.Timestamp):
        return value.date()
    if isinstance(value, date):
        return value
    return pd.to_datetime(value).date()


def inject_theme() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_page_intro(title: str, description: str, kicker: str = "광주은행 주간업무보고") -> None:
    st.markdown(
        f"""
        <div class="hero-panel">
            <div class="hero-kicker">{kicker}</div>
            <div class="hero-title">{title}</div>
            <div class="hero-body">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_brand_hero(show_copy: bool = True) -> None:
    description = (
        '<div class="hero-body">주간업무보고 작성, 취합, 다운로드와 차트 분석을 한 곳에서 운영하는 업무 리포트 서비스</div>'
        if show_copy
        else ""
    )
    st.markdown(
        f"""
        <div class="hero-panel minimal">
            <div class="brand-lockup">
                <div class="brand-mark">WF</div>
                <div class="brand-copy">
                    <div class="brand-name">광주은행</div>
                    <div class="brand-tag">Weekly Reporting Service</div>
                </div>
            </div>
            {description}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_open(label: str, compact: bool = False) -> None:
    class_name = "glass-card compact" if compact else "glass-card"
    st.markdown(
        f'<div class="{class_name}"><div class="section-label">{label}</div>',
        unsafe_allow_html=True,
    )


def render_section_close() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


def current_user() -> dict[str, object] | None:
    return st.session_state.get("auth_user")


def is_admin(user: dict[str, object]) -> bool:
    return str(user.get("role", "")) == "admin"


def build_period_options() -> list[tuple[date, date]]:
    current_period = get_week_range(date.today())
    options = [current_period]

    try:
        periods = get_report_periods()
    except Exception:
        return options

    for row in periods.itertuples(index=False):
        candidate = (safe_date(row.week_start), safe_date(row.week_end))
        if candidate not in options:
            options.append(candidate)

    return options


def render_connection_status() -> None:
    missing_vars = get_missing_env_vars()
    if missing_vars:
        joined = ", ".join(missing_vars)
        st.error(f"DB 연결에 필요한 환경변수가 비어 있습니다: {joined}")
        st.stop()

    try:
        healthcheck()
        ensure_auth_schema()
        ensure_admin_user()
        cleanup_legacy_seeded_employee_users()
    except MissingEnvironmentError as exc:
        st.error(str(exc))
        st.stop()
    except Exception as exc:
        st.error(f"초기화 중 오류가 발생했습니다: {exc}")
        st.info("DB 연결, 스키마 적용, 사용자 시드 상태를 확인해 주세요.")
        st.stop()


def render_period_info(selected_period: tuple[date, date]) -> None:
    week_start, week_end = selected_period
    st.info(f"현재 보고 기간: {format_week_label(week_start, week_end)}")


def render_service_badges(values: list[str]) -> None:
    badges = "".join(f'<span class="service-badge">{value}</span>' for value in values)
    st.markdown(badges, unsafe_allow_html=True)


def render_login_page() -> None:
    if SIGNATURE_IMAGE.exists():
        logo_left, logo_center, logo_right = st.columns([1.2, 2.8, 1.2])
        with logo_center:
            st.image(str(SIGNATURE_IMAGE), width=280)
    else:
        render_brand_hero(show_copy=False)
    left, right = st.columns([1, 1], gap="medium")

    with left:
        render_section_open("로그인", compact=True)
        with st.form("login_form"):
            username = st.text_input("아이디", placeholder="예: a24b901")
            password = st.text_input("비밀번호", type="password")
            submitted = st.form_submit_button("로그인", type="primary")
        st.caption("관리자 데모 계정: `admin / admin123!`")
        render_section_close()

        if submitted:
            user = authenticate_user(username=username, password=password)
            if not user:
                st.error("아이디 또는 비밀번호가 올바르지 않습니다.")
            else:
                st.session_state["auth_user"] = user
                st.rerun()

        st.caption("직원은 본인 보고서 작성/조회, 관리자는 전체 취합과 다운로드 기능을 사용할 수 있습니다.")

    with right:
        departments = get_departments()
        department_lookup = {row.department_name: int(row.department_id) for row in departments.itertuples(index=False)}
        department_names = list(department_lookup.keys())

        render_section_open("회원가입", compact=True)
        with st.form("signup_form"):
            emp_no_input = st.text_input("직번", placeholder="예: A24B901")
            emp_valid, emp_result = validate_emp_no(emp_no_input) if emp_no_input.strip() else (True, "")
            employee_name = st.text_input("이름")
            selected_department_name = st.selectbox("부서", department_names)
            department_id = department_lookup[selected_department_name]

            cells = get_cells_by_department(department_id)
            cell_lookup = {row.cell_name: int(row.cell_id) for row in cells.itertuples(index=False)}
            cell_names = list(cell_lookup.keys())
            selected_cell_name = st.selectbox("셀", cell_names)
            cell_id = cell_lookup[selected_cell_name]

            email = st.text_input("이메일", placeholder="사내 이메일 또는 등록된 이메일")
            password = st.text_input("비밀번호", type="password")
            password_confirm = st.text_input("비밀번호 확인", type="password")
            submitted = st.form_submit_button("회원가입", type="primary")
        render_section_close()

        render_service_badges(
            [
                "직번 7자리 검증",
                "숫자-only 허용",
                "이메일 대조 확인",
                "직원 마스터 일치 검증",
            ]
        )
        st.caption("로그인 아이디는 회원가입 후 직번 소문자 형태로 사용됩니다. 예: `A24B901 -> a24b901`")

        if submitted:
            if not emp_valid:
                st.error(emp_result)
            elif password != password_confirm:
                st.error("비밀번호와 비밀번호 확인이 일치하지 않습니다.")
            else:
                success, message = register_user(
                    emp_no=emp_no_input,
                    employee_name=employee_name,
                    department_id=department_id,
                    cell_id=cell_id,
                    email=email,
                    password=password,
                )
                if success:
                    st.success(message)
                else:
                    st.error(message)


def render_chart_analysis_page() -> None:
    render_page_intro(
        "운영 현황을 차트로 빠르게 읽어보세요",
        "제출률, 셀별 평균 진행률, 기간 추이를 한 화면에서 확인해 팀 운영 상태를 빠르게 파악할 수 있습니다.",
        kicker="Analytics",
    )
    render_section_open("분석 기준")
    selected_period, department_id, cell_id, department_name, cell_name = render_filters()
    render_period_info(selected_period)
    render_section_close()

    summary = get_report_summary_metrics(
        week_start=selected_period[0],
        week_end=selected_period[1],
        department_id=department_id,
        cell_id=cell_id,
    )
    summary_cols = st.columns(4)
    summary_cols[0].metric("대상 인원", f"{summary['total_employees']}명")
    summary_cols[1].metric("제출 인원", f"{summary['submitted_employees']}명")
    summary_cols[2].metric("제출률", f"{summary['completion_rate']}%")
    summary_cols[3].metric("평균 진행률", f"{summary['avg_progress']}%")

    submission_chart = get_submission_chart_data(
        week_start=selected_period[0],
        week_end=selected_period[1],
        department_id=department_id,
    )
    progress_chart = get_progress_chart_data(
        week_start=selected_period[0],
        week_end=selected_period[1],
        department_id=department_id,
        cell_id=cell_id,
    )
    trend_chart = get_weekly_trend_chart_data()

    chart_cols = st.columns(2, gap="large")
    with chart_cols[0]:
        render_section_open("셀별 제출 현황", compact=True)
        if submission_chart.empty:
            st.info("표시할 제출 현황이 없습니다.")
        else:
            st.bar_chart(
                submission_chart.set_index("셀")[["제출", "미제출"]],
                use_container_width=True,
            )
            st.dataframe(submission_chart, use_container_width=True, hide_index=True)
        render_section_close()

    with chart_cols[1]:
        render_section_open("셀별 평균 진행률", compact=True)
        if progress_chart.empty:
            st.info("표시할 진행률 데이터가 없습니다.")
        else:
            st.bar_chart(
                progress_chart.set_index("셀")[["평균 진행률"]],
                use_container_width=True,
            )
            st.dataframe(progress_chart, use_container_width=True, hide_index=True)
        render_section_close()

    render_section_open("기간별 추이")
    if trend_chart.empty:
        st.info("표시할 주간 추이 데이터가 없습니다.")
    else:
        trend_view = trend_chart.set_index("week_label")[["제출 인원", "평균 진행률"]]
        st.line_chart(trend_view, use_container_width=True)
        st.dataframe(
            trend_chart[["week_label", "제출 인원", "평균 진행률"]],
            use_container_width=True,
            hide_index=True,
        )
    render_section_close()


def render_filters() -> tuple[tuple[date, date], int | None, int | None, str | None, str | None]:
    period_options = build_period_options()
    departments = get_departments()

    period_labels = [format_week_label(start, end) for start, end in period_options]
    selected_label = st.selectbox("보고 기간", period_labels, index=0)
    period_index = period_labels.index(selected_label)
    selected_period = period_options[period_index]

    department_lookup = {row.department_name: int(row.department_id) for row in departments.itertuples(index=False)}
    department_names = ["전체"] + list(department_lookup.keys())
    selected_department_name = st.selectbox("부서", department_names)
    department_id = None if selected_department_name == "전체" else department_lookup[selected_department_name]

    cells = get_cells_by_department(department_id)
    cell_lookup = {row.cell_name: int(row.cell_id) for row in cells.itertuples(index=False)}
    cell_names = ["전체"] + list(cell_lookup.keys())
    selected_cell_name = st.selectbox("셀", cell_names)
    cell_id = None if selected_cell_name == "전체" else cell_lookup[selected_cell_name]

    return (
        selected_period,
        department_id,
        cell_id,
        None if selected_department_name == "전체" else selected_department_name,
        None if selected_cell_name == "전체" else selected_cell_name,
    )


def build_download_filename(
    prefix: str,
    extension: str,
    department_name: str | None,
    cell_name: str | None,
    selected_period: tuple[date, date],
) -> str:
    week_start, week_end = selected_period
    scope_parts = [part for part in [department_name, cell_name] if part]
    scope = "_".join(scope_parts) if scope_parts else "전체"
    return f"{scope}_{prefix}_{week_start:%Y%m%d}_{week_end:%Y%m%d}.{extension}"


def render_report_query_page() -> None:
    render_page_intro(
        "조직 단위로 보고서를 취합하고 내려받으세요",
        "부서와 셀, 기간 기준으로 주간업무보고를 한 번에 모아 Excel과 Word로 다운로드할 수 있습니다.",
        kicker="Admin Console",
    )
    render_section_open("조회 조건")
    selected_period, department_id, cell_id, department_name, cell_name = render_filters()
    render_period_info(selected_period)
    render_section_close()

    if st.button("보고서 조회", type="primary"):
        result = get_reports_by_cell(
            week_start=selected_period[0],
            week_end=selected_period[1],
            department_id=department_id,
            cell_id=cell_id,
        )

        if result.empty:
            st.warning("조회된 주간업무보고가 없습니다.")
            return

        metric_cols = st.columns(4)
        metric_cols[0].metric("조회 행 수", f"{len(result)}건")
        metric_cols[1].metric("부서", department_name or "전체")
        metric_cols[2].metric("셀", cell_name or "전체")
        metric_cols[3].metric("다운로드 형식", "Excel + Word")
        st.dataframe(result, use_container_width=True)

        excel_bytes = dataframe_to_excel_bytes(result, sheet_name="weekly_reports")
        word_bytes = build_report_docx(
            dataframe=result,
            week_start=selected_period[0],
            week_end=selected_period[1],
            department_name=department_name,
            cell_name=cell_name,
        )

        dl_cols = st.columns(2)
        with dl_cols[0]:
            st.download_button(
                label="Excel 다운로드",
                data=excel_bytes,
                file_name=build_download_filename("주간업무보고", "xlsx", department_name, cell_name, selected_period),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        with dl_cols[1]:
            st.download_button(
                label="Word 다운로드",
                data=word_bytes,
                file_name=build_download_filename("주간업무보고", "docx", department_name, cell_name, selected_period),
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )


def render_my_report_page(user: dict[str, object]) -> None:
    render_page_intro(
        "내가 제출한 보고서를 기간별로 확인하세요",
        "로그인한 본인 계정 기준으로 제출 이력을 다시 확인하고 업무 항목을 검토할 수 있습니다.",
        kicker="My Workspace",
    )
    period_options = build_period_options()
    period_labels = [format_week_label(start, end) for start, end in period_options]
    selected_label = st.selectbox("보고 기간", period_labels, index=0)
    selected_period = period_options[period_labels.index(selected_label)]
    render_period_info(selected_period)

    employee_id = user.get("employee_id")
    if not employee_id:
        st.warning("직원 계정에 연결된 사번 정보가 없습니다.")
        return

    result = get_employee_report_items(
        employee_id=int(employee_id),
        week_start=selected_period[0],
        week_end=selected_period[1],
    )

    if result.empty:
        st.info("선택한 기간에 제출한 보고서가 없습니다.")
        return

    st.dataframe(result, use_container_width=True)


def render_report_write_page(user: dict[str, object]) -> None:
    render_page_intro(
        "이번 주 업무를 정리해 제출하세요",
        "여러 개의 SR 항목을 한 번에 작성하고 저장할 수 있습니다. 직원은 본인 계정 기준으로만 제출됩니다.",
        kicker="Write Report",
    )
    selected_period = get_week_range(date.today())
    render_period_info(selected_period)

    render_section_open("작성 대상")
    if is_admin(user):
        departments = get_departments()
        department_lookup = {row.department_name: int(row.department_id) for row in departments.itertuples(index=False)}
        department_names = list(department_lookup.keys())
        selected_department_name = st.selectbox("부서 선택", department_names)
        department_id = department_lookup[selected_department_name]

        cells = get_cells_by_department(department_id)
        cell_lookup = {row.cell_name: int(row.cell_id) for row in cells.itertuples(index=False)}
        cell_names = list(cell_lookup.keys())
        selected_cell_name = st.selectbox("셀 선택", cell_names)
        cell_id = cell_lookup[selected_cell_name]

        employees = get_employees(department_id=department_id, cell_id=cell_id)
        employee_lookup = {
            f"{row.직번} / {row.이름}": int(row.employee_id)
            for row in employees.itertuples(index=False)
        }
    else:
        employee_lookup = {
            f"{user['emp_no']} / {user['employee_name']}": int(user["employee_id"])
        }
        preview_cols = st.columns(3)
        preview_cols[0].text_input("직번", value=str(user.get("emp_no", "")), disabled=True)
        preview_cols[1].text_input("부서", value=str(user.get("department_name", "")), disabled=True)
        preview_cols[2].text_input("셀", value=str(user.get("cell_name", "")), disabled=True)

    if not employee_lookup:
        st.warning("선택한 부서/셀에 등록된 직원이 없습니다.")
        render_section_close()
        return

    selected_employee_label = st.selectbox("직원 선택", list(employee_lookup.keys()))
    item_count = st.selectbox("업무 항목 수", [1, 2, 3, 4, 5], index=0)
    render_section_close()

    render_section_open("업무 입력")
    with st.form("weekly_report_write_form"):
        report_items: list[dict[str, object]] = []
        for idx in range(item_count):
            st.markdown(f"**업무 항목 {idx + 1}**")
            left, right = st.columns([1.2, 0.5], gap="medium")
            with left:
                sr_title = st.text_input("SR 제목", key=f"sr_title_{idx}")
            with right:
                progress = st.number_input(
                    "진행률",
                    min_value=0,
                    max_value=100,
                    value=0,
                    step=5,
                    key=f"progress_{idx}",
                )
            sr_dev_content = st.text_area("SR 개발내용", key=f"sr_dev_content_{idx}")
            report_items.append(
                {
                    "sr_title": sr_title,
                    "progress": progress,
                    "sr_dev_content": sr_dev_content,
                }
            )

        submitted = st.form_submit_button("저장", type="primary")
    render_section_close()

    if not submitted:
        return

    try:
        report_id = save_weekly_report(
            employee_id=employee_lookup[selected_employee_label],
            week_start=selected_period[0],
            week_end=selected_period[1],
            items=report_items,
        )
    except ValueError as exc:
        st.error(str(exc))
        return
    except Exception as exc:
        st.error(f"저장 중 오류가 발생했습니다: {exc}")
        return

    st.success(f"주간업무보고가 저장되었습니다. report_id={report_id}")


def render_not_submitted_page() -> None:
    render_page_intro(
        "미작성자를 빠르게 점검하고 후속 조치하세요",
        "선택한 기간 기준으로 아직 보고서를 제출하지 않은 대상을 확인하고 후속 알림 자료로 활용할 수 있습니다.",
        kicker="Follow-up",
    )
    render_section_open("조회 조건")
    selected_period, department_id, cell_id, department_name, cell_name = render_filters()
    render_period_info(selected_period)
    render_section_close()

    if st.button("미작성자 조회", type="primary"):
        result = get_not_submitted_employees(
            week_start=selected_period[0],
            week_end=selected_period[1],
            department_id=department_id,
            cell_id=cell_id,
        )

        if result.empty:
            st.success("모든 직원이 보고서를 작성했습니다.")
            return

        st.warning("미작성자가 있습니다.")
        metric_cols = st.columns(3)
        metric_cols[0].metric("미작성자 수", f"{len(result)}명")
        metric_cols[1].metric("부서", department_name or "전체")
        metric_cols[2].metric("셀", cell_name or "전체")
        st.dataframe(result, use_container_width=True)
        excel_bytes = dataframe_to_excel_bytes(result, sheet_name="not_submitted")
        st.download_button(
            label="미작성자 Excel 다운로드",
            data=excel_bytes,
            file_name=build_download_filename("미작성자목록", "xlsx", department_name, cell_name, selected_period),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


def render_employee_page() -> None:
    render_page_intro(
        "기준 정보를 운영 화면처럼 관리하세요",
        "직원, 부서, 셀 기준 정보를 필터링해 현재 조직 구성을 빠르게 검토할 수 있습니다.",
        kicker="Master Data",
    )
    render_section_open("필터")
    departments = get_departments()
    department_lookup = {row.department_name: int(row.department_id) for row in departments.itertuples(index=False)}
    department_names = ["전체"] + list(department_lookup.keys())
    selected_department_name = st.selectbox("부서 필터", department_names)
    department_id = None if selected_department_name == "전체" else department_lookup[selected_department_name]

    cells = get_cells_by_department(department_id)
    cell_lookup = {row.cell_name: int(row.cell_id) for row in cells.itertuples(index=False)}
    cell_names = ["전체"] + list(cell_lookup.keys())
    selected_cell_name = st.selectbox("셀 필터", cell_names)
    cell_id = None if selected_cell_name == "전체" else cell_lookup[selected_cell_name]
    render_section_close()

    employees = get_employees(department_id=department_id, cell_id=cell_id)
    metric_cols = st.columns(4)
    metric_cols[0].metric("직원 수", f"{len(employees)}명")
    metric_cols[1].metric("부서", selected_department_name)
    metric_cols[2].metric("셀", selected_cell_name)
    metric_cols[3].metric("이메일 필드", "포함")
    st.dataframe(employees, use_container_width=True)


def render_authenticated_app() -> None:
    user = current_user()
    if not user:
        render_login_page()
        return

    st.sidebar.markdown("## 광주은행")
    st.sidebar.caption("주간업무보고 서비스")
    if SYMBOL_IMAGE.exists():
        st.sidebar.image(str(SYMBOL_IMAGE), width=72)
    st.sidebar.write(f"사용자: **{user['display_name']}**")
    st.sidebar.write(f"아이디: **{user['username']}**")
    st.sidebar.write(f"권한: **{user['role']}**")
    if user.get("email"):
        st.sidebar.write(f"이메일: **{user['email']}**")
    if st.sidebar.button("로그아웃"):
        st.session_state.pop("auth_user", None)
        st.rerun()

    if is_admin(user):
        menu_items = ["주간업무보고 작성", "전체/셀 보고서 조회", "차트 분석", "미작성자 확인", "기초정보 조회"]
    else:
        menu_items = ["주간업무보고 작성", "내 보고서 조회"]

    menu = st.sidebar.radio("메뉴", menu_items)

    if menu == "주간업무보고 작성":
        render_report_write_page(user)
    elif menu == "전체/셀 보고서 조회":
        render_report_query_page()
    elif menu == "차트 분석":
        render_chart_analysis_page()
    elif menu == "미작성자 확인":
        render_not_submitted_page()
    elif menu == "기초정보 조회":
        render_employee_page()
    else:
        render_my_report_page(user)


def main() -> None:
    inject_theme()
    render_connection_status()
    render_authenticated_app()


if __name__ == "__main__":
    main()
