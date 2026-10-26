import React from "react";
import { useLanguage } from "../utils/LanguageContext";

const Footer = () => {
  const { t } = useLanguage();
  return (
    <footer className="site-footer">
      <div className="site-footer-content">
        <h2>{t.brandName}</h2>
        <p>{t.aboutTagline}</p>
        <p className="site-footer-copyright">© 2025 Mittika | {t.reservedRights}</p>
        <div className="site-footer-socials" aria-label={t.followUs}>
          <span role="img" aria-label="Website">🌐</span>
          <span role="img" aria-label="Instagram">📷</span>
          <span role="img" aria-label="Twitter">🐦</span>
          <span role="img" aria-label="YouTube">▶️</span>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
