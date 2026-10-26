import React from "react";
import ProductCard from "./ProductCard"; // Import the ProductCard 
import ArtisanProductListings from "./ArtisanProductListings";
import { useLanguage } from "../utils/LanguageContext";

// The component now receives the 'addToCart' function as a prop
function Rukhwat({ addToCart, addToWishlist }) {
  const { t } = useLanguage();
  const products = [
    { img: "images/ruk_ (26).jpg", title: "Hand-decorated Gift Platter", price: "1,500", description: "A festive platter dressed with colorful hand-finished details, ready to display or present as a thoughtful gift." },
    { img: "images/ruk_ (25).jpg", title: "Hand-painted Miniature Kitchen Set", price: "1,100", description: "A miniature kitchen collection painted by hand, capturing the charm of traditional household scenes in a keepsake display." },
    { img: "images/ruk_ (24).jpg", title: "Decorative Pistachio Shell Birdhouses (Set of 4)", price: "2,400", description: "Four whimsical birdhouses decorated with pistachio shells, bringing a playful natural texture to a festive display." },
    { img: "images/ruk_ (23).jpg", title: "Handcrafted Wooden & Fabric Trays (Set of 5)", price: "2,800", description: "A set of five small wooden trays finished with patterned fabric, made for decorative presentation and serving." },
    { img: "images/ruk_ (22).jpg", title: "Miniature Musical Instrument Set - Type 2", price: "2,000", description: "A miniature collection of musical instruments arranged as a decorative tribute to India's rich musical traditions." },
    { img: "images/ruk_ (21).jpg", title: "Miniature Musical Instrument Set - Type 1", price: "2,200", description: "A finely arranged miniature instrument set that makes a distinctive display piece for music lovers and festive décor." },
    { img: "images/ruk_ (20).jpg", title: "Hand-painted Marathi Rukhwat Plate", price: "1,800", description: "A hand-painted plate inspired by Marathi wedding traditions, created to bring regional color to a Rukhwat display." },
    { img: "images/ruk_ (19).jpg", title: "Hand-Painted Wedding Thali", price: "2,500", description: "A decorative wedding thali finished with hand-painted details for ceremonies, gifting, or a traditional home display." },
    { img: "images/ruk_ (18).jpg", title: "Decorative Popsicle Stick House", price: "1,100", description: "A miniature house assembled from craft sticks, turning simple materials into a charming handmade display." },
    { img: "images/ruk_ (17).jpg", title: "Bridal & Groom Decorative Cones", price: "1,500", description: "A decorative pair of cones for bridal and groom displays, adding a traditional finishing touch to wedding décor." },
    { img: "images/ruk_ (16).jpg", title: "Miniature Silk Gift Bags (Set of 4)", price: "850", description: "Four small silk-look gift bags designed for miniature displays, festive favors, or decorative presentation." },
    { img: "images/ruk_ (15).jpg", title: "Miniature Paper Dolls in Traditional Attire", price: "1,200", description: "Handmade miniature paper dolls dressed in traditional attire, celebrating folk style in a compact keepsake display." },
    { img: "images/ruk_ (14).jpg", title: "Miniature Wedding Ceremony Thali", price: "950", description: "A small wedding ceremony thali arranged for miniature Rukhwat displays and traditional festive decoration." },
    { img: "images/ruk_ (13).jpg", title: "Decorative Winnowing Basket with Wheat", price: "1,600", description: "A traditional winnowing basket styled with wheat, representing harvest and abundance in a festive display." },
    { img: "images/ruk_ (12).jpg", title: "Large Decorative Rukhwat Basket", price: "3,000", description: "A generously sized decorative basket for arranging wedding keepsakes and celebrating the custom of Rukhwat." },
    { img: "images/ruk_ (11).jpg", title: "Miniature Tulsi Vivah Set", price: "750", description: "A miniature Tulsi Vivah arrangement that brings the beloved ceremonial tradition into a detailed decorative keepsake." },
    { img: "images/ruk_ (10).jpg", title: "Hand-painted Marathi Rukhwat Plate", price: "1,800", description: "A colorful hand-painted plate made to honor Marathi wedding customs and complete a traditional Rukhwat arrangement." },
    { img: "images/ruk_ (9).jpg", title: "Hand-Painted Wedding Thali", price: "2,500", description: "A hand-painted thali with a festive presence, suitable for wedding ceremonies, gifting, and cultural displays." },
    { img: "images/ruk_ (8).jpg", title: "Decorative Popsicle Stick House", price: "1,100", description: "A handcrafted miniature house made from craft sticks, adding a cheerful handmade accent to a celebration display." },
    { img: "images/ruk_ (7).jpg", title: "Bridal & Groom Decorative Cones", price: "1,500", description: "A matching set of decorative bridal and groom cones for traditional wedding arrangements and keepsake displays." },
    { img: "images/ruk_ (6).jpg", title: "Miniature Silk Gift Bags (Set of 4)", price: "850", description: "A set of four miniature gift bags with a silk-inspired finish, perfect for festive styling and tiny keepsakes." },
    { img: "images/ruk_ (5).jpg", title: "Miniature Paper Dolls in Traditional Attire", price: "1,200", description: "Traditional attire and handmade detail give these miniature paper dolls a charming place in a cultural display." },
    { img: "images/ruk_ (4).jpg", title: "Miniature Wedding Ceremony Thali", price: "950", description: "A miniature thali for wedding-themed displays, thoughtfully styled to evoke the rituals of a traditional celebration." },
    { img: "images/ruk_ (3).jpg", title: "Decorative Winnowing Basket with Wheat", price: "1,600", description: "A decorative wheat-filled winnowing basket that brings a harvest-inspired touch to wedding and festive décor." },
    { img: "images/ruk_ (2).jpg", title: "Large Decorative Rukhwat Basket", price: "3,000", description: "A large showcase basket designed to hold wedding display pieces and add a traditional focal point to the occasion." },
    { img: "images/ruk_ (1).jpg", title: "Miniature Tulsi Vivah Set", price: "750", description: "A detailed miniature set inspired by Tulsi Vivah, bringing a meaningful ceremonial scene to your home décor." }
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