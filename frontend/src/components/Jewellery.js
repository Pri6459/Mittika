import React, { useState, useEffect } from "react";
import ProductCard from "./ProductCard";
import ArtisanProductListings from "./ArtisanProductListings";
import { useLanguage } from "../utils/LanguageContext";

function Jewellery({ addToCart, addToWishlist }) {
  const { t } = useLanguage();
  const [products, setProducts] = useState([]);

  useEffect(() => {
    const defaultProducts = [
  // Corrected: changed 'image' to 'img' to match other components
  { img: "images/jewellery_ (1).jpg", title: "Meenakari Necklace Set", price: "3200" },
  { img: "images/jewellery_ (2).jpg", title: "Antique Silver Hoop Earrings", price: "1800" },
  { img: "images/jewellery_ (3).jpg", title: "Oxidised Silver Tassel Necklace", price: "2500" },
  { img: "images/jewellery_ (4).jpg", title: "Tribal Beaded Necklace Set", price: "1950" },
  { img: "images/jewellery_ (5).jpg", title: "Lotus Beaded Drop Earrings", price: "1200" },
  { img: "images/jewellery_ (6).jpg", title: "Fabric Rose Necklace Set", price: "1500" },
  { img: "images/jewellery_ (7).jpg", title: "Bohemian Cowrie Shell Necklace Set", price: "2100" },
  { img: "images/jewellery_ (8).jpg", title: "Golden Spiral Coin Choker Necklace", price: "2800" },
  { img: "images/jewellery_ (9).jpg", title: "Handmade Pearl Necklace", price: "2700" },
  { img: "images/jewellery_ (10).jpg", title: "Kundan Bridal Earrings", price: "3000" },
  { img: "images/jewellery_ (11).jpg", title: "Rajasthani Lac Bangles", price: "1600" },
  { img: "images/jewellery_ (12).jpg", title: "Peacock Design Oxidised Necklace", price: "2400" },
  { img: "images/jewellery_ (13).jpg", title: "Hand-painted Wooden Jhumkas", price: 900 },
  { img: "images/jewellery_ (14).jpg", title: "Filigree Silver Pendant", price: "2200" },
  { img: "images/jewellery_ (15).jpg", title: "Terracotta Necklace with Bell Charms", price: "1100" },
  { img: "images/jewellery_ (16).jpg", title: "Enamel Work Bangle Set", price: "1900" },
  { img: "images/jewellery_ (17).jpg", title: "Golden Elephant Head Necklace", price: "2600" },
  { img: "images/jewellery_ (18).jpg", title: "Mirror Work Stud Earrings", price: "850" },
  { img: "images/jewellery_ (19).jpg", title: "Temple Jewellery Necklace", price: "3500" },
  { img: "images/jewellery_ (20).jpg", title: "Oxidised Nose Pin Set", price: "800" },
  { img: "images/jewellery_ (21).jpg", title: "Brass Tribal Earrings", price: "1300" },
  { img: "images/jewellery_ (22).jpg", title: "Crystal Drop Pendant", price: "1750" },
  { img: "images/jewellery_ (23).jpg", title: "Antique Silver Kada", price: "2100" },
  { img: "images/jewellery_ (24).jpg", title: "Handwoven Thread Necklace", price: "1200" },
  { img: "images/jewellery_ (25).jpg", title: "Polki Bridal Set", price: "4800" },
  { img: "images/jewellery_ (26).jpg", title: "Handcrafted Wooden Earrings", price: "950" },
  { img: "images/jewellery_ (27).jpg", title: "Mirror Beaded Bangles", price: "1450" },
  { img: "images/jewellery_ (28).jpg", title: "Pearl Studded Hair Pin", price: "700" },
  { img: "images/jewellery_ (29).jpg", title: "Stone Engraved Toe Rings", price: "900" },
  { img: "images/jewellery_ (30).jpg", title: "Kundan Bridal Maang Tikka", price: "2900" },
];

    let artisanProducts = [];
    try {
      const savedProducts = JSON.parse(localStorage.getItem("mittika_products") || "[]");
      artisanProducts = Array.isArray(savedProducts)
        ? savedProducts.filter(
            (p) => p && typeof p.category === "string" && (p.category.toLowerCase() === "jewelry" || p.category.toLowerCase() === "jewellery")
          )
        : [];
    } catch {
      artisanProducts = [];
    }

    const formattedArtisanProducts = artisanProducts.map((p) => ({
      img: p.image,
      title: p.name,
      price: `₹${p.price}`,
      id: p.id
    }));

    setProducts([...defaultProducts, ...formattedArtisanProducts]);
  }, []); // run once on mount

  return (
    <div>
      <div className="page-header">
        <h1>{t.jewelleryCollection}</h1>
      </div>

      <div className="product-grid">
        {products.map((product, index) => (
          <ProductCard
            key={product.id || index}
            image={product.img}
            title={product.title}
            price={product.price}
            description={product.description}
            addToCart={() =>
              addToCart({
                id: product.id || product.title,
                title: product.title,
                price: product.price,
                image: product.img
              })
            }
            addToWishlist={() =>
              addToWishlist({
                id: product.id || product.title,
                title: product.title,
                price: product.price,
                image: product.img
              })
            }
          />
        ))}
        <ArtisanProductListings category="jewellery" addToCart={addToCart} addToWishlist={addToWishlist} />
      </div>
    </div>
  );
}

export default Jewellery;