import React from "react";
import { Link, useNavigate } from "react-router-dom";

const Layout = ({ children }) => {
  const navigate = useNavigate();

  const handleShopClick = () => {
    const isLoggedIn = localStorage.getItem("isLoggedIn") === "true";

    if (!isLoggedIn) {
      alert("Please login to access the shop");
      navigate("/login");
    } else {
      navigate("/shop");
    }
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      {/* Navbar */}
      <nav style={{ background: "#333", color: "white", padding: "15px 30px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <Link to="/" style={{ fontSize: "22px", fontWeight: "bold", color: "white", textDecoration: "none" }}>
            Mittika
          </Link>

          <div style={{ display: "flex", gap: "20px" }}>
            <Link to="/about" style={{ color: "white", textDecoration: "none" }}>About Us</Link>
            <Link to="/" style={{ color: "white", textDecoration: "none" }}>Home</Link>
          </div>

          <div style={{ display: "flex", gap: "10px" }}>
            <button
              onClick={() => navigate("/signup")}
              style={{ background: "transparent", border: "1px solid white", color: "white", padding: "6px 12px", cursor: "pointer" }}
            >
              Sign Up
            </button>
            <button
              onClick={() => navigate("/login")}
              style={{ background: "transparent", border: "1px solid white", color: "white", padding: "6px 12px", cursor: "pointer" }}
            >
              Login
            </button>
          </div>
        </div>
      </nav>

      {/* Page Content */}
      <div style={{ flex: 1 }}>{children}</div>

      {/* Footer */}
      <footer style={{ background: "#f5f5f5", padding: "40px 20px", marginTop: "40px" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: "30px" }}>
          <div>
            <h4>About Company</h4>
            <p><Link to="/about">About us</Link></p>
            <p><a href="#">Reviews</a></p>
            <p><a href="#">Blog</a></p>
            <p><a href="#">FAQs</a></p>
          </div>

          <div>
            <h4>Customer Service</h4>
            <p><a href="#">Track Order</a></p>
            <p><a href="#">Privacy Policy</a></p>
            <p><a href="#">Shipping & Returns</a></p>
            <p><a href="#">Contact Us</a></p>
          </div>

          <div>
            <h4>Get in touch</h4>
            <p>+91 10101010</p>
            <h5>Follow us</h5>
            <div style={{ display: "flex", gap: "15px" }}>
              <a href="#">Instagram</a>
              <a href="#">Facebook</a>
              <a href="#">Twitter</a>
            </div>
          </div>
        </div>

        <div style={{ marginTop: "30px", textAlign: "center", borderTop: "1px solid #ddd", paddingTop: "20px" }}>
          <p>
            A marketplace where <strong>artisans</strong> can share their craft directly,
            and <strong>customers</strong> can find unique pieces with a story.
          </p>
          <p style={{ marginTop: "10px", fontStyle: "italic", color: "#333" }}>
            Mittika: Bringing the soul of the earth to your home.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
