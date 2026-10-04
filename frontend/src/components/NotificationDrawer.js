import React, { useState, useEffect, useCallback } from 'react';
import { FaBell, FaTimes, FaCheck, FaTag, FaTruck, FaRobot, FaExclamationTriangle } from 'react-icons/fa';
import API from '../api';
import { useLanguage } from '../utils/LanguageContext';
import { useTranslatedValues } from '../utils/useTranslatedValues';

const NotificationCard = ({ item, getIcon }) => {
  const { t } = useLanguage();
  const { values, error, isTranslating } = useTranslatedValues([item.title, item.message]);

  return (
    <div
      style={{
        ...styles.notifCard,
        borderLeft: item.priority === 'high' ? '4px solid #C85A32' : '4px solid #D97706',
        backgroundColor: item.read ? '#FAF5EE' : '#FFFFFF'
      }}
      aria-busy={isTranslating}
    >
      <div style={styles.iconBox}>{getIcon(item.type)}</div>
      <div style={styles.notifContent}>
        <div style={styles.cardHeader}>
          <h5 style={styles.notifTitle}>
            {values[0] || (isTranslating ? t.translatingProduct : t.productTranslationUnavailable)}
          </h5>
          <span style={styles.timestamp}>{item.timestamp}</span>
        </div>
        <p style={styles.notifMsg}>
          {values[1] || (isTranslating ? t.translatingProduct : t.productTranslationUnavailable)}
        </p>
        {error && <p role="status">{t.translationFailed}</p>}
      </div>
    </div>
  );
};

const NotificationDrawer = ({ isOpen, onClose, role = 'customer' }) => {
  const { t } = useLanguage();
  const [notifications, setNotifications] = useState([]);
  const [activeTab, setActiveTab] = useState('all');

  const fetchNotifications = useCallback(async () => {
    try {
      const res = await API.get(`/ml/notifications?role=${role}`);
      setNotifications(res.data || []);
    } catch (err) {
      console.error("Error fetching notifications:", err);
    }
  }, [role]);

  useEffect(() => {
    if (isOpen) fetchNotifications();
  }, [isOpen, fetchNotifications]);

  const markAllAsRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  };

  const getIcon = (type) => {
    if (type === 'price_drop') return <FaTag style={{ color: '#D97706' }} />;
    if (type === 'shipping' || type === 'order') return <FaTruck style={{ color: '#0D9488' }} />;
    if (type === 'inventory') return <FaExclamationTriangle style={{ color: '#DC2626' }} />;
    return <FaRobot style={{ color: '#C85A32' }} />;
  };

  const filteredNotifs = notifications.filter((n) => {
    if (activeTab === 'all') return true;
    if (activeTab === 'orders') return n.type === 'order' || n.type === 'shipping';
    if (activeTab === 'alerts') return n.type === 'price_drop' || n.type === 'inventory';
    return true;
  });

  if (!isOpen) return null;

  return (
    <div style={styles.overlay} onClick={onClose}>
      <div style={styles.drawer} onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div style={styles.drawerHeader}>
          <div style={styles.titleRow}>
            <FaBell style={{ color: '#C85A32', fontSize: '20px', marginRight: 10 }} />
            <h3 style={styles.title}>{t.notifications}</h3>
          </div>
          <button style={styles.closeBtn} onClick={onClose}>
            <FaTimes />
          </button>
        </div>

        {/* Filter Tabs & Mark Read */}
        <div style={styles.subHeader}>
          <div style={styles.tabBar}>
            <button
              style={activeTab === 'all' ? styles.tabActive : styles.tab}
              onClick={() => setActiveTab('all')}
            >
              {t.allAlerts}
            </button>
            <button
              style={activeTab === 'orders' ? styles.tabActive : styles.tab}
              onClick={() => setActiveTab('orders')}
            >
              {t.orders}
            </button>
            <button
              style={activeTab === 'alerts' ? styles.tabActive : styles.tab}
              onClick={() => setActiveTab('alerts')}
            >
              {t.priceDropsRestock}
            </button>
          </div>
          <button style={styles.markReadBtn} onClick={markAllAsRead}>
            <FaCheck style={{ marginRight: 4 }} /> {t.readAll}
          </button>
        </div>

        {/* Notification Cards Feed */}
        <div style={styles.notifFeed}>
          {filteredNotifs.length === 0 ? (
            <div style={styles.emptyState}>
              <p>{t.noNotifications}</p>
            </div>
          ) : (
            filteredNotifs.map((item) => (
              <NotificationCard key={item.id} item={item} getIcon={getIcon} />
            ))
          )}
        </div>
      </div>
    </div>
  );
};

const styles = {
  overlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.4)',
    zIndex: 9999,
    display: 'flex',
    justifyContent: 'flex-end'
  },
  drawer: {
    width: '420px',
    height: '100%',
    backgroundColor: '#FAF5EE',
    boxShadow: '-10px 0 30px rgba(0,0,0,0.2)',
    display: 'flex',
    flexDirection: 'column',
    padding: '25px 20px'
  },
  drawerHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '15px'
  },
  titleRow: {
    display: 'flex',
    alignItems: 'center'
  },
  title: {
    fontSize: '1.25rem',
    color: '#362417',
    fontWeight: '700',
    margin: 0
  },
  closeBtn: {
    background: 'none',
    border: 'none',
    fontSize: '20px',
    color: '#8C6D58',
    cursor: 'pointer'
  },
  subHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '20px'
  },
  tabBar: {
    display: 'flex',
    gap: '6px'
  },
  tab: {
    padding: '5px 10px',
    borderRadius: '16px',
    border: '1px solid #D9C5B2',
    background: '#FFF',
    fontSize: '0.78rem',
    color: '#6B5446',
    cursor: 'pointer'
  },
  tabActive: {
    padding: '5px 10px',
    borderRadius: '16px',
    border: '1px solid #C85A32',
    background: '#C85A32',
    fontSize: '0.78rem',
    color: '#FFF',
    fontWeight: '700',
    cursor: 'pointer'
  },
  markReadBtn: {
    background: 'none',
    border: 'none',
    fontSize: '0.78rem',
    color: '#C85A32',
    fontWeight: '700',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center'
  },
  notifFeed: {
    flex: 1,
    overflowY: 'auto',
    display: 'flex',
    flexDirection: 'column',
    gap: '12px'
  },
  notifCard: {
    borderRadius: '14px',
    padding: '14px',
    display: 'flex',
    gap: '12px',
    boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
    transition: 'transform 0.15s'
  },
  iconBox: {
    fontSize: '20px',
    display: 'flex',
    alignItems: 'flex-start',
    marginTop: '2px'
  },
  notifContent: {
    flex: 1
  },
  cardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '4px'
  },
  notifTitle: {
    fontSize: '0.92rem',
    color: '#362417',
    fontWeight: '700',
    margin: 0
  },
  timestamp: {
    fontSize: '0.75rem',
    color: '#A08A7B'
  },
  notifMsg: {
    fontSize: '0.84rem',
    color: '#5B4636',
    margin: 0,
    lineHeight: '1.35'
  },
  emptyState: {
    textAlign: 'center',
    padding: '40px 20px',
    color: '#A08A7B'
  }
};

export default NotificationDrawer;
