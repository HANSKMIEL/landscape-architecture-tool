import React, { useState, useEffect, useCallback } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import {
  Package,
  Plus,
  Upload,
  Edit,
  Trash2,
  Search,
  X,
  Loader2,
  DollarSign,
  Package2
} from 'lucide-react'
import ApiService from '../services/api'
import { useLanguage } from '../i18n/LanguageProvider'

const Products = () => {
  const { t } = useLanguage()
  // State management
  const [products, setProducts] = useState([])
  const [suppliers, setSuppliers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showAddModal, setShowAddModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [editingProduct, setEditingProduct] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [totalProducts, setTotalProducts] = useState(0)

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    price: '',
    category: '',
    supplier_id: '',
    stock_quantity: '',
    unit: '',
    sku: '',
    notes: ''
  })

  // Category options
  const categoryOptions = [
    { value: 'plants', label: t('products.categories.plants', 'Plants') },
    { value: 'tools', label: t('products.categories.tools', 'Tools') },
    { value: 'materials', label: t('products.categories.materials', 'Materials') },
    { value: 'fertilizers', label: t('products.categories.fertilizers', 'Fertilizers') },
    { value: 'irrigation', label: t('products.categories.irrigation', 'Irrigation') },
    { value: 'lighting', label: t('products.categories.lighting', 'Lighting') },
    { value: 'hardscape', label: t('products.categories.hardscape', 'Hardscape') },
    { value: 'other', label: t('products.categories.other', 'Other') }
  ]

  // Unit options
  const unitOptions = [
    { value: 'piece', label: t('products.units.piece', 'Piece') },
    { value: 'kg', label: t('products.units.kg', 'Kilogram') },
    { value: 'liter', label: t('products.units.liter', 'Liter') },
    { value: 'm2', label: t('products.units.m2', 'Square Meter') },
    { value: 'm3', label: t('products.units.m3', 'Cubic Meter') },
    { value: 'pack', label: t('products.units.pack', 'Pack') },
    { value: 'box', label: t('products.units.box', 'Box') }
  ]

  // Load products from API
  const loadProducts = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const params = searchTerm ? { search: searchTerm } : {}
      const data = await ApiService.getProducts(params)

      // Defensive programming: ensure products is always an array
      const productsArray = Array.isArray(data?.products) ? data.products :
        Array.isArray(data) ? data : []

      setProducts(productsArray)
      setTotalProducts(data?.total || data?.pagination?.total || productsArray.length)
    } catch (err) {
      console.error('Error loading products:', err)
      setError(err.message)
      // Set empty array on error to prevent map() failures
      setProducts([])
    } finally {
      setLoading(false)
    }
  }, [searchTerm])

  // Load suppliers for dropdown
  const loadSuppliers = async () => {
    try {
      const data = await ApiService.getSuppliers()
      setSuppliers(data.suppliers || [])
    } catch (err) {
      console.error('Error loading suppliers:', err)
    }
  }

  useEffect(() => {
    loadProducts()
    loadSuppliers()
  }, [loadProducts])

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
      description: '',
      price: '',
      category: '',
      supplier_id: '',
      stock_quantity: '',
      unit: '',
      sku: '',
      notes: ''
    })
  }

  // Handle add product
  const handleAddProduct = async (e) => {
    e.preventDefault()
    try {
      await ApiService.createProduct(formData)
      await loadProducts()
      setShowAddModal(false)
      resetForm()
      alert(t('products.addSuccess', 'Product successfully added!'))
    } catch (err) {
      console.error('Error adding product:', err)
      alert(t('products.addError', 'Error adding product: ') + err.message)
    }
  }

  // Handle edit product
  const handleEditProduct = async (e) => {
    e.preventDefault()
    try {
      await ApiService.updateProduct(editingProduct.id, formData)
      await loadProducts()
      setShowEditModal(false)
      setEditingProduct(null)
      resetForm()
      alert(t('products.updateSuccess', 'Product successfully updated!'))
    } catch (err) {
      console.error('Error updating product:', err)
      alert(t('products.updateError', 'Error updating product: ') + err.message)
    }
  }

  // Handle delete product
  const handleDeleteProduct = async (productId, productName) => {
    if (!confirm(t('products.deleteConfirm', 'Are you sure you want to delete "{name}"?').replace('{name}', productName))) {
      return
    }

    try {
      await ApiService.deleteProduct(productId)
      await loadProducts()
      alert(t('products.deleteSuccess', 'Product successfully deleted!'))
    } catch (err) {
      console.error('Error deleting product:', err)
      alert(t('products.deleteError', 'Error deleting product: ') + err.message)
    }
  }

  // Open edit modal
  const openEditModal = (product) => {
    setEditingProduct(product)
    setFormData({
      name: product.name || '',
      description: product.description || '',
      price: product.price || '',
      category: product.category || '',
      supplier_id: product.supplier_id || '',
      stock_quantity: product.stock_quantity || '',
      unit: product.unit || '',
      sku: product.sku || '',
      notes: product.notes || ''
    })
    setShowEditModal(true)
  }

  // Get supplier name by ID
  const getSupplierName = (supplierId) => {
    const supplier = suppliers.find(s => s.id === supplierId)
    return supplier ? supplier.name : t('common.unknown', 'Unknown')
  }

  // Get category label
  const getCategoryLabel = (category) => {
    const categoryOption = categoryOptions.find(c => c.value === category)
    return categoryOption ? categoryOption.label : category
  }

  // Format currency
  const formatCurrency = (amount) => {
    if (!amount) return '€0.00'
    return new Intl.NumberFormat('nl-NL', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 2
    }).format(amount)
  }

  // Get stock status badge
  const getStockBadge = (quantity) => {
    const qty = parseInt(quantity) || 0
    if (qty === 0) return { variant: 'destructive', label: t('products.outOfStock', 'Out of Stock') }
    if (qty < 10) return { variant: 'warning', label: t('products.lowStock', 'Low Stock') }
    return { variant: 'success', label: t('products.inStock', 'In Stock') }
  }

  // Product Form Component
  const ProductForm = ({ isEdit = false, onSubmit, onCancel }) => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">
            {isEdit ? t('products.editProduct', 'Edit Product') : t('products.addProduct', 'Add Product')}
          </h2>
          <Button variant="ghost" size="sm" onClick={onCancel}>
            <X className="h-4 w-4" />
          </Button>
        </div>

        <form onSubmit={onSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">
                {t('products.name', 'Product Name')} *
              </label>
              <Input
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required
                placeholder={t('products.namePlaceholder', 'Enter product name')}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                {t('products.sku', 'SKU')}
              </label>
              <Input
                name="sku"
                value={formData.sku}
                onChange={handleInputChange}
                placeholder={t('products.skuPlaceholder', 'Enter SKU code')}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              {t('products.description', 'Description')}
            </label>
            <Textarea
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              rows={3}
              placeholder={t('products.descriptionPlaceholder', 'Enter product description')}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">
                {t('products.category', 'Category')}
              </label>
              <select
                name="category"
                value={formData.category}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option value="">{t('products.selectCategory', 'Select a category')}</option>
                {categoryOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                {t('products.supplier', 'Supplier')}
              </label>
              <select
                name="supplier_id"
                value={formData.supplier_id}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option value="">{t('products.selectSupplier', 'Select a supplier')}</option>
                {suppliers.map(supplier => (
                  <option key={supplier.id} value={supplier.id}>
                    {supplier.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">
                {t('products.price', 'Price')} (€)
              </label>
              <Input
                name="price"
                type="number"
                value={formData.price}
                onChange={handleInputChange}
                placeholder="0.00"
                step="0.01"
                min="0"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                {t('products.stockQuantity', 'Stock Quantity')}
              </label>
              <Input
                name="stock_quantity"
                type="number"
                value={formData.stock_quantity}
                onChange={handleInputChange}
                placeholder="Enter quantity"
                min="0"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                {t('products.unit', 'Unit')}
              </label>
              <select
                name="unit"
                value={formData.unit}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option value="">{t('products.selectUnit', 'Select unit')}</option>
                {unitOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              {t('products.notes', 'Notes')}
            </label>
            <Textarea
              name="notes"
              value={formData.notes}
              onChange={handleInputChange}
              rows={3}
              placeholder={t('products.notesPlaceholder', 'Additional notes about the product')}
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
        {t('products.errorLoading', 'Error Loading Products')}
      </h2>
      <p className="text-red-600 mb-4">{error}</p>
      <Button onClick={loadProducts} variant="destructive">
        {t('common.tryAgain', 'Try Again')}
      </Button>
    </div>
  )

  if (error && products.length === 0) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {t('products.title', 'Products')}
            </h1>
            <p className="text-gray-600">
              {t('products.subtitle', 'Manage your landscape architecture products and materials')}
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
            {t('products.title', 'Products')}
          </h1>
          <p className="text-gray-600">
            {t('products.subtitle', 'Manage your landscape architecture products and materials')}
          </p>
        </div>
        <div className="flex space-x-2">
          <Button
            variant="outline"
            className="flex items-center space-x-2"
          >
            <Upload className="h-4 w-4" />
            <span>{t('products.importExcel', 'Import Excel/CSV')}</span>
          </Button>
          <Button
            className="flex items-center space-x-2"
            onClick={() => setShowAddModal(true)}
          >
            <Plus className="h-4 w-4" />
            <span>{t('products.addProduct', 'Add Product')}</span>
          </Button>
        </div>
      </div>

      {/* Search Bar */}
      <div className="flex items-center space-x-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input
            placeholder={t('products.searchPlaceholder', 'Search products...')}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        {totalProducts > 0 && (
          <span className="text-sm text-gray-500">
            {totalProducts} {t('products.total', 'products')}
          </span>
        )}
      </div>

      {loading ? (
        <Card>
          <CardContent>
            <LoadingSpinner />
          </CardContent>
        </Card>
      ) : !Array.isArray(products) || products.length === 0 ? (
        <Card>
          <CardContent className="p-12">
            <div className="text-center">
              <Package className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h2 className="text-lg font-semibold text-gray-900 mb-2">
                {t('products.noProducts', 'No products found')}
              </h2>
              <p className="text-gray-500 mb-6">
                {searchTerm
                  ? t('products.noSearchResults', 'No products match your search criteria')
                  : t('products.createFirst', 'Add your first product to get started')
                }
              </p>
              <Button onClick={() => setShowAddModal(true)}>
                <Plus className="h-4 w-4 mr-2" />
                {t('products.addProduct', 'Add Product')}
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {products.map((product) => {
            const stockBadge = getStockBadge(product.stock_quantity)
            return (
              <Card key={product.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-lg flex items-center">
                      <Package2 className="h-5 w-5 mr-2 text-green-600" />
                      <div>
                        {product.name}
                        {product.sku && (
                          <div className="text-sm text-gray-500 font-normal">
                            SKU: {product.sku}
                          </div>
                        )}
                      </div>
                    </CardTitle>
                    <div className="flex space-x-1">
                      <Button
                        onClick={() => openEditModal(product)}
                        variant="outline"
                        size="sm"
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button
                        onClick={() => handleDeleteProduct(product.id, product.name)}
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
                  {product.description && (
                    <p className="text-gray-600 text-sm line-clamp-2">
                      {product.description}
                    </p>
                  )}

                  <div className="flex items-center justify-between">
                    {product.price && (
                      <div className="flex items-center text-green-600 font-semibold">
                        <DollarSign className="h-4 w-4 mr-1" />
                        <span>{formatCurrency(product.price)}</span>
                        {product.unit && (
                          <span className="text-gray-500 text-sm ml-1">
                            /{product.unit}
                          </span>
                        )}
                      </div>
                    )}

                    <Badge variant={stockBadge.variant}>
                      {stockBadge.label}
                    </Badge>
                  </div>

                  {product.category && (
                    <div className="text-sm">
                      <span className="font-medium text-gray-700">
                        {t('products.category', 'Category')}:
                      </span>
                      <span className="text-gray-600 ml-2">
                        {getCategoryLabel(product.category)}
                      </span>
                    </div>
                  )}

                  {product.supplier_id && (
                    <div className="text-sm">
                      <span className="font-medium text-gray-700">
                        {t('products.supplier', 'Supplier')}:
                      </span>
                      <span className="text-gray-600 ml-2">
                        {getSupplierName(product.supplier_id)}
                      </span>
                    </div>
                  )}

                  {product.stock_quantity !== undefined && (
                    <div className="text-sm">
                      <span className="font-medium text-gray-700">
                        {t('products.stock', 'Stock')}:
                      </span>
                      <span className="text-gray-600 ml-2">
                        {product.stock_quantity} {product.unit || t('products.units.piece', 'pieces')}
                      </span>
                    </div>
                  )}
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}

      {/* Add Product Modal */}
      {showAddModal && (
        <ProductForm
          onSubmit={handleAddProduct}
          onCancel={() => {
            setShowAddModal(false)
            resetForm()
          }}
        />
      )}

      {/* Edit Product Modal */}
      {showEditModal && (
        <ProductForm
          isEdit={true}
          onSubmit={handleEditProduct}
          onCancel={() => {
            setShowEditModal(false)
            setEditingProduct(null)
            resetForm()
          }}
        />
      )}
    </div>
  )
}

export default Products
