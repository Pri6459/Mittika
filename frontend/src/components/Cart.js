import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import API from "../api";
import { useLanguage } from "../utils/LanguageContext";
import { useTranslatedValues } from "../utils/useTranslatedValues";
import "./Cart.css";

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

const CartItem = ({ item, updateQty, removeItem }) => {
  const { t } = useLanguage();
  const { values, error, isTranslating } = useTranslatedValues([item.title || item.name || ""]);
  const title = values[0] || (
    isTranslating ? t.translatingProduct : error ? t.productTranslationUnavailable : t.yourCart
  );

  return (
    <div className="cart-item">
      <img
        src={resolveProductImage(item.image || item.img)}
        alt={title}
        className="item-image"
      />

      <div className="item-details" aria-busy={isTranslating}>
        <h3 className="item-name">{title}</h3>
        {error && <p role="status">{t.translationFailed}</p>}
        <p className="item-price">₹{item.price}</p>

        <div className="quantity-controls">
          <button
            className="quantity-btn"
            onClick={() => updateQty(item.id || item._id, item.quantity - 1)}
          >
            -
          </button>

          <span className="quantity-number">{item.quantity}</span>

          <button
            className="quantity-btn"
            onClick={() => updateQty(item.id || item._id, item.quantity + 1)}
          >
            +
          </button>
        </div>
      </div>

      <button
        className="remove-button"
        onClick={() => removeItem(item.id || item._id)}
      >
        {t.remove}
      </button>
    </div>
  );
};

const Cart = ({ user }) => {
  const { t } = useLanguage();
  const [cartItems, setCartItems] = useState([]);

  // ✅ FETCH
  const fetchCart = async () => {
    try {
      const res = await API.get("/cart");
      setCartItems(res.data.items || []);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    if (user) fetchCart();
  }, [user]);

  // ✅ REMOVE
  const removeItem = async (id) => {
    try {
      await API.delete(`/cart/${id}`);
      fetchCart(); // 🔥 refresh
    } catch (err) {
      console.error(err);
    }
  };

  // ✅ UPDATE QTY
  const updateQty = async (id, qty) => {
    if (qty < 1) return;

    try {
      await API.put(`/cart/${id}`, { quantity: qty });
      fetchCart(); // 🔥 refresh
    } catch (err) {
      console.error(err);
    }
  };

  const total = cartItems.reduce(
    (sum, item) => sum + item.price * (item.quantity || 1),
    0
  );

  if (!user) return <p>{t.pleaseLogin}</p>;

  return (
    <div className="cart-container">
      <h2>{t.yourCart} 🛒</h2>

      {cartItems.length === 0 ? (
        <p>{t.cartEmpty}</p>
      ) : (
        <div className="cart-items">
          {cartItems.map((item) => (
            <CartItem
              key={item.id || item._id}
              item={item}
              updateQty={updateQty}
              removeItem={removeItem}
            />
          ))}

          <div className="cart-total">
            {t.total}: ₹{total}
          </div>
          <Link className="checkout-link" to="/checkout">{t.continueCheckout}</Link>
        </div>
      )}
    </div>
  );
};

export default Cart;