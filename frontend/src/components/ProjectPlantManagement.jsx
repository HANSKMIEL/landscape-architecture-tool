import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { 
  Plus, 
  Trash2, 
  Edit3, 
  DollarSign, 
  ShoppingCart, 
  Download,
  Search,
  Loader2
} from 'lucide-react';

const ProjectPlantManagement = ({ projectId, language = 'en' }) => {
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

  const translations = {
    en: {
      title: 'Project Plants',
      subtitle: 'Manage plants for this project',
      addPlant: 'Add Plant',
      plantName: 'Plant Name',
      quantity: 'Quantity',
      unitCost: 'Unit Cost',
      totalCost: 'Total Cost',
      status: 'Status',
      actions: 'Actions',
      notes: 'Notes',
      search: 'Search plants...',
      costAnalysis: 'Cost Analysis',
      totalProjectCost: 'Total Project Cost',
      plantsWithCost: 'Plants with Cost',
      plantsWithoutCost: 'Plants without Cost',
      generateOrderList: 'Generate Order List',
      exportData: 'Export Data',
      remove: 'Remove',
      edit: 'Edit',
      save: 'Save',
      cancel: 'Cancel',
      loading: 'Loading...',
      noPlants: 'No plants added to this project yet',
      addFirstPlant: 'Add your first plant to get started',
      planned: 'Planned',
      ordered: 'Ordered',
      planted: 'Planted',
      completed: 'Completed'
    },
    nl: {
      title: 'Project Planten',
      subtitle: 'Beheer planten voor dit project',
      addPlant: 'Plant Toevoegen',
      plantName: 'Plant Naam',
      quantity: 'Aantal',
      unitCost: 'Stukprijs',
      totalCost: 'Totale Kosten',
      status: 'Status',
      actions: 'Acties',
      notes: 'Notities',
      search: 'Zoek planten...',
      costAnalysis: 'Kostenanalyse',
      totalProjectCost: 'Totale Project Kosten',
      plantsWithCost: 'Planten met Kosten',
      plantsWithoutCost: 'Planten zonder Kosten',
      generateOrderList: 'Bestellijst Genereren',
      exportData: 'Data Exporteren',
      remove: 'Verwijderen',
      edit: 'Bewerken',
      save: 'Opslaan',
      cancel: 'Annuleren',
      loading: 'Laden...',
      noPlants: 'Nog geen planten toegevoegd aan dit project',
      addFirstPlant: 'Voeg je eerste plant toe om te beginnen',
      planned: 'Gepland',
      ordered: 'Besteld',
      planted: 'Geplant',
      completed: 'Voltooid'
    }
  };

  const t = translations[language] || translations.en;

  // Fetch project plants
  const fetchProjectPlants = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`http://127.0.0.1:5001/api/projects/${projectId}/plants`);
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
      const response = await fetch('http://127.0.0.1:5001/api/plants');
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
      const response = await fetch(`http://127.0.0.1:5001/api/projects/${projectId}/cost-analysis`);
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
      
      const response = await fetch(`http://127.0.0.1:5001/api/projects/${projectId}/plants`, {
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
    if (!confirm('Are you sure you want to remove this plant from the project?')) {
      return;
    }

    try {
      setLoading(true);
      
      const response = await fetch(`http://127.0.0.1:5001/api/projects/${projectId}/plants/${plantId}`, {
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
      const response = await fetch(`http://127.0.0.1:5001/api/projects/${projectId}/plants/${plantId}`, {
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
      const response = await fetch(`http://127.0.0.1:5001/api/projects/${projectId}/plant-order-list`);
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

  // Get status badge variant
  const getStatusVariant = (status) => {
    switch (status) {
      case 'planned': return 'secondary';
      case 'ordered': return 'warning';
      case 'planted': return 'info';
      case 'completed': return 'success';
      default: return 'secondary';
    }
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
  }, [projectId]);

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
      <h3 className="text-lg font-semibold text-red-800 mb-2">Error Loading Data</h3>
      <p className="text-red-600 mb-4">{error}</p>
      <Button onClick={fetchProjectPlants} variant="destructive">
        Try Again
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
          <h1 className="text-2xl font-bold text-gray-900">{t.title}</h1>
          <p className="text-gray-600">{t.subtitle}</p>
        </div>
        <div className="flex space-x-2">
          <Button onClick={() => setShowAddModal(true)} className="flex items-center space-x-2">
            <Plus className="h-4 w-4" />
            <span>{t.addPlant}</span>
          </Button>
          <Button onClick={generateOrderList} variant="outline" className="flex items-center space-x-2">
            <Download className="h-4 w-4" />
            <span>{t.generateOrderList}</span>
          </Button>
        </div>
      </div>

      {/* Cost Analysis Card */}
      {costAnalysis && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <DollarSign className="h-5 w-5" />
              <span>{t.costAnalysis}</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {formatCurrency(costAnalysis.total_cost)}
                </div>
                <div className="text-sm text-gray-600">{t.totalProjectCost}</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {costAnalysis.total_plants}
                </div>
                <div className="text-sm text-gray-600">Total Plants</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {costAnalysis.plants_with_cost}
                </div>
                <div className="text-sm text-gray-600">{t.plantsWithCost}</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {costAnalysis.plants_without_cost}
                </div>
                <div className="text-sm text-gray-600">{t.plantsWithoutCost}</div>
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
              <h3 className="text-lg font-semibold text-gray-900 mb-2">{t.noPlants}</h3>
              <p className="text-gray-600 mb-6">{t.addFirstPlant}</p>
              <Button onClick={() => setShowAddModal(true)}>
                {t.addPlant}
              </Button>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>{t.plantName}</TableHead>
                  <TableHead>{t.quantity}</TableHead>
                  <TableHead>{t.unitCost}</TableHead>
                  <TableHead>{t.totalCost}</TableHead>
                  <TableHead>{t.status}</TableHead>
                  <TableHead>{t.actions}</TableHead>
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
                        <option value="planned">{t.planned}</option>
                        <option value="ordered">{t.ordered}</option>
                        <option value="planted">{t.planted}</option>
                        <option value="completed">{t.completed}</option>
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
              <h2 className="text-xl font-semibold text-gray-900">{t.addPlant}</h2>
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
                  {t.search}
                </label>
                <Input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder={t.search}
                />
              </div>

              {/* Select Plant */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Plant
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
                  {t.quantity}
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
                  {t.unitCost}
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
                  {t.notes}
                </label>
                <Input
                  type="text"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Optional notes..."
                />
              </div>
            </div>

            <div className="flex items-center justify-end space-x-2 p-6 border-t">
              <Button onClick={() => setShowAddModal(false)} variant="outline">
                {t.cancel}
              </Button>
              <Button onClick={addPlantToProject} disabled={!selectedPlant || loading}>
                {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                {t.save}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProjectPlantManagement;