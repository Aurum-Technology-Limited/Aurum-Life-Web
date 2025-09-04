import React, { useState, useCallback } from 'react';
import { LazyImage } from './LazyImage';
import { Upload, X, Image as ImageIcon } from 'lucide-react';
import { cn } from '../../lib/utils';

/**
 * ImageUpload Component
 * Handles image uploads with automatic WebP conversion
 * Shows preview using LazyImage component
 */
export function ImageUpload({
  onUpload,
  maxSize = 10 * 1024 * 1024, // 10MB
  acceptedFormats = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'],
  className,
  preview = true,
  multiple = false
}) {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  }, []);

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFiles(e.target.files);
    }
  };

  const handleFiles = (files) => {
    setError(null);
    const fileArray = Array.from(files);
    
    // Validate files
    for (const file of fileArray) {
      if (!acceptedFormats.includes(file.type)) {
        setError(`Invalid file type: ${file.type}. Accepted formats: ${acceptedFormats.join(', ')}`);
        return;
      }
      
      if (file.size > maxSize) {
        setError(`File too large: ${file.name}. Maximum size: ${maxSize / 1024 / 1024}MB`);
        return;
      }
    }
    
    // Create preview URLs
    const newFiles = fileArray.map(file => ({
      file,
      preview: URL.createObjectURL(file),
      name: file.name,
      size: file.size,
      type: file.type
    }));
    
    if (multiple) {
      setSelectedFiles(prev => [...prev, ...newFiles]);
    } else {
      setSelectedFiles(newFiles.slice(0, 1));
    }
  };

  const removeFile = (index) => {
    setSelectedFiles(prev => {
      const newFiles = [...prev];
      URL.revokeObjectURL(newFiles[index].preview);
      newFiles.splice(index, 1);
      return newFiles;
    });
  };

  const uploadFiles = async () => {
    if (selectedFiles.length === 0) return;
    
    setUploading(true);
    setError(null);
    
    try {
      const uploadPromises = selectedFiles.map(async ({ file }) => {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('generate_webp', 'true');
        formData.append('generate_responsive', 'true');
        
        const response = await fetch('/api/upload/image', {
          method: 'POST',
          body: formData,
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        if (!response.ok) {
          throw new Error(`Upload failed: ${response.statusText}`);
        }
        
        return response.json();
      });
      
      const results = await Promise.all(uploadPromises);
      
      // Clean up preview URLs
      selectedFiles.forEach(file => URL.revokeObjectURL(file.preview));
      setSelectedFiles([]);
      
      // Notify parent component
      onUpload?.(multiple ? results : results[0]);
      
    } catch (err) {
      setError(err.message || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className={cn("w-full", className)}>
      {/* Upload area */}
      <div
        className={cn(
          "relative border-2 border-dashed rounded-lg p-6 transition-colors",
          dragActive ? "border-blue-400 bg-blue-50" : "border-gray-300",
          "hover:border-gray-400 cursor-pointer"
        )}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          id="file-upload"
          className="sr-only"
          onChange={handleChange}
          accept={acceptedFormats.join(',')}
          multiple={multiple}
        />
        
        <label
          htmlFor="file-upload"
          className="flex flex-col items-center justify-center cursor-pointer"
        >
          <Upload className="w-12 h-12 text-gray-400 mb-3" />
          <p className="text-sm text-gray-600">
            <span className="font-medium">Click to upload</span> or drag and drop
          </p>
          <p className="text-xs text-gray-500 mt-1">
            {acceptedFormats.map(f => f.split('/')[1].toUpperCase()).join(', ')} up to {maxSize / 1024 / 1024}MB
          </p>
        </label>
      </div>

      {/* Error message */}
      {error && (
        <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {/* Selected files preview */}
      {selectedFiles.length > 0 && (
        <div className="mt-4 space-y-3">
          <h3 className="text-sm font-medium text-gray-700">Selected files:</h3>
          
          {selectedFiles.map((file, index) => (
            <div key={index} className="relative bg-gray-50 rounded-lg p-3">
              <div className="flex items-start space-x-3">
                {/* Image preview using LazyImage */}
                {preview && file.type.startsWith('image/') && (
                  <div className="flex-shrink-0">
                    <LazyImage
                      src={file.preview}
                      alt={file.name}
                      width={80}
                      height={80}
                      className="rounded-md overflow-hidden"
                      objectFit="cover"
                      priority={true}
                    />
                  </div>
                )}
                
                {/* File info */}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {file.name}
                  </p>
                  <p className="text-sm text-gray-500">
                    {(file.size / 1024).toFixed(1)} KB
                  </p>
                  <p className="text-xs text-gray-400 mt-1">
                    Will be converted to WebP format
                  </p>
                </div>
                
                {/* Remove button */}
                <button
                  type="button"
                  onClick={() => removeFile(index)}
                  className="flex-shrink-0 p-1 rounded-md hover:bg-gray-200 transition-colors"
                >
                  <X className="w-4 h-4 text-gray-500" />
                </button>
              </div>
            </div>
          ))}
          
          {/* Upload button */}
          <button
            type="button"
            onClick={uploadFiles}
            disabled={uploading}
            className={cn(
              "w-full py-2 px-4 rounded-md font-medium transition-colors",
              "bg-blue-600 text-white hover:bg-blue-700",
              "disabled:bg-gray-300 disabled:cursor-not-allowed"
            )}
          >
            {uploading ? 'Uploading...' : `Upload ${selectedFiles.length} file${selectedFiles.length > 1 ? 's' : ''}`}
          </button>
        </div>
      )}
    </div>
  );
}

/**
 * Example usage in a component
 */
export function ImageUploadExample() {
  const handleUpload = (result) => {
    console.log('Upload complete:', result);
    // result contains URLs for original, WebP, and responsive versions
  };

  return (
    <div className="max-w-md mx-auto p-6">
      <h2 className="text-lg font-semibold mb-4">Upload Images</h2>
      <ImageUpload
        onUpload={handleUpload}
        multiple={true}
        maxSize={5 * 1024 * 1024} // 5MB
      />
      
      {/* Example of using LazyImage with uploaded images */}
      <div className="mt-8">
        <h3 className="text-md font-medium mb-3">Uploaded Images:</h3>
        <div className="grid grid-cols-2 gap-4">
          {/* Images would be displayed here using LazyImage component */}
          <LazyImage
            src="/path/to/image.jpg"
            alt="Example image"
            className="rounded-lg overflow-hidden"
            width={200}
            height={200}
          />
        </div>
      </div>
    </div>
  );
}

export default ImageUpload;