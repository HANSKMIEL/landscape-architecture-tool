import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Palette, Type, Paintbrush, Monitor, Sun, Moon } from 'lucide-react'

const AppearanceSettings = ({ language = 'nl' }) => {
  const [theme, setTheme] = useState('light')
  const [colorScheme, setColorScheme] = useState('blue')
  const [fontSize, setFontSize] = useState('medium')
  const [fontFamily, setFontFamily] = useState('inter')
  const [companyLogo, setCompanyLogo] = useState('')
  const [companyColors, setCompanyColors] = useState({
    primary: '#3B82F6',
    secondary: '#10B981',
    accent: '#F59E0B'
  })

  const translations = {
    en: {
      title: 'Appearance Settings',
      subtitle: 'Customize the look and feel of your application',
      themeSection: 'Theme',
      themeDesc: 'Choose your preferred application theme',
      light: 'Light Mode',
      dark: 'Dark Mode',
      auto: 'Auto (System)',
      colorSchemeSection: 'Color Scheme',
      colorSchemeDesc: 'Select your preferred color palette',
      fontSection: 'Typography',
      fontDesc: 'Customize fonts and text size',
      fontSize: 'Font Size',
      fontFamily: 'Font Family',
      small: 'Small',
      medium: 'Medium',
      large: 'Large',
      brandingSection: 'Company Branding',
      brandingDesc: 'Customize with your company identity',
      companyLogo: 'Company Logo',
      logoPlaceholder: 'Upload your company logo',
      primaryColor: 'Primary Color',
      secondaryColor: 'Secondary Color',
      accentColor: 'Accent Color',
      previewSection: 'Preview',
      previewDesc: 'See how your settings look',
      saveSettings: 'Save Settings',
      resetDefaults: 'Reset to Defaults'
    },
    nl: {
      title: 'Uiterlijk Instellingen',
      subtitle: 'Pas het uiterlijk van uw applicatie aan',
      themeSection: 'Thema',
      themeDesc: 'Kies uw voorkeursthema voor de applicatie',
      light: 'Lichte Modus',
      dark: 'Donkere Modus',
      auto: 'Automatisch (Systeem)',
      colorSchemeSection: 'Kleurenschema',
      colorSchemeDesc: 'Selecteer uw voorkeurs kleurenpalet',
      fontSection: 'Typografie',
      fontDesc: 'Pas lettertypen en tekstgrootte aan',
      fontSize: 'Lettergrootte',
      fontFamily: 'Lettertype Familie',
      small: 'Klein',
      medium: 'Gemiddeld',
      large: 'Groot',
      brandingSection: 'Bedrijfsbranding',
      brandingDesc: 'Personaliseer met uw bedrijfsidentiteit',
      companyLogo: 'Bedrijfslogo',
      logoPlaceholder: 'Upload uw bedrijfslogo',
      primaryColor: 'Primaire Kleur',
      secondaryColor: 'Secundaire Kleur',
      accentColor: 'Accent Kleur',
      previewSection: 'Voorbeeld',
      previewDesc: 'Bekijk hoe uw instellingen eruitzien',
      saveSettings: 'Instellingen Opslaan',
      resetDefaults: 'Standaardwaarden Herstellen'
    }
  }

  const t = translations[language]

  const colorSchemes = [
    { id: 'blue', name: 'Blue', primary: '#3B82F6', secondary: '#10B981' },
    { id: 'green', name: 'Green', primary: '#10B981', secondary: '#059669' },
    { id: 'purple', name: 'Purple', primary: '#8B5CF6', secondary: '#7C3AED' },
    { id: 'orange', name: 'Orange', primary: '#F59E0B', secondary: '#D97706' },
    { id: 'custom', name: 'Custom', primary: companyColors.primary, secondary: companyColors.secondary }
  ]

  const fonts = [
    { id: 'inter', name: 'Inter', family: 'Inter, sans-serif' },
    { id: 'roboto', name: 'Roboto', family: 'Roboto, sans-serif' },
    { id: 'poppins', name: 'Poppins', family: 'Poppins, sans-serif' },
    { id: 'opensans', name: 'Open Sans', family: 'Open Sans, sans-serif' }
  ]

  useEffect(() => {
    // Load saved settings from localStorage
    const savedSettings = localStorage.getItem('appearanceSettings')
    if (savedSettings) {
      const settings = JSON.parse(savedSettings)
      setTheme(settings.theme || 'light')
      setColorScheme(settings.colorScheme || 'blue')
      setFontSize(settings.fontSize || 'medium')
      setFontFamily(settings.fontFamily || 'inter')
      setCompanyColors(settings.companyColors || companyColors)
    }
  }, [companyColors])

  const saveSettings = () => {
    const settings = {
      theme,
      colorScheme,
      fontSize,
      fontFamily,
      companyColors,
      companyLogo
    }
    localStorage.setItem('appearanceSettings', JSON.stringify(settings))
    
    // Apply settings to document
    applySettings(settings)
    
    // Show success message
    alert(language === 'nl' ? 'Instellingen opgeslagen!' : 'Settings saved!')
  }

  const applySettings = (settings) => {
    const root = document.documentElement
    
    // Apply theme
    if (settings.theme === 'dark') {
      root.classList.add('dark')
      document.body.classList.add('dark')
    } else if (settings.theme === 'auto') {
      // Auto theme based on system preference
      if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        root.classList.add('dark')
        document.body.classList.add('dark')
      } else {
        root.classList.remove('dark')
        document.body.classList.remove('dark')
      }
    } else {
      root.classList.remove('dark')
      document.body.classList.remove('dark')
    }
    
    // Apply colors
    const scheme = colorSchemes.find(s => s.id === settings.colorScheme)
    if (scheme) {
      root.style.setProperty('--primary-color', scheme.primary)
      root.style.setProperty('--secondary-color', scheme.secondary)
      root.style.setProperty('--accent-color', settings.companyColors?.accent || '#F59E0B')
    }
    
    // Apply custom company colors if using custom scheme
    if (settings.colorScheme === 'custom') {
      root.style.setProperty('--primary-color', settings.companyColors.primary)
      root.style.setProperty('--secondary-color', settings.companyColors.secondary)
      root.style.setProperty('--accent-color', settings.companyColors.accent)
    }
    
    // Apply font size
    const fontSizes = { small: '14px', medium: '16px', large: '18px' }
    root.style.setProperty('--base-font-size', fontSizes[settings.fontSize])
    
    // Apply font family
    const selectedFont = fonts.find(f => f.id === settings.fontFamily)
    if (selectedFont) {
      root.style.setProperty('--font-family', selectedFont.family)
      document.body.style.fontFamily = selectedFont.family
    }
  }

  const resetDefaults = () => {
    const defaultSettings = {
      theme: 'light',
      colorScheme: 'blue',
      fontSize: 'medium',
      fontFamily: 'inter',
      companyColors: {
        primary: '#3B82F6',
        secondary: '#10B981',
        accent: '#F59E0B'
      },
      companyLogo: ''
    }
    
    setTheme(defaultSettings.theme)
    setColorScheme(defaultSettings.colorScheme)
    setFontSize(defaultSettings.fontSize)
    setFontFamily(defaultSettings.fontFamily)
    setCompanyColors(defaultSettings.companyColors)
    setCompanyLogo(defaultSettings.companyLogo)
    
    // Clear localStorage
    localStorage.removeItem('appearanceSettings')
    
    // Apply default settings immediately for preview
    applySettings(defaultSettings)
    
    alert(language === 'nl' ? 'Standaardwaarden hersteld!' : 'Defaults restored!')
   useEffect(() => {
    // Apply current settings
    const currentSettings = {
      theme,
      colorScheme,
      fontSize,
      fontFamily,
      companyColors,
      companyLogo
    }
    applySettings(currentSettings)
  }, [theme, colorScheme, fontSize, fontFamily, companyColors, companyLogo, applySettings])
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900">{t.title}</h2>
        <p className="text-gray-600">{t.subtitle}</p>
      </div>

      {/* Theme Selection */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Monitor className="h-5 w-5 text-blue-600" />
            {t.themeSection}
          </CardTitle>
          <p className="text-sm text-gray-600">{t.themeDesc}</p>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4">
            {[
              { id: 'light', label: t.light, icon: Sun },
              { id: 'dark', label: t.dark, icon: Moon },
              { id: 'auto', label: t.auto, icon: Monitor }
            ].map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setTheme(id)}
                className={`p-4 border rounded-lg flex flex-col items-center gap-2 transition-colors ${
                  theme === id
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <Icon className="h-6 w-6" />
                <span className="text-sm font-medium">{label}</span>
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Color Scheme */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Palette className="h-5 w-5 text-purple-600" />
            {t.colorSchemeSection}
          </CardTitle>
          <p className="text-sm text-gray-600">{t.colorSchemeDesc}</p>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {colorSchemes.map((scheme) => (
              <button
                key={scheme.id}
                onClick={() => setColorScheme(scheme.id)}
                className={`p-4 border rounded-lg flex flex-col items-center gap-2 transition-colors ${
                  colorScheme === scheme.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex gap-1">
                  <div 
                    className="w-4 h-4 rounded-full border border-gray-300" 
                    style={{ backgroundColor: scheme.primary }}
                  />
                  <div 
                    className="w-4 h-4 rounded-full border border-gray-300" 
                    style={{ backgroundColor: scheme.secondary }}
                  />
                </div>
                <span className="text-sm font-medium">{scheme.name}</span>
              </button>
            ))}
          </div>
          
          {colorScheme === 'custom' && (
            <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t.primaryColor}
                </label>
                <div className="flex items-center gap-2">
                  <input
                    type="color"
                    value={companyColors.primary}
                    onChange={(e) => setCompanyColors({...companyColors, primary: e.target.value})}
                    className="w-12 h-8 border border-gray-300 rounded"
                  />
                  <input
                    type="text"
                    value={companyColors.primary}
                    onChange={(e) => setCompanyColors({...companyColors, primary: e.target.value})}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t.secondaryColor}
                </label>
                <div className="flex items-center gap-2">
                  <input
                    type="color"
                    value={companyColors.secondary}
                    onChange={(e) => setCompanyColors({...companyColors, secondary: e.target.value})}
                    className="w-12 h-8 border border-gray-300 rounded"
                  />
                  <input
                    type="text"
                    value={companyColors.secondary}
                    onChange={(e) => setCompanyColors({...companyColors, secondary: e.target.value})}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t.accentColor}
                </label>
                <div className="flex items-center gap-2">
                  <input
                    type="color"
                    value={companyColors.accent}
                    onChange={(e) => setCompanyColors({...companyColors, accent: e.target.value})}
                    className="w-12 h-8 border border-gray-300 rounded"
                  />
                  <input
                    type="text"
                    value={companyColors.accent}
                    onChange={(e) => setCompanyColors({...companyColors, accent: e.target.value})}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm"
                  />
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Typography */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Type className="h-5 w-5 text-green-600" />
            {t.fontSection}
          </CardTitle>
          <p className="text-sm text-gray-600">{t.fontDesc}</p>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t.fontSize}
              </label>
              <select
                value={fontSize}
                onChange={(e) => setFontSize(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="small">{t.small}</option>
                <option value="medium">{t.medium}</option>
                <option value="large">{t.large}</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t.fontFamily}
              </label>
              <select
                value={fontFamily}
                onChange={(e) => setFontFamily(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {fonts.map((font) => (
                  <option key={font.id} value={font.id}>{font.name}</option>
                ))}
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Company Branding */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Paintbrush className="h-5 w-5 text-orange-600" />
            {t.brandingSection}
          </CardTitle>
          <p className="text-sm text-gray-600">{t.brandingDesc}</p>
        </CardHeader>
        <CardContent>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {t.companyLogo}
            </label>
            <input
              type="file"
              accept="image/*"
              onChange={(e) => {
                const file = e.target.files[0]
                if (file) {
                  const reader = new FileReader()
                  reader.onload = (e) => setCompanyLogo(e.target.result)
                  reader.readAsDataURL(file)
                }
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {companyLogo && (
              <div className="mt-4">
                <img src={companyLogo} alt="Company Logo Preview" className="h-16 object-contain" />
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Preview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Monitor className="h-5 w-5 text-gray-600" />
            {t.previewSection}
          </CardTitle>
          <p className="text-sm text-gray-600">{t.previewDesc}</p>
        </CardHeader>
        <CardContent>
          <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
            <div className="text-center">
              <div className="text-lg font-semibold mb-2" style={{ 
                color: colorSchemes.find(s => s.id === colorScheme)?.primary,
                fontSize: fontSize === 'small' ? '16px' : fontSize === 'large' ? '20px' : '18px',
                fontFamily: fonts.find(f => f.id === fontFamily)?.family
              }}>
                {language === 'nl' ? 'Voorbeeld Tekst' : 'Sample Text'}
              </div>
              <p className="text-gray-600" style={{
                fontSize: fontSize === 'small' ? '13px' : fontSize === 'large' ? '16px' : '14px',
                fontFamily: fonts.find(f => f.id === fontFamily)?.family
              }}>
                {language === 'nl' 
                  ? 'Dit is hoe uw applicatie eruit zal zien met de geselecteerde instellingen.'
                  : 'This is how your application will look with the selected settings.'
                }
              </p>
              <button 
                className="mt-4 px-4 py-2 rounded-md text-white text-sm font-medium"
                style={{ 
                  backgroundColor: colorSchemes.find(s => s.id === colorScheme)?.primary,
                  fontFamily: fonts.find(f => f.id === fontFamily)?.family
                }}
              >
                {language === 'nl' ? 'Voorbeeld Knop' : 'Sample Button'}
              </button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className="flex gap-4">
        <button
          onClick={saveSettings}
          className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-medium"
        >
          {t.saveSettings}
        </button>
        <button
          onClick={resetDefaults}
          className="px-6 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors font-medium"
        >
          {t.resetDefaults}
        </button>
      </div>
    </div>
  )
}

export default AppearanceSettings