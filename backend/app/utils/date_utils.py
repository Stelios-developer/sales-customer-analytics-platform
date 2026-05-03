from datetime import datetime, date
from typing import Optional, List
import pandas as pd


def parse_date(date_value, formats: Optional[List[str]] = None) -> Optional[date]:
    """Parse a date from multiple possible formats."""
    if formats is None:
        formats = [
            "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y",
            "%d-%m-%Y", "%m-%d-%Y", "%Y/%m/%d",
            "%d.%m.%Y", "%Y%m%d"
        ]

    if pd.isna(date_value):
        return None

    if isinstance(date_value, (datetime, pd.Timestamp)):
        return date_value.date()

    value = str(date_value).strip()

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue

    return None


def to_iso_month(d: date) -> str:
    return d.strftime("%Y-%m")
