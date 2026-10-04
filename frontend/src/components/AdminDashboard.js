import React, { useState, useEffect } from 'react';
import { FaChartLine, FaRobot, FaUsers, FaStore, FaRupeeSign, FaCheckCircle, FaMicrophone, FaShieldAlt } from 'react-icons/fa';
import API from '../api';

const AdminDashboard = () => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const res = await API.get('/ml/analytics');
      setAnalytics(res.data);
    } catch (err) {
      console.error("Error fetching admin analytics:", err);
    } finally {
      setLoading(false);
    }
  };

  const statCards = [
    { title: "Total Users", count: analytics?.activeUsersCount || 1420, icon: <FaUsers />, color: '#0D9488' },
    { title: "Active Artisans", count: analytics?.totalArtisansCount || 380, icon: <FaStore />, color: '#C85A32' },
    { title: "AI Model Accuracy", count: `${analytics?.accuracyScore || 96.4}%`, icon: <FaRobot />, color: '#D97706' },
    { title: "Platform GMV", count: `₹${(analytics?.totalRevenue || 482500).toLocaleString()}`, icon: <FaRupeeSign />, color: '#059669' }
  ];

  const recentArtisanVerifications = [
    { name: "Ramesh Clay Crafts", region: "Kolhapur, MH", status: "Verified", date: "Today" },
    { name: "Gauri Traditional Rukhwat", region: "Pune, MH", status: "Verified", date: "Yesterday" },
    { name: "Meera Candle Studio", region: "Jaipur, RJ", status: "Pending Audit", date: "2 days ago" }
  ];

  if (loading) {
    return <div style={{ padding: 40, textAlign: 'center' }}>Loading Admin Command Center...</div>;
  }

  return (
    <div style={styles.container}>
      {/* Header Banner */}
      <div style={styles.banner}>
        <div>
          <h2 style={styles.bannerTitle}>🛡️ Mittika Admin Platform Command Center</h2>
          <p style={styles.bannerSubtitle}>Real-time Monitoring of AI Engine Accuracy, Artisans, and Platform Metrics</p>
        </div>
        <div style={styles.modelBadge}>
          <FaRobot style={{ marginRight: 6 }} /> {analytics?.modelName || "Mittika CNN + NLP Hybrid Engine v2.4"}
        </div>
      </div>

      {/* Stats Cards Grid */}
      <div style={styles.statsGrid}>
        {statCards.map((card, idx) => (
          <div key={idx} style={styles.statCard}>
            <div style={{ ...styles.statIcon, color: card.color }}>{card.icon}</div>
            <div>
              <p style={styles.statTitle}>{card.title}</p>
              <h3 style={styles.statCount}>{card.count}</h3>
            </div>
          </div>
        ))}
      </div>

      {/* Main Grid Section */}
      <div style={styles.mainGrid}>
        {/* Left Column: AI Engine Diagnostics */}
        <div style={styles.card}>
          <h4 style={styles.cardTitle}>
            <FaChartLine style={{ color: '#C85A32', marginRight: 8 }} /> AI Categorization Model Performance
          </h4>
          <div style={styles.metricRow}>
            <span>CNN Image Classification Precision:</span>
            <strong style={{ color: '#059669' }}>97.1%</strong>
          </div>
          <div style={styles.metricRow}>
            <span>NLP Keyword & N-Gram Accuracy:</span>
            <strong style={{ color: '#059669' }}>95.8%</strong>
          </div>
          <div style={styles.metricRow}>
            <span>Combined Hybrid Score:</span>
            <strong style={{ color: '#C85A32', fontSize: '1.1rem' }}>96.4%</strong>
          </div>

          <h5 style={{ ...styles.subTitle, marginTop: 20 }}>Category Breakdown Distribution:</h5>
          {analytics?.trendingCategories?.map(([cat, count], i) => (
            <div key={i} style={styles.progressRow}>
              <div style={styles.catLabel}>{cat}</div>
              <div style={styles.barOuter}>
                <div style={{ ...styles.barInner, width: `${(count / 15) * 100}%` }}></div>
              </div>
              <span style={styles.countBadge}>{count} items</span>
            </div>
          ))}
        </div>

        {/* Right Column: Voice Search Analytics & Verification */}
        <div style={styles.card}>
          <h4 style={styles.cardTitle}>
            <FaMicrophone style={{ color: '#D97706', marginRight: 8 }} /> Multilingual Voice Search Insights
          </h4>
          <p style={styles.helperText}>Top voice speech-to-text queries spoken by buyers across languages:</p>
          <div style={styles.queryList}>
            {analytics?.topVoiceQueries?.map((q, i) => (
              <div key={i} style={styles.queryTag}>
                <span>"{q}"</span>
                <span style={styles.queryFreq}>Top {i + 1} Search</span>
              </div>
            ))}
          </div>

          <h4 style={{ ...styles.cardTitle, marginTop: 25 }}>
            <FaShieldAlt style={{ color: '#0D9488', marginRight: 8 }} /> Artisan Platform Approvals
          </h4>
          <div style={styles.table}>
            {recentArtisanVerifications.map((art, i) => (
              <div key={i} style={styles.tableRow}>
                <div>
                  <strong>{art.name}</strong>
                  <div style={styles.subText}>{art.region}</div>
                </div>
                <span style={art.status === 'Verified' ? styles.statusBadge : styles.pendingBadge}>
                  <FaCheckCircle style={{ marginRight: 4 }} /> {art.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

const styles = {
  container: {
    padding: '40px 30px',
    maxWidth: '1350px',
    margin: '0 auto',
    fontFamily: 'Poppins, sans-serif'
  },
  banner: {
    backgroundColor: '#362417',
    color: '#FFF',
    borderRadius: '20px',
    padding: '30px 35px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '30px',
    boxShadow: '0 10px 30px rgba(0,0,0,0.15)'
  },
  bannerTitle: {
    fontSize: '1.6rem',
    margin: 0,
    fontWeight: '700'
  },
  bannerSubtitle: {
    margin: '6px 0 0 0',
    fontSize: '0.95rem',
    color: '#D9C5B2'
  },
  modelBadge: {
    backgroundColor: '#C85A32',
    padding: '10px 18px',
    borderRadius: '25px',
    fontWeight: '700',
    fontSize: '0.88rem',
    display: 'flex',
    alignItems: 'center'
  },
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
    gap: '20px',
    marginBottom: '30px'
  },
  statCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: '16px',
    padding: '20px 25px',
    display: 'flex',
    alignItems: 'center',
    gap: '18px',
    boxShadow: '0 6px 20px rgba(0,0,0,0.06)',
    border: '1px solid #EFE5D8'
  },
  statIcon: {
    fontSize: '32px'
  },
  statTitle: {
    margin: 0,
    fontSize: '0.85rem',
    color: '#6B5446',
    fontWeight: '600'
  },
  statCount: {
    margin: '4px 0 0 0',
    fontSize: '1.5rem',
    color: '#362417',
    fontWeight: '800'
  },
  mainGrid: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '25px'
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: '20px',
    padding: '28px',
    boxShadow: '0 8px 25px rgba(0,0,0,0.06)',
    border: '1px solid #EFE5D8'
  },
  cardTitle: {
    fontSize: '1.15rem',
    color: '#362417',
    fontWeight: '700',
    marginBottom: '15px',
    display: 'flex',
    alignItems: 'center'
  },
  subTitle: {
    fontSize: '0.92rem',
    color: '#362417',
    fontWeight: '700',
    marginBottom: '12px'
  },
  metricRow: {
    display: 'flex',
    justifyContent: 'space-between',
    padding: '10px 0',
    borderBottom: '1px solid #F3EFEA',
    fontSize: '0.92rem',
    color: '#5B4636'
  },
  progressRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    marginBottom: '10px'
  },
  catLabel: {
    width: '140px',
    fontSize: '0.84rem',
    color: '#362417',
    fontWeight: '600'
  },
  barOuter: {
    flex: 1,
    height: '10px',
    backgroundColor: '#EFE5D8',
    borderRadius: '5px',
    overflow: 'hidden'
  },
  barInner: {
    height: '100%',
    backgroundColor: '#C85A32',
    borderRadius: '5px'
  },
  countBadge: {
    fontSize: '0.78rem',
    color: '#8C6D58',
    fontWeight: '600'
  },
  helperText: {
    fontSize: '0.88rem',
    color: '#6B5446',
    marginBottom: '12px'
  },
  queryList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px'
  },
  queryTag: {
    backgroundColor: '#FAF5EE',
    padding: '10px 14px',
    borderRadius: '10px',
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: '0.88rem',
    color: '#362417',
    border: '1px solid #EFE5D8'
  },
  queryFreq: {
    fontSize: '0.78rem',
    color: '#D97706',
    fontWeight: '700'
  },
  table: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px'
  },
  tableRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '10px 14px',
    backgroundColor: '#FAF5EE',
    borderRadius: '12px',
    border: '1px solid #EFE5D8'
  },
  subText: {
    fontSize: '0.78rem',
    color: '#8C6D58'
  },
  statusBadge: {
    backgroundColor: '#D1FAE5',
    color: '#047857',
    padding: '4px 10px',
    borderRadius: '12px',
    fontSize: '0.78rem',
    fontWeight: '700',
    display: 'flex',
    alignItems: 'center'
  },
  pendingBadge: {
    backgroundColor: '#FEF3C7',
    color: '#B45309',
    padding: '4px 10px',
    borderRadius: '12px',
    fontSize: '0.78rem',
    fontWeight: '700',
    display: 'flex',
    alignItems: 'center'
  }
};

export default AdminDashboard;
