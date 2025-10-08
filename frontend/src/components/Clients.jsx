import React, { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { 
  Building2, 
  Plus, 
  Upload, 
  Download,
  Edit, 
  Trash2, 
  Search, 
  Eye, 
  X, 
  Loader2,
  Mail,
  Phone,
  MapPin,
  User
} from 'lucide-react'
import ApiService from '../services/api'
import { useLanguage } from '../i18n/LanguageProvider'

const Clients = () => {
  const { t } = useLanguage()
  const navigate = useNavigate()
  // State management
  const [clients, setClients] = useState([])
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showAddModal, setShowAddModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showProjectsModal, setShowProjectsModal] = useState(false)
  const [editingClient, setEditingClient] = useState(null)
  const [selectedClient, setSelectedClient] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [totalClients, setTotalClients] = useState(0)

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
    notes: ''
  })

  // Load clients from API
  const loadClients = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const params = searchTerm ? { search: searchTerm } : {}
      const data = await ApiService.getClients(params)
      
      // Defensive programming: ensure clients is always an array  
      const clientsArray = Array.isArray(data?.clients) ? data.clients :
                          Array.isArray(data) ? data : []
      
      setClients(clientsArray)
      setTotalClients(data?.total || data?.pagination?.total || clientsArray.length)
    } catch (err) {
      console.error('Error loading clients:', err)
      setError(err.message)
      // Set empty array on error to prevent filter() failures
      setClients([])
    } finally {
      setLoading(false)
    }
  }, [searchTerm])

  // Load client projects
  const loadClientProjects = async (clientId) => {
    try {
      const data = await ApiService.getProjects({ client_id: clientId })
      setProjects(data.projects || [])
    } catch (err) {
      console.error('Error loading client projects:', err)
      setProjects([])
    }
  }

  useEffect(() => {
    loadClients()
  }, [loadClients])

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

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
      notes: ''
    })
  }

  // Handle add client
  const handleAddClient = async (e) => {
    e.preventDefault()
    try {
      await ApiService.createClient(formData)
      await loadClients()
      setShowAddModal(false)
      resetForm()
      alert(t('clients.addSuccess', 'Client successfully added!'))
    } catch (err) {
      console.error('Error adding client:', err)
      alert(t('clients.addError', 'Error adding client: ') + err.message)
    }
  }

  // Handle edit client
  const handleEditClient = async (e) => {
    e.preventDefault()
    try {
      await ApiService.updateClient(editingClient.id, formData)
      await loadClients()
      setShowEditModal(false)
      setEditingClient(null)
      resetForm()
      alert(t('clients.updateSuccess', 'Client successfully updated!'))
    } catch (err) {
      console.error('Error updating client:', err)
      alert(t('clients.updateError', 'Error updating client: ') + err.message)
    }
  }

  // Handle delete client
  const handleDeleteClient = async (clientId, clientName) => {
    if (!confirm(t('clients.deleteConfirm', 'Are you sure you want to delete "{name}"?').replace('{name}', clientName))) {
      return
    }

    try {
      await ApiService.deleteClient(clientId)
      await loadClients()
      alert(t('clients.deleteSuccess', 'Client successfully deleted!'))
    } catch (err) {
      console.error('Error deleting client:', err)
      alert(t('clients.deleteError', 'Error deleting client: ') + err.message)
    }
  }

  // Export clients to CSV
  const exportClientsCSV = () => {
    try {
      if (!clients || clients.length === 0) {
        alert(t('importExport.noDataToExport', 'No data available to export'))
        return
      }

      const headers = ['Name', 'Contact Person', 'Email', 'Phone', 'Address', 'City', 'Postal Code', 'Country', 'Website', 'Notes']
      const csvContent = [
        headers.join(','),
        ...clients.map(client => [
          `"${client.name || ''}"`,
          `"${client.contact_person || ''}"`,
          `"${client.email || ''}"`,
          `"${client.phone || ''}"`,
          `"${client.address || ''}"`,
          `"${client.city || ''}"`,
          `"${client.postal_code || ''}"`,
          `"${client.country || ''}"`,
          `"${client.website || ''}"`,
          `"${client.notes || ''}"`
        ].join(','))
      ].join('\n')

      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `clients_export_${new Date().toISOString().split('T')[0]}.csv`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      alert(t('importExport.exportCompleted', 'Export completed successfully'))
    } catch (error) {
      console.error('Export error:', error)
      alert(t('importExport.exportError', 'Export error: ') + error.message)
    }
  }

  // Open edit modal
  const openEditModal = (client) => {
    setEditingClient(client)
    setFormData({
      name: client.name || '',
      contact_person: client.contact_person || '',
      email: client.email || '',
      phone: client.phone || '',
      address: client.address || '',
      city: client.city || '',
      postal_code: client.postal_code || '',
      country: client.country || '',
      website: client.website || '',
      notes: client.notes || ''
    })
    setShowEditModal(true)
  }

  // Open projects modal
  const openProjectsModal = async (client) => {
    setSelectedClient(client)
    await loadClientProjects(client.id)
    setShowProjectsModal(true)
  }

  // Client Form Component
  const ClientForm = ({ isEdit = false, onSubmit, onCancel }) => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">
            {isEdit ? t('clients.editClient', 'Edit Client') : t('clients.addClient', 'Add Client')}
          </h2>
          <Button variant="ghost" size="sm" onClick={onCancel}>
            <X className="h-4 w-4" />
          </Button>
        </div>

        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">
              {t('clients.name', 'Client Name')} *
            </label>
            <Input
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              required
              placeholder={t('clients.namePlaceholder', 'Enter client name')}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">
                {t('clients.contactPerson', 'Contact Person')}
              </label>
              <Input
                name="contact_person"
                value={formData.contact_person}
                onChange={handleInputChange}
                placeholder={t('clients.contactPersonPlaceholder', 'Enter contact person name')}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                {t('clients.email', 'Email')}
              </label>
              <Input
                name="email"
                type="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder={t('clients.emailPlaceholder', 'Enter email address')}
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">
                {t('clients.phone', 'Phone')}
              </label>
              <Input
                name="phone"
                value={formData.phone}
                onChange={handleInputChange}
                placeholder={t('clients.phonePlaceholder', 'Enter phone number')}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                {t('clients.website', 'Website')}
              </label>
              <Input
                name="website"
                type="url"
                value={formData.website}
                onChange={handleInputChange}
                placeholder={t('clients.websitePlaceholder', 'Enter website URL')}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              {t('clients.address', 'Address')}
            </label>
            <Input
              name="address"
              value={formData.address}
              onChange={handleInputChange}
              placeholder={t('clients.addressPlaceholder', 'Enter street address')}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">
                {t('clients.city', 'City')}
              </label>
              <Input
                name="city"
                value={formData.city}
                onChange={handleInputChange}
                placeholder={t('clients.cityPlaceholder', 'Enter city')}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                {t('clients.postalCode', 'Postal Code')}
              </label>
              <Input
                name="postal_code"
                value={formData.postal_code}
                onChange={handleInputChange}
                placeholder={t('clients.postalCodePlaceholder', 'Enter postal code')}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                {t('clients.country', 'Country')}
              </label>
              <Input
                name="country"
                value={formData.country}
                onChange={handleInputChange}
                placeholder={t('clients.countryPlaceholder', 'Enter country')}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              {t('clients.notes', 'Notes')}
            </label>
            <Textarea
              name="notes"
              value={formData.notes}
              onChange={handleInputChange}
              rows={3}
              placeholder={t('clients.notesPlaceholder', 'Additional notes about the client')}
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

  // Projects Modal Component
  const ProjectsModal = ({ client, projects, onClose }) => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">
            {t('clients.clientProjects', 'Projects for {name}').replace('{name}', client?.name || '')}
          </h2>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>

        {projects.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-gray-500">
              {t('clients.noProjects', 'No projects found for this client')}
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {projects.map((project) => (
              <Card key={project.id}>
                <CardHeader>
                  <CardTitle className="text-lg">{project.name}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 text-sm">
                    {project.description && (
                      <p className="text-gray-600">{project.description}</p>
                    )}
                    {project.status && (
                      <div>
                        <span className="font-medium">{t('projects.status', 'Status')}:</span>
                        <span className="ml-2">{project.status}</span>
                      </div>
                    )}
                    {project.budget && (
                      <div>
                        <span className="font-medium">{t('projects.budget', 'Budget')}:</span>
                        <span className="ml-2">€{project.budget}</span>
                      </div>
                    )}
                    {project.start_date && (
                      <div>
                        <span className="font-medium">{t('projects.startDate', 'Start Date')}:</span>
                        <span className="ml-2">{new Date(project.start_date).toLocaleDateString()}</span>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
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
        {t('clients.errorLoading', 'Error Loading Clients')}
      </h2>
      <p className="text-red-600 mb-4">{error}</p>
      <Button onClick={loadClients} variant="destructive">
        {t('common.tryAgain', 'Try Again')}
      </Button>
    </div>
  )

  if (error && clients.length === 0) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {t('clients.title', 'Clients')}
            </h1>
            <p className="text-gray-600">
              {t('clients.subtitle', 'Manage your landscape architecture clients and their projects')}
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
            {t('clients.title', 'Clients')}
          </h1>
          <p className="text-gray-600">
            {t('clients.subtitle', 'Manage your landscape architecture clients and their projects')}
          </p>
        </div>
        <div className="flex space-x-2">
          <Button 
            variant="outline"
            onClick={exportClientsCSV}
            className="flex items-center space-x-2"
          >
            <Download className="h-4 w-4" />
            <span>{t('common.export', 'Export')}</span>
          </Button>
          <Button 
            variant="outline"
            onClick={() => navigate('/import-export')}
            className="flex items-center space-x-2"
          >
            <Upload className="h-4 w-4" />
            <span>{t('clients.importExcel', 'Import Excel/CSV')}</span>
          </Button>
          <Button 
            className="flex items-center space-x-2"
            onClick={() => setShowAddModal(true)}
          >
            <Plus className="h-4 w-4" />
            <span>{t('clients.addClient', 'Add Client')}</span>
          </Button>
        </div>
      </div>

      {/* Search Bar */}
      <div className="flex items-center space-x-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input
            placeholder={t('clients.searchPlaceholder', 'Search clients...')}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        {totalClients > 0 && (
          <span className="text-sm text-gray-500">
            {totalClients} {t('clients.total', 'clients')}
          </span>
        )}
      </div>

      {loading ? (
        <Card>
          <CardContent>
            <LoadingSpinner />
          </CardContent>
        </Card>
      ) : !Array.isArray(clients) || clients.length === 0 ? (
        <Card>
          <CardContent className="p-12">
            <div className="text-center">
              <Building2 className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h2 className="text-lg font-semibold text-gray-900 mb-2">
                {t('clients.noClients', 'No clients found')}
              </h2>
              <p className="text-gray-500 mb-6">
                {searchTerm 
                  ? t('clients.noSearchResults', 'No clients match your search criteria')
                  : t('clients.createFirst', 'Add your first client to get started')
                }
              </p>
              <Button onClick={() => setShowAddModal(true)}>
                <Plus className="h-4 w-4 mr-2" />
                {t('clients.addClient', 'Add Client')}
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {clients.map((client) => (
            <Card key={client.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <CardTitle className="text-lg flex items-center">
                    <Building2 className="h-5 w-5 mr-2 text-green-600" />
                    {client.name}
                  </CardTitle>
                  <div className="flex space-x-1">
                    <Button
                      onClick={() => openProjectsModal(client)}
                      variant="outline"
                      size="sm"
                      title={t('clients.viewProjects', 'View Projects')}
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                    <Button
                      onClick={() => openEditModal(client)}
                      variant="outline"
                      size="sm"
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      onClick={() => handleDeleteClient(client.id, client.name)}
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
                {client.contact_person && (
                  <div className="flex items-center text-gray-600 text-sm">
                    <User className="h-4 w-4 mr-2" />
                    <span>{client.contact_person}</span>
                  </div>
                )}
                
                {client.email && (
                  <div className="flex items-center text-gray-600 text-sm">
                    <Mail className="h-4 w-4 mr-2" />
                    <a 
                      href={`mailto:${client.email}`}
                      className="text-blue-600 hover:underline"
                    >
                      {client.email}
                    </a>
                  </div>
                )}
                
                {client.phone && (
                  <div className="flex items-center text-gray-600 text-sm">
                    <Phone className="h-4 w-4 mr-2" />
                    <a 
                      href={`tel:${client.phone}`}
                      className="text-blue-600 hover:underline"
                    >
                      {client.phone}
                    </a>
                  </div>
                )}
                
                {(client.city || client.address) && (
                  <div className="flex items-start text-gray-600 text-sm">
                    <MapPin className="h-4 w-4 mr-2 mt-0.5" />
                    <div>
                      {client.address && <div>{client.address}</div>}
                      {client.city && (
                        <div>
                          {client.city}
                          {client.postal_code && `, ${client.postal_code}`}
                          {client.country && `, ${client.country}`}
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {client.website && (
                  <div className="pt-2">
                    <a 
                      href={client.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline text-sm"
                    >
                      {t('clients.visitWebsite', 'Visit Website')} →
                    </a>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Add Client Modal */}
      {showAddModal && (
        <ClientForm
          onSubmit={handleAddClient}
          onCancel={() => {
            setShowAddModal(false)
            resetForm()
          }}
        />
      )}

      {/* Edit Client Modal */}
      {showEditModal && (
        <ClientForm
          isEdit={true}
          onSubmit={handleEditClient}
          onCancel={() => {
            setShowEditModal(false)
            setEditingClient(null)
            resetForm()
          }}
        />
      )}

      {/* Projects Modal */}
      {showProjectsModal && selectedClient && (
        <ProjectsModal
          client={selectedClient}
          projects={projects}
          onClose={() => {
            setShowProjectsModal(false)
            setSelectedClient(null)
            setProjects([])
          }}
        />
      )}
    </div>
  )
}

export default Clients
