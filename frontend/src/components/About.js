import React from "react";
import { useLanguage } from "../utils/LanguageContext";

const Dashboard = () => {
  const { t } = useLanguage();
  return (
    <>
      <style>{`
        :root {
          --primary: #8b4513;
          --secondary: #f9c74f;
          --accent: #ff6f61;
          --light: #fffaf5;
          --dark: #2f2f2f;
          --gradient: linear-gradient(135deg, #8b4513, #ff6f61);
        }

        body {
          font-family: "Poppins", sans-serif;
          margin: 0;
          padding: 0;
          background: var(--light);
          color: var(--dark);
          line-height: 1.7;
          overflow-x: hidden;
        }

        /* Navbar */
        nav {
          background: rgba(139, 69, 19, 0.95);
          backdrop-filter: blur(10px);
          color: white;
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 18px 60px;
          position: sticky;
          top: 0;
          z-index: 1000;
          border-bottom: 2px solid rgba(255, 255, 255, 0.2);
        }
        nav .logo {
          font-size: 1.8rem;
          font-weight: 700;
          letter-spacing: 1px;
        }
        nav ul {
          list-style: none;
          display: flex;
          gap: 35px;
          margin: 0;
          padding: 0;
        }
        nav ul li a {
          color: white;
          text-decoration: none;
          font-weight: 500;
          position: relative;
          transition: color 0.3s;
        }
        nav ul li a::after {
          content: "";
          position: absolute;
          width: 0;
          height: 2px;
          background: var(--secondary);
          left: 0;
          bottom: -6px;
          transition: width 0.3s;
        }
        nav ul li a:hover {
          color: var(--secondary);
        }
        nav ul li a:hover::after {
          width: 100%;
        }

        /* Hero */
        header {
          background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)),
            url('about-bg.jpg') center/cover no-repeat fixed;
          color: white;
          text-align: center;
          padding: 140px 20px;
          animation: fadeIn 1.5s ease-in;
        }
        header h1 {
          font-size: 3.5rem;
          margin: 0;
          font-weight: 800;
        }
        header p {
          font-size: 1.3rem;
          max-width: 700px;
          margin: 20px auto;
          opacity: 0.9;
        }

        /* Buttons */
        .btn {
          display: inline-block;
          background: var(--gradient);
          color: white;
          padding: 12px 26px;
          border-radius: 30px;
          font-weight: 600;
          text-decoration: none;
          box-shadow: 0px 4px 15px rgba(0,0,0,0.2);
          position: relative;
          overflow: hidden;
          transition: transform 0.3s, box-shadow 0.3s;
        }
        .btn:hover {
          transform: scale(1.07);
          box-shadow: 0px 6px 20px rgba(0,0,0,0.3);
        }

        /* Container & Headings */
        .container { width: 90%; max-width: 1200px; margin: auto; padding: 70px 20px; }
        h2 {
          color: var(--primary);
          font-size: 2.4rem;
          margin-bottom: 15px;
          position: relative;
        }
        h2::after {
          content: "";
          width: 60px;
          height: 4px;
          background: var(--accent);
          display: block;
          margin-top: 8px;
          border-radius: 2px;
        }

        /* Section Split */
        .section-split {
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 50px;
          margin-bottom: 80px;
        }
        .section-split div { flex: 1; }
        .section-split img {
          width: 45%;
          border-radius: 18px;
          box-shadow: 0px 12px 25px rgba(0,0,0,0.15);
        }

        /* Cards */
        .grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
          gap: 30px;
        }
        .card {
          background: white;
          padding: 22px;
          border-radius: 16px;
          box-shadow: 0px 8px 18px rgba(0,0,0,0.1);
          text-align: center;
          border: 2px solid transparent;
        }
        .card img {
          width: 100%;
          border-radius: 12px;
          margin-bottom: 15px;
          height: 230px;
          object-fit: cover;
        }

        /* Stats */
        .numbers {
          background: var(--gradient);
          color: white;
          padding: 70px 20px;
          border-radius: 20px;
          margin-top: 70px;
        }
        .stats {
          display: flex;
          flex-wrap: wrap;
          justify-content: space-around;
          gap: 25px;
          text-align: center;
        }
        .stat { flex: 1 1 220px; padding: 30px; }
        .stat h3 { font-size: 2.5rem; margin: 0; color: var(--secondary); }

        /* Artisan */
        .artisan-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 25px;
          text-align: center;
        }
        .artisan-card {
          background: white;
          border-radius: 16px;
          padding: 22px;
          box-shadow: 0 8px 18px rgba(0,0,0,0.15);
        }
        .artisan-card img {
          width: 100%;
          height: 230px;
          object-fit: cover;
          border-radius: 12px;
          margin-bottom: 15px;
        }
        .artisan-card h3 { margin: 10px 0; color: var(--primary); }

        /* Footer */
        footer {
          text-align: center;
          background: var(--dark);
          color: white;
          padding: 35px 20px;
          margin-top: 80px;
        }
        footer a { color: var(--secondary); text-decoration: none; font-weight: 500; }

        /* Animations */
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(40px); }
          to { opacity: 1; transform: translateY(0); }
        }

        @media (max-width: 900px) {
          .section-split { flex-direction: column; text-align: center; }
          .section-split img { width: 100%; }
          header h1 { font-size: 2.5rem; }
        }
      `}</style>

  

      {/* Hero */}
      <header>
        <h1>{t.aboutUs}</h1>
        <p>{t.aboutIntro}</p>
      </header>

      <main>
        <div className="container">
          {/* Mission */}
          <section className="section-split">
            <div>
              <h2>{t.ourMission}</h2>
              <p>{t.missionDescription}</p>
              <a href="/shop" className="btn">{t.exploreProducts}</a>
            </div>
            <img src="smile.jpg" alt={t.ourMission} />
          </section>

          {/* Story */}
          <section className="section-split" style={{background:"#fff8f2", padding:"40px", borderRadius:"12px"}}>
            <img src="story.jpg" alt={t.ourStory} />
            <div>
              <h2>{t.ourStory}</h2>
              <p>{t.storyDescriptionOne}</p>
              <p>{t.storyDescriptionTwo}</p>
            </div>
          </section>

          {/* Crafts */}
          <section>
            <h2>{t.meetCrafts}</h2>
            <div className="grid">
              <div className="card">
                <img src="madhu.jpg" alt={t.madhubaniArt} />
                <h3>{t.madhubaniArt}</h3>
                <p>{t.madhubaniDescription}</p>
              </div>
              <div className="card">
                <img src="blue.jpg" alt={t.bluePottery} />
                <h3>{t.bluePottery}</h3>
                <p>{t.bluePotteryDescription}</p>
              </div>
              <div className="card">
                <img src="chan.jpg" alt={t.channapatnaToys} />
                <h3>{t.channapatnaToys}</h3>
                <p>{t.channapatnaDescription}</p>
              </div>
            </div>
          </section>

          {/* Artisans */}
          <section>
            <h2>{t.meetArtisans}</h2>
            <div className="artisan-grid">
              <div className="artisan-card">
                <img src="mp.jpg" alt="Artisan 1" />
                <h3>Ramesh Kumar</h3>
                <p>{t.artisanRameshDescription}</p>
              </div>
              <div className="artisan-card">
                <img src="bp.jpg" alt="Artisan 2" />
                <h3>Sunita Devi</h3>
                <p>{t.artisanSunitaDescription}</p>
              </div>
              <div className="artisan-card">
                <img src="cp.jpg" alt="Artisan 3" />
                <h3>Abdul Rahman</h3>
                <p>{t.artisanAbdulDescription}</p>
              </div>
            </div>
          </section>

          {/* Stats */}
          <section className="numbers">
            <h2>{t.ourImpact}</h2>
            <div className="stats">
              <div className="stat">
                <h3>7M+</h3>
                <p>{t.indianArtisans}</p>
              </div>
              <div className="stat">
                <h3>3,000+</h3>
                <p>{t.traditionsPreserved}</p>
              </div>
              <div className="stat">
                <h3>100+</h3>
                <p>{t.countriesReached}</p>
              </div>
              <div className="stat">
                <h3>1M+</h3>
                <p>{t.handmadeProductsSold}</p>
              </div>
            </div>
          </section>
        </div>
      </main>

      <footer>
        <p>&copy; 2025 Indian Handicrafts | <a href="/">{t.backHome}</a></p>
      </footer>
    </>
  );
};

export default Dashboard;
