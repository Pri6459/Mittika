import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../api";
import { useLanguage } from "../utils/LanguageContext";

const Login = ({ setUser }) => {
  const { t } = useLanguage();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!email || !password) {
      alert(t.pleaseFillFields);
      return;
    }

    try {
      // 🔥 Call backend login API
      const res = await API.post("/auth/login", {
        email,
        password,
      });

      // ✅ Save token + user separately
      localStorage.setItem("token", res.data.token);
      localStorage.setItem("user", JSON.stringify(res.data.user));

      // ✅ VERY IMPORTANT FIX (only user)
      setUser(res.data.user);

      alert(t.loginSuccessful);

      // 🔥 Redirect based on role
      navigate(res.data.user.userType === "artisan" ? "/artisan" : "/");

    } catch (error) {
      console.error(error);

      if (error.response) {
        alert(error.response.data.detail || t.loginFailed);
      } else {
        alert(t.serverNotResponding);
      }
    }
  };

  return (
    <div className="login-page">
      <style>
        {`
          @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

          body, html {
            margin: 0;
            padding: 0;
            font-family: 'Inter', sans-serif;
          }

          .login-page {
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
            max-width: 420px;
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

          input {
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
        <h2>{t.login}</h2>

        <form onSubmit={handleSubmit}>
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

          <button type="submit" className="primary">
            {t.signIn}
          </button>

          <button
            type="button"
            className="secondary"
            onClick={() => navigate("/signup")}
          >
            {t.createAccount}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;