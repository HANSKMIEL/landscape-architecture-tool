import React, { useState, useEffect, useCallback } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import {
  FolderOpen,
  Plus,
  Users,
  MapPin,
  Calendar,
  Loader2,
  Edit,
  Trash2,
  Search,
  X,
  DollarSign
} from 'lucide-react'
import ProjectPlantManagement from './ProjectPlantManagement'
import ApiService from '../services/api'
import { useLanguage } from '../i18n/LanguageProvider'

const Projects = () => {
  const { t } = useLanguage()
  const [projects, setProjects] = useState([])
  const [clients, setClients] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [selectedProject, setSelectedProject] = useState(null)
  const [showAddModal, setShowAddModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [editingProject, setEditingProject] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    client_id: '',
    location: '',
    budget: '',
    start_date: '',
    end_date: '',
    status: 'planning',
    notes: ''
  })

  // Status options
  const statusOptions = [
    { value: 'planning', label: t('projects.status.planning', 'Planning') },
    { value: 'in_progress', label: t('projects.status.inProgress', 'In Progress') },
    { value: 'on_hold', label: t('projects.status.onHold', 'On Hold') },
    { value: 'completed', label: t('projects.status.completed', 'Completed') },
    { value: 'cancelled', label: t('projects.status.cancelled', 'Cancelled') }
  ]

  // Fetch projects from API
  const fetchProjects = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const params = {}
      if (searchTerm) {
        params.search = searchTerm
      }

      const data = await ApiService.getProjects(params)

      // Defensive programming: ensure projects is always an array
      const projectsArray = Array.isArray(data?.projects) ? data.projects :
        Array.isArray(data) ? data : []

      setProjects(projectsArray)
    } catch (err) {
      console.error('Error fetching projects:', err)
      // Set empty array on error to prevent map() failures
      setProjects([])
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [searchTerm])

  // Fetch clients for dropdown
  const fetchClients = async () => {
    try {
      const data = await ApiService.getClients()
      setClients(data.clients || [])
    } catch (err) {
      console.error('Error fetching clients:', err)
    }
  }

  useEffect(() => {
    fetchProjects()
    fetchClients()
  }, [fetchProjects])

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
      description: '',
      client_id: '',
      location: '',
      budget: '',
      start_date: '',
      end_date: '',
      status: 'planning',
      notes: ''
    })
  }

  // Handle add project
  const handleAddProject = async (e) => {
    e.preventDefault()
    try {
      await ApiService.createProject(formData)
      await fetchProjects()
      setShowAddModal(false)
      resetForm()
      alert(t('projects.addSuccess', 'Project successfully added!'))
    } catch (err) {
      console.error('Error adding project:', err)
      alert(t('projects.addError', 'Error adding project: ') + err.message)
    }
  }

  // Handle edit project
  const handleEditProject = async (e) => {
    e.preventDefault()
    try {
      await ApiService.updateProject(editingProject.id, formData)
      await fetchProjects()
      setShowEditModal(false)
      setEditingProject(null)
      resetForm()
      alert(t('projects.updateSuccess', 'Project successfully updated!'))
    } catch (err) {
      console.error('Error updating project:', err)
      alert(t('projects.updateError', 'Error updating project: ') + err.message)
    }
  }

  // Handle delete project
  const handleDeleteProject = async (projectId, projectName) => {
    if (!confirm(t('projects.deleteConfirm', 'Are you sure you want to delete "{name}"?').replace('{name}', projectName))) {
      return
    }

    try {
      await ApiService.deleteProject(projectId)
      await fetchProjects()
      alert(t('projects.deleteSuccess', 'Project successfully deleted!'))
    } catch (err) {
      console.error('Error deleting project:', err)
      alert(t('projects.deleteError', 'Error deleting project: ') + err.message)
    }
  }

  // Open edit modal
  const openEditModal = (project) => {
    setEditingProject(project)
    setFormData({
      name: project.name || '',
      description: project.description || '',
      client_id: project.client_id || '',
      location: project.location || '',
      budget: project.budget || '',
      start_date: project.start_date || '',
      end_date: project.end_date || '',
      status: project.status || 'planning',
      notes: project.notes || ''
    })
    setShowEditModal(true)
  }

  // Get client name by ID
  const getClientName = (clientId) => {
    const client = clients.find(c => c.id === clientId)
    return client ? client.name : t('common.unknown', 'Unknown')
  }

  // Format currency
  const formatCurrency = (amount) => {
    if (!amount) return '€0.00'
    return new Intl.NumberFormat('nl-NL', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0
    }).format(amount)
  }

  // Get status badge variant
  const getStatusVariant = (status) => {
    switch (status?.toLowerCase()) {
      case 'planning': return 'secondary'
      case 'in_progress': return 'default'
      case 'completed': return 'success'
      case 'on_hold': return 'warning'
      case 'cancelled': return 'destructive'
      default: return 'secondary'
    }
  }

  // If a project is selected, show the ProjectPlantManagement component
  if (selectedProject) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <Button
              onClick={() => setSelectedProject(null)}
              variant="outline"
              className="mb-4"
            >
              ← {t('projects.backToProjects', 'Back to Projects')}
            </Button>
            <h1 className="text-2xl font-bold text-gray-900">{selectedProject.name}</h1>
            <p className="text-gray-600">{selectedProject.description}</p>
          </div>
        </div>

        <ProjectPlantManagement
          projectId={selectedProject.id}
        />
      </div>
    )
  }

  // Project Form Component
  const ProjectForm = ({ isEdit = false, onSubmit, onCancel }) => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">
            {isEdit ? t('projects.editProject', 'Edit Project') : t('projects.addProject', 'Add Project')}
          </h2>
          <Button
            variant="ghost"
            size="sm"
            onClick={onCancel}
            aria-label={t('projects.closeForm', 'Close form')}
          >
            <X className="h-4 w-4" />
            <span className="sr-only">{t('projects.closeForm', 'Close form')}</span>
          </Button>
        </div>

        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">
              {t('projects.name', 'Project Name')} *
            </label>
            <Input
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              required
              placeholder={t('projects.namePlaceholder', 'Enter project name')}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              {t('projects.description', 'Description')}
            </label>
            <Textarea
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              rows={3}
              placeholder={t('projects.descriptionPlaceholder', 'Enter project description')}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">
                {t('projects.client', 'Client')} *
              </label>
              <select
                name="client_id"
                value={formData.client_id}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option value="">{t('projects.selectClient', 'Select a client')}</option>
                {clients.map(client => (
                  <option key={client.id} value={client.id}>
                    {client.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                {t('projects.status', 'Status')}
              </label>
              <select
                name="status"
                value={formData.status}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                {statusOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              {t('projects.location', 'Location')}
            </label>
            <Input
              name="location"
              value={formData.location}
              onChange={handleInputChange}
              placeholder={t('projects.locationPlaceholder', 'Enter project location')}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">
                {t('projects.budget', 'Budget')} (€)
              </label>
              <Input
                name="budget"
                type="number"
                value={formData.budget}
                onChange={handleInputChange}
                placeholder="0.00"
                step="0.01"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                {t('projects.startDate', 'Start Date')}
              </label>
              <Input
                name="start_date"
                type="date"
                value={formData.start_date}
                onChange={handleInputChange}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                {t('projects.endDate', 'End Date')}
              </label>
              <Input
                name="end_date"
                type="date"
                value={formData.end_date}
                onChange={handleInputChange}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              {t('projects.notes', 'Notes')}
            </label>
            <Textarea
              name="notes"
              value={formData.notes}
              onChange={handleInputChange}
              rows={3}
              placeholder={t('projects.notesPlaceholder', 'Additional notes about the project')}
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
        {t('projects.errorLoading', 'Error Loading Projects')}
      </h2>
      <p className="text-red-600 mb-4">{error}</p>
      <Button onClick={fetchProjects} variant="destructive">
        {t('common.tryAgain', 'Try Again')}
      </Button>
    </div>
  )

  if (error) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {t('projects.title', 'Projects')}
            </h1>
            <p className="text-gray-600">
              {t('projects.subtitle', 'Manage your landscape architecture projects and their progress')}
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
            {t('projects.title', 'Projects')}
          </h1>
          <p className="text-gray-600">
            {t('projects.subtitle', 'Manage your landscape architecture projects and their progress')}
          </p>
        </div>
        <Button
          className="flex items-center space-x-2"
          onClick={() => setShowAddModal(true)}
        >
          <Plus className="h-4 w-4" />
          <span>{t('projects.newProject', 'New Project')}</span>
        </Button>
      </div>

      {/* Search Bar */}
      <div className="flex items-center space-x-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input
            placeholder={t('projects.searchPlaceholder', 'Search projects...')}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {loading ? (
        <Card>
          <CardContent>
            <LoadingSpinner />
          </CardContent>
        </Card>
      ) : !Array.isArray(projects) || projects.length === 0 ? (
        <Card>
          <CardContent className="p-12">
            <div className="text-center">
              <FolderOpen className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h2 className="text-lg font-semibold text-gray-900 mb-2">
                {t('projects.noProjects', 'No projects found')}
              </h2>
              <p className="text-gray-500 mb-6">
                {searchTerm
                  ? t('projects.noSearchResults', 'No projects match your search criteria')
                  : t('projects.createFirst', 'Create your first project to get started')
                }
              </p>
              <Button onClick={() => setShowAddModal(true)}>
                <Plus className="h-4 w-4 mr-2" />
                {t('projects.newProject', 'New Project')}
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => (
            <Card key={project.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <CardTitle className="text-lg">{project.name}</CardTitle>
                  <Badge variant={getStatusVariant(project.status)}>
                    {statusOptions.find(s => s.value === project.status)?.label || project.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-gray-600 text-sm line-clamp-2">
                  {project.description}
                </p>

                <div className="space-y-2 text-sm">
                  <div className="flex items-center text-gray-600">
                    <Users className="h-4 w-4 mr-2" />
                    <span>{getClientName(project.client_id)}</span>
                  </div>

                  {project.location && (
                    <div className="flex items-center text-gray-600">
                      <MapPin className="h-4 w-4 mr-2" />
                      <span>{project.location}</span>
                    </div>
                  )}

                  {project.start_date && (
                    <div className="flex items-center text-gray-600">
                      <Calendar className="h-4 w-4 mr-2" />
                      <span>{new Date(project.start_date).toLocaleDateString()}</span>
                    </div>
                  )}

                  {project.budget && (
                    <div className="flex items-center text-green-600 font-semibold">
                      <DollarSign className="h-4 w-4 mr-2" />
                      <span>{formatCurrency(project.budget)}</span>
                    </div>
                  )}
                </div>

                <div className="flex space-x-2 pt-2">
                  <Button
                    onClick={() => setSelectedProject(project)}
                    className="flex-1"
                    variant="outline"
                  >
                    {t('projects.managePlants', 'Manage Plants')}
                  </Button>
                  <Button
                    onClick={() => openEditModal(project)}
                    variant="outline"
                    size="sm"
                    aria-label={t('projects.editProject', 'Edit project')}
                  >
                    <Edit className="h-4 w-4" />
                    <span className="sr-only">{t('projects.editProject', 'Edit project')}</span>
                  </Button>
                  <Button
                    onClick={() => handleDeleteProject(project.id, project.name)}
                    variant="outline"
                    size="sm"
                    className="text-red-600 hover:text-red-700"
                    aria-label={t('projects.deleteProject', 'Delete project')}
                  >
                    <Trash2 className="h-4 w-4" />
                    <span className="sr-only">{t('projects.deleteProject', 'Delete project')}</span>
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Add Project Modal */}
      {showAddModal && (
        <ProjectForm
          onSubmit={handleAddProject}
          onCancel={() => {
            setShowAddModal(false)
            resetForm()
          }}
        />
      )}

      {/* Edit Project Modal */}
      {showEditModal && (
        <ProjectForm
          isEdit={true}
          onSubmit={handleEditProject}
          onCancel={() => {
            setShowEditModal(false)
            setEditingProject(null)
            resetForm()
          }}
        />
      )}
    </div>
  )
}

export default Projects
