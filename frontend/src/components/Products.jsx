import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Package, Plus, Upload } from 'lucide-react'

const Products = ({ language }) => {
  const translations = {
    en: {
      title: 'Products',
      subtitle: 'Manage your landscape architecture products and materials',
      addProduct: 'Add Product',
      importExcel: 'Import Excel/CSV',
      comingSoon: 'Coming Soon',
      description: 'Product management with Excel/CSV import functionality will be available here.'
    },
    nl: {
      title: 'Producten',
      subtitle: 'Beheer uw landschapsarchitectuur producten en materialen',
      addProduct: 'Product Toevoegen',
      importExcel: 'Excel/CSV Importeren',
      comingSoon: 'Binnenkort Beschikbaar',
      description: 'Productbeheer met Excel/CSV import functionaliteit komt hier beschikbaar.'
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
        <div className="flex items-center space-x-3">
          <Button variant="outline" className="flex items-center space-x-2">
            <Upload className="h-4 w-4" />
            <span>{t.importExcel}</span>
          </Button>
          <Button className="flex items-center space-x-2">
            <Plus className="h-4 w-4" />
            <span>{t.addProduct}</span>
          </Button>
        </div>
      </div>

      <Card>
        <CardContent className="p-12">
          <div className="text-center">
            <Package className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">{t.comingSoon}</h3>
            <p className="text-gray-500">{t.description}</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default Products

