from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from config import connect_db, close_db, get_database

import auth, cart, wishlist, products, artisan, payment, translations
import ml_routes

from ml_instance import ml_engine   # ✅ ONLY SOURCE OF TRUTH


# 🔥 Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()

    db = await get_database()
    products_data = await db["products"].find().to_list(1000)

    ml_engine.load_products(products_data)

    print(f"🔥 ML Loaded with {len(products_data)} products")

    yield

    await close_db()


# 🔥 CREATE APP FIRST
app = FastAPI(title="Craftly API", version="1.0.0", lifespan=lifespan)


# 🔥 Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 🔥 Static
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# 🔥 Routes (AFTER app creation)
app.include_router(auth.router)
app.include_router(cart.router)
app.include_router(wishlist.router)
app.include_router(products.router)
app.include_router(artisan.router)
app.include_router(payment.router)
app.include_router(translations.router)
app.include_router(ml_routes.router)   # ✅ FIXED POSITION


# 🔥 Root
@app.get("/")
async def root():
    return {"message": "🧶 Craftly API is running", "docs": "/docs"}