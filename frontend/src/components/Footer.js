import React from "react";
import { useLanguage } from "../utils/LanguageContext";

const Footer = () => {
  const { t } = useLanguage();
  return (
    <footer>
      <h2>{t.brandName}</h2>
      <p>{t.aboutTagline}</p>
      <p>© 2025 Mittika | {t.reservedRights}</p>
      <div className="social-icons">
        <a href="#">🌐</a>
        <a href="#">📷</a>
        <a href="#">🐦</a>
        <a href="#">▶️</a>
      </div>
    </footer>
  );
};

export default Footer;
