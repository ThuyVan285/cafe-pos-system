# FILE: utils/formatter.py
from datetime import datetime
from config.settings import APP_CONFIG


def format_currency(amount: int | float) -> str:
    """Format integer VND amount to display string."""
    return f"{int(amount):,}{APP_CONFIG.currency_symbol}"


def format_datetime(dt: datetime, fmt: str = "%d/%m/%Y %H:%M") -> str:
    return dt.strftime(fmt) if dt else ""


def format_date(dt: datetime) -> str:
    return dt.strftime("%d/%m/%Y") if dt else ""


def format_percent(value: float) -> str:
    return f"{value * 100:.0f}%"


def short_name(name: str, max_len: int = 18) -> str:
    return name if len(name) <= max_len else name[:max_len - 1] + "…"