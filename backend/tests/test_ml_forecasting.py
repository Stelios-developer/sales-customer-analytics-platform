from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.customer import Customer
from app.models.order import Order
from app.services.ml.forecasting import train_forecast_model


def test_train_forecast_insufficient_data(db_session: Session):
    result = train_forecast_model(db_session)
    assert result["status"] == "insufficient_data"
    assert "message" in result


def test_train_forecast_uses_xgboost(db_session: Session, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "ARTIFACT_DIR", str(tmp_path))

    customer = Customer(
        customer_code="C001",
        first_name="Forecast",
        last_name="Customer",
        email="forecast@test.com",
        country="United Kingdom",
        city="London",
    )
    db_session.add(customer)
    db_session.flush()

    start = date(2024, 1, 1)
    for i in range(70):
        db_session.add(Order(
            order_number=f"FC{i:03d}",
            customer_id=customer.id,
            order_date=start + timedelta(days=i),
            status="completed",
            total_amount=100 + (i * 3) + ((i % 7) * 20),
            discount_amount=0,
            shipping_amount=0,
            country="United Kingdom",
            city="London",
        ))
    db_session.commit()

    result = train_forecast_model(db_session)

    assert result["model_name"] == "XGBoostRegressor"
    assert result["training_rows"] > 0
    assert "mae" in result
