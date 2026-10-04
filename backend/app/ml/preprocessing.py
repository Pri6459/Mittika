from __future__ import annotations

import joblib
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from app.core.config import settings


class FraudPreprocessor:
    """Reusable pipeline for tabular fraud detection preprocessing."""

    def __init__(self, target_column: str | None = None):
        self.target_column = target_column
        self.numeric_features: List[str] = []
        self.categorical_features: List[str] = []
        self.datetime_features: List[str] = []
        self.preprocessor: ColumnTransformer | None = None
        self.feature_columns: List[str] = []

    def detect_feature_types(self, df: pd.DataFrame) -> None:
        candidate_columns = [col for col in df.columns if col != self.target_column]

        self.numeric_features = [
            col for col in candidate_columns if pd.api.types.is_numeric_dtype(df[col])
        ]
        self.categorical_features = [
            col for col in candidate_columns if col not in self.numeric_features and df[col].dtype == "object"
        ]
        self.datetime_features = [
            col for col in candidate_columns if "date" in col.lower() or "time" in col.lower()
        ]

        for col in self.datetime_features:
            if col not in self.numeric_features and col not in self.categorical_features:
                self.categorical_features.append(col)

    def build_preprocessor(self, df: pd.DataFrame) -> None:
        self.detect_feature_types(df)

        transform_steps = []
        if self.numeric_features:
            numeric_transformer = Pipeline(
                steps=[
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                ]
            )
            transform_steps.append(
                ("num", numeric_transformer, self.numeric_features)
            )

        if self.categorical_features:
            categorical_transformer = Pipeline(
                steps=[
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    ("onehot", OneHotEncoder(handle_unknown="ignore")),
                ]
            )
            transform_steps.append(
                ("cat", categorical_transformer, self.categorical_features)
            )

        self.preprocessor = ColumnTransformer(transformers=transform_steps, remainder="drop")
        self.feature_columns = [
            col for col in df.columns if col != self.target_column
        ]

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.preprocessor is None:
            self.build_preprocessor(df)

        X = df[self.feature_columns].copy()
        transformed = self.preprocessor.fit_transform(X)
        return pd.DataFrame(transformed)

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.preprocessor is None:
            raise ValueError("Preprocessor has not been fit yet")
        X = df[self.feature_columns].copy()
        transformed = self.preprocessor.transform(X)
        return pd.DataFrame(transformed)

    def save(self, path: str | Path | None = None) -> str:
        if path is None:
            path = Path(settings.MODELS_DIR) / "preprocessor.pkl"
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, str(path))
        return str(path)

    @classmethod
    def load(cls, path: str | Path) -> "FraudPreprocessor":
        return joblib.load(path)


def prepare_dataset_for_training(df: pd.DataFrame, target_column: str | None = "is_fraud") -> Tuple[pd.DataFrame, pd.Series]:
    if df.empty:
        raise ValueError("Dataset is empty")

    if target_column and target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' not found. Supervised training requires a target label.")

    working_df = df.copy()
    working_df = working_df.drop_duplicates()
    working_df = working_df.reset_index(drop=True)

    if target_column:
        y = working_df[target_column].astype(int)
        X = working_df.drop(columns=[target_column])
        return X, y

    return working_df, pd.Series([0] * len(working_df), index=working_df.index)
