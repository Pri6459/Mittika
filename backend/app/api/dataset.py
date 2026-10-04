import os
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.core.config import settings
from app.db.database import get_db
from app.models.dataset import DatasetRecord
from app.schemas.dataset import DatasetAnalysis, DatasetUploadResponse

router = APIRouter(prefix="/api/dataset", tags=["dataset"])


@router.post("/upload", response_model=DatasetUploadResponse)
async def upload_dataset(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    safe_name = Path(file.filename).name
    file_path = upload_dir / safe_name
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    with open(file_path, "wb") as f:
        f.write(contents)

    try:
        df = pd.read_csv(file_path)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid CSV file: {str(exc)}") from exc

    if df.empty:
        raise HTTPException(status_code=400, detail="Dataset is empty")

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = df.select_dtypes(exclude=["number"]).columns.tolist()
    target_column = "is_fraud" if "is_fraud" in df.columns else None

    summary = {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "missing_values": int(df.isnull().sum().sum()),
        "duplicate_records": int(df.duplicated().sum()),
        "numerical_features": numeric_cols,
        "categorical_features": categorical_cols,
        "fraud_count": int((df[target_column] == 1).sum()) if target_column else 0,
        "legitimate_count": int((df[target_column] == 0).sum()) if target_column else 0,
        "fraud_percentage": round((df[target_column].mean() * 100), 2) if target_column else 0.0,
    }

    db_record = DatasetRecord(
        filename=safe_name,
        rows=int(df.shape[0]),
        columns=int(df.shape[1]),
        target_column=target_column,
        summary=summary,
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)

    return DatasetUploadResponse(
        filename=safe_name,
        rows=int(df.shape[0]),
        columns=int(df.shape[1]),
        target_column=target_column,
        summary=summary,
    )


@router.get("/summary")
def get_dataset_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    latest = db.query(DatasetRecord).order_by(DatasetRecord.id.desc()).first()
    if not latest:
        raise HTTPException(status_code=404, detail="No dataset uploaded yet")

    return {
        "filename": latest.filename,
        "rows": latest.rows,
        "columns": latest.columns,
        "target_column": latest.target_column,
        "summary": latest.summary,
    }
