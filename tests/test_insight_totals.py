from datetime import datetime, timezone
from decimal import Decimal

from common.insight_totals import compute_totals
from common.time_utils import relative_time

SAMPLE = [
    {"type": "credit", "balanceField": "CURRENT", "balance": 1200.50},
    {"type": "credit", "balanceField": "CURRENT", "balance": 300.25},
    {"type": "depository", "balanceField": "AVAILABLE", "balance": 5000.00},
    {"type": "investment", "balanceField": "AVAILABLE", "balance": 12450.31, "current": 48210.0},
    {"type": "investment", "balanceField": "CURRENT", "balance": 99999.00},
    {"type": "loan", "balanceField": "CURRENT", "balance": 7777.00},
]


def test_totals():
    t = compute_totals(SAMPLE)
    assert t.total_liability == Decimal("1500.75")
    assert t.total_cash == Decimal("17450.31")
    assert t.net_position == Decimal("15949.56")


def test_empty_and_none_balance():
    assert compute_totals([]).net_position == 0
    assert compute_totals([{"type": "credit", "balance": None}]).total_liability == 0


def test_relative_time():
    now = datetime(2026, 11, 16, 16, 5, 12, tzinfo=timezone.utc)
    assert relative_time("2026-11-16T14:05:12Z", now) == "2h ago"
    assert relative_time("2026-11-16T16:04:50Z", now) == "just now"
    assert relative_time("2026-11-13T16:05:12Z", now) == "3d ago"
    assert relative_time("garbage", now) == "unknown"
