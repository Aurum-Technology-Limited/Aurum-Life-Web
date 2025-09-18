import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '../ui/dialog';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { 
  Calendar, 
  Clock, 
  MapPin, 
  Users, 
  CheckSquare, 
  AlertCircle, 
  Edit, 
  Trash2,
  Copy,
  X
} from 'lucide-react';

interface CalendarEvent {
  id: string;
  title: string;
  description?: string;
  startTime: Date;
  endTime: Date;
  type: 'task' | 'event' | 'meeting' | 'deadline' | 'reminder';
  pillarId: string;
  pillarName: string;
  pillarColor: string;
  areaId?: string;
  areaName?: string;
  projectId?: string;
  projectName?: string;
  priority: 'low' | 'medium' | 'high';
  status: 'pending' | 'in-progress' | 'completed' | 'cancelled';
  isRecurring?: boolean;
  location?: string;
  attendees?: string[];
}

interface EventModalProps {
  event: CalendarEvent | null;
  isOpen: boolean;
  onClose: () => void;
  onEdit?: (event: CalendarEvent) => void;
  onDelete?: (eventId: string) => void;
  onDuplicate?: (event: CalendarEvent) => void;
  onComplete?: (eventId: string) => void;
}

const eventTypeIcons = {
  task: CheckSquare,
  event: Calendar,
  meeting: Users,
  deadline: AlertCircle,
  reminder: Clock
};

const eventTypeColors = {
  task: '#10B981',
  event: '#3B82F6',
  meeting: '#8B5CF6',
  deadline: '#EF4444',
  reminder: '#F59E0B'
};

const priorityColors = {
  low: '#6B7280',
  medium: '#F59E0B',
  high: '#EF4444'
};

const statusColors = {
  pending: '#F59E0B',
  'in-progress': '#3B82F6',
  completed: '#10B981',
  cancelled: '#6B7280'
};

export default function EventModal({
  event,
  isOpen,
  onClose,
  onEdit,
  onDelete,
  onDuplicate,
  onComplete
}: EventModalProps) {
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  if (!event) return null;

  const EventIcon = eventTypeIcons[event.type];
  const duration = Math.round((event.endTime.getTime() - event.startTime.getTime()) / (1000 * 60));
  const formatTime = (date: Date) => date.toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit',
    hour12: true 
  });
  const formatDate = (date: Date) => date.toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });

  const handleDelete = () => {
    if (showDeleteConfirm) {
      onDelete?.(event.id);
      onClose();
    } else {
      setShowDeleteConfirm(true);
    }
  };

  const handleComplete = () => {
    onComplete?.(event.id);
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="glassmorphism-card border-0 bg-[#1A1D29] text-white max-w-2xl">
        <DialogHeader className="space-y-4">
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-4">
              <div 
                className="w-12 h-12 rounded-lg flex items-center justify-center"
                style={{ backgroundColor: `${eventTypeColors[event.type]}20` }}
              >
                <EventIcon 
                  className="w-6 h-6" 
                  style={{ color: eventTypeColors[event.type] }}
                />
              </div>
              <div className="flex-1">
                <DialogTitle className="text-xl text-white mb-2">{event.title}</DialogTitle>
                <DialogDescription className="text-muted-foreground text-sm">
                  Event details for {event.title}, scheduled for {formatDate(event.startTime)} from {formatTime(event.startTime)} to {formatTime(event.endTime)}
                </DialogDescription>
                <div className="flex items-center space-x-2">
                  <Badge 
                    variant="outline" 
                    className="border-[rgba(244,208,63,0.3)] text-[#F4D03F]"
                  >
                    {event.type.charAt(0).toUpperCase() + event.type.slice(1)}
                  </Badge>
                  <Badge 
                    variant="outline"
                    style={{ 
                      borderColor: `${priorityColors[event.priority]}50`,
                      color: priorityColors[event.priority]
                    }}
                  >
                    {event.priority.charAt(0).toUpperCase() + event.priority.slice(1)} Priority
                  </Badge>
                  <Badge 
                    variant="outline"
                    style={{ 
                      borderColor: `${statusColors[event.status]}50`,
                      color: statusColors[event.status]
                    }}
                  >
                    {event.status.charAt(0).toUpperCase() + event.status.slice(1)}
                  </Badge>
                </div>
              </div>
            </div>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={onClose}
              className="text-[#B8BCC8] hover:text-white"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
        </DialogHeader>

        <div className="space-y-6">
          {/* Event Details */}
          <div className="space-y-4">
            {/* Date and Time */}
            <div className="flex items-center space-x-3">
              <Calendar className="w-5 h-5 text-[#F4D03F]" />
              <div>
                <div className="text-white font-medium">{formatDate(event.startTime)}</div>
                <div className="text-[#B8BCC8] text-sm">
                  {formatTime(event.startTime)} - {formatTime(event.endTime)} ({duration} minutes)
                </div>
              </div>
            </div>

            {/* Location */}
            {event.location && (
              <div className="flex items-center space-x-3">
                <MapPin className="w-5 h-5 text-[#F4D03F]" />
                <div className="text-white">{event.location}</div>
              </div>
            )}

            {/* Attendees */}
            {event.attendees && event.attendees.length > 0 && (
              <div className="flex items-start space-x-3">
                <Users className="w-5 h-5 text-[#F4D03F] mt-1" />
                <div>
                  <div className="text-white font-medium mb-1">Attendees ({event.attendees.length})</div>
                  <div className="space-y-1">
                    {event.attendees.map((attendee, index) => (
                      <div key={index} className="text-[#B8BCC8] text-sm">{attendee}</div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Description */}
            {event.description && (
              <div className="space-y-2">
                <h4 className="text-white font-medium">Description</h4>
                <p className="text-[#B8BCC8] text-sm leading-relaxed">{event.description}</p>
              </div>
            )}
          </div>

          {/* Hierarchy Information */}
          <div className="space-y-3 p-4 rounded-lg bg-[rgba(244,208,63,0.05)] border border-[rgba(244,208,63,0.1)]">
            <h4 className="text-white font-medium flex items-center">
              <div 
                className="w-3 h-3 rounded-full mr-2"
                style={{ backgroundColor: event.pillarColor }}
              />
              Life Framework
            </h4>
            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-[#B8BCC8]">Pillar:</span>
                <Badge 
                  variant="outline" 
                  className="border-[rgba(244,208,63,0.3)]"
                  style={{ color: event.pillarColor }}
                >
                  {event.pillarName}
                </Badge>
              </div>
              {event.areaName && (
                <div className="flex items-center justify-between">
                  <span className="text-[#B8BCC8]">Area:</span>
                  <span className="text-white">{event.areaName}</span>
                </div>
              )}
              {event.projectName && (
                <div className="flex items-center justify-between">
                  <span className="text-[#B8BCC8]">Project:</span>
                  <span className="text-white">{event.projectName}</span>
                </div>
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-between pt-4 border-t border-[rgba(244,208,63,0.1)]">
            <div className="flex space-x-2">
              {event.status !== 'completed' && event.type === 'task' && (
                <Button 
                  size="sm" 
                  className="bg-[#10B981] text-white hover:bg-[#059669]"
                  onClick={handleComplete}
                >
                  <CheckSquare className="w-4 h-4 mr-2" />
                  Mark Complete
                </Button>
              )}
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => onDuplicate?.(event)}
                className="text-[#B8BCC8] hover:text-[#F4D03F]"
              >
                <Copy className="w-4 h-4 mr-2" />
                Duplicate
              </Button>
            </div>
            
            <div className="flex space-x-2">
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => onEdit?.(event)}
                className="text-[#B8BCC8] hover:text-[#F4D03F]"
              >
                <Edit className="w-4 h-4 mr-2" />
                Edit
              </Button>
              <Button 
                variant="ghost" 
                size="sm"
                onClick={handleDelete}
                className={showDeleteConfirm 
                  ? "text-[#EF4444] hover:text-[#F87171] bg-[rgba(239,68,68,0.1)]" 
                  : "text-[#B8BCC8] hover:text-[#EF4444]"
                }
              >
                <Trash2 className="w-4 h-4 mr-2" />
                {showDeleteConfirm ? 'Confirm Delete' : 'Delete'}
              </Button>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}