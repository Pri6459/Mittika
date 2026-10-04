from fastapi import APIRouter, Depends, HTTPException
from schemas import PaymentIn, PaymentOut
from auth_utils import get_shopper_user
from config import get_database
import asyncio

router = APIRouter(prefix="/payment", tags=["Payment"])

@router.post("/process", response_model=PaymentOut)
async def process_payment(
    body: PaymentIn,
    current_user=Depends(get_shopper_user),
    db=Depends(get_database),
):
    cart = await db["carts"].find_one({"userId": str(current_user["_id"])})
    cart_items = cart.get("items", []) if cart else []
    requested_ids = set(body.itemIds)
    selected_items = [item for item in cart_items if item.get("id") in requested_ids]

    if not requested_ids or len(requested_ids) != len(body.itemIds) or len(selected_items) != len(requested_ids):
        raise HTTPException(400, "Selected items were not found in your cart")

    total_amount = sum(float(item["price"]) * int(item.get("quantity", 1)) for item in selected_items)
    await asyncio.sleep(0.5)
    remaining_items = [item for item in cart_items if item.get("id") not in requested_ids]
    await db["carts"].update_one(
        {"userId": str(current_user["_id"])},
        {"$set": {"items": remaining_items}},
    )
    return PaymentOut(success=True, message=f"Payment of ₹{total_amount:.2f} processed successfully!")