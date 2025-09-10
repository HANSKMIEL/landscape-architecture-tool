import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Palette, Type, Paintbrush, Monitor, Sun, Moon } from 'lucide-react'

const AppearanceSettings = ({ language = 'nl' }) => {
  const [theme, setTheme] = useState('light')
  const [colorScheme, setColorScheme] = useState('blue')
  const [fontSize, setFontSize] = useState('medium')

  const translations = {
    en: {
      title: 'Appearance Settings',
      subtitle: 'Customize the look and feel of your application',
      themeSection: 'Theme',
      light: 'Light Mode',
      dark: 'Dark Mode',
      colorSchemeSection: 'Color Scheme',
      fontSection: 'Typography',
      fontSize: 'Font Size',
      saveSettings: 'Save Settings',
      resetDefaults: 'Reset to Defaults'
    },
    nl: {
      title: 'Uiterlijk Instellingen',
      subtitle: 'Pas het uiterlijk van uw applicatie aan',
      themeSection: 'Thema',
      light: 'Lichte Modus',
      dark: 'Donkere Modus',
      colorSchemeSection: 'Kleurenschema',
      fontSection: 'Typografie',
      fontSize: 'Lettergrootte',
      saveSettings: 'Instellingen Opslaan',
      resetDefaults: 'Standaardwaarden Herstellen'
    }
  }

  const t = translations[language] || translations.nl

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Palette className="h-5 w-5" />
            {t.title}
          </CardTitle>
          <p className="text-sm text-gray-600">{t.subtitle}</p>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Theme Selection */}
          <div>
            <h3 className="text-lg font-medium mb-3 flex items-center gap-2">
              <Monitor className="h-4 w-4" />
              {t.themeSection}
            </h3>
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => setTheme('light')}
                className={`p-3 rounded-lg border-2 transition-all ${
                  theme === 'light'
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <Sun className="h-5 w-5 mx-auto mb-2" />
                <span className="text-sm font-medium">{t.light}</span>
              </button>
              <button
                onClick={() => setTheme('dark')}
                className={`p-3 rounded-lg border-2 transition-all ${
                  theme === 'dark'
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <Moon className="h-5 w-5 mx-auto mb-2" />
                <span className="text-sm font-medium">{t.dark}</span>
              </button>
            </div>
          </div>

          {/* Color Scheme */}
          <div>
            <h3 className="text-lg font-medium mb-3 flex items-center gap-2">
              <Paintbrush className="h-4 w-4" />
              {t.colorSchemeSection}
            </h3>
            <div className="grid grid-cols-4 gap-3">
              {['blue', 'green', 'purple', 'orange'].map((color) => (
                <button
                  key={color}
                  onClick={() => setColorScheme(color)}
                  className={`h-12 rounded-lg border-2 transition-all ${
                    colorScheme === color
                      ? 'border-gray-800 scale-105'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  style={{
                    backgroundColor: {
                      blue: '#3B82F6',
                      green: '#10B981',
                      purple: '#8B5CF6',
                      orange: '#F59E0B'
                    }[color]
                  }}
                />
              ))}
            </div>
          </div>

          {/* Typography */}
          <div>
            <h3 className="text-lg font-medium mb-3 flex items-center gap-2">
              <Type className="h-4 w-4" />
              {t.fontSection}
            </h3>
            <div>
              <label className="block text-sm font-medium mb-2">{t.fontSize}</label>
              <select
                value={fontSize}
                onChange={(e) => setFontSize(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="small">Small</option>
                <option value="medium">Medium</option>
                <option value="large">Large</option>
              </select>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4">
            <button className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-medium">
              {t.saveSettings}
            </button>
            <button className="px-6 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors font-medium">
              {t.resetDefaults}
            </button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default AppearanceSettings
