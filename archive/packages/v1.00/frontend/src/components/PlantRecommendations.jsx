import { useLanguage } from "../i18n/LanguageProvider";
import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Separator } from '@/components/ui/separator'
import { 
  Lightbulb, 
  Sparkles, 
  Search, 
  Star, 
  Heart, 
  Download,
  AlertTriangle,
  CheckCircle,
  Leaf,
  Sun,
  Droplets,
  TreePine,
  Palette
} from 'lucide-react'

const PlantRecommendations = () => {
  const [criteriaOptions, setCriteriaOptions] = useState(null)
  const [searchCriteria, setSearchCriteria] = useState({
    hardiness_zone: '',
    sun_exposure: '',
    soil_type: '',
    soil_ph: '',
    moisture_level: '',
    desired_height_min: '',
    desired_height_max: '',
    desired_width_min: '',
    desired_width_max: '',
    color_preferences: [],
    bloom_season: '',
    maintenance_level: '',
    budget_range: '',
    native_preference: false,
    wildlife_friendly: false,
    deer_resistant_required: false,
    pollinator_friendly_required: false,
    container_planting: false,
    screening_purpose: false,
    hedging_purpose: false,
    groundcover_purpose: false,
    slope_planting: false,
  })
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [requestId, setRequestId] = useState(null)
  const [selectedPlants, setSelectedPlants] = useState([])
  const [showFeedback, setShowFeedback] = useState(false)

  const translations = {
    en: {
      title: 'Plant Recommendations',
      subtitle: 'Get AI-powered plant recommendations for your projects',
      getRecommendations: 'Get Recommendations',
      searchCriteria: 'Search Criteria',
      results: 'Recommendations',
      feedback: 'Feedback',
      
      // Criteria sections
      environmental: 'Environmental Conditions',
      designPrefs: 'Design Preferences',
      maintenance: 'Maintenance & Budget',
      specialRequirements: 'Special Requirements',
      projectContext: 'Project Context',
      
      // Form fields
      hardinessZone: 'Hardiness Zone',
      sunExposure: 'Sun Exposure',
      soilType: 'Soil Type',
      soilPh: 'Soil pH',
      moistureLevel: 'Moisture Level',
      desiredHeight: 'Desired Height (meters)',
      desiredWidth: 'Desired Width (meters)',
      colorPreferences: 'Color Preferences',
      bloomSeason: 'Bloom Season',
      maintenanceLevel: 'Maintenance Level',
      budgetRange: 'Budget Range',
      
      // Special requirements
      nativePreference: 'Prefer native plants',
      wildlifeFriendly: 'Wildlife friendly',
      deerResistant: 'Deer resistant required',
      pollinatorFriendly: 'Pollinator friendly required',
      
      // Project context
      containerPlanting: 'Container planting',
      screeningPurpose: 'For screening',
      hedgingPurpose: 'For hedging',
      groundcoverPurpose: 'For groundcover',
      slopePlanting: 'Slope planting',
      
      // Results
      score: 'Match Score',
      matchReasons: 'Why This Plant',
      warnings: 'Considerations',
      exportResults: 'Export Results',
      provideFeedback: 'Provide Feedback',
      
      // Feedback
      helpful: 'Was this helpful?',
      selectedPlants: 'Which plants did you select?',
      additionalComments: 'Additional comments',
      submitFeedback: 'Submit Feedback',
      
      // Messages
      noResults: 'No plant recommendations found. Try adjusting your criteria.',
      searchError: 'Error getting recommendations. Please try again.',
      loadingResults: 'Finding the perfect plants for you...',
      feedbackSubmitted: 'Thank you for your feedback!',
    },
    nl: {
      title: 'Plant Aanbevelingen',
      subtitle: 'Krijg AI-gestuurde plantaanbevelingen voor uw projecten',
      getRecommendations: 'Aanbevelingen Krijgen',
      searchCriteria: 'Zoek Criteria',
      results: 'Aanbevelingen',
      feedback: 'Feedback',
      
      environmental: 'Omgevingsomstandigheden',
      designPrefs: 'Ontwerp Voorkeuren',
      maintenance: 'Onderhoud & Budget',
      specialRequirements: 'Speciale Eisen',
      projectContext: 'Project Context',
      
      hardinessZone: 'Winterhardheidszone',
      sunExposure: 'Zonblootstelling',
      soilType: 'Grondsoort',
      soilPh: 'Grond pH',
      moistureLevel: 'Vochtniveau',
      desiredHeight: 'Gewenste Hoogte (meters)',
      desiredWidth: 'Gewenste Breedte (meters)',
      colorPreferences: 'Kleur Voorkeuren',
      bloomSeason: 'Bloeiseizoen',
      maintenanceLevel: 'Onderhoudsniveau',
      budgetRange: 'Budget Bereik',
      
      nativePreference: 'Voorkeur voor inheemse planten',
      wildlifeFriendly: 'Diervriendelijk',
      deerResistant: 'Hertenbestendig vereist',
      pollinatorFriendly: 'Bestuivervriendelijk vereist',
      
      containerPlanting: 'Container beplanting',
      screeningPurpose: 'Voor afscherming',
      hedgingPurpose: 'Voor hagen',
      groundcoverPurpose: 'Voor bodembedekking',
      slopePlanting: 'Helling beplanting',
      
      score: 'Match Score',
      matchReasons: 'Waarom Deze Plant',
      warnings: 'Overwegingen',
      exportResults: 'Resultaten Exporteren',
      provideFeedback: 'Feedback Geven',
      
      helpful: 'Was dit nuttig?',
      selectedPlants: 'Welke planten heeft u geselecteerd?',
      additionalComments: 'Aanvullende opmerkingen',
      submitFeedback: 'Feedback Versturen',
      
      noResults: 'Geen plantaanbevelingen gevonden. Pas uw criteria aan.',
      searchError: 'Fout bij het krijgen van aanbevelingen. Probeer opnieuw.',
      loadingResults: 'De perfecte planten voor u vinden...',
      feedbackSubmitted: 'Bedankt voor uw feedback!',
    }
  }

  const { t } = useLanguage()

  // Load criteria options on component mount
  useEffect(() => {
    fetchCriteriaOptions()
  }, [])

  const fetchCriteriaOptions = async () => {
    try {
      const response = await fetch('/api/plant-recommendations/criteria-options')
      if (response.ok) {
        const options = await response.json()
        setCriteriaOptions(options)
      }
    } catch (error) {
      console.error('Error fetching criteria options:', error)
    }
  }

  const handleCriteriaChange = (field, value) => {
    setSearchCriteria(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleColorPreferenceToggle = (color) => {
    setSearchCriteria(prev => ({
      ...prev,
      color_preferences: prev.color_preferences.includes(color)
        ? prev.color_preferences.filter(c => c !== color)
        : [...prev.color_preferences, color]
    }))
  }

  const handleSearch = async () => {
    setLoading(true)
    setError(null)
    setRecommendations([])
    
    try {
      const response = await fetch('/api/plant-recommendations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(searchCriteria)
      })
      
      if (response.ok) {
        const data = await response.json()
        setRecommendations(data.recommendations)
        setRequestId(data.request_id)
      } else {
        setError(t.searchError)
      }
    } catch (error) {
      setError(t.searchError)
      console.error('Error getting recommendations:', error)
    } finally {
      setLoading(false)
    }
  }

  const handlePlantSelection = (plantId) => {
    setSelectedPlants(prev => 
      prev.includes(plantId)
        ? prev.filter(id => id !== plantId)
        : [...prev, plantId]
    )
  }

  const handleExport = async () => {
    if (!requestId) return
    
    try {
      const response = await fetch('/api/plant-recommendations/export', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          request_id: requestId,
          format: 'csv'
        })
      })
      
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `plant_recommendations_${requestId}.csv`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      }
    } catch (error) {
      console.error('Error exporting results:', error)
    }
  }

  // eslint-disable-next-line no-unused-vars
  const submitFeedback = async (feedbackData) => {
    if (!requestId) return
    
    try {
      const response = await fetch('/api/plant-recommendations/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          request_id: requestId,
          feedback: feedbackData,
          rating: feedbackData.rating
        })
      })
      
      if (response.ok) {
        setShowFeedback(false)
        // Show success message
      }
    } catch (error) {
      console.error('Error submitting feedback:', error)
    }
  }

  const renderCriteriaForm = () => (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Search className="h-5 w-5" />
          <span>{t.searchCriteria}</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Environmental Conditions */}
        <div>
          <h3 className="font-semibold mb-3 flex items-center space-x-2">
            <Sun className="h-4 w-4" />
            <span>{t.environmental}</span>
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <Label>{t.hardinessZone}</Label>
              <Select value={searchCriteria.hardiness_zone} onValueChange={(value) => handleCriteriaChange('hardiness_zone', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select zone" />
                </SelectTrigger>
                <SelectContent>
                  {criteriaOptions?.hardiness_zones?.map(zone => (
                    <SelectItem key={zone} value={zone}>{zone}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label>{t.sunExposure}</Label>
              <Select value={searchCriteria.sun_exposure} onValueChange={(value) => handleCriteriaChange('sun_exposure', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select exposure" />
                </SelectTrigger>
                <SelectContent>
                  {criteriaOptions?.sun_exposures?.map(exposure => (
                    <SelectItem key={exposure} value={exposure}>{exposure}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label>{t.soilType}</Label>
              <Select value={searchCriteria.soil_type} onValueChange={(value) => handleCriteriaChange('soil_type', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select soil type" />
                </SelectTrigger>
                <SelectContent>
                  {criteriaOptions?.soil_types?.map(soil => (
                    <SelectItem key={soil} value={soil}>{soil}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label>{t.soilPh}</Label>
              <Input 
                type="number" 
                step="0.1" 
                min="1" 
                max="14"
                value={searchCriteria.soil_ph}
                onChange={(e) => handleCriteriaChange('soil_ph', e.target.value)}
                placeholder="6.5"
              />
            </div>
            
            <div>
              <Label>{t.moistureLevel}</Label>
              <Select value={searchCriteria.moisture_level} onValueChange={(value) => handleCriteriaChange('moisture_level', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select moisture" />
                </SelectTrigger>
                <SelectContent>
                  {criteriaOptions?.moisture_levels?.map(level => (
                    <SelectItem key={level} value={level}>{level}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>

        <Separator />

        {/* Design Preferences */}
        <div>
          <h3 className="font-semibold mb-3 flex items-center space-x-2">
            <Palette className="h-4 w-4" />
            <span>{t.designPrefs}</span>
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label>{t.desiredHeight}</Label>
              <div className="flex space-x-2">
                <Input 
                  type="number" 
                  step="0.1"
                  value={searchCriteria.desired_height_min}
                  onChange={(e) => handleCriteriaChange('desired_height_min', e.target.value)}
                  placeholder="Min"
                />
                <Input 
                  type="number" 
                  step="0.1"
                  value={searchCriteria.desired_height_max}
                  onChange={(e) => handleCriteriaChange('desired_height_max', e.target.value)}
                  placeholder="Max"
                />
              </div>
            </div>
            
            <div>
              <Label>{t.desiredWidth}</Label>
              <div className="flex space-x-2">
                <Input 
                  type="number" 
                  step="0.1"
                  value={searchCriteria.desired_width_min}
                  onChange={(e) => handleCriteriaChange('desired_width_min', e.target.value)}
                  placeholder="Min"
                />
                <Input 
                  type="number" 
                  step="0.1"
                  value={searchCriteria.desired_width_max}
                  onChange={(e) => handleCriteriaChange('desired_width_max', e.target.value)}
                  placeholder="Max"
                />
              </div>
            </div>
            
            <div>
              <Label>{t.bloomSeason}</Label>
              <Select value={searchCriteria.bloom_season} onValueChange={(value) => handleCriteriaChange('bloom_season', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select season" />
                </SelectTrigger>
                <SelectContent>
                  {criteriaOptions?.bloom_seasons?.map(season => (
                    <SelectItem key={season} value={season}>{season}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label>{t.colorPreferences}</Label>
              <div className="flex flex-wrap gap-2 mt-2">
                {criteriaOptions?.bloom_colors?.slice(0, 8).map(color => (
                  <Badge 
                    key={color}
                    variant={searchCriteria.color_preferences.includes(color) ? "default" : "outline"}
                    className="cursor-pointer"
                    onClick={() => handleColorPreferenceToggle(color)}
                  >
                    {color}
                  </Badge>
                ))}
              </div>
            </div>
          </div>
        </div>

        <Separator />

        {/* Maintenance & Budget */}
        <div>
          <h3 className="font-semibold mb-3 flex items-center space-x-2">
            <TreePine className="h-4 w-4" />
            <span>{t.maintenance}</span>
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label>{t.maintenanceLevel}</Label>
              <Select value={searchCriteria.maintenance_level} onValueChange={(value) => handleCriteriaChange('maintenance_level', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select level" />
                </SelectTrigger>
                <SelectContent>
                  {criteriaOptions?.maintenance_levels?.map(level => (
                    <SelectItem key={level} value={level}>{level}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label>{t.budgetRange}</Label>
              <Select value={searchCriteria.budget_range} onValueChange={(value) => handleCriteriaChange('budget_range', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select range" />
                </SelectTrigger>
                <SelectContent>
                  {criteriaOptions?.budget_ranges?.map(range => (
                    <SelectItem key={range} value={range}>{range}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>

        <Separator />

        {/* Special Requirements */}
        <div>
          <h3 className="font-semibold mb-3 flex items-center space-x-2">
            <Leaf className="h-4 w-4" />
            <span>{t.specialRequirements}</span>
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { key: 'native_preference', label: t.nativePreference },
              { key: 'wildlife_friendly', label: t.wildlifeFriendly },
              { key: 'deer_resistant_required', label: t.deerResistant },
              { key: 'pollinator_friendly_required', label: t.pollinatorFriendly },
            ].map(requirement => (
              <div key={requirement.key} className="flex items-center space-x-2">
                <Checkbox
                  checked={searchCriteria[requirement.key]}
                  onCheckedChange={(checked) => handleCriteriaChange(requirement.key, checked)}
                />
                <Label>{requirement.label}</Label>
              </div>
            ))}
          </div>
        </div>

        <Separator />

        {/* Project Context */}
        <div>
          <h3 className="font-semibold mb-3 flex items-center space-x-2">
            <Droplets className="h-4 w-4" />
            <span>{t.projectContext}</span>
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { key: 'container_planting', label: t.containerPlanting },
              { key: 'screening_purpose', label: t.screeningPurpose },
              { key: 'hedging_purpose', label: t.hedgingPurpose },
              { key: 'groundcover_purpose', label: t.groundcoverPurpose },
              { key: 'slope_planting', label: t.slopePlanting },
            ].map(context => (
              <div key={context.key} className="flex items-center space-x-2">
                <Checkbox
                  checked={searchCriteria[context.key]}
                  onCheckedChange={(checked) => handleCriteriaChange(context.key, checked)}
                />
                <Label>{context.label}</Label>
              </div>
            ))}
          </div>
        </div>

        <div className="flex justify-end pt-4">
          <Button 
            onClick={handleSearch} 
            disabled={loading}
            className="flex items-center space-x-2"
          >
            <Sparkles className="h-4 w-4" />
            <span>{loading ? t.loadingResults : t.getRecommendations}</span>
          </Button>
        </div>
      </CardContent>
    </Card>
  )

  const renderResults = () => {
    if (loading) {
      return (
        <Card>
          <CardContent className="p-12">
            <div className="text-center">
              <Sparkles className="h-16 w-16 text-blue-500 mx-auto mb-4 animate-spin" />
              <p className="text-gray-600">{t.loadingResults}</p>
            </div>
          </CardContent>
        </Card>
      )
    }

    if (error) {
      return (
        <Card>
          <CardContent className="p-12">
            <div className="text-center">
              <AlertTriangle className="h-16 w-16 text-red-500 mx-auto mb-4" />
              <p className="text-red-600">{error}</p>
            </div>
          </CardContent>
        </Card>
      )
    }

    if (recommendations.length === 0) {
      return (
        <Card>
          <CardContent className="p-12">
            <div className="text-center">
              <Lightbulb className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">{t.noResults}</p>
            </div>
          </CardContent>
        </Card>
      )
    }

    return (
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h3 className="text-lg font-semibold">
            {recommendations.length} {t.results}
          </h3>
          <div className="flex space-x-2">
            <Button variant="outline" onClick={handleExport}>
              <Download className="h-4 w-4 mr-2" />
              {t.exportResults}
            </Button>
            <Button variant="outline" onClick={() => setShowFeedback(true)}>
              <Heart className="h-4 w-4 mr-2" />
              {t.provideFeedback}
            </Button>
          </div>
        </div>

        {recommendations.map((rec, index) => (
          <Card key={index} className="hover:shadow-md transition-shadow">
            <CardContent className="p-6">
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h4 className="text-xl font-semibold">{rec.plant.name}</h4>
                    {rec.plant.common_name && (
                      <span className="text-gray-600">({rec.plant.common_name})</span>
                    )}
                    <Badge variant="secondary">{rec.plant.category}</Badge>
                  </div>
                  
                  <div className="flex items-center space-x-4 mb-3">
                    <div className="flex items-center space-x-1">
                      <Star className="h-4 w-4 text-yellow-500 fill-current" />
                      <span className="font-medium">{(rec.score * 100).toFixed(0)}%</span>
                      <span className="text-sm text-gray-500">{t.score}</span>
                    </div>
                    
                    {rec.plant.price && (
                      <div className="text-sm text-gray-600">
                        ${rec.plant.price}
                      </div>
                    )}
                    
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        checked={selectedPlants.includes(rec.plant.id)}
                        onCheckedChange={() => handlePlantSelection(rec.plant.id)}
                      />
                      <span className="text-sm text-gray-600">Select</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <h5 className="font-medium text-green-700 mb-2 flex items-center space-x-1">
                    <CheckCircle className="h-4 w-4" />
                    <span>{t.matchReasons}</span>
                  </h5>
                  <ul className="text-sm space-y-1">
                    {rec.match_reasons.map((reason, i) => (
                      <li key={i} className="text-green-600">• {reason}</li>
                    ))}
                  </ul>
                </div>
                
                {rec.warnings.length > 0 && (
                  <div>
                    <h5 className="font-medium text-yellow-700 mb-2 flex items-center space-x-1">
                      <AlertTriangle className="h-4 w-4" />
                      <span>{t.warnings}</span>
                    </h5>
                    <ul className="text-sm space-y-1">
                      {rec.warnings.map((warning, i) => (
                        <li key={i} className="text-yellow-600">• {warning}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Plant details */}
              <div className="border-t pt-4">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="font-medium">Height:</span>
                    <span className="ml-1">{rec.plant.height_min}-{rec.plant.height_max}m</span>
                  </div>
                  <div>
                    <span className="font-medium">Sun:</span>
                    <span className="ml-1">{rec.plant.sun_requirements}</span>
                  </div>
                  <div>
                    <span className="font-medium">Water:</span>
                    <span className="ml-1">{rec.plant.water_needs}</span>
                  </div>
                  <div>
                    <span className="font-medium">Maintenance:</span>
                    <span className="ml-1">{rec.plant.maintenance}</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
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
      </div>

      <Tabs defaultValue="search" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="search">{t.searchCriteria}</TabsTrigger>
          <TabsTrigger value="results">{t.results}</TabsTrigger>
        </TabsList>
        
        <TabsContent value="search" className="space-y-4">
          {renderCriteriaForm()}
        </TabsContent>
        
        <TabsContent value="results" className="space-y-4">
          {renderResults()}
        </TabsContent>
      </Tabs>

      {/* Feedback Modal would go here */}
      {showFeedback && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="max-w-md w-full m-4">
            <CardHeader>
              <CardTitle>{t.provideFeedback}</CardTitle>
            </CardHeader>
            <CardContent>
              {/* Feedback form implementation */}
              <div className="space-y-4">
                <div>
                  <Label>{t.helpful}</Label>
                  {/* Rating component */}
                </div>
                <div>
                  <Label>{t.additionalComments}</Label>
                  <textarea className="w-full p-2 border rounded" rows="3" />
                </div>
                <div className="flex justify-end space-x-2">
                  <Button variant="outline" onClick={() => setShowFeedback(false)}>
                    Cancel
                  </Button>
                  <Button onClick={() => setShowFeedback(false)}>
                    {t.submitFeedback}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}

export default PlantRecommendations

