from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_database_session
from app.schemas.order import OrderDetailRead, OrderListParams, OrderItemRead
from app.schemas.common import PaginatedResponse
from app.services.order_service import get_orders, get_order_by_id, get_recent_orders_service

router = APIRouter()


@router.get("", response_model=PaginatedResponse[OrderDetailRead])
def list_orders(
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    sort_by: str = Query("order_date"),
    sort_order: str = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_database_session),
):
    params = OrderListParams(
        search=search,
        status=status,
        country=country,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )
    result = get_orders(db, params)
    # Convert ORM to detail schema
    items = []
    for o in result["items"]:
        items.append(OrderDetailRead(
            id=o.id,
            order_number=o.order_number,
            customer_id=o.customer_id,
            order_date=o.order_date,
            status=o.status,
            total_amount=float(o.total_amount),
            discount_amount=float(o.discount_amount),
            shipping_amount=float(o.shipping_amount),
            country=o.country,
            city=o.city,
            created_at=o.created_at,
            updated_at=o.updated_at,
            customer_name=f"{o.customer.first_name} {o.customer.last_name}",
            items=[],
            payment_status=o.payment.payment_status if o.payment else "",
            payment_method=o.payment.payment_method if o.payment else "",
        ))
    return PaginatedResponse[OrderDetailRead](
        items=items,
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
        pages=result["pages"],
    )


@router.get("/recent", response_model=list[OrderDetailRead])
def recent_orders(db: Session = Depends(get_database_session)):
    orders = get_recent_orders_service(db, limit=10)
    return [
        OrderDetailRead(
            id=o.id,
            order_number=o.order_number,
            customer_id=o.customer_id,
            order_date=o.order_date,
            status=o.status,
            total_amount=float(o.total_amount),
            discount_amount=float(o.discount_amount),
            shipping_amount=float(o.shipping_amount),
            country=o.country,
            city=o.city,
            created_at=o.created_at,
            updated_at=o.updated_at,
            customer_name=f"{o.customer.first_name} {o.customer.last_name}",
            items=[],
            payment_status=o.payment.payment_status if o.payment else "",
            payment_method=o.payment.payment_method if o.payment else "",
        )
        for o in orders
    ]


@router.get("/{order_id}", response_model=OrderDetailRead)
def get_order(order_id: int, db: Session = Depends(get_database_session)):
    o = get_order_by_id(db, order_id)
    if not o:
        raise HTTPException(status_code=404, detail="Order not found")
    return OrderDetailRead(
        id=o.id,
        order_number=o.order_number,
        customer_id=o.customer_id,
        order_date=o.order_date,
        status=o.status,
        total_amount=float(o.total_amount),
        discount_amount=float(o.discount_amount),
        shipping_amount=float(o.shipping_amount),
        country=o.country,
        city=o.city,
        created_at=o.created_at,
        updated_at=o.updated_at,
        customer_name=f"{o.customer.first_name} {o.customer.last_name}",
        items=[
            OrderItemRead(
                id=i.id,
                product_id=i.product_id,
                quantity=i.quantity,
                unit_price=float(i.unit_price),
                discount_amount=float(i.discount_amount),
                line_total=float(i.line_total),
                created_at=i.created_at,
                updated_at=i.updated_at,
            )
            for i in o.items
        ],
        payment_status=o.payment.payment_status if o.payment else "",
        payment_method=o.payment.payment_method if o.payment else "",
    )
