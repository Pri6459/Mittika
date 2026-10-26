import React from "react";
import ProductCard from "./ProductCard";
import ArtisanProductListings from "./ArtisanProductListings";
import { useLanguage } from "../utils/LanguageContext";


// The component now receives the 'addToCart' function as a prop
function Pottery({ addToCart, addToWishlist }) {
  const { t } = useLanguage();
  const products = [
    { img: "images/pot1.jpg", title: "Terracotta Wind Chimes", price: "950", description: "Earthy terracotta chimes bring gentle movement and a warm, handmade accent to a balcony, window, or garden." },
    { img: "images/pot2.jpg", title: "Terracotta Planter with Designs", price: "800", description: "A terracotta planter decorated with traditional motifs, ready to display a favorite plant indoors or outside." },
    { img: "images/pot3.jpg", title: "Decorative Glass Bottle", price: "650", description: "A glass bottle transformed into a decorative accent, adding handcrafted character to a shelf or tabletop." },
    { img: "images/pot4.jpg", title: "Ceramic Utensil Holder", price: "950", description: "A ceramic countertop holder that keeps cooking utensils together while adding an artful touch to the kitchen." },
    { img: "images/pot5.jpg", title: "Hand-Painted Storage Pot", price: "1,100", description: "A storage pot finished with hand-painted decoration, combining practical use with the warmth of artisan craft." },
    { img: "images/pot6.jpg", title: "Elephant-Themed Ceramic Vase", price: "1,500", description: "A ceramic vase featuring elephant-inspired detailing, designed to stand out with flowers or as a display piece." },
    { img: "images/pot7.jpg", title: "Small Decorative Jar", price: "450", description: "A petite decorative jar for storing small keepsakes or adding a handcrafted accent to a shelf." },
    { img: "images/pot8.jpg", title: "Terracotta Decorative Lantern", price: "2,200", description: "A terracotta lantern with a warm, earthy presence, bringing a welcoming glow to a quiet corner or celebration." },
    { img: "images/pot9.jpg", title: "Black & White Painted Vase", price: "2,500", description: "A statement vase with contrasting black-and-white painted decoration for contemporary or traditional interiors." },
    { img: "images/pot10.jpg", title: "Red Decorative Stacked Pots", price: "1,700", description: "A stacked-pot arrangement in a rich red tone, offering a sculptural focal point for indoor or outdoor spaces." },
    { img: "images/pot11.jpg", title: "Traditional Clay Jug with Carvings", price: "1,500", description: "A traditional clay jug highlighted with carved details, celebrating the texture and form of earthenware." },
    { img: "images/pot12.jpg", title: "Decorative Leaf Wall Hanging", price: "1,800", description: "A leaf-inspired wall hanging that brings a nature-led shape and handmade detail to your wall décor." },
    { img: "images/pot13.jpg", title: "Set of 4 Wooden Bowls", price: "2,100", description: "Four wooden bowls with natural character, suited to serving, arranging small items, or styling a tabletop." },
    { img: "images/pot14.jpg", title: "Decorative Plates (Set of 4)", price: "2,500", description: "A coordinated set of four decorative plates for creating a colorful arrangement on a wall or display shelf." },
    { img: "images/pot15.jpg", title: "Blue Elephant Painted Vase", price: "1,400", description: "A vase decorated with a blue elephant motif, bringing folk-inspired color to flowers or a display shelf." },
    { img: "images/pot16.jpg", title: "Terracotta Diya Lamp", price: "650", description: "A classic terracotta diya for a warm, traditional glow during daily prayers and festive gatherings." },
    { img: "images/pot17.jpg", title: "Terracotta Wind Chime Bell", price: "950", description: "A terracotta bell-style chime with an earthy handmade look, adding a gentle accent to open spaces." },
    { img: "images/pot18.jpg", title: "Set of 2 Camel Planters", price: "1,600", description: "A pair of camel-shaped planters that bring a playful folk-art touch to small plants and succulents." },
    { img: "images/pot19.jpg", title: "Abstract Ceramic Flower Vase", price: "1,750", description: "An abstract ceramic vase with an expressive silhouette, made to complement blooms or stand alone as art." },
    { img: "images/pot20.jpg", title: "Set of 3 Humanoid Figurines", price: "2,800", description: "Three characterful humanoid figurines arranged as a sculptural set for shelves, desks, or curated displays." },
    { img: "images/pot (21).jpg", title: "Hand-painted Figurine Planters (Set of 2)", price: "₹,200", description: "Two hand-painted figurine planters that pair functional planting space with cheerful sculptural detail." },
    { img: "images/pot (22).jpg", title: "Large Elephant Terracotta Planter", price: "1,800", description: "A large terracotta planter shaped around an elephant motif, bringing folk-inspired character to a favorite plant." },
    { img: "images/pot (23).jpg", title: "Handmade Ceramic Tic-Tac-Toe Set", price: "900", description: "A handmade ceramic tic-tac-toe set that turns a familiar game into a playful keepsake for the home." },
    { img: "images/pot (24).jpg", title: "Ceramic Sloth Incense Holder", price: "650", description: "A relaxed sloth design makes this ceramic incense holder a charming addition to a calm corner." },
    { img: "images/pot (25).jpg", title: "Miniature Terracotta Kitchen Set", price: "1,200", description: "A miniature terracotta kitchen set that captures the charm of traditional earthenware in a decorative display." },
    { img: "images/pot (26).jpg", title: "Mushroom Brush Holder", price: "850", description: "A whimsical mushroom-shaped holder keeps brushes together while adding a playful handmade detail to a desk." },
    { img: "images/pot (27).jpg", title: "Handmade Earthenware Money Bank", price: "700", description: "A handmade earthenware money bank offers a simple place to save and a charming accent for a shelf." },
    { img: "images/pot (28).jpg", title: "Hanging Terracotta Planters (Set of 4)", price: "1,650", description: "Four hanging terracotta planters create a warm, layered display for trailing plants on a balcony or patio." },
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