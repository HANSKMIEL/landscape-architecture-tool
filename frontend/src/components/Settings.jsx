import { Card, CardContent } from '@/components/ui/card'
import { Settings as SettingsIcon } from 'lucide-react'

const Settings = ({ language }) => {
  const translations = {
    en: {
      title: 'Settings',
      subtitle: 'Configure your landscape architecture application preferences',
      comingSoon: 'Coming Soon',
      description: 'Application settings and preferences will be available here.'
    },
    nl: {
      title: 'Instellingen',
      subtitle: 'Configureer uw landschapsarchitectuur applicatie voorkeuren',
      comingSoon: 'Binnenkort Beschikbaar',
      description: 'Applicatie-instellingen en voorkeuren komen hier beschikbaar.'
    }
  }

  const t = translations[language]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{t.title}</h1>
        <p className="text-gray-600">{t.subtitle}</p>
      </div>

      <Card>
        <CardContent className="p-12">
          <div className="text-center">
            <SettingsIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">{t.comingSoon}</h3>
            <p className="text-gray-500">{t.description}</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default Settings

