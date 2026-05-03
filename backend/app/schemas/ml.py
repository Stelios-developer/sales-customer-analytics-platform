from pydantic import BaseModel, ConfigDict
from typing import List, Optional


class ForecastPoint(BaseModel):
    date: str
    predicted_revenue: float


class ForecastResponse(BaseModel):
    status: str
    forecast: List[ForecastPoint]
    message: Optional[str] = None


class TrainForecastResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    model_name: str
    mae: float
    rmse: float
    r2: float
    training_rows: int


class SegmentPoint(BaseModel):
    customer_id: int
    customer_name: str
    segment: str
    recency_days: int
    frequency: int
    monetary_value: float


class SegmentSummary(BaseModel):
    segment: str
    count: int
    avg_monetary_value: float
    avg_frequency: float
    avg_recency_days: float


class SegmentationResponse(BaseModel):
    status: str
    customers: List[SegmentPoint]
    summary: List[SegmentSummary]
    message: Optional[str] = None


class TrainSegmentationResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    model_name: str
    n_components: int
    covariance_type: str
    silhouette_score: Optional[float] = None
    aic: Optional[float] = None
    bic: Optional[float] = None
    training_rows: int
