from typing import Optional, List
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.order import Order
from app.models.customer import Customer
from app.schemas.order import OrderListParams

ORDER_SORT_COLUMNS = {
    "id": Order.id,
    "order_number": Order.order_number,
    "order_date": Order.order_date,
    "status": Order.status,
    "total_amount": Order.total_amount,
    "country": Order.country,
    "created_at": Order.created_at,
}


def get_orders(db: Session, params: OrderListParams):
    q = db.query(Order).join(Customer)

    if params.search:
        q = q.filter(
            (Order.order_number.ilike(f"%{params.search}%")) |
            (Customer.first_name.ilike(f"%{params.search}%")) |
            (Customer.last_name.ilike(f"%{params.search}%"))
        )

    if params.status:
        q = q.filter(Order.status == params.status)

    if params.country:
        q = q.filter(Order.country == params.country)

    if params.date_from:
        q = q.filter(Order.order_date >= params.date_from)

    if params.date_to:
        q = q.filter(Order.order_date <= params.date_to)

    sort_col = ORDER_SORT_COLUMNS.get(params.sort_by, Order.order_date)
    if params.sort_order == "desc":
        q = q.order_by(desc(sort_col))
    else:
        q = q.order_by(sort_col)

    total = q.count()
    items = q.offset((params.page - 1) * params.page_size).limit(params.page_size).all()
    pages = (total + params.page_size - 1) // params.page_size if total > 0 else 1

    return {
        "items": items,
        "total": total,
        "page": params.page,
        "page_size": params.page_size,
        "pages": pages,
    }


def get_order_by_id(db: Session, order_id: int) -> Optional[Order]:
    return db.query(Order).filter_by(id=order_id).first()


def get_recent_orders_service(db: Session, limit: int = 10):
    return db.query(Order).order_by(desc(Order.order_date)).limit(limit).all()
