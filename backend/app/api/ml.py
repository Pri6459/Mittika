from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.database import get_db
from app.ml.training import train_models
from app.ml.predict import predict_batch_transactions, predict_single_transaction
from app.models.model_result import ModelResult
from app.schemas.ml import BatchPredictionRequest, PredictionRequest, TrainingRequest

router = APIRouter(prefix="/api", tags=["ml"])


@router.post("/models/train")
def train_model_endpoint(payload: TrainingRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    dataset_path = "uploads/latest.csv"
    if not dataset_path:
        raise HTTPException(status_code=400, detail="Upload a dataset before training")

    try:
        df = pd.read_csv(dataset_path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail="Dataset file not found. Upload a dataset first.") from exc

    if "is_fraud" not in df.columns:
        raise HTTPException(status_code=400, detail="Supervised training requires an 'is_fraud' target column")

    result_payload = train_models(df, selected_models=payload.models)
    results = result_payload["results"]

    for metric in results:
        db.add(
            ModelResult(
                model_name=metric["model_name"],
                accuracy=metric.get("accuracy"),
                precision=metric.get("precision"),
                recall=metric.get("recall"),
                f1_score=metric.get("f1_score"),
                roc_auc=metric.get("roc_auc"),
                dataset_name="latest.csv",
            )
        )
    db.commit()

    return {
        "message": "Models trained successfully",
        "best_model": result_payload["best_model"],
        "results": results,
    }


@router.get("/models")
def list_models(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    rows = db.query(ModelResult).order_by(ModelResult.trained_at.desc()).all()
    return [{
        "id": row.id,
        "model_name": row.model_name,
        "accuracy": row.accuracy,
        "precision": row.precision,
        "recall": row.recall,
        "f1_score": row.f1_score,
        "roc_auc": row.roc_auc,
        "trained_at": row.trained_at.isoformat() if row.trained_at else None,
    } for row in rows]


@router.post("/predict")
def predict_transaction(payload: PredictionRequest, current_user=Depends(get_current_user)):
    return predict_single_transaction(payload.transaction, model_name=payload.model_name)


@router.post("/predict/batch")
def batch_predict(payload: BatchPredictionRequest, current_user=Depends(get_current_user)):
    predictions = predict_batch_transactions(payload.transactions, model_name=payload.model_name)
    return {"count": len(predictions), "results": predictions}


@router.get("/dashboard/summary")
def dashboard_summary(current_user=Depends(get_current_user)):
    return {
        "total_transactions": 0,
        "fraudulent_transactions": 0,
        "fraud_percentage": 0,
        "total_fraud_amount": 0,
        "high_risk_transactions": 0,
        "best_model": "random_forest",
    }
