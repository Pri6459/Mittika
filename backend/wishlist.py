from fastapi import APIRouter, HTTPException, Depends
from config import get_database
from schemas import WishlistItemIn
from auth_utils import get_shopper_user
import uuid

router = APIRouter(prefix="/wishlist", tags=["Wishlist"])


# ✅ SAFE FORMAT
def fmt_item(i):
    return {
        "id": i.get("id"),
        "productId": i.get("productId"),
        "title": i.get("title"),
        "price": i.get("price"),
        "image": i.get("image", "")
    }


# ✅ GET OR CREATE WISHLIST
async def get_wishlist(uid, db):
    wl = await db["wishlists"].find_one({"userId": uid})

    if not wl:
        wl = {"userId": uid, "items": []}
        await db["wishlists"].insert_one(wl)

    return wl


# ✅ GET WISHLIST
@router.get("")
async def get_user_wishlist(current_user=Depends(get_shopper_user),
                            db=Depends(get_database)):

    uid = str(current_user["_id"])
    wl = await get_wishlist(uid, db)

    return {"items": [fmt_item(i) for i in wl.get("items", [])]}


# ✅ ADD TO WISHLIST
@router.post("")
async def add_to_wishlist(body: WishlistItemIn,
                          current_user=Depends(get_shopper_user),
                          db=Depends(get_database)):

    uid = str(current_user["_id"])
    wl = await get_wishlist(uid, db)
    items = wl.get("items", [])

    # prevent duplicate
    if any(i["productId"] == body.productId for i in items):
        return {"items": [fmt_item(i) for i in items]}

    new_item = {
        "id": str(uuid.uuid4()),  # ✅ unique id
        "productId": body.productId,
        "title": body.title,
        "price": body.price,
        "image": body.image
    }

    items.append(new_item)

    await db["wishlists"].update_one(
        {"userId": uid},
        {"$set": {"items": items}}
    )

    return {"items": [fmt_item(i) for i in items]}


# ✅ REMOVE FROM WISHLIST
@router.delete("/{item_id}")
async def remove_from_wishlist(item_id: str,
                               current_user=Depends(get_shopper_user),
                               db=Depends(get_database)):

    uid = str(current_user["_id"])
    wl = await get_wishlist(uid, db)
    items = wl.get("items", [])

    new_items = [i for i in items if i["id"] != item_id]

    if len(new_items) == len(items):
        raise HTTPException(status_code=404, detail="Item not found")

    await db["wishlists"].update_one(
        {"userId": uid},
        {"$set": {"items": new_items}}
    )

    return {"items": [fmt_item(i) for i in new_items]}