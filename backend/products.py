from fastapi import APIRouter, Depends
from config import get_database
from bson import ObjectId

router = APIRouter(prefix="/products", tags=["Products"])

def fmt_product(p):
    return {
        "id": str(p["_id"]), "title": p["title"], "description": p.get("description",""),
        "price": p["price"], "category": p["category"], "image": p.get("image",""),
        "stock": p.get("stock", 10),
        "artisanName": p.get("artisanName",""), "artisanId": p.get("artisanId","")
    }

@router.get("")
async def get_all_products(db=Depends(get_database)):
    products = await db["products"].find().to_list(100)
    return {"products": [fmt_product(p) for p in products]}

@router.get("/{category}")
async def get_by_category(category: str, db=Depends(get_database)):
    products = await db["products"].find({"category": category}).to_list(100)
    return {"products": [fmt_product(p) for p in products]}