"""Pure classification/aggregation of /accounts data. No I/O, no UI."""

from dataclasses import dataclass
from decimal import Decimal

CASH = "cash"
LIABILITY = "liability"


@dataclass(frozen=True)
class Totals:
    total_cash: Decimal
    total_liability: Decimal

    @property
    def net_position(self) -> Decimal:
        return self.total_cash - self.total_liability


def _to_decimal(value) -> Decimal:
    if value is None:
        return Decimal(0)
    return Decimal(str(value))


def is_liability(account: dict) -> bool:
    return account.get("type") == "credit"


def is_cash(account: dict) -> bool:
    acct_type = account.get("type")
    if acct_type == "depository":
        return True
    return acct_type == "investment" and account.get("balanceField") == "AVAILABLE"


def classify(account: dict) -> str | None:
    """Single source of truth: CASH, LIABILITY, or None (e.g. loans)."""
    if is_liability(account):
        return LIABILITY
    if is_cash(account):
        return CASH
    return None


def accounts_in_category(accounts, category: str) -> list[dict]:
    """Accounts behind a total, in input order. Same rule compute_totals sums."""
    return [a for a in accounts or [] if classify(a) == category]


def compute_totals(accounts) -> Totals:
    """Sum `balance` per the classification rules.

    Accounts matching neither rule (e.g. loans) are excluded from both totals.
    `balance` is trusted as-is; never re-derived from current/available.
    """
    cash = sum((_to_decimal(a.get("balance")) for a in accounts_in_category(accounts, CASH)),
               Decimal(0))
    liability = sum((_to_decimal(a.get("balance"))
                     for a in accounts_in_category(accounts, LIABILITY)), Decimal(0))
    return Totals(total_cash=cash, total_liability=liability)
