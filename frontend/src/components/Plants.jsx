import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { 
  Search, 
  Plus, 
  Leaf, 
  Sun, 
  Droplets, 
  Lightbulb,
  Filter,
  Star
} from 'lucide-react'
import { toast } from 'sonner'
import apiService from '../services/api'

const Plants = ({ language }) => {
  const [plants, setPlants] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [totalPlants, setTotalPlants] = useState(0)
  const [filters, setFilters] = useState({
    category: '',
    sun_requirements: '',
    water_requirements: '',
    native_only: false
  })

  const translations = {
    en: {
      title: 'Plants',
      subtitle: 'Manage your plant database and get AI recommendations',
      search: 'Search plants...',
      addPlant: 'Add Plant',
      getRecommendations: 'Get AI Recommendations',
      filters: 'Filters',
      category: 'Category',
      sunRequirements: 'Sun Requirements',
      waterRequirements: 'Water Requirements',
      nativeOnly: 'Native Plants Only',
      scientificName: 'Scientific Name',
      commonName: 'Common Name',
      height: 'Height',
      width: 'Width',
      bloomTime: 'Bloom Time',
      bloomColor: 'Bloom Color',
      maintenance: 'Maintenance',
      price: 'Price',
      supplier: 'Supplier',
      loading: 'Loading plants...',
      noPlants: 'No plants found',
      error: 'Error loading plants',
      native: 'Native',
      deerResistant: 'Deer Resistant',
      droughtTolerant: 'Drought Tolerant',
      attractsPollinators: 'Attracts Pollinators',
      low: 'Low',
      medium: 'Medium',
      high: 'High',
      fullSun: 'Full Sun',
      partialSun: 'Partial Sun',
      shade: 'Shade'
    },
    nl: {
      title: 'Planten',
      subtitle: 'Beheer uw plantendatabase en krijg AI-aanbevelingen',
      search: 'Zoek planten...',
      addPlant: 'Plant Toevoegen',
      getRecommendations: 'AI-Aanbevelingen Krijgen',
      filters: 'Filters',
      category: 'Categorie',
      sunRequirements: 'Zonvereisten',
      waterRequirements: 'Watervereisten',
      nativeOnly: 'Alleen Inheemse Planten',
      scientificName: 'Wetenschappelijke Naam',
      commonName: 'Nederlandse Naam',
      height: 'Hoogte',
      width: 'Breedte',
      bloomTime: 'Bloeitijd',
      bloomColor: 'Bloeikleur',
      maintenance: 'Onderhoud',
      price: 'Prijs',
      supplier: 'Leverancier',
      loading: 'Planten laden...',
      noPlants: 'Geen planten gevonden',
      error: 'Fout bij laden van planten',
      native: 'Inheems',
      deerResistant: 'Hertresistent',
      droughtTolerant: 'Droogteresistent',
      attractsPollinators: 'Trekt Bestuivers Aan',
      low: 'Laag',
      medium: 'Gemiddeld',
      high: 'Hoog',
      fullSun: 'Volle Zon',
      partialSun: 'Gedeeltelijke Zon',
      shade: 'Schaduw'
    }
  }

  const t = translations[language]

  useEffect(() => {
    loadPlants()
  }, [searchTerm, filters])

  const loadPlants = async () => {
    try {
      setLoading(true)
      const params = {
        ...(searchTerm && { search: searchTerm }),
        ...filters
      }
      const data = await apiService.getPlants(params)
      setPlants(data.plants || [])
      setTotalPlants(data.total || 0)
    } catch (error) {
      console.error('Error loading plants:', error)
      toast.error(`${t.error}: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value)
  }

  const getMaintenanceLabel = (level) => {
    const labels = {
      'Low': t.low,
      'Medium': t.medium,
      'High': t.high
    }
    return labels[level] || level
  }

  const getSunRequirementsLabel = (requirement) => {
    const labels = {
      'Full Sun': t.fullSun,
      'Partial Sun': t.partialSun,
      'Shade': t.shade
    }
    return labels[requirement] || requirement
  }

  const getWaterRequirementsLabel = (requirement) => {
    const labels = {
      'Low': t.low,
      'Medium': t.medium,
      'High': t.high
    }
    return labels[requirement] || requirement
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t.title}</h1>
          <p className="text-gray-600">{t.subtitle}</p>
        </div>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600 mx-auto"></div>
            <p className="mt-2 text-gray-500">{t.loading}</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t.title}</h1>
          <p className="text-gray-600">{t.subtitle}</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button variant="outline" className="flex items-center space-x-2">
            <Lightbulb className="h-4 w-4" />
            <span>{t.getRecommendations}</span>
          </Button>
          <Button className="flex items-center space-x-2">
            <Plus className="h-4 w-4" />
            <span>{t.addPlant}</span>
          </Button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        <div className="lg:col-span-2">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <Input
              placeholder={t.search}
              value={searchTerm}
              onChange={handleSearchChange}
              className="pl-10"
            />
          </div>
        </div>
        <Button variant="outline" className="flex items-center space-x-2">
          <Filter className="h-4 w-4" />
          <span>{t.filters}</span>
        </Button>
      </div>

      {/* Plants List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>{t.title} ({totalPlants})</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {plants.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {plants.map((plant) => (
                <div key={plant.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between mb-3">
                    <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                      <Leaf className="h-6 w-6 text-green-600" />
                    </div>
                    {plant.native_to_netherlands && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        {t.native}
                      </span>
                    )}
                  </div>

                  <div className="space-y-2">
                    <h3 className="text-lg font-semibold text-gray-900">{plant.name}</h3>
                    {plant.scientific_name && (
                      <p className="text-sm italic text-gray-600">{plant.scientific_name}</p>
                    )}
                    {plant.common_name && (
                      <p className="text-sm text-gray-600">{plant.common_name}</p>
                    )}

                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      {plant.sun_requirements && (
                        <div className="flex items-center space-x-1">
                          <Sun className="h-4 w-4" />
                          <span>{getSunRequirementsLabel(plant.sun_requirements)}</span>
                        </div>
                      )}
                      {plant.water_requirements && (
                        <div className="flex items-center space-x-1">
                          <Droplets className="h-4 w-4" />
                          <span>{getWaterRequirementsLabel(plant.water_requirements)}</span>
                        </div>
                      )}
                    </div>

                    {(plant.mature_height || plant.mature_width) && (
                      <div className="text-sm text-gray-600">
                        {plant.mature_height && <span>{t.height}: {plant.mature_height}</span>}
                        {plant.mature_height && plant.mature_width && <span> × </span>}
                        {plant.mature_width && <span>{t.width}: {plant.mature_width}</span>}
                      </div>
                    )}

                    {plant.bloom_time && (
                      <div className="text-sm text-gray-600">
                        <span>{t.bloomTime}: {plant.bloom_time}</span>
                        {plant.bloom_color && <span> ({plant.bloom_color})</span>}
                      </div>
                    )}

                    {plant.maintenance_level && (
                      <div className="text-sm text-gray-600">
                        {t.maintenance}: {getMaintenanceLabel(plant.maintenance_level)}
                      </div>
                    )}

                    <div className="flex flex-wrap gap-1 mt-3">
                      {plant.deer_resistant && (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          {t.deerResistant}
                        </span>
                      )}
                      {plant.drought_tolerant && (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                          {t.droughtTolerant}
                        </span>
                      )}
                      {plant.attracts_pollinators && (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                          {t.attractsPollinators}
                        </span>
                      )}
                    </div>

                    <div className="flex items-center justify-between pt-3 border-t">
                      {plant.price && (
                        <span className="text-lg font-semibold text-green-600">
                          €{plant.price.toFixed(2)}
                        </span>
                      )}
                      {plant.supplier_name && (
                        <span className="text-sm text-gray-500">{plant.supplier_name}</span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Leaf className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">{t.noPlants}</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default Plants

