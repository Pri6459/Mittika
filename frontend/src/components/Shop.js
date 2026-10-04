import React, { useEffect, useState } from "react";
import API from "../api";
import { categoryForSearch } from "../utils/translations";
import { useLanguage } from "../utils/LanguageContext";
import { useTranslatedValues } from "../utils/useTranslatedValues";

const resolveProductImage = (image) => {
  if (!image || typeof image !== "string") {
    return "https://via.placeholder.com/200";
  }

  const trimmed = image.trim();
  if (!trimmed) {
    return "https://via.placeholder.com/200";
  }

  if (trimmed.startsWith("http://") || trimmed.startsWith("https://")) {
    return trimmed;
  }

  if (trimmed.startsWith("/uploads")) {
    return `http://127.0.0.1:8000${trimmed}`;
  }

  if (trimmed.startsWith("uploads/")) {
    return `http://127.0.0.1:8000/${trimmed}`;
  }

  return trimmed;
};

const formatPrice = (price) => {
  const value = String(price ?? "").trim();
  return value.startsWith("₹") ? value : `₹${value}`;
};

const fallbackProducts = [
  {
    id: "jewellery-1",
    title: "Meenakari Necklace Set",
    category: "jewellery",
    price: "₹3200",
    image: "images/jewellery_ (1).jpg",
    description: "Elegant handcrafted necklace with vibrant meenakari detailing and festive charm."
  },
  {
    id: "jewellery-2",
    title: "Antique Silver Hoop Earrings",
    category: "jewellery",
    price: "₹1800",
    image: "images/jewellery_ (2).jpg",
    description: "Classic silver hoops with antique finish, crafted for everyday elegance."
  },
  {
    id: "spiritual-1",
    title: "Lakshmi-Ganesha Tea Light Holder",
    category: "spiritual",
    price: "₹1100",
    image: "images/spritual_5.jpg",
    description: "A devotional décor piece made for home puja and gifting occasions."
  },
  {
    id: "pottery-1",
    title: "Terracotta Wind Chimes",
    category: "pottery",
    price: "₹950",
    image: "images/pot1.jpg",
    description: "Natural terracotta handmade wind chimes that add earthy rhythm to your space."
  },
  {
    id: "rukhwat-1",
    title: "Hand-decorated Gift Platter",
    category: "rukhwat",
    price: "₹1500",
    image: "images/ruk_ (26).jpg",
    description: "Traditional festive décor platter beautifully handcrafted for festive gifting."
  },
  {
    id: "candle-1",
    title: "Lotus-shaped Wax Candle Set",
    category: "candle",
    price: "₹450",
    image: "images/candle (4).jpg",
    description: "Soft pastel lotus candles that bring warmth, calm and traditional grace."
  },
  {
    id: "home-1",
    title: "Hand-painted Terracotta Pot",
    category: "home",
    price: "₹850",
    image: "images/home (68).jpeg",
    description: "Decorative handcrafted pot with rustic detailing for modern boho interiors."
  }
];

const ShopProductCard = ({
  item,
  user,
  addToCart,
  addToWishlist,
  getCategoryLabel,
  onSimilar
}) => {
  const { t } = useLanguage();
  const title = item.title || item.name || "";
  const description = item.description || "";
  const { values, error, isTranslating } = useTranslatedValues([title, description]);
  const productTitle = values[0] || (
    isTranslating ? t.translatingProduct : error ? t.productTranslationUnavailable : t.unnamedProduct
  );
  const productDescription = values[1] || (
    isTranslating ? t.translatingProduct : error ? t.productTranslationUnavailable : t.handcraftedProduct
  );
  const productId = item._id || item.id;

  return (
    <div key={productId || title} className="product-card">
      <img src={resolveProductImage(item.image || item.img)} alt={productTitle} />
      <div className="product-details" aria-busy={isTranslating}>
        <h3>{productTitle}</h3>
        <p className="product-description">{productDescription}</p>
        {item.category && <p className="product-category">{getCategoryLabel(item.category)}</p>}
        <p>{formatPrice(item.price)}</p>
        {error && <p role="status">{t.translationFailed}</p>}
      </div>

      {["customer", "artisan"].includes(user?.userType) && (
        <div className="product-actions">
          <button className="add-to-cart" onClick={() => addToCart(item)}>{t.addToCart}</button>
          <button className="add-to-wishlist" onClick={() => addToWishlist(item)}>{t.wishlist}</button>
        </div>
      )}
      <button style={{ marginTop: "10px" }} onClick={() => onSimilar(productId)}>
        {t.viewSimilar}
      </button>
    </div>
  );
};

const RecommendedProductCard = ({ item }) => {
  const { t } = useLanguage();
  const { values, error, isTranslating } = useTranslatedValues([
    item.title || item.name || "",
    item.description || ""
  ]);
  const productTitle = values[0] || (
    isTranslating ? t.translatingProduct : error ? t.productTranslationUnavailable : t.recommendedProducts
  );
  const productDescription = values[1] || (
    isTranslating ? t.translatingProduct : error ? t.productTranslationUnavailable : t.handcraftedProduct
  );

  return (
    <div key={item._id || item.id || productTitle} className="product-card">
      <img src={resolveProductImage(item.image || item.img)} alt={productTitle} />
      <div className="product-details" aria-busy={isTranslating}>
        <h3>{productTitle}</h3>
        <p className="product-description">{productDescription}</p>
        <p>{formatPrice(item.price)}</p>
        {error && <p role="status">{t.translationFailed}</p>}
      </div>
    </div>
  );
};

const Shop = ({ addToCart, addToWishlist, user, voiceSearchQuery, clearVoiceSearch }) => {
  const { t } = useLanguage();
  const [products, setProducts] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const safeProducts = Array.isArray(products) ? products : [];
  const safeRecommendations = Array.isArray(recommendations) ? recommendations : [];
  const normalizedQuery = voiceSearchQuery?.trim().toLocaleLowerCase() || "";
  const searchedCategory = categoryForSearch(normalizedQuery);
  const visibleProducts = normalizedQuery
    ? safeProducts.filter((item) => {
        const category = categoryForSearch(item.category || "");
        const searchableText = [item.title, item.name, item.description, item.category]
          .filter(Boolean)
          .join(" ")
          .toLocaleLowerCase();
        if (searchedCategory && category === searchedCategory) return true;
        if (searchedCategory && category) return false;
        return normalizedQuery.split(/\s+/).every((term) => searchableText.includes(term));
      })
    : safeProducts;
  const getCategoryLabel = (category) => {
    const categoryKey = categoryForSearch(category || "");
    const categoryLabels = {
      jewellery: t.navJewellery,
      pottery: t.navPottery,
      spiritual: t.navSpiritual,
      candle: t.navCandle,
      rukhwat: t.navRukhwat,
      home: t.navHomeStyling
    };
    return categoryLabels[categoryKey] || category;
  };

  // ✅ Fetch products from backend
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const res = await API.get("/products");
        const backendProducts = Array.isArray(res.data?.products)
          ? res.data.products
          : Array.isArray(res.data)
          ? res.data
          : [];

        setProducts(backendProducts.length > 0 ? backendProducts : fallbackProducts);
      } catch (err) {
        console.error("Error fetching products:", err);
        setProducts(fallbackProducts);
      }
    };

    fetchProducts();
  }, []);

  // ✅ ML Recommendation
  const getRecommendations = async (id) => {
    try {
      const res = await API.get(`/ml/recommend/${id}`);
      setRecommendations(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      console.error("ML error:", err);
      setRecommendations([]);
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2 style={{ textAlign: "center" }}>{normalizedQuery ? `${t.searchResultsFor} "${voiceSearchQuery}"` : t.shopProducts}</h2>
      {normalizedQuery && <button type="button" onClick={clearVoiceSearch}>{t.clearSearch}</button>}

      {/* ✅ PRODUCTS */}
      <div className="product-grid">
        {visibleProducts.map((item) => (
          <ShopProductCard
            key={item._id || item.id || item.title}
            item={item}
            user={user}
            addToCart={addToCart}
            addToWishlist={addToWishlist}
            getCategoryLabel={getCategoryLabel}
            onSimilar={getRecommendations}
          />
        ))}
      </div>
      {normalizedQuery && visibleProducts.length === 0 && (
        <p role="status" style={{ textAlign: "center" }}>{t.noSearchMatches}</p>
      )}

      {/* 🔥 ML RECOMMENDATIONS */}
      {safeRecommendations.length > 0 && (
        <>
          <h2 style={{ marginTop: "40px", textAlign: "center" }}>
            {t.recommendedProducts} 🤖
          </h2>

          <div className="product-grid">
            {safeRecommendations.map((item) => (
              <RecommendedProductCard
                key={item._id || item.id || item.title}
                item={item}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
};

export default Shop;