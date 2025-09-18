import { ReactNode } from 'react';
import { Button } from '../ui/button';
import { Card, CardContent } from '../ui/card';

interface EmptyStateProps {
  icon: ReactNode;
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
  className?: string;
}

export default function EmptyState({
  icon,
  title,
  description,
  actionLabel,
  onAction,
  className = '',
}: EmptyStateProps) {
  return (
    <Card className={`glassmorphism-card border-0 ${className}`}>
      <CardContent className="flex flex-col items-center justify-center py-16 text-center space-y-6">
        <div className="w-20 h-20 rounded-full bg-[rgba(244,208,63,0.1)] flex items-center justify-center">
          <div className="text-[#F4D03F]">
            {icon}
          </div>
        </div>
        
        <div className="space-y-2">
          <h3 className="text-xl font-semibold text-white">{title}</h3>
          <p className="text-[#B8BCC8] text-sm max-w-md">
            {description}
          </p>
        </div>

        {actionLabel && onAction && (
          <Button 
            onClick={onAction}
            className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
          >
            {actionLabel}
          </Button>
        )}
      </CardContent>
    </Card>
  );
}