import React, { useState, useEffect, useCallback, useMemo } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import {
  Calendar,
  Clock,
  CheckCircle,
  AlertTriangle,
  Users,
  FileText,
  Plus,
  MapPin,
  Target,
  TrendingUp
} from 'lucide-react'
import { useLanguage } from '../i18n/LanguageProvider'
import toast from 'react-hot-toast'

const createEmptyMilestone = () => ({
  title: '',
  description: '',
  target_date: '',
  milestone_type: 'design',
  priority: 'medium',
  assigned_to: '',
  notes: ''
})

const ProjectTimeline = () => {
  const { t } = useLanguage()
  const [projects, setProjects] = useState([])
  const [selectedProject, setSelectedProject] = useState(null)
  const [timelineData, setTimelineData] = useState([])
  const [loading, setLoading] = useState(true)
  const [showAddMilestone, setShowAddMilestone] = useState(false)
  const [newMilestone, setNewMilestone] = useState(() => createEmptyMilestone())

  const milestoneTypes = useMemo(() => [
    { value: 'design', label: t('timeline.types.design', 'Design Phase'), icon: FileText, color: 'blue' },
    { value: 'planning', label: t('timeline.types.planning', 'Planning'), icon: Target, color: 'green' },
    { value: 'permits', label: t('timeline.types.permits', 'Permits & Approvals'), icon: AlertTriangle, color: 'yellow' },
    { value: 'preparation', label: t('timeline.types.preparation', 'Site Preparation'), icon: MapPin, color: 'orange' },
    { value: 'installation', label: t('timeline.types.installation', 'Installation'), icon: Users, color: 'purple' },
    { value: 'planting', label: t('timeline.types.planting', 'Planting'), icon: Calendar, color: 'green' },
    { value: 'maintenance', label: t('timeline.types.maintenance', 'Maintenance'), icon: TrendingUp, color: 'teal' },
    { value: 'completion', label: t('timeline.types.completion', 'Project Completion'), icon: CheckCircle, color: 'emerald' }
  ], [t])

  const priorityLevels = useMemo(() => [
    { value: 'low', label: t('timeline.priority.low', 'Low'), color: 'gray' },
    { value: 'medium', label: t('timeline.priority.medium', 'Medium'), color: 'yellow' },
    { value: 'high', label: t('timeline.priority.high', 'High'), color: 'orange' },
    { value: 'critical', label: t('timeline.priority.critical', 'Critical'), color: 'red' }
  ], [t])

  const generateMockTimeline = useCallback((projectId) => {
    const baseDate = new Date()
    return [
      {
        id: 1,
        project_id: projectId,
        title: t('timeline.demo.initialConsultation', 'Initial Consultation'),
        description: t('timeline.demo.consultationDesc', 'Meet with client to discuss requirements and vision'),
        target_date: new Date(baseDate.getTime() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        completed_date: new Date(baseDate.getTime() - 28 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        milestone_type: 'design',
        priority: 'high',
        status: 'completed',
        assigned_to: 'Design Team',
        notes: t('timeline.demo.consultationNotes', 'Completed successfully. Client approved initial concept.')
      },
      {
        id: 2,
        project_id: projectId,
        title: t('timeline.demo.siteAnalysis', 'Site Analysis & Survey'),
        description: t('timeline.demo.analysisDesc', 'Detailed site measurement and soil analysis'),
        target_date: new Date(baseDate.getTime() - 20 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        completed_date: new Date(baseDate.getTime() - 18 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        milestone_type: 'planning',
        priority: 'high',
        status: 'completed',
        assigned_to: 'Survey Team',
        notes: t('timeline.demo.analysisNotes', 'Site survey completed. Soil test results pending.')
      },
      {
        id: 3,
        project_id: projectId,
        title: t('timeline.demo.designDevelopment', 'Design Development'),
        description: t('timeline.demo.designDesc', 'Create detailed landscape design and plant selections'),
        target_date: new Date(baseDate.getTime() - 5 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        completed_date: null,
        milestone_type: 'design',
        priority: 'high',
        status: 'in_progress',
        assigned_to: 'Design Team',
        notes: t('timeline.demo.designNotes', 'Design 80% complete. Awaiting client feedback on plant selections.')
      },
      {
        id: 4,
        project_id: projectId,
        title: t('timeline.demo.permitSubmission', 'Permit Submission'),
        description: t('timeline.demo.permitDesc', 'Submit landscape plans for municipal approval'),
        target_date: new Date(baseDate.getTime() + 10 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        completed_date: null,
        milestone_type: 'permits',
        priority: 'medium',
        status: 'pending',
        assigned_to: 'Admin Team',
        notes: ''
      },
      {
        id: 5,
        project_id: projectId,
        title: t('timeline.demo.materialProcurement', 'Material Procurement'),
        description: t('timeline.demo.procurementDesc', 'Order plants, materials, and equipment'),
        target_date: new Date(baseDate.getTime() + 25 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        completed_date: null,
        milestone_type: 'preparation',
        priority: 'medium',
        status: 'pending',
        assigned_to: 'Procurement Team',
        notes: ''
      },
      {
        id: 6,
        project_id: projectId,
        title: t('timeline.demo.installation', 'Installation Phase'),
        description: t('timeline.demo.installationDesc', 'Begin landscape installation and planting'),
        target_date: new Date(baseDate.getTime() + 40 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        completed_date: null,
        milestone_type: 'installation',
        priority: 'high',
        status: 'pending',
        assigned_to: 'Installation Team',
        notes: ''
      }
    ]
  }, [t])

  const fetchProjectTimeline = useCallback(async (projectId) => {
    if (!projectId) {
      setTimelineData([])
      return
    }

    try {
      const response = await fetch(`/api/projects/${projectId}/timeline`, {
        credentials: 'include'
      })

      if (response.ok) {
        const data = await response.json()
        setTimelineData(data.timeline || [])
      } else {
        setTimelineData(generateMockTimeline(projectId))
      }
    } catch (error) {
      console.error('Error fetching timeline:', error)
      setTimelineData(generateMockTimeline(projectId))
    }
  }, [generateMockTimeline])

  const fetchProjects = useCallback(async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/projects', {
        credentials: 'include'
      })

      if (response.ok) {
        const data = await response.json()
        const fetchedProjects = data.projects || []
        setProjects(fetchedProjects)

        if (fetchedProjects.length > 0) {
          setSelectedProject(fetchedProjects[0])
        } else {
          setSelectedProject(null)
          setTimelineData([])
        }
      } else {
        toast.error(t('timeline.errors.fetchProjects', 'Failed to load projects'))
      }
    } catch (error) {
      console.error('Error fetching projects:', error)
      toast.error(t('timeline.errors.fetchProjects', 'Failed to load projects'))
    } finally {
      setLoading(false)
    }
  }, [t])

  useEffect(() => {
    fetchProjects()
  }, [fetchProjects])

  useEffect(() => {
    if (selectedProject) {
      fetchProjectTimeline(selectedProject.id)
    } else {
      setTimelineData([])
    }
  }, [selectedProject, fetchProjectTimeline])

  const addMilestone = () => {
    if (!newMilestone.title || !newMilestone.target_date) {
      toast.error(t('timeline.errors.missingFields', 'Please fill in all required fields'))
      return
    }

    if (!selectedProject) {
      toast.error(t('timeline.errors.noProjectSelected', 'Select a project before adding milestones'))
      return
    }

    const milestone = {
      id: timelineData.length + 1,
      project_id: selectedProject.id,
      ...newMilestone,
      status: 'pending',
      created_at: new Date().toISOString()
    }

    setTimelineData(prev => [...prev, milestone])
    setNewMilestone(createEmptyMilestone())
    setShowAddMilestone(false)
    toast.success(t('timeline.success.milestoneAdded', 'Milestone added successfully'))
  }

  const updateMilestoneStatus = (milestoneId, newStatus) => {
    try {
      const updatedTimeline = timelineData.map(milestone =>
        milestone.id === milestoneId
          ? {
            ...milestone,
            status: newStatus,
            completed_date: newStatus === 'completed' ? new Date().toISOString().split('T')[0] : null
          }
          : milestone
      )

      setTimelineData(updatedTimeline)
      toast.success(t('timeline.success.statusUpdated', 'Status updated successfully'))
    } catch (error) {
      console.error('Error updating milestone:', error)
      toast.error(t('timeline.errors.updateStatus', 'Failed to update status'))
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'in_progress':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'delayed':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'pending':
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getPriorityColor = (priority) => {
    const level = priorityLevels.find(item => item.value === priority)
    return level ? `text-${level.color}-600` : 'text-gray-600'
  }

  const getTypeIcon = (type) => {
    const milestoneType = milestoneTypes.find(item => item.value === type)
    return milestoneType ? milestoneType.icon : FileText
  }

  const completedCount = timelineData.filter(milestone => milestone.status === 'completed').length
  const inProgressCount = timelineData.filter(milestone => milestone.status === 'in_progress').length
  const pendingCount = timelineData.filter(milestone => milestone.status === 'pending').length
  const progressPercent = timelineData.length === 0
    ? 0
    : Math.round((completedCount / timelineData.length) * 100)

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p className="text-gray-600">{t('common.loading', 'Loading...')}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                <Calendar className="h-8 w-8 text-green-600" />
                {t('timeline.title', 'Project Timeline')}
              </h1>
              <p className="text-gray-600 mt-2">
                {t('timeline.subtitle', 'Track project milestones and progress')}
              </p>
            </div>
            <button
              onClick={() => setShowAddMilestone(true)}
              className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
            >
              <Plus className="h-5 w-5" />
              {t('timeline.addMilestone', 'Add Milestone')}
            </button>
          </div>
        </div>

        {/* Project Selector */}
        <div className="mb-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MapPin className="h-5 w-5" />
                {t('timeline.selectProject', 'Select Project')}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <select
                value={selectedProject?.id || ''}
                onChange={(event) => {
                  const projectId = Number(event.target.value)
                  const project = projects.find(item => item.id === projectId) || null
                  setSelectedProject(project)
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              >
                <option value="">{t('timeline.chooseProject', 'Choose a project...')}</option>
                {projects.map(project => (
                  <option key={project.id} value={project.id}>
                    {project.name} - {project.client_name}
                  </option>
                ))}
              </select>
            </CardContent>
          </Card>
        </div>

        {/* Timeline Content */}
        {selectedProject && (
          <>
            {/* Project Summary */}
            <div className="mb-6 grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-white rounded-lg p-4 shadow-sm border">
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-8 w-8 text-green-600" />
                  <div>
                    <p className="text-sm text-gray-600">{t('timeline.stats.completed', 'Completed')}</p>
                    <p className="text-2xl font-bold text-gray-900">{completedCount}</p>
                  </div>
                </div>
              </div>
              <div className="bg-white rounded-lg p-4 shadow-sm border">
                <div className="flex items-center gap-3">
                  <Clock className="h-8 w-8 text-blue-600" />
                  <div>
                    <p className="text-sm text-gray-600">{t('timeline.stats.inProgress', 'In Progress')}</p>
                    <p className="text-2xl font-bold text-gray-900">{inProgressCount}</p>
                  </div>
                </div>
              </div>
              <div className="bg-white rounded-lg p-4 shadow-sm border">
                <div className="flex items-center gap-3">
                  <AlertTriangle className="h-8 w-8 text-orange-600" />
                  <div>
                    <p className="text-sm text-gray-600">{t('timeline.stats.pending', 'Pending')}</p>
                    <p className="text-2xl font-bold text-gray-900">{pendingCount}</p>
                  </div>
                </div>
              </div>
              <div className="bg-white rounded-lg p-4 shadow-sm border">
                <div className="flex items-center gap-3">
                  <TrendingUp className="h-8 w-8 text-purple-600" />
                  <div>
                    <p className="text-sm text-gray-600">{t('timeline.stats.progress', 'Progress')}</p>
                    <p className="text-2xl font-bold text-gray-900">{progressPercent}%</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Timeline */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="h-5 w-5" />
                  {t('timeline.projectTimeline', 'Project Timeline')} - {selectedProject.name}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {timelineData.length === 0 ? (
                    <div className="text-center py-12">
                      <Calendar className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                      <h3 className="text-lg font-semibold text-gray-600 mb-2">
                        {t('timeline.noMilestones', 'No milestones yet')}
                      </h3>
                      <p className="text-gray-500 mb-4">
                        {t('timeline.addFirstMilestone', 'Add your first milestone to get started')}
                      </p>
                    </div>
                  ) : (
                    timelineData.map((milestone, index) => {
                      const Icon = getTypeIcon(milestone.milestone_type)
                      const isLast = index === timelineData.length - 1

                      return (
                        <div key={milestone.id} className="flex gap-4">
                          {/* Timeline connector */}
                          <div className="flex flex-col items-center">
                            <div
                              className={`p-2 rounded-full ${milestone.status === 'completed'
                                  ? 'bg-green-100 text-green-600'
                                  : milestone.status === 'in_progress'
                                    ? 'bg-blue-100 text-blue-600'
                                    : 'bg-gray-100 text-gray-400'
                                }`}
                            >
                              <Icon className="h-5 w-5" />
                            </div>
                            {!isLast && (
                              <div
                                className={`w-px h-16 ${milestone.status === 'completed' ? 'bg-green-200' : 'bg-gray-200'
                                  }`}
                              />
                            )}
                          </div>

                          {/* Milestone content */}
                          <div className="flex-1 pb-8">
                            <div className="bg-white rounded-lg border shadow-sm p-4">
                              <div className="flex items-start justify-between mb-3">
                                <div>
                                  <h3 className="font-semibold text-gray-900">{milestone.title}</h3>
                                  <p className="text-gray-600 text-sm">{milestone.description}</p>
                                </div>
                                <div className="flex flex-col items-end gap-2">
                                  <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(milestone.status)}`}>
                                    {t(`timeline.status.${milestone.status}`, milestone.status)}
                                  </span>
                                  <span className={`text-xs font-medium ${getPriorityColor(milestone.priority)}`}>
                                    {t(`timeline.priority.${milestone.priority}`, milestone.priority)}
                                  </span>
                                </div>
                              </div>

                              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                                <div>
                                  <span className="font-medium">{t('timeline.targetDate', 'Target Date')}:</span>
                                  <br />
                                  {new Date(milestone.target_date).toLocaleDateString()}
                                </div>
                                {milestone.completed_date && (
                                  <div>
                                    <span className="font-medium">{t('timeline.completedDate', 'Completed')}:</span>
                                    <br />
                                    {new Date(milestone.completed_date).toLocaleDateString()}
                                  </div>
                                )}
                                <div>
                                  <span className="font-medium">{t('timeline.assignedTo', 'Assigned To')}:</span>
                                  <br />
                                  {milestone.assigned_to || t('timeline.unassigned', 'Unassigned')}
                                </div>
                              </div>

                              {milestone.notes && (
                                <div className="mt-3 p-3 bg-gray-50 rounded-lg text-sm">
                                  <span className="font-medium text-gray-700">{t('timeline.notes', 'Notes')}:</span>
                                  <br />
                                  {milestone.notes}
                                </div>
                              )}

                              {/* Actions */}
                              <div className="mt-4 flex gap-2">
                                {milestone.status !== 'completed' && (
                                  <button
                                    onClick={() => updateMilestoneStatus(milestone.id, 'completed')}
                                    className="px-3 py-1 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 transition-colors"
                                  >
                                    {t('timeline.markComplete', 'Mark Complete')}
                                  </button>
                                )}
                                {milestone.status === 'pending' && (
                                  <button
                                    onClick={() => updateMilestoneStatus(milestone.id, 'in_progress')}
                                    className="px-3 py-1 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors"
                                  >
                                    {t('timeline.startProgress', 'Start Progress')}
                                  </button>
                                )}
                              </div>
                            </div>
                          </div>
                        </div>
                      )
                    })
                  )}
                </div>
              </CardContent>
            </Card>
          </>
        )}

        {/* Add Milestone Modal */}
        {showAddMilestone && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-2xl w-full max-h-90vh overflow-y-auto">
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-bold text-gray-900">
                    {t('timeline.addMilestone', 'Add Milestone')}
                  </h2>
                  <button
                    onClick={() => setShowAddMilestone(false)}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    ×
                  </button>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {t('timeline.form.title', 'Title')} *
                    </label>
                    <input
                      type="text"
                      value={newMilestone.title}
                      onChange={(event) => setNewMilestone(prev => ({ ...prev, title: event.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                      placeholder={t('timeline.form.titlePlaceholder', 'Enter milestone title...')}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {t('timeline.form.description', 'Description')}
                    </label>
                    <textarea
                      value={newMilestone.description}
                      onChange={(event) => setNewMilestone(prev => ({ ...prev, description: event.target.value }))}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                      placeholder={t('timeline.form.descriptionPlaceholder', 'Enter milestone description...')}
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {t('timeline.form.targetDate', 'Target Date')} *
                      </label>
                      <input
                        type="date"
                        value={newMilestone.target_date}
                        onChange={(event) => setNewMilestone(prev => ({ ...prev, target_date: event.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {t('timeline.form.type', 'Milestone Type')}
                      </label>
                      <select
                        value={newMilestone.milestone_type}
                        onChange={(event) => setNewMilestone(prev => ({ ...prev, milestone_type: event.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                      >
                        {milestoneTypes.map(type => (
                          <option key={type.value} value={type.value}>
                            {type.label}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {t('timeline.form.priority', 'Priority')}
                      </label>
                      <select
                        value={newMilestone.priority}
                        onChange={(event) => setNewMilestone(prev => ({ ...prev, priority: event.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                      >
                        {priorityLevels.map(priority => (
                          <option key={priority.value} value={priority.value}>
                            {priority.label}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {t('timeline.form.assignedTo', 'Assigned To')}
                      </label>
                      <input
                        type="text"
                        value={newMilestone.assigned_to}
                        onChange={(event) => setNewMilestone(prev => ({ ...prev, assigned_to: event.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                        placeholder={t('timeline.form.assignedToPlaceholder', 'Team or person responsible...')}
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {t('timeline.form.notes', 'Notes')}
                    </label>
                    <textarea
                      value={newMilestone.notes}
                      onChange={(event) => setNewMilestone(prev => ({ ...prev, notes: event.target.value }))}
                      rows={2}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                      placeholder={t('timeline.form.notesPlaceholder', 'Additional notes or requirements...')}
                    />
                  </div>
                </div>

                <div className="flex gap-3 mt-6">
                  <button
                    onClick={addMilestone}
                    className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                  >
                    {t('timeline.form.addMilestone', 'Add Milestone')}
                  </button>
                  <button
                    onClick={() => setShowAddMilestone(false)}
                    className="px-6 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors"
                  >
                    {t('common.cancel', 'Cancel')}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default ProjectTimeline