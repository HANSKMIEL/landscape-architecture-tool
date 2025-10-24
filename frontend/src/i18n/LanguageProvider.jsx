/**
 * Multi-language internationalization system for Landscape Architecture Tool
 * Supports dynamic language switching with comprehensive translation management
 */

import React, { createContext, useContext, useState, useEffect } from 'react';

// Import language files
import nlTranslations from './locales/nl.json';
import enTranslations from './locales/en.json';

// Available languages
export const AVAILABLE_LANGUAGES = [
  { code: 'nl', name: 'Nederlands', flag: '🇳🇱' },
  { code: 'en', name: 'English', flag: '🇬🇧' }
];

// Translation data
const translations = {
  nl: nlTranslations,
  en: enTranslations
};

// Language context
const LanguageContext = createContext();

// Custom hook to use language context
export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};

// Language provider component
export const LanguageProvider = ({ children, initialLanguage = 'nl' }) => {
  const getStoredLanguage = () => {
    try {
      return typeof window !== 'undefined' ? localStorage.getItem('preferredLanguage') : null;
    } catch (error) {
      console.warn('Unable to access localStorage for language preference:', error);
      return null;
    }
  };

  const resolveInitialLanguage = () => {
    if (initialLanguage && translations[initialLanguage]) {
      return initialLanguage;
    }

    const storedLanguage = getStoredLanguage();
    if (storedLanguage && translations[storedLanguage]) {
      return storedLanguage;
    }

    return 'nl';
  };

  const [currentLanguage, setCurrentLanguage] = useState(resolveInitialLanguage); // Default to resolved language

  // Keep language in sync if initialLanguage prop changes
  useEffect(() => {
    if (initialLanguage && translations[initialLanguage]) {
      setCurrentLanguage(initialLanguage);
      return;
    }

    const savedLanguage = getStoredLanguage();
    if (savedLanguage && translations[savedLanguage]) {
      setCurrentLanguage(savedLanguage);
    }
  }, [initialLanguage]);

  // Save language preference to localStorage when changed
  const changeLanguage = (languageCode) => {
    if (translations[languageCode]) {
      setCurrentLanguage(languageCode);
      try {
        if (typeof window !== 'undefined') {
          localStorage.setItem('preferredLanguage', languageCode);
        }
      } catch (error) {
        console.warn('Unable to persist language preference:', error);
      }
    }
  };

  // Translation function with nested key support
  const t = (key, fallback = key) => {
    const keys = key.split('.');
    let value = translations[currentLanguage];

    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k];
      } else {
        // Try English as fallback
        let englishValue = translations.en;
        for (const englishKey of keys) {
          if (englishValue && typeof englishValue === 'object' && englishKey in englishValue) {
            englishValue = englishValue[englishKey];
          } else {
            return fallback;
          }
        }
        return englishValue;
      }
    }

    return typeof value === 'string' ? value : fallback;
  };

  // Get current language info
  const getCurrentLanguageInfo = () => {
    return AVAILABLE_LANGUAGES.find(lang => lang.code === currentLanguage) || AVAILABLE_LANGUAGES[0];
  };

  const value = {
    currentLanguage,
    changeLanguage,
    t,
    availableLanguages: AVAILABLE_LANGUAGES,
    getCurrentLanguageInfo
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
};

// HOC for class components
export const withLanguage = (Component) => {
  return function LanguageComponent(props) {
    const languageProps = useLanguage();
    return <Component {...props} {...languageProps} />;
  };
};

// Language selector component
export const LanguageSelector = ({ className = '' }) => {
  const { currentLanguage, changeLanguage, availableLanguages } = useLanguage();

  return (
    <div className={`language-selector ${className}`}>
      <select
        value={currentLanguage}
        onChange={(e) => changeLanguage(e.target.value)}
        className="bg-white border border-gray-300 rounded-md px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
      >
        {availableLanguages.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.flag} {lang.name}
          </option>
        ))}
      </select>
    </div>
  );
};

export default LanguageProvider;