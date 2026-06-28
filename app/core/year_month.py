import re

DB_YEAR_MONTH_RE = re.compile(r"^\d{6}$")
UI_YEAR_MONTH_RE = re.compile(r"^\d{4}-\d{2}$")


def validate_db_year_month(value: str) -> bool:
    return bool(value and DB_YEAR_MONTH_RE.fullmatch(value))


def validate_ui_year_month(value: str) -> bool:
    return bool(value and UI_YEAR_MONTH_RE.fullmatch(value))


def to_db_year_month(value: str) -> str:
    if validate_db_year_month(value):
        return value
    if not validate_ui_year_month(value):
        raise ValueError(f"Invalid UI year_month format: {value!r}")
    return value.replace("-", "")


def to_ui_year_month(value: str) -> str:
    if validate_ui_year_month(value):
        return value
    if not validate_db_year_month(value):
        raise ValueError(f"Invalid DB year_month format: {value!r}")
    return f"{value[:4]}-{value[4:]}"
