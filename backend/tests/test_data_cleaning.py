import pandas as pd
from app.services.data_cleaning import (
    validate_columns,
    clean_amount,
    clean_customer_name,
    clean_country,
    clean_status,
    clean_category,
    validate_positive_quantity,
    validate_monetary_value,
    parse_date,
    clean_dataframe,
)


def test_validate_columns_success():
    df = pd.DataFrame(columns=["order_number", "order_date", "customer_code", "product_code"])
    # Should fail since not all required columns present
    valid, missing = validate_columns(df)
    assert valid is False
    assert len(missing) > 0


def test_validate_columns_full():
    required = [
        "order_number", "order_date", "customer_code", "customer_first_name",
        "customer_last_name", "customer_email", "customer_country", "customer_city",
        "product_code", "product_name", "product_category", "quantity",
        "unit_price", "cost_price", "discount_amount", "shipping_amount",
        "payment_method", "payment_status", "payment_date", "order_status"
    ]
    df = pd.DataFrame(columns=required)
    valid, missing = validate_columns(df)
    assert valid is True
    assert len(missing) == 0


def test_clean_amount():
    assert clean_amount("1,234.56") == 1234.56
    assert clean_amount("1.234,56") == 1234.56
    assert clean_amount("$100.50") == 100.50
    assert clean_amount(42) == 42.0
    assert clean_amount(None) == 0.0


def test_clean_customer_name():
    assert clean_customer_name("  john   doe ") == "John Doe"
    assert clean_customer_name("") == "Unknown"


def test_clean_country():
    assert clean_country("usa") == "United States"
    assert clean_country("Deutschland") == "Germany"
    assert clean_country("Greece") == "Greece"


def test_clean_status():
    assert clean_status("PAID") == "paid"
    assert clean_status("Completed") == "completed"
    assert clean_status("") == "pending"


def test_clean_category():
    assert clean_category("Electronics") == "Electronics"
    assert clean_category("office supply") == "Office Supplies"
    assert clean_category("") == "Uncategorized"


def test_validate_positive_quantity():
    assert validate_positive_quantity(5) == 5
    assert validate_positive_quantity(-3) == 1
    assert validate_positive_quantity("abc") == 1


def test_validate_monetary_value():
    assert validate_monetary_value("100.50") == 100.50
    assert validate_monetary_value(-20) == 0.0


def test_parse_date():
    assert parse_date("2024-01-15").strftime("%Y-%m-%d") == "2024-01-15"
    assert parse_date("15/01/2024").strftime("%Y-%m-%d") == "2024-01-15"
    assert parse_date("invalid") is None


def test_clean_dataframe():
    df = pd.DataFrame({
        "order_number": ["ORD001", "ORD001"],
        "order_date": ["2024-01-15", "2024-01-16"],
        "customer_code": ["C001", "C001"],
        "customer_first_name": ["john", "jane"],
        "customer_last_name": ["doe", "smith"],
        "customer_email": ["john@test.com", None],
        "customer_country": ["usa", "germany"],
        "customer_city": ["NYC", None],
        "product_code": ["P001", "P002"],
        "product_name": ["Widget", "Gadget"],
        "product_category": ["electronics", "books"],
        "quantity": [2, 3],
        "unit_price": ["10.00", "20.00"],
        "cost_price": ["5.00", "10.00"],
        "discount_amount": ["0", "1.00"],
        "shipping_amount": ["2.00", "3.00"],
        "payment_method": ["card", "bank"],
        "payment_status": ["paid", "pending"],
        "payment_date": ["2024-01-15", "2024-01-16"],
        "order_status": ["completed", "shipped"],
    })
    cleaned, validation = clean_dataframe(df)
    assert len(validation["errors"]) == 0
    assert len(cleaned) == 2
    assert cleaned.iloc[0]["customer_country"] == "United States"
    assert cleaned.iloc[0]["customer_city"] == "Nyc"
