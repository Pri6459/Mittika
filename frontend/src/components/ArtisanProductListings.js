import React, { useEffect, useState } from "react";
import API from "../api";
import ProductCard from "./ProductCard";

const ArtisanProductListings = ({ category, addToCart, addToWishlist }) => {
  const [products, setProducts] = useState([]);
  useEffect(() => {
    let active = true;
    API.get(`/products/${encodeURIComponent(category)}`)
      .then((response) => {
        if (active) setProducts(Array.isArray(response.data?.products) ? response.data.products : []);
      })
      .catch((error) => console.error("Could not load artisan products:", error));

    return () => {
      active = false;
    };
  }, [category]);

  if (products.length === 0) return null;

  return products.map((product) => (
          <ProductCard
            key={product.id}
            image={product.image}
            title={product.title}
            price={product.price}
            description={product.description}
            addToCart={addToCart ? () => addToCart(product) : undefined}
            addToWishlist={addToWishlist ? () => addToWishlist(product) : undefined}
          />
        ));
};

export default ArtisanProductListings;
