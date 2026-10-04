from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from config import get_database
from schemas import NoteIn
from auth_utils import get_artisan_user
from bson import ObjectId
import aiofiles, os, uuid

router = APIRouter(prefix="/artisan", tags=["Artisan"])
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def fmt_product(p):
    return {
        "id": str(p["_id"]), "title": p["title"], "description": p.get("description",""),
        "price": p["price"], "category": p["category"], "image": p.get("image",""),
        "stock": p.get("stock", 10), "artisanId": p.get("artisanId","")
    }

@router.get("/products")
async def get_artisan_products(current_user=Depends(get_artisan_user), db=Depends(get_database)):
    uid = str(current_user["_id"])
    products = await db["products"].find({"artisanId": uid}).to_list(100)
    return {"products": [fmt_product(p) for p in products]}

@router.post("/products")
async def add_product(
    title: str = Form(...), description: str = Form(""),
    price: float = Form(...), category: str = Form(...), stock: int = Form(10),
    image: UploadFile = File(None),
    current_user=Depends(get_artisan_user), db=Depends(get_database)
):
    image_url = ""
    if image:
        ext = image.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        path = os.path.join(UPLOAD_DIR, filename)
        async with aiofiles.open(path, "wb") as f:
            await f.write(await image.read())
        image_url = f"/uploads/{filename}"

    doc = {
        "title": title, "description": description, "price": price,
        "category": category, "stock": stock, "image": image_url,
        "artisanId": str(current_user["_id"]), "artisanName": current_user["name"]
    }
    result = await db["products"].insert_one(doc)
    doc["_id"] = result.inserted_id
    return {"product": fmt_product(doc)}

@router.delete("/products/{product_id}")
async def delete_product(product_id: str, current_user=Depends(get_artisan_user), db=Depends(get_database)):
    result = await db["products"].delete_one({"_id": ObjectId(product_id), "artisanId": str(current_user["_id"])})
    if result.deleted_count == 0:
        raise HTTPException(404, "Product not found")
    return {"message": "Product deleted"}

@router.get("/notes")
async def get_notes(current_user=Depends(get_artisan_user), db=Depends(get_database)):
    doc = await db["artisan_notes"].find_one({"userId": str(current_user["_id"])})
    return {"note": doc["note"] if doc else ""}

@router.post("/notes")
async def save_notes(body: NoteIn, current_user=Depends(get_artisan_user), db=Depends(get_database)):
    uid = str(current_user["_id"])
    await db["artisan_notes"].update_one({"userId": uid}, {"$set": {"note": body.note}}, upsert=True)
    return {"note": body.note}

@router.delete("/notes")
async def clear_notes(current_user=Depends(get_artisan_user), db=Depends(get_database)):
    await db["artisan_notes"].update_one({"userId": str(current_user["_id"])}, {"$set": {"note": ""}})
    return {"message": "Notes cleared"}