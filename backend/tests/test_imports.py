import io
from fastapi.testclient import TestClient


def test_import_csv_success(client: TestClient):
    csv_content = """order_number,order_date,customer_code,customer_first_name,customer_last_name,customer_email,customer_country,customer_city,product_code,product_name,product_category,quantity,unit_price,cost_price,discount_amount,shipping_amount,payment_method,payment_status,payment_date,order_status
ORD001,2024-01-15,C001,John,Doe,john@test.com,USA,NYC,P001,Widget,Electronics,2,10.00,5.00,0.00,2.00,card,paid,2024-01-15,completed
ORD002,2024-01-16,C002,Jane,Smith,jane@test.com,Germany,Berlin,P002,Gadget,Software,1,50.00,25.00,0.00,3.00,bank,paid,2024-01-16,completed
"""
    response = client.post(
        "/api/imports/sales",
        files={"file": ("test.csv", io.BytesIO(csv_content.encode()), "text/csv")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["rows_processed"] == 2
    assert data["rows_inserted"] == 2
    assert data["rows_failed"] == 0

    kpi_response = client.get("/api/analytics/kpis")
    assert kpi_response.status_code == 200
    kpis = kpi_response.json()
    assert kpis["number_of_orders"] == 2
    assert kpis["total_revenue"] == 75.0
    assert kpis["average_order_value"] == 37.5


def test_import_csv_bad_extension(client: TestClient):
    response = client.post(
        "/api/imports/sales",
        files={"file": ("test.txt", io.BytesIO(b"not a csv"), "text/plain")},
    )
    assert response.status_code == 422


def test_import_csv_numeric_order_number(client: TestClient):
    csv_content = """order_number,order_date,customer_code,customer_first_name,customer_last_name,customer_email,customer_country,customer_city,product_code,product_name,product_category,quantity,unit_price,cost_price,discount_amount,shipping_amount,payment_method,payment_status,payment_date,order_status
536365,2024-01-15,17850,Jane,Doe,jane@test.com,United Kingdom,London,85123A,White Mug,Home Office,2,10.00,6.50,0.00,0.00,card,paid,2024-01-15,completed
536365,2024-01-15,17850,Jane,Doe,jane@test.com,United Kingdom,London,71053,Red Bowl,Home Office,1,50.00,32.50,0.00,0.00,card,paid,2024-01-15,completed
"""
    response = client.post(
        "/api/imports/sales",
        files={"file": ("numeric-orders.csv", io.BytesIO(csv_content.encode()), "text/csv")},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["rows_processed"] == 2
    assert data["rows_inserted"] == 2
    assert data["rows_failed"] == 0

    kpi_response = client.get("/api/analytics/kpis")
    assert kpi_response.status_code == 200
    kpis = kpi_response.json()
    assert kpis["number_of_orders"] == 1
    assert kpis["total_revenue"] == 70.0
