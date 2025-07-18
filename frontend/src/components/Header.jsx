import { Menu, Bell, User, Globe } from 'lucide-react'
import { Button } from '@/components/ui/button'

const Header = ({ onMenuClick, language, onLanguageToggle }) => {
  const currentDate = new Date().toLocaleDateString(language === 'nl' ? 'nl-NL' : 'en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })

  const translations = {
    en: {
      welcome: 'Welcome back, Hans',
      notifications: 'Notifications',
      profile: 'Profile',
      language: 'Language'
    },
    nl: {
      welcome: 'Welkom terug, Hans',
      notifications: 'Meldingen',
      profile: 'Profiel',
      language: 'Taal'
    }
  }

  const t = translations[language]

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="flex items-center justify-between px-6 py-4">
        <div className="flex items-center space-x-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={onMenuClick}
            className="lg:hidden"
          >
            <Menu className="h-5 w-5" />
          </Button>
          
          <div>
            <h2 className="text-xl font-semibold text-gray-900">{t.welcome}</h2>
            <p className="text-sm text-gray-500">{currentDate}</p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={onLanguageToggle}
            className="flex items-center space-x-2"
            title={t.language}
          >
            <Globe className="h-4 w-4" />
            <span className="text-sm font-medium">{language.toUpperCase()}</span>
          </Button>

          <Button
            variant="ghost"
            size="sm"
            className="relative"
            title={t.notifications}
          >
            <Bell className="h-5 w-5" />
            <span className="absolute -top-1 -right-1 h-3 w-3 bg-red-500 rounded-full"></span>
          </Button>

          <Button
            variant="ghost"
            size="sm"
            className="flex items-center space-x-2"
            title={t.profile}
          >
            <User className="h-5 w-5" />
            <span className="hidden sm:inline text-sm">Hans</span>
          </Button>
        </div>
      </div>
    </header>
  )
}

export default Header

