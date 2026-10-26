import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../api";
import { useLanguage } from "../utils/LanguageContext";

const Signup = () => {
  const { t } = useLanguage();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [accountType, setAccountType] = useState("customer");
  const [location, setLocation] = useState("");
  const [experience, setExperience] = useState("");
  const [craft, setCraft] = useState("");
  const [profilePhoto, setProfilePhoto] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!name.trim() || !email.trim() || !password) {
      alert(t.pleaseFillFields);
      return;
    }

    try {
      setIsSubmitting(true);
      if (accountType === "artisan") {
        if (!location.trim() || !experience || !craft.trim() || !profilePhoto) {
          alert(t.pleaseFillArtisanFields);
          return;
        }
        const formData = new FormData();
        formData.append("name", name.trim());
        formData.append("email", email.trim());
        formData.append("password", password);
        formData.append("location", location.trim());
        formData.append("experience", experience);
        formData.append("craft", craft.trim());
        formData.append("profile_photo", profilePhoto);
        await API.post("/auth/artisan-signup", formData);
      } else {
        await API.post("/auth/signup", { name, email, password });
      }

      alert(t.accountCreated);
      navigate("/login");
    } catch (error) {
      console.error(error);

      if (error.response) {
        alert(error.response.data.detail || t.signupFailed);
      } else {
        alert(t.serverNotResponding);
      }
    } finally {
      setIsSubmitting(false);
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
            padding: clamp(1.5rem, 5vw, 3rem);
            border-radius: 1.5rem;
            box-shadow: 0 15px 35px rgba(0,0,0,0.15);
            width: 100%;
            max-width: 520px;
            box-sizing: border-box;
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

          .signup-page label {
            display: block;
            margin-bottom: 0.45rem;
          }

          .signup-page input,
          .signup-page select {
            display: block;
            width: 100%;
            min-width: 0;
            box-sizing: border-box;
            font: inherit;
          }

          .artisan-profile-fields {
            display: grid;
            grid-template-columns: minmax(0, 1fr);
            gap: 0.9rem;
            width: 100%;
            min-width: 0;
            margin: 0;
            padding: 1rem;
            box-sizing: border-box;
          }

          .artisan-profile-fields legend {
            padding: 0 0.4rem;
            font-weight: 600;
            color: #5b4636;
          }

          .artisan-profile-fields small {
            display: block;
            margin-top: 0.4rem;
            line-height: 1.5;
            color: #725846;
          }

          .artisan-profile-fields input[type="file"] {
            padding: 0.6rem;
          }

          @media (max-width: 480px) {
            .signup-page {
              align-items: flex-start;
            }

            .form-box {
              padding: 1.5rem 1.1rem;
            }
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
          <label htmlFor="signup-name">{t.fullName}</label>
          <input
            id="signup-name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />

          <label htmlFor="signup-email">{t.email}</label>
          <input
            id="signup-email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <label htmlFor="signup-password">{t.password}</label>
          <input
            id="signup-password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            minLength={8}
            required
          />

          <label htmlFor="account-type">{t.accountType}</label>
          <select
            id="account-type"
            value={accountType}
            onChange={(e) => setAccountType(e.target.value)}
            required
          >
            <option value="customer">{t.customer}</option>
            <option value="artisan">{t.artisan}</option>
          </select>

          {accountType === "artisan" && (
            <fieldset className="artisan-profile-fields" style={{ border: "1px solid #c9b89c", borderRadius: "0.75rem" }}>
              <legend>{t.artisanProfile}</legend>
              <label htmlFor="artisan-location">{t.artisanLocation}</label>
              <input
                id="artisan-location"
                type="text"
                value={location}
                onChange={(event) => setLocation(event.target.value)}
                maxLength={120}
                required
              />

              <label htmlFor="artisan-experience">{t.artisanExperience}</label>
              <input
                id="artisan-experience"
                type="number"
                min="0"
                max="80"
                step="1"
                value={experience}
                onChange={(event) => setExperience(event.target.value)}
                required
              />

              <label htmlFor="artisan-craft">{t.artisanCraft}</label>
              <input
                id="artisan-craft"
                type="text"
                value={craft}
                onChange={(event) => setCraft(event.target.value)}
                maxLength={120}
                required
              />

              <label htmlFor="artisan-photo">{t.artisanPhoto}</label>
              <input
                id="artisan-photo"
                type="file"
                accept="image/jpeg,image/png,image/webp"
                onChange={(event) => setProfilePhoto(event.target.files?.[0] || null)}
                required
              />
              <small>{t.artisanPhotoRequirements}</small>
            </fieldset>
          )}

          <button type="submit" className="primary" disabled={isSubmitting}>
            {isSubmitting ? t.creatingAccount : t.createAccount}
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