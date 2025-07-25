import React, { useState, useEffect } from 'react';
import { X, Download, ZoomIn, ZoomOut, RotateCw } from 'lucide-react';
import { resourcesAPI } from '../services/api';

const FileViewer = ({ resource, isOpen, onClose }) => {
  const [fileContent, setFileContent] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [imageZoom, setImageZoom] = useState(1);
  const [imageRotation, setImageRotation] = useState(0);

  // Load file content when modal opens
  useEffect(() => {
    if (isOpen && resource) {
      loadFileContent();
    } else {
      // Reset state when modal closes
      setFileContent(null);
      setError('');
      setImageZoom(1);
      setImageRotation(0);
    }
  }, [isOpen, resource]);

  const loadFileContent = async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await resourcesAPI.getResourceContent(resource.id);
      setFileContent(response.data);
    } catch (err) {
      console.error('Error loading file content:', err);
      setError('Failed to load file content');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!fileContent) return;
    
    try {
      // Convert base64 to blob
      const byteCharacters = atob(fileContent.file_content);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: fileContent.mime_type });
      
      // Create download link
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = fileContent.filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Error downloading file:', err);
      setError('Failed to download file');
    }
  };

  const getDataUrl = () => {
    if (!fileContent) return '';
    return `data:${fileContent.mime_type};base64,${fileContent.file_content}`;
  };

  const renderFileContent = () => {
    if (loading) {
      return (
        <div className="flex items-center justify-center h-96">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-400"></div>
        </div>
      );
    }

    if (error) {
      return (
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <div className="text-red-400 mb-2">⚠️</div>
            <div className="text-red-400">{error}</div>
          </div>
        </div>
      );
    }

    if (!fileContent) return null;

    const { mime_type } = fileContent;

    // Handle Images
    if (mime_type.startsWith('image/')) {
      return (
        <div className="flex flex-col items-center">
          {/* Image Controls */}
          <div className="flex items-center space-x-2 mb-4">
            <button
              onClick={() => setImageZoom(Math.max(0.25, imageZoom - 0.25))}
              className="p-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-gray-300"
              title="Zoom Out"
            >
              <ZoomOut className="h-4 w-4" />
            </button>
            <span className="text-gray-300 text-sm">{Math.round(imageZoom * 100)}%</span>
            <button
              onClick={() => setImageZoom(Math.min(3, imageZoom + 0.25))}
              className="p-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-gray-300"
              title="Zoom In"
            >
              <ZoomIn className="h-4 w-4" />
            </button>
            <button
              onClick={() => setImageRotation((imageRotation + 90) % 360)}
              className="p-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-gray-300"
              title="Rotate"
            >
              <RotateCw className="h-4 w-4" />
            </button>
          </div>
          
          {/* Image Display */}
          <div className="overflow-auto max-h-96 bg-gray-800 rounded-lg p-4">
            <img
              src={getDataUrl()}
              alt={fileContent.filename}
              className="max-w-none"
              style={{
                transform: `scale(${imageZoom}) rotate(${imageRotation}deg)`,
                transformOrigin: 'center',
                transition: 'transform 0.2s ease'
              }}
            />
          </div>
        </div>
      );
    }

    // Handle PDFs
    if (mime_type === 'application/pdf') {
      return (
        <div className="h-96">
          <iframe
            src={getDataUrl()}
            className="w-full h-full border border-gray-700 rounded-lg"
            title={fileContent.filename}
          />
        </div>
      );
    }

    // Handle Text Files
    if (mime_type === 'text/plain') {
      try {
        const textContent = atob(fileContent.file_content);
        return (
          <div className="bg-gray-800 rounded-lg p-4 h-96 overflow-auto">
            <pre className="text-gray-300 text-sm whitespace-pre-wrap font-mono">
              {textContent}
            </pre>
          </div>
        );
      } catch (err) {
        return (
          <div className="text-center py-8">
            <div className="text-red-400 mb-2">⚠️</div>
            <div className="text-red-400">Unable to display text content</div>
          </div>
        );
      }
    }

    // Handle Other Files (DOC, DOCX, etc.) - Show download option
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">📄</div>
        <div className="text-gray-300 mb-4">
          <div className="font-medium">{fileContent.filename}</div>
          <div className="text-sm text-gray-400 mt-1">
            {(fileContent.file_size / 1024 / 1024).toFixed(2)} MB
          </div>
        </div>
        <div className="text-gray-400 mb-6">
          This file type cannot be previewed. Click download to view it.
        </div>
        <button
          onClick={handleDownload}
          className="inline-flex items-center space-x-2 px-6 py-3 bg-yellow-600 hover:bg-yellow-500 text-black rounded-lg font-medium transition-colors"
        >
          <Download className="h-4 w-4" />
          <span>Download File</span>
        </button>
      </div>
    );
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center p-4 z-50">
      <div className="bg-gray-900 rounded-xl w-full max-w-4xl max-h-[90vh] overflow-hidden border border-gray-800">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-800">
          <div className="flex items-center space-x-3">
            <div className="text-2xl">
              {resource?.mime_type?.startsWith('image/') ? '🖼️' : 
               resource?.mime_type === 'application/pdf' ? '📄' :
               resource?.mime_type?.includes('word') ? '📝' :
               resource?.mime_type === 'text/plain' ? '📄' : '📁'}
            </div>
            <div>
              <h2 className="text-xl font-semibold text-white">
                {resource?.filename}
              </h2>
              <div className="text-sm text-gray-400">
                {resource?.mime_type} • {((resource?.file_size || 0) / 1024 / 1024).toFixed(2)} MB
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={handleDownload}
              className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
              title="Download"
              disabled={!fileContent}
            >
              <Download className="h-5 w-5" />
            </button>
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
              title="Close"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-auto max-h-[calc(90vh-120px)]">
          {renderFileContent()}
        </div>
      </div>
    </div>
  );
};

export default FileViewer;