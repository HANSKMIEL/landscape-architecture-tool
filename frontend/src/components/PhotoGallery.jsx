import React, { useState, useEffect, useCallback } from 'react';
import { Camera, Download, Trash2, Star, Eye, MoreVertical } from 'lucide-react';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from './ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from './ui/dialog';

const PhotoGallery = ({ 
  category = null, 
  entityId = null, 
  title = "Foto Galerij",
  showUpload = true,
  maxPhotos = 50,
  columns = 4,
  onPhotoUpdate = () => {}
}) => {
  const [__photos, set_photos] = useState([]);
  const [__loading, set_loading] = useState(true);
  // Note: useToast hook would need to be imported from your toast library
  // const { toast } = useToast();

  const __categoryLabels = {
    plant: 'Plant',
    material: 'Materiaal',
    property: 'Eigendom',
    project: 'Project',
    example: 'Voorbeeld',
    inspiration: 'Inspiratie',
    reference: 'Referentie'
  };

  const fetchPhotos = useCallback(async () => {
    try {
      const params = new URLSearchParams();
      if (category) params.append('category', category);
      if (entityId) params.append('entity_id', entityId.toString());
      params.append('limit', maxPhotos.toString());

      const response = await fetch(`/api/photos?${params.toString()}`, {
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        setPhotos(data.photos || []);
      } else {
        console.error('Failed to fetch photos');
      }
    } catch (_error) {
      console.error('Error fetching photos:', _error);
    } finally {
      setLoading(false);
    }
  }, [category, entityId, maxPhotos]);

  useEffect(() => {
    fetchPhotos();
  }, [fetchPhotos]);

  const handleSetPrimary = async (photoId) => {
    try {
      const response = await fetch(`/api/photos/${photoId}/primary`, {
        method: 'POST',
        credentials: 'include'
      });

      if (response.ok) {
        console.log("Primaire foto ingesteld");
        await fetchPhotos(); // Refresh to show updated primary status
        onPhotoUpdate();
      } else {
        const errorData = await response.json();
        console.error("Fout:", errorData.error || "Kon primaire foto niet instellen.");
      }
    } catch (_error) {
      console.error("Netwerkfout bij het instellen van primaire foto:", _error);
    }
  };

  const handleDeletePhoto = async (photoId) => {
    if (!confirm('Weet je zeker dat je deze foto wilt verwijderen?')) {
      return;
    }

    try {
      const response = await fetch(`/api/photos/${photoId}`, {
        method: 'DELETE',
        credentials: 'include'
      });

      if (response.ok) {
        console.log("Foto verwijderd");
        await fetchPhotos(); // Refresh photos
        onPhotoUpdate();
      } else {
        const errorData = await response.json();
        console.error("Fout:", errorData.error || "Kon foto niet verwijderen.");
      }
    } catch (_error) {
      console.error("Netwerkfout bij het verwijderen van foto:", _error);
    }
  };

  const handleDownload = (photo) => {
    const link = document.createElement('a');
    link.href = `/api/photos/file/${photo.id}`;
    link.download = photo.original_filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString('nl-NL', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '';
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-center">
            <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin" />
            <span className="ml-2">Foto's laden...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">{title}</h3>
        {photos.length > 0 && (
          <span className="text-sm text-gray-500">
            {photos.length} foto{photos.length > 1 ? "'s" : ''}
          </span>
        )}
      </div>

      {photos.length === 0 ? (
        <Card>
          <CardContent className="p-6 text-center">
            <Camera className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <p className="text-gray-500 mb-2">Nog geen foto's geüpload</p>
            {showUpload && (
              <p className="text-sm text-gray-400">
                Upload je eerste foto om te beginnen
              </p>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className={`grid grid-cols-1 sm:grid-cols-2 md:grid-cols-${Math.min(columns, 4)} gap-4`}>
          {photos.map((photo) => (
            <Card key={photo.id} className="overflow-hidden group">
              <div className="relative aspect-square">
                <img
                  src={`/api/photos/thumbnail/${photo.id}`}
                  alt={photo.alt_text || photo.title || 'Foto'}
                  className="w-full h-full object-cover transition-transform group-hover:scale-105"
                  onError={(e) => {
                    e.target.src = `/api/photos/file/${photo.id}`;
                  }}
                />
                
                {/* Primary badge */}
                {photo.is_primary && (
                  <Badge variant="secondary" className="absolute top-2 left-2">
                    <Star className="w-3 h-3 mr-1" />
                    Primair
                  </Badge>
                )}

                {/* Category badge */}
                {photo.category && (
                  <Badge variant="outline" className="absolute top-2 right-2 bg-white/90">
                    {categoryLabels[photo.category] || photo.category}
                  </Badge>
                )}

                {/* Overlay with actions */}
                <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                  <div className="flex gap-2">
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button size="sm" variant="secondary">
                          <Eye className="w-4 h-4" />
                        </Button>
                      </DialogTrigger>
                      <DialogContent className="max-w-4xl">
                        <DialogHeader>
                          <DialogTitle>{photo.title || photo.original_filename}</DialogTitle>
                        </DialogHeader>
                        <div className="space-y-4">
                          <img
                            src={`/api/photos/file/${photo.id}`}
                            alt={photo.alt_text || photo.title || 'Foto'}
                            className="w-full h-auto max-h-[70vh] object-contain"
                          />
                          {photo.description && (
                            <p className="text-gray-600">{photo.description}</p>
                          )}
                          <div className="flex flex-wrap gap-4 text-sm text-gray-500">
                            <span>Geüpload: {formatDate(photo.uploaded_at)}</span>
                            <span>Grootte: {formatFileSize(photo.file_size)}</span>
                            {photo.width && photo.height && (
                              <span>Afmetingen: {photo.width} × {photo.height}</span>
                            )}
                          </div>
                        </div>
                      </DialogContent>
                    </Dialog>

                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button size="sm" variant="secondary">
                          <MoreVertical className="w-4 h-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent>
                        <DropdownMenuItem onClick={() => handleDownload(photo)}>
                          <Download className="w-4 h-4 mr-2" />
                          Download
                        </DropdownMenuItem>
                        {entityId && !photo.is_primary && (
                          <DropdownMenuItem onClick={() => handleSetPrimary(photo.id)}>
                            <Star className="w-4 h-4 mr-2" />
                            Instellen als primair
                          </DropdownMenuItem>
                        )}
                        <DropdownMenuSeparator />
                        <DropdownMenuItem 
                          onClick={() => handleDeletePhoto(photo.id)}
                          className="text-red-600"
                        >
                          <Trash2 className="w-4 h-4 mr-2" />
                          Verwijderen
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </div>
              </div>

              {/* Photo info */}
              <CardContent className="p-3">
                <div className="space-y-1">
                  <h4 className="font-medium text-sm truncate">
                    {photo.title || photo.original_filename}
                  </h4>
                  {photo.description && (
                    <p className="text-xs text-gray-500 line-clamp-2">
                      {photo.description}
                    </p>
                  )}
                  <div className="flex justify-between items-center text-xs text-gray-400">
                    <span>{formatDate(photo.uploaded_at)}</span>
                    <span>{formatFileSize(photo.file_size)}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default PhotoGallery;
