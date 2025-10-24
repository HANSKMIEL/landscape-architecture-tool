import React, { useState } from 'react';
import { Camera, Upload, Images } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import PhotoUpload from './PhotoUpload';
import PhotoGallery from './PhotoGallery';
import { useLanguage } from '../i18n/LanguageProvider';

const PhotoManager = ({
  category = null,
  entityId = null,
  entityName = null,
  title = null,
  allowedCategories = ['plant', 'material', 'property', 'project', 'example', 'inspiration', 'reference'],
  showTabs = true
}) => {
  const { t } = useLanguage();
  const [refreshKey, setRefreshKey] = useState(0);

  const handleUploadSuccess = () => {
    // Trigger refresh of photo gallery
    setRefreshKey(prev => prev + 1);
  };

  const handlePhotoUpdate = () => {
    // Trigger refresh of photo gallery
    setRefreshKey(prev => prev + 1);
  };

  const getTitle = () => {
    const defaultTitle = title || t('photos.title', 'Photo Management');
    if (entityName) {
      return `${defaultTitle} - ${entityName}`;
    }
    return defaultTitle;
  };

  if (!showTabs) {
    // Simple layout without tabs
    return (
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Camera className="w-5 h-5" />
              {getTitle()}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <PhotoUpload
              category={category}
              entityId={entityId}
              onUploadSuccess={handleUploadSuccess}
              allowedCategories={allowedCategories}
            />

            <div key={refreshKey}>
              <PhotoGallery
                category={category}
                entityId={entityId}
                title={t('photos.uploaded', 'Uploaded Photos')}
                onPhotoUpdate={handlePhotoUpdate}
              />
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Tabbed layout
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Camera className="w-5 h-5" />
          {getTitle()}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="gallery" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="gallery" className="flex items-center gap-2">
              <Images className="w-4 h-4" />
              {t('photos.gallery', 'Gallery')}
            </TabsTrigger>
            <TabsTrigger value="upload" className="flex items-center gap-2">
              <Upload className="w-4 h-4" />
              {t('photos.upload', 'Upload')}
            </TabsTrigger>
          </TabsList>

          <TabsContent value="gallery" className="mt-6">
            <div key={refreshKey}>
              <PhotoGallery
                category={category}
                entityId={entityId}
                title={t('photos.photoGallery', 'Photo Gallery')}
                onPhotoUpdate={handlePhotoUpdate}
              />
            </div>
          </TabsContent>

          <TabsContent value="upload" className="mt-6">
            <PhotoUpload
              category={category}
              entityId={entityId}
              onUploadSuccess={handleUploadSuccess}
              allowedCategories={allowedCategories}
            />
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};

export default PhotoManager;