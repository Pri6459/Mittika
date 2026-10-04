import React from "react";
import ProductCard from "./ProductCard";
import ArtisanProductListings from "./ArtisanProductListings";
import { useLanguage } from "../utils/LanguageContext";


function Candle({ addToCart, addToWishlist }) {
  const { t } = useLanguage();
  const products = [
    {
      img: "images/candle (1).jpg",
      title: "Resin-Art Nesting Tables (Set of 3)",
      price: "850",
      description: "Three wooden nesting tables with glossy black tabletops decorated with swirling white and gold resin-art patterns."
    },
    {
      img: "images/candle (2).jpg",
      title: "Hand-painted Terracotta Wall Candle Holder",
      price: "1,200",
      description: "A red terracotta wall-mounted candle holder with hand-painted white floral motifs and a cup for one tealight."
    },
    {
      img: "images/candle (3).jpg",
      title: "Textured Bowl Candles",
      price: "700",
      description: "Candles set in white textured, bowl-shaped holders with hand-finished carved and painted patterns."
    },
    {
      img: "images/candle (4).jpg",
      title: "Three-Cup Resin and Wood Tealight Holder",
      price: "450",
      description: "A long rectangular holder combining teal-colored resin and natural wood, with spaces for three tealights."
    },
    {
      img: "images/candle (5).jpg",
      title: "Leaf-Shaped Wall Candle Holders (Set of 3)",
      price: "600",
      description: "Three rustic wall-mounted candle holders shaped like leaves, each designed to hold one small candle."
    },
    {
      img: "images/candle (6).jpg",
      title: "Painted Terracotta Candle Holders (Set of 3)",
      price: "350",
      description: "Three red terracotta candle holders decorated with bold white geometric patterns."
    },
    {
      img: "images/candle (7).jpg",
      title: "Pillar Candle with Glitter & Jewels",
      price: "280",
      description: "A decorative pillar candle embellished with gold glitter and small jewels, perfect for festive occasions."
    },
    {
      img: "images/candle (8).jpg",
      title: "Assorted Scented Jar Candles (Set of 4)",
      price: "950",
      description: "A collection of four scented candles in glass jars, each with a different aroma to create a unique mood."
    },
    {
      img: "images/candle (9).jpg",
      title: "Wooden Base with Scented Candles",
      price: "1,100",
      description: "A trio of scented jar candles artfully arranged on a rustic wooden base, tied with a jute rope for a natural look."
    },
    {
      img: "images/candle (10).jpg",
      title: "Hand-painted Terracotta Diyas (Set of 6)",
      price: "500",
      description: "A set of six traditional terracotta diyas (oil lamps) with intricate hand-painted designs, perfect for festivals and puja."
    },
    {
      img: "images/candle (11).jpg",
      title: "Custom Resin Letter/Alphabet",
      price: "400",
      description: "A resin art piece shaped like a letter of the alphabet, with intricate fillings of glitter and dried flowers."
    },
    {
      img: "images/candle (12).jpg",
      title: "Hand-poured Bubble Candles (Set of 4)",
      price: "750",
      description: "A set of four small, cube-shaped bubble candles in pastel colors, perfect for modern home decor."
    },
    {
      img: "images/candle (13).jpg",
      title: "Geode-Inspired Resin Wall Clock",
      price: "2,500",
      description: "A circular wall clock with a geode-inspired resin design, featuring gold flakes and shades of blue and white."
    },
    {
      img: "images/candle (14).jpg",
      title: "Resin & Agate Tray",
      price: "1,800",
      description: "A decorative serving tray made from resin with a marbled pattern, adorned with a slice of natural agate stone."
    },
    {
      img: "images/candle (15).jpg",
      title: "Terracotta Diffuser & Tea Light Holder",
      price: "650",
      description: "A two-piece terracotta set, including a base for a tea light and a top for essential oils or wax melts."
    },
    {
      img: "images/candle (16).jpg",
      title: "Shell-Shaped Wax Candles",
      price: "550",
      description: "A set of unique, shell-shaped wax candles in various colors, adding a coastal feel to your decor."
    },
    {
      img: "images/candle (17).jpg",
      title: "Handmade Ceramic Candle Holder",
      price: "900",
      description: "A rustic, handmade ceramic candle holder with a textured surface and a slot for a small taper candle."
    },
    {
      img: "images/candle (18).jpg",
      title: "Resin Art Wall Hanging",
      price: "1,300",
      description: "A circular resin art wall decor piece featuring a vibrant mix of colors and a shimmering finish."
    },
    {
      img: "images/candle (19).jpg",
      title: "Assorted Pillar Candles (Set of 3)",
      price: "450",
      description: "A set of three cylindrical pillar candles in different sizes and colors, perfect for a layered centerpiece."
    },
    {
      img: "images/candle (20).jpg",
      title: "Hand-Painted Resin Name Plate",
      price: "1,500",
      description: "A custom-made resin art nameplate, personalized with names and decorated with metallic and floral accents."
    },
    {
      img: "images/candle (21).jpg",
      title: "Decorative Resin Ganesha Idol",
      price: "1,400",
      description: "A seated resin sculpture of Lord Ganesha, with a matte finish and decorated with colorful hand-painted details."
    },
    {
      img: "images/candle (22).jpg",
      title: "Resin & Clay Coasters (Set of 4)",
      price: "1,600",
      description: "A set of four coasters with a unique design featuring a combination of resin and intricate claywork in a circular pattern."
    },
    {
      img: "images/candle (23).jpg",
      title: "Hand-painted Terracotta Tea Light Holders",
      price: "550",
      description: "A set of traditional terracotta tea light holders, painted in a striking black and white geometric pattern."
    },
    {
      img: "images/candle (24).jpg",
      title: "Floral Resin & Wood Name Plate",
      price: "1,700",
      description: "A custom resin and wood nameplate with a floral motif, featuring names written in elegant script."
    },
    {
      img: "images/candle (25).jpg",
      title: "Resin Art Wall Decor Frame",
      price: "1,900",
      description: "A decorative wall art frame made from a blend of resin and metallic pigments, with a shimmering, marbled finish."
    }
  ];

  return (
    <div>
      <div className="page-header">
        <h1>{t.candleCollection}</h1>
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
        <ArtisanProductListings category="candle" addToCart={addToCart} addToWishlist={addToWishlist} />
      </div>
    </div>
  );
}

export default Candle;