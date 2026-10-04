import React, { useEffect, useState } from "react";
import API from "../api";
import { useLanguage } from "../utils/LanguageContext";
import { useTranslatedValues } from "../utils/useTranslatedValues";
import "./Wishlist.css";

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

const WishlistItem = ({ item, moveToCart, removeItem }) => {
  const { t } = useLanguage();
  const { values, error, isTranslating } = useTranslatedValues([item.title || item.name || ""]);
  const title = values[0] || (
    isTranslating ? t.translatingProduct : error ? t.productTranslationUnavailable : t.wishlist
  );

  return (
    <div className="wishlist-item">
      <img
        src={resolveProductImage(item.image || item.img)}
        alt={title}
        className="item-image"
      />

      <div className="item-details" aria-busy={isTranslating}>
        <h3 className="item-name">{title}</h3>
        {error && <p role="status">{t.translationFailed}</p>}
        <p className="item-price">₹{item.price}</p>
      </div>

      <div className="item-actions">
        <button className="add-to-cart-button" onClick={() => moveToCart(item)}>
          {t.addToCart}
        </button>
        <button
          className="remove-button"
          onClick={() => removeItem(item.id || item._id)}
        >
          {t.remove}
        </button>
      </div>
    </div>
  );
};

const Wishlist = ({ user, addToCart }) => {
  const { t } = useLanguage();
  const [items, setItems] = useState([]);

  // ✅ FETCH
  const fetchWishlist = async () => {
    try {
      const res = await API.get("/wishlist");
      setItems(res.data.items || []);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    if (user) fetchWishlist();
  }, [user]);

  // ✅ REMOVE
  const removeItem = async (id) => {
    try {
      await API.delete(`/wishlist/${id}`);
      fetchWishlist(); // 🔥 ALWAYS REFRESH
    } catch (err) {
      console.error(err);
    }
  };

  // ✅ MOVE TO CART
  const moveToCart = async (item) => {
    try {
      const added = await addToCart(item);
      if (!added) return;
      await API.delete(`/wishlist/${item.id || item._id}`);
      fetchWishlist();
    } catch (err) {
      console.error(err);
    }
  };

  if (!user) return <p>{t.pleaseLogin}</p>;

  return (
    <div className="wishlist-container">
      <h2>{t.wishlist} ❤️</h2>

      {items.length === 0 ? (
        <p>{t.noWishlistItems}</p>
      ) : (
        <div className="wishlist-items"> {/* 🔥 IMPORTANT */}
          {items.map((item) => (
            <WishlistItem
              key={item.id || item._id}
              item={item}
              moveToCart={moveToCart}
              removeItem={removeItem}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default Wishlist;