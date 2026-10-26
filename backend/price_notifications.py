from datetime import datetime, timezone


async def notify_shoppers_of_price_change(product, previous_price, new_price, db):
    product_id = str(product["_id"])
    shoppers = {}

    for collection_name in ("carts", "wishlists"):
        documents = await db[collection_name].find({}).to_list(None)
        for document in documents:
            items = document.get("items", [])
            changed = False
            for item in items:
                if str(item.get("productId")) == product_id:
                    item["price"] = new_price
                    changed = True
            if changed:
                user_id = str(document["userId"])
                shoppers[user_id] = True
                await db[collection_name].update_one(
                    {"userId": document["userId"]},
                    {"$set": {"items": items}},
                )

    timestamp = datetime.now(timezone.utc).isoformat()
    message = (
        f"The price of {product['title']} changed from "
        f"₹{previous_price:g} to ₹{new_price:g}."
    )
    for user_id in shoppers:
        await db["notifications"].insert_one({
            "userId": user_id,
            "title": "Product price updated",
            "message": message,
            "timestamp": timestamp,
            "type": "price_update",
            "priority": "high",
            "read": False,
            "productId": product_id,
        })
    return len(shoppers)
