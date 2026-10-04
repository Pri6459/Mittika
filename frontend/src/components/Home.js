import React from "react";
import ProductCard from "./ProductCard";
import ArtisanProductListings from "./ArtisanProductListings";
import { useLanguage } from "../utils/LanguageContext";


function Home({ addToCart, addToWishlist }) {
  const { t } = useLanguage();
  const products = [
    {
      img: "images/home (1).jpeg",
      title: "Carved Wooden Elephant Accent Table",
      price: "1,200",
      description: "A hand-carved wooden elephant-form stand with a wide bowl-shaped top, suitable as a decorative accent table."
    },
    {
      img: "images/home (2).jpeg",
      title: "Hand-woven Striped Cotton Rug",
      price: "2,500",
      description: "A flat-woven cotton floor rug with green geometric stripes and fringed edges."
    },
    {
      img: "images/home (3).jpeg",
      title: "Embroidered Tree-of-Life Wall Hanging",
      price: "1,800",
      description: "A teal textile wall hanging embroidered with a flowering tree motif in white, blue, and yellow thread."
    },
    {
      img: "images/home (4).jpeg",
      title: "Textured Ceramic Vase",
      price: "950",
      description: "A small, textured ceramic vase with a matte finish, ideal for a single stem or a small bouquet."
    },
    {
      img: "images/home (5).jpeg",
      title: "Hand-painted Ceramic Serving Dish",
      price: "750",
      description: "A square-shaped ceramic serving dish with a unique hand-painted design in shades of blue and gold."
    },
    {
      img: "images/home (6).jpeg",
      title: "Decorative Miniature Clay Pots",
      price: "400",
      description: "A set of small, decorative clay pots with subtle, hand-painted designs, suitable for small plants or as standalone decor."
    },
    {
      img: "images/home (7).jpeg",
      title: "Carved Wooden Elephant",
      price: "1,100",
      description: "A small, intricately carved wooden figurine of an elephant, a traditional symbol of good luck."
    },
    {
      img: "images/home (8).jpeg",
      title: "Colorful Hand-painted Kettle",
      price: "1,300",
      description: "A decorative metal kettle with vibrant, hand-painted floral patterns, perfect as a centerpiece or home accent."
    },
    {
      img: "images/home (9).jpeg",
      title: "Resin & Pressed Flower Tray",
      price: "1,900",
      description: "A decorative tray made from resin, with dried pressed flowers and golden flakes embedded inside for a luxurious feel."
    },
    {
      img: "images/home (10).jpeg",
      title: "Hand-woven Jute Rug",
      price: "3,500",
      description: "A circular hand-woven jute rug with a fringed border, adding a natural and earthy texture to any room."
    },
    {
      img: "images/home (11).jpeg",
      title: "Hand-painted Wooden Wall Hanging",
      price: "1,500",
      description: "A decorative wooden wall hanging with traditional hand-painted patterns and a central mirror."
    },
    {
      img: "images/home (12).jpeg",
      title: "Set of Hand-painted Vases",
      price: "2,200",
      description: "A collection of assorted vases, each with a unique, hand-painted design in shades of blue and white."
    },
    {
      img: "images/home (13).jpeg",
      title: "Clay Decorative Plate",
      price: "1,100",
      description: "A decorative clay plate with a beige and brown patterned finish, suitable as a centerpiece or wall decor."
    },
    {
      img: "images/home (14).jpeg",
      title: "Hand-Painted Bird Figurines (Set of 3)",
      price: "950",
      description: "A set of three small, ceramic or clay bird figurines with intricate hand-painted details."
    },
    {
      img: "images/home (15).jpeg",
      title: "Terracotta Flower Pot with Stand",
      price: "1,400",
      description: "A classic terracotta flower pot with a simple, dark metal stand, perfect for indoor plants."
    },
    {
      img: "images/home (16).jpeg",
      title: "Resin-framed Wall Art",
      price: "2,800",
      description: "A large wall art piece with a unique abstract design and a textured resin frame."
    },
    {
      img: "images/home (17).jpeg",
      title: "Miniature Terracotta Lantern",
      price: "650",
      description: "A small, decorative terracotta lantern with detailed cutouts for light to shine through."
    },
    {
      img: "images/home (18).jpeg",
      title: "Decorative Terracotta Wall Plate",
      price: "1,600",
      description: "A decorative terracotta plate with a white and blue hand-painted design, ideal for hanging on a wall."
    },
    {
      img: "images/home (19).jpeg",
      title: "Hand-painted Wooden Stool",
      price: "2,900",
      description: "A small, handcrafted wooden stool with a vibrant hand-painted top featuring a mandala-like design."
    },
    {
      img: "images/home (20).jpeg",
      title: "Terracotta Vase with Handles",
      price: "1,350",
      description: "A unique terracotta vase with handles, featuring a geometric pattern and a natural, rustic finish."
    },
    {
      img: "images/home (21).jpeg",
      title: "Hand-painted Terracotta Jar",
      price: "850",
      description: "A small terracotta jar with a lid, featuring a geometric hand-painted design in white and red."
    },
    {
      img: "images/home (22).jpeg",
      title: "Decorative Macrame Wall Hanging",
      price: "1,200",
      description: "A beautiful macrame wall hanging with a detailed woven pattern and tassels, adding a bohemian touch to any room."
    },
    {
      img: "images/home (23).jpeg",
      title: "Hand-painted Ceramic Bowl",
      price: "600",
      description: "A small, hand-painted ceramic bowl with a unique floral design on the inside."
    },
    {
      img: "images/home (24).jpeg",
      title: "Decorative Glass Bottle with Jute & Flowers",
      price: "500",
      description: "A decorative glass bottle wrapped in jute string and adorned with small artificial flowers."
    },
    {
      img: "images/home (25).jpeg",
      title: "Hand-woven Planter Basket",
      price: "900",
      description: "A rustic, hand-woven basket perfect for holding a plant pot, with a natural and textured look."
    },
    {
      img: "images/home (26).jpeg",
      title: "Decorative Terracotta Pot with Stand",
      price: "1,600",
      description: "A decorative terracotta pot with intricate carvings, seated on a sturdy wooden stand."
    },
    {
      img: "images/home (27).jpeg",
      title: "Hand-painted Wall Mirror",
      price: "2,100",
      description: "A circular wall mirror with a beautifully hand-painted border featuring traditional Indian folk art."
    },
    {
      img: "images/home (28).jpeg",
      title: "Set of Miniature Clay Vases",
      price: "700",
      description: "A set of several small, handmade clay vases in different shapes and sizes."
    },
    {
      img: "images/home (29).jpeg",
      title: "Hand-Painted Clay Lantern",
      price: "1,100",
      description: "A rustic clay lantern with hand-painted details and cutouts, designed to hold a small candle or light."
    },
    {
      img: "images/home (30).jpeg",
      title: "Decorative Bird Figurines on a Log",
      price: "850",
      description: "A decorative piece featuring several small, colorful bird figurines perched on a natural piece of wood or log."
    },
    {
      img: "images/home (31).jpeg",
      title: "Ceramic Plate with Leaf Impression",
      price: "800",
      description: "A decorative ceramic plate with an impressed leaf pattern and a light green glaze."
    },
    {
      img: "images/home (32).jpeg",
      title: "Hand-Painted Terracotta Pot",
      price: "750",
      description: "A small terracotta pot with a delicate floral design hand-painted on a white background."
    },
    {
      img: "images/home (33).jpeg",
      title: "Traditional Wooden & Metal Wall Clock",
      price: "2,800",
      description: "A large, traditional-style wall clock with a distressed wooden frame and a metal clock face."
    },
    {
      img: "images/home (34).jpeg",
      title: "Set of Miniature Clay Pots (Colored)",
      price: "650",
      description: "A set of small clay pots in different shapes, painted in vibrant colors."
    },
    {
      img: "images/home (35).jpeg",
      title: "Hand-painted Terracotta Water Pitcher",
      price: "1,500",
      description: "A traditional terracotta water pitcher with a colorful, hand-painted peacock design."
    },
    {
      img: "images/home (36).jpeg",
      title: "Intricate Carved Wooden Panel",
      price: "3,200",
      description: "A detailed, hand-carved wooden panel featuring a complex geometric pattern."
    },
    {
      img: "images/home (37).jpeg",
      title: "Decorative Clay & Twine Vase",
      price: "950",
      description: "A unique decorative vase with a natural clay base and a top wrapped in twine for a rustic feel."
    },
    {
      img: "images/home (38).jpeg",
      title: "Assorted Decorative Vases",
      price: "2,000",
      description: "A collection of assorted small vases in different materials and colors, perfect for a shelf display."
    },
    {
      img: "images/home (39).jpeg",
      title: "Terracotta Flower Pot with a Hand-painted Design",
      price: "1,200",
      description: "A simple terracotta flower pot adorned with a hand-painted black and white pattern."
    },
    {
      img: "images/home (40).jpeg",
      title: "Hand-painted Kettle with Floral Design",
      price: "1,400",
      description: "A metal kettle with a vibrant and detailed hand-painted floral pattern, a perfect decorative accent."
    },
    {
      img: "images/home (41).jpeg",
      title: "Set of Wooden Wall Planters",
      price: "1,800",
      description: "A set of wooden wall-mounted planters in a triangular shape, ideal for succulents or small air plants."
    },
    {
      img: "images/home (42).jpeg",
      title: "Hand-painted Terracotta Tray",
      price: "1,100",
      description: "A rectangular terracotta tray with a black and white geometric pattern, perfect for serving or as a decorative piece."
    },
    {
      img: "images/home (43).jpeg",
      title: "Ceramic Bowl with Textured Finish",
      price: "750",
      description: "A small, deep ceramic bowl with a unique textured outer surface and a smooth, dark blue glazed interior."
    },
    {
      img: "images/home (44).jpeg",
      title: "Resin Wall Art with Gold Flakes",
      price: "2,600",
      description: "A modern wall art piece made of resin with a marble-like effect and embedded gold flakes."
    },
    {
      img: "images/home (45).jpeg",
      title: "Hand-painted Terracotta Serving Pot",
      price: "950",
      description: "A small terracotta pot with a lid, hand-painted with a simple yet elegant design."
    },
    {
      img: "images/home (46).jpeg",
      title: "Carved Wooden Elephant Head",
      price: "3,000",
      description: "A magnificent, hand-carved wooden elephant head wall mount, perfect for a statement wall."
    },
    {
      img: "images/home (47).jpeg",
      title: "Decorative Resin Ganesha Idol",
      price: "1,800",
      description: "A small resin idol of Lord Ganesha, seated on a base, with a metallic finish and intricate details."
    },
    {
      img: "images/home (48).jpeg",
      title: "Hand-painted Terracotta Wind Chime",
      price: "1,150",
      description: "A rustic wind chime made from small terracotta pieces with a hand-painted floral design."
    },
    {
      img: "images/home (49).jpeg",
      title: "Hand-painted Bird House",
      price: "1,500",
      description: "A small, hand-painted wooden birdhouse with a colorful and inviting design."
    },
    {
      img: "images/home (50).jpeg",
      title: "Resin & Wood Coaster Set",
      price: "1,300",
      description: "A set of coasters combining the natural look of wood with a colorful resin design."
    },
    {
      img: "images/home (51).jpeg",
      title: "Hand-painted Terracotta Vase",
      price: "1,100",
      description: "A rustic terracotta vase with a wide mouth and a simple, hand-painted floral pattern."
    },
    {
      img: "images/home (52).jpeg",
      title: "Wooden Wall Art with Terracotta Plates",
      price: "2,400",
      description: "A unique wall decor piece featuring a dark wooden frame holding three small, hand-painted terracotta plates."
    },
    {
      img: "images/home (53).jpeg",
      title: "Hand-painted Terracotta Plate Set",
      price: "1,700",
      description: "A set of two decorative terracotta plates, each with a different hand-painted design in blue and red."
    },
    {
      img: "images/home (54).jpeg",
      title: "Small Decorative Clay Bell",
      price: "450",
      description: "A small, handcrafted clay bell with an intricate cutout design."
    },
    {
      img: "images/home (55).jpeg",
      title: "Decorative Miniature Clay Pots (Abstract)",
      price: "550",
      description: "A set of two small, decorative clay pots with abstract, artistic paint strokes."
    },
    {
      img: "images/home (56).jpeg",
      title: "Hand-painted Clay Pot with Handles",
      price: "1,250",
      description: "A small clay pot with a handle on each side, featuring a hand-painted design of a bird and flowers."
    },
    {
      img: "images/home (57).jpeg",
      title: "Hand-painted Wooden Wall Plate",
      price: "1,900",
      description: "A circular wooden wall plate with a detailed hand-painted scene of a village and a person."
    },
    {
      img: "images/home (58).jpeg",
      title: "Set of Hand-painted Terracotta Cups",
      price: "850",
      description: "A set of two small terracotta cups with simple, hand-painted designs, ideal for tea or as decor."
    },
    {
      img: "images/home (59).jpeg",
      title: "Rustic Wooden Plant Stand",
      price: "1,600",
      description: "A handcrafted wooden plant stand with a natural, unfinished look, perfect for a single pot."
    },
    {
      img: "images/home (60).jpeg",
      title: "Hand-painted Terracotta Jug",
      price: "1,300",
      description: "A large terracotta jug with a handle, featuring a vibrant hand-painted pattern around the body."
    },
    {
      img: "images/home (61).jpeg",
      title: "Textured Terracotta Vase",
      price: "1,150",
      description: "A medium-sized terracotta vase with a rough, textured finish and a natural, unpainted look."
    },
    {
      img: "images/home (62).jpeg",
      title: "Decorative Miniature Pots with a Rope Accent",
      price: "750",
      description: "A set of two small, decorative clay pots with a simple, solid color and a rope tied around the neck."
    },
    {
      img: "images/home (63).jpeg",
      title: "Hand-painted Terracotta Plate",
      price: "900",
      description: "A decorative terracotta plate with a rustic finish and a hand-painted design of a bird in a cage."
    },
    {
      img: "images/home (64).jpeg",
      title: "Hand-carved Wooden Coaster Set",
      price: "1,100",
      description: "A set of wooden coasters with an intricate, hand-carved floral pattern."
    },
    {
      img: "images/home (65).jpeg",
      title: "Hand-painted Decorative Box",
      price: "1,300",
      description: "A small, hand-painted wooden box with a vibrant, detailed design on the lid."
    },
    {
      img: "images/home (66).jpeg",
      title: "Terracotta Flower Pot with a Hand-painted Pattern",
      price: "950",
      description: "A classic terracotta flower pot with a simple, hand-painted geometric pattern in black."
    },
    {
      img: "images/home (67).jpeg",
      title: "Decorative Clay Pots with Rope",
      price: "600",
      description: "A set of small, decorative clay pots with a simple design and a thick rope handle."
    },
    {
      img: "images/home (68).jpeg",
      title: "Hand-painted Terracotta Pot",
      price: "850",
      description: "A decorative terracotta pot with a hand-painted scene of a village and a tree."
    },
    {
      img: "images/home (69).jpeg",
      title: "Miniature Terracotta Jugs",
      price: "500",
      description: "A pair of small, decorative terracotta jugs with a rustic finish and intricate carvings."
    },
    {
      img: "images/home (70).jpeg",
      title: "Hand-painted Terracotta Plate with Floral Design",
      price: "1,000",
      description: "A decorative terracotta plate with a simple, hand-painted floral motif in a rustic style."
    },
    {
      img: "images/home (71).jpeg",
      title: "Hand-painted Wooden Wall Hanging",
      price: "1,700",
      description: "A rectangular wooden wall hanging with a hand-painted scene of a rustic landscape."
    },
    {
      img: "images/home (72).jpeg",
      title: "Set of Miniature Clay Pots",
      price: "750",
      description: "A collection of small, unpainted clay pots in various shapes and sizes, suitable for small plants or display."
    },
    {
      img: "images/home (73).jpeg",
      title: "Decorative Hanging Terracotta Bird",
      price: "550",
      description: "A decorative hanging ornament of a bird, handcrafted from terracotta with hand-painted details."
    },
    {
      img: "images/home (74).jpeg",
      title: "Hand-painted Terracotta Pot",
      price: "800",
      description: "A decorative terracotta pot with a unique hand-painted design and a natural, unglazed finish."
    },
    {
      img: "images/home (75).jpeg",
      title: "Hand-carved Wooden Wall Art",
      price: "2,500",
      description: "A round, hand-carved wooden wall art piece featuring a detailed mandala-like pattern."
    }
  ];

  return (
    <div>
      <div className="page-header">
        <h1>{t.homeCollection}</h1>
      </div>

      <div className="product-grid">
        {products.map((product, index) => (
          <ProductCard
            key={index}
            image={product.img}
            title={product.title}
            price={product.price}
            description={product.description}
            addToCart={() => addToCart({
              id: product.title,
              title: product.title,
              price: product.price,
              image: product.img
            })}
            addToWishlist={() => addToWishlist({ id: product.title, title: product.title, price: product.price, image: product.img })}
          />
        ))}
        <ArtisanProductListings category="home" addToCart={addToCart} addToWishlist={addToWishlist} />
      </div>
    </div>
  );
}

export default Home;