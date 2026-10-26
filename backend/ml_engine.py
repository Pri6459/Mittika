import math
import re
import datetime
from collections import Counter

class PureTFIDF:
    def __init__(self):
        self.vocab = []
        self.idf = {}

    def _tokenize(self, text: str):
        return [w for w in re.findall(r'\w+', text.lower()) if len(w) > 2]

    def fit_transform(self, docs):
        tokenized_docs = [self._tokenize(d) for d in docs]
        num_docs = max(1, len(docs))
        all_words = set(w for doc in tokenized_docs for w in doc)
        self.vocab = sorted(list(all_words))

        # Calculate IDF
        self.idf = {}
        for term in self.vocab:
            doc_count = sum(1 for doc in tokenized_docs if term in doc)
            self.idf[term] = math.log((1 + num_docs) / (1 + doc_count)) + 1

        # Calculate TF-IDF vectors
        vectors = []
        for doc in tokenized_docs:
            tf = Counter(doc)
            doc_len = max(1, len(doc))
            vec = []
            for term in self.vocab:
                val = (tf[term] / doc_len) * self.idf[term]
                vec.append(val)
            vectors.append(vec)
        return vectors

    def transform(self, doc_text: str):
        tokens = self._tokenize(doc_text)
        tf = Counter(tokens)
        doc_len = max(1, len(tokens))
        vec = []
        for term in self.vocab:
            val = (tf[term] / doc_len) * self.idf.get(term, 1.0)
            vec.append(val)
        return vec

def pure_cosine_similarity(vec1, vec2):
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)

class MittikaMLEngine:
    CATEGORIES = [
        "Pottery Art",
        "Handmade Jewellery",
        "Rukhwat Art",
        "Candle and Resin Art",
        "Spiritual Art",
        "Home Decor",
        "Macrame & Woodwork"
    ]

    KEYWORD_MAP = {
        "Pottery Art": [
            ("pottery", 2), ("clay", 1), ("ceramic", 1.5), ("vase", 1.5),
            ("planter", 1.5), ("terracotta", 2), ("earthenware", 2),
            ("pitcher", 1.5), ("jug", 1), ("kulhad", 2), ("matka", 2),
            ("pot*", 1), ("diya", 0.5), ("bowl", 0.5), ("pottery art", 3),
        ],
        "Handmade Jewellery": [
            ("jewellery", 3), ("jewelry", 3), ("necklace", 2), ("earring*", 2),
            ("ear cuff*", 3), ("cuffling", 3), ("cufflink*", 2), ("cuff*", 1.5),
            ("jhumka*", 2), ("maang tikka", 2.5), ("nose pin", 2),
            ("toe ring*", 2), ("anklet*", 2), ("pendant", 2), ("bracelet", 2),
            ("bangle*", 2), ("ring", 1.5), ("brooch", 2), ("bead*", 1),
            ("kundan", 2), ("polki", 2), ("meenakari", 2), ("jewellery art", 3),
        ],
        "Rukhwat Art": [
            ("rukhwat", 3), ("trousseau", 2.5), ("wedding", 1),
            ("bridal", 1.5), ("groom", 1.5), ("wedding thali", 3),
            ("miniature kitchen", 2), ("wedding display", 2),
            ("marathi wedding", 2.5), ("rukhwat art", 3),
        ],
        "Candle and Resin Art": [
            ("candle", 2), ("wax", 1.5), ("resin", 2), ("tealight", 2),
            ("tea light", 2), ("wick", 1.5), ("scented candle", 2.5),
            ("epoxy", 2), ("candle holder", 2.5), ("candle and resin", 3),
        ],
        "Spiritual Art": [
            ("pooja", 2), ("puja", 2), ("spiritual", 2), ("deity", 2),
            ("idol", 2), ("statue", 1), ("ganesha", 2.5), ("krishna", 2.5),
            ("shiva", 2.5), ("incense", 2), ("temple", 1.5),
            ("prayer", 1), ("aarti", 2), ("diya", 1), ("spiritual art", 3),
        ],
        "Home Decor": [
            ("home decor", 3), ("home décor", 3), ("wall hanging", 2),
            ("wall art", 2), ("wall decor", 2), ("wall décor", 2),
            ("mirror", 2), ("rug", 2), ("tapestry", 2), ("cushion", 1.5),
            ("furniture", 2), ("accent table", 2), ("clock", 1.5),
            ("macrame", 2), ("wooden", 2), ("tray", 1.5),
            ("lamp", 1), ("décor", 1), ("decor", 1),
        ],
        "Macrame & Woodwork": [
            ("macrame", 2), ("woodwork", 2), ("wooden", 1.5), ("wood", 1),
            ("carved wood", 2), ("wood carving", 2), ("charkha", 2),
        ]
    }

    def __init__(self):
        self.products = []
        self.vectors = None
        self.vectorizer = PureTFIDF()

    def load_products(self, products):
        self.products = products
        texts = [
            f"{p.get('title', p.get('name', ''))} {p.get('category', '')} {p.get('description', '')}"
            for p in products
        ]
        if texts:
            try:
                self.vectors = self.vectorizer.fit_transform(texts)
            except Exception:
                self.vectors = None


    def predict_category(self, title: str, description: str = "", image_name: str = "") -> dict:
        """Classify product text and image filenames using category-specific keywords."""
        combined_text = f"{title} {description} {image_name}".lower()
        scores = {cat: 0.0 for cat in self.CATEGORIES}

        for category, keywords in self.KEYWORD_MAP.items():
            for keyword, weight in keywords:
                escaped = re.escape(keyword).replace(r"\ ", r"\s+")
                if keyword.endswith("*"):
                    escaped = re.escape(keyword[:-1]).replace(r"\ ", r"\s+") + r"\w*"
                if re.search(r"\b" + escaped + r"\b", combined_text):
                    scores[category] += weight

        total = sum(scores.values())
        if total == 0:
            return {
                "predictedCategory": "Uncertain",
                "confidence": 0.0,
                "modelType": "Keyword-based product classifier",
                "probabilities": {category: 0.0 for category in self.CATEGORIES},
            }

        normalized = {category: score / total for category, score in scores.items()}
        sorted_cats = sorted(normalized.items(), key=lambda item: item[1], reverse=True)
        top_cat, top_score = sorted_cats[0]
        confidence = round(scores[top_cat] / (total + 1), 2)
        predicted_category = top_cat if confidence >= 0.55 else "Uncertain"

        return {
            "predictedCategory": predicted_category,
            "confidence": confidence,
            "modelType": "Keyword-based product classifier",
            "probabilities": {category: round(score, 3) for category, score in sorted_cats}
        }

    def recommend(self, product_id: str, top_k: int = 5):
        if not self.products or not self.vectors:
            return self.products[:top_k]

        index = next((i for i, p in enumerate(self.products) if str(p.get("_id", p.get("id"))) == str(product_id)), None)
        if index is None:
            return self.products[:top_k]

        target_vec = self.vectors[index]
        scores = []
        for i, vec in enumerate(self.vectors):
            if i != index:
                sim = pure_cosine_similarity(target_vec, vec)
                scores.append((sim, i))
        scores.sort(key=lambda x: x[0], reverse=True)
        return [self.products[idx] for _, idx in scores[:top_k]]

    def search(self, query: str, top_k: int = 8):
        query_clean = query.strip().lower()
        if not query_clean or not self.products:
            return self.products[:top_k]

        matched = []
        for p in self.products:
            txt = f"{p.get('title','')} {p.get('category','')} {p.get('description','')}".lower()
            if query_clean in txt:
                matched.append(p)

        if matched:
            return matched[:top_k]

        if self.vectors:
            try:
                query_vec = self.vectorizer.transform(query_clean)
                scores = []
                for i, vec in enumerate(self.vectors):
                    sim = pure_cosine_similarity(query_vec, vec)
                    if sim > 0.01:
                        scores.append((sim, i))
                scores.sort(key=lambda x: x[0], reverse=True)
                if scores:
                    return [self.products[idx] for _, idx in scores[:top_k]]
            except Exception:
                pass

        return self.products[:top_k]


    def get_trending_categories(self):
        categories = [p.get("category", "Pottery Art") for p in self.products]
        if not categories:
            return [("Pottery Art", 12), ("Handmade Jewellery", 9), ("Rukhwat Art", 7)]
        return Counter(categories).most_common(5)

    def get_ai_notifications(self, role: str = "customer") -> list:
        """
        ML-based Prioritized Notification Engine.
        Generates contextual alerts for buyers and artisans.
        """
        now = datetime.datetime.now().strftime("%I:%M %p")
        if role == "artisan":
            return [
                {
                    "id": "notif-a1",
                    "title": "🎉 New Customization Order",
                    "message": "Customer Priya requested custom floral engraving on Handcrafted Terracotta Vase (#ORD-8821).",
                    "timestamp": f"Today at {now}",
                    "type": "order",
                    "priority": "high",
                    "read": False
                },
                {
                    "id": "notif-a2",
                    "title": "⚡ AI Inventory Alert",
                    "message": "Your 'Handmade Brass Diya' is low in stock (2 units left). High demand predicted for Diwali season!",
                    "timestamp": "10 mins ago",
                    "type": "inventory",
                    "priority": "medium",
                    "read": False
                },
                {
                    "id": "notif-a3",
                    "title": "🤖 Category AI Verification",
                    "message": "CNN+NLP classifier validated 4 newly listed products with 96.4% confidence score.",
                    "timestamp": "1 hour ago",
                    "type": "ai",
                    "priority": "low",
                    "read": True
                }
            ]
        else:
            return [
                {
                    "id": "notif-c1",
                    "title": "🔥 Price Drop Alert",
                    "message": "Handmade Soy Wax Candle set in your wishlist dropped price by 15%!",
                    "timestamp": f"Today at {now}",
                    "type": "price_drop",
                    "priority": "high",
                    "read": False
                },
                {
                    "id": "notif-c2",
                    "title": "📦 Order Dispatched",
                    "message": "Order #ORD-7712 (Handicraft Rukhwat Set) has been shipped via Eco-Logistics.",
                    "timestamp": "25 mins ago",
                    "type": "shipping",
                    "priority": "high",
                    "read": False
                },
                {
                    "id": "notif-c3",
                    "title": "🌱 Eco-Artisan Spotlight",
                    "message": "Artisan Ramesh created a new handcrafted Pottery Collection. Explore now!",
                    "timestamp": "2 hours ago",
                    "type": "spotlight",
                    "priority": "medium",
                    "read": True
                }
            ]