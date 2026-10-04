from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

from app.core.config import settings
from app.ml.feature_engineering import derive_transaction_features
from app.ml.preprocessing import FraudPreprocessor, prepare_dataset_for_training


MODEL_CONFIG = {
    "logistic_regression": LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42),
    "random_forest": RandomForestClassifier(n_estimators=200, random_state=42, class_weight="balanced"),
    "xgboost": XGBClassifier(
        objective="binary:logistic",
        n_estimators=200,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=42,
        eval_metric="logloss",
    ),
}


def split_data(X: pd.DataFrame, y: pd.Series, test_size: float = 0.2):
    return train_test_split(X, y, test_size=test_size, random_state=42, stratify=y)


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    working = df.copy()
    working = working.drop_duplicates().reset_index(drop=True)
    working = derive_transaction_features(working)

    for column in list(working.columns):
        if pd.api.types.is_datetime64_any_dtype(working[column]):
            working[column] = working[column].astype(str)

    return working


def train_models(df: pd.DataFrame, selected_models: List[str] | None = None) -> Dict[str, Any]:
    selected = selected_models or ["logistic_regression", "random_forest", "xgboost", "isolation_forest"]
    working = prepare_features(df)

    if "is_fraud" not in working.columns:
        raise ValueError("Dataset does not contain the required target column 'is_fraud'.")

    X, y = prepare_dataset_for_training(working, target_column="is_fraud")
    X_train, X_test, y_train, y_test = split_data(X, y)

    preprocessor = FraudPreprocessor(target_column=None)
    X_train_processed = preprocessor.fit_transform(X_train)
    X_test_processed = preprocessor.transform(X_test)

    results = []
    model_artifacts = {}

    for model_name in selected:
        if model_name not in MODEL_CONFIG and model_name != "isolation_forest":
            continue

        if model_name == "isolation_forest":
            iso = IsolationForest(contamination=0.05, random_state=42)
            iso.fit(X_train_processed)
            preds = (iso.predict(X_test_processed) == -1).astype(int)
            prob = np.clip((-iso.score_samples(X_test_processed) + np.max(-iso.score_samples(X_test_processed))) / (np.max(-iso.score_samples(X_test_processed)) - np.min(-iso.score_samples(X_test_processed)) + 1e-8), 0, 1)
            # Convert anomaly score to fraud probability-like risk measure.
            model_metrics = {
                "model_name": model_name,
                "accuracy": accuracy_score(y_test, preds),
                "precision": precision_score(y_test, preds, zero_division=0),
                "recall": recall_score(y_test, preds, zero_division=0),
                "f1_score": f1_score(y_test, preds, zero_division=0),
                "roc_auc": roc_auc_score(y_test, prob),
                "confusion_matrix": confusion_matrix(y_test, preds).tolist(),
                "true_positive": int(confusion_matrix(y_test, preds)[1, 1]),
                "true_negative": int(confusion_matrix(y_test, preds)[0, 0]),
                "false_positive": int(confusion_matrix(y_test, preds)[0, 1]),
                "false_negative": int(confusion_matrix(y_test, preds)[1, 0]),
                "selected_metric": "f1_score",
                "probabilities": prob,
            }
        else:
            model = MODEL_CONFIG[model_name]
            model.fit(X_train_processed, y_train)
            probs = model.predict_proba(X_test_processed)[:, 1]
            preds = (probs >= 0.5).astype(int)
            model_metrics = {
                "model_name": model_name,
                "accuracy": accuracy_score(y_test, preds),
                "precision": precision_score(y_test, preds, zero_division=0),
                "recall": recall_score(y_test, preds, zero_division=0),
                "f1_score": f1_score(y_test, preds, zero_division=0),
                "roc_auc": roc_auc_score(y_test, probs),
                "confusion_matrix": confusion_matrix(y_test, preds).tolist(),
                "true_positive": int(confusion_matrix(y_test, preds)[1, 1]),
                "true_negative": int(confusion_matrix(y_test, preds)[0, 0]),
                "false_positive": int(confusion_matrix(y_test, preds)[0, 1]),
                "false_negative": int(confusion_matrix(y_test, preds)[1, 0]),
                "selected_metric": "f1_score",
                "probabilities": probs,
            }

        model_artifacts[model_name] = model_metrics
        results.append(model_metrics)

    best_model = max(results, key=lambda r: r["f1_score"] if r["f1_score"] is not None else 0)
    save_dir = Path(settings.MODELS_DIR)
    save_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "results": results,
        "best_model": best_model["model_name"],
        "preprocessor": preprocessor,
        "feature_columns": list(X.columns),
        "y_test": y_test,
        "X_test": X_test,
        "models": model_artifacts,
    }

    for model_name, metrics in model_artifacts.items():
        if model_name == "isolation_forest":
            model = IsolationForest(contamination=0.05, random_state=42)
            model.fit(preprocessor.transform(X_train))
            joblib.dump(model, save_dir / f"{model_name}.pkl")
        else:
            model = MODEL_CONFIG[model_name]
            model.fit(preprocessor.transform(X_train), y_train)
            joblib.dump(model, save_dir / f"{model_name}.pkl")

    joblib.dump(preprocessor, save_dir / "preprocessor.pkl")
    joblib.dump(payload, save_dir / "training_payload.pkl")

    return payload
