import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import Navbar from './components/Navbar';
import Jewellery from './components/Jewellery';
import Pottery from './components/Pottery';
import Rukhwat from './components/Rukhwat';
import SpiritualCorner from './components/SpiritualCorner';
import Candle from './components/Candle';
import Dashboard from './components/Dashboard';
import ArtisanDashboard from './components/ArtisanDashboard';
import VoiceSearchModal from './components/VoiceSearchModal';
import NotificationDrawer from './components/NotificationDrawer';
import Login from './components/Login';
import Signup from './components/Signup';
import Cart from './components/Cart';
import Wishlist from './components/Wishlist';
import About from './components/About';
import Shop from './components/Shop';
import Home from './components/Home';
import ProtectedRoute from './components/ProtectedRoute';
import Footer from './components/Footer';
import DummyPayment from "./components/DummyPayment";

import API from "./api";
import { LanguageContext } from "./utils/LanguageContext";
import './App.css';

function App() {
  const [user, setUser] = useState(null);

  // Global Interactive Modals & Language/Role State
  const [currentLang, setCurrentLang] = useState(() => {
    const storedLanguage = localStorage.getItem("mittika_language");
    return ["en", "hi", "mr"].includes(storedLanguage) ? storedLanguage : "en";
  });
  const [isVoiceOpen, setIsVoiceOpen] = useState(false);
  const [isNotifOpen, setIsNotifOpen] = useState(false);
  const [voiceSearchQuery, setVoiceSearchQuery] = useState('');
  const canShop = ["customer", "artisan"].includes(user?.userType);

  const setLang = (language) => {
    if (!["en", "hi", "mr"].includes(language)) return;
    localStorage.setItem("mittika_language", language);
    setCurrentLang(language);
  };

  useEffect(() => {
    let active = true;
    const token = localStorage.getItem("token");

    if (!token) {
      localStorage.removeItem("user");
      setUser(null);
      return () => { active = false; };
    }

    API.get("/auth/me")
      .then((res) => {
        if (!active) return;
        setUser(res.data.user);
        localStorage.setItem("user", JSON.stringify(res.data.user));
      })
      .catch(() => {
        if (!active) return;
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        setUser(null);
      });

    return () => { active = false; };
  }, []);

  useEffect(() => {
    const invalidateSession = () => {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      setUser(null);
    };
    window.addEventListener("mittika:unauthorized", invalidateSession);
    return () => window.removeEventListener("mittika:unauthorized", invalidateSession);
  }, []);

  const addToCart = async (product) => {
    if (!user) {
      alert("Please login first");
      return false;
    }
    if (!canShop) return false;

    try {
      const price = Number(String(product.price ?? "").replace(/[^\d.-]/g, ""));
      await API.post("/cart", {
        productId: String(product._id || product.id || product.title || product.name),
        title: product.title || product.name,
        price,
        image: product.image || product.img || "",
        quantity: 1
      });
      return true;
    } catch (err) {
      console.error(err);
      alert("Error adding to cart");
      return false;
    }
  };

  const addToWishlist = async (product) => {
    if (!user) {
      alert("Please login first");
      return false;
    }
    if (!canShop) return false;

    try {
      const price = Number(String(product.price ?? "").replace(/[^\d.-]/g, ""));
      await API.post("/wishlist", {
        productId: String(product._id || product.id || product.title || product.name),
        title: product.title || product.name,
        price,
        image: product.image || product.img || ""
      });
      return true;
    } catch (err) {
      console.error(err);
      alert("Error adding to wishlist");
      return false;
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("user");
    localStorage.removeItem("token");
    setUser(null);
  };

  const handleVoiceSearchSubmit = (query) => {
    setVoiceSearchQuery(query);
    console.log("Voice Search Triggered:", query);
  };

  return (
    <Router>
      <LanguageContext.Provider value={currentLang}>
        <>
        <Navbar
          user={user}
          handleLogout={handleLogout}
          currentLang={currentLang}
          setLang={setLang}
          openVoiceSearch={() => setIsVoiceOpen(true)}
          openNotifications={() => setIsNotifOpen(true)}
        />

        <Routes>
          <Route path="/" element={<Dashboard voiceSearchQuery={voiceSearchQuery} />} />
          <Route path="/login" element={<Login setUser={setUser} />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/about" element={<About />} />

          {/* Protected Product Categories */}
          <Route path="/jewellery" element={<ProtectedRoute user={user}><Jewellery addToCart={canShop ? addToCart : undefined} addToWishlist={canShop ? addToWishlist : undefined} /></ProtectedRoute>} />
          <Route path="/pottery" element={<ProtectedRoute user={user}><Pottery addToCart={canShop ? addToCart : undefined} addToWishlist={canShop ? addToWishlist : undefined} /></ProtectedRoute>} />
          <Route path="/rukhwat" element={<ProtectedRoute user={user}><Rukhwat addToCart={canShop ? addToCart : undefined} addToWishlist={canShop ? addToWishlist : undefined} /></ProtectedRoute>} />
          <Route path="/spiritualcorner" element={<ProtectedRoute user={user}><SpiritualCorner addToCart={canShop ? addToCart : undefined} addToWishlist={canShop ? addToWishlist : undefined} /></ProtectedRoute>} />
          <Route path="/candle" element={<ProtectedRoute user={user}><Candle addToCart={canShop ? addToCart : undefined} addToWishlist={canShop ? addToWishlist : undefined} /></ProtectedRoute>} />
          <Route path="/home" element={<ProtectedRoute user={user}><Home addToCart={canShop ? addToCart : undefined} addToWishlist={canShop ? addToWishlist : undefined} /></ProtectedRoute>} />

          <Route path="/cart" element={<ProtectedRoute user={user} requiredRole={["customer", "artisan"]}><Cart user={user} /></ProtectedRoute>} />
          <Route path="/wishlist" element={<ProtectedRoute user={user} requiredRole={["customer", "artisan"]}><Wishlist user={user} addToCart={addToCart} /></ProtectedRoute>} />
          <Route path="/checkout" element={<ProtectedRoute user={user} requiredRole={["customer", "artisan"]}><DummyPayment user={user} /></ProtectedRoute>} />

          <Route path="/artisan" element={<ProtectedRoute user={user} requiredRole="artisan"><ArtisanDashboard user={user} handleLogout={handleLogout} /></ProtectedRoute>} />
          <Route path="/customer" element={<ProtectedRoute user={user} requiredRole="customer"><Dashboard /></ProtectedRoute>} />

          <Route path="/shop" element={<Shop addToCart={addToCart} addToWishlist={addToWishlist} user={user} voiceSearchQuery={voiceSearchQuery} clearVoiceSearch={() => setVoiceSearchQuery("")} />} />
        </Routes>

        {/* Global Interactive Overlay Modals */}
        <VoiceSearchModal
          isOpen={isVoiceOpen}
          onClose={() => setIsVoiceOpen(false)}
          onSearch={handleVoiceSearchSubmit}
          currentLang={currentLang}
        />

        <NotificationDrawer
          isOpen={isNotifOpen}
          onClose={() => setIsNotifOpen(false)}
          role={user?.userType || "customer"}
        />

        <Footer />
        </>
      </LanguageContext.Provider>
    </Router>
  );
}

export default App;