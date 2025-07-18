import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Lightbulb, Sparkles } from 'lucide-react'

const PlantRecommendations = ({ language }) => {
  const translations = {
    en: {
      title: 'Plant Recommendations',
      subtitle: 'Get AI-powered plant recommendations for your projects',
      getRecommendations: 'Get AI Recommendations',
      comingSoon: 'Coming Soon',
      description: 'AI-powered plant recommendation system with site analysis will be available here.'
    },
    nl: {
      title: 'Plant Aanbevelingen',
      subtitle: 'Krijg AI-gestuurde plantaanbevelingen voor uw projecten',
      getRecommendations: 'AI-Aanbevelingen Krijgen',
      comingSoon: 'Binnenkort Beschikbaar',
      description: 'AI-gestuurd plantaanbevelingssysteem met locatieanalyse komt hier beschikbaar.'
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
          <Sparkles className="h-4 w-4" />
          <span>{t.getRecommendations}</span>
        </Button>
      </div>

      <Card>
        <CardContent className="p-12">
          <div className="text-center">
            <Lightbulb className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">{t.comingSoon}</h3>
            <p className="text-gray-500">{t.description}</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default PlantRecommendations

