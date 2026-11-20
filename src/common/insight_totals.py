"""Pure classification/aggregation of /accounts data. No I/O, no UI."""

from dataclasses import dataclass
from decimal import Decimal


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


def compute_totals(accounts) -> Totals:
    """Sum `balance` per the classification rules.

    Accounts matching neither rule (e.g. loans) are excluded from both totals.
    `balance` is trusted as-is; never re-derived from current/available.
    """
    cash = Decimal(0)
    liability = Decimal(0)
    for account in accounts or []:
        if is_liability(account):
            liability += _to_decimal(account.get("balance"))
        elif is_cash(account):
            cash += _to_decimal(account.get("balance"))
    return Totals(total_cash=cash, total_liability=liability)
