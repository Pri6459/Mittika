from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TrainingRequest(BaseModel):
    models: List[str] = Field(default_factory=lambda: ["logistic_regression", "random_forest", "xgboost", "isolation_forest"])


class PredictionRequest(BaseModel):
    model_name: str = "random_forest"
    transaction: Dict[str, Any]


class BatchPredictionRequest(BaseModel):
    model_name: str = "random_forest"
    transactions: List[Dict[str, Any]]


class ModelEvaluation(BaseModel):
    model_name: str
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    roc_auc: Optional[float] = None
    confusion_matrix: List[List[int]]
    true_positive: int
    true_negative: int
    false_positive: int
    false_negative: int
    selected_metric: str


class FraudPrediction(BaseModel):
    prediction: str
    fraud_probability: float
    risk_score: int
    risk_level: str
    model_used: str
    contributing_features: Dict[str, float]
