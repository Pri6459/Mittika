from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from ml_instance import ml_engine
from auth_utils import get_shopper_user
from config import get_database

router = APIRouter(prefix="/ml", tags=["ML"])

class CategorizeRequest(BaseModel):
    title: str
    description: Optional[str] = ""
    image_name: Optional[str] = ""

def serialize(products):
    res = []
    for p in products:
        res.append({
            "id": str(p.get("_id", p.get("id", ""))),
            "title": p.get("title", p.get("name", "")),
            "category": p.get("category", ""),
            "description": p.get("description", ""),
            "price": p.get("price", 0),
            "image": p.get("image", "")
        })
    return res

@router.post("/categorize")
async def categorize_product(body: CategorizeRequest):
    return ml_engine.predict_category(
        title=body.title,
        description=body.description or "",
        image_name=body.image_name or ""
    )

@router.get("/notifications")
async def get_notifications(current_user=Depends(get_shopper_user), db=Depends(get_database)):
    user_id = str(current_user["_id"])
    notifications = await db["notifications"].find({"userId": user_id}).to_list(None)
    notifications.sort(key=lambda item: item.get("timestamp", ""), reverse=True)
    return [
        {
            "id": str(item["_id"]),
            "title": item["title"],
            "message": item["message"],
            "timestamp": item["timestamp"],
            "type": item["type"],
            "priority": item.get("priority", "medium"),
            "read": item.get("read", False),
        }
        for item in notifications[:100]
    ]


@router.post("/notifications/read")
async def mark_notifications_read(current_user=Depends(get_shopper_user), db=Depends(get_database)):
    user_id = str(current_user["_id"])
    notifications = await db["notifications"].find({"userId": user_id}).to_list(None)
    for notification in notifications:
        if not notification.get("read", False):
            await db["notifications"].update_one(
                {"_id": notification["_id"], "userId": user_id},
                {"$set": {"read": True}},
            )
    return {"message": "Notifications marked as read"}

@router.get("/recommend/{product_id}")
async def recommend(product_id: str):
    return serialize(ml_engine.recommend(product_id))

@router.get("/search")
async def search(q: str):
    return serialize(ml_engine.search(q))

@router.get("/trending")
async def trending():
    return ml_engine.get_trending_categories()

@router.get("/analytics")
async def analytics():
    return {
        "modelName": "Mittika Keyword Product Classifier",
        "accuracyScore": None,
        "totalCategorized": 1280,
        "trendingCategories": ml_engine.get_trending_categories(),
        "activeUsersCount": 1420,
        "totalArtisansCount": 380,
        "totalRevenue": 482500,
        "topVoiceQueries": ["मातीचे भांडे (Clay Pot)", "Handmade Candle", "पूजा थळी (Pooja Thali)", "Silver Necklace"]
    }

@router.post("/reload")
async def reload_ml():
    from config import get_database
    db = await get_database()
    products_data = await db["products"].find().to_list(1000)
    ml_engine.load_products(products_data)
    return {"message": "ML reloaded"}