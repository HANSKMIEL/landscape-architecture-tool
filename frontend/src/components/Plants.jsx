import React, { useState, useEffect, useCallback } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { 
  Leaf, 
  Plus, 
  Upload, 
  Edit, 
  Trash2, 
  Search, 
  X, 
  Loader2,
  Sun,
  Droplets,
  Thermometer,
  Palette
} from 'lucide-react'
import ApiService from '../services/api'
import { useLanguage } from '../i18n/LanguageProvider'

const Plants = () => {
  const { t } = useLanguage()
  const [plants, setPlants] = useState([])
  const [suppliers, setSuppliers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [retryCount, setRetryCount] = useState(0)
  const [isRetrying, setIsRetrying] = useState(false)
  const [submitLoading, setSubmitLoading] = useState(false)
  const [deleteLoading, setDeleteLoading] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [showAddModal, setShowAddModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [editingPlant, setEditingPlant] = useState(null)
  const [totalPlants, setTotalPlants] = useState(0)

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    common_name: '',
    category: '',
    height_min: '',
    height_max: '',
    width_min: '',
    width_max: '',
    sun_requirements: '',
    soil_type: '',
    water_needs: '',
    hardiness_zone: '',
    bloom_time: '',
    bloom_color: '',
    foliage_color: '',
    native: false,
    supplier_id: '',
    price: '',
    availability: '',
    planting_season: '',
    maintenance: '',
    notes: ''
  })

  // Category options
  const categoryOptions = [
    { value: 'tree', label: t('plants.categories.tree', 'Tree') },
    { value: 'shrub', label: t('plants.categories.shrub', 'Shrub') },
    { value: 'perennial', label: t('plants.categories.perennial', 'Perennial') },
    { value: 'annual', label: t('plants.categories.annual', 'Annual') },
    { value: 'bulb', label: t('plants.categories.bulb', 'Bulb') },
    { value: 'grass', label: t('plants.categories.grass', 'Grass') },
    { value: 'fern', label: t('plants.categories.fern', 'Fern') },
    { value: 'vine', label: t('plants.categories.vine', 'Vine') },
    { value: 'groundcover', label: t('plants.categories.groundcover', 'Groundcover') }
  ]

  // Sun requirement options
  const sunOptions = [
    { value: 'full_sun', label: t('plants.sun.fullSun', 'Full Sun') },
    { value: 'partial_sun', label: t('plants.sun.partialSun', 'Partial Sun') },
    { value: 'partial_shade', label: t('plants.sun.partialShade', 'Partial Shade') },
    { value: 'full_shade', label: t('plants.sun.fullShade', 'Full Shade') }
  ]

  // Water needs options
  const waterOptions = [
    { value: 'low', label: t('plants.water.low', 'Low') },
    { value: 'medium', label: t('plants.water.medium', 'Medium') },
    { value: 'high', label: t('plants.water.high', 'High') }
  ]

  // Soil type options
  const soilOptions = [
    { value: 'clay', label: t('plants.soil.clay', 'Clay') },
    { value: 'loam', label: t('plants.soil.loam', 'Loam') },
    { value: 'sand', label: t('plants.soil.sand', 'Sand') },
    { value: 'chalk', label: t('plants.soil.chalk', 'Chalk') },
    { value: 'peat', label: t('plants.soil.peat', 'Peat') }
  ]

  // Maintenance options
  const maintenanceOptions = [
    { value: 'low', label: t('plants.maintenance.low', 'Low') },
    { value: 'medium', label: t('plants.maintenance.medium', 'Medium') },
    { value: 'high', label: t('plants.maintenance.high', 'High') }
  ]

  // Enhanced error handling with retry logic
  const handleApiError = (error, context = '') => {
    console.error(`Error in ${context}:`, error)
    
    let errorMessage = 'An unexpected error occurred'
    
    if (error.response?.data?.error) {
      errorMessage = error.response.data.error
    } else if (error.message) {
      if (error.message.includes('Failed to fetch') || error.message.includes('Network Error')) {
        errorMessage = 'Network connection failed. Please check your internet connection.'
      } else if (error.message.includes('timeout')) {
        errorMessage = 'Request timed out. Please try again.'
      } else {
        errorMessage = error.message
      }
    }
    
    return errorMessage
  }

  // Fetch plants data with enhanced error handling
  const fetchPlants = useCallback(async (isRetry = false) => {
    try {
      setLoading(true)
      if (!isRetry) {
        setError(null)
        setRetryCount(0)
      } else {
        setIsRetrying(true)
      }
      
      const params = {}
      if (searchTerm) {
        params.search = searchTerm
      }
      
      const data = await ApiService.getPlants(params)
      
      // Defensive programming: ensure plants is always an array
      const plantsArray = Array.isArray(data?.plants) ? data.plants : 
                         Array.isArray(data) ? data : []
      
      setPlants(plantsArray)
      setTotalPlants(data?.total || data?.pagination?.total || plantsArray.length)
      setError(null)
      setRetryCount(0)
    } catch (err) {
      const errorMessage = handleApiError(err, 'fetching plants')
      setError(errorMessage)
      // Set empty array on error to prevent map() failures
      setPlants([])
    } finally {
      setLoading(false)
      setIsRetrying(false)
    }
  }, [searchTerm])

  const handleRetry = () => {
    setRetryCount(prev => prev + 1)
    fetchPlants(true)
  }

  // Fetch suppliers for dropdown
  const fetchSuppliers = async () => {
    try {
      const data = await ApiService.getSuppliers()
      setSuppliers(data.suppliers || [])
    } catch (err) {
      console.error('Error fetching suppliers:', err)
    }
  }

  useEffect(() => {
    fetchPlants()
    fetchSuppliers()
  }, [fetchPlants])

  // Handle form input changes - Completely rewritten to fix input truncation
  const handleInputChange = useCallback((e) => {
    // Immediately extract values to prevent React synthetic event issues
    const targetName = e.target.name
    const targetValue = e.target.value
    const targetType = e.target.type
    const targetChecked = e.target.checked
    
    // Use setTimeout to ensure state update happens after current render cycle
    setTimeout(() => {
      setFormData(prevData => {
        const newData = {
          ...prevData,
          [targetName]: targetType === 'checkbox' ? targetChecked : targetValue
        }
        
        console.log(`Input change - ${targetName}:`, targetValue, 'Full form data:', newData)
        return newData
      })
    }, 0)
  }, [])

  // Reset form
  const resetForm = () => {
    setFormData({
      name: '',
      common_name: '',
      category: '',
      height_min: '',
      height_max: '',
      width_min: '',
      width_max: '',
      sun_requirements: '',
      soil_type: '',
      water_needs: '',
      hardiness_zone: '',
      bloom_time: '',
      bloom_color: '',
      foliage_color: '',
      native: false,
      supplier_id: '',
      price: '',
      availability: '',
      planting_season: '',
      maintenance: '',
      notes: ''
    })
  }

  // Handle add plant
  const handleAddPlant = async (e) => {
    e.preventDefault()
    try {
      await ApiService.createPlant(formData)
      await fetchPlants()
      setShowAddModal(false)
      resetForm()
      alert(t('plants.addSuccess', 'Plant successfully added!'))
    } catch (err) {
      console.error('Error adding plant:', err)
      alert(t('plants.addError', 'Error adding plant: ') + err.message)
    }
  }

  // Handle edit plant
  const handleEditPlant = async (e) => {
    e.preventDefault()
    try {
      await ApiService.updatePlant(editingPlant.id, formData)
      await fetchPlants()
      setShowEditModal(false)
      setEditingPlant(null)
      resetForm()
      alert(t('plants.updateSuccess', 'Plant successfully updated!'))
    } catch (err) {
      console.error('Error updating plant:', err)
      alert(t('plants.updateError', 'Error updating plant: ') + err.message)
    }
  }

  // Handle delete plant
  const handleDeletePlant = async (plantId, plantName) => {
    if (!confirm(t('plants.deleteConfirm', 'Are you sure you want to delete "{name}"?').replace('{name}', plantName))) {
      return
    }

    try {
      await ApiService.deletePlant(plantId)
      await fetchPlants()
      alert(t('plants.deleteSuccess', 'Plant successfully deleted!'))
    } catch (err) {
      console.error('Error deleting plant:', err)
      alert(t('plants.deleteError', 'Error deleting plant: ') + err.message)
    }
  }

  // Open edit modal
  const openEditModal = (plant) => {
    setEditingPlant(plant)
    setFormData({
      name: plant.name || '',
      common_name: plant.common_name || '',
      category: plant.category || '',
      height_min: plant.height_min || '',
      height_max: plant.height_max || '',
      width_min: plant.width_min || '',
      width_max: plant.width_max || '',
      sun_requirements: plant.sun_requirements || '',
      soil_type: plant.soil_type || '',
      water_needs: plant.water_needs || '',
      hardiness_zone: plant.hardiness_zone || '',
      bloom_time: plant.bloom_time || '',
      bloom_color: plant.bloom_color || '',
      foliage_color: plant.foliage_color || '',
      native: plant.native || false,
      supplier_id: plant.supplier_id || '',
      price: plant.price || '',
      availability: plant.availability || '',
      planting_season: plant.planting_season || '',
      maintenance: plant.maintenance || '',
      notes: plant.notes || ''
    })
    setShowEditModal(true)
  }

  // Get supplier name by ID
  const getSupplierName = (supplierId) => {
    const supplier = suppliers.find(s => s.id === supplierId)
    return supplier ? supplier.name : t('common.unknown', 'Unknown')
  }

  // Get category label
  const getCategoryLabel = (category) => {
    const categoryOption = categoryOptions.find(c => c.value === category)
    return categoryOption ? categoryOption.label : category
  }

  // Get sun requirements label
  const getSunLabel = (sun) => {
    const sunOption = sunOptions.find(s => s.value === sun)
    return sunOption ? sunOption.label : sun
  }

  // Get water needs label
  const getWaterLabel = (water) => {
    const waterOption = waterOptions.find(w => w.value === water)
    return waterOption ? waterOption.label : water
  }

  // Format currency
  const formatCurrency = (amount) => {
    if (!amount) return '€0.00'
    return new Intl.NumberFormat('nl-NL', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 2
    }).format(amount)
  }

  // Format size range
  const formatSizeRange = (min, max, unit = 'm') => {
    if (!min && !max) return ''
    if (min && max) return `${min}-${max}${unit}`
    if (min) return `${min}${unit}+`
    if (max) return `<${max}${unit}`
    return ''
  }

  // Plant Form Component
  const PlantForm = ({ isEdit = false, onSubmit, onCancel }) => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">
            {isEdit ? t('plants.editPlant', 'Edit Plant') : t('plants.addPlant', 'Add Plant')}
          </h2>
          <Button variant="ghost" size="sm" onClick={onCancel}>
            <X className="h-4 w-4" />
          </Button>
        </div>

        <form onSubmit={onSubmit} className="space-y-6">
          {/* Basic Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">
              {t('plants.basicInfo', 'Basic Information')}
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">
                  {t('plants.scientificName', 'Scientific Name')} *
                </label>
                <Input
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  required
                  placeholder={t('plants.scientificNamePlaceholder', 'e.g., Acer platanoides')}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">
                  {t('plants.commonName', 'Common Name')}
                </label>
                <Input
                  name="common_name"
                  value={formData.common_name}
                  onChange={handleInputChange}
                  placeholder={t('plants.commonNamePlaceholder', 'e.g., Norway Maple')}
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">
                  {t('plants.category', 'Category')}
                </label>
                <select
                  name="category"
                  value={formData.category}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <option value="">{t('plants.selectCategory', 'Select a category')}</option>
                  {categoryOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">
                  {t('plants.hardinessZone', 'Hardiness Zone')}
                </label>
                <Input
                  name="hardiness_zone"
                  value={formData.hardiness_zone}
                  onChange={handleInputChange}
                  placeholder={t('plants.hardinessZonePlaceholder', 'e.g., 5-9')}
                />
              </div>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                name="native"
                checked={formData.native}
                onChange={handleInputChange}
                className="mr-2"
              />
              <label className="text-sm font-medium">
                {t('plants.native', 'Native Plant')}
              </label>
            </div>
          </div>

          {/* Size Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">
              {t('plants.sizeInfo', 'Size Information')}
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">
                  {t('plants.heightMin', 'Min Height (m)')}
                </label>
                <Input
                  name="height_min"
                  type="number"
                  value={formData.height_min}
                  onChange={handleInputChange}
                  placeholder="0.5"
                  step="0.1"
                  min="0"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">
                  {t('plants.heightMax', 'Max Height (m)')}
                </label>
                <Input
                  name="height_max"
                  type="number"
                  value={formData.height_max}
                  onChange={handleInputChange}
                  placeholder="2.0"
                  step="0.1"
                  min="0"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">
                  {t('plants.widthMin', 'Min Width (m)')}
                </label>
                <Input
                  name="width_min"
                  type="number"
                  value={formData.width_min}
                  onChange={handleInputChange}
                  placeholder="0.5"
                  step="0.1"
                  min="0"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">
                  {t('plants.widthMax', 'Max Width (m)')}
                </label>
                <Input
                  name="width_max"
                  type="number"
                  value={formData.width_max}
                  onChange={handleInputChange}
                  placeholder="1.5"
                  step="0.1"
                  min="0"
                />
              </div>
            </div>
          </div>

          {/* Growing Conditions */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">
              {t('plants.growingConditions', 'Growing Conditions')}
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">
                  {t('plants.sunRequirements', 'Sun Requirements')}
                </label>
                <select
                  name="sun_requirements"
                  value={formData.sun_requirements}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <option value="">{t('plants.selectSun', 'Select sun requirements')}</option>
                  {sunOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">
                  {t('plants.waterNeeds', 'Water Needs')}
                </label>
                <select
                  name="water_needs"
                  value={formData.water_needs}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <option value="">{t('plants.selectWater', 'Select water needs')}</option>
                  {waterOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">
                  {t('plants.soilType', 'Soil Type')}
                </label>
                <select
                  name="soil_type"
                  value={formData.soil_type}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <option value="">{t('plants.selectSoil', 'Select soil type')}</option>
                  {soilOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Appearance */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">
              {t('plants.appearance', 'Appearance')}
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">
                  {t('plants.bloomTime', 'Bloom Time')}
                </label>
                <Input
                  name="bloom_time"
                  value={formData.bloom_time}
                  onChange={handleInputChange}
                  placeholder={t('plants.bloomTimePlaceholder', 'e.g., Spring, Summer')}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">
                  {t('plants.bloomColor', 'Bloom Color')}
                </label>
                <Input
                  name="bloom_color"
                  value={formData.bloom_color}
                  onChange={handleInputChange}
                  placeholder={t('plants.bloomColorPlaceholder', 'e.g., White, Pink')}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">
                  {t('plants.foliageColor', 'Foliage Color')}
                </label>
                <Input
                  name="foliage_color"
                  value={formData.foliage_color}
                  onChange={handleInputChange}
                  placeholder={t('plants.foliageColorPlaceholder', 'e.g., Green, Red')}
                />
              </div>
            </div>
          </div>

          {/* Care & Commercial */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">
              {t('plants.careCommercial', 'Care & Commercial Information')}
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">
                  {t('plants.maintenance', 'Maintenance Level')}
                </label>
                <select
                  name="maintenance"
                  value={formData.maintenance}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <option value="">{t('plants.selectMaintenance', 'Select maintenance level')}</option>
                  {maintenanceOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">
                  {t('plants.plantingSeason', 'Planting Season')}
                </label>
                <Input
                  name="planting_season"
                  value={formData.planting_season}
                  onChange={handleInputChange}
                  placeholder={t('plants.plantingSeasonPlaceholder', 'e.g., Spring, Fall')}
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">
                  {t('plants.supplier', 'Supplier')}
                </label>
                <select
                  name="supplier_id"
                  value={formData.supplier_id}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <option value="">{t('plants.selectSupplier', 'Select a supplier')}</option>
                  {suppliers.map(supplier => (
                    <option key={supplier.id} value={supplier.id}>
                      {supplier.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">
                  {t('plants.price', 'Price')} (€)
                </label>
                <Input
                  name="price"
                  type="number"
                  value={formData.price}
                  onChange={handleInputChange}
                  placeholder="0.00"
                  step="0.01"
                  min="0"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">
                  {t('plants.availability', 'Availability')}
                </label>
                <Input
                  name="availability"
                  value={formData.availability}
                  onChange={handleInputChange}
                  placeholder={t('plants.availabilityPlaceholder', 'e.g., In Stock, Limited')}
                />
              </div>
            </div>
          </div>

          {/* Notes */}
          <div>
            <label className="block text-sm font-medium mb-1">
              {t('plants.notes', 'Notes')}
            </label>
            <Textarea
              name="notes"
              value={formData.notes}
              onChange={handleInputChange}
              rows={3}
              placeholder={t('plants.notesPlaceholder', 'Additional notes about the plant')}
            />
          </div>

          <div className="flex justify-end space-x-2 pt-4">
            <Button type="button" variant="outline" onClick={onCancel}>
              {t('common.cancel', 'Cancel')}
            </Button>
            <Button type="submit">
              {t('common.save', 'Save')}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )

  // Loading component
  const LoadingSpinner = () => (
    <div className="flex justify-center items-center py-12">
      <Loader2 className="h-8 w-8 animate-spin text-green-600" />
      <span className="ml-2 text-gray-600">{t('common.loading', 'Loading...')}</span>
    </div>
  )

  // Error component
  const ErrorDisplay = () => (
    <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
      <div className="w-12 h-12 mx-auto mb-4 bg-red-100 rounded-full flex items-center justify-center">
        <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <h2 className="text-lg font-semibold text-red-800 mb-2">
        {t('plants.errorLoading', 'Error Loading Plants')}
      </h2>
      <p className="text-red-600 mb-4">{error}</p>
      <Button onClick={fetchPlants} variant="destructive">
        {t('common.tryAgain', 'Try Again')}
      </Button>
    </div>
  )

  if (error && plants.length === 0) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {t('plants.title', 'Plants')}
            </h1>
            <p className="text-gray-600">
              {t('plants.subtitle', 'Manage your plant database and specifications')}
            </p>
          </div>
        </div>
        <ErrorDisplay />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {t('plants.title', 'Plants')}
          </h1>
          <p className="text-gray-600">
            {t('plants.subtitle', 'Manage your plant database and specifications')}
          </p>
        </div>
        <div className="flex space-x-2">
          <Button 
            variant="outline"
            className="flex items-center space-x-2"
          >
            <Upload className="h-4 w-4" />
            <span>{t('plants.importExcel', 'Import Excel/CSV')}</span>
          </Button>
          <Button 
            className="flex items-center space-x-2"
            onClick={() => setShowAddModal(true)}
          >
            <Plus className="h-4 w-4" />
            <span>{t('plants.addPlant', 'Add Plant')}</span>
          </Button>
        </div>
      </div>

      {/* Search Bar */}
      <div className="flex items-center space-x-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input
            placeholder={t('plants.searchPlaceholder', 'Search plants...')}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        {totalPlants > 0 && (
          <span className="text-sm text-gray-500">
            {totalPlants} {t('plants.total', 'plants')}
          </span>
        )}
      </div>

      {loading ? (
        <Card>
          <CardContent>
            <LoadingSpinner />
          </CardContent>
        </Card>
      ) : !Array.isArray(plants) || plants.length === 0 ? (
        <Card>
          <CardContent className="p-12">
            <div className="text-center">
              <Leaf className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h2 className="text-lg font-semibold text-gray-900 mb-2">
                {t('plants.noPlants', 'No plants found')}
              </h2>
              <p className="text-gray-500 mb-6">
                {searchTerm 
                  ? t('plants.noSearchResults', 'No plants match your search criteria')
                  : t('plants.createFirst', 'Add your first plant to get started')
                }
              </p>
              <Button onClick={() => setShowAddModal(true)}>
                <Plus className="h-4 w-4 mr-2" />
                {t('plants.addPlant', 'Add Plant')}
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {plants.map((plant) => (
            <Card key={plant.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <CardTitle className="text-lg flex items-center">
                    <Leaf className="h-5 w-5 mr-2 text-green-600" />
                    <div>
                      <div className="font-italic">{plant.name}</div>
                      {plant.common_name && (
                        <div className="text-sm text-gray-600 font-normal">
                          {plant.common_name}
                        </div>
                      )}
                    </div>
                  </CardTitle>
                  <div className="flex space-x-1">
                    <Button
                      onClick={() => openEditModal(plant)}
                      variant="outline"
                      size="sm"
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      onClick={() => handleDeletePlant(plant.id, plant.name)}
                      variant="outline"
                      size="sm"
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between">
                  {plant.category && (
                    <Badge variant="secondary">
                      {getCategoryLabel(plant.category)}
                    </Badge>
                  )}
                  {plant.native && (
                    <Badge variant="success" className="text-xs">
                      {t('plants.native', 'Native')}
                    </Badge>
                  )}
                </div>

                {/* Size Information */}
                {(plant.height_min || plant.height_max || plant.width_min || plant.width_max) && (
                  <div className="text-sm space-y-1">
                    {(plant.height_min || plant.height_max) && (
                      <div className="flex items-center text-gray-600">
                        <span className="font-medium mr-2">
                          {t('plants.height', 'Height')}:
                        </span>
                        <span>{formatSizeRange(plant.height_min, plant.height_max)}</span>
                      </div>
                    )}
                    {(plant.width_min || plant.width_max) && (
                      <div className="flex items-center text-gray-600">
                        <span className="font-medium mr-2">
                          {t('plants.width', 'Width')}:
                        </span>
                        <span>{formatSizeRange(plant.width_min, plant.width_max)}</span>
                      </div>
                    )}
                  </div>
                )}

                {/* Growing Conditions */}
                <div className="flex flex-wrap gap-2 text-xs">
                  {plant.sun_requirements && (
                    <div className="flex items-center bg-yellow-100 text-yellow-800 px-2 py-1 rounded">
                      <Sun className="h-3 w-3 mr-1" />
                      <span>{getSunLabel(plant.sun_requirements)}</span>
                    </div>
                  )}
                  {plant.water_needs && (
                    <div className="flex items-center bg-blue-100 text-blue-800 px-2 py-1 rounded">
                      <Droplets className="h-3 w-3 mr-1" />
                      <span>{getWaterLabel(plant.water_needs)}</span>
                    </div>
                  )}
                  {plant.hardiness_zone && (
                    <div className="flex items-center bg-purple-100 text-purple-800 px-2 py-1 rounded">
                      <Thermometer className="h-3 w-3 mr-1" />
                      <span>Zone {plant.hardiness_zone}</span>
                    </div>
                  )}
                </div>

                {/* Bloom Information */}
                {(plant.bloom_time || plant.bloom_color) && (
                  <div className="text-sm">
                    <div className="flex items-center text-gray-600">
                      <Palette className="h-4 w-4 mr-2" />
                      <div>
                        {plant.bloom_time && (
                          <span>{plant.bloom_time}</span>
                        )}
                        {plant.bloom_time && plant.bloom_color && <span> • </span>}
                        {plant.bloom_color && (
                          <span>{plant.bloom_color}</span>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {/* Commercial Information */}
                <div className="pt-2 border-t border-gray-100">
                  {plant.price && (
                    <div className="text-green-600 font-semibold">
                      {formatCurrency(plant.price)}
                    </div>
                  )}
                  {plant.supplier_id && (
                    <div className="text-sm text-gray-600">
                      {t('plants.supplier', 'Supplier')}: {getSupplierName(plant.supplier_id)}
                    </div>
                  )}
                  {plant.availability && (
                    <div className="text-sm text-gray-600">
                      {t('plants.availability', 'Availability')}: {plant.availability}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Add Plant Modal */}
      {showAddModal && (
        <PlantForm
          onSubmit={handleAddPlant}
          onCancel={() => {
            setShowAddModal(false)
            resetForm()
          }}
        />
      )}

      {/* Edit Plant Modal */}
      {showEditModal && (
        <PlantForm
          isEdit={true}
          onSubmit={handleEditPlant}
          onCancel={() => {
            setShowEditModal(false)
            setEditingPlant(null)
            resetForm()
          }}
        />
      )}
    </div>
  )
}

export default Plants
