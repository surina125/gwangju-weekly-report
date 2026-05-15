CREATE TABLE IF NOT EXISTS departments (
    department_id INTEGER PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cells (
    cell_id INTEGER PRIMARY KEY,
    department_id INTEGER NOT NULL REFERENCES departments(department_id),
    cell_name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS employees (
    employee_id INTEGER PRIMARY KEY,
    emp_no VARCHAR(7) NOT NULL UNIQUE,
    employee_name VARCHAR(50) NOT NULL,
    department_id INTEGER NOT NULL REFERENCES departments(department_id),
    cell_id INTEGER NOT NULL REFERENCES cells(cell_id),
    email VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS weekly_reports (
    report_id INTEGER PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(employee_id),
    week_start DATE NOT NULL,
    week_end DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT '미작성',
    submitted_at TIMESTAMP NULL,
    reminder_sent_at TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (employee_id, week_start, week_end)
);

CREATE TABLE IF NOT EXISTS weekly_report_items (
    item_id INTEGER PRIMARY KEY,
    report_id INTEGER NOT NULL REFERENCES weekly_reports(report_id) ON DELETE CASCADE,
    sr_title VARCHAR(200) NOT NULL,
    progress INTEGER NOT NULL CHECK (progress BETWEEN 0 AND 100),
    sr_dev_content TEXT NOT NULL,
    sort_order INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS weekly_notifications (
    notification_id INTEGER PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(employee_id),
    week_start DATE NOT NULL,
    week_end DATE NOT NULL,
    check_time VARCHAR(50),
    notification_type VARCHAR(50) NOT NULL,
    target_status VARCHAR(20) NOT NULL,
    message TEXT,
    sent_yn CHAR(1) NOT NULL DEFAULT 'N',
    checked_at TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS app_users (
    user_id SERIAL PRIMARY KEY,
    employee_id INTEGER NULL REFERENCES employees(employee_id),
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role VARCHAR(20) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_cells_department_id ON cells (department_id);
CREATE INDEX IF NOT EXISTS idx_employees_department_cell ON employees (department_id, cell_id);
CREATE INDEX IF NOT EXISTS idx_weekly_reports_period ON weekly_reports (week_start, week_end);
CREATE INDEX IF NOT EXISTS idx_weekly_reports_employee ON weekly_reports (employee_id);
CREATE INDEX IF NOT EXISTS idx_weekly_report_items_report ON weekly_report_items (report_id);
CREATE INDEX IF NOT EXISTS idx_app_users_username ON app_users (username);
