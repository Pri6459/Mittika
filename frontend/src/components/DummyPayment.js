import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import API from "../api";
import { useLanguage } from "../utils/LanguageContext";
import { useTranslatedValues } from "../utils/useTranslatedValues";
import "./DummyPayment.css";

const DummyPayment = ({ user }) => {
  const { t } = useLanguage();
  const navigate = useNavigate();
  const [cartItems, setCartItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState("idle");
  const [message, setMessage] = useState("");
  const {
    values: translatedTitles,
    error: translationError,
    isTranslating
  } = useTranslatedValues(cartItems.map((item) => item.title || ""));
  const totalAmount = cartItems.reduce((sum, item) => sum + item.price * (item.quantity || 1), 0);

  useEffect(() => {
    API.get("/cart")
      .then((response) => setCartItems(response.data.items || []))
      .catch((error) => {
        console.error(error);
        setMessage(t.unableToLoadCart);
      })
      .finally(() => setLoading(false));
  }, [t]);

  const handlePayment = async () => {
    if (!cartItems.length) return;
    setMessage("");
    setStatus("processing");
    try {
      await API.post("/payment/process", {
        itemIds: cartItems.map((item) => item.id)
      });
      setMessage("");
      setCartItems([]);
      setStatus("success");
    } catch (error) {
      console.error(error);
      setMessage(error.response?.data?.detail || t.paymentCouldNotComplete);
      setStatus("failed");
    }
  };

  if (!user) return null;

  return (
    <div className="dummy-payment">
      <h2>{t.checkout}</h2>
      <p>{user.name}</p>
      {loading ? <p>{t.loadingCart}</p> : cartItems.length === 0 && status !== "success" ? (
        <p>{t.cartEmpty}</p>
      ) : (
        <>
          <ul className="selected-products" aria-busy={isTranslating}>
            {cartItems.map((item, index) => (
              <li key={item.id}>
                <span>
                  {translatedTitles[index] || (
                    isTranslating ? t.translatingProduct : translationError ? t.productTranslationUnavailable : t.unnamedProduct
                  )} × {item.quantity}
                </span>
                <strong>₹{(item.price * item.quantity).toLocaleString("en-IN")}</strong>
              </li>
            ))}
          </ul>
          {translationError && <p role="status">{t.translationFailed}</p>}
          <p>{t.amountToPay}: ₹{totalAmount.toLocaleString("en-IN")}</p>
        </>
      )}

      {message && <p role="status">{message}</p>}

      {status === "idle" && !loading && cartItems.length > 0 && (
        <>
          <button onClick={handlePayment} className="pay-btn">
            {t.payNow}
          </button>
          <button onClick={() => navigate("/cart")} className="cancel-btn">
            {t.backToCart}
          </button>
        </>
      )}

      {status === "processing" && <p>{t.processingPayment}</p>}

      {status === "success" && (
        <div className="success">
          <h3>{t.paymentSuccessful}</h3>
          <button onClick={() => navigate("/shop")}>{t.continueShopping}</button>
        </div>
      )}

      {status === "failed" && (
        <div className="failed">
          <h3>{t.paymentFailed}</h3>
          <button onClick={handlePayment} className="pay-btn">
            {t.tryAgain}
          </button>
        </div>
      )}
    </div>
  );
};

export default DummyPayment;
