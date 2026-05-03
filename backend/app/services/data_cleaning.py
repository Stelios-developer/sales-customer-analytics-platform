import re
from typing import Dict, List, Optional, Tuple
import pandas as pd
from app.utils.date_utils import parse_date
from app.utils.money_utils import clean_amount


REQUIRED_COLUMNS = [
    "order_number", "order_date", "customer_code", "customer_first_name",
    "customer_last_name", "customer_email", "customer_country", "customer_city",
    "product_code", "product_name", "product_category", "quantity",
    "unit_price", "cost_price", "discount_amount", "shipping_amount",
    "payment_method", "payment_status", "payment_date", "order_status"
]


def validate_columns(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Check if DataFrame contains all required columns."""
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    return len(missing) == 0, missing


def clean_customer_name(name: str) -> str:
    """Normalize customer names: title case, strip extra spaces."""
    if pd.isna(name) or not name:
        return "Unknown"
    name = re.sub(r"\s+", " ", str(name).strip())
    return name.title()


def clean_country(country: str) -> str:
    """Normalize country names."""
    if pd.isna(country) or not country:
        return "Unknown"
    country = str(country).strip().title()
    mapping = {
        "Usa": "United States",
        "Us": "United States",
        "Uk": "United Kingdom",
        "Great Britain": "United Kingdom",
        "England": "United Kingdom",
        "Deutschland": "Germany",
        "Nederland": "Netherlands",
        "Holland": "Netherlands",
        "Hellas": "Greece",
        "Ellada": "Greece",
        "Kypros": "Cyprus",
    }
    return mapping.get(country, country)


def clean_status(status: str, valid_statuses: Optional[List[str]] = None) -> str:
    """Normalize order/payment status to lowercase standardized form."""
    if valid_statuses is None:
        valid_statuses = ["pending", "completed", "paid", "failed", "refunded", "cancelled", "shipped"]
    if pd.isna(status) or not status:
        return "pending"
    s = re.sub(r"[^a-z]+", "_", str(status).strip().lower()).strip("_")
    aliases = {
        "complete": "completed",
        "completed": "completed",
        "paid": "paid",
        "payment_paid": "paid",
        "pending": "pending",
        "in_progress": "pending",
        "failed": "failed",
        "declined": "failed",
        "refunded": "refunded",
        "cancelled": "cancelled",
        "canceled": "cancelled",
        "shipped": "shipped",
        "fulfilled": "shipped",
    }
    normalized = aliases.get(s, s)
    return normalized if normalized in valid_statuses else "pending"


def clean_category(category: str) -> str:
    """Standardize product categories."""
    if pd.isna(category) or not category:
        return "Uncategorized"
    raw = str(category).strip()
    key = re.sub(r"[^a-z0-9]+", " ", raw.lower()).strip()
    aliases = {
        "office supply": "Office Supplies",
        "office supplies": "Office Supplies",
        "home office": "Home Office",
        "cloud service": "Cloud Services",
        "cloud services": "Cloud Services",
    }
    if key in aliases:
        return aliases[key]

    cat = raw.title()
    valid = [
        "Electronics", "Software", "Office Supplies", "Home Office",
        "Books", "Accessories", "Consulting", "Cloud Services", "Training"
    ]
    for v in valid:
        if v.lower() in cat.lower():
            return v
    return cat


def validate_positive_quantity(qty) -> int:
    """Ensure quantity is a positive integer."""
    try:
        val = int(float(qty))
        return val if val > 0 else 1
    except (ValueError, TypeError):
        return 1


def validate_monetary_value(value, allow_negative: bool = False) -> float:
    """Clean and validate a monetary value."""
    cleaned = clean_amount(value)
    if not allow_negative and cleaned < 0:
        return 0.0
    return cleaned


def remove_duplicate_rows(df: pd.DataFrame, subset: Optional[List[str]] = None) -> pd.DataFrame:
    """Remove duplicate rows based on key columns."""
    if subset is None:
        subset = ["order_number", "product_code"]
    return df.drop_duplicates(subset=subset, keep="first")


def clean_dataframe(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, List[str]]]:
    """
    Main data cleaning pipeline.
    Returns cleaned DataFrame and dict of warnings/errors.
    """
    warnings: List[str] = []
    errors: List[str] = []

    df = df.copy()
    df.columns = [str(col).strip() for col in df.columns]

    # Validate required columns
    valid, missing = validate_columns(df)
    if not valid:
        errors.append(f"Missing required columns: {', '.join(missing)}")
        return df, {"warnings": warnings, "errors": errors}

    # Remove exact duplicates
    before = len(df)
    df = remove_duplicate_rows(df)
    dupes = before - len(df)
    if dupes > 0:
        warnings.append(f"{dupes} duplicate rows removed")

    # Clean dates
    invalid_dates = 0
    for col in ["order_date", "payment_date"]:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: parse_date(x))
            if col == "order_date":
                invalid_dates = df[col].isna().sum()
    if invalid_dates > 0:
        warnings.append(f"{invalid_dates} invalid dates detected")
        # Drop rows with invalid order_date
        df = df.dropna(subset=["order_date"])

    # Clean monetary columns
    monetary_cols = ["unit_price", "cost_price", "discount_amount", "shipping_amount"]
    for col in monetary_cols:
        if col in df.columns:
            df[col] = df[col].apply(validate_monetary_value)

    # Clean quantity
    df["quantity"] = df["quantity"].apply(validate_positive_quantity)

    # Clean text fields
    df["customer_first_name"] = df["customer_first_name"].apply(clean_customer_name)
    df["customer_last_name"] = df["customer_last_name"].apply(clean_customer_name)
    df["customer_country"] = df["customer_country"].apply(clean_country)
    df["customer_city"] = df["customer_city"].fillna("Unknown").apply(lambda x: str(x).strip().title() if pd.notna(x) else "Unknown")
    df["product_category"] = df["product_category"].apply(clean_category)
    df["order_status"] = df["order_status"].apply(lambda x: clean_status(x, ["pending", "completed", "cancelled", "shipped", "refunded"]))
    df["payment_status"] = df["payment_status"].apply(lambda x: clean_status(x, ["pending", "paid", "failed", "refunded"]))

    # Fill missing emails
    missing_emails = df["customer_email"].isna().sum()
    if missing_emails > 0:
        warnings.append(f"{missing_emails} missing customer emails")
        df["customer_email"] = df["customer_email"].fillna("")

    # Clean email format loosely
    df["customer_email"] = df["customer_email"].apply(lambda x: str(x).strip().lower() if pd.notna(x) else "")

    # Calculate line totals
    df["line_total"] = (df["quantity"] * df["unit_price"] - df["discount_amount"]).round(2)
    df["line_total"] = df["line_total"].clip(lower=0)

    suspicious = df[df["line_total"] == 0]
    if len(suspicious) > 0:
        warnings.append(f"{len(suspicious)} rows with zero line total after discount")

    return df, {"warnings": warnings, "errors": errors}
