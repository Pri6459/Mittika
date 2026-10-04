from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Float, JSON

from app.db.database import Base


class DatasetRecord(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    rows = Column(Integer, nullable=False)
    columns = Column(Integer, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    target_column = Column(String, nullable=True)
    summary = Column(JSON, nullable=True)
