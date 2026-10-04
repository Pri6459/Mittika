import React from "react";
import ProductCard from "./ProductCard"; // Import the ProductCard 
import ArtisanProductListings from "./ArtisanProductListings";
import { useLanguage } from "../utils/LanguageContext";

// The component now receives the 'addToCart' function as a prop
function SpiritualCorner({ addToCart, addToWishlist }) {
  const { t } = useLanguage();
  const products = [
    { img: "images/spritual_2.jpg", title: "Set of Miniature Divine Figurines", price: "2,500", alt: "Miniature clay figurines" },
    { img: "images/spritual_5.jpg", title: "Lakshmi-Ganesha Tea Light Holder", price: "1,100", alt: "Lakshmi and Ganesha tea light holder" },
    { img: "images/spritual_3.jpg", title: "Terracotta Divine Lamp Stand", price: "950", alt: "Terracotta lamp stand" },
    { img: "images/spritual_1.jpg", title: "Handcrafted Coconut Shell Incense Burner", price: "750", alt: "Coconut shell incense burner" },
    { img: "images/spritual_8.jpg", title: "Miniature Stone Temple Replica", price: "1,200", alt: "Stone temple replica" },
    { img: "images/spritual_6.jpg", title: "Mirror Mosaic Elephant Wall Decor", price: "1,800", alt: "Elephant wall decor" },
    { img: "images/spritual_9.jpg", title: "Hand-knitted Lotus Dress for Krishna Figurine", price: "850", alt: "Krishna lotus dress" },
    { img: "images/spritual_7.jpg", title: "Hand-knitted White & Red Floral Garland", price: "600", alt: "Knitted garland" },
    { img: "images/spritual_4.jpg", title: "Servdharam Ganga Jal (250ml)", price: "350", alt: "Bottle of Ganga Jal" },
    { img: "images/spritual_10.jpg", title: "Complete Karwa Chauth Puja Kit", price: "1,800", alt: "Karwa Chauth Puja Kit" },
    { img: "images/spritual_11.jpg", title: "Hand-carved Wooden Buddha Head", price: "3,200", alt: "Wooden Buddha Head" },
    { img: "images/spritual_12.jpg", title: "Terracotta Sculpture of Shiva Parvati", price: "2,500", alt: "Terracotta Shiva Parvati" },
    { img: "images/spritual_13.jpg", title: "Terracotta Deity Figurines & Diyas", price: "1,300", alt: "Terracotta deity figurines" },
    { img: "images/spritual_14.jpg", title: "Brass Lamp & Bell Wall Decor", price: "1,600", alt: "Brass lamp wall decor" },
    { img: "images/spritual_15.jpg", title: "Resin Agate Deity Coasters (Set of 5)", price: "2,200", alt: "Resin deity coasters" },
    { img: "images/spritual_16.jpg", title: "Shiva Lingam Waterfall Incense Burner", price: "1,400", alt: "Shiva lingam incense burner" },
    { img: "images/spritual_17.jpg", title: "Lord Shiva Backflow Incense Burner", price: "1,100", alt: "Backflow incense burner" },
    { img: "images/spritual_18.jpg", title: "Goddess Face Wall Plate", price: "1,200", alt: "Goddess face wall plate" },
    { img: "images/spritual_19.jpg", title: "'Shubh Labh' Wall Hanging Set", price: "950", alt: "Shubh Labh wall hanging" },
    { img: "images/spritual_20.jpg", title: "Hand-painted Deity Winnowing Basket", price: "1,800", alt: "Deity basket" },
  ];

  return (
    <div>
      <div className="page-header">
        <h1>{t.spiritualCollection}</h1>
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
        <ArtisanProductListings category="spiritual" addToCart={addToCart} addToWishlist={addToWishlist} />
      </div>
    </div>
  );
}

export default SpiritualCorner;