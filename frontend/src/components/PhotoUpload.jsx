import React, { useState, useCallback } from 'react';
import { Upload, X, Camera, Image, FileImage, MessageSquare } from 'lucide-react';
import { toast } from 'sonner';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Label } from './ui/label';

const PhotoUpload = ({ 
  category = 'example', 
  entityId = null, 
  onUploadSuccess = () => {},
  allowedCategories = ['plant', 'material', 'property', 'project', 'example', 'inspiration', 'reference']
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploadCategory, setUploadCategory] = useState(category);
  const [uploadTitle, setUploadTitle] = useState('');
  const [uploadDescription, setUploadDescription] = useState('');

  const categoryIcons = {
    plant: <Image className="w-4 h-4" />,
    material: <FileImage className="w-4 h-4" />,
    property: <Camera className="w-4 h-4" />,
    project: <Camera className="w-4 h-4" />,
    example: <Image className="w-4 h-4" />,
    inspiration: <MessageSquare className="w-4 h-4" />,
    reference: <FileImage className="w-4 h-4" />
  };

  const categoryLabels = {
    plant: 'Plant Foto',
    material: 'Materiaal Foto',
    property: 'Eigendom Foto',
    project: 'Project Foto',
    example: 'Voorbeeld',
    inspiration: 'Inspiratie',
    reference: 'Referentie'
  };

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    const imageFiles = files.filter(file => file.type.startsWith('image/'));
    
    if (imageFiles.length !== files.length) {
      toast({
        title: "Alleen afbeeldingen toegestaan",
        description: "Enkele bestanden zijn overgeslagen omdat ze geen afbeeldingen zijn.",
        variant: "destructive"
      });
    }

    setSelectedFiles(prev => [...prev, ...imageFiles]);
  }, []);

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    setSelectedFiles(prev => [...prev, ...files]);
  };

  const removeFile = (index) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const uploadFile = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', uploadCategory);
    if (entityId) {
      formData.append('entity_id', entityId.toString());
    }
    if (uploadTitle) {
      formData.append('title', uploadTitle);
    }
    if (uploadDescription) {
      formData.append('description', uploadDescription);
    }

    const response = await fetch('/api/photos/upload', {
      method: 'POST',
      credentials: 'include',
      body: formData
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Upload mislukt');
    }

    return response.json();
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) return;

    setIsUploading(true);
    let successCount = 0;
    let errorCount = 0;

    try {
      for (const file of selectedFiles) {
        try {
          await uploadFile(file);
          successCount++;
        } catch (error) {
          console.error(`Upload failed for ${file.name}:`, error);
          errorCount++;
        }
      }

      if (successCount > 0) {
        toast({
          title: "Upload voltooid",
          description: `${successCount} foto${successCount > 1 ? '’s' : ''} succesvol geüpload${errorCount > 0 ? `, ${errorCount} mislukt` : ''}.`
        });
        setSelectedFiles([]);
        setUploadTitle('');
        setUploadDescription('');
        onUploadSuccess();
      } else {
        toast({
          title: "Upload mislukt",
          description: "Geen foto’s konden worden geüpload.",
          variant: "destructive"
        });
      }
    } catch (error) {
      toast({
        title: "Upload fout",
        description: error.message,
        variant: "destructive"
      });
    } finally {
      setIsUploading(false);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Upload className="w-5 h-5" />
          Foto Upload
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Category Selection */}
        <div className="space-y-2">
          <Label htmlFor="category">Categorie</Label>
          <Select value={uploadCategory} onValueChange={setUploadCategory}>
            <SelectTrigger>
              <SelectValue placeholder="Selecteer categorie" />
            </SelectTrigger>
            <SelectContent>
              {allowedCategories.map(cat => (
                <SelectItem key={cat} value={cat}>
                  <div className="flex items-center gap-2">
                    {categoryIcons[cat]}
                    {categoryLabels[cat]}
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Title and Description */}
        <div className="space-y-2">
          <Label htmlFor="title">Titel (optioneel)</Label>
          <Input
            id="title"
            value={uploadTitle}
            onChange={(e) => setUploadTitle(e.target.value)}
            placeholder="Foto titel..."
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="description">Beschrijving (optioneel)</Label>
          <Textarea
            id="description"
            value={uploadDescription}
            onChange={(e) => setUploadDescription(e.target.value)}
            placeholder="Beschrijf de foto..."
            rows={3}
          />
        </div>

        {/* Drag and Drop Area */}
        <div
          className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
            isDragging 
              ? 'border-primary bg-primary/5' 
              : 'border-gray-300 hover:border-gray-400'
          }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <p className="text-lg font-medium text-gray-700 mb-2">
            Sleep foto’s hierheen of klik om te selecteren
          </p>
          <p className="text-sm text-gray-500 mb-4">
            PNG, JPG, JPEG, GIF, WEBP tot 10MB
          </p>
          <input
            type="file"
            multiple
            accept="image/*"
            onChange={handleFileSelect}
            className="hidden"
            id="file-upload"
          />
          <Button
            type="button"
            variant="outline"
            onClick={() => document.getElementById('file-upload').click()}
          >
            Bestanden selecteren
          </Button>
        </div>

        {/* Selected Files */}
        {selectedFiles.length > 0 && (
          <div className="space-y-2">
            <Label>Geselecteerde bestanden</Label>
            <div className="space-y-2 max-h-32 overflow-y-auto">
              {selectedFiles.map((file, index) => (
                <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <div className="flex items-center gap-2">
                    <Image className="w-4 h-4 text-gray-500" />
                    <span className="text-sm font-medium">{file.name}</span>
                    <span className="text-xs text-gray-500">({formatFileSize(file.size)})</span>
                  </div>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => removeFile(index)}
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Upload Button */}
        {selectedFiles.length > 0 && (
          <Button
            onClick={handleUpload}
            disabled={isUploading}
            className="w-full"
          >
            {isUploading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                Uploaden...
              </>
            ) : (
              <>
                <Upload className="w-4 h-4 mr-2" />
                {selectedFiles.length} foto{selectedFiles.length > 1 ? '’s' : ''} uploaden
              </>
            )}
          </Button>
        )}
      </CardContent>
    </Card>
  );
};

export default PhotoUpload;