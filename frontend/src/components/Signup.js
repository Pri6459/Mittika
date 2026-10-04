import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../api"; // ✅ connect backend
import { useLanguage } from "../utils/LanguageContext";

const Signup = () => {
  const { t } = useLanguage();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [accountType, setAccountType] = useState("customer");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!name || !email || !password) {
      alert(t.pleaseFillFields);
      return;
    }

    try {
      // ✅ Call FastAPI backend
      await API.post(accountType === "artisan" ? "/auth/artisan-signup" : "/auth/signup", {
        name,
        email,
        password,
      });

      alert(t.accountCreated);
      navigate("/login");
    } catch (error) {
      console.error(error);

      if (error.response) {
        alert(error.response.data.detail || t.signupFailed);
      } else {
        alert(t.serverNotResponding);
      }
    }
  };

  return (
    <div className="signup-page">
      <style>
        {`
          @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

          body, html {
            margin: 0;
            padding: 0;
            font-family: 'Inter', sans-serif;
          }

          .signup-page {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            background: linear-gradient(135deg, #f0e6dc, #d4c2a8);
            padding: 1rem;
          }

          .form-box {
            background: #fffdf7;
            padding: 3rem 2.5rem;
            border-radius: 1.5rem;
            box-shadow: 0 15px 35px rgba(0,0,0,0.15);
            width: 100%;
            max-width: 450px;
          }

          h2 {
            text-align: center;
            color: #6b4c3b;
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 2rem;
          }

          form {
            display: flex;
            flex-direction: column;
            gap: 1.2rem;
          }

          label {
            font-weight: 500;
            color: #5b4636;
          }

          input, select {
            padding: 0.75rem;
            border-radius: 0.75rem;
            border: 1px solid #c9b89c;
          }

          button.primary {
            background-color: #a67852;
            color: white;
            padding: 0.85rem;
            border-radius: 0.75rem;
            border: none;
            cursor: pointer;
          }

          button.secondary {
            margin-top: 10px;
            background: transparent;
            border: 2px solid #a67852;
            color: #a67852;
            padding: 0.85rem;
            border-radius: 0.75rem;
            cursor: pointer;
          }
        `}
      </style>

      <div className="form-box">
        <h2>{t.createAccount}</h2>

        <form onSubmit={handleSubmit}>
          <label>{t.fullName}</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />

          <label>{t.email}</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <label>{t.password}</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <label>{t.accountType}</label>
          <select
            value={accountType}
            onChange={(e) => setAccountType(e.target.value)}
          >
            <option value="customer">{t.customer}</option>
            <option value="artisan">{t.artisan}</option>
          </select>

          <button type="submit" className="primary">
            {t.createAccount}
          </button>

          <button
            type="button"
            className="secondary"
            onClick={() => navigate("/login")}
          >
            {t.alreadyHaveAccount}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Signup;