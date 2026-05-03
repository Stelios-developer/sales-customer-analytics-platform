from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.models.product import Product
from app.models.order_item import OrderItem


def get_products(db: Session, search: Optional[str] = None, category: Optional[str] = None, skip: int = 0, limit: int = 100):
    q = db.query(Product)
    if search:
        q = q.filter(Product.name.ilike(f"%{search}%"))
    if category:
        q = q.filter(Product.category == category)
    return q.offset(skip).limit(limit).all()


def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
    return db.query(Product).filter_by(id=product_id).first()


def get_top_products_service(db: Session, limit: int = 10):
    return db.query(
        Product.id,
        Product.name,
        Product.category,
        func.sum(OrderItem.quantity).label("qty"),
        func.sum(OrderItem.line_total).label("revenue"),
        func.sum(OrderItem.line_total - (OrderItem.quantity * Product.cost_price)).label("profit"),
    ).join(OrderItem).group_by(
        Product.id,
        Product.name,
        Product.category,
    ).order_by(desc("revenue")).limit(limit).all()


def get_product_categories(db: Session) -> List[str]:
    rows = db.query(Product.category).distinct().all()
    return [r[0] for r in rows]
