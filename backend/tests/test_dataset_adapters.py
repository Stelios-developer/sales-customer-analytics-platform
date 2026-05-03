import pandas as pd

from app.services.dataset_adapters import convert_online_retail_dataframe
from app.services.data_cleaning import REQUIRED_COLUMNS


def test_convert_online_retail_dataframe():
    raw = pd.DataFrame(
        {
            "InvoiceNo": ["536365", "536365", "C536366", "536367"],
            "StockCode": ["85123A", "85123A", "71053", "84406B"],
            "Description": ["WHITE HANGING HEART T-LIGHT HOLDER", "WHITE HANGING HEART T-LIGHT HOLDER", "WHITE METAL LANTERN", "CREAM CUPID HEARTS COAT HANGER"],
            "Quantity": [6, 2, -1, 4],
            "InvoiceDate": ["2010-12-01 08:26:00", "2010-12-01 08:26:00", "2010-12-01 08:28:00", "2010-12-01 08:34:00"],
            "UnitPrice": [2.55, 2.55, 3.39, 2.75],
            "CustomerID": [17850, 17850, 17850, 13047],
            "Country": ["United Kingdom", "United Kingdom", "United Kingdom", "United Kingdom"],
        }
    )

    converted = convert_online_retail_dataframe(raw)

    assert list(converted.columns) == REQUIRED_COLUMNS
    assert len(converted) == 2
    assert converted.iloc[0]["order_number"] == "536365"
    assert converted.iloc[0]["quantity"] == 8
    assert converted.iloc[0]["customer_code"] == "CUST-17850"
    assert converted.iloc[0]["payment_status"] == "paid"
    assert converted.iloc[0]["order_status"] == "completed"
