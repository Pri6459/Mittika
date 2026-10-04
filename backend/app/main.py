from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.api.auth import router as auth_router
from app.api.dataset import router as dataset_router
from app.api.ml import router as ml_router
from app.core.config import settings

app = FastAPI(title="Fraud Detection and Risk Analysis System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.MODELS_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.DATA_DIR).mkdir(parents=True, exist_ok=True)

app.include_router(auth_router)
app.include_router(dataset_router)
app.include_router(ml_router)

@app.get("/")
def root():
    return {"message": "Fraud detection API is running", "docs": "/docs"}
