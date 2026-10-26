import React from "react";
import ProductCard from "./ProductCard"; // Import the ProductCard 
import ArtisanProductListings from "./ArtisanProductListings";
import { useLanguage } from "../utils/LanguageContext";

// The component now receives the 'addToCart' function as a prop
function SpiritualCorner({ addToCart, addToWishlist }) {
  const { t } = useLanguage();
  const products = [
    { img: "images/spritual_2.jpg", title: "Set of Miniature Divine Figurines", price: "2,500", alt: "Miniature clay figurines", description: "A set of miniature divine figurines for a home shrine, prayer space, or thoughtful spiritual gift." },
    { img: "images/spritual_5.jpg", title: "Lakshmi-Ganesha Tea Light Holder", price: "1,100", alt: "Lakshmi and Ganesha tea light holder", description: "A devotional tea light holder featuring Lakshmi and Ganesha, made to bring a warm glow to festive prayers." },
    { img: "images/spritual_3.jpg", title: "Terracotta Divine Lamp Stand", price: "950", alt: "Terracotta lamp stand", description: "A terracotta lamp stand with a devotional design, bringing an earthy handmade presence to your puja space." },
    { img: "images/spritual_1.jpg", title: "Handcrafted Coconut Shell Incense Burner", price: "750", alt: "Coconut shell incense burner", description: "A handcrafted incense burner made from coconut shell, offering a natural-looking accent for moments of reflection." },
    { img: "images/spritual_8.jpg", title: "Miniature Stone Temple Replica", price: "1,200", alt: "Stone temple replica", description: "A miniature temple-inspired replica that makes a meaningful decorative piece for a shelf or prayer corner." },
    { img: "images/spritual_6.jpg", title: "Mirror Mosaic Elephant Wall Decor", price: "1,800", alt: "Elephant wall decor", description: "An elephant wall accent decorated with mirror-mosaic detail, adding sparkle and a traditional motif to your space." },
    { img: "images/spritual_9.jpg", title: "Hand-knitted Lotus Dress for Krishna Figurine", price: "850", alt: "Krishna lotus dress", description: "A hand-knitted lotus-inspired outfit made to dress a Krishna figurine for worship or festive display." },
    { img: "images/spritual_7.jpg", title: "Hand-knitted White & Red Floral Garland", price: "600", alt: "Knitted garland", description: "A hand-knitted garland in white and red floral tones for decorating a home shrine or festive setting." },
    { img: "images/spritual_4.jpg", title: "Servdharam Ganga Jal (250ml)", price: "350", alt: "Bottle of Ganga Jal", description: "A 250 ml bottle of Ganga Jal for personal worship and customary religious rituals." },
    { img: "images/spritual_10.jpg", title: "Complete Karwa Chauth Puja Kit", price: "1,800", alt: "Karwa Chauth Puja Kit", description: "A coordinated puja kit prepared for Karwa Chauth observances and the rituals of the festive evening." },
    { img: "images/spritual_11.jpg", title: "Hand-carved Wooden Buddha Head", price: "3,200", alt: "Wooden Buddha Head", description: "A hand-carved wooden Buddha head with a contemplative presence, suited to a quiet space for rest or reflection." },
    { img: "images/spritual_12.jpg", title: "Terracotta Sculpture of Shiva Parvati", price: "2,500", alt: "Terracotta Shiva Parvati", description: "A terracotta sculpture of Shiva and Parvati, bringing devotional artistry and an earthy finish to your home." },
    { img: "images/spritual_13.jpg", title: "Terracotta Deity Figurines & Diyas", price: "1,300", alt: "Terracotta deity figurines", description: "A collection of terracotta deity figurines and diyas for a warm, traditional arrangement during prayer or festivals." },
    { img: "images/spritual_14.jpg", title: "Brass Lamp & Bell Wall Decor", price: "1,600", alt: "Brass lamp wall decor", description: "A wall décor arrangement combining a brass lamp and bell, inspired by traditional details of a prayer space." },
    { img: "images/spritual_15.jpg", title: "Resin Agate Deity Coasters (Set of 5)", price: "2,200", alt: "Resin deity coasters", description: "Five resin coasters with agate-inspired color and deity motifs, blending everyday function with devotional décor." },
    { img: "images/spritual_16.jpg", title: "Shiva Lingam Waterfall Incense Burner", price: "1,400", alt: "Shiva lingam incense burner", description: "A Shiva Lingam-inspired incense burner designed to create a calm focal point in a meditation or prayer area." },
    { img: "images/spritual_17.jpg", title: "Lord Shiva Backflow Incense Burner", price: "1,100", alt: "Backflow incense burner", description: "A backflow incense burner featuring Lord Shiva, combining devotional styling with a soothing incense ritual." },
    { img: "images/spritual_18.jpg", title: "Goddess Face Wall Plate", price: "1,200", alt: "Goddess face wall plate", description: "A decorative wall plate centered on a goddess face, created as a striking spiritual accent for the home." },
    { img: "images/spritual_19.jpg", title: "'Shubh Labh' Wall Hanging Set", price: "950", alt: "Shubh Labh wall hanging", description: "A traditional 'Shubh Labh' hanging set to welcome auspicious wishes at an entrance or festive display." },
    { img: "images/spritual_20.jpg", title: "Hand-painted Deity Winnowing Basket", price: "1,800", alt: "Deity basket", description: "A winnowing basket decorated with hand-painted deity imagery, bringing folk craft to a devotional display." },
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