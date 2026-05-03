from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_database_session
from app.schemas.imports import ImportResponse
from app.services.csv_import_service import import_sales_csv

router = APIRouter()


@router.post("/sales", response_model=ImportResponse)
def import_sales_csv_endpoint(
    file: UploadFile = File(...),
    db: Session = Depends(get_database_session),
):
    """Upload and import a sales CSV file."""
    result = import_sales_csv(file, db)
    return ImportResponse(**result)
