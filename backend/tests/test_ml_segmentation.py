from datetime import date
from sqlalchemy.orm import Session
from app.core.config import settings
from app.services.ml.customer_segmentation import train_segmentation_model
from app.services.ml.features import get_customer_rfm_features
from app.models.customer import Customer
from app.models.order import Order


def test_train_segmentation_insufficient_data(db_session: Session):
    result = train_segmentation_model(db_session)
    assert result["status"] == "insufficient_data"
    assert "message" in result


def test_rfm_recency_uses_dataset_reference_date(db_session: Session):
    customer = Customer(
        customer_code="C001",
        first_name="Jane",
        last_name="Doe",
        email="jane@test.com",
        country="United Kingdom",
        city="London",
    )
    db_session.add(customer)
    db_session.flush()

    db_session.add_all([
        Order(
            order_number="OLD001",
            customer_id=customer.id,
            order_date=date(2011, 1, 1),
            status="completed",
            total_amount=100,
            discount_amount=0,
            shipping_amount=0,
            country="United Kingdom",
            city="London",
        ),
        Order(
            order_number="NEW001",
            customer_id=customer.id,
            order_date=date(2011, 1, 10),
            status="completed",
            total_amount=200,
            discount_amount=0,
            shipping_amount=0,
            country="United Kingdom",
            city="London",
        ),
    ])
    db_session.commit()

    df = get_customer_rfm_features(db_session)

    assert len(df) == 1
    assert int(df.iloc[0]["recency_days"]) == 1


def test_train_segmentation_uses_gaussian_mixture(db_session: Session, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "ARTIFACT_DIR", str(tmp_path))

    start = date(2024, 1, 1)
    for i in range(8):
        customer = Customer(
            customer_code=f"C{i:03d}",
            first_name="Segment",
            last_name=str(i),
            email=f"segment{i}@test.com",
            country="United Kingdom",
            city="London",
        )
        db_session.add(customer)
        db_session.flush()

        for order_idx in range(1 + (i % 4)):
            db_session.add(Order(
                order_number=f"SEG{i:03d}-{order_idx}",
                customer_id=customer.id,
                order_date=start.replace(day=1 + i + order_idx),
                status="completed",
                total_amount=100 + (i * 50) + (order_idx * 20),
                discount_amount=0,
                shipping_amount=0,
                country="United Kingdom",
                city="London",
            ))
    db_session.commit()

    result = train_segmentation_model(db_session)

    assert result["model_name"] == "GaussianMixture"
    assert result["n_components"] == 4
    assert result["covariance_type"] == "full"
    assert result["training_rows"] == 8
