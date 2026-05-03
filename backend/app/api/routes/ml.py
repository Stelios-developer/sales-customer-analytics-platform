from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_database_session
from app.services.ml.forecasting import train_forecast_model, get_sales_forecast
from app.services.ml.customer_segmentation import train_segmentation_model, get_customer_segments
from app.schemas.ml import TrainForecastResponse, ForecastResponse, TrainSegmentationResponse, SegmentationResponse

router = APIRouter()


@router.post("/train-forecast")
def train_forecast(db: Session = Depends(get_database_session)):
    result = train_forecast_model(db)
    if "status" in result:
        return {"status": result["status"], "message": result["message"]}
    return TrainForecastResponse(**result)


@router.get("/sales-forecast")
def sales_forecast(db: Session = Depends(get_database_session)):
    result = get_sales_forecast(db)
    if isinstance(result, dict) and "status" in result and result["status"] != "success":
        return {"status": result["status"], "message": result.get("message", ""), "forecast": []}
    return ForecastResponse(
        status="success",
        forecast=result["forecast"],
    )


@router.post("/train-segmentation")
def train_segmentation(db: Session = Depends(get_database_session)):
    result = train_segmentation_model(db)
    if "status" in result:
        return {"status": result["status"], "message": result["message"]}
    return TrainSegmentationResponse(**result)


@router.get("/customer-segments")
def customer_segments(db: Session = Depends(get_database_session)):
    result = get_customer_segments(db)
    if isinstance(result, dict) and "status" in result and result["status"] != "success":
        return {"status": result["status"], "message": result.get("message", ""), "customers": [], "summary": []}
    return SegmentationResponse(
        status="success",
        customers=result["customers"],
        summary=result["summary"],
    )
