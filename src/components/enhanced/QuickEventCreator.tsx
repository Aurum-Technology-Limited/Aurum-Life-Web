import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '../ui/dialog';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Badge } from '../ui/badge';
import { 
  Calendar, 
  Clock, 
  CheckSquare, 
  Users, 
  AlertCircle,
  Plus
} from 'lucide-react';

interface QuickEventCreatorProps {
  isOpen: boolean;
  onClose: () => void;
  selectedDate: Date | null;
  selectedHour?: number;
  onCreateEvent: (eventData: any) => void;
}

const eventTypes = [
  { value: 'task', label: 'Task', icon: CheckSquare, color: '#10B981' },
  { value: 'event', label: 'Event', icon: Calendar, color: '#3B82F6' },
  { value: 'meeting', label: 'Meeting', icon: Users, color: '#8B5CF6' },
  { value: 'deadline', label: 'Deadline', icon: AlertCircle, color: '#EF4444' },
  { value: 'reminder', label: 'Reminder', icon: Clock, color: '#F59E0B' }
];

const mockPillars = [
  { id: '1', name: 'Health & Fitness', color: '#10B981' },
  { id: '2', name: 'Career Growth', color: '#3B82F6' },
  { id: '3', name: 'Relationships', color: '#EF4444' },
  { id: '4', name: 'Personal Finance', color: '#F59E0B' },
  { id: '5', name: 'Learning & Growth', color: '#8B5CF6' }
];

const durations = [
  { value: 15, label: '15 minutes' },
  { value: 30, label: '30 minutes' },
  { value: 45, label: '45 minutes' },
  { value: 60, label: '1 hour' },
  { value: 90, label: '1.5 hours' },
  { value: 120, label: '2 hours' }
];

export default function QuickEventCreator({
  isOpen,
  onClose,
  selectedDate,
  selectedHour = 9,
  onCreateEvent
}: QuickEventCreatorProps) {
  const [title, setTitle] = useState('');
  const [type, setType] = useState('task');
  const [pillarId, setPillarId] = useState('');
  const [duration, setDuration] = useState(60);
  const [priority, setPriority] = useState('medium');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!title.trim() || !selectedDate || !pillarId) return;

    const startTime = new Date(selectedDate);
    startTime.setHours(selectedHour, 0, 0, 0);
    
    const endTime = new Date(startTime);
    endTime.setMinutes(endTime.getMinutes() + duration);

    const selectedPillar = mockPillars.find(p => p.id === pillarId);

    const eventData = {
      id: `event_${Date.now()}`,
      title: title.trim(),
      startTime,
      endTime,
      type,
      pillarId,
      pillarName: selectedPillar?.name || '',
      pillarColor: selectedPillar?.color || '#F4D03F',
      priority,
      status: 'pending'
    };

    onCreateEvent(eventData);
    handleClose();
  };

  const handleClose = () => {
    setTitle('');
    setType('task');
    setPillarId('');
    setDuration(60);
    setPriority('medium');
    onClose();
  };

  const selectedEventType = eventTypes.find(t => t.value === type);
  const formatDateTime = () => {
    if (!selectedDate) return '';
    return `${selectedDate.toLocaleDateString('en-US', { 
      weekday: 'long', 
      month: 'short', 
      day: 'numeric' 
    })} at ${selectedHour.toString().padStart(2, '0')}:00`;
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="glassmorphism-card border-0 bg-[#1A1D29] text-white max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center text-white">
            <Plus className="w-5 h-5 mr-2 text-[#F4D03F]" />
            Quick Add Event
          </DialogTitle>
          <DialogDescription className="text-[#B8BCC8] text-sm">
            {selectedDate ? formatDateTime() : 'Create a new event for your Life Calendar'}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Title */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-[#B8BCC8]">Title</label>
            <Input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Enter event title..."
              className="bg-[rgba(255,255,255,0.05)] border-[rgba(244,208,63,0.2)] text-white placeholder:text-[#6B7280]"
              required
            />
          </div>

          {/* Event Type */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-[#B8BCC8]">Type</label>
            <div className="grid grid-cols-5 gap-2">
              {eventTypes.map((eventType) => {
                const IconComponent = eventType.icon;
                return (
                  <Button
                    key={eventType.value}
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => setType(eventType.value)}
                    className={`flex flex-col items-center p-2 h-auto ${
                      type === eventType.value
                        ? 'bg-[rgba(244,208,63,0.2)] border border-[#F4D03F]'
                        : 'bg-[rgba(255,255,255,0.05)] hover:bg-[rgba(244,208,63,0.1)]'
                    }`}
                  >
                    <IconComponent 
                      className="w-4 h-4 mb-1" 
                      style={{ color: eventType.color }}
                    />
                    <span className="text-xs">{eventType.label}</span>
                  </Button>
                );
              })}
            </div>
          </div>

          {/* Pillar */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-[#B8BCC8]">Life Pillar</label>
            <Select value={pillarId} onValueChange={setPillarId} required>
              <SelectTrigger className="bg-[rgba(255,255,255,0.05)] border-[rgba(244,208,63,0.2)] text-white">
                <SelectValue placeholder="Select a pillar..." />
              </SelectTrigger>
              <SelectContent className="glassmorphism-card border-0 bg-[#1A1D29]">
                {mockPillars.map((pillar) => (
                  <SelectItem 
                    key={pillar.id} 
                    value={pillar.id}
                    className="text-white hover:bg-[rgba(244,208,63,0.1)]"
                  >
                    <div className="flex items-center">
                      <div 
                        className="w-3 h-3 rounded-full mr-2"
                        style={{ backgroundColor: pillar.color }}
                      />
                      {pillar.name}
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            {/* Duration */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-[#B8BCC8]">Duration</label>
              <Select value={duration.toString()} onValueChange={(value) => setDuration(parseInt(value))}>
                <SelectTrigger className="bg-[rgba(255,255,255,0.05)] border-[rgba(244,208,63,0.2)] text-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="glassmorphism-card border-0 bg-[#1A1D29]">
                  {durations.map((dur) => (
                    <SelectItem 
                      key={dur.value} 
                      value={dur.value.toString()}
                      className="text-white hover:bg-[rgba(244,208,63,0.1)]"
                    >
                      {dur.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Priority */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-[#B8BCC8]">Priority</label>
              <Select value={priority} onValueChange={setPriority}>
                <SelectTrigger className="bg-[rgba(255,255,255,0.05)] border-[rgba(244,208,63,0.2)] text-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="glassmorphism-card border-0 bg-[#1A1D29]">
                  <SelectItem value="low" className="text-white hover:bg-[rgba(244,208,63,0.1)]">
                    <div className="flex items-center">
                      <div className="w-2 h-2 rounded-full bg-[#6B7280] mr-2" />
                      Low
                    </div>
                  </SelectItem>
                  <SelectItem value="medium" className="text-white hover:bg-[rgba(244,208,63,0.1)]">
                    <div className="flex items-center">
                      <div className="w-2 h-2 rounded-full bg-[#F59E0B] mr-2" />
                      Medium
                    </div>
                  </SelectItem>
                  <SelectItem value="high" className="text-white hover:bg-[rgba(244,208,63,0.1)]">
                    <div className="flex items-center">
                      <div className="w-2 h-2 rounded-full bg-[#EF4444] mr-2" />
                      High
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Preview */}
          <div className="p-3 rounded-lg bg-[rgba(244,208,63,0.05)] border border-[rgba(244,208,63,0.1)]">
            <div className="text-xs text-[#B8BCC8] mb-2">Preview:</div>
            <div className="flex items-center space-x-2">
              {selectedEventType && (
                <selectedEventType.icon 
                  className="w-4 h-4" 
                  style={{ color: selectedEventType.color }}
                />
              )}
              <span className="text-white text-sm font-medium">
                {title || 'Untitled Event'}
              </span>
              <Badge 
                variant="outline" 
                className="border-[rgba(244,208,63,0.3)] text-[#F4D03F] text-xs"
              >
                {duration}min
              </Badge>
            </div>
          </div>

          {/* Actions */}
          <div className="flex space-x-2 pt-2">
            <Button
              type="button"
              variant="ghost"
              onClick={handleClose}
              className="flex-1 text-[#B8BCC8] hover:text-white"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              className="flex-1 bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
              disabled={!title.trim() || !pillarId}
            >
              Create Event
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}