from __future__ import annotations

import re
from typing import Iterable

import pandas as pd

from app.services.data_cleaning import REQUIRED_COLUMNS


ONLINE_RETAIL_REQUIRED_COLUMNS = {
    "InvoiceNo",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
    "CustomerID",
    "Country",
}


def _normalize_customer_id(value) -> str:
    if pd.isna(value):
        return ""
    try:
        return str(int(float(value)))
    except (TypeError, ValueError):
        return re.sub(r"\W+", "", str(value).strip())


def _infer_product_category(description: str) -> str:
    text = str(description or "").lower()
    rules: Iterable[tuple[str, str]] = [
        ("christmas|easter|valentine|holiday", "Seasonal"),
        ("bag|purse|wallet|tote", "Accessories"),
        ("mug|cup|glass|bottle|teapot|plate|bowl", "Kitchenware"),
        ("candle|holder|lantern|light|lamp", "Home Decor"),
        ("card|paper|notebook|pencil|pen|stationery", "Office Supplies"),
        ("toy|game|doll|children|child", "Toys"),
        ("jewellery|necklace|bracelet|earring", "Accessories"),
        ("garden|plant|flower", "Garden"),
    ]
    for pattern, category in rules:
        if re.search(pattern, text):
            return category
    return "General Merchandise"


def convert_online_retail_dataframe(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert the common Online Retail dataset format into the platform CSV schema.

    Expected input columns:
    InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country.

    Notes:
    - Cancelled invoices and non-positive quantities/prices are removed.
    - Customer names/emails are anonymized because the source dataset does not contain them.
    - Cost price is estimated at 65% of unit price because the source dataset has sales price only.
    """
    df = raw_df.copy()
    df.columns = [str(column).strip() for column in df.columns]

    missing = sorted(ONLINE_RETAIL_REQUIRED_COLUMNS - set(df.columns))
    if missing:
        raise ValueError(f"Missing Online Retail columns: {', '.join(missing)}")

    df = df[list(ONLINE_RETAIL_REQUIRED_COLUMNS)].copy()
    df["InvoiceNo"] = df["InvoiceNo"].astype(str).str.strip()
    df["StockCode"] = df["StockCode"].astype(str).str.strip()
    df["Description"] = df["Description"].astype(str).str.strip()
    df["Country"] = df["Country"].astype(str).str.strip()
    df["CustomerID"] = df["CustomerID"].apply(_normalize_customer_id)
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    df["UnitPrice"] = pd.to_numeric(df["UnitPrice"], errors="coerce")
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")

    df = df[
        df["InvoiceNo"].ne("")
        & ~df["InvoiceNo"].str.startswith("C", na=False)
        & df["StockCode"].ne("")
        & df["Description"].ne("")
        & df["CustomerID"].ne("")
        & df["Country"].ne("")
        & df["InvoiceDate"].notna()
        & df["Quantity"].gt(0)
        & df["UnitPrice"].gt(0)
    ].copy()

    df["order_date"] = df["InvoiceDate"].dt.date.astype(str)
    df["product_category"] = df["Description"].apply(_infer_product_category)

    group_cols = [
        "InvoiceNo",
        "order_date",
        "CustomerID",
        "Country",
        "StockCode",
        "Description",
        "product_category",
        "UnitPrice",
    ]
    grouped = (
        df.groupby(group_cols, as_index=False, dropna=False)
        .agg(quantity=("Quantity", "sum"))
        .sort_values(["order_date", "InvoiceNo", "StockCode"])
    )

    converted = pd.DataFrame(
        {
            "order_number": grouped["InvoiceNo"],
            "order_date": grouped["order_date"],
            "customer_code": "CUST-" + grouped["CustomerID"],
            "customer_first_name": "Customer",
            "customer_last_name": grouped["CustomerID"].astype(str),
            "customer_email": "customer_" + grouped["CustomerID"].astype(str) + "@example.invalid",
            "customer_country": grouped["Country"],
            "customer_city": "Unknown",
            "product_code": grouped["StockCode"],
            "product_name": grouped["Description"].str.title().str.slice(0, 255),
            "product_category": grouped["product_category"],
            "quantity": grouped["quantity"].round().astype(int),
            "unit_price": grouped["UnitPrice"].round(2),
            "cost_price": (grouped["UnitPrice"] * 0.65).round(2),
            "discount_amount": 0.0,
            "shipping_amount": 0.0,
            "payment_method": "Unknown",
            "payment_status": "paid",
            "payment_date": grouped["order_date"],
            "order_status": "completed",
        }
    )

    return converted[REQUIRED_COLUMNS]
