import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { FileText, Download } from 'lucide-react'

const Reports = ({ language }) => {
  const translations = {
    en: {
      title: 'Reports',
      subtitle: 'Generate professional reports for your landscape architecture projects',
      generateReport: 'Generate Report',
      comingSoon: 'Coming Soon',
      description: 'Professional PDF report generation with project specifications and costs will be available here.'
    },
    nl: {
      title: 'Rapporten',
      subtitle: 'Genereer professionele rapporten voor uw landschapsarchitectuur projecten',
      generateReport: 'Rapport Genereren',
      comingSoon: 'Binnenkort Beschikbaar',
      description: 'Professionele PDF-rapportgeneratie met projectspecificaties en kosten komt hier beschikbaar.'
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
          <Download className="h-4 w-4" />
          <span>{t.generateReport}</span>
        </Button>
      </div>

      <Card>
        <CardContent className="p-12">
          <div className="text-center">
            <FileText className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">{t.comingSoon}</h3>
            <p className="text-gray-500">{t.description}</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default Reports

