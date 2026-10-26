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
  { img: "images/jewellery_ (1).jpg", title: "Meenakari Necklace Set", price: "3200", description: "A statement necklace set with colorful Meenakari-inspired detailing, made to bring a festive touch to special occasions." },
  { img: "images/jewellery_ (2).jpg", title: "Antique Silver Hoop Earrings", price: "1800", description: "Classic hoop earrings with an antique silver look and handcrafted detailing for an easy traditional accent." },
  { img: "images/jewellery_ (3).jpg", title: "Oxidised Silver Tassel Necklace", price: "2500", description: "An oxidised-look necklace finished with playful tassels, pairing traditional character with a striking pop of color." },
  { img: "images/jewellery_ (4).jpg", title: "Tribal Beaded Necklace Set", price: "1950", description: "A coordinated beaded necklace set inspired by bold tribal patterns and heritage craft." },
  { img: "images/jewellery_ (5).jpg", title: "Lotus Beaded Drop Earrings", price: "1200", description: "Lotus-inspired drop earrings accented with beads for a graceful finish to festive and everyday outfits." },
  { img: "images/jewellery_ (6).jpg", title: "Fabric Rose Necklace Set", price: "1500", description: "A decorative necklace set featuring fabric rose motifs for a soft, handcrafted floral look." },
  { img: "images/jewellery_ (7).jpg", title: "Bohemian Cowrie Shell Necklace Set", price: "2100", description: "A bohemian-style set with cowrie shell accents, designed to add an earthy statement to relaxed looks." },
  { img: "images/jewellery_ (8).jpg", title: "Golden Spiral Coin Choker Necklace", price: "2800", description: "A close-fitting choker with golden spiral and coin-inspired accents for a bold traditional silhouette." },
  { img: "images/jewellery_ (9).jpg", title: "Handmade Pearl Necklace", price: "2700", description: "A handcrafted pearl necklace with a timeless, elegant look for celebrations or thoughtful gifting." },
  { img: "images/jewellery_ (10).jpg", title: "Kundan Bridal Earrings", price: "3000", description: "Bridal earrings inspired by classic Kundan work, created to complement festive and wedding attire." },
  { img: "images/jewellery_ (11).jpg", title: "Rajasthani Lac Bangles", price: "1600", description: "Traditional-style Rajasthani lac bangles that bring vibrant color and folk-inspired charm to your look." },
  { img: "images/jewellery_ (12).jpg", title: "Peacock Design Oxidised Necklace", price: "2400", description: "An oxidised-look necklace featuring a peacock-inspired design, celebrating the detail of Indian ornamentation." },
  { img: "images/jewellery_ (13).jpg", title: "Hand-painted Wooden Jhumkas", price: 900, description: "Lightweight wooden jhumkas finished with hand-painted detail for a playful take on a familiar silhouette." },
  { img: "images/jewellery_ (14).jpg", title: "Filigree Silver Pendant", price: "2200", description: "A silver-look pendant with delicate filigree-inspired openwork for an understated handcrafted accent." },
  { img: "images/jewellery_ (15).jpg", title: "Terracotta Necklace with Bell Charms", price: "1100", description: "A terracotta necklace decorated with bell charms, combining earthy character with a gentle festive feel." },
  { img: "images/jewellery_ (16).jpg", title: "Enamel Work Bangle Set", price: "1900", description: "A coordinated bangle set with colorful enamel-inspired decoration to brighten traditional outfits." },
  { img: "images/jewellery_ (17).jpg", title: "Golden Elephant Head Necklace", price: "2600", description: "A distinctive necklace centered on an elephant-head motif, with golden tones inspired by traditional adornment." },
  { img: "images/jewellery_ (18).jpg", title: "Mirror Work Stud Earrings", price: "850", description: "Compact stud earrings with mirror-work-inspired accents that catch the light and add a festive touch." },
  { img: "images/jewellery_ (19).jpg", title: "Temple Jewellery Necklace", price: "3500", description: "A temple-style necklace inspired by traditional Indian motifs, suited to celebrations and cultural occasions." },
  { img: "images/jewellery_ (20).jpg", title: "Oxidised Nose Pin Set", price: "800", description: "A set of nose pins with an oxidised finish, offering a small but distinctive traditional accent." },
  { img: "images/jewellery_ (21).jpg", title: "Brass Tribal Earrings", price: "1300", description: "Brass earrings shaped by tribal-inspired styling, bringing a bold artisanal detail to your ensemble." },
  { img: "images/jewellery_ (22).jpg", title: "Crystal Drop Pendant", price: "1750", description: "A crystal-accented drop pendant with a simple, luminous design for both special occasions and gifting." },
  { img: "images/jewellery_ (23).jpg", title: "Antique Silver Kada", price: "2100", description: "A kada bracelet with an antique silver look, adding a substantial traditional accent to the wrist." },
  { img: "images/jewellery_ (24).jpg", title: "Handwoven Thread Necklace", price: "1200", description: "A necklace built around handwoven thread, with a colorful, relaxed style rooted in craft." },
  { img: "images/jewellery_ (25).jpg", title: "Polki Bridal Set", price: "4800", description: "A bridal jewellery set inspired by Polki design, made to bring a graceful statement to wedding attire." },
  { img: "images/jewellery_ (26).jpg", title: "Handcrafted Wooden Earrings", price: "950", description: "Handcrafted wooden earrings with a natural, lightweight feel and a distinctive artisan finish." },
  { img: "images/jewellery_ (27).jpg", title: "Mirror Beaded Bangles", price: "1450", description: "A set of bangles combining beadwork and mirror-inspired accents for a lively festive look." },
  { img: "images/jewellery_ (28).jpg", title: "Pearl Studded Hair Pin", price: "700", description: "A decorative hair pin accented with pearls, adding a delicate finishing touch to styled hair." },
  { img: "images/jewellery_ (29).jpg", title: "Stone Engraved Toe Rings", price: "900", description: "Toe rings with engraved stone-inspired detail, offering a subtle traditional accent for everyday wear." },
  { img: "images/jewellery_ (30).jpg", title: "Kundan Bridal Maang Tikka", price: "2900", description: "A Kundan-inspired maang tikka designed as a graceful centerpiece for bridal and festive styling." },
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
      description: p.description,
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