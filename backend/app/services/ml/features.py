from typing import List, Dict, Optional
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd
import numpy as np
from app.models.order import Order
from app.models.customer import Customer
from app.models.order_item import OrderItem


def get_daily_sales_features(db: Session, date_from: Optional[date] = None, date_to: Optional[date] = None) -> pd.DataFrame:
    """Aggregate daily sales from the database for forecasting."""
    q = db.query(
        Order.order_date,
        func.sum(Order.total_amount).label("revenue"),
        func.count(Order.id).label("orders"),
    ).group_by(Order.order_date).order_by(Order.order_date)

    if date_from:
        q = q.filter(Order.order_date >= date_from)
    if date_to:
        q = q.filter(Order.order_date <= date_to)

    rows = q.all()
    if not rows:
        return pd.DataFrame(columns=["date", "revenue", "orders"])

    df = pd.DataFrame([{"date": r.order_date, "revenue": float(r.revenue), "orders": r.orders} for r in rows])
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    return df


def get_customer_rfm_features(db: Session) -> pd.DataFrame:
    """Generate RFM-style features for customer segmentation."""
    latest_order_date = db.query(func.max(Order.order_date)).scalar()
    reference_date = (latest_order_date + timedelta(days=1)) if latest_order_date else date.today()

    customers = db.query(Customer).all()
    if not customers:
        return pd.DataFrame()

    records = []
    for customer in customers:
        orders = sorted(customer.orders, key=lambda o: o.order_date, reverse=True)
        if not orders:
            continue

        recency_days = max((reference_date - orders[0].order_date).days, 0)
        frequency = len(orders)

        monetary_value = sum(float(o.total_amount) for o in orders)
        aov = monetary_value / frequency if frequency > 0 else 0.0

        records.append({
            "customer_id": customer.id,
            "customer_name": f"{customer.first_name} {customer.last_name}",
            "recency_days": recency_days,
            "frequency": frequency,
            "monetary_value": monetary_value,
            "average_order_value": aov,
        })

    return pd.DataFrame(records)
