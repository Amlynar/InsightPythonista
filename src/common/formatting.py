from decimal import ROUND_HALF_UP, Decimal


def format_money(value: Decimal) -> str:
    cents = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    sign = "-" if cents < 0 else ""
    return f"{sign}${abs(cents):,.2f}"
