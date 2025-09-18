import React, { useState } from 'react';
import { 
  Paperclip, 
  Download, 
  Trash2, 
  Eye, 
  File, 
  Image, 
  Video, 
  Music, 
  Archive, 
  FileText,
  ExternalLink,
  MoreVertical
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Alert, AlertDescription } from '../ui/alert';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '../ui/dropdown-menu';
import { ProjectAttachment } from '../../types/enhanced-features';
import { useEnhancedFeaturesStore } from '../../stores/enhancedFeaturesStore';

interface ProjectAttachmentsViewProps {
  projectId: string;
  className?: string;
}

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

const formatDate = (date: Date): string => {
  return new Date(date).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const getFileTypeColor = (type: string): string => {
  if (type.startsWith('image/')) return 'bg-green-500/10 text-green-500 border-green-500/20';
  if (type.startsWith('video/')) return 'bg-purple-500/10 text-purple-500 border-purple-500/20';
  if (type.startsWith('audio/')) return 'bg-orange-500/10 text-orange-500 border-orange-500/20';
  if (type.includes('pdf')) return 'bg-red-500/10 text-red-500 border-red-500/20';
  if (type.includes('document') || type.includes('text')) return 'bg-blue-500/10 text-blue-500 border-blue-500/20';
  if (type.includes('zip') || type.includes('archive')) return 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20';
  return 'bg-gray-500/10 text-gray-500 border-gray-500/20';
};

export default function ProjectAttachmentsView({ projectId, className = '' }: ProjectAttachmentsViewProps) {
  const { getProjectAttachments, removeProjectAttachment } = useEnhancedFeaturesStore();
  const [deletingAttachment, setDeletingAttachment] = useState<string | null>(null);

  const attachments = getProjectAttachments(projectId);

  const handleDownload = (attachment: ProjectAttachment) => {
    // In a real implementation, this would download the file from storage
    // For now, we'll simulate a download action
    console.log('Downloading file:', attachment.fileName);
    
    // Create a simulated download
    const link = document.createElement('a');
    link.href = attachment.url || '#';
    link.download = attachment.originalName;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handlePreview = (attachment: ProjectAttachment) => {
    // In a real implementation, this would open a preview modal or new window
    if (attachment.url) {
      window.open(attachment.url, '_blank');
    } else {
      console.log('Preview not available for:', attachment.fileName);
    }
  };

  const handleDelete = async (attachment: ProjectAttachment) => {
    if (window.confirm(`Are you sure you want to delete "${attachment.originalName}"?`)) {
      setDeletingAttachment(attachment.id);
      try {
        removeProjectAttachment(projectId, attachment.id);
      } catch (error) {
        console.error('Error deleting attachment:', error);
      } finally {
        setDeletingAttachment(null);
      }
    }
  };

  if (attachments.length === 0) {
    return (
      <Card className={`glassmorphism-card border-0 ${className}`}>
        <CardContent className="p-6 text-center">
          <Paperclip className="w-12 h-12 mx-auto mb-3 text-muted-foreground/30" />
          <h3 className="font-medium mb-1">No attachments</h3>
          <p className="text-sm text-muted-foreground">
            Files uploaded to this project will appear here
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={`glassmorphism-card border-0 ${className}`}>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center space-x-2">
          <Paperclip className="w-5 h-5" />
          <span>Attachments ({attachments.length})</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {attachments.map((attachment) => {
          const FileIcon = getFileIcon(attachment.fileType);
          const fileTypeColor = getFileTypeColor(attachment.fileType);
          const isDeleting = deletingAttachment === attachment.id;

          return (
            <div
              key={attachment.id}
              className={`flex items-center space-x-3 p-3 rounded-lg border transition-all duration-200 ${
                isDeleting 
                  ? 'opacity-50 pointer-events-none' 
                  : 'border-border hover:border-primary/30 hover:bg-primary/5'
              }`}
            >
              {/* File Icon */}
              <div className="flex-shrink-0">
                {attachment.thumbnail ? (
                  <img 
                    src={attachment.thumbnail} 
                    alt={attachment.originalName}
                    className="w-10 h-10 object-cover rounded border"
                  />
                ) : (
                  <div className="w-10 h-10 flex items-center justify-center rounded glassmorphism-subtle">
                    <FileIcon className="w-5 h-5 text-muted-foreground" />
                  </div>
                )}
              </div>

              {/* File Info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2 mb-1">
                  <p className="font-medium truncate" title={attachment.originalName}>
                    {attachment.originalName}
                  </p>
                  <Badge 
                    variant="outline" 
                    className={`text-xs ${fileTypeColor}`}
                  >
                    {attachment.fileType.split('/')[1].toUpperCase()}
                  </Badge>
                </div>
                <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                  <span>{formatFileSize(attachment.fileSize)}</span>
                  <span>•</span>
                  <span>Uploaded {formatDate(attachment.uploadedAt)}</span>
                  {attachment.uploadedBy && (
                    <>
                      <span>•</span>
                      <span>by {attachment.uploadedBy}</span>
                    </>
                  )}
                </div>
              </div>

              {/* Actions */}
              <div className="flex-shrink-0">
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-8 w-8 p-0"
                      disabled={isDeleting}
                    >
                      <MoreVertical className="w-4 h-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="glassmorphism-card border-0 bg-card">
                    <DropdownMenuItem 
                      onClick={() => handlePreview(attachment)}
                      className="flex items-center space-x-2"
                    >
                      <Eye className="w-4 h-4" />
                      <span>Preview</span>
                    </DropdownMenuItem>
                    <DropdownMenuItem 
                      onClick={() => handleDownload(attachment)}
                      className="flex items-center space-x-2"
                    >
                      <Download className="w-4 h-4" />
                      <span>Download</span>
                    </DropdownMenuItem>
                    {attachment.url && (
                      <DropdownMenuItem 
                        onClick={() => window.open(attachment.url, '_blank')}
                        className="flex items-center space-x-2"
                      >
                        <ExternalLink className="w-4 h-4" />
                        <span>Open in new tab</span>
                      </DropdownMenuItem>
                    )}
                    <DropdownMenuItem 
                      onClick={() => handleDelete(attachment)}
                      className="flex items-center space-x-2 text-destructive focus:text-destructive"
                    >
                      <Trash2 className="w-4 h-4" />
                      <span>Delete</span>
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </div>
          );
        })}

        {/* Storage Info */}
        <div className="pt-3 border-t border-border">
          <div className="text-xs text-muted-foreground">
            Total: {formatFileSize(attachments.reduce((sum, att) => sum + att.fileSize, 0))}
            {' • '}
            {attachments.length} file{attachments.length !== 1 ? 's' : ''}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}