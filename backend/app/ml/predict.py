from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import joblib
import numpy as np
import pandas as pd

from app.core.config import settings
from app.ml.feature_engineering import derive_transaction_features


def risk_level_from_score(score: float) -> str:
    if score >= 75:
        return "Critical"
    if score >= 50:
        return "High"
    if score >= 25:
        return "Medium"
    return "Low"


def score_probability(probability: float) -> int:
    return int(max(0, min(100, round(probability * 100))))


def load_model_bundle(model_name: str):
    model_path = Path(settings.MODELS_DIR) / f"{model_name}.pkl"
    preprocessor_path = Path(settings.MODELS_DIR) / "preprocessor.pkl"
    if not model_path.exists() or not preprocessor_path.exists():
        raise FileNotFoundError("Model or preprocessor not found. Train a model first.")

    model = joblib.load(model_path)
    preprocessor = joblib.load(preprocessor_path)
    return model, preprocessor


def predict_single_transaction(transaction: Dict[str, Any], model_name: str = "random_forest") -> Dict[str, Any]:
    model, preprocessor = load_model_bundle(model_name)
    frame = pd.DataFrame([transaction])
    frame = derive_transaction_features(frame)
    feature_frame = frame.copy()

    if "transaction_time" in feature_frame.columns and not pd.api.types.is_datetime64_any_dtype(feature_frame["transaction_time"]):
        try:
            feature_frame["transaction_time"] = pd.to_datetime(feature_frame["transaction_time"], errors="coerce")
        except Exception:
            pass

    transformed = preprocessor.transform(feature_frame)
    if model_name == "isolation_forest":
        anomaly = model.score_samples(transformed)
        normalized = (np.abs(anomaly - np.min(anomaly)) / (np.abs(np.max(anomaly) - np.min(anomaly)) + 1e-8))
        probability = float(np.clip(normalized[0], 0, 1))
        prediction = "FRAUD" if probability >= 0.5 else "LEGITIMATE"
        risk_score = score_probability(probability)
        risk_level = risk_level_from_score(risk_score)
        return {
            "prediction": prediction,
            "fraud_probability": round(probability * 100, 2),
            "risk_score": risk_score,
            "risk_level": risk_level,
            "model_used": model_name,
            "contributing_features": {},
        }

    probability = float(model.predict_proba(transformed)[0][1])
    prediction = "FRAUD" if probability >= 0.5 else "LEGITIMATE"
    risk_score = score_probability(probability)
    risk_level = risk_level_from_score(risk_score)
    return {
        "prediction": prediction,
        "fraud_probability": round(probability * 100, 2),
        "risk_score": risk_score,
        "risk_level": risk_level,
        "model_used": model_name,
        "contributing_features": {},
    }


def predict_batch_transactions(transactions: List[Dict[str, Any]], model_name: str = "random_forest") -> List[Dict[str, Any]]:
    return [predict_single_transaction(tx, model_name=model_name) for tx in transactions]
