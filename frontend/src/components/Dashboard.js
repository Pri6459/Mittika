import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  FaFacebookF,
  FaInstagram,
  FaMicrophone,
  FaPinterestP,
  FaTwitter
} from "react-icons/fa";
import { useLanguage } from "../utils/LanguageContext";
import API from "../api";
import { backendUrl } from "../utils/backendUrl";


const Dashboard = ({ voiceSearchQuery }) => {
  const { t } = useLanguage();
  const [artisans, setArtisans] = useState([]);
  const [artisanLoadError, setArtisanLoadError] = useState(false);
  useEffect(() => {
    let active = true;
    API.get("/auth/artisans")
      .then((response) => {
        if (active) setArtisans(response.data.artisans || []);
      })
      .catch((error) => {
        console.error("Could not load artisan profiles:", error);
        if (active) setArtisanLoadError(true);
      });
    return () => { active = false; };
  }, []);

  const productImages = [
    "art_1.png", "art_2.png", "art_3.png", "art_4.png",
    "art_1.png", "art_2.png", "art_3.png", "art_4.png"
  ];

  const categories = [
    { img: "categ_homestyle.png", title: t.homeDecorCategory, to: "/home" },
    { img: "categ_rukhwat.png", title: t.rukhwatArtCategory, to: "/rukhwat" },
    { img: "categ_handmade_pot.png", title: t.potteryArtCategory, to: "/pottery" },
    { img: "categ_candle_resine.png", title: t.candleResinCategory, to: "/candle" },
    { img: "categ_jewllery.png", title: t.jewelleryArtCategory, to: "/jewellery" },
    { img: "categ_spritual.png", title: t.spiritualArtCategory, to: "/spiritualcorner" }
  ];

  const socialIcons = [
    { Icon: FaInstagram, alt: "Instagram" },
    { Icon: FaFacebookF, alt: "Facebook" },
    { Icon: FaTwitter, alt: "Twitter" },
    { Icon: FaPinterestP, alt: "Pinterest" }
  ];

  return (
    <div style={styles.app}>
      <style>
        {`
          @keyframes marquee {
            0% { transform: translateX(0); }
            100% { transform: translateX(-50%); }
          }
        `}
      </style>

      {/* Voice Search Spoken Query Banner */}
      {voiceSearchQuery && (
        <div style={{
          backgroundColor: "#C85A32",
          color: "#FFF",
          padding: "12px 25px",
          textAlign: "center",
          fontWeight: "700",
          fontSize: "1rem",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: "10px"
        }}>
          <FaMicrophone /> {t.voiceSearchResult}: "{voiceSearchQuery}"
          <Link to="/shop" style={{ color: "#FFF", textDecoration: "underline", marginLeft: 15 }}>
            {t.viewMatchingItems} &rarr;
          </Link>
        </div>
      )}

      <main className="dashboard-main" style={styles.container}>
        {/* Hero Section */}
        <section className="dashboard-hero" style={styles.heroSection}>
          <div className="dashboard-hero-left" style={styles.heroLeft}>
            <p style={styles.heroLabel}>{t.aiMarketplace}</p>
            <h1 style={styles.heroTitle}>{t.heroTitle}</h1>
            <p style={styles.heroText}>{t.heroSubtitle}</p>
          </div>
          <div className="dashboard-hero-right" style={styles.heroRight}>
            <Link to="/shop" style={styles.shopButton}>{t.shopNow}</Link>
          </div>
        </section>


        {/* Product Gallery */}
        <section style={styles.productGalleryContainer}>
          <div style={styles.marquee}>
            <div style={styles.marqueeContent}>
              {productImages.map((img, i) => (
                <div key={i} style={styles.productItem}>
                  <img src={img} alt={`Product ${i + 1}`} style={styles.productImg} />
                </div>
              ))}
            </div>
            <div style={styles.marqueeContent}>
              {productImages.map((img, i) => (
                <div key={`copy-${i}`} style={styles.productItem}>
                  <img src={img} alt={`Product ${i + 1}`} style={styles.productImg} />
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Categories Section */}
        <section className="dashboard-art-section" style={styles.artForms}>
          <h2 style={styles.sectionTitle}>{t.category}</h2>
          <div className="dashboard-category-gallery" style={styles.artGallery}>
            {categories.map((item, i) => (
              <Link key={i} to={item.to} style={{ textDecoration: 'none', color: 'inherit' }}>
                <div style={styles.artItem}>
                  <div style={styles.artImageWrapper}>
                    <img src={item.img} alt={item.title} style={styles.artImg} />
                  </div>
                  <p style={styles.artTitle}>{item.title}</p>
                </div>
              </Link>
            ))}
          </div>
        </section>

        {artisans.length > 0 && (
          <section className="dashboard-art-section" style={styles.artForms}>
            <h2 style={styles.sectionTitle}>{t.meetOurArtisans}</h2>
            <p style={styles.artisanIntro}>{t.meetOurArtisansDescription}</p>
            {artisanLoadError && <p role="status">{t.artisanProfilesFailed}</p>}
            <div style={styles.artisanGallery}>
              {artisans.map((artisan) => (
                <article key={artisan.id} style={styles.artisanCard}>
                  <img
                    src={backendUrl(artisan.profilePhoto)}
                    alt={artisan.name}
                    style={styles.artisanPhoto}
                  />
                  <h3 style={styles.artisanName}>{artisan.name}</h3>
                  {artisan.craft && <p style={styles.artisanDetail}>{artisan.craft}</p>}
                  {artisan.location && <p style={styles.artisanDetail}>{artisan.location}</p>}
                  <p style={styles.artisanDetail}>
                    {artisan.experience} {t.yearsExperience}
                  </p>
                </article>
              ))}
            </div>
          </section>
        )}

        {artisanLoadError && artisans.length === 0 && (
          <section style={styles.artForms} role="status">
            <h2 style={styles.sectionTitle}>{t.meetOurArtisans}</h2>
            <p>{t.artisanProfilesFailed}</p>
          </section>
        )}

        {/* Map Section */}
        <section style={styles.mapSection}>
          <h2 style={styles.sectionTitle}>{t.findUs}</h2>
          <div style={styles.mapContainer}>
            <iframe
              src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3770.8175440787723!2d73.01691127599059!3d19.071197982136058!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3be7c3905b452e8d%3A0xc3f6a297e2898991!2sDatta%20Meghe%20College%20of%20Engineering!5e0!3m2!1sen!2sin!4v1700685651554!5m2!1sen!2sin"
              width="600"
              height="450"
              style={{border:0, borderRadius: "15px"}}
              allowFullScreen=""
              loading="lazy"
              referrerPolicy="no-referrer-when-downgrade"
              title="location"
            ></iframe>
          </div>
        </section>

        {/* Newsletter */}
        <section style={styles.newsletter}>
          <p style={{marginBottom:"15px"}}>{t.subscribeText}</p>
          <div style={styles.subscribeForm}>
            <input type="email" placeholder={t.emailPlaceholder} style={styles.input}/>
            <button style={styles.subscribeButton}>{t.subscribe}</button>
          </div>
        </section>

        {/* Footer */}
        <footer style={styles.footer}>
          <div style={styles.footerContent}>
            <div style={styles.footerColumn}>
              <h4>{t.aboutCompany}</h4>
              <ul style={styles.footerList}>
                <li><span style={styles.footerLink}>About us</span></li>
                <li><span style={styles.footerLink}>{t.reviews}</span></li>
                <li><span style={styles.footerLink}>{t.blog}</span></li>
                <li><span style={styles.footerLink}>{t.coupons}</span></li>
                <li><span style={styles.footerLink}>{t.faqs}</span></li>
              </ul>
            </div>
            <div style={styles.footerColumn}>
              <h4>{t.customerService}</h4>
              <ul style={styles.footerList}>
                <li><span style={styles.footerLink}>{t.trackOrder}</span></li>
                <li><span style={styles.footerLink}>{t.privacyPolicy}</span></li>
                <li><span style={styles.footerLink}>{t.shippingReturns}</span></li>
                <li><span style={styles.footerLink}>{t.bulkOrders}</span></li>
                <li><span style={styles.footerLink}>{t.termsConditions}</span></li>
                <li><span style={styles.footerLink}>{t.contactUs}</span></li>
              </ul>
            </div>
            <div style={styles.footerColumn}>
              <h4>{t.followUs}</h4>
              <div style={styles.socialIcons}>
                {socialIcons.map(({ Icon, alt }) => (
                  <span key={alt} role="img" aria-label={alt} style={styles.socialIcon}>
                    <Icon aria-hidden="true" focusable="false" />
                  </span>
                ))}
              </div>
            </div>
          </div>
        </footer>
      </main>
    </div>
  );
};

// Styles with Hover Animations
const styles = {
 app: {
    fontFamily: "Poppins, sans-serif",
   background: "#FBF7F1",
   color: "#403126",
    minHeight: "100vh"
  },
  container: { padding: "40px clamp(18px, 4vw, 48px)", maxWidth: "1400px", margin: "0 auto" },
  heroSection: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "36px",
    marginBottom: "64px",
    background: "linear-gradient(125deg, #FFF9EF 0%, #F8EBDD 100%)",
    padding: "clamp(24px, 4vw, 48px)",
    borderRadius: "25px",
    boxShadow: "0 14px 40px rgba(93, 59, 38, 0.1)",
    border: "1px solid rgba(169, 79, 47, 0.08)"
  },
 heroLeft: { flex: "1 1 0", minWidth: 0 },
 heroRight: { flex: "1 1 0", minWidth: 0, paddingLeft: "clamp(0px, 2vw, 24px)" },
  heroLabel: {
    letterSpacing: "0.4px",
    color: "#974528",
    fontWeight: 700,
    marginBottom: "15px",
    padding: "5px 15px",
    borderRadius: "10px",
    background: "rgba(169,79,47,0.12)",
    display: "inline-block"
  },
  heroTitle: {
    fontSize: "clamp(2rem, 4vw, 3rem)",
    fontWeight: 800,
    lineHeight: 1.2,
    margin: "20px 0",
    background: "rgba(255,255,255,0.52)",
    padding: "10px 15px",
    borderRadius: "12px"
  },
  heroSubtitle: { fontSize: "2rem", color: "#974528", fontWeight: 700, marginBottom: "10px" },
  heroText: { fontSize: "1.2rem", color: "#5B4636", marginBottom: "10px" },
  promoBox: {
    marginTop: "20px",
    padding: "18px",
    backgroundColor: "#F0DEC2",
    borderRadius: "15px",
    fontWeight: 600,
    color: "#5B4636",
    textAlign: "center",
    boxShadow: "0 6px 20px rgba(0,0,0,0.1)",
    transition: "transform 0.3s, box-shadow 0.3s",
    cursor: "pointer",
  },
  shopButton: {
    display: "inline-block",
    padding: "15px 35px",
    backgroundColor: "#A0522D",
    color: "#fff",
    borderRadius: "12px",
    textDecoration: "none",
    fontWeight: 700,
    marginTop: "20px",
    transition: "0.3s",
    cursor: "pointer"
  },

  productGalleryContainer: {
    overflow: "hidden",
    position: "relative",
    marginBottom: "60px",
    borderRadius: "20px",
    boxShadow: "0 6px 20px rgba(0,0,0,0.1)",
    background: "linear-gradient(120deg, #F4E8D9, #EAD8C4)",
    padding: "20px 0"
  },
  marquee: { display: "flex", width: "200%", animation: "marquee 20s linear infinite" },
  marqueeContent: { display: "flex", gap: "20px" },
  productItem: {
    flex: "0 0 auto",
    transition: "transform 0.3s",
  },
  productImg: {
    width: "180px",
    height: "180px",
    objectFit: "cover",
    borderRadius: "15px",
    boxShadow: "0 6px 15px rgba(0,0,0,0.12)",
    transition: "transform 0.3s, box-shadow 0.3s",
    cursor: "pointer"
  },

  artForms: { marginBottom: "60px" },
  sectionTitle: { fontSize: "2rem", fontWeight: 700, color: "#49352A", borderBottom: "3px solid #B45C38", paddingBottom: "8px", marginBottom: "30px" },
  artGallery: { display: "grid", alignItems: "start", gap: "clamp(10px, 1.5vw, 22px)" },
  artisanIntro: { color: "#5B4636", textAlign: "center", marginTop: "-12px", marginBottom: "24px" },
  artisanGallery: { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(210px, 1fr))", gap: "24px" },
  artisanCard: { background: "#FFFDF9", border: "1px solid #E9D7C1", borderRadius: "18px", padding: "18px", textAlign: "center", boxShadow: "0 6px 20px rgba(0,0,0,0.08)" },
  artisanPhoto: { width: "100%", maxWidth: "220px", aspectRatio: "1 / 1", objectFit: "cover", borderRadius: "50%", boxShadow: "0 5px 16px rgba(0,0,0,0.12)" },
  artisanName: { color: "#49352A", margin: "14px 0 8px" },
  artisanDetail: { color: "#725846", margin: "5px 0" },
  artItem: { width: "100%", minWidth: 0, height: "100%", textAlign: "center", transition: "transform 0.3s" },
  artImageWrapper: { width: "100%", aspectRatio: "1 / 1", overflow: "hidden", borderRadius: "15px", boxShadow: "0 6px 20px rgba(0,0,0,0.1)", transition: "transform 0.3s, box-shadow 0.3s" },
  artImg: { width: "100%", height: "100%", objectFit: "cover", transition: "transform 0.3s", cursor: "pointer" },
  artTitle: { marginTop: "10px", fontWeight: 600, color: "#5B4636" },

  mapSection: { marginBottom: "60px" },
  mapContainer: { display: "flex", justifyContent:"center" },

  newsletter: { textAlign:"center", marginBottom:"60px", padding:"32px 24px", background:"#F4E9DA", borderRadius:"20px", border:"1px solid #E9D7C1" },
  subscribeForm: { display:"flex", justifyContent:"center", gap:"15px", marginTop:"15px" },
  input: { padding:"12px", width:"280px", borderRadius:"10px", border:"1px solid #C2A57B" },
  subscribeButton: { padding:"12px 25px", backgroundColor:"#AD5433", color:"#fff", border:"none", borderRadius:"10px", cursor:"pointer", transition:"0.3s" },

  footer: { backgroundColor:"#EFE0CC", padding:"50px 20px", borderRadius:"25px", border:"1px solid #E4D0B8" },
  footerContent: { display:"flex", justifyContent:"space-between", flexWrap:"wrap", gap:"30px" },
  footerColumn: { flex:1, minWidth:"200px", marginBottom:"20px" },
  footerList: { listStyle:"none", padding:0, marginTop:"6px", lineHeight:1.8 },
  footerLink: { color:"#5B4636", textDecoration:"none" },
  socialIcons: { display:"flex", alignItems:"center", gap:"16px", marginTop:"8px" },
  socialIcon: { display:"inline-flex", alignItems:"center", justifyContent:"center", color:"#AD5433", fontSize:"22px", lineHeight:1 }
};

export default Dashboard;