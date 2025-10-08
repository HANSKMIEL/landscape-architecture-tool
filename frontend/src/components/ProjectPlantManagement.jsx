import { useLanguage } from "../i18n/LanguageProvider";
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import {
  Plus,
  Trash2,
  DollarSign,
  ShoppingCart,
  Download,
  Loader2
} from 'lucide-react';

const translationDefaults = {
  title: 'Project Plants',
  subtitle: 'Manage plants for this project',
  addPlant: 'Add Plant',
  generateOrderList: 'Generate Order List',
  costAnalysis: 'Cost Analysis',
  totalProjectCost: 'Total Project Cost',
  totalPlantsLabel: 'Total Plants',
  plantsWithCost: 'Plants with Cost',
  plantsWithoutCost: 'Plants without Cost',
  noPlants: 'No plants added to this project yet',
  addFirstPlant: 'Add your first plant to get started',
  plantName: 'Plant Name',
  quantity: 'Quantity',
  unitCost: 'Unit Cost',
  totalCost: 'Total Cost',
  status: 'Status',
  actions: 'Actions',
  planned: 'Planned',
  ordered: 'Ordered',
  planted: 'Planted',
  completed: 'Completed',
  search: 'Search plants...',
  notes: 'Notes',
  cancel: 'Cancel',
  save: 'Save',
  selectPlant: 'Select Plant',
  notesPlaceholder: 'Optional notes...',
  removeConfirmation: 'Are you sure you want to remove this plant from the project?',
  errorLoading: 'Error Loading Data',
  tryAgain: 'Try Again'
};

const ProjectPlantManagement = ({ projectId }) => {
  const [projectPlants, setProjectPlants] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [availablePlants, setAvailablePlants] = useState([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [costAnalysis, setCostAnalysis] = useState(null);
  const [selectedPlant, setSelectedPlant] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [unitCost, setUnitCost] = useState('');
  const [notes, setNotes] = useState('');

  const { t } = useLanguage();
  const translate = (key) => t(`projectPlantManagement.${key}`, translationDefaults[key] ?? key);

  // Fetch project plants
  const fetchProjectPlants = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`/api/projects/${projectId}/plants`);
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      const data = await response.json();
      setProjectPlants(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Fetch available plants for adding
  const fetchAvailablePlants = async () => {
    try {
      const response = await fetch('/api/plants');
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      const data = await response.json();
      setAvailablePlants(data);
    } catch (err) {
      console.error('Error fetching plants:', err);
    }
  };

  // Fetch cost analysis
  const fetchCostAnalysis = async () => {
    try {
      const response = await fetch(`/api/projects/${projectId}/cost-analysis`);
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      const data = await response.json();
      setCostAnalysis(data);
    } catch (err) {
      console.error('Error fetching cost analysis:', err);
    }
  };

  // Add plant to project
  const addPlantToProject = async () => {
    if (!selectedPlant) return;

    try {
      setLoading(true);
      
      const response = await fetch(`/api/projects/${projectId}/plants`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          plant_id: selectedPlant.id,
          quantity: quantity,
          unit_cost: unitCost ? parseFloat(unitCost) : null,
          notes: notes || null
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      // Reset form and refresh data
      setSelectedPlant(null);
      setQuantity(1);
      setUnitCost('');
      setNotes('');
      setShowAddModal(false);
      
      await fetchProjectPlants();
      await fetchCostAnalysis();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Remove plant from project
  const removePlantFromProject = async (plantId) => {
    if (!confirm(translate('removeConfirmation'))) {
      return;
    }

    try {
      setLoading(true);
      
      const response = await fetch(`/api/projects/${projectId}/plants/${plantId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      await fetchProjectPlants();
      await fetchCostAnalysis();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Update plant status
  const updatePlantStatus = async (plantId, newStatus) => {
    try {
      const response = await fetch(`/api/projects/${projectId}/plants/${plantId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          status: newStatus
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      await fetchProjectPlants();
    } catch (err) {
      setError(err.message);
    }
  };

  // Generate order list
  const generateOrderList = async () => {
    try {
      const response = await fetch(`/api/projects/${projectId}/plant-order-list`);
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Create and download CSV
      const csvContent = generateCSVContent(data);
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', `project-${projectId}-plant-order-list.csv`);
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      setError(err.message);
    }
  };

  // Generate CSV content for order list
  const generateCSVContent = (orderData) => {
    let csv = 'Supplier,Plant Name,Common Name,Quantity,Unit Cost,Total Cost,Status,Notes\n';
    
    orderData.forEach(supplier => {
      supplier.plants.forEach(plant => {
        csv += `"${supplier.supplier_name}","${plant.plant_name}","${plant.common_name || ''}",${plant.quantity},${plant.unit_cost || 0},${plant.total_cost || 0},"${plant.status}","${plant.notes || ''}"\n`;
      });
    });
    
    return csv;
  };

  // Format currency
  const formatCurrency = (amount) => {
    if (!amount) return '€0.00';
    return new Intl.NumberFormat('nl-NL', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 2
    }).format(amount);
  };

  // Filter available plants based on search
  const filteredPlants = availablePlants.filter(plant =>
    plant.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (plant.common_name && plant.common_name.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  useEffect(() => {
    if (projectId) {
      fetchProjectPlants();
      fetchCostAnalysis();
      fetchAvailablePlants();
    }
  }, [projectId]); // eslint-disable-line react-hooks/exhaustive-deps

  // Loading component
  const LoadingSpinner = () => (
    <div className="flex justify-center items-center py-12">
      <Loader2 className="h-8 w-8 animate-spin text-green-600" />
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
  <h3 className="text-lg font-semibold text-red-800 mb-2">{translate('errorLoading')}</h3>
      <p className="text-red-600 mb-4">{error}</p>
      <Button onClick={fetchProjectPlants} variant="destructive">
        {translate('tryAgain')}
      </Button>
    </div>
  );

  if (error) {
    return <ErrorDisplay />;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{translate('title')}</h1>
          <p className="text-gray-600">{translate('subtitle')}</p>
        </div>
        <div className="flex space-x-2">
          <Button onClick={() => setShowAddModal(true)} className="flex items-center space-x-2">
            <Plus className="h-4 w-4" />
            <span>{translate('addPlant')}</span>
          </Button>
          <Button onClick={generateOrderList} variant="outline" className="flex items-center space-x-2">
            <Download className="h-4 w-4" />
            <span>{translate('generateOrderList')}</span>
          </Button>
        </div>
      </div>

      {/* Cost Analysis Card */}
      {costAnalysis && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <DollarSign className="h-5 w-5" />
              <span>{translate('costAnalysis')}</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {formatCurrency(costAnalysis.total_cost)}
                </div>
                <div className="text-sm text-gray-600">{translate('totalProjectCost')}</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {costAnalysis.total_plants}
                </div>
                <div className="text-sm text-gray-600">{translate('totalPlantsLabel')}</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {costAnalysis.plants_with_cost}
                </div>
                <div className="text-sm text-gray-600">{translate('plantsWithCost')}</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {costAnalysis.plants_without_cost}
                </div>
                <div className="text-sm text-gray-600">{translate('plantsWithoutCost')}</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Plants Table */}
      <Card>
        <CardContent>
          {loading ? (
            <LoadingSpinner />
          ) : projectPlants.length === 0 ? (
            <div className="text-center py-12">
              <div className="w-24 h-24 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
                <ShoppingCart className="w-12 h-12 text-gray-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">{translate('noPlants')}</h3>
              <p className="text-gray-600 mb-6">{translate('addFirstPlant')}</p>
              <Button onClick={() => setShowAddModal(true)}>
                {translate('addPlant')}
              </Button>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>{translate('plantName')}</TableHead>
                  <TableHead>{translate('quantity')}</TableHead>
                  <TableHead>{translate('unitCost')}</TableHead>
                  <TableHead>{translate('totalCost')}</TableHead>
                  <TableHead>{translate('status')}</TableHead>
                  <TableHead>{translate('actions')}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {projectPlants.map((projectPlant) => (
                  <TableRow key={projectPlant.id}>
                    <TableCell>
                      <div>
                        <div className="font-medium">{projectPlant.plant?.name}</div>
                        <div className="text-sm text-gray-600">{projectPlant.plant?.common_name}</div>
                      </div>
                    </TableCell>
                    <TableCell>{projectPlant.quantity}</TableCell>
                    <TableCell>{formatCurrency(projectPlant.unit_cost)}</TableCell>
                    <TableCell>{formatCurrency(projectPlant.total_cost)}</TableCell>
                    <TableCell>
                      <select
                        value={projectPlant.status}
                        onChange={(e) => updatePlantStatus(projectPlant.plant_id, e.target.value)}
                        className="text-xs rounded px-2 py-1 border"
                      >
                        <option value="planned">{translate('planned')}</option>
                        <option value="ordered">{translate('ordered')}</option>
                        <option value="planted">{translate('planted')}</option>
                        <option value="completed">{translate('completed')}</option>
                      </select>
                    </TableCell>
                    <TableCell>
                      <Button
                        onClick={() => removePlantFromProject(projectPlant.plant_id)}
                        variant="destructive"
                        size="sm"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Add Plant Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b">
              <h2 className="text-xl font-semibold text-gray-900">{translate('addPlant')}</h2>
              <button
                onClick={() => setShowAddModal(false)}
                className="text-gray-400 hover:text-gray-600 transition-colors duration-200"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="p-6 space-y-4">
              {/* Search Plants */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {translate('search')}
                </label>
                <Input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder={translate('search')}
                />
              </div>

              {/* Select Plant */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {translate('selectPlant')}
                </label>
                <div className="max-h-40 overflow-y-auto border rounded-md">
                  {filteredPlants.map((plant) => (
                    <div
                      key={plant.id}
                      onClick={() => {
                        setSelectedPlant(plant);
                        setUnitCost(plant.price?.toString() || '');
                      }}
                      className={`p-3 cursor-pointer hover:bg-gray-50 border-b ${
                        selectedPlant?.id === plant.id ? 'bg-blue-50 border-blue-200' : ''
                      }`}
                    >
                      <div className="font-medium">{plant.name}</div>
                      <div className="text-sm text-gray-600">{plant.common_name}</div>
                      <div className="text-sm text-green-600">{formatCurrency(plant.price)}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Quantity */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {translate('quantity')}
                </label>
                <Input
                  type="number"
                  value={quantity}
                  onChange={(e) => setQuantity(parseInt(e.target.value) || 1)}
                  min="1"
                />
              </div>

              {/* Unit Cost */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {translate('unitCost')}
                </label>
                <Input
                  type="number"
                  value={unitCost}
                  onChange={(e) => setUnitCost(e.target.value)}
                  step="0.01"
                  min="0"
                />
              </div>

              {/* Notes */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {translate('notes')}
                </label>
                <Input
                  type="text"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder={translate('notesPlaceholder')}
                />
              </div>
            </div>

            <div className="flex items-center justify-end space-x-2 p-6 border-t">
              <Button onClick={() => setShowAddModal(false)} variant="outline">
                {translate('cancel')}
              </Button>
              <Button onClick={addPlantToProject} disabled={!selectedPlant || loading}>
                {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                {translate('save')}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProjectPlantManagement;