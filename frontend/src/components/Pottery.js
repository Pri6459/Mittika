import React from "react";
import ProductCard from "./ProductCard";
import ArtisanProductListings from "./ArtisanProductListings";
import { useLanguage } from "../utils/LanguageContext";


// The component now receives the 'addToCart' function as a prop
function Pottery({ addToCart, addToWishlist }) {
  const { t } = useLanguage();
  const products = [
    { img: "images/pot1.jpg", title: "Terracotta Wind Chimes", price: "950" },
    { img: "images/pot2.jpg", title: "Terracotta Planter with Designs", price: "800" },
    { img: "images/pot3.jpg", title: "Decorative Glass Bottle", price: "650" },
    { img: "images/pot4.jpg", title: "Ceramic Utensil Holder", price: "950" },
    { img: "images/pot5.jpg", title: "Hand-Painted Storage Pot", price: "1,100" },
    { img: "images/pot6.jpg", title: "Elephant-Themed Ceramic Vase", price: "1,500" },
    { img: "images/pot7.jpg", title: "Small Decorative Jar", price: "450" },
    { img: "images/pot8.jpg", title: "Terracotta Decorative Lantern", price: "2,200" },
    { img: "images/pot9.jpg", title: "Black & White Painted Vase", price: "2,500" },
    { img: "images/pot10.jpg", title: "Red Decorative Stacked Pots", price: "1,700" },
    { img: "images/pot11.jpg", title: "Traditional Clay Jug with Carvings", price: "1,500" },
    { img: "images/pot12.jpg", title: "Decorative Leaf Wall Hanging", price: "1,800" },
    { img: "images/pot13.jpg", title: "Set of 4 Wooden Bowls", price: "2,100" },
    { img: "images/pot14.jpg", title: "Decorative Plates (Set of 4)", price: "2,500" },
    { img: "images/pot15.jpg", title: "Blue Elephant Painted Vase", price: "1,400" },
    { img: "images/pot16.jpg", title: "Terracotta Diya Lamp", price: "650" },
    { img: "images/pot17.jpg", title: "Terracotta Wind Chime Bell", price: "950" },
    { img: "images/pot18.jpg", title: "Set of 2 Camel Planters", price: "1,600" },
    { img: "images/pot19.jpg", title: "Abstract Ceramic Flower Vase", price: "1,750" },
    { img: "images/pot20.jpg", title: "Set of 3 Humanoid Figurines", price: "2,800" },
    { img: "images/pot (21).jpg", title: "Hand-painted Figurine Planters (Set of 2)", price: "₹,200" },
    { img: "images/pot (22).jpg", title: "Large Elephant Terracotta Planter", price: "1,800" },
    { img: "images/pot (23).jpg", title: "Handmade Ceramic Tic-Tac-Toe Set", price: "900" },
    { img: "images/pot (24).jpg", title: "Ceramic Sloth Incense Holder", price: "650" },
    { img: "images/pot (25).jpg", title: "Miniature Terracotta Kitchen Set", price: "1,200" },
    { img: "images/pot (26).jpg", title: "Mushroom Brush Holder", price: "850" },
    { img: "images/pot (27).jpg", title: "Handmade Earthenware Money Bank", price: "700" },
    { img: "images/pot (28).jpg", title: "Hanging Terracotta Planters (Set of 4)", price: "1,650" },
  ];

  return (
    <div>
      <div className="page-header">
        <h1>{t.potteryCollection}</h1>
      </div>

      <div className="product-grid">
        {products.map((product, index) => (
          <ProductCard
            key={index}
            image={product.img}
            title={product.title}
            price={product.price}
            description={product.description}
            // Pass the addToCart function as a prop to ProductCard
            addToCart={() => addToCart({
              id: product.title,
              title: product.title,
              price: product.price,
              image: product.img
            })}
            addToWishlist={() => addToWishlist({ id: product.title, title: product.title, price: product.price, image: product.img })}
          />
        ))}
        <ArtisanProductListings category="pottery" addToCart={addToCart} addToWishlist={addToWishlist} />
      </div>
    </div>
  );
}

export default Pottery;