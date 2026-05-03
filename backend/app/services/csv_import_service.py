import os
import uuid
from typing import Dict
import pandas as pd
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import ImportValidationException
from app.services.sales_transformer import transform_and_load


ALLOWED_EXTENSIONS = {".csv"}
MAX_SIZE_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
KEY_COLUMN_DTYPES = {
    "order_number": "string",
    "customer_code": "string",
    "product_code": "string",
}


def validate_file(upload: UploadFile) -> None:
    """Validate uploaded file extension, MIME type and size."""
    filename = upload.filename or ""
    ext = os.path.splitext(filename)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise ImportValidationException(f"Invalid file extension: {ext}. Only CSV files are allowed.")

    content_type = upload.content_type or ""
    if content_type and not (
        "csv" in content_type
        or content_type == "application/octet-stream"
        or content_type == "text/plain"
    ):
        raise ImportValidationException(f"Invalid content type: {content_type}")

    # Read and check size
    contents = upload.file.read()
    if len(contents) > MAX_SIZE_BYTES:
        raise ImportValidationException(f"File exceeds maximum size of {settings.MAX_UPLOAD_SIZE_MB}MB")

    # Reset file pointer for downstream
    upload.file.seek(0)


def save_upload_file(upload: UploadFile) -> str:
    """Save uploaded file to disk and return path."""
    ext = os.path.splitext(upload.filename or "")[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, unique_name)

    with open(filepath, "wb") as f:
        f.write(upload.file.read())

    upload.file.seek(0)
    return filepath


def import_sales_csv(upload: UploadFile, db: Session) -> Dict:
    """End-to-end CSV import: validate, save, read, clean, transform, load."""
    validate_file(upload)
    filepath = save_upload_file(upload)

    try:
        df = pd.read_csv(filepath, dtype=KEY_COLUMN_DTYPES)
        if df.empty:
            raise ImportValidationException("CSV file is empty")
        result = transform_and_load(df, db, upload.filename or "unknown.csv")
        if result["status"] == "failed" and result.get("errors"):
            raise ImportValidationException("; ".join(result["errors"]))
        return result
    except Exception as e:
        if isinstance(e, ImportValidationException):
            raise
        raise ImportValidationException(f"Failed to parse CSV: {str(e)}")
    finally:
        try:
            os.remove(filepath)
        except OSError:
            pass
