import React from "react";
import { Link } from "react-router-dom";
import { FaShoppingCart, FaHeart, FaCreditCard, FaMicrophone, FaBell, FaGlobe, FaStore } from "react-icons/fa";
import { translations } from "../utils/translations";

const Navbar = ({
  handleLogout,
  user,
  currentLang = 'en',
  setLang,
  openVoiceSearch,
  openNotifications,
}) => {
  const isLoggedIn = !!user;
  const canShop = ["customer", "artisan"].includes(user?.userType);
  const t = translations[currentLang] || translations.en;

  return (
    <nav className="main-nav" style={styles.nav}>
      {/* Brand Logo & Tagline */}
      <div className="nav-brand" style={styles.brandGroup}>
        <Link to="/" style={styles.brandLink}>
          <span style={styles.brandName}>{t.brandName}</span>
          <span style={styles.brandTagline}>{t.brandTagline}</span>
        </Link>
      </div>

      {/* Main Nav Links */}
      <div className="nav-links" style={styles.navLinks}>
        <Link to="/">{t.navHome}</Link>
        <Link to="/about">{t.navAbout}</Link>
        <Link to="/jewellery">{t.navJewellery}</Link>
        <Link to="/rukhwat">{t.navRukhwat}</Link>
        <Link to="/pottery">{t.navPottery}</Link>
        <Link to="/spiritualcorner">{t.navSpiritual}</Link>
        <Link to="/candle">{t.navCandle}</Link>
        <Link to="/home">{t.navHomeStyling}</Link>
      </div>

      {/* Controls & Quick Actions */}
      <div className="nav-controls" style={styles.controlsGroup}>
        {isLoggedIn && (
          <button
            style={styles.micBtn}
            onClick={openVoiceSearch}
            title={t.voiceSearchTooltip}
          >
            <FaMicrophone style={styles.micIcon} />
            <span style={styles.micText}>{t.voiceSearch}</span>
          </button>
        )}

        {/* Language Picker Dropdown */}
        <div style={styles.langPickerBox}>
          <FaGlobe style={{ color: '#AD5433', marginRight: 4 }} />
          <select
            value={currentLang}
            onChange={(e) => setLang && setLang(e.target.value)}
            style={styles.langSelect}
          >
            <option value="en">English (EN)</option>
            <option value="hi">हिंदी (Hindi)</option>
            <option value="mr">मराठी (Marathi)</option>
          </select>
        </div>

        {/* AI Notification Bell */}
        <button style={styles.notifBellBtn} onClick={openNotifications} title={t.notifications}>
          <FaBell />
          <span style={styles.notifBadge}>3</span>
        </button>

        {canShop && (
          <div style={styles.iconRow}>
            <Link to="/cart" style={styles.iconLink} title={t.yourCart}><FaShoppingCart /></Link>
            <Link to="/wishlist" style={styles.iconLink} title={t.wishlist}><FaHeart /></Link>
            <Link to="/checkout" style={styles.iconLink} title={t.checkout}><FaCreditCard /></Link>
          </div>
        )}
        {user?.userType === "artisan" && (
          <Link to="/artisan" style={styles.artisanLink}><FaStore /> {t.roleArtisan}</Link>
        )}

        {/* Auth Actions */}
        {!isLoggedIn ? (
          <div style={styles.authGroup}>
            <Link to="/login" style={styles.authBtn}>{t.navLogin}</Link>
            <Link to="/signup" style={styles.authPrimaryBtn}>{t.navSignup}</Link>
          </div>
        ) : (
          <button onClick={handleLogout} style={styles.logoutBtn}>
            {t.navLogout}
          </button>
        )}
      </div>
    </nav>
  );
};

const styles = {
  nav: {
    backgroundColor: '#FFFDF9',
    borderBottom: '1px solid #EADCCB',
    padding: '12px clamp(16px, 2.5vw, 32px)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    flexWrap: 'wrap',
    gap: '10px 20px',
    position: 'sticky',
    top: 0,
    zIndex: 1000,
    boxShadow: '0 6px 20px rgba(74, 48, 34, 0.08)'
  },
  brandGroup: {
    display: 'flex',
    flexDirection: 'column'
  },
  brandLink: {
    textDecoration: 'none',
    display: 'flex',
    flexDirection: 'column'
  },
  brandName: {
    fontSize: '1.45rem',
    fontWeight: '800',
    color: '#A94F2F',
    letterSpacing: '0.5px'
  },
  brandTagline: {
    fontSize: '0.68rem',
    color: '#725846',
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: '0.8px'
  },
  navLinks: {
    display: 'flex',
    flex: '1 1 480px',
    minWidth: 0,
    flexWrap: 'wrap',
    justifyContent: 'center',
    alignItems: 'center',
    gap: '8px 16px',
    fontSize: '0.86rem',
    fontWeight: '600'
  },
  controlsGroup: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'flex-end',
    flexWrap: 'wrap',
    gap: '8px 12px'
  },
  micBtn: {
    backgroundColor: '#AD5433',
    color: '#FFF',
    border: 'none',
    borderRadius: '20px',
    padding: '6px 14px',
    fontSize: '0.82rem',
    fontWeight: '700',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    boxShadow: '0 3px 10px rgba(173, 84, 51, 0.24)'
  },
  micIcon: {
    fontSize: '13px'
  },
  micText: {
    display: 'inline'
  },
  langPickerBox: {
    display: 'flex',
    alignItems: 'center',
    backgroundColor: '#FFF',
    border: '1px solid #E4D3C0',
    borderRadius: '16px',
    padding: '3px 8px'
  },
  langSelect: {
    border: 'none',
    background: 'transparent',
    fontSize: '0.8rem',
    color: '#49352A',
    fontWeight: '600',
    cursor: 'pointer',
    outline: 'none'
  },
  artisanLink: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    color: '#49352A',
    textDecoration: 'none',
    fontWeight: '700',
    fontSize: '0.82rem'
  },
  notifBellBtn: {
    position: 'relative',
    backgroundColor: '#FFF',
    border: '1px solid #E4D3C0',
    borderRadius: '50%',
    width: '34px',
    height: '34px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: '#49352A',
    cursor: 'pointer'
  },
  notifBadge: {
    position: 'absolute',
    top: '-4px',
    right: '-4px',
    backgroundColor: '#AD5433',
    color: '#FFF',
    borderRadius: '50%',
    width: '16px',
    height: '16px',
    fontSize: '10px',
    fontWeight: 'bold',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  },
  iconRow: {
    display: 'flex',
    gap: '10px',
    fontSize: '16px',
    color: '#49352A'
  },
  iconLink: {
    color: '#49352A',
    textDecoration: 'none'
  },
  authGroup: {
    display: 'flex',
    gap: '8px'
  },
  authBtn: {
    padding: '5px 12px',
    color: '#362417',
    textDecoration: 'none',
    fontWeight: '600',
    fontSize: '0.82rem'
  },
  authPrimaryBtn: {
    padding: '5px 14px',
    backgroundColor: '#49352A',
    color: '#FFF',
    borderRadius: '16px',
    textDecoration: 'none',
    fontWeight: '600',
    fontSize: '0.82rem'
  },
  logoutBtn: {
    backgroundColor: '#8C6047',
    color: '#FFF',
    border: 'none',
    padding: '5px 12px',
    borderRadius: '16px',
    fontSize: '0.82rem',
    cursor: 'pointer'
  }
};

export default Navbar;