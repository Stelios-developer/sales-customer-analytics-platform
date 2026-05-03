from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.models.customer import Customer
from app.models.order import Order
from app.schemas.customer import CustomerSummary


def get_customers(db: Session, search: Optional[str] = None, country: Optional[str] = None, skip: int = 0, limit: int = 100):
    q = db.query(Customer)
    if search:
        q = q.filter(
            (Customer.first_name.ilike(f"%{search}%")) |
            (Customer.last_name.ilike(f"%{search}%")) |
            (Customer.email.ilike(f"%{search}%"))
        )
    if country:
        q = q.filter(Customer.country == country)
    return q.offset(skip).limit(limit).all()


def get_customer_by_id(db: Session, customer_id: int) -> Optional[Customer]:
    return db.query(Customer).filter_by(id=customer_id).first()


def get_customer_orders(db: Session, customer_id: int):
    return db.query(Order).filter_by(customer_id=customer_id).order_by(desc(Order.order_date)).all()


def get_top_customers_service(db: Session, limit: int = 10) -> List[CustomerSummary]:
    q = db.query(
        Customer.id,
        Customer.first_name,
        Customer.last_name,
        Customer.country,
        func.count(Order.id).label("orders"),
        func.sum(Order.total_amount).label("spent"),
    ).join(Order).group_by(
        Customer.id,
        Customer.first_name,
        Customer.last_name,
        Customer.country,
    ).order_by(desc("spent")).limit(limit)

    return [
        CustomerSummary(
            customer_id=row.id,
            customer_name=f"{row.first_name} {row.last_name}",
            country=row.country,
            orders=int(row.orders),
            total_spent=float(row.spent),
            average_order_value=float(row.spent) / int(row.orders) if int(row.orders) > 0 else 0.0,
        )
        for row in q.all()
    ]


def get_customer_segments(db: Session) -> List[Dict]:
    q = db.query(Customer.segment, func.count(Customer.id)).group_by(Customer.segment).all()
    return [{"segment": row.segment or "Unsegmented", "count": row[1]} for row in q]
