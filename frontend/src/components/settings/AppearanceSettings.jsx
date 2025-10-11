import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Palette, Type, Paintbrush, Monitor, Sun, Moon } from 'lucide-react';
import { useLanguage } from '../../i18n/LanguageProvider';

const translationDefaults = {
  title: 'Appearance Settings',
  subtitle: 'Customize the look and feel of your application',
  theme: {
    sectionTitle: 'Theme',
    light: 'Light Mode',
    dark: 'Dark Mode'
  },
  colorScheme: {
    sectionTitle: 'Color Scheme',
    options: {
      blue: 'Blue',
      green: 'Green',
      purple: 'Purple',
      orange: 'Orange'
    }
  },
  typography: {
    sectionTitle: 'Typography',
    fontSizeLabel: 'Font Size',
    sizes: {
      small: 'Small',
      medium: 'Medium',
      large: 'Large'
    }
  },
  actions: {
    save: 'Save Settings',
    reset: 'Reset to Defaults',
    saveSuccess: 'Appearance settings saved!',
    saveError: 'Unable to save appearance settings. Please try again.',
    resetSuccess: 'Appearance settings reset to defaults!'
  }
};

const getTranslationDefault = (path) =>
  path.split('.').reduce((acc, segment) => (acc && acc[segment] !== undefined ? acc[segment] : undefined), translationDefaults);

const DEFAULT_APPEARANCE_SETTINGS = {
  theme: 'light',
  colorScheme: 'blue',
  fontSize: 'medium'
};

const COLOR_VALUES = {
  blue: '#3B82F6',
  green: '#10B981',
  purple: '#8B5CF6',
  orange: '#F59E0B'
};

const AppearanceSettings = () => {
  const { t } = useLanguage();

  const [theme, setTheme] = useState(DEFAULT_APPEARANCE_SETTINGS.theme);
  const [colorScheme, setColorScheme] = useState(DEFAULT_APPEARANCE_SETTINGS.colorScheme);
  const [fontSize, setFontSize] = useState(DEFAULT_APPEARANCE_SETTINGS.fontSize);

  useEffect(() => {
    try {
      const storedSettings = localStorage.getItem('appearanceSettings');
      if (!storedSettings) {
        return;
      }

      const parsedSettings = JSON.parse(storedSettings);
      if (parsedSettings.theme) {
        setTheme(parsedSettings.theme);
      }
      if (parsedSettings.colorScheme) {
        setColorScheme(parsedSettings.colorScheme);
      }
      if (parsedSettings.fontSize) {
        setFontSize(parsedSettings.fontSize);
      }
    } catch (error) {
      console.error('Failed to load appearance settings from storage:', error);
    }
  }, []);

  const translate = useCallback(
    (key) => t(`settings.appearance.${key}`, getTranslationDefault(key) ?? key),
    [t]
  );

  const uiText = useMemo(
    () => ({
      title: translate('title'),
      subtitle: translate('subtitle'),
      themeSectionTitle: translate('theme.sectionTitle'),
      lightMode: translate('theme.light'),
      darkMode: translate('theme.dark'),
      colorSchemeSectionTitle: translate('colorScheme.sectionTitle'),
      colorOptions: {
        blue: translate('colorScheme.options.blue'),
        green: translate('colorScheme.options.green'),
        purple: translate('colorScheme.options.purple'),
        orange: translate('colorScheme.options.orange')
      },
      typographySectionTitle: translate('typography.sectionTitle'),
      fontSizeLabel: translate('typography.fontSizeLabel'),
      fontSizes: {
        small: translate('typography.sizes.small'),
        medium: translate('typography.sizes.medium'),
        large: translate('typography.sizes.large')
      },
      save: translate('actions.save'),
      reset: translate('actions.reset'),
      saveSuccess: translate('actions.saveSuccess'),
      saveError: translate('actions.saveError'),
      resetSuccess: translate('actions.resetSuccess')
    }),
    [translate]
  );

  const colorOptions = useMemo(
    () => ['blue', 'green', 'purple', 'orange'],
    []
  );

  const fontSizeOptions = useMemo(
    () => ['small', 'medium', 'large'],
    []
  );

  const saveSettings = useCallback(() => {
    const settingsToSave = {
      theme,
      colorScheme,
      fontSize,
      timestamp: new Date().toISOString()
    };

    try {
      localStorage.setItem('appearanceSettings', JSON.stringify(settingsToSave));
      window.alert(uiText.saveSuccess);
    } catch (error) {
      console.error('Failed to save appearance settings:', error);
      window.alert(uiText.saveError);
    }
  }, [colorScheme, fontSize, theme, uiText.saveError, uiText.saveSuccess]);

  const resetSettings = useCallback(() => {
    setTheme(DEFAULT_APPEARANCE_SETTINGS.theme);
    setColorScheme(DEFAULT_APPEARANCE_SETTINGS.colorScheme);
    setFontSize(DEFAULT_APPEARANCE_SETTINGS.fontSize);

    try {
      localStorage.removeItem('appearanceSettings');
    } catch (error) {
      console.error('Failed to clear appearance settings from storage:', error);
    }

    window.alert(uiText.resetSuccess);
  }, [uiText.resetSuccess]);

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Palette className="h-5 w-5" />
            {uiText.title}
          </CardTitle>
          <p className="text-sm text-gray-600">{uiText.subtitle}</p>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <h3 className="text-lg font-medium mb-3 flex items-center gap-2">
              <Monitor className="h-4 w-4" />
              {uiText.themeSectionTitle}
            </h3>
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => setTheme('light')}
                className={`p-3 rounded-lg border-2 transition-all ${theme === 'light' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                  }`}
              >
                <Sun className="h-5 w-5 mx-auto mb-2" />
                <span className="text-sm font-medium">{uiText.lightMode}</span>
              </button>
              <button
                onClick={() => setTheme('dark')}
                className={`p-3 rounded-lg border-2 transition-all ${theme === 'dark' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                  }`}
              >
                <Moon className="h-5 w-5 mx-auto mb-2" />
                <span className="text-sm font-medium">{uiText.darkMode}</span>
              </button>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-medium mb-3 flex items-center gap-2">
              <Paintbrush className="h-4 w-4" />
              {uiText.colorSchemeSectionTitle}
            </h3>
            <div className="grid grid-cols-4 gap-3">
              {colorOptions.map((color) => (
                <button
                  key={color}
                  onClick={() => setColorScheme(color)}
                  className={`h-12 rounded-lg border-2 transition-all ${colorScheme === color ? 'border-gray-800 scale-105' : 'border-gray-200 hover:border-gray-300'
                    }`}
                  style={{ backgroundColor: COLOR_VALUES[color] }}
                  aria-label={uiText.colorOptions[color]}
                />
              ))}
            </div>
          </div>

          <div>
            <h3 className="text-lg font-medium mb-3 flex items-center gap-2">
              <Type className="h-4 w-4" />
              {uiText.typographySectionTitle}
            </h3>
            <div>
              <label className="block text-sm font-medium mb-2">{uiText.fontSizeLabel}</label>
              <select
                value={fontSize}
                onChange={(event) => setFontSize(event.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {fontSizeOptions.map((option) => (
                  <option key={option} value={option}>
                    {uiText.fontSizes[option]}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex gap-3 pt-4">
            <Button onClick={saveSettings} className="px-6">
              {uiText.save}
            </Button>
            <Button onClick={resetSettings} variant="outline" className="px-6">
              {uiText.reset}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AppearanceSettings;
