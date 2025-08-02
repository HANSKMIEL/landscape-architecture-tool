import React, { useState, useEffect, useCallback } from 'react';
import ApiService from '../services/api';

const Plants = () => {
  const [plants, setPlants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingPlant, setEditingPlant] = useState(null);
  const [suppliers, setSuppliers] = useState([]);

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
  });

  // Fetch plants data
  const fetchPlants = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = {};
      if (searchTerm) {
        params.search = searchTerm;
      }
      
      const data = await ApiService.getPlants(params);
      // API returns { plants: [...], total: X, ... } format
      setPlants(data.plants || []);
    } catch (err) {
      console.error('Error fetching plants:', err.message);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [searchTerm]);

  // Fetch suppliers for dropdown
  const fetchSuppliers = async () => {
    try {
      const data = await ApiService.getSuppliers();
      // API returns { suppliers: [...] } format
      setSuppliers(data.suppliers || []);
    } catch (err) {
      console.error('Error fetching suppliers:', err);
    }
  };

  useEffect(() => {
    fetchPlants();
    fetchSuppliers();
  }, [fetchPlants]);

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

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
    });
  };

  // Handle add plant
  const handleAddPlant = async (e) => {
    e.preventDefault();
    try {
      await ApiService.createPlant(formData);
      await fetchPlants();
      setShowAddModal(false);
      resetForm();
      alert('Plant succesvol toegevoegd!');
    } catch (err) {
      console.error('Error adding plant:', err);
      alert(`Fout bij toevoegen plant: ${err.message}`);
    }
  };

  // Handle edit plant
  const handleEditPlant = async (e) => {
    e.preventDefault();
    try {
      await ApiService.updatePlant(editingPlant.id, formData);
      await fetchPlants();
      setShowEditModal(false);
      setEditingPlant(null);
      resetForm();
      alert('Plant succesvol bijgewerkt!');
    } catch (err) {
      console.error('Error updating plant:', err);
      alert(`Fout bij bijwerken plant: ${err.message}`);
    }
  };

  // Handle delete plant
  const handleDeletePlant = async (plantId, plantName) => {
    if (!confirm(`Weet je zeker dat je "${plantName}" wilt verwijderen?`)) {
      return;
    }

    try {
      await ApiService.deletePlant(plantId);
      await fetchPlants();
      alert('Plant succesvol verwijderd!');
    } catch (err) {
      console.error('Error deleting plant:', err);
      alert(`Fout bij verwijderen plant: ${err.message}`);
    }
  };

  // Open edit modal
  const openEditModal = (plant) => {
    setEditingPlant(plant);
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
    });
    setShowEditModal(true);
  };

  // Get supplier name by ID
  const getSupplierName = (supplierId) => {
    const supplier = Array.isArray(suppliers) ? suppliers.find(s => s.id === supplierId) : null;
    return supplier ? supplier.name : 'Onbekend';
  };

  // Format currency
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('nl-NL', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 2
    }).format(amount);
  };

  // Loading component
  const LoadingSpinner = () => (
    <div className="flex justify-center items-center py-12">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-landscape-primary"></div>
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
      <h3 className="text-lg font-semibold text-red-800 mb-2">Fout bij laden van planten</h3>
      <p className="text-red-600 mb-4">{error}</p>
      <button
        onClick={fetchPlants}
        className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200"
      >
        Opnieuw proberen
      </button>
    </div>
  );

  // Empty state component
  const EmptyState = () => (
    <div className="text-center py-12">
      <div className="w-24 h-24 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
        <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
        </svg>
      </div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">
        {searchTerm ? 'Geen planten gevonden' : 'Nog geen planten toegevoegd'}
      </h3>
      <p className="text-gray-600 mb-6">
        {searchTerm 
          ? `Geen resultaten voor "${searchTerm}". Probeer een andere zoekterm.`
          : 'Voeg je eerste plant toe om te beginnen met je plantendatabase.'
        }
      </p>
      {!searchTerm && (
        <button
          onClick={() => setShowAddModal(true)}
          className="bg-landscape-primary hover:bg-landscape-primary-dark text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200"
        >
          Eerste plant toevoegen
        </button>
      )}
    </div>
  );

  // Modal component
  const Modal = ({ isOpen, onClose, title, children }) => {
    if (!isOpen) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
          <div className="flex items-center justify-between p-6 border-b">
            <h2 className="text-xl font-semibold text-gray-900">{title}</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors duration-200"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div className="p-6">
            {children}
          </div>
        </div>
      </div>
    );
  };

  // Plant form component
  const PlantForm = ({ onSubmit, submitText }) => (
    <form onSubmit={onSubmit} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Wetenschappelijke naam *
          </label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleInputChange}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-landscape-primary focus:border-transparent"
            placeholder="bijv. Acer platanoides"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Nederlandse naam *
          </label>
          <input
            type="text"
            name="common_name"
            value={formData.common_name}
            onChange={handleInputChange}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-landscape-primary focus:border-transparent"
            placeholder="bijv. Noorse esdoorn"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Categorie *
          </label>
          <select
            name="category"
            value={formData.category}
            onChange={handleInputChange}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-landscape-primary focus:border-transparent"
          >
            <option value="">Selecteer categorie</option>
            <option value="Boom">Boom</option>
            <option value="Heester">Heester</option>
            <option value="Vaste plant">Vaste plant</option>
            <option value="Eenjarige">Eenjarige</option>
            <option value="Bol- en knolgewas">Bol- en knolgewas</option>
            <option value="Gras">Gras</option>
            <option value="Varen">Varen</option>
            <option value="Klimplant">Klimplant</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Leverancier
          </label>
          <select
            name="supplier_id"
            value={formData.supplier_id}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-landscape-primary focus:border-transparent"
          >
            <option value="">Selecteer leverancier</option>
            {Array.isArray(suppliers) ? suppliers.map(supplier => (
              <option key={supplier.id} value={supplier.id}>
                {supplier.name}
              </option>
            )) : null}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Min. hoogte (m)
          </label>
          <input
            type="number"
            name="height_min"
            value={formData.height_min}
            onChange={handleInputChange}
            step="0.1"
            min="0"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-landscape-primary focus:border-transparent"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Max. hoogte (m)
          </label>
          <input
            type="number"
            name="height_max"
            value={formData.height_max}
            onChange={handleInputChange}
            step="0.1"
            min="0"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-landscape-primary focus:border-transparent"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Min. breedte (m)
          </label>
          <input
            type="number"
            name="width_min"
            value={formData.width_min}
            onChange={handleInputChange}
            step="0.1"
            min="0"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-landscape-primary focus:border-transparent"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Max. breedte (m)
          </label>
          <input
            type="number"
            name="width_max"
            value={formData.width_max}
            onChange={handleInputChange}
            step="0.1"
            min="0"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-landscape-primary focus:border-transparent"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Zonbehoefte
          </label>
          <select
            name="sun_requirements"
            value={formData.sun_requirements}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-landscape-primary focus:border-transparent"
          >
            <option value="">Selecteer zonbehoefte</option>
            <option value="Volle zon">Volle zon</option>
            <option value="Zon tot halfschaduw">Zon tot halfschaduw</option>
            <option value="Halfschaduw">Halfschaduw</option>
            <option value="Halfschaduw tot schaduw">Halfschaduw tot schaduw</option>
            <option value="Schaduw">Schaduw</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Waterbehoefte
          </label>
          <select
            name="water_needs"
            value={formData.water_needs}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-landscape-primary focus:border-transparent"
          >
            <option value="">Selecteer waterbehoefte</option>
            <option value="Droog">Droog</option>
            <option value="Droog tot matig">Droog tot matig</option>
            <option value="Matig">Matig</option>
            <option value="Matig tot vochtig">Matig tot vochtig</option>
            <option value="Vochtig">Vochtig</option>
            <option value="Nat">Nat</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Onderhoud
          </label>
          <select
            name="maintenance"
            value={formData.maintenance}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-landscape-primary focus:border-transparent"
          >
            <option value="">Selecteer onderhoudsniveau</option>
            <option value="Laag">Laag</option>
            <option value="Matig">Matig</option>
            <option value="Hoog">Hoog</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Grondtype
          </label>
          <input
            type="text"
            name="soil_type"
            value={formData.soil_type}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-landscape-primary focus:border-transparent"
            placeholder="bijv. Alle grondsoorten"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Hardheidszone
          </label>
          <input
            type="text"
            name="hardiness_zone"
            value={formData.hardiness_zone}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-landscape-primary focus:border-transparent"
            placeholder="bijv. 4-7"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Bloeitijd
          </label>
          <input
            type="text"
            name="bloom_time"
            value={formData.bloom_time}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-landscape-primary focus:border-transparent"
            placeholder="bijv. April-Mei"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Bloeikleur
          </label>
          <input
            type="text"
            name="bloom_color"
            value={formData.bloom_color}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-landscape-primary focus:border-transparent"
            placeholder="bijv. Wit, roze"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Bladkleur
          </label>
          <input
            type="text"
            name="foliage_color"
            value={formData.foliage_color}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-landscape-primary focus:border-transparent"
            placeholder="bijv. Groen, geel in herfst"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Prijs (€)
          </label>
          <input
            type="number"
            name="price"
            value={formData.price}
            onChange={handleInputChange}
            step="0.01"
            min="0"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-landscape-primary focus:border-transparent"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Beschikbaarheid
          </label>
          <select
            name="availability"
            value={formData.availability}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-landscape-primary focus:border-transparent"
          >
            <option value="">Selecteer beschikbaarheid</option>
            <option value="Voorradig">Voorradig</option>
            <option value="Beperkt voorradig">Beperkt voorradig</option>
            <option value="Op bestelling">Op bestelling</option>
            <option value="Niet beschikbaar">Niet beschikbaar</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Plantseizoen
          </label>
          <select
            name="planting_season"
            value={formData.planting_season}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-landscape-primary focus:border-transparent"
          >
            <option value="">Selecteer plantseizoen</option>
            <option value="Voorjaar">Voorjaar</option>
            <option value="Zomer">Zomer</option>
            <option value="Herfst">Herfst</option>
            <option value="Winter">Winter</option>
            <option value="Herfst/Voorjaar">Herfst/Voorjaar</option>
            <option value="Jaar rond">Jaar rond</option>
          </select>
        </div>
      </div>

      <div>
        <label className="flex items-center space-x-2">
          <input
            type="checkbox"
            name="native"
            checked={formData.native}
            onChange={handleInputChange}
            className="rounded border-gray-300 text-landscape-primary focus:ring-landscape-primary"
          />
          <span className="text-sm font-medium text-gray-700">Inheemse plant</span>
        </label>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Opmerkingen
        </label>
        <textarea
          name="notes"
          value={formData.notes}
          onChange={handleInputChange}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-landscape-primary focus:border-transparent"
          placeholder="Aanvullende informatie over de plant..."
        />
      </div>

      <div className="flex justify-end space-x-4 pt-4">
        <button
          type="button"
          onClick={() => {
            setShowAddModal(false);
            setShowEditModal(false);
            resetForm();
          }}
          className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors duration-200"
        >
          Annuleren
        </button>
        <button
          type="submit"
          className="bg-landscape-primary hover:bg-landscape-primary-dark text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200"
        >
          {submitText}
        </button>
      </div>
    </form>
  );

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Planten</h1>
          <p className="text-gray-600 mt-2">Beheer uw plantendatabase</p>
        </div>

        {/* Search and Add */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
            <div className="flex-1 max-w-md">
              <div className="relative">
                <svg className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <input
                  type="text"
                  placeholder="Zoek planten..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-landscape-primary focus:border-transparent"
                />
              </div>
            </div>
            <button
              onClick={() => setShowAddModal(true)}
              className="bg-landscape-primary hover:bg-landscape-primary-dark text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 flex items-center space-x-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              <span>Plant toevoegen</span>
            </button>
          </div>
        </div>

        {/* Content */}
        {error ? (
          <ErrorDisplay />
        ) : loading ? (
          <LoadingSpinner />
        ) : !Array.isArray(plants) || plants.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm border">
            <EmptyState />
          </div>
        ) : (
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Plantenlijst</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {Array.isArray(plants) ? plants.map((plant) => (
                <div key={plant.id} className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow duration-200">
                  <div className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900 mb-1">
                          {plant.common_name}
                        </h3>
                      <p className="text-sm text-gray-600 italic mb-2">
                        {plant.name}
                      </p>
                      <div className="flex items-center space-x-2">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-landscape-primary/10 text-landscape-primary">
                          {plant.category}
                        </span>
                        {plant.native && (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            Inheems
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2 mb-4">
                    {plant.height_min && plant.height_max && (
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Hoogte:</span>
                        <span className="font-medium">{plant.height_min}m - {plant.height_max}m</span>
                      </div>
                    )}
                    {plant.sun_requirements && (
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Zon:</span>
                        <span className="font-medium">{plant.sun_requirements}</span>
                      </div>
                    )}
                    {plant.bloom_time && (
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Bloei:</span>
                        <span className="font-medium">{plant.bloom_time}</span>
                      </div>
                    )}
                    {plant.price && (
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Prijs:</span>
                        <span className="font-medium text-landscape-primary">
                          {formatCurrency(plant.price)}
                        </span>
                      </div>
                    )}
                    {plant.supplier_id && (
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Leverancier:</span>
                        <span className="font-medium">{getSupplierName(plant.supplier_id)}</span>
                      </div>
                    )}
                  </div>

                  <div className="flex items-center justify-between pt-4 border-t">
                    <div className="flex items-center space-x-2">
                      {plant.availability && (
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                          plant.availability === 'Voorradig' 
                            ? 'bg-green-100 text-green-800'
                            : plant.availability === 'Beperkt voorradig'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {plant.availability}
                        </span>
                      )}
                    </div>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => openEditModal(plant)}
                        className="text-landscape-primary hover:text-landscape-primary-dark transition-colors duration-200"
                        title="Bewerken"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                      </button>
                      <button
                        onClick={() => handleDeletePlant(plant.id, plant.common_name)}
                        className="text-red-600 hover:text-red-800 transition-colors duration-200"
                        title="Verwijderen"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )) : (
              <div className="col-span-full text-center py-8 text-gray-500">
                No plants data available
              </div>
            )}
            </div>
          </div>
        )}

        {/* Add Modal */}
        <Modal
          isOpen={showAddModal}
          onClose={() => {
            setShowAddModal(false);
            resetForm();
          }}
          title="Plant toevoegen"
        >
          <PlantForm onSubmit={handleAddPlant} submitText="Plant toevoegen" />
        </Modal>

        {/* Edit Modal */}
        <Modal
          isOpen={showEditModal}
          onClose={() => {
            setShowEditModal(false);
            setEditingPlant(null);
            resetForm();
          }}
          title="Plant bewerken"
        >
          <PlantForm onSubmit={handleEditPlant} submitText="Plant bijwerken" />
        </Modal>
      </div>
    </div>
  );
};

export default Plants;

