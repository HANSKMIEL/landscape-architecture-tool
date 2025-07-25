import { useState, useEffect, useCallback } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { 
  Search, 
  Plus, 
  Building2, 
  Phone, 
  Mail, 
  MapPin,
  Trash2,
  Edit
} from 'lucide-react'
import { toast } from 'sonner'
import apiService from '../services/api'

const Suppliers = ({ language }) => {
  const [suppliers, setSuppliers] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [totalSuppliers, setTotalSuppliers] = useState(0)

  const translations = {
    en: {
      title: 'Suppliers',
      subtitle: 'Manage your landscape architecture suppliers',
      search: 'Search suppliers...',
      addSupplier: 'Add Supplier',
      name: 'Name',
      contact: 'Contact Person',
      email: 'Email',
      phone: 'Phone',
      location: 'Location',
      products: 'Products',
      actions: 'Actions',
      edit: 'Edit',
      delete: 'Delete',
      loading: 'Loading suppliers...',
      noSuppliers: 'No suppliers found',
      error: 'Error loading suppliers',
      deleteConfirm: 'Are you sure you want to delete this supplier?',
      deleteSuccess: 'Supplier deleted successfully',
      deleteError: 'Error deleting supplier'
    },
    nl: {
      title: 'Leveranciers',
      subtitle: 'Beheer uw landschapsarchitectuur leveranciers',
      search: 'Zoek leveranciers...',
      addSupplier: 'Leverancier Toevoegen',
      name: 'Naam',
      contact: 'Contactpersoon',
      email: 'E-mail',
      phone: 'Telefoon',
      location: 'Locatie',
      products: 'Producten',
      actions: 'Acties',
      edit: 'Bewerken',
      delete: 'Verwijderen',
      loading: 'Leveranciers laden...',
      noSuppliers: 'Geen leveranciers gevonden',
      error: 'Fout bij laden van leveranciers',
      deleteConfirm: 'Weet u zeker dat u deze leverancier wilt verwijderen?',
      deleteSuccess: 'Leverancier succesvol verwijderd',
      deleteError: 'Fout bij verwijderen van leverancier'
    }
  }

  const t = translations[language]

  useEffect(() => {
    loadSuppliers()
  }, [loadSuppliers])

  const loadSuppliers = useCallback(async () => {
    try {
      setLoading(true)
      const params = searchTerm ? { search: searchTerm } : {}
      const data = await apiService.getSuppliers(params)
      setSuppliers(data.suppliers || [])
      setTotalSuppliers(data.total || 0)
    } catch (error) {
      console.error('Error loading suppliers:', error)
      toast.error(`${t.error}: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }, [searchTerm, t])

  const handleDeleteSupplier = async (supplierId) => {
    if (!confirm(`${t.deleteConfirm}`)) return

    try {
      await apiService.deleteSupplier(supplierId)
      toast.success(t.deleteSuccess)
      loadSuppliers() // Reload the list
    } catch (error) {
      console.error('Error deleting supplier:', error)
      toast.error(`${t.deleteError}: ${error.message}`)
    }
  }

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value)
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t.title}</h1>
          <p className="text-gray-600">{t.subtitle}</p>
        </div>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600 mx-auto"></div>
            <p className="mt-2 text-gray-500">{t.loading}</p>
          </div>
        </div>
      </div>
    )
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
          <span>{t.addSupplier}</span>
        </Button>
      </div>

      {/* Search */}
      <Card>
        <CardContent className="p-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <Input
              placeholder={t.search}
              value={searchTerm}
              onChange={handleSearchChange}
              className="pl-10"
            />
          </div>
        </CardContent>
      </Card>

      {/* Suppliers List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>{t.title} ({totalSuppliers})</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {suppliers.length > 0 ? (
            <div className="space-y-4">
              {suppliers.map((supplier) => (
                <div key={supplier.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-4">
                      <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                        <Building2 className="h-6 w-6 text-green-600" />
                      </div>
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900">{supplier.name}</h3>
                        {supplier.contact_person && (
                          <p className="text-sm text-gray-600">{supplier.contact_person}</p>
                        )}
                        
                        <div className="mt-2 space-y-1">
                          {supplier.email && (
                            <div className="flex items-center space-x-2 text-sm text-gray-500">
                              <Mail className="h-4 w-4" />
                              <span>{supplier.email}</span>
                            </div>
                          )}
                          {supplier.phone && (
                            <div className="flex items-center space-x-2 text-sm text-gray-500">
                              <Phone className="h-4 w-4" />
                              <span>{supplier.phone}</span>
                            </div>
                          )}
                          {(supplier.city || supplier.address) && (
                            <div className="flex items-center space-x-2 text-sm text-gray-500">
                              <MapPin className="h-4 w-4" />
                              <span>{supplier.city ? `${supplier.city}${supplier.address ? ', ' + supplier.address : ''}` : supplier.address}</span>
                            </div>
                          )}
                        </div>

                        <div className="mt-3 flex items-center space-x-4">
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            {supplier.product_count || 0} {t.products}
                          </span>
                          {supplier.website && (
                            <a 
                              href={supplier.website} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="text-sm text-blue-600 hover:text-blue-800"
                            >
                              Website
                            </a>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-2">
                      <Button variant="outline" size="sm" className="flex items-center space-x-1">
                        <Edit className="h-4 w-4" />
                        <span>{t.edit}</span>
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className="flex items-center space-x-1 text-red-600 hover:text-red-700"
                        onClick={() => handleDeleteSupplier(supplier.id, supplier.name)}
                      >
                        <Trash2 className="h-4 w-4" />
                        <span>{t.delete}</span>
                      </Button>
                    </div>
                  </div>

                  {supplier.notes && (
                    <div className="mt-3 pt-3 border-t">
                      <p className="text-sm text-gray-600">{supplier.notes}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Building2 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">{t.noSuppliers}</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default Suppliers

