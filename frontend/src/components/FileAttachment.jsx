/**
 * FileAttachment Component with Supabase Storage Support
 * Handles file uploads, management, and display for contextual attachments
 */

import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/BackendAuthContext';
import { toast } from '../hooks/use-toast';
import {Upload, File, Image, FileText, Archive, Download, Trash2, Loader2} from 'lucide-react';

const FileAttachment = ({ 
  parentType, 
  parentId, 
  parentName = 'item',
  className = ''
}) => {
  const { user, token } = useAuth();
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(true);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || '';

  useEffect(() => {
    if (user && parentType && parentId) {
      fetchFiles();
    }
  }, [user, parentType, parentId]);

  const fetchFiles = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `${API_BASE_URL}/api/resources/parent/${parentType}/${parentId}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.ok) {
        const fetchedFiles = await response.json();
        setFiles(fetchedFiles);
      } else {
        console.error('Failed to fetch files:', response.status);
      }
    } catch (error) {
      console.error('Error fetching files:', error);
      toast({
        title: "Error",
        description: "Failed to load attachments",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (selectedFiles) => {
    if (!selectedFiles || selectedFiles.length === 0) return;

    Array.from(selectedFiles).forEach(file => {
      uploadFile(file);
    });
  };

  const uploadFile = async (file) => {
    if (!file) return;

    // Validate file size (10MB limit)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
      toast({
        title: "File too large",
        description: "Maximum file size is 10MB",
        variant: "destructive"
      });
      return;
    }

    setUploading(true);

    try {
      // Convert file to base64
      const fileReader = new FileReader();
      fileReader.onload = async (e) => {
        try {
          const base64Content = e.target.result;
          
          // Determine file type
          const getFileType = (mimeType) => {
            if (mimeType.startsWith('image/')) return 'image';
            if (mimeType.includes('pdf') || mimeType.includes('document') || mimeType.includes('text')) return 'document';
            if (mimeType.includes('sheet') || mimeType.includes('csv')) return 'spreadsheet';
            if (mimeType.includes('presentation')) return 'presentation';
            if (mimeType.includes('zip') || mimeType.includes('rar') || mimeType.includes('archive')) return 'archive';
            return 'other';
          };

          const resourceData = {
            filename: file.name,
            original_filename: file.name,
            file_type: getFileType(file.type),
            mime_type: file.type,
            file_size: file.size,
            file_content: base64Content, // Will be uploaded to Supabase Storage
            parent_type: parentType,
            parent_id: parentId,
            description: `Attachment for ${parentName}`
          };

          const response = await fetch(`${API_BASE_URL}/api/resources`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(resourceData)
          });

          if (response.ok) {
            const newFile = await response.json();
            setFiles(prev => [...prev, newFile]);
            toast({
              title: "File uploaded",
              description: `${file.name} uploaded successfully`
            });
          } else {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Upload failed');
          }
        } catch (error) {
          console.error('Upload error:', error);
          toast({
            title: "Upload failed",
            description: error.message || 'Failed to upload file',
            variant: "destructive"
          });
        } finally {
          setUploading(false);
        }
      };

      fileReader.onerror = () => {
        toast({
          title: "File read error",
          description: "Failed to read the selected file",
          variant: "destructive"
        });
        setUploading(false);
      };

      fileReader.readAsDataURL(file);
    } catch (error) {
      console.error('Upload error:', error);
      toast({
        title: "Upload failed",
        description: "Failed to upload file",
        variant: "destructive"
      });
      setUploading(false);
    }
  };

  const deleteFile = async (fileId, filename) => {
    if (!confirm(`Are you sure you want to delete "${filename}"?`)) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/resources/${fileId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        setFiles(prev => prev.filter(file => file.id !== fileId));
        toast({
          title: "File deleted",
          description: `${filename} deleted successfully`
        });
      } else {
        throw new Error('Delete failed');
      }
    } catch (error) {
      console.error('Delete error:', error);
      toast({
        title: "Delete failed",
        description: "Failed to delete file",
        variant: "destructive"
      });
    }
  };

  const downloadFile = (file) => {
    if (file.file_url) {
      // Open file URL in new tab for download
      window.open(file.file_url, '_blank');
    } else if (file.file_content) {
      // Handle legacy base64 files
      const link = document.createElement('a');
      link.href = file.file_content;
      link.download = file.original_filename;
      link.click();
    }
  };

  const getFileIcon = (fileType, mimeType) => {
    switch (fileType) {
      case 'image':
        return <Image className="w-5 h-5 text-blue-400" />;
      case 'document':
        return <FileText className="w-5 h-5 text-green-400" />;
      case 'archive':
        return <Archive className="w-5 h-5 text-yellow-400" />;
      default:
        return <File className="w-5 h-5 text-gray-400" />;
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragActive(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragActive(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    const droppedFiles = e.dataTransfer.files;
    handleFileSelect(droppedFiles);
  };

  if (!user) {
    return null;
  }

  return (
    <div className={`file-attachment space-y-4 ${className}`}>
      {/* Upload Area */}
      <div
        className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
          dragActive
            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
            : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          className="hidden"
          onChange={(e) => handleFileSelect(e.target.files)}
        />
        
        {uploading ? (
          <div className="flex flex-col items-center">
            <Loader2 className="w-8 h-8 text-blue-500 animate-spin mb-2" />
            <p className="text-sm text-gray-600 dark:text-gray-400">Uploading...</p>
          </div>
        ) : (
          <div className="flex flex-col items-center">
            <Upload className="w-8 h-8 text-gray-400 mb-2" />
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
              Drag and drop files here, or{' '}
              <button
                onClick={() => fileInputRef.current?.click()}
                className="text-blue-500 hover:text-blue-600 underline"
              >
                browse
              </button>
            </p>
            <p className="text-xs text-gray-500">Maximum file size: 10MB</p>
          </div>
        )}
      </div>

      {/* Files List */}
      {loading ? (
        <div className="flex items-center justify-center p-4">
          <Loader2 className="w-5 h-5 animate-spin text-gray-400" />
          <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">Loading attachments...</span>
        </div>
      ) : files.length > 0 ? (
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Attachments ({files.length})
          </h4>
          {files.map((file) => (
            <div
              key={file.id}
              className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg"
            >
              <div className="flex items-center space-x-3">
                {getFileIcon(file.file_type, file.mime_type)}
                <div>
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {file.original_filename}
                  </p>
                  <p className="text-xs text-gray-500">
                    {formatFileSize(file.file_size)} • {file.file_type}
                  </p>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => downloadFile(file)}
                  className="p-1 text-gray-400 hover:text-blue-500 transition-colors"
                  title="Download"
                >
                  <Download className="w-4 h-4" />
                </button>
                <button
                  onClick={() => deleteFile(file.id, file.original_filename)}
                  className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                  title="Delete"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center p-4">
          <p className="text-sm text-gray-500">No attachments yet</p>
        </div>
      )}
    </div>
  );
};

export default FileAttachment;