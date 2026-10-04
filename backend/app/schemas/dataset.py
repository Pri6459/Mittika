from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class DatasetUploadResponse(BaseModel):
    filename: str
    rows: int
    columns: int
    target_column: Optional[str]
    summary: Dict[str, Any]


class DatasetAnalysis(BaseModel):
    rows: int
    columns: int
    missing_values: int
    duplicate_records: int
    numerical_features: List[str]
    categorical_features: List[str]
    fraud_count: int
    legitimate_count: int
    fraud_percentage: float
