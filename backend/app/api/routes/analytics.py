from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.deps import get_database_session
from app.services.analytics_service import (
    get_kpis,
    get_monthly_sales,
    get_top_products,
    get_top_customers,
    get_sales_by_country,
    get_sales_by_category,
    get_payment_methods_summary,
    get_order_status_summary,
    get_profit_summary,
    get_recent_orders,
)

router = APIRouter()


@router.get("/kpis")
def kpis(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_database_session),
):
    return get_kpis(db, date_from=date_from, date_to=date_to)


@router.get("/monthly-sales")
def monthly_sales(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_database_session),
):
    return get_monthly_sales(db, date_from=date_from, date_to=date_to)


@router.get("/top-products")
def top_products(
    limit: int = Query(10, ge=1, le=50),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_database_session),
):
    return get_top_products(db, limit=limit, date_from=date_from, date_to=date_to)


@router.get("/top-customers")
def top_customers(
    limit: int = Query(10, ge=1, le=50),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_database_session),
):
    return get_top_customers(db, limit=limit, date_from=date_from, date_to=date_to)


@router.get("/sales-by-country")
def sales_by_country(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_database_session),
):
    return get_sales_by_country(db, date_from=date_from, date_to=date_to)


@router.get("/sales-by-category")
def sales_by_category(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_database_session),
):
    return get_sales_by_category(db, date_from=date_from, date_to=date_to)


@router.get("/payment-methods")
def payment_methods(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_database_session),
):
    return get_payment_methods_summary(db, date_from=date_from, date_to=date_to)


@router.get("/order-status")
def order_status(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_database_session),
):
    return get_order_status_summary(db, date_from=date_from, date_to=date_to)


@router.get("/profit-summary")
def profit_summary(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_database_session),
):
    return get_profit_summary(db, date_from=date_from, date_to=date_to)


@router.get("/recent-orders")
def recent_orders(db: Session = Depends(get_database_session)):
    return get_recent_orders(db, limit=10)
