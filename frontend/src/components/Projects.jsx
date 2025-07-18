import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { FolderOpen, Plus } from 'lucide-react'

const Projects = ({ language }) => {
  const translations = {
    en: {
      title: 'Projects',
      subtitle: 'Manage your landscape architecture projects and their progress',
      newProject: 'New Project',
      comingSoon: 'Coming Soon',
      description: 'Project management with plant and product assignments will be available here.'
    },
    nl: {
      title: 'Projecten',
      subtitle: 'Beheer uw landschapsarchitectuur projecten en hun voortgang',
      newProject: 'Nieuw Project',
      comingSoon: 'Binnenkort Beschikbaar',
      description: 'Projectbeheer met plant- en producttoewijzingen komt hier beschikbaar.'
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
          <span>{t.newProject}</span>
        </Button>
      </div>

      <Card>
        <CardContent className="p-12">
          <div className="text-center">
            <FolderOpen className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">{t.comingSoon}</h3>
            <p className="text-gray-500">{t.description}</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default Projects

