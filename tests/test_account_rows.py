from datetime import datetime, timezone
from decimal import Decimal

from common.account_rows import TAG_REAUTH, TAG_STALE, build_rows
from common.insight_totals import CASH, LIABILITY, accounts_in_category, compute_totals

RESPONSE = {
    "linksNeedingReauth": [{"id": "L2", "institutionName": "Chase"}],
    "accounts": [
        {"linkId": "L1", "institutionName": "Ally", "name": "Savings", "type": "depository",
         "balanceField": "AVAILABLE", "balance": 1000.5, "stale": False},
        {"linkId": "L2", "institutionName": "Chase", "name": "Sapphire", "type": "credit",
         "balanceField": "CURRENT", "balance": 300.25, "stale": True,
         "fetchedAt": "2026-11-16T14:05:12Z"},
        {"linkId": "L3", "institutionName": "Fidelity", "name": "Brokerage", "type": "investment",
         "balanceField": "AVAILABLE", "balance": 50, "stale": True,
         "fetchedAt": "2000-01-01T00:00:00Z"},
        {"linkId": "L3", "institutionName": "Fidelity", "name": "Empty", "type": "depository",
         "balance": None, "fetchedAt": None, "stale": True},
        {"linkId": "L4", "institutionName": "Bank", "name": "Loan", "type": "loan",
         "balanceField": "CURRENT", "balance": 9},
    ],
}


def test_list_matches_totals():
    cash = accounts_in_category(RESPONSE["accounts"], CASH)
    liab = accounts_in_category(RESPONSE["accounts"], LIABILITY)
    assert [a["name"] for a in cash] == ["Savings", "Brokerage", "Empty"]
    assert [a["name"] for a in liab] == ["Sapphire"]
    totals = compute_totals(RESPONSE["accounts"])
    assert totals.total_cash == sum(Decimal(str(a["balance"] or 0)) for a in cash)
    assert totals.total_liability == Decimal("300.25")


def test_cash_rows_tags_and_formatting():
    rows = build_rows(RESPONSE, CASH)
    assert rows[0].title == "Savings"
    assert rows[0].institution_text == "Ally"
    assert rows[0].balance_text == "$1,000.50"
    assert rows[0].tag_text is None
    assert rows[1].tag_kind == TAG_STALE and rows[1].tag_text.startswith("Updated ")
    assert rows[2].balance_text == "\u2014"
    assert rows[2].tag_text == "No data yet"


def test_reauth_beats_stale():
    (row,) = build_rows(RESPONSE, LIABILITY)
    assert row.tag_kind == TAG_REAUTH
    assert row.tag_text == "Needs reauthorization"


def test_empty_category():
    assert build_rows({"accounts": []}, CASH) == []
