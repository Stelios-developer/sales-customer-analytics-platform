from typing import Dict, List, Tuple
import pandas as pd
from datetime import date
from sqlalchemy.orm import Session
from app.models.customer import Customer
from app.models.product import Product
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.payment import Payment
from app.models.data_import_log import DataImportLog
from app.utils.money_utils import to_decimal
from app.services.data_cleaning import clean_dataframe
from app.core.logging import logger


def transform_and_load(df: pd.DataFrame, db: Session, filename: str) -> Dict:
    """
    Transform denormalized sales CSV into relational tables and load into database.
    Returns import summary dict.
    """
    df, validation = clean_dataframe(df)

    if validation["errors"]:
        log = DataImportLog(
            filename=filename,
            rows_processed=len(df),
            rows_inserted=0,
            rows_failed=len(df),
            status="failed",
            error_message="; ".join(validation["errors"]),
        )
        db.add(log)
        db.commit()
        return {
            "status": "failed",
            "filename": filename,
            "rows_processed": len(df),
            "rows_inserted": 0,
            "rows_failed": len(df),
            "warnings": validation["warnings"],
            "errors": validation["errors"]
        }

    key_columns = ["order_number", "customer_code", "product_code"]
    for column in key_columns:
        df[column] = df[column].astype("string").fillna("").str.strip()

    warnings = validation["warnings"]
    rows_processed = len(df)
    rows_inserted = 0
    rows_failed = 0

    try:
        # Pre-load existing customers and products to avoid repeated queries
        existing_customers = {c.customer_code: c for c in db.query(Customer).all()}
        existing_products = {p.product_code: p for p in db.query(Product).all()}
        existing_orders = {o.order_number: o for o in db.query(Order).all()}

        customers_to_add: Dict[str, Customer] = {}
        products_to_add: Dict[str, Product] = {}
        orders_to_add: Dict[str, Order] = {}
        order_identity: Dict[str, Tuple[str, object]] = {
            o.order_number: (str(o.customer_id), o.order_date) for o in existing_orders.values()
        }
        skipped_rows: set[int] = set()

        for idx, row in df.iterrows():
            try:
                customer_code = str(row["customer_code"]).strip()
                product_code = str(row["product_code"]).strip()
                order_number = str(row["order_number"]).strip()
                order_date = row["order_date"] if isinstance(row["order_date"], date) else row["order_date"].date() if hasattr(row["order_date"], "date") else row["order_date"]

                if not customer_code or not product_code or not order_number:
                    rows_failed += 1
                    skipped_rows.add(idx)
                    warnings.append(f"Row {idx + 2} skipped because key fields are blank")
                    continue

                # Customer
                if customer_code not in existing_customers and customer_code not in customers_to_add:
                    customer = Customer(
                        customer_code=customer_code,
                        first_name=row["customer_first_name"],
                        last_name=row["customer_last_name"],
                        email=row.get("customer_email", ""),
                        country=row["customer_country"],
                        city=row["customer_city"],
                    )
                    customers_to_add[customer_code] = customer

                # Product
                if product_code not in existing_products and product_code not in products_to_add:
                    product = Product(
                        product_code=product_code,
                        name=row["product_name"],
                        category=row["product_category"],
                        unit_price=to_decimal(row["unit_price"]),
                        cost_price=to_decimal(row["cost_price"]),
                    )
                    products_to_add[product_code] = product

                # Order
                if order_number not in existing_orders and order_number not in orders_to_add:
                    customer = existing_customers.get(customer_code) or customers_to_add.get(customer_code)
                    order = Order(
                        order_number=order_number,
                        customer_id=customer.id if customer and hasattr(customer, 'id') and customer.id else None,
                        order_date=order_date,
                        status=row["order_status"],
                        total_amount=to_decimal(0),  # Will recalc after items
                        discount_amount=to_decimal(row["discount_amount"]),
                        shipping_amount=to_decimal(row["shipping_amount"]),
                        country=row["customer_country"],
                        city=row["customer_city"],
                    )
                    orders_to_add[order_number] = order
                    order_identity[order_number] = (customer_code, order_date)
                elif order_number in order_identity:
                    original_customer, original_date = order_identity[order_number]
                    if str(original_customer) != customer_code and not str(original_customer).isdigit():
                        rows_failed += 1
                        skipped_rows.add(idx)
                        warnings.append(f"Row {idx + 2} skipped because order_number {order_number} conflicts with an earlier customer")
                        continue
                    if original_date != order_date:
                        rows_failed += 1
                        skipped_rows.add(idx)
                        warnings.append(f"Row {idx + 2} skipped because order_number {order_number} conflicts with an earlier order_date")
                        continue

            except Exception as e:
                rows_failed += 1
                skipped_rows.add(idx)
                logger.warning("Row transform error: %s", e)
                continue

        # Bulk insert customers
        if customers_to_add:
            db.add_all(customers_to_add.values())
            db.flush()
            for c in customers_to_add.values():
                existing_customers[c.customer_code] = c

        # Bulk insert products
        if products_to_add:
            db.add_all(products_to_add.values())
            db.flush()
            for p in products_to_add.values():
                existing_products[p.product_code] = p

        # Fix order customer_ids and bulk insert orders
        for order_number, order in orders_to_add.items():
            row = df[df["order_number"] == order_number].iloc[0]
            customer_code = str(row["customer_code"]).strip()
            customer = existing_customers.get(customer_code)
            if customer:
                order.customer_id = customer.id

        if orders_to_add:
            db.add_all(orders_to_add.values())
            db.flush()
            for o in orders_to_add.values():
                existing_orders[o.order_number] = o

        # Now create order items
        for idx, row in df.iterrows():
            if idx in skipped_rows:
                continue
            try:
                order_number = str(row["order_number"]).strip()
                product_code = str(row["product_code"]).strip()
                order = existing_orders.get(order_number)
                product = existing_products.get(product_code)

                if not order or not product:
                    rows_failed += 1
                    continue

                # Check for duplicate item
                existing_item = db.query(OrderItem).filter_by(
                    order_id=order.id, product_id=product.id
                ).first()
                if existing_item:
                    continue

                item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=int(row["quantity"]),
                    unit_price=to_decimal(row["unit_price"]),
                    discount_amount=to_decimal(row["discount_amount"]),
                    line_total=to_decimal(row["line_total"]),
                )
                db.add(item)
                rows_inserted += 1

            except Exception as e:
                rows_failed += 1
                logger.warning("Item insert error: %s", e)

        # SessionLocal uses autoflush=False, so pending items must be flushed
        # before querying them to recalculate order totals.
        db.flush()

        # Recalculate order totals
        for order_number in df["order_number"].unique():
            order = existing_orders.get(str(order_number).strip())
            if not order:
                continue
            items = db.query(OrderItem).filter_by(order_id=order.id).all()
            total = sum(i.line_total for i in items)
            order.total_amount = total + order.shipping_amount

        # Create one payment per order, even when the CSV has multiple item rows
        # for the same order.
        payment_order_ids = {order_id for (order_id,) in db.query(Payment.order_id).all()}

        # Create payments
        for idx, row in df.iterrows():
            if idx in skipped_rows:
                continue
            try:
                order_number = str(row["order_number"]).strip()
                order = existing_orders.get(order_number)
                if not order:
                    continue

                if order.id in payment_order_ids:
                    continue

                payment_date = row.get("payment_date")
                if hasattr(payment_date, 'date'):
                    payment_date = payment_date.date()

                payment = Payment(
                    order_id=order.id,
                    payment_method=row["payment_method"],
                    payment_status=row["payment_status"],
                    paid_amount=order.total_amount if row["payment_status"] == "paid" else to_decimal(0),
                    payment_date=payment_date if isinstance(payment_date, date) else None,
                )
                db.add(payment)
                payment_order_ids.add(order.id)
            except Exception as e:
                logger.warning("Payment insert error: %s", e)

        db.commit()

    except Exception as e:
        db.rollback()
        logger.error("Import failed: %s", e)
        return {
            "status": "failed",
            "filename": filename,
            "rows_processed": rows_processed,
            "rows_inserted": 0,
            "rows_failed": rows_failed,
            "warnings": warnings,
            "errors": [str(e)]
        }

    # Save import log
    log = DataImportLog(
        filename=filename,
        rows_processed=rows_processed,
        rows_inserted=rows_inserted,
        rows_failed=rows_failed,
        status="success" if rows_inserted > 0 else "partial",
    )
    db.add(log)
    db.commit()

    return {
        "status": "success",
        "filename": filename,
        "rows_processed": rows_processed,
        "rows_inserted": rows_inserted,
        "rows_failed": rows_failed,
        "warnings": warnings,
        "errors": []
    }
