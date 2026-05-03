from datetime import date
from sqlalchemy.orm import Session
from app.services.analytics_service import get_kpis
from app.models.customer import Customer
from app.models.product import Product
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.payment import Payment
from app.utils.money_utils import to_decimal


def seed_test_data(db: Session):
    customer = Customer(customer_code="C001", first_name="Alice", last_name="Anderson", email="alice@test.com", country="Greece", city="Athens")
    db.add(customer)
    db.flush()

    product = Product(product_code="P001", name="Laptop", category="Electronics", unit_price=to_decimal(1000), cost_price=to_decimal(700))
    db.add(product)
    db.flush()

    order = Order(order_number="ORD001", customer_id=customer.id, order_date=date(2024, 1, 15), status="completed", total_amount=to_decimal(1000), country="Greece", city="Athens")
    db.add(order)
    db.flush()

    item = OrderItem(order_id=order.id, product_id=product.id, quantity=1, unit_price=to_decimal(1000), line_total=to_decimal(1000))
    db.add(item)

    payment = Payment(order_id=order.id, payment_method="card", payment_status="paid", paid_amount=to_decimal(1000), payment_date=date(2024, 1, 15))
    db.add(payment)

    db.commit()


def test_kpis_empty_db(db_session: Session):
    result = get_kpis(db_session)
    assert result["total_revenue"] == 0.0
    assert result["number_of_orders"] == 0


def test_kpis_with_data(db_session: Session):
    seed_test_data(db_session)
    result = get_kpis(db_session)
    assert result["total_revenue"] == 1000.0
    assert result["number_of_orders"] == 1
    assert result["number_of_customers"] == 1
    assert result["top_product"] == "Laptop"
    assert result["best_country"] == "Greece"
