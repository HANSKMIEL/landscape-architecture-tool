import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Users, Plus } from 'lucide-react'

const Clients = ({ language }) => {
  const translations = {
    en: {
      title: 'Clients',
      subtitle: 'Manage your landscape architecture clients and their projects',
      addClient: 'Add Client',
      comingSoon: 'Coming Soon',
      description: 'Client management with project relationships will be available here.'
    },
    nl: {
      title: 'Klanten',
      subtitle: 'Beheer uw landschapsarchitectuur klanten en hun projecten',
      addClient: 'Klant Toevoegen',
      comingSoon: 'Binnenkort Beschikbaar',
      description: 'Klantbeheer met projectrelaties komt hier beschikbaar.'
    }
  }

  const t = translations[language]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t.title}</h1>
          <p className="text-gray-600">{t.subtitle}</p>
        </div>
        <Button className="flex items-center space-x-2">
          <Plus className="h-4 w-4" />
          <span>{t.addClient}</span>
        </Button>
      </div>

      <Card>
        <CardContent className="p-12">
          <div className="text-center">
            <Users className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">{t.comingSoon}</h3>
            <p className="text-gray-500">{t.description}</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default Clients

