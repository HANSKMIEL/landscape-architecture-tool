import { useLanguage } from "../i18n/LanguageProvider";
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { FolderOpen, Plus, Users, MapPin, Calendar, Loader2 } from 'lucide-react'
import ProjectPlantManagement from './ProjectPlantManagement'
import ApiService from '../services/api';

const Projects = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedProject, setSelectedProject] = useState(null);

  const translations = {
    en: {
      title: 'Projects',
      subtitle: 'Manage your landscape architecture projects and their progress',
      newProject: 'New Project',
      backToProjects: 'Back to Projects',
      client: 'Client',
      location: 'Location',
      budget: 'Budget',
      startDate: 'Start Date',
      status: 'Status',
      managePlants: 'Manage Plants',
      noProjects: 'No projects found',
      createFirst: 'Create your first project to get started',
      loading: 'Loading projects...'
    },
    nl: {
      title: 'Projecten',
      subtitle: 'Beheer uw landschapsarchitectuur projecten en hun voortgang',
      newProject: 'Nieuw Project',
      backToProjects: 'Terug naar Projecten',
      client: 'Klant',
      location: 'Locatie',
      budget: 'Budget',
      startDate: 'Startdatum',
      status: 'Status',
      managePlants: 'Planten Beheren',
      noProjects: 'Geen projecten gevonden',
      createFirst: 'Maak je eerste project aan om te beginnen',
      loading: 'Projecten laden...'
    }
  }

  const { t } = useLanguage();

  // Fetch projects from API
  const fetchProjects = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await ApiService.getProjects();
      // API returns { projects: [...] } format
      setProjects(data.projects || []);
    } catch (err) {
      console.error('Error fetching projects:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  // Format currency
  const formatCurrency = (amount) => {
    if (!amount) return '€0.00';
    return new Intl.NumberFormat('nl-NL', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0
    }).format(amount);
  };

  // Get status badge variant
  const getStatusVariant = (status) => {
    switch (status?.toLowerCase()) {
      case 'planning': return 'secondary';
      case 'in progress': return 'warning';
      case 'completed': return 'success';
      case 'on hold': return 'destructive';
      default: return 'secondary';
    }
  };

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
              ← {t.backToProjects}
            </Button>
            <h1 className="text-2xl font-bold text-gray-900">{selectedProject.name}</h1>
            <p className="text-gray-600">{selectedProject.description}</p>
          </div>
        </div>

        <ProjectPlantManagement 
          projectId={selectedProject.id} 
           
        />
      </div>
    );
  }

  // Loading component
  const LoadingSpinner = () => (
    <div className="flex justify-center items-center py-12">
      <Loader2 className="h-8 w-8 animate-spin text-green-600" />
      <span className="ml-2 text-gray-600">{t.loading}</span>
    </div>
  );

  // Error component
  const ErrorDisplay = () => (
    <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
      <div className="w-12 h-12 mx-auto mb-4 bg-red-100 rounded-full flex items-center justify-center">
        <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <h2 className="text-lg font-semibold text-red-800 mb-2">Error Loading Projects</h2>
      <p className="text-red-600 mb-4">{error}</p>
      <Button onClick={fetchProjects} variant="destructive">
        Try Again
      </Button>
    </div>
  );

  if (error) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{t.title}</h1>
            <p className="text-gray-600">{t.subtitle}</p>
          </div>
        </div>
        <ErrorDisplay />
      </div>
    );
  }

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
              <h2 className="text-lg font-semibold text-gray-900 mb-2">{t.noProjects}</h2>
              <p className="text-gray-500 mb-6">{t.createFirst}</p>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                {t.newProject}
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.isArray(projects) ? projects.map((project) => (
            <Card key={project.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <CardTitle className="text-lg">{project.name}</CardTitle>
                  <Badge variant={getStatusVariant(project.status)}>
                    {project.status}
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
                    <span>{project.client_name}</span>
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
                      <span>{project.start_date}</span>
                    </div>
                  )}
                  
                  {project.budget && (
                    <div className="text-green-600 font-semibold">
                      {formatCurrency(project.budget)}
                    </div>
                  )}
                </div>

                <Button 
                  onClick={() => setSelectedProject(project)} 
                  className="w-full mt-4"
                  variant="outline"
                >
                  {t.managePlants}
                </Button>
              </CardContent>
            </Card>
          )) : (
            <div className="col-span-full text-center py-8 text-gray-500">
              No projects data available
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default Projects

