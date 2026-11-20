"""Pure time helpers."""

import re
from datetime import datetime, timezone


def parse_iso(value: str) -> datetime:
    """Parse ISO-8601 (incl. trailing 'Z' / long fractions) on Python 3.10+."""
    text = value.strip()
    if text.endswith(("Z", "z")):
        text = text[:-1] + "+00:00"
    text = re.sub(r"(\.\d{6})\d+", r"\1", text)
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def relative_time(iso_value: str, now: datetime | None = None) -> str:
    try:
        then = parse_iso(iso_value)
    except (ValueError, TypeError, AttributeError):
        return "unknown"
    now = now or datetime.now(timezone.utc)
    seconds = int((now - then).total_seconds())
    if seconds < 60:
        return "just now"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h ago"
    return f"{hours // 24}d ago"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
