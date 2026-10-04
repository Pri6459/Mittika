import React from "react";
import ProductCard from "./ProductCard"; // Import the ProductCard 
import ArtisanProductListings from "./ArtisanProductListings";
import { useLanguage } from "../utils/LanguageContext";

// The component now receives the 'addToCart' function as a prop
function Rukhwat({ addToCart, addToWishlist }) {
  const { t } = useLanguage();
  const products = [
    { img: "images/ruk_ (26).jpg", title: "Hand-decorated Gift Platter", price: "1,500" },
    { img: "images/ruk_ (25).jpg", title: "Hand-painted Miniature Kitchen Set", price: "1,100" },
    { img: "images/ruk_ (24).jpg", title: "Decorative Pistachio Shell Birdhouses (Set of 4)", price: "2,400" },
    { img: "images/ruk_ (23).jpg", title: "Handcrafted Wooden & Fabric Trays (Set of 5)", price: "2,800" },
    { img: "images/ruk_ (22).jpg", title: "Miniature Musical Instrument Set - Type 2", price: "2,000" },
    { img: "images/ruk_ (21).jpg", title: "Miniature Musical Instrument Set - Type 1", price: "2,200" },
    { img: "images/ruk_ (20).jpg", title: "Hand-painted Marathi Rukhwat Plate", price: "1,800" },
    { img: "images/ruk_ (19).jpg", title: "Hand-Painted Wedding Thali", price: "2,500" },
    { img: "images/ruk_ (18).jpg", title: "Decorative Popsicle Stick House", price: "1,100" },
    { img: "images/ruk_ (17).jpg", title: "Bridal & Groom Decorative Cones", price: "1,500" },
    { img: "images/ruk_ (16).jpg", title: "Miniature Silk Gift Bags (Set of 4)", price: "850" },
    { img: "images/ruk_ (15).jpg", title: "Miniature Paper Dolls in Traditional Attire", price: "1,200" },
    { img: "images/ruk_ (14).jpg", title: "Miniature Wedding Ceremony Thali", price: "950" },
    { img: "images/ruk_ (13).jpg", title: "Decorative Winnowing Basket with Wheat", price: "1,600" },
    { img: "images/ruk_ (12).jpg", title: "Large Decorative Rukhwat Basket", price: "3,000" },
    { img: "images/ruk_ (11).jpg", title: "Miniature Tulsi Vivah Set", price: "750" },
    { img: "images/ruk_ (10).jpg", title: "Hand-painted Marathi Rukhwat Plate", price: "1,800" },
    { img: "images/ruk_ (9).jpg", title: "Hand-Painted Wedding Thali", price: "2,500" },
    { img: "images/ruk_ (8).jpg", title: "Decorative Popsicle Stick House", price: "1,100" },
    { img: "images/ruk_ (7).jpg", title: "Bridal & Groom Decorative Cones", price: "1,500" },
    { img: "images/ruk_ (6).jpg", title: "Miniature Silk Gift Bags (Set of 4)", price: "850" },
    { img: "images/ruk_ (5).jpg", title: "Miniature Paper Dolls in Traditional Attire", price: "1,200" },
    { img: "images/ruk_ (4).jpg", title: "Miniature Wedding Ceremony Thali", price: "950" },
    { img: "images/ruk_ (3).jpg", title: "Decorative Winnowing Basket with Wheat", price: "1,600" },
    { img: "images/ruk_ (2).jpg", title: "Large Decorative Rukhwat Basket", price: "3,000" },
    { img: "images/ruk_ (1).jpg", title: "Miniature Tulsi Vivah Set", price: "750" }
  ];

  return (
    <div>
      <div className="page-header">
        <h1>{t.rukhwatCollection}</h1>
      </div>

      <div className="product-grid">
        {products.map((product, index) => (
          // Use the ProductCard component instead of writing the JSX here
          <ProductCard
            key={index}
            image={product.img}
            title={product.title}
            price={product.price}
            description={product.description}
            // Pass the addToCart function as a prop
            addToCart={() => addToCart({
              id: product.title,
              title: product.title,
              price: product.price,
              image: product.img
            })}
            addToWishlist={() => addToWishlist({ id: product.title, title: product.title, price: product.price, image: product.img })}
          />
        ))}
        <ArtisanProductListings category="rukhwat" addToCart={addToCart} addToWishlist={addToWishlist} />
      </div>
    </div>
  );
}

export default Rukhwat;