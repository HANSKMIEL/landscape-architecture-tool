import React, { useState, useEffect, useCallback } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { 
  Search, 
  Plus, 
  Building2, 
  Phone, 
  Mail, 
  MapPin,
  Trash2,
  Edit,
  X,
  Loader2
} from 'lucide-react'
import { toast } from 'sonner'
import apiService from '../services/api'
import { useLanguage } from '../i18n/LanguageProvider'

const Suppliers = () => {
  const { t } = useLanguage()
  const [suppliers, setSuppliers] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [totalSuppliers, setTotalSuppliers] = useState(0)
  const [showAddModal, setShowAddModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [editingSupplier, setEditingSupplier] = useState(null)
  const [error, setError] = useState(null)
  const [submitLoading, setSubmitLoading] = useState(false)
  const [deleteLoading, setDeleteLoading] = useState(null)

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    contact_person: '',
    email: '',
    phone: '',
    address: '',
    city: '',
    postal_code: '',
    country: '',
    website: '',
    notes: '',
    specialties: ''
  })

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

  const loadSuppliers = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const params = searchTerm ? { search: searchTerm } : {}
      const data = await apiService.getSuppliers(params)
      setSuppliers(data.suppliers || [])
      setTotalSuppliers(data.total || 0)
    } catch (error) {
      const errorMessage = handleApiError(error, 'loading suppliers')
      setError(errorMessage)
      toast.error(`${t('suppliers.error', 'Error loading suppliers')}: ${errorMessage}`)
    } finally {
      setLoading(false)
    }
  }, [searchTerm, t])

  useEffect(() => {
    loadSuppliers()
  }, [loadSuppliers])

  // Handle form input changes
  const handleInputChange = useCallback((e) => {
    const { name, value } = e.target
    
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }, [])

  // Reset form
  const resetForm = () => {
    setFormData({
      name: '',
      contact_person: '',
      email: '',
      phone: '',
      address: '',
      city: '',
      postal_code: '',
      country: '',
      website: '',
      notes: '',
      specialties: ''
    })
  }

  // Handle add supplier with enhanced error handling
  const handleAddSupplier = async (e) => {
    e.preventDefault()
    setSubmitLoading(true)
    
    try {
      await apiService.createSupplier(formData)
      await loadSuppliers()
      setShowAddModal(false)
      resetForm()
      toast.success(t('suppliers.addSuccess', 'Supplier successfully added!'))
    } catch (error) {
      const errorMessage = handleApiError(error, 'adding supplier')
      toast.error(`${t('suppliers.addError', 'Error adding supplier:')} ${errorMessage}`)
    } finally {
      setSubmitLoading(false)
    }
  }

  // Handle edit supplier with enhanced error handling
  const handleEditSupplier = async (e) => {
    e.preventDefault()
    setSubmitLoading(true)
    
    try {
      await apiService.updateSupplier(editingSupplier.id, formData)
      await loadSuppliers()
      setShowEditModal(false)
      setEditingSupplier(null)
      resetForm()
      toast.success(t('suppliers.updateSuccess', 'Supplier successfully updated!'))
    } catch (error) {
      const errorMessage = handleApiError(error, 'updating supplier')
      toast.error(`${t('suppliers.updateError', 'Error updating supplier:')} ${errorMessage}`)
    } finally {
      setSubmitLoading(false)
    }
  }

  // Handle delete supplier with enhanced error handling and loading state
  const handleDeleteSupplier = async (supplierId, supplierName) => {
    const confirmationMessage = t(
      'suppliers.deleteConfirm',
      'Are you sure you want to delete "{name}"?'
    ).replace('{name}', supplierName)

    if (!window.confirm(confirmationMessage)) {
      return
    }

    setDeleteLoading(supplierId)
    
    try {
      await apiService.deleteSupplier(supplierId)
      toast.success(t('suppliers.deleteSuccess', 'Supplier successfully deleted!'))
      loadSuppliers()
    } catch (error) {
      const errorMessage = handleApiError(error, 'deleting supplier')
      toast.error(t('suppliers.deleteError', 'Error deleting supplier: ') + errorMessage)
    } finally {
      setDeleteLoading(null)
    }
  }

  // Open edit modal
  const openEditModal = (supplier) => {
    setEditingSupplier(supplier)
    setFormData({
      name: supplier.name || '',
      contact_person: supplier.contact_person || '',
      email: supplier.email || '',
      phone: supplier.phone || '',
      address: supplier.address || '',
      city: supplier.city || '',
      postal_code: supplier.postal_code || '',
      country: supplier.country || '',
      website: supplier.website || '',
      notes: supplier.notes || '',
      specialties: supplier.specialties || ''
    })
    setShowEditModal(true)
  }

  // Supplier Form Component
  const SupplierForm = ({ isEdit = false, onSubmit, onCancel, isSubmitting = false }) => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">
            {isEdit ? t('suppliers.editSupplier', 'Edit Supplier') : t('suppliers.addSupplier', 'Add Supplier')}
          </h2>
          <Button variant="ghost" size="sm" onClick={onCancel}>
            <X className="h-4 w-4" />
          </Button>
        </div>

        <form onSubmit={onSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">
                {t('suppliers.name', 'Company Name')} *
              </label>
              <Input
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required
                placeholder={t('suppliers.namePlaceholder', 'Enter company name')}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                {t('suppliers.contactPerson', 'Contact Person')}
              </label>
              <Input
                name="contact_person"
                value={formData.contact_person}
                onChange={handleInputChange}
                placeholder={t('suppliers.contactPersonPlaceholder', 'Enter contact person name')}
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">
                {t('suppliers.email', 'Email')}
              </label>
              <Input
                name="email"
                type="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder={t('suppliers.emailPlaceholder', 'Enter email address')}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                {t('suppliers.phone', 'Phone')}
              </label>
              <Input
                name="phone"
                value={formData.phone}
                onChange={handleInputChange}
                placeholder={t('suppliers.phonePlaceholder', 'Enter phone number')}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              {t('suppliers.address', 'Address')}
            </label>
            <Input
              name="address"
              value={formData.address}
              onChange={handleInputChange}
              placeholder={t('suppliers.addressPlaceholder', 'Enter street address')}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">
                {t('suppliers.city', 'City')}
              </label>
              <Input
                name="city"
                value={formData.city}
                onChange={handleInputChange}
                placeholder={t('suppliers.cityPlaceholder', 'Enter city')}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                {t('suppliers.postalCode', 'Postal Code')}
              </label>
              <Input
                name="postal_code"
                value={formData.postal_code}
                onChange={handleInputChange}
                placeholder={t('suppliers.postalCodePlaceholder', 'Enter postal code')}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                {t('suppliers.country', 'Country')}
              </label>
              <Input
                name="country"
                value={formData.country}
                onChange={handleInputChange}
                placeholder={t('suppliers.countryPlaceholder', 'Enter country')}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              {t('suppliers.website', 'Website')}
            </label>
            <Input
              name="website"
              type="url"
              value={formData.website}
              onChange={handleInputChange}
              placeholder={t('suppliers.websitePlaceholder', 'Enter website URL')}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              {t('suppliers.specialties', 'Specialties')}
            </label>
            <Input
              name="specialties"
              value={formData.specialties}
              onChange={handleInputChange}
              placeholder={t('suppliers.specialtiesPlaceholder', 'e.g., Native plants, Trees, Garden tools')}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              {t('suppliers.notes', 'Notes')}
            </label>
            <Textarea
              name="notes"
              value={formData.notes}
              onChange={handleInputChange}
              rows={3}
              placeholder={t('suppliers.notesPlaceholder', 'Additional notes about the supplier')}
            />
          </div>

          <div className="flex justify-end space-x-2 pt-4">
            <Button type="button" variant="outline" onClick={onCancel} disabled={isSubmitting}>
              {t('common.cancel', 'Cancel')}
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? (
                <span className="flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  {t('common.saving', 'Saving...')}
                </span>
              ) : (
                t('common.save', 'Save')
              )}
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
        {t('suppliers.errorLoading', 'Error Loading Suppliers')}
      </h2>
      <p className="text-red-600 mb-4">{error}</p>
      <Button onClick={loadSuppliers} variant="destructive">
        {t('common.tryAgain', 'Try Again')}
      </Button>
    </div>
  )

  if (error && suppliers.length === 0) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {t('suppliers.title', 'Suppliers')}
            </h1>
            <p className="text-gray-600">
              {t('suppliers.subtitle', 'Manage your landscape architecture suppliers')}
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
            {t('suppliers.title', 'Suppliers')}
          </h1>
          <p className="text-gray-600">
            {t('suppliers.subtitle', 'Manage your landscape architecture suppliers')}
          </p>
        </div>
        <Button 
          className="flex items-center space-x-2"
          onClick={() => setShowAddModal(true)}
        >
          <Plus className="h-4 w-4" />
          <span>{t('suppliers.addSupplier', 'Add Supplier')}</span>
        </Button>
      </div>

      {/* Search Bar */}
      <div className="flex items-center space-x-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input
            placeholder={t('suppliers.searchPlaceholder', 'Search suppliers...')}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        {totalSuppliers > 0 && (
          <span className="text-sm text-gray-500">
            {totalSuppliers} {t('suppliers.total', 'suppliers')}
          </span>
        )}
      </div>

      {loading ? (
        <Card>
          <CardContent>
            <LoadingSpinner />
          </CardContent>
        </Card>
      ) : !Array.isArray(suppliers) || suppliers.length === 0 ? (
        <Card>
          <CardContent className="p-12">
            <div className="text-center">
              <Building2 className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h2 className="text-lg font-semibold text-gray-900 mb-2">
                {t('suppliers.noSuppliers', 'No suppliers found')}
              </h2>
              <p className="text-gray-500 mb-6">
                {searchTerm 
                  ? t('suppliers.noSearchResults', 'No suppliers match your search criteria')
                  : t('suppliers.createFirst', 'Add your first supplier to get started')
                }
              </p>
              <Button onClick={() => setShowAddModal(true)}>
                <Plus className="h-4 w-4 mr-2" />
                {t('suppliers.addSupplier', 'Add Supplier')}
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {suppliers.map((supplier) => (
            <Card key={supplier.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <CardTitle className="text-lg flex items-center">
                    <Building2 className="h-5 w-5 mr-2 text-green-600" />
                    {supplier.name}
                  </CardTitle>
                  <div className="flex space-x-1">
                    <Button
                      onClick={() => openEditModal(supplier)}
                      variant="outline"
                      size="sm"
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      onClick={() => handleDeleteSupplier(supplier.id, supplier.name)}
                      variant="outline"
                      size="sm"
                      className="text-red-600 hover:text-red-700"
                      disabled={deleteLoading === supplier.id}
                    >
                      {deleteLoading === supplier.id ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Trash2 className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                {supplier.contact_person && (
                  <div className="flex items-center text-gray-600 text-sm">
                    <span className="font-medium mr-2">{t('suppliers.contact', 'Contact')}:</span>
                    <span>{supplier.contact_person}</span>
                  </div>
                )}
                
                {supplier.email && (
                  <div className="flex items-center text-gray-600 text-sm">
                    <Mail className="h-4 w-4 mr-2" />
                    <a 
                      href={`mailto:${supplier.email}`}
                      className="text-blue-600 hover:underline"
                    >
                      {supplier.email}
                    </a>
                  </div>
                )}
                
                {supplier.phone && (
                  <div className="flex items-center text-gray-600 text-sm">
                    <Phone className="h-4 w-4 mr-2" />
                    <a 
                      href={`tel:${supplier.phone}`}
                      className="text-blue-600 hover:underline"
                    >
                      {supplier.phone}
                    </a>
                  </div>
                )}
                
                {(supplier.city || supplier.address) && (
                  <div className="flex items-start text-gray-600 text-sm">
                    <MapPin className="h-4 w-4 mr-2 mt-0.5" />
                    <div>
                      {supplier.address && <div>{supplier.address}</div>}
                      {supplier.city && (
                        <div>
                          {supplier.city}
                          {supplier.postal_code && `, ${supplier.postal_code}`}
                          {supplier.country && `, ${supplier.country}`}
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {supplier.specialties && (
                  <div className="text-sm">
                    <span className="font-medium text-gray-700">
                      {t('suppliers.specialties', 'Specialties')}:
                    </span>
                    <div className="text-gray-600 mt-1">
                      {supplier.specialties}
                    </div>
                  </div>
                )}

                {supplier.website && (
                  <div className="pt-2">
                    <a 
                      href={supplier.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline text-sm"
                    >
                      {t('suppliers.visitWebsite', 'Visit Website')} →
                    </a>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Add Supplier Modal */}
      {showAddModal && (
        <SupplierForm
          onSubmit={handleAddSupplier}
          onCancel={() => {
            setShowAddModal(false)
            setSubmitLoading(false)
            resetForm()
          }}
          isSubmitting={submitLoading}
        />
      )}

      {/* Edit Supplier Modal */}
      {showEditModal && (
        <SupplierForm
          isEdit={true}
          onSubmit={handleEditSupplier}
          onCancel={() => {
            setShowEditModal(false)
            setEditingSupplier(null)
            setSubmitLoading(false)
            resetForm()
          }}
          isSubmitting={submitLoading}
        />
      )}
    </div>
  )
}

export default Suppliers
