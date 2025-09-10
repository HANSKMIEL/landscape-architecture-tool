import React, { createContext, useContext, useState, useEffect } from 'react';

const translations = {
  nl: {
    common: {
      loading: 'Laden...',
      error: 'Fout',
      save: 'Opslaan',
      cancel: 'Annuleren',
      delete: 'Verwijderen',
      edit: 'Bewerken',
      add: 'Toevoegen',
      search: 'Zoeken'
    },
    auth: {
      login: 'Inloggen',
      logout: 'Uitloggen',
      username: 'Gebruikersnaam',
      password: 'Wachtwoord',
      loginSuccess: 'Succesvol ingelogd',
      loginFailed: 'Inloggen mislukt',
      logoutSuccess: 'Succesvol uitgelogd'
    },
    navigation: {
      dashboard: 'Dashboard',
      suppliers: 'Leveranciers',
      plants: 'Planten',
      products: 'Producten',
      clients: 'Klanten',
      projects: 'Projecten'
    }
  },
  en: {
    common: {
      loading: 'Loading...',
      error: 'Error',
      save: 'Save',
      cancel: 'Cancel',
      delete: 'Delete',
      edit: 'Edit',
      add: 'Add',
      search: 'Search'
    },
    auth: {
      login: 'Login',
      logout: 'Logout',
      username: 'Username',
      password: 'Password',
      loginSuccess: 'Login successful',
      loginFailed: 'Login failed',
      logoutSuccess: 'Logout successful'
    },
    navigation: {
      dashboard: 'Dashboard',
      suppliers: 'Suppliers',
      plants: 'Plants',
      products: 'Products',
      clients: 'Clients',
      projects: 'Projects'
    }
  }
};

export const AVAILABLE_LANGUAGES = [
  { code: 'nl', name: 'Nederlands', flag: '🇳🇱' },
  { code: 'en', name: 'English', flag: '🇬🇧' }
];

const LanguageContext = createContext();

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    return {
      currentLanguage: 'nl',
      changeLanguage: () => {},
      t: (key, fallback = key) => fallback,
      availableLanguages: AVAILABLE_LANGUAGES,
      getCurrentLanguageInfo: () => AVAILABLE_LANGUAGES[0]
    };
  }
  return context;
};

export const LanguageProvider = ({ children }) => {
  const [currentLanguage, setCurrentLanguage] = useState('nl');

  useEffect(() => {
    const savedLanguage = localStorage.getItem('preferredLanguage');
    if (savedLanguage && (savedLanguage === 'nl' || savedLanguage === 'en')) {
      setCurrentLanguage(savedLanguage);
    }
  }, []);

  const changeLanguage = (languageCode) => {
    if (translations[languageCode]) {
      setCurrentLanguage(languageCode);
      localStorage.setItem('preferredLanguage', languageCode);
    }
  };

  const t = (key, fallback = key) => {
    try {
      if (!key || typeof key !== 'string') return fallback;
      
      const keys = key.split('.');
      let value = translations[currentLanguage];
      
      for (const k of keys) {
        if (value && typeof value === 'object' && k in value) {
          value = value[k];
        } else {
          let englishValue = translations.en;
          for (const englishKey of keys) {
            if (englishValue && typeof englishValue === 'object' && englishKey in englishValue) {
              englishValue = englishValue[englishKey];
            } else {
              return fallback;
            }
          }
          return typeof englishValue === 'string' ? englishValue : fallback;
        }
      }
      
      return typeof value === 'string' ? value : fallback;
    } catch (error) {
      console.warn('Translation error:', key, error);
      return fallback;
    }
  };

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

export default LanguageProvider;

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
