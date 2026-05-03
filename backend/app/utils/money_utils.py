from decimal import Decimal, InvalidOperation
import re


def clean_amount(value) -> float:
    """Clean a monetary value from strings such as '$1,234.56' or '1.234,56'."""
    if value is None or (isinstance(value, float) and value != value):
        return 0.0

    if isinstance(value, (int, float)):
        return float(value)

    value = str(value).strip()
    is_negative = value.startswith("(") and value.endswith(")")

    value = re.sub(r"[^\d,.\-]", "", value)

    if "," in value and "." in value:
        if value.rfind(",") > value.rfind("."):
            value = value.replace(".", "").replace(",", ".")
        else:
            value = value.replace(",", "")
    elif "," in value:
        parts = value.split(",")
        if len(parts) == 2 and len(parts[1]) <= 2:
            value = value.replace(",", ".")
        else:
            value = value.replace(",", "")

    try:
        amount = float(value)
        return -amount if is_negative and amount > 0 else amount
    except ValueError:
        return 0.0


def to_decimal(value) -> Decimal:
    """Convert a value to Decimal safely."""
    try:
        return Decimal(str(clean_amount(value))).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        return Decimal("0.00")
