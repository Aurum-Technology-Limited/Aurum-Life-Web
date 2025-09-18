import { AlertDialog, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '../ui/alert-dialog';
import { Button } from '../ui/button';
import { Trash2, AlertTriangle } from 'lucide-react';

interface DeleteConfirmModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  itemName: string;
  type: 'pillar' | 'area' | 'project' | 'task';
  childrenCount?: number;
  isLoading?: boolean;
}

export default function DeleteConfirmModal({
  isOpen,
  onClose,
  onConfirm,
  title,
  itemName,
  type,
  childrenCount = 0,
  isLoading = false,
}: DeleteConfirmModalProps) {
  const getChildrenText = () => {
    if (childrenCount === 0) return null;
    
    switch (type) {
      case 'pillar':
        return `This will also delete ${childrenCount} area${childrenCount !== 1 ? 's' : ''} and all their projects and tasks.`;
      case 'area':
        return `This will also delete ${childrenCount} project${childrenCount !== 1 ? 's' : ''} and all their tasks.`;
      case 'project':
        return `This will also delete ${childrenCount} task${childrenCount !== 1 ? 's' : ''}.`;
      default:
        return null;
    }
  };

  const childrenText = getChildrenText();

  return (
    <AlertDialog open={isOpen} onOpenChange={onClose}>
      <AlertDialogContent className="glassmorphism-card border-0 bg-[#1A1D29] text-white">
        <AlertDialogHeader>
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 rounded-full bg-destructive/20 flex items-center justify-center">
              <AlertTriangle className="w-6 h-6 text-destructive" />
            </div>
            <div>
              <AlertDialogTitle className="text-left">
                Delete {type.charAt(0).toUpperCase() + type.slice(1)}
              </AlertDialogTitle>
              <AlertDialogDescription className="text-left text-[#B8BCC8]">
                {title}
              </AlertDialogDescription>
            </div>
          </div>
        </AlertDialogHeader>

        <div className="py-4">
          <div className="glassmorphism-panel p-4 rounded-lg">
            <div className="flex items-center space-x-3 mb-3">
              <Trash2 className="w-5 h-5 text-destructive" />
              <span className="font-semibold text-white">"{itemName}"</span>
            </div>
            
            <p className="text-[#B8BCC8] text-sm mb-3">
              This action cannot be undone. This will permanently delete the {type} and remove all associated data.
            </p>

            {childrenText && (
              <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-3">
                <p className="text-destructive text-sm font-medium">
                  ⚠️ Warning: {childrenText}
                </p>
              </div>
            )}
          </div>
        </div>

        <AlertDialogFooter>
          <Button 
            variant="outline" 
            onClick={onClose}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button 
            variant="destructive" 
            onClick={onConfirm}
            disabled={isLoading}
            className="bg-destructive hover:bg-destructive/90"
          >
            {isLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" />
                Deleting...
              </>
            ) : (
              <>
                <Trash2 className="w-4 h-4 mr-2" />
                Delete {type.charAt(0).toUpperCase() + type.slice(1)}
              </>
            )}
          </Button>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}