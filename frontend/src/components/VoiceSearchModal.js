import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { FaMicrophone, FaTimes, FaVolumeUp, FaSearch } from 'react-icons/fa';
import { useLanguage } from '../utils/LanguageContext';

const VoiceSearchModal = ({ isOpen, onClose, onSearch, currentLang = 'en' }) => {
  const { t } = useLanguage();
  const navigate = useNavigate();
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [selectedLangCode, setSelectedLangCode] = useState('en-US');
  const [speechError, setSpeechError] = useState('');
  const recognitionRef = useRef(null);
  const presetQueries = [
    { text: currentLang === 'hi' ? 'मिट्टी का घड़ा' : currentLang === 'mr' ? 'मातीचे भांडे' : 'Clay Pot', query: 'pottery clay matka' },
    { text: currentLang === 'hi' ? 'पूजा थाली' : currentLang === 'mr' ? 'पूजा थाळी' : 'Pooja Thali', query: 'pooja thali brass' },
    { text: currentLang === 'hi' ? 'हस्तनिर्मित मोमबत्ती' : currentLang === 'mr' ? 'हस्तनिर्मित मेणबत्ती' : 'Handmade Soy Candle', query: 'candle' },
    { text: currentLang === 'hi' ? 'चाँदी का हार' : currentLang === 'mr' ? 'चांदीचा हार' : 'Silver Necklace', query: 'jewellery' },
    { text: currentLang === 'hi' ? 'रुखवत विवाह सेट' : currentLang === 'mr' ? 'रुखवत लग्न संच' : 'Rukhwat Wedding Set', query: 'rukhwat' }
  ];

  useEffect(() => {
    const languageCodes = { en: 'en-US', hi: 'hi-IN', mr: 'mr-IN' };
    setSelectedLangCode(languageCodes[currentLang] || 'en-US');
  }, [currentLang]);

  useEffect(() => {
    if (isOpen) return;
    const recognition = recognitionRef.current;
    if (!recognition) return;
    recognition.onresult = null;
    recognition.onend = null;
    recognition.onerror = null;
    try {
      recognition.abort();
    } catch (error) {
      console.error('Could not stop voice recognition after closing the dialog:', error);
    }
    recognitionRef.current = null;
    setIsListening(false);
  }, [isOpen]);

  useEffect(() => () => {
    const recognition = recognitionRef.current;
    if (!recognition) return;
    recognition.onresult = null;
    recognition.onend = null;
    recognition.onerror = null;
    try {
      recognition.abort();
    } catch (error) {
      console.error('Could not stop voice recognition while closing the app:', error);
    }
  }, []);

  const startListening = () => {
    setTranscript('');
    setSpeechError('');
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setSpeechError(t.voiceUnsupported);
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = selectedLangCode;
    recognition.onresult = (event) => {
      const resultTranscript = Array.from(event.results)
        .map((result) => result[0]?.transcript || '')
        .join(' ')
        .trim();
      setTranscript(resultTranscript);
      setSpeechError('');
    };
    recognition.onend = () => {
      setIsListening(false);
      if (recognitionRef.current === recognition) recognitionRef.current = null;
    };
    recognition.onerror = (event) => {
      setIsListening(false);
      const errorMessages = {
        'not-allowed': t.micBlocked,
        'service-not-allowed': t.speechBlocked,
        'no-speech': t.noSpeech,
        network: t.speechNetworkError
      };
      setSpeechError(errorMessages[event.error] || t.speechFailed);
      if (recognitionRef.current === recognition) recognitionRef.current = null;
    };
    recognitionRef.current = recognition;
    try {
      recognition.start();
      setIsListening(true);
    } catch (error) {
      setIsListening(false);
      recognitionRef.current = null;
      console.error('Could not start voice recognition:', error);
      setSpeechError(t.micStartFailed);
    }
  };

  const stopListening = () => {
    setIsListening(false);
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (error) {
        console.error('Could not stop voice recognition:', error);
        setSpeechError(t.speechFailed);
      }
    }
  };

  const handleApplySearch = (queryToUse) => {
    const q = (queryToUse || transcript).trim();
    if (q) {
      onSearch(q);
      onClose();
      navigate('/shop');
    }
  };

  if (!isOpen) return null;

  return (
    <div style={styles.overlay}>
      <div style={styles.modalCard}>
        <button style={styles.closeBtn} onClick={onClose}>
          <FaTimes />
        </button>

        <div style={styles.header}>
          <h3 style={styles.title}>🎙️ {t.multilingualVoiceSearch}</h3>
          <p style={styles.subtitle}>{t.speakToDiscover}</p>
        </div>

        {/* Language selector for voice recognition */}
        <div style={styles.langBar}>
          <button
            style={selectedLangCode === 'en-US' ? styles.langActive : styles.langBtn}
            onClick={() => setSelectedLangCode('en-US')}
          >
            English
          </button>
          <button
            style={selectedLangCode === 'hi-IN' ? styles.langActive : styles.langBtn}
            onClick={() => setSelectedLangCode('hi-IN')}
          >
            हिंदी (Hindi)
          </button>
          <button
            style={selectedLangCode === 'mr-IN' ? styles.langActive : styles.langBtn}
            onClick={() => setSelectedLangCode('mr-IN')}
          >
            मराठी (Marathi)
          </button>
        </div>

        {/* Pulsing Voice Visualizer */}
        <div style={styles.micCircleWrapper}>
          <button
            type="button"
            aria-label={isListening ? t.stopVoiceSearch : t.startVoiceSearch}
            style={{
              ...styles.micCircle,
              ...(isListening ? styles.micPulsing : {})
            }}
            onClick={isListening ? stopListening : startListening}
          >
            <FaMicrophone style={styles.micIcon} />
          </button>
          <p style={styles.micStatus}>
            {isListening ? t.listeningSpeak : t.clickMicToSpeak}
          </p>
        </div>

        {/* Sound Wave Indicator */}
        {isListening && (
          <div style={styles.waveContainer}>
            <div style={{ ...styles.waveBar, animationDelay: '0.1s' }}></div>
            <div style={{ ...styles.waveBar, animationDelay: '0.3s' }}></div>
            <div style={{ ...styles.waveBar, animationDelay: '0.2s' }}></div>
            <div style={{ ...styles.waveBar, animationDelay: '0.4s' }}></div>
            <div style={{ ...styles.waveBar, animationDelay: '0.15s' }}></div>
          </div>
        )}

        {/* Live Transcript Display */}
        <div style={styles.transcriptBox}>
          {transcript ? (
            <p style={styles.transcriptText}>"{transcript}"</p>
          ) : (
            <p style={styles.placeholderText}>{t.spokenWordsHere}</p>
          )}
        </div>

        <input
          type="search"
          aria-label={t.searchProductsByTyping}
          placeholder={t.typeSearchPlaceholder}
          value={transcript}
          onChange={(event) => setTranscript(event.target.value)}
          style={styles.searchInput}
        />
        {speechError && <p role="status" style={styles.errorText}>{speechError}</p>}

        {transcript && (
          <button style={styles.searchSubmitBtn} onClick={() => handleApplySearch()}>
            <FaSearch style={{ marginRight: 8 }} /> {t.search} "{transcript}"
          </button>
        )}

        {/* Preset Voice Chips */}
        <div style={styles.presetsSection}>
          <p style={styles.presetLabel}><FaVolumeUp style={{ marginRight: 6 }} /> {t.tryVoicePresets}</p>
          <div style={styles.chipGrid}>
            {presetQueries.map((item, idx) => (
              <button key={idx} style={styles.chip} onClick={() => handleApplySearch(item.query)}>
                {item.text}
              </button>
            ))}
          </div>
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
    backgroundColor: 'rgba(25, 16, 10, 0.75)',
    backdropFilter: 'blur(8px)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 9999,
    padding: '20px'
  },
  modalCard: {
    backgroundColor: '#FAF5EE',
    borderRadius: '24px',
    padding: '35px 30px',
    maxWidth: '520px',
    width: '100%',
    boxShadow: '0 20px 50px rgba(0,0,0,0.3)',
    position: 'relative',
    textAlign: 'center',
    border: '1px solid rgba(200, 90, 50, 0.2)'
  },
  closeBtn: {
    position: 'absolute',
    top: '20px',
    right: '20px',
    background: 'none',
    border: 'none',
    fontSize: '20px',
    color: '#8C6D58',
    cursor: 'pointer'
  },
  header: {
    marginBottom: '20px'
  },
  title: {
    fontSize: '1.5rem',
    color: '#362417',
    marginBottom: '6px',
    fontWeight: '700'
  },
  subtitle: {
    fontSize: '0.92rem',
    color: '#6B5446'
  },
  langBar: {
    display: 'flex',
    justifyContent: 'center',
    gap: '10px',
    marginBottom: '25px'
  },
  langBtn: {
    padding: '6px 14px',
    borderRadius: '20px',
    border: '1px solid #D9C5B2',
    background: '#FFF',
    color: '#6B5446',
    fontSize: '0.85rem',
    cursor: 'pointer',
    fontWeight: '600'
  },
  langActive: {
    padding: '6px 14px',
    borderRadius: '20px',
    border: '1px solid #C85A32',
    background: '#C85A32',
    color: '#FFF',
    fontSize: '0.85rem',
    cursor: 'pointer',
    fontWeight: '700'
  },
  micCircleWrapper: {
    margin: '20px 0',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center'
  },
  micCircle: {
    width: '85px',
    height: '85px',
    borderRadius: '50%',
    backgroundColor: '#C85A32',
    color: '#FFF',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    cursor: 'pointer',
    boxShadow: '0 10px 25px rgba(200, 90, 50, 0.35)',
    transition: 'transform 0.2s, background-color 0.2s'
  },
  micPulsing: {
    backgroundColor: '#D97706',
    animation: 'pulse 1.2s infinite ease-in-out'
  },
  micIcon: {
    fontSize: '34px'
  },
  micStatus: {
    marginTop: '12px',
    fontWeight: '600',
    fontSize: '0.92rem',
    color: '#362417'
  },
  waveContainer: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    gap: '5px',
    height: '24px',
    marginBottom: '15px'
  },
  waveBar: {
    width: '4px',
    height: '100%',
    backgroundColor: '#C85A32',
    borderRadius: '3px'
  },
  transcriptBox: {
    minHeight: '55px',
    backgroundColor: '#FFFFFF',
    borderRadius: '14px',
    padding: '12px 18px',
    border: '1px dashed #C85A32',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: '20px'
  },
  searchInput: {
    width: '100%',
    padding: '11px 13px',
    marginBottom: '12px',
    border: '1px solid #D9C5B2',
    borderRadius: '8px',
    color: '#362417',
    fontSize: '0.95rem'
  },
  errorText: {
    color: '#9B2C20',
    fontSize: '0.85rem',
    marginBottom: '12px'
  },
  transcriptText: {
    fontSize: '1.05rem',
    color: '#C85A32',
    fontWeight: '700'
  },
  placeholderText: {
    fontSize: '0.88rem',
    color: '#A08A7B',
    fontStyle: 'italic'
  },
  searchSubmitBtn: {
    width: '100%',
    padding: '12px',
    backgroundColor: '#C85A32',
    color: '#FFF',
    border: 'none',
    borderRadius: '12px',
    fontWeight: '700',
    fontSize: '0.98rem',
    cursor: 'pointer',
    marginBottom: '20px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  },
  presetsSection: {
    textAlign: 'left'
  },
  presetLabel: {
    fontSize: '0.85rem',
    fontWeight: '700',
    color: '#6B5446',
    marginBottom: '10px',
    display: 'flex',
    alignItems: 'center'
  },
  chipGrid: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '8px'
  },
  chip: {
    padding: '6px 12px',
    backgroundColor: '#EFE5D8',
    border: '1px solid #D9C5B2',
    borderRadius: '16px',
    fontSize: '0.82rem',
    color: '#362417',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'background-color 0.2s'
  }
};

export default VoiceSearchModal;
