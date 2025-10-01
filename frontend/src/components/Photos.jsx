import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { 
  Camera, 
  Upload, 
  Grid, 
  List, 
  Filter, 
  Search,
  Image as ImageIcon,
  MapPin,
  Calendar,
  Tag,
  Download,
  Trash2
} from 'lucide-react'
import PhotoUpload from './PhotoUpload'
import PhotoGallery from './PhotoGallery'
import { useLanguage } from '../i18n/LanguageProvider'
import toast from 'react-hot-toast'

const Photos = ({ user }) => {
  const { t } = useLanguage()
  const [__photos, set_photos] = useState([])
  const [__loading, set_loading] = useState(true)
  const [__viewMode, set_viewMode] = useState('grid') // 'grid' or 'list'
  const [__selectedCategory, set_selectedCategory] = useState('all')
  const [__searchTerm, set_searchTerm] = useState('')
  const [__showUpload, set_showUpload] = useState(false)

  // Photo categories for organization
  const categories = [
    { value: 'all', label: t('photos.categories.all', 'All Photos'), icon: ImageIcon },
    { value: 'plants', label: t('photos.categories.plants', 'Plants'), icon: ImageIcon },
    { value: 'materials', label: t('photos.categories.materials', 'Materials'), icon: ImageIcon },
    { value: 'properties', label: t('photos.categories.properties', 'Properties'), icon: MapPin },
    { value: 'projects', label: t('photos.categories.projects', 'Projects'), icon: ImageIcon },
    { value: 'examples', label: t('photos.categories.examples', 'Examples'), icon: ImageIcon },
    { value: 'inspiration', label: t('photos.categories.inspiration', 'Inspiration'), icon: ImageIcon },
    { value: 'reference', label: t('photos.categories.reference', 'Reference'), icon: ImageIcon }
  ]

  useEffect(() => {
    fetchPhotos()
  }, [])

  const fetchPhotos = async () => {
    try {
      const response = await fetch('/api/photos', {
        credentials: 'include'
      })
      if (response.ok) {
        const data = await response.json()
        setPhotos(data.photos || [])
      } else {
        console.error('Failed to fetch photos')
      }
    } catch (error) {
      console.error('Error fetching photos:', error)
    } finally {
      setLoading(false)
    }
  }

  const handlePhotoUploaded = (newPhotos) => {
    setPhotos(prev => [...prev, ...newPhotos])
    setShowUpload(false)
    toast.success(t('photos.uploadSuccess', 'Photos uploaded successfully'))
  }

  const handleDeletePhoto = async (photoId) => {
    if (!window.confirm(t('photos.confirmDelete', 'Are you sure you want to delete this photo?'))) {
      return
    }

    try {
      const response = await fetch(`/api/photos/${photoId}`, {
        method: 'DELETE',
        credentials: 'include'
      })

      if (response.ok) {
        setPhotos(prev => prev.filter(photo => photo.id !== photoId))
        toast.success(t('photos.deleteSuccess', 'Photo deleted successfully'))
      } else {
        toast.error(t('photos.deleteError', 'Failed to delete photo'))
      }
    } catch (error) {
      console.error('Error deleting photo:', error)
      toast.error(t('photos.deleteError', 'Failed to delete photo'))
    }
  }

  // Filter photos based on search and category
  const filteredPhotos = photos.filter(photo => {
    const matchesSearch = photo.filename?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         photo.caption?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         photo.tags?.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
    
    const matchesCategory = selectedCategory === 'all' || photo.category === selectedCategory
    
    return matchesSearch && matchesCategory
  })

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
                <Camera className="h-8 w-8 text-green-600" />
                {t('photos.title', 'Photo Gallery')}
              </h1>
              <p className="text-gray-600 mt-2">
                {t('photos.subtitle', 'Manage and organize your project photos')}
              </p>
            </div>
            <button
              onClick={() => setShowUpload(true)}
              className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
            >
              <Upload className="h-5 w-5" />
              {t('photos.uploadPhotos', 'Upload Photos')}
            </button>
          </div>
        </div>

        {/* Controls */}
        <div className="mb-6 flex flex-wrap gap-4 items-center justify-between">
          {/* Search */}
          <div className="relative flex-1 min-w-64">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
            <input
              type="text"
              placeholder={t('photos.searchPlaceholder', 'Search photos...')}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
          </div>

          {/* Category Filter */}
          <div className="flex items-center gap-2">
            <Filter className="h-5 w-5 text-gray-500" />
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            >
              {categories.map(category => (
                <option key={category.value} value={category.value}>
                  {category.label}
                </option>
              ))}
            </select>
          </div>

          {/* View Mode Toggle */}
          <div className="flex items-center gap-1 bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded ${viewMode === 'grid' ? 'bg-white shadow' : ''}`}
            >
              <Grid className="h-4 w-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded ${viewMode === 'list' ? 'bg-white shadow' : ''}`}
            >
              <List className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Stats */}
        <div className="mb-6 grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg p-4 shadow-sm border">
            <div className="flex items-center gap-3">
              <ImageIcon className="h-8 w-8 text-blue-600" />
              <div>
                <p className="text-sm text-gray-600">{t('photos.stats.total', 'Total Photos')}</p>
                <p className="text-2xl font-bold text-gray-900">{photos.length}</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg p-4 shadow-sm border">
            <div className="flex items-center gap-3">
              <Filter className="h-8 w-8 text-green-600" />
              <div>
                <p className="text-sm text-gray-600">{t('photos.stats.filtered', 'Filtered')}</p>
                <p className="text-2xl font-bold text-gray-900">{filteredPhotos.length}</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg p-4 shadow-sm border">
            <div className="flex items-center gap-3">
              <Tag className="h-8 w-8 text-purple-600" />
              <div>
                <p className="text-sm text-gray-600">{t('photos.stats.categories', 'Categories')}</p>
                <p className="text-2xl font-bold text-gray-900">{categories.length - 1}</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg p-4 shadow-sm border">
            <div className="flex items-center gap-3">
              <Calendar className="h-8 w-8 text-orange-600" />
              <div>
                <p className="text-sm text-gray-600">{t('photos.stats.recent', 'This Month')}</p>
                <p className="text-2xl font-bold text-gray-900">
                  {photos.filter(photo => {
                    const photoDate = new Date(photo.uploaded_at)
                    const oneMonthAgo = new Date()
                    oneMonthAgo.setMonth(oneMonthAgo.getMonth() - 1)
                    return photoDate > oneMonthAgo
                  }).length}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Photo Gallery */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ImageIcon className="h-5 w-5" />
              {selectedCategory === 'all' 
                ? t('photos.allPhotos', 'All Photos')
                : categories.find(c => c.value === selectedCategory)?.label
              }
              {searchTerm && (
                <span className="text-sm text-gray-500">
                  - {t('photos.searchResults', 'Search results for')}: "{searchTerm}"
                </span>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {filteredPhotos.length === 0 ? (
              <div className="text-center py-12">
                <ImageIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-600 mb-2">
                  {t('photos.noPhotos', 'No photos found')}
                </h3>
                <p className="text-gray-500 mb-4">
                  {searchTerm || selectedCategory !== 'all'
                    ? t('photos.noPhotosFiltered', 'Try adjusting your search or filter settings')
                    : t('photos.noPhotosYet', 'Upload some photos to get started')
                  }
                </p>
                <button
                  onClick={() => setShowUpload(true)}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  {t('photos.uploadFirst', 'Upload Your First Photo')}
                </button>
              </div>
            ) : (
              <PhotoGallery 
                photos={filteredPhotos}
                viewMode={viewMode}
                onDeletePhoto={handleDeletePhoto}
                user={user}
              />
            )}
          </CardContent>
        </Card>

        {/* Upload Modal */}
        {showUpload && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-2xl w-full max-h-90vh overflow-y-auto">
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-bold text-gray-900">
                    {t('photos.uploadPhotos', 'Upload Photos')}
                  </h2>
                  <button
                    onClick={() => setShowUpload(false)}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    ×
                  </button>
                </div>
                <PhotoUpload 
                  onPhotoUploaded={handlePhotoUploaded}
                  onCancel={() => setShowUpload(false)}
                />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Photos