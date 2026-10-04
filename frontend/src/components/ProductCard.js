import React from "react";
import { useTranslatedValues } from "../utils/useTranslatedValues";
import './ProductCard.js'; // Assuming you have a CSS file for styling

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

// Add addToCart and addToWishlist to the props list
const ProductCard = ({
  image,
  title,
  price,
  description,
  addToCart,
  addToWishlist
}) => {
  const { values, error, isTranslating, t } = useTranslatedValues([title, description]);
  const productTitle = values[0] || (
    isTranslating ? t.translatingProduct : error ? t.productTranslationUnavailable : t.unnamedProduct
  );
  const productDescription = values[1] || (
    isTranslating ? t.translatingProduct : error ? t.productTranslationUnavailable : t.handcraftedProduct
  );

  return (
    <div className="product-card">
      <img src={resolveProductImage(image)} alt={productTitle} />
      <div className="product-details" aria-busy={isTranslating}>
        <h3>{productTitle}</h3>
        <p className="product-description">{productDescription}</p>
        {error && <p role="status">{t.translationFailed}</p>}
        <p>{formatPrice(price)}</p>
      </div>
      {(addToCart || addToWishlist) && (
        <div className="product-actions">
          {addToCart && <button className="add-to-cart" onClick={addToCart}>{t.addToCart}</button>}
          {addToWishlist && <button className="add-to-wishlist" onClick={addToWishlist}>{t.wishlist}</button>}
        </div>
      )}
    </div>
  );
};

export default ProductCard;