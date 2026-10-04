from fastapi import APIRouter, HTTPException, Depends
from config import get_database
from schemas import CartItemIn, UpdateQuantity
from auth_utils import get_shopper_user
import uuid

router = APIRouter(prefix="/cart", tags=["Cart"])


# ✅ FORMAT ITEM
def fmt_item(i):
    return {
        "id": i.get("id"),
        "productId": i.get("productId"),
        "title": i.get("title"),
        "price": i.get("price"),
        "image": i.get("image", ""),
        "quantity": i.get("quantity", 1)
    }


# ✅ GET OR CREATE CART
async def get_cart(uid, db):
    cart = await db["carts"].find_one({"userId": uid})

    if not cart:
        cart = {"userId": uid, "items": []}
        await db["carts"].insert_one(cart)

    return cart


# ✅ GET CART
@router.get("")
async def get_user_cart(current_user=Depends(get_shopper_user), db=Depends(get_database)):
    uid = str(current_user["_id"])
    cart = await get_cart(uid, db)

    return {"items": [fmt_item(i) for i in cart.get("items", [])]}


# ✅ ADD TO CART
@router.post("")
async def add_to_cart(body: CartItemIn,
                      current_user=Depends(get_shopper_user),
                      db=Depends(get_database)):

    uid = str(current_user["_id"])
    cart = await get_cart(uid, db)
    items = cart.get("items", [])

    existing = next((i for i in items if i["productId"] == body.productId), None)

    if existing:
        existing["quantity"] += body.quantity
    else:
        new_item = {
            "id": str(uuid.uuid4()),  # ✅ unique id
            "productId": body.productId,
            "title": body.title,
            "price": body.price,
            "image": body.image,
            "quantity": body.quantity
        }
        items.append(new_item)

    await db["carts"].update_one(
        {"userId": uid},
        {"$set": {"items": items}}
    )

    return {"items": [fmt_item(i) for i in items]}


# ✅ UPDATE QUANTITY
@router.put("/{item_id}")
async def update_quantity(item_id: str,
                          body: UpdateQuantity,
                          current_user=Depends(get_shopper_user),
                          db=Depends(get_database)):

    uid = str(current_user["_id"])
    cart = await get_cart(uid, db)
    items = cart.get("items", [])

    item = next((i for i in items if i["id"] == item_id), None)

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item["quantity"] = body.quantity

    await db["carts"].update_one(
        {"userId": uid},
        {"$set": {"items": items}}
    )

    return {"items": [fmt_item(i) for i in items]}


# ✅ REMOVE ITEM
@router.delete("/{item_id}")
async def remove_item(item_id: str,
                      current_user=Depends(get_shopper_user),
                      db=Depends(get_database)):

    uid = str(current_user["_id"])
    cart = await get_cart(uid, db)
    items = cart.get("items", [])

    new_items = [i for i in items if i["id"] != item_id]

    if len(new_items) == len(items):
        raise HTTPException(status_code=404, detail="Item not found")

    await db["carts"].update_one(
        {"userId": uid},
        {"$set": {"items": new_items}}
    )

    return {"items": [fmt_item(i) for i in new_items]}


# ✅ CLEAR CART
@router.delete("/clear")
async def clear_cart(current_user=Depends(get_shopper_user),
                     db=Depends(get_database)):

    uid = str(current_user["_id"])

    await db["carts"].update_one(
        {"userId": uid},
        {"$set": {"items": []}}
    )

    return {"items": []}