import React, { useState, useCallback } from 'react';
import { Upload, X, File, Image, Video, Music, Archive, FileText, AlertTriangle, Check } from 'lucide-react';
import { Button } from '../ui/button';
import { Progress } from '../ui/progress';
import { Alert, AlertDescription } from '../ui/alert';
import { Badge } from '../ui/badge';

export interface FileUploadConfig {
  maxFileSize: number; // in MB
  maxFiles: number;
  allowedTypes: string[]; // MIME types
  allowedExtensions: string[]; // file extensions
}

export interface UploadedFile {
  id: string;
  file: File;
  name: string;
  size: number;
  type: string;
  uploadProgress: number;
  uploaded: boolean;
  error?: string;
  preview?: string; // for images
}

interface FileUploadProps {
  config: FileUploadConfig;
  onFilesUploaded: (files: UploadedFile[]) => void;
  onFileRemoved: (fileId: string) => void;
  existingFiles?: UploadedFile[];
  disabled?: boolean;
  className?: string;
}

const DEFAULT_CONFIG: FileUploadConfig = {
  maxFileSize: 10, // 10MB
  maxFiles: 5,
  allowedTypes: [
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp',
    'application/pdf',
    'text/plain',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/zip',
    'application/x-zip-compressed'
  ],
  allowedExtensions: ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.pdf', '.txt', '.doc', '.docx', '.xls', '.xlsx', '.zip']
};

const getFileIcon = (type: string) => {
  if (type.startsWith('image/')) return Image;
  if (type.startsWith('video/')) return Video;
  if (type.startsWith('audio/')) return Music;
  if (type.includes('pdf') || type.includes('document') || type.includes('text')) return FileText;
  if (type.includes('zip') || type.includes('archive')) return Archive;
  return File;
};

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const validateFile = (file: File, config: FileUploadConfig): string | null => {
  // Check file size
  const maxSizeBytes = config.maxFileSize * 1024 * 1024;
  if (file.size > maxSizeBytes) {
    return `File size exceeds ${config.maxFileSize}MB limit`;
  }

  // Check file type
  if (!config.allowedTypes.includes(file.type)) {
    const extension = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!config.allowedExtensions.includes(extension)) {
      return 'File type not supported';
    }
  }

  return null;
};

export default function FileUpload({
  config = DEFAULT_CONFIG,
  onFilesUploaded,
  onFileRemoved,
  existingFiles = [],
  disabled = false,
  className = ''
}: FileUploadProps) {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>(existingFiles);
  const [dragActive, setDragActive] = useState(false);
  const [errors, setErrors] = useState<string[]>([]);

  const createFilePreview = (file: File): Promise<string | undefined> => {
    return new Promise((resolve) => {
      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target?.result as string);
        reader.readAsDataURL(file);
      } else {
        resolve(undefined);
      }
    });
  };

  const simulateUpload = (file: UploadedFile): Promise<void> => {
    return new Promise((resolve) => {
      let progress = 0;
      const interval = setInterval(() => {
        progress += Math.random() * 30;
        if (progress >= 100) {
          progress = 100;
          clearInterval(interval);
          setUploadedFiles(files => 
            files.map(f => 
              f.id === file.id 
                ? { ...f, uploadProgress: 100, uploaded: true }
                : f
            )
          );
          resolve();
        } else {
          setUploadedFiles(files => 
            files.map(f => 
              f.id === file.id 
                ? { ...f, uploadProgress: progress }
                : f
            )
          );
        }
      }, 200);
    });
  };

  const handleFiles = useCallback(async (files: FileList) => {
    const newErrors: string[] = [];
    const validFiles: UploadedFile[] = [];

    // Check total file count
    if (uploadedFiles.length + files.length > config.maxFiles) {
      newErrors.push(`Maximum ${config.maxFiles} files allowed`);
      setErrors(newErrors);
      return;
    }

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const validationError = validateFile(file, config);
      
      if (validationError) {
        newErrors.push(`${file.name}: ${validationError}`);
        continue;
      }

      // Check for duplicates
      if (uploadedFiles.some(f => f.name === file.name && f.size === file.size)) {
        newErrors.push(`${file.name}: File already exists`);
        continue;
      }

      const preview = await createFilePreview(file);
      
      const uploadedFile: UploadedFile = {
        id: crypto.randomUUID(),
        file,
        name: file.name,
        size: file.size,
        type: file.type,
        uploadProgress: 0,
        uploaded: false,
        preview
      };

      validFiles.push(uploadedFile);
    }

    if (validFiles.length > 0) {
      setUploadedFiles(prev => [...prev, ...validFiles]);
      
      // Simulate upload for each file
      validFiles.forEach(file => {
        simulateUpload(file);
      });

      onFilesUploaded([...uploadedFiles, ...validFiles]);
    }

    setErrors(newErrors);
  }, [uploadedFiles, config, onFilesUploaded]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    
    if (disabled) return;
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files);
    }
  }, [handleFiles, disabled]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    if (!disabled) {
      setDragActive(true);
    }
  }, [disabled]);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
  }, []);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFiles(e.target.files);
    }
  };

  const removeFile = (fileId: string) => {
    setUploadedFiles(files => files.filter(f => f.id !== fileId));
    onFileRemoved(fileId);
  };

  const clearErrors = () => {
    setErrors([]);
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Upload Area */}
      <div
        className={`
          relative border-2 border-dashed rounded-lg p-6 text-center transition-colors
          ${dragActive ? 'border-primary bg-primary/5' : 'border-border'}
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:border-primary/50'}
        `}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => !disabled && document.getElementById('file-upload')?.click()}
      >
        <input
          id="file-upload"
          type="file"
          multiple
          accept={config.allowedTypes.join(',')}
          onChange={handleFileInput}
          disabled={disabled}
          className="hidden"
        />
        
        <Upload className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
        <h3 className="text-lg font-medium mb-2">
          {dragActive ? 'Drop files here' : 'Upload files'}
        </h3>
        <p className="text-sm text-muted-foreground mb-4">
          Drag and drop files here, or click to browse
        </p>
        
        {/* File restrictions */}
        <div className="text-xs text-muted-foreground space-y-1">
          <p>Maximum {config.maxFiles} files, {config.maxFileSize}MB each</p>
          <p>Supported: {config.allowedExtensions.slice(0, 5).join(', ')}
            {config.allowedExtensions.length > 5 && ` +${config.allowedExtensions.length - 5} more`}
          </p>
        </div>
      </div>

      {/* Error Messages */}
      {errors.length > 0 && (
        <Alert className="border-destructive/50 text-destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            <div className="space-y-1">
              {errors.map((error, index) => (
                <div key={index}>{error}</div>
              ))}
            </div>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={clearErrors}
              className="mt-2 h-6 px-2 text-xs"
            >
              Dismiss
            </Button>
          </AlertDescription>
        </Alert>
      )}

      {/* Uploaded Files */}
      {uploadedFiles.length > 0 && (
        <div className="space-y-3">
          <h4 className="font-medium">Uploaded Files ({uploadedFiles.length})</h4>
          <div className="space-y-2">
            {uploadedFiles.map((file) => {
              const FileIcon = getFileIcon(file.type);
              
              return (
                <div key={file.id} className="flex items-center space-x-3 p-3 rounded-lg border border-border">
                  {/* File Icon/Preview */}
                  <div className="flex-shrink-0">
                    {file.preview ? (
                      <img 
                        src={file.preview} 
                        alt={file.name}
                        className="w-10 h-10 object-cover rounded"
                      />
                    ) : (
                      <div className="w-10 h-10 flex items-center justify-center rounded bg-muted">
                        <FileIcon className="w-5 h-5" />
                      </div>
                    )}
                  </div>
                  
                  {/* File Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2">
                      <p className="text-sm font-medium truncate">{file.name}</p>
                      {file.uploaded ? (
                        <Check className="w-4 h-4 text-green-500" />
                      ) : (
                        <div className="w-4 h-4 animate-spin rounded-full border-2 border-primary border-t-transparent" />
                      )}
                    </div>
                    <div className="flex items-center space-x-2 mt-1">
                      <Badge variant="secondary" className="text-xs">
                        {formatFileSize(file.size)}
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        {file.type.split('/')[1].toUpperCase()}
                      </span>
                    </div>
                    
                    {/* Progress Bar */}
                    {!file.uploaded && (
                      <Progress 
                        value={file.uploadProgress} 
                        className="w-full h-1 mt-2"
                      />
                    )}
                    
                    {file.error && (
                      <p className="text-xs text-destructive mt-1">{file.error}</p>
                    )}
                  </div>
                  
                  {/* Remove Button */}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeFile(file.id)}
                    className="h-8 w-8 p-0"
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}