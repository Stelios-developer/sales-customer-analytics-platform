import os
import json
from typing import List, Dict, Optional
import pandas as pd
import numpy as np
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import joblib
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.logging import logger
from app.models.customer import Customer
from app.models.ml_model_run import MLModelRun
from app.services.ml.features import get_customer_rfm_features


def get_segment_labels(cluster_centers: np.ndarray, feature_names: List[str]) -> Dict[int, str]:
    """
    Assign human-readable labels to clusters based on center values.
    Higher monetary + frequency + lower recency = High Value.
    """
    labels = {}
    # Normalize centers for ranking
    norms = StandardScaler().fit_transform(cluster_centers)
    # Score: negative recency (lower is better) + frequency + monetary
    scores = []
    for i, center in enumerate(norms):
        score = 0
        for j, name in enumerate(feature_names):
            if name == "recency_days":
                score += -center[j]  # lower recency is better
            else:
                score += center[j]
        scores.append((i, score))

    scores.sort(key=lambda x: x[1], reverse=True)
    label_names = [
        "High Value Customers",
        "Loyal Customers",
        "At Risk Customers",
        "Low Activity Customers",
    ]
    for idx, (cluster_idx, _) in enumerate(scores):
        labels[cluster_idx] = label_names[min(idx, len(label_names) - 1)]
    return labels


def train_segmentation_model(db: Session, n_components: int = 4) -> Dict:
    """Train a Gaussian Mixture customer segmentation model."""
    df = get_customer_rfm_features(db)

    if len(df) < n_components * 2:
        return {
            "status": "insufficient_data",
            "message": f"At least {n_components * 2} customers with orders are required for segmentation.",
        }

    feature_cols = ["recency_days", "frequency", "monetary_value", "average_order_value"]
    X = df[feature_cols].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = GaussianMixture(
        n_components=n_components,
        covariance_type="full",
        random_state=42,
        n_init=10,
        reg_covar=1e-6,
    )
    labels = model.fit_predict(X_scaled)

    try:
        sil_score = silhouette_score(X_scaled, labels) if len(set(labels)) > 1 else None
    except Exception:
        sil_score = None

    # Assign readable labels
    cluster_labels = get_segment_labels(model.means_, feature_cols)
    readable_labels = [cluster_labels[int(label)] for label in labels]

    # Save artifacts
    artifact_base = os.path.join(settings.ARTIFACT_DIR, "segmentation")
    os.makedirs(artifact_base, exist_ok=True)
    joblib.dump(model, os.path.join(artifact_base, "gmm.joblib"))
    joblib.dump(scaler, os.path.join(artifact_base, "scaler.joblib"))
    joblib.dump(cluster_labels, os.path.join(artifact_base, "labels.joblib"))

    metrics = {
        "model_name": "GaussianMixture",
        "n_components": n_components,
        "covariance_type": "full",
        "silhouette_score": round(sil_score, 3) if sil_score is not None else None,
        "aic": round(float(model.aic(X_scaled)), 2),
        "bic": round(float(model.bic(X_scaled)), 2),
        "training_rows": len(df),
    }

    run = MLModelRun(
        model_type="segmentation",
        model_name="GaussianMixture",
        metrics_json=json.dumps(metrics),
        artifact_path=artifact_base,
    )
    db.add(run)
    for customer_id, segment in zip(df["customer_id"].tolist(), readable_labels):
        customer = db.query(Customer).filter(Customer.id == int(customer_id)).first()
        if customer:
            customer.segment = segment
    db.commit()

    return metrics


def get_customer_segments(db: Session) -> Dict:
    """Generate customer segments using the latest trained model."""
    df = get_customer_rfm_features(db)
    if df.empty:
        return {
            "status": "insufficient_data",
            "message": "No customer order data available for segmentation.",
        }

    artifact_base = os.path.join(settings.ARTIFACT_DIR, "segmentation")
    model_path = os.path.join(artifact_base, "gmm.joblib")
    scaler_path = os.path.join(artifact_base, "scaler.joblib")
    labels_path = os.path.join(artifact_base, "labels.joblib")

    if not os.path.exists(model_path):
        return {
            "status": "no_model",
            "message": "No trained segmentation model found. Please train a model first.",
        }

    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    cluster_labels = joblib.load(labels_path)

    feature_cols = ["recency_days", "frequency", "monetary_value", "average_order_value"]
    X = df[feature_cols].values
    X_scaled = scaler.transform(X)
    predictions = model.predict(X_scaled)

    customers = []
    for i, row in df.iterrows():
        label = cluster_labels.get(int(predictions[i]), "Unknown")
        customers.append({
            "customer_id": int(row["customer_id"]),
            "customer_name": row["customer_name"],
            "segment": label,
            "recency_days": int(row["recency_days"]),
            "frequency": int(row["frequency"]),
            "monetary_value": round(float(row["monetary_value"]), 2),
        })

    # Summary stats
    summary = {}
    for c in customers:
        seg = c["segment"]
        if seg not in summary:
            summary[seg] = []
        summary[seg].append(c)

    summary_list = []
    for seg, members in summary.items():
        summary_list.append({
            "segment": seg,
            "count": len(members),
            "avg_monetary_value": round(np.mean([m["monetary_value"] for m in members]), 2),
            "avg_frequency": round(np.mean([m["frequency"] for m in members]), 2),
            "avg_recency_days": round(np.mean([m["recency_days"] for m in members]), 2),
        })

    return {
        "status": "success",
        "customers": customers,
        "summary": summary_list,
    }
