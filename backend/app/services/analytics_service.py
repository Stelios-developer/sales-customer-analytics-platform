from datetime import date
from typing import Dict, List, Optional

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.payment import Payment
from app.models.product import Product


def _apply_order_date_filters(query, date_from: Optional[date] = None, date_to: Optional[date] = None):
    if date_from:
        query = query.filter(Order.order_date >= date_from)
    if date_to:
        query = query.filter(Order.order_date <= date_to)
    return query


def _month_expression(db: Session):
    if db.bind and db.bind.dialect.name == "sqlite":
        return func.strftime("%Y-%m", Order.order_date)
    return func.to_char(Order.order_date, "YYYY-MM")


def _as_float(value) -> float:
    return float(value or 0)


def get_kpis(db: Session, date_from: Optional[date] = None, date_to: Optional[date] = None) -> Dict:
    """Calculate core KPIs from database."""
    order_query = _apply_order_date_filters(db.query(Order), date_from, date_to)
    orders = order_query.all()

    if not orders:
        return {
            "total_revenue": 0.0,
            "total_profit": 0.0,
            "number_of_orders": 0,
            "number_of_customers": 0,
            "number_of_products": 0,
            "average_order_value": 0.0,
            "conversion_proxy": 0.0,
            "paid_revenue": 0.0,
            "pending_revenue": 0.0,
            "top_product": None,
            "top_customer": None,
            "best_country": None,
        }

    items_query = _apply_order_date_filters(db.query(OrderItem).join(Order), date_from, date_to)
    items = items_query.all()

    total_revenue = sum(_as_float(o.total_amount) for o in orders)
    total_cost = sum(_as_float(i.quantity) * _as_float(i.product.cost_price) for i in items)
    total_profit = total_revenue - total_cost
    number_of_orders = len(orders)
    average_order_value = total_revenue / number_of_orders if number_of_orders else 0.0

    payments = _apply_order_date_filters(db.query(Payment).join(Order), date_from, date_to).all()
    paid_revenue = sum(_as_float(p.paid_amount) for p in payments if p.payment_status == "paid")
    pending_revenue = sum(_as_float(p.order.total_amount) for p in payments if p.payment_status == "pending")
    conversion_proxy = (paid_revenue / total_revenue * 100) if total_revenue > 0 else 0.0

    product_revenue: Dict[int, float] = {}
    for item in items:
        product_revenue[item.product_id] = product_revenue.get(item.product_id, 0.0) + _as_float(item.line_total)
    top_product = None
    if product_revenue:
        product = db.query(Product).filter(Product.id == max(product_revenue, key=product_revenue.get)).first()
        top_product = product.name if product else None

    customer_revenue: Dict[int, float] = {}
    country_revenue: Dict[str, float] = {}
    for order in orders:
        customer_revenue[order.customer_id] = customer_revenue.get(order.customer_id, 0.0) + _as_float(order.total_amount)
        country_revenue[order.country] = country_revenue.get(order.country, 0.0) + _as_float(order.total_amount)

    top_customer = None
    if customer_revenue:
        customer = db.query(Customer).filter(Customer.id == max(customer_revenue, key=customer_revenue.get)).first()
        top_customer = f"{customer.first_name} {customer.last_name}" if customer else None

    return {
        "total_revenue": round(total_revenue, 2),
        "total_profit": round(total_profit, 2),
        "number_of_orders": number_of_orders,
        "number_of_customers": len({o.customer_id for o in orders}),
        "number_of_products": len({i.product_id for i in items}),
        "average_order_value": round(average_order_value, 2),
        "conversion_proxy": round(conversion_proxy, 2),
        "paid_revenue": round(paid_revenue, 2),
        "pending_revenue": round(pending_revenue, 2),
        "top_product": top_product,
        "top_customer": top_customer,
        "best_country": max(country_revenue, key=country_revenue.get) if country_revenue else None,
    }


def get_monthly_sales(db: Session, date_from: Optional[date] = None, date_to: Optional[date] = None) -> List[Dict]:
    """Aggregate sales by month."""
    month_expr = _month_expression(db)

    revenue_query = db.query(
        month_expr.label("month"),
        func.sum(Order.total_amount).label("revenue"),
        func.count(Order.id).label("orders"),
    )
    revenue_query = _apply_order_date_filters(revenue_query, date_from, date_to)
    revenue_rows = revenue_query.group_by(month_expr).order_by(month_expr).all()

    profit_query = db.query(
        month_expr.label("month"),
        func.sum(OrderItem.line_total - (OrderItem.quantity * Product.cost_price)).label("profit"),
    ).join(OrderItem, OrderItem.order_id == Order.id).join(Product, Product.id == OrderItem.product_id)
    profit_query = _apply_order_date_filters(profit_query, date_from, date_to)
    profit_by_month = {
        row.month: _as_float(row.profit)
        for row in profit_query.group_by(month_expr).all()
    }

    return [
        {
            "month": row.month,
            "revenue": round(_as_float(row.revenue), 2),
            "profit": round(profit_by_month.get(row.month, 0.0), 2),
            "orders": int(row.orders),
        }
        for row in revenue_rows
    ]


def get_top_products(db: Session, limit: int = 10, date_from: Optional[date] = None, date_to: Optional[date] = None) -> List[Dict]:
    """Get top products by revenue."""
    query = db.query(
        Product.id,
        Product.name,
        Product.category,
        func.sum(OrderItem.quantity).label("qty"),
        func.sum(OrderItem.line_total).label("revenue"),
        func.sum(OrderItem.line_total - (OrderItem.quantity * Product.cost_price)).label("profit"),
    ).join(OrderItem, OrderItem.product_id == Product.id).join(Order, Order.id == OrderItem.order_id)

    query = _apply_order_date_filters(query, date_from, date_to)
    rows = (
        query.group_by(Product.id, Product.name, Product.category)
        .order_by(desc("revenue"))
        .limit(limit)
        .all()
    )

    return [
        {
            "product_id": row.id,
            "product_name": row.name,
            "category": row.category,
            "quantity_sold": int(row.qty or 0),
            "revenue": round(_as_float(row.revenue), 2),
            "profit": round(_as_float(row.profit), 2),
        }
        for row in rows
    ]


def get_top_customers(db: Session, limit: int = 10, date_from: Optional[date] = None, date_to: Optional[date] = None) -> List[Dict]:
    """Get top customers by total spent."""
    query = db.query(
        Customer.id,
        Customer.first_name,
        Customer.last_name,
        Customer.country,
        func.count(Order.id).label("orders"),
        func.sum(Order.total_amount).label("spent"),
    ).join(Order, Order.customer_id == Customer.id)

    query = _apply_order_date_filters(query, date_from, date_to)
    rows = (
        query.group_by(Customer.id, Customer.first_name, Customer.last_name, Customer.country)
        .order_by(desc("spent"))
        .limit(limit)
        .all()
    )

    return [
        {
            "customer_id": row.id,
            "customer_name": f"{row.first_name} {row.last_name}",
            "country": row.country,
            "orders": int(row.orders),
            "total_spent": round(_as_float(row.spent), 2),
            "average_order_value": round(_as_float(row.spent) / int(row.orders), 2) if int(row.orders) else 0.0,
        }
        for row in rows
    ]


def get_sales_by_country(db: Session, date_from: Optional[date] = None, date_to: Optional[date] = None) -> List[Dict]:
    """Aggregate sales by country."""
    query = db.query(
        Order.country,
        func.sum(Order.total_amount).label("revenue"),
        func.count(Order.id).label("orders"),
        func.count(func.distinct(Order.customer_id)).label("customers"),
    )
    query = _apply_order_date_filters(query, date_from, date_to)
    rows = query.group_by(Order.country).order_by(desc("revenue")).all()

    return [
        {
            "country": row.country,
            "revenue": round(_as_float(row.revenue), 2),
            "orders": int(row.orders),
            "customers": int(row.customers),
        }
        for row in rows
    ]


def get_sales_by_category(db: Session, date_from: Optional[date] = None, date_to: Optional[date] = None) -> List[Dict]:
    """Aggregate sales by product category."""
    query = db.query(
        Product.category,
        func.sum(OrderItem.line_total).label("revenue"),
        func.sum(OrderItem.line_total - (OrderItem.quantity * Product.cost_price)).label("profit"),
        func.count(func.distinct(Order.id)).label("orders"),
        func.sum(OrderItem.quantity).label("qty"),
    ).join(OrderItem, OrderItem.product_id == Product.id).join(Order, Order.id == OrderItem.order_id)

    query = _apply_order_date_filters(query, date_from, date_to)
    rows = query.group_by(Product.category).order_by(desc("revenue")).all()

    return [
        {
            "category": row.category,
            "revenue": round(_as_float(row.revenue), 2),
            "profit": round(_as_float(row.profit), 2),
            "orders": int(row.orders),
            "quantity_sold": int(row.qty or 0),
        }
        for row in rows
    ]


def get_payment_methods_summary(db: Session, date_from: Optional[date] = None, date_to: Optional[date] = None) -> List[Dict]:
    """Aggregate by payment method."""
    query = db.query(
        Payment.payment_method,
        func.sum(Payment.paid_amount).label("total"),
        func.count(Payment.id).label("count"),
    ).join(Order, Order.id == Payment.order_id)

    query = _apply_order_date_filters(query, date_from, date_to)
    rows = query.group_by(Payment.payment_method).order_by(desc("total")).all()

    return [
        {
            "payment_method": row.payment_method,
            "total": round(_as_float(row.total), 2),
            "count": int(row.count),
        }
        for row in rows
    ]


def get_order_status_summary(db: Session, date_from: Optional[date] = None, date_to: Optional[date] = None) -> List[Dict]:
    """Aggregate by order status."""
    query = db.query(
        Order.status,
        func.count(Order.id).label("count"),
        func.sum(Order.total_amount).label("revenue"),
    )
    query = _apply_order_date_filters(query, date_from, date_to)
    rows = query.group_by(Order.status).order_by(desc("count")).all()

    return [
        {
            "status": row.status,
            "count": int(row.count),
            "revenue": round(_as_float(row.revenue), 2),
        }
        for row in rows
    ]


def get_profit_summary(db: Session, date_from: Optional[date] = None, date_to: Optional[date] = None) -> Dict:
    """Calculate overall profit summary."""
    orders = _apply_order_date_filters(db.query(Order), date_from, date_to).all()
    total_revenue = sum(_as_float(o.total_amount) for o in orders)

    items = _apply_order_date_filters(db.query(OrderItem).join(Order), date_from, date_to).all()
    total_cost = sum(_as_float(i.quantity) * _as_float(i.product.cost_price) for i in items)
    total_profit = total_revenue - total_cost
    margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0.0

    return {
        "total_revenue": round(total_revenue, 2),
        "total_cost": round(total_cost, 2),
        "total_profit": round(total_profit, 2),
        "profit_margin_pct": round(margin, 2),
    }


def get_recent_orders(db: Session, limit: int = 10) -> List[Dict]:
    """Get most recent orders."""
    orders = db.query(Order).order_by(Order.order_date.desc(), Order.id.desc()).limit(limit).all()
    return [
        {
            "order_id": o.id,
            "order_number": o.order_number,
            "customer_name": f"{o.customer.first_name} {o.customer.last_name}",
            "total_amount": round(_as_float(o.total_amount), 2),
            "status": o.status,
            "order_date": o.order_date.isoformat(),
        }
        for o in orders
    ]
