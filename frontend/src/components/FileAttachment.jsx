import React, { useState, useEffect, useCallback } from 'react';
import { resourcesAPI } from '../services/api';
import { useDataContext } from '../contexts/DataContext';
import FileViewer from './FileViewer';

const FileAttachment = ({ 
  parentType, 
  parentId, 
  parentName = 'item',
  className = ''
}) => {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const [viewingFile, setViewingFile] = useState(null);
  const { onDataMutation } = useDataContext();

  // Supported file types for validation
  const supportedTypes = {
    'image/png': 'PNG Image',
    'image/jpeg': 'JPEG Image', 
    'image/gif': 'GIF Image',
    'application/pdf': 'PDF Document',
    'application/msword': 'Word Document',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'Word Document (DOCX)',
    'text/plain': 'Text File'
  };

  // Load files for this parent entity
  const loadFiles = useCallback(async () => {
    if (!parentType || !parentId) return;
    
    setLoading(true);
    setError('');
    
    try {
      const response = await resourcesAPI.getParentResources(parentType, parentId);
      setFiles(response.data);
    } catch (err) {
      console.error('Error loading files:', err);
      setError('Failed to load files');
    } finally {
      setLoading(false);
    }
  }, [parentType, parentId]);

  useEffect(() => {
    loadFiles();
  }, [loadFiles]);

  // Handle file upload
  const handleFileUpload = async (files) => {
    if (!files.length) return;
    
    setUploading(true);
    setError('');
    setSuccess('');
    
    const uploadPromises = Array.from(files).map(async (file) => {
      try {
        // Validate file type
        if (!supportedTypes[file.type]) {
          throw new Error(`File type ${file.type} is not supported`);
        }
        
        // Upload file with contextual attachment
        const resource = await resourcesAPI.uploadFileWithParent(
          file,
          `File for ${parentName}`,
          parentType,
          parentId,
          'document'
        );
        
        return resource;
      } catch (error) {
        console.error(`Error uploading ${file.name}:`, error);
        throw new Error(`Failed to upload ${file.name}: ${error.message}`);
      }
    });
    
    try {
      const uploadedFiles = await Promise.all(uploadPromises);
      setSuccess(`Successfully uploaded ${uploadedFiles.length} file(s)`);
      await loadFiles(); // Refresh the list
      onDataMutation('resource', 'upload', { parentType, parentId, count: uploadedFiles.length });
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  // Handle file input change
  const handleFileInputChange = (e) => {
    const files = e.target.files;
    if (files) {
      handleFileUpload(files);
    }
    // Clear the input so the same file can be uploaded again
    e.target.value = '';
  };

  // Handle drag and drop
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
    
    const files = e.dataTransfer.files;
    if (files) {
      handleFileUpload(files);
    }
  };

  // Handle file deletion
  const handleDelete = async (fileId, filename) => {
    if (!window.confirm(`Are you sure you want to delete "${filename}"?`)) {
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      await resourcesAPI.deleteResource(fileId);
      setSuccess('File deleted successfully');
      await loadFiles();
      onDataMutation('resource', 'delete', { parentType, parentId, fileId });
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      console.error('Error deleting file:', err);
      setError('Failed to delete file');
    } finally {
      setLoading(false);
    }
  };

  // Format file size
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // Get file type display name
  const getFileTypeDisplay = (mimeType) => {
    return supportedTypes[mimeType] || 'Unknown';
  };

  // Get file icon based on type
  const getFileIcon = (mimeType) => {
    if (mimeType.startsWith('image/')) {
      return '🖼️';
    }
    if (mimeType === 'application/pdf') {
      return '📄';
    }
    if (mimeType.includes('word')) {
      return '📝';
    }
    if (mimeType === 'text/plain') {
      return '📄';
    }
    return '📁';
  };

  return (
    <div className={`file-attachment ${className}`}>
      <div className="bg-gray-800 rounded-lg p-4 mt-4">
        <div className="flex items-center justify-between mb-4">
          <h4 className="text-md font-medium text-white">
            Files ({files.length})
          </h4>
        </div>
        
        {/* Upload Area */}
        <div className="mb-4">
          <div 
            className={`border-2 border-dashed rounded-lg p-4 text-center transition-colors relative ${
              dragActive 
                ? 'border-blue-500 bg-blue-500/10' 
                : 'border-gray-600 hover:border-gray-500'
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <div className="text-gray-400">
              <div className="text-2xl mb-2">📁</div>
              <div className="text-sm">
                <span className="font-medium">Attach files</span> or drag and drop
              </div>
              <div className="text-xs mt-1">
                PNG, JPEG, GIF, PDF, DOC, DOCX, TXT (max 10MB)
              </div>
            </div>
            
            <input
              type="file"
              multiple
              accept=".png,.jpg,.jpeg,.gif,.pdf,.doc,.docx,.txt"
              onChange={handleFileInputChange}
              disabled={uploading}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed z-10"
              style={{ pointerEvents: uploading ? 'none' : 'auto' }}
            />
            
            {uploading && (
              <div className="absolute inset-0 bg-gray-800/50 rounded-lg flex items-center justify-center z-20">
                <div className="inline-flex items-center px-3 py-2 bg-blue-600 text-white rounded-lg text-sm">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Uploading...
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Status Messages */}
        {error && (
          <div className="mb-4 p-3 bg-red-900/50 border border-red-500 rounded-lg text-red-200 text-sm">
            {error}
          </div>
        )}
        
        {success && (
          <div className="mb-4 p-3 bg-green-900/50 border border-green-500 rounded-lg text-green-200 text-sm">
            {success}
          </div>
        )}

        {/* Files List */}
        {loading && files.length === 0 ? (
          <div className="text-center py-6 text-gray-400">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500 mx-auto mb-2"></div>
            <div className="text-sm">Loading files...</div>
          </div>
        ) : files.length === 0 ? (
          <div className="text-center py-6 text-gray-400">
            <div className="text-2xl mb-2">📄</div>
            <div className="text-sm">No files attached</div>
          </div>
        ) : (
          <div className="space-y-2">
            {files.map((file) => (
              <div 
                key={file.id} 
                className="flex items-center justify-between p-3 bg-gray-700 rounded-lg hover:bg-gray-650 transition-colors"
              >
                <div className="flex items-center space-x-3 flex-1 min-w-0">
                  <div className="text-xl">
                    {getFileIcon(file.mime_type)}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="text-white font-medium truncate text-sm">
                      {file.filename}
                    </div>
                    <div className="text-gray-400 text-xs flex items-center space-x-2">
                      <span>{getFileTypeDisplay(file.mime_type)}</span>
                      <span>•</span>
                      <span>{formatFileSize(file.file_size)}</span>
                      <span>•</span>
                      <span>{new Date(file.upload_date).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  {/* View/Download button */}
                  <button
                    className="p-2 text-gray-400 hover:text-white transition-colors"
                    title="View file"
                    onClick={() => setViewingFile(file)}
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  </button>
                  
                  {/* Delete button */}
                  <button
                    className="p-2 text-gray-400 hover:text-red-400 transition-colors"
                    title="Delete file"
                    onClick={() => handleDelete(file.id, file.filename)}
                    disabled={loading}
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* File Viewer Modal */}
      <FileViewer 
        resource={viewingFile}
        isOpen={!!viewingFile}
        onClose={() => setViewingFile(null)}
      />
    </div>
  );
};

export default FileAttachment;