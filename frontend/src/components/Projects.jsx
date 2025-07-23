// Enhanced Projects Component
// File location: frontend/src/components/Projects.jsx
// This component provides complete project management with plant/product selection

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Textarea } from '@/components/ui/textarea';
import { Progress } from '@/components/ui/progress';
import { toast } from 'sonner';
import { Search, Plus, Edit, Trash2, FolderOpen, Calendar, Euro, Users, Leaf, Package, MapPin, Clock } from 'lucide-react';
import { apiService } from '../services/api';

const Projects = () => {
  const [projects, setProjects] = useState([]);
  const [clients, setClients] = useState([]);
  const [plants, setPlants] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('');
  const [selectedClient, setSelectedClient] = useState('');
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [showPlantsDialog, setShowPlantsDialog] = useState(false);
  const [showProductsDialog, setShowProductsDialog] = useState(false);
  const [editingProject, setEditingProject] = useState(null);
  const [selectedProject, setSelectedProject] = useState(null);
  const [stats, setStats] = useState({});

  const [newProject, setNewProject] = useState({
    name: '',
    description: '',
    client_id: '',
    status: 'planning',
    budget: '',
    start_date: '',
    end_date: '',
    location: '',
    notes: ''
  });

  const statusOptions = [
    { value: 'planning', label: 'Planning', color: 'bg-blue-100 text-blue-800' },
    { value: 'in_progress', label: 'In Progress', color: 'bg-yellow-100 text-yellow-800' },
    { value: 'completed', label: 'Completed', color: 'bg-green-100 text-green-800' },
    { value: 'on_hold', label: 'On Hold', color: 'bg-gray-100 text-gray-800' },
    { value: 'cancelled', label: 'Cancelled', color: 'bg-red-100 text-red-800' }
  ];

  const fetchProjects = useCallback(async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (searchTerm) params.append('search', searchTerm);
      if (selectedStatus) params.append('status', selectedStatus);
      if (selectedClient) params.append('client_id', selectedClient);
      
      const response = await apiService.get(`/api/projects?${params.toString()}`);
      setProjects(response.projects || []);
      setStats(response.stats || {});
    } catch (error) {
      console.error('Error fetching projects:', error);
      toast.error('Failed to load projects');
    } finally {
      setLoading(false);
    }
  }, [searchTerm, selectedStatus, selectedClient]);

  const fetchClients = useCallback(async () => {
    try {
      const response = await apiService.get('/api/clients');
      setClients(response.clients || []);
    } catch (error) {
      console.error('Error fetching clients:', error);
    }
  }, []);

  const fetchPlants = useCallback(async () => {
    try {
      const response = await apiService.get('/api/plants');
      setPlants(response.plants || []);
    } catch (error) {
      console.error('Error fetching plants:', error);
    }
  }, []);

  const fetchProducts = useCallback(async () => {
    try {
      const response = await apiService.get('/api/products');
      setProducts(response.products || []);
    } catch (error) {
      console.error('Error fetching products:', error);
    }
  }, []);

  useEffect(() => {
    fetchProjects();
    fetchClients();
    fetchPlants();
    fetchProducts();
  }, [fetchProjects, fetchClients, fetchPlants, fetchProducts]);

  const handleAddProject = async (e) => {
    e.preventDefault();
    try {
      const projectData = {
        ...newProject,
        client_id: newProject.client_id ? parseInt(newProject.client_id) : null,
        budget: newProject.budget ? parseFloat(newProject.budget) : null
      };

      await apiService.post('/api/projects', projectData);
      toast.success('Project added successfully');
      setShowAddDialog(false);
      setNewProject({
        name: '',
        description: '',
        client_id: '',
        status: 'planning',
        budget: '',
        start_date: '',
        end_date: '',
        location: '',
        notes: ''
      });
      fetchProjects();
    } catch (error) {
      console.error('Error adding project:', error);
      toast.error('Failed to add project');
    }
  };

  const handleEditProject = async (e) => {
    e.preventDefault();
    try {
      const projectData = {
        ...editingProject,
        client_id: editingProject.client_id ? parseInt(editingProject.client_id) : null,
        budget: editingProject.budget ? parseFloat(editingProject.budget) : null
      };

      await apiService.put(`/api/projects/${editingProject.id}`, projectData);
      toast.success('Project updated successfully');
      setShowEditDialog(false);
      setEditingProject(null);
      fetchProjects();
    } catch (error) {
      console.error('Error updating project:', error);
      toast.error('Failed to update project');
    }
  };

  const handleDeleteProject = async (projectId) => {
    if (!confirm('Are you sure you want to delete this project?')) return;
    
    try {
      await apiService.delete(`/api/projects/${projectId}`);
      toast.success('Project deleted successfully');
      fetchProjects();
    } catch (error) {
      console.error('Error deleting project:', error);
      toast.error('Failed to delete project');
    }
  };

  const handleAddPlantToProject = async (plantId) => {
    try {
      await apiService.post(`/api/projects/${selectedProject.id}/plants`, { plant_id: plantId });
      toast.success('Plant added to project');
      // Refresh project data
      const updatedProject = await apiService.get(`/api/projects/${selectedProject.id}`);
      setSelectedProject(updatedProject);
    } catch (error) {
      console.error('Error adding plant to project:', error);
      toast.error('Failed to add plant to project');
    }
  };

  const handleRemovePlantFromProject = async (plantId) => {
    try {
      await apiService.delete(`/api/projects/${selectedProject.id}/plants/${plantId}`);
      toast.success('Plant removed from project');
      // Refresh project data
      const updatedProject = await apiService.get(`/api/projects/${selectedProject.id}`);
      setSelectedProject(updatedProject);
    } catch (error) {
      console.error('Error removing plant from project:', error);
      toast.error('Failed to remove plant from project');
    }
  };

  const handleAddProductToProject = async (productId) => {
    try {
      await apiService.post(`/api/projects/${selectedProject.id}/products`, { product_id: productId });
      toast.success('Product added to project');
      // Refresh project data
      const updatedProject = await apiService.get(`/api/projects/${selectedProject.id}`);
      setSelectedProject(updatedProject);
    } catch (error) {
      console.error('Error adding product to project:', error);
      toast.error('Failed to add product to project');
    }
  };

  const handleRemoveProductFromProject = async (productId) => {
    try {
      await apiService.delete(`/api/projects/${selectedProject.id}/products/${productId}`);
      toast.success('Product removed from project');
      // Refresh project data
      const updatedProject = await apiService.get(`/api/projects/${selectedProject.id}`);
      setSelectedProject(updatedProject);
    } catch (error) {
      console.error('Error removing product from project:', error);
      toast.error('Failed to remove product from project');
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = statusOptions.find(s => s.value === status);
    return statusConfig ? (
      <Badge className={statusConfig.color}>
        {statusConfig.label}
      </Badge>
    ) : <Badge variant="secondary">{status}</Badge>;
  };

  const calculateProgress = (project) => {
    if (project.status === 'completed') return 100;
    if (project.status === 'cancelled') return 0;
    if (project.status === 'planning') return 10;
    if (project.status === 'in_progress') {
      // Calculate based on dates if available
      if (project.start_date && project.end_date) {
        const start = new Date(project.start_date);
        const end = new Date(project.end_date);
        const now = new Date();
        const total = end - start;
        const elapsed = now - start;
        const progress = Math.max(0, Math.min(100, (elapsed / total) * 100));
        return Math.round(progress);
      }
      return 50; // Default for in progress
    }
    return 0;
  };

  const filteredProjects = projects.filter(project => {
    const matchesSearch = project.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         project.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         project.location?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = !selectedStatus || project.status === selectedStatus;
    const matchesClient = !selectedClient || project.client_id === parseInt(selectedClient);
    
    return matchesSearch && matchesStatus && matchesClient;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Stats */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Projects</h1>
          <p className="text-gray-600">Manage your landscape architecture projects</p>
        </div>
        <div className="flex gap-4">
          <Card className="p-4">
            <div className="flex items-center gap-2">
              <FolderOpen className="h-5 w-5 text-green-600" />
              <div>
                <p className="text-2xl font-bold">{stats.total_projects || projects.length}</p>
                <p className="text-sm text-gray-600">Total Projects</p>
              </div>
            </div>
          </Card>
          <Card className="p-4">
            <div className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-blue-600" />
              <div>
                <p className="text-2xl font-bold">{stats.active_projects || 0}</p>
                <p className="text-sm text-gray-600">Active Projects</p>
              </div>
            </div>
          </Card>
          <Card className="p-4">
            <div className="flex items-center gap-2">
              <Euro className="h-5 w-5 text-purple-600" />
              <div>
                <p className="text-2xl font-bold">€{stats.total_budget?.toLocaleString() || '0'}</p>
                <p className="text-sm text-gray-600">Total Budget</p>
              </div>
            </div>
          </Card>
        </div>
      </div>

      {/* Controls */}
      <div className="flex flex-col sm:flex-row gap-4 justify-between">
        <div className="flex flex-1 gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <Input
              placeholder="Search projects..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          <Select value={selectedStatus} onValueChange={setSelectedStatus}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="All Statuses" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All Statuses</SelectItem>
              {statusOptions.map(status => (
                <SelectItem key={status.value} value={status.value}>{status.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={selectedClient} onValueChange={setSelectedClient}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="All Clients" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All Clients</SelectItem>
              {clients.map(client => (
                <SelectItem key={client.id} value={client.id.toString()}>
                  {client.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        
        <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Add Project
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Add New Project</DialogTitle>
              <DialogDescription>
                Enter the project details below.
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleAddProject} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="name">Project Name *</Label>
                  <Input
                    id="name"
                    value={newProject.name}
                    onChange={(e) => setNewProject({...newProject, name: e.target.value})}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="client">Client *</Label>
                  <Select 
                    value={newProject.client_id} 
                    onValueChange={(value) => setNewProject({...newProject, client_id: value})}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select client" />
                    </SelectTrigger>
                    <SelectContent>
                      {clients.map(client => (
                        <SelectItem key={client.id} value={client.id.toString()}>
                          {client.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="status">Status</Label>
                  <Select 
                    value={newProject.status} 
                    onValueChange={(value) => setNewProject({...newProject, status: value})}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select status" />
                    </SelectTrigger>
                    <SelectContent>
                      {statusOptions.map(status => (
                        <SelectItem key={status.value} value={status.value}>{status.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="budget">Budget (€)</Label>
                  <Input
                    id="budget"
                    type="number"
                    step="0.01"
                    value={newProject.budget}
                    onChange={(e) => setNewProject({...newProject, budget: e.target.value})}
                  />
                </div>
                <div>
                  <Label htmlFor="start_date">Start Date</Label>
                  <Input
                    id="start_date"
                    type="date"
                    value={newProject.start_date}
                    onChange={(e) => setNewProject({...newProject, start_date: e.target.value})}
                  />
                </div>
                <div>
                  <Label htmlFor="end_date">End Date</Label>
                  <Input
                    id="end_date"
                    type="date"
                    value={newProject.end_date}
                    onChange={(e) => setNewProject({...newProject, end_date: e.target.value})}
                  />
                </div>
                <div className="col-span-2">
                  <Label htmlFor="location">Location</Label>
                  <Input
                    id="location"
                    value={newProject.location}
                    onChange={(e) => setNewProject({...newProject, location: e.target.value})}
                    placeholder="Project location or address"
                  />
                </div>
              </div>
              <div>
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={newProject.description}
                  onChange={(e) => setNewProject({...newProject, description: e.target.value})}
                  rows={3}
                  placeholder="Project description and objectives..."
                />
              </div>
              <div>
                <Label htmlFor="notes">Notes</Label>
                <Textarea
                  id="notes"
                  value={newProject.notes}
                  onChange={(e) => setNewProject({...newProject, notes: e.target.value})}
                  rows={2}
                  placeholder="Additional notes..."
                />
              </div>
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setShowAddDialog(false)}>
                  Cancel
                </Button>
                <Button type="submit">Add Project</Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Projects Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredProjects.map((project) => (
          <Card key={project.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <CardTitle className="text-lg">{project.name}</CardTitle>
                  <CardDescription className="mt-1">
                    {project.client_name}
                  </CardDescription>
                </div>
                {getStatusBadge(project.status)}
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {project.description && (
                  <p className="text-sm text-gray-600 line-clamp-2">{project.description}</p>
                )}
                
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Progress</span>
                    <span>{calculateProgress(project)}%</span>
                  </div>
                  <Progress value={calculateProgress(project)} className="h-2" />
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm">
                  {project.budget && (
                    <div className="flex items-center gap-1">
                      <Euro className="h-3 w-3 text-gray-400" />
                      <span>€{project.budget.toLocaleString()}</span>
                    </div>
                  )}
                  {project.location && (
                    <div className="flex items-center gap-1">
                      <MapPin className="h-3 w-3 text-gray-400" />
                      <span className="truncate">{project.location}</span>
                    </div>
                  )}
                  {project.start_date && (
                    <div className="flex items-center gap-1">
                      <Calendar className="h-3 w-3 text-gray-400" />
                      <span>{new Date(project.start_date).toLocaleDateString()}</span>
                    </div>
                  )}
                  <div className="flex items-center gap-1">
                    <Leaf className="h-3 w-3 text-green-600" />
                    <span>{project.plant_count || 0} plants</span>
                  </div>
                </div>

                <div className="flex gap-2 pt-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setSelectedProject(project);
                      setShowPlantsDialog(true);
                    }}
                  >
                    <Leaf className="h-3 w-3 mr-1" />
                    Plants
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setSelectedProject(project);
                      setShowProductsDialog(true);
                    }}
                  >
                    <Package className="h-3 w-3 mr-1" />
                    Products
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      setEditingProject(project);
                      setShowEditDialog(true);
                    }}
                  >
                    <Edit className="h-3 w-3" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDeleteProject(project.id)}
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredProjects.length === 0 && (
        <Card>
          <CardContent className="text-center py-8">
            <FolderOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No projects found</p>
            {searchTerm && (
              <p className="text-sm text-gray-400 mt-2">
                Try adjusting your search terms
              </p>
            )}
          </CardContent>
        </Card>
      )}

      {/* Edit Project Dialog */}
      <Dialog open={showEditDialog} onOpenChange={setShowEditDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Edit Project</DialogTitle>
            <DialogDescription>
              Update the project details below.
            </DialogDescription>
          </DialogHeader>
          {editingProject && (
            <form onSubmit={handleEditProject} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="edit-name">Project Name *</Label>
                  <Input
                    id="edit-name"
                    value={editingProject.name}
                    onChange={(e) => setEditingProject({...editingProject, name: e.target.value})}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="edit-client">Client *</Label>
                  <Select 
                    value={editingProject.client_id?.toString() || ''} 
                    onValueChange={(value) => setEditingProject({...editingProject, client_id: value})}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select client" />
                    </SelectTrigger>
                    <SelectContent>
                      {clients.map(client => (
                        <SelectItem key={client.id} value={client.id.toString()}>
                          {client.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="edit-status">Status</Label>
                  <Select 
                    value={editingProject.status} 
                    onValueChange={(value) => setEditingProject({...editingProject, status: value})}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select status" />
                    </SelectTrigger>
                    <SelectContent>
                      {statusOptions.map(status => (
                        <SelectItem key={status.value} value={status.value}>{status.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="edit-budget">Budget (€)</Label>
                  <Input
                    id="edit-budget"
                    type="number"
                    step="0.01"
                    value={editingProject.budget || ''}
                    onChange={(e) => setEditingProject({...editingProject, budget: e.target.value})}
                  />
                </div>
                <div>
                  <Label htmlFor="edit-start_date">Start Date</Label>
                  <Input
                    id="edit-start_date"
                    type="date"
                    value={editingProject.start_date || ''}
                    onChange={(e) => setEditingProject({...editingProject, start_date: e.target.value})}
                  />
                </div>
                <div>
                  <Label htmlFor="edit-end_date">End Date</Label>
                  <Input
                    id="edit-end_date"
                    type="date"
                    value={editingProject.end_date || ''}
                    onChange={(e) => setEditingProject({...editingProject, end_date: e.target.value})}
                  />
                </div>
                <div className="col-span-2">
                  <Label htmlFor="edit-location">Location</Label>
                  <Input
                    id="edit-location"
                    value={editingProject.location || ''}
                    onChange={(e) => setEditingProject({...editingProject, location: e.target.value})}
                    placeholder="Project location or address"
                  />
                </div>
              </div>
              <div>
                <Label htmlFor="edit-description">Description</Label>
                <Textarea
                  id="edit-description"
                  value={editingProject.description || ''}
                  onChange={(e) => setEditingProject({...editingProject, description: e.target.value})}
                  rows={3}
                  placeholder="Project description and objectives..."
                />
              </div>
              <div>
                <Label htmlFor="edit-notes">Notes</Label>
                <Textarea
                  id="edit-notes"
                  value={editingProject.notes || ''}
                  onChange={(e) => setEditingProject({...editingProject, notes: e.target.value})}
                  rows={2}
                  placeholder="Additional notes..."
                />
              </div>
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setShowEditDialog(false)}>
                  Cancel
                </Button>
                <Button type="submit">Update Project</Button>
              </DialogFooter>
            </form>
          )}
        </DialogContent>
      </Dialog>

      {/* Plants Dialog */}
      <Dialog open={showPlantsDialog} onOpenChange={setShowPlantsDialog}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Project Plants - {selectedProject?.name}</DialogTitle>
            <DialogDescription>
              Manage plants for this project
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div>
              <h4 className="font-medium mb-2">Current Plants ({selectedProject?.plants?.length || 0})</h4>
              {selectedProject?.plants?.length > 0 ? (
                <div className="border rounded-lg">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Plant</TableHead>
                        <TableHead>Scientific Name</TableHead>
                        <TableHead>Category</TableHead>
                        <TableHead>Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {selectedProject.plants.map((plant) => (
                        <TableRow key={plant.id}>
                          <TableCell className="font-medium">{plant.common_name}</TableCell>
                          <TableCell className="italic">{plant.scientific_name}</TableCell>
                          <TableCell>
                            <Badge variant="secondary">{plant.category}</Badge>
                          </TableCell>
                          <TableCell>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleRemovePlantFromProject(plant.id)}
                            >
                              <Trash2 className="h-3 w-3" />
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              ) : (
                <p className="text-gray-500 text-center py-4">No plants added to this project yet</p>
              )}
            </div>

            <div>
              <h4 className="font-medium mb-2">Available Plants</h4>
              <div className="border rounded-lg max-h-64 overflow-y-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Plant</TableHead>
                      <TableHead>Scientific Name</TableHead>
                      <TableHead>Category</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {plants
                      .filter(plant => !selectedProject?.plants?.some(p => p.id === plant.id))
                      .map((plant) => (
                        <TableRow key={plant.id}>
                          <TableCell className="font-medium">{plant.common_name}</TableCell>
                          <TableCell className="italic">{plant.scientific_name}</TableCell>
                          <TableCell>
                            <Badge variant="secondary">{plant.category}</Badge>
                          </TableCell>
                          <TableCell>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleAddPlantToProject(plant.id)}
                            >
                              <Plus className="h-3 w-3" />
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                  </TableBody>
                </Table>
              </div>
            </div>
          </div>
          
          <DialogFooter>
            <Button onClick={() => setShowPlantsDialog(false)}>Close</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Products Dialog */}
      <Dialog open={showProductsDialog} onOpenChange={setShowProductsDialog}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Project Products - {selectedProject?.name}</DialogTitle>
            <DialogDescription>
              Manage products for this project
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div>
              <h4 className="font-medium mb-2">Current Products ({selectedProject?.products?.length || 0})</h4>
              {selectedProject?.products?.length > 0 ? (
                <div className="border rounded-lg">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Product</TableHead>
                        <TableHead>Category</TableHead>
                        <TableHead>Price</TableHead>
                        <TableHead>Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {selectedProject.products.map((product) => (
                        <TableRow key={product.id}>
                          <TableCell className="font-medium">{product.name}</TableCell>
                          <TableCell>
                            <Badge variant="secondary">{product.category}</Badge>
                          </TableCell>
                          <TableCell>
                            {product.price ? `€${product.price.toFixed(2)}` : '-'}
                          </TableCell>
                          <TableCell>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleRemoveProductFromProject(product.id)}
                            >
                              <Trash2 className="h-3 w-3" />
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              ) : (
                <p className="text-gray-500 text-center py-4">No products added to this project yet</p>
              )}
            </div>

            <div>
              <h4 className="font-medium mb-2">Available Products</h4>
              <div className="border rounded-lg max-h-64 overflow-y-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Product</TableHead>
                      <TableHead>Category</TableHead>
                      <TableHead>Price</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {products
                      .filter(product => !selectedProject?.products?.some(p => p.id === product.id))
                      .map((product) => (
                        <TableRow key={product.id}>
                          <TableCell className="font-medium">{product.name}</TableCell>
                          <TableCell>
                            <Badge variant="secondary">{product.category}</Badge>
                          </TableCell>
                          <TableCell>
                            {product.price ? `€${product.price.toFixed(2)}` : '-'}
                          </TableCell>
                          <TableCell>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleAddProductToProject(product.id)}
                            >
                              <Plus className="h-3 w-3" />
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                  </TableBody>
                </Table>
              </div>
            </div>
          </div>
          
          <DialogFooter>
            <Button onClick={() => setShowProductsDialog(false)}>Close</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Projects;

