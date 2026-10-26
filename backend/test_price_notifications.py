import unittest

from price_notifications import notify_shoppers_of_price_change


class FakeCursor:
    def __init__(self, documents):
        self.documents = documents

    async def to_list(self, length):
        return self.documents[:length]


class FakeCollection:
    def __init__(self, documents=None):
        self.documents = documents or []

    def find(self, query):
        return FakeCursor(self.documents)

    async def update_one(self, query, update):
        document = next(
            item for item in self.documents
            if item.get("userId") == query.get("userId")
        )
        document.update(update["$set"])

    async def insert_one(self, document):
        self.documents.append(document)


class FakeDatabase:
    def __init__(self):
        self.collections = {
            "carts": FakeCollection([
                {"userId": "shopper-1", "items": [
                    {"productId": "product-1", "price": 10},
                    {"productId": "other-product", "price": 20},
                ]},
            ]),
            "wishlists": FakeCollection([
                {"userId": "shopper-1", "items": [
                    {"productId": "product-1", "price": 10},
                ]},
                {"userId": "shopper-2", "items": [
                    {"productId": "product-1", "price": 10},
                ]},
            ]),
            "notifications": FakeCollection(),
        }

    def __getitem__(self, name):
        return self.collections[name]


class PriceChangeNotificationTests(unittest.IsolatedAsyncioTestCase):
    async def test_updates_saved_item_prices_and_notifies_each_shopper_once(self):
        db = FakeDatabase()
        product = {"_id": "product-1", "title": "Handmade Bowl"}

        notified_count = await notify_shoppers_of_price_change(product, 10, 12.5, db)

        self.assertEqual(notified_count, 2)
        self.assertEqual(db["carts"].documents[0]["items"][0]["price"], 12.5)
        self.assertEqual(db["carts"].documents[0]["items"][1]["price"], 20)
        self.assertEqual(db["wishlists"].documents[0]["items"][0]["price"], 12.5)
        notifications = db["notifications"].documents
        self.assertEqual({item["userId"] for item in notifications}, {"shopper-1", "shopper-2"})
        self.assertEqual(len(notifications), 2)
        self.assertTrue(all(item["type"] == "price_update" for item in notifications))
        self.assertTrue(all(item["read"] is False for item in notifications))
        self.assertTrue(all("₹10 to ₹12.5" in item["message"] for item in notifications))


if __name__ == "__main__":
    unittest.main()
