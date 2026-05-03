import os
import json
from typing import Dict
from datetime import date, timedelta
import pandas as pd
import numpy as np
from sklearn.compose import TransformedTargetRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.logging import logger
from app.models.ml_model_run import MLModelRun
from app.services.ml.features import get_daily_sales_features


FORECAST_FEATURE_COLUMNS = [
    "dayofweek",
    "month",
    "day",
    "quarter",
    "year",
    "weekofyear",
    "is_weekend",
    "revenue_lag_1",
    "revenue_lag_7",
    "revenue_lag_14",
    "revenue_rolling_7",
    "revenue_rolling_14",
    "revenue_rolling_30",
    "orders",
    "orders_lag_1",
    "orders_rolling_7",
]


def prepare_daily_sales_series(df: pd.DataFrame) -> pd.DataFrame:
    """Return a continuous daily sales series, filling no-order days with zero."""
    if df.empty:
        return pd.DataFrame(columns=["date", "revenue", "orders"])

    daily = df.copy()
    daily["date"] = pd.to_datetime(daily["date"])
    daily = daily.sort_values("date").set_index("date")
    full_index = pd.date_range(daily.index.min(), daily.index.max(), freq="D")
    daily = daily.reindex(full_index)
    daily.index.name = "date"
    daily["revenue"] = daily["revenue"].fillna(0.0)
    daily["orders"] = daily["orders"].fillna(0).astype(int)
    return daily.reset_index()


def create_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Engineer time-based features from date column."""
    df = df.copy()
    df["dayofweek"] = df["date"].dt.dayofweek
    df["month"] = df["date"].dt.month
    df["day"] = df["date"].dt.day
    df["quarter"] = df["date"].dt.quarter
    df["year"] = df["date"].dt.year
    df["weekofyear"] = df["date"].dt.isocalendar().week.astype(int)
    df["is_weekend"] = df["dayofweek"].isin([5, 6]).astype(int)

    for lag in [1, 7, 14]:
        df[f"revenue_lag_{lag}"] = df["revenue"].shift(lag)

    previous_revenue = df["revenue"].shift(1)
    for window in [7, 14, 30]:
        df[f"revenue_rolling_{window}"] = previous_revenue.rolling(window=window, min_periods=1).mean()

    df["orders_lag_1"] = df["orders"].shift(1)
    df["orders_rolling_7"] = df["orders"].shift(1).rolling(window=7, min_periods=1).mean()
    df = df.dropna(subset=FORECAST_FEATURE_COLUMNS + ["revenue"])
    return df


def train_forecast_model(db: Session) -> Dict:
    """Train a sales forecasting model and save artifact."""
    df = prepare_daily_sales_series(get_daily_sales_features(db))

    if len(df) < 45:
        return {
            "status": "insufficient_data",
            "message": "At least 45 daily sales records are required to train the XGBoost forecasting model.",
        }

    df = create_time_features(df)
    if len(df) < 20:
        return {
            "status": "insufficient_data",
            "message": "Not enough usable lagged sales records are available after feature engineering.",
        }

    try:
        from xgboost import XGBRegressor
    except ImportError:
        logger.error("xgboost is not installed. Run pip install -r requirements.txt.")
        return {
            "status": "dependency_missing",
            "message": "xgboost is not installed. Run pip install -r requirements.txt and restart the backend.",
        }

    X = df[FORECAST_FEATURE_COLUMNS].values
    y = df["revenue"].values

    # Simple train/test split: last 20% for test
    split_idx = int(len(X) * 0.8)
    if split_idx < 10:
        split_idx = len(X) - 5

    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    regressor = XGBRegressor(
        objective="reg:squarederror",
        n_estimators=350,
        max_depth=4,
        learning_rate=0.04,
        subsample=0.9,
        colsample_bytree=0.9,
        reg_lambda=1.0,
        random_state=42,
        n_jobs=1,
        tree_method="hist",
    )
    model = TransformedTargetRegressor(
        regressor=regressor,
        func=np.log1p,
        inverse_func=np.expm1,
    )
    model.fit(X_train, y_train)
    model_name = "XGBoostRegressor"

    y_pred = np.maximum(0.0, model.predict(X_test))
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    # Save artifact
    artifact_path = os.path.join(settings.ARTIFACT_DIR, "forecast_model_xgboost.joblib")
    joblib.dump(model, artifact_path)

    metrics = {
        "model_name": model_name,
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "r2": round(r2, 2),
        "training_rows": len(X_train),
    }

    # Log to DB
    run = MLModelRun(
        model_type="forecasting",
        model_name=model_name,
        metrics_json=json.dumps(metrics),
        artifact_path=artifact_path,
    )
    db.add(run)
    db.commit()

    return metrics


def get_sales_forecast(db: Session, days: int = 30) -> Dict:
    """Generate sales forecast for the next N days."""
    df = prepare_daily_sales_series(get_daily_sales_features(db))
    if len(df) < 45:
        return {
            "status": "insufficient_data",
            "message": "At least 45 daily sales records are required to generate an XGBoost forecast.",
        }

    latest_run = (
        db.query(MLModelRun)
        .filter(MLModelRun.model_type == "forecasting")
        .order_by(MLModelRun.created_at.desc(), MLModelRun.id.desc())
        .first()
    )
    artifact_path = latest_run.artifact_path if latest_run else ""

    if latest_run and latest_run.model_name != "XGBoostRegressor":
        return {
            "status": "no_model",
            "message": "No trained XGBoost forecast model found. Please retrain the forecast model.",
        }

    if not os.path.exists(artifact_path):
        return {
            "status": "no_model",
            "message": "No trained forecast model found. Please train a model first.",
        }

    model = joblib.load(artifact_path)

    feature_df = create_time_features(df)
    if feature_df.empty:
        return {
            "status": "insufficient_data",
            "message": "Not enough usable lagged sales records are available after feature engineering.",
        }

    last_date = df.iloc[-1]["date"]
    history = [float(value) for value in df["revenue"].tolist()]
    orders_history = [int(value) for value in df["orders"].tolist()]
    mean_orders = max(1, int(round(float(feature_df["orders"].mean()))))
    forecast = []

    for i in range(1, days + 1):
        next_date = last_date + timedelta(days=i)
        future_orders = mean_orders

        row = {
            "dayofweek": next_date.dayofweek,
            "month": next_date.month,
            "day": next_date.day,
            "quarter": (next_date.month - 1) // 3 + 1,
            "year": next_date.year,
            "weekofyear": int(next_date.isocalendar().week),
            "is_weekend": int(next_date.dayofweek in [5, 6]),
            "revenue_lag_1": history[-1],
            "revenue_lag_7": history[-7] if len(history) >= 7 else history[0],
            "revenue_lag_14": history[-14] if len(history) >= 14 else history[0],
            "revenue_rolling_7": float(np.mean(history[-7:])),
            "revenue_rolling_14": float(np.mean(history[-14:])),
            "revenue_rolling_30": float(np.mean(history[-30:])),
            "orders": future_orders,
            "orders_lag_1": orders_history[-1] if orders_history else future_orders,
            "orders_rolling_7": float(np.mean(orders_history[-7:])) if orders_history else float(future_orders),
        }

        X = np.array([[row[col] for col in FORECAST_FEATURE_COLUMNS]])
        pred = max(0.0, float(model.predict(X)[0]))

        forecast.append({
            "date": next_date.strftime("%Y-%m-%d"),
            "predicted_revenue": round(pred, 2),
        })
        history.append(pred)
        orders_history.append(future_orders)

    return {
        "status": "success",
        "forecast": forecast,
    }
