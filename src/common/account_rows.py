"""Pure view-model for the per-category account list. No I/O, no UI."""

from dataclasses import dataclass
from decimal import Decimal

from common.formatting import format_money
from common.insight_totals import accounts_in_category
from common.time_utils import relative_time

TAG_REAUTH = "reauth"
TAG_STALE = "stale"


@dataclass(frozen=True)
class AccountRow:
    title: str
    institution_text: str
    balance_text: str
    tag_text: str | None
    tag_kind: str | None


def _title(account: dict) -> str:
    return account.get("name") or "Account"


def _institution(account: dict) -> str:
    institution = account.get("institutionName") or ""
    mask = account.get("mask")
    if mask:
        return f"{institution} (...{mask})".strip()
    return institution


def _tag(account: dict, reauth_link_ids: set) -> tuple[str | None, str | None]:
    # Order matters: reauth (actionable) beats stale (informational).
    if account.get("linkId") in reauth_link_ids:
        return "Needs reauthorization", TAG_REAUTH
    if account.get("stale") is True:
        fetched_at = account.get("fetchedAt")
        if fetched_at:
            return f"Updated {relative_time(fetched_at)}", TAG_STALE
        return "No data yet", TAG_STALE
    return None, None


def build_rows(response: dict, category: str) -> list[AccountRow]:
    reauth_ids = {link.get("id") for link in response.get("linksNeedingReauth") or []}
    rows = []
    for account in accounts_in_category(response.get("accounts"), category):
        balance = account.get("balance")
        balance_text = "\u2014" if balance is None else format_money(Decimal(str(balance)))
        tag_text, tag_kind = _tag(account, reauth_ids)
        rows.append(AccountRow(_title(account), _institution(account), balance_text,
                               tag_text, tag_kind))
    return rows
