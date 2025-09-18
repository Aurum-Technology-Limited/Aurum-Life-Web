import { useMemo } from 'react';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { 
  CheckSquare, 
  Calendar, 
  Users, 
  AlertCircle, 
  Clock,
  MoreHorizontal 
} from 'lucide-react';
import { motion } from 'motion/react';

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

interface CalendarViewsProps {
  view: 'day' | 'week' | 'month';
  currentDate: Date;
  events: CalendarEvent[];
  onEventClick?: (event: CalendarEvent) => void;
  onTimeSlotClick?: (date: Date, hour: number) => void;
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

// Helper functions
const formatTime = (date: Date) => {
  return date.toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit',
    hour12: false 
  });
};

const isSameDay = (date1: Date, date2: Date) => {
  return date1.getDate() === date2.getDate() &&
         date1.getMonth() === date2.getMonth() &&
         date1.getFullYear() === date2.getFullYear();
};

const getWeekDays = (date: Date) => {
  const week = [];
  const startOfWeek = new Date(date);
  const day = startOfWeek.getDay();
  const diff = startOfWeek.getDate() - day;
  startOfWeek.setDate(diff);

  for (let i = 0; i < 7; i++) {
    const day = new Date(startOfWeek);
    day.setDate(startOfWeek.getDate() + i);
    week.push(day);
  }
  return week;
};

const getMonthDays = (date: Date) => {
  const year = date.getFullYear();
  const month = date.getMonth();
  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);
  const startDate = new Date(firstDay);
  const endDate = new Date(lastDay);
  
  // Adjust to show full weeks
  startDate.setDate(startDate.getDate() - startDate.getDay());
  endDate.setDate(endDate.getDate() + (6 - endDate.getDay()));
  
  const days = [];
  const currentDate = new Date(startDate);
  
  while (currentDate <= endDate) {
    days.push(new Date(currentDate));
    currentDate.setDate(currentDate.getDate() + 1);
  }
  
  return days;
};

// Event component
const EventCard = ({ 
  event, 
  onClick, 
  compact = false 
}: { 
  event: CalendarEvent; 
  onClick?: () => void;
  compact?: boolean;
}) => {
  const EventIcon = eventTypeIcons[event.type];
  
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.02, y: -1 }}
      className={`p-2 rounded-lg cursor-pointer transition-all ${
        compact ? 'mb-1' : 'mb-2'
      } bg-[rgba(244,208,63,0.05)] hover:bg-[rgba(244,208,63,0.1)] border-l-4`}
      style={{ borderLeftColor: event.pillarColor }}
      onClick={onClick}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-2 flex-1 min-w-0">
          <div 
            className={`${compact ? 'w-4 h-4' : 'w-6 h-6'} rounded flex items-center justify-center flex-shrink-0`}
            style={{ backgroundColor: `${eventTypeColors[event.type]}20` }}
          >
            <EventIcon 
              className={`${compact ? 'w-2 h-2' : 'w-3 h-3'}`}
              style={{ color: eventTypeColors[event.type] }}
            />
          </div>
          <div className="flex-1 min-w-0">
            <h4 className={`text-white font-medium truncate ${compact ? 'text-xs' : 'text-sm'}`}>
              {event.title}
            </h4>
            <div className={`flex items-center space-x-2 ${compact ? 'text-xs' : 'text-xs'} text-[#B8BCC8] mt-1`}>
              <span className="text-[#F4D03F] font-mono">
                {formatTime(event.startTime)}
              </span>
              {!compact && (
                <>
                  <span>•</span>
                  <span>{event.pillarName}</span>
                </>
              )}
              {event.priority === 'high' && (
                <Badge className="bg-[#EF4444] text-white text-xs px-1 py-0">!</Badge>
              )}
            </div>
            {!compact && event.projectName && (
              <div className="text-xs text-[#6B7280] mt-1 truncate">
                📋 {event.projectName}
              </div>
            )}
          </div>
        </div>
        <div 
          className={`${compact ? 'w-1 h-1' : 'w-2 h-2'} rounded-full flex-shrink-0 mt-1`}
          style={{ backgroundColor: event.pillarColor }}
        />
      </div>
    </motion.div>
  );
};

// Day View Component
const DayView = ({ currentDate, events, onEventClick, onTimeSlotClick }: Omit<CalendarViewsProps, 'view'>) => {
  const dayEvents = useMemo(() => {
    return events.filter(event => isSameDay(event.startTime, currentDate))
      .sort((a, b) => a.startTime.getTime() - b.startTime.getTime());
  }, [events, currentDate]);

  const hours = Array.from({ length: 24 }, (_, i) => i);

  return (
    <div className="calendar-day-view space-y-4">
      <div className="text-center mb-4">
        <h3 className="text-lg font-semibold text-white mb-2">
          {currentDate.toLocaleDateString('en-US', { 
            weekday: 'long', 
            month: 'long', 
            day: 'numeric' 
          })}
        </h3>
        <Badge variant="outline" className="border-[rgba(244,208,63,0.3)] text-[#F4D03F]">
          {dayEvents.length} events
        </Badge>
      </div>

      {dayEvents.length === 0 ? (
        <div className="text-center py-8">
          <Calendar className="w-12 h-12 text-[#6B7280] mx-auto mb-4" />
          <p className="text-[#B8BCC8]">No events scheduled for this day</p>
          <Button 
            size="sm" 
            className="mt-4 bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
            onClick={() => onTimeSlotClick?.(currentDate, 9)}
          >
            Add Event
          </Button>
        </div>
      ) : (
        <div className="space-y-2">
          {dayEvents.map(event => (
            <EventCard 
              key={event.id} 
              event={event} 
              onClick={() => onEventClick?.(event)}
            />
          ))}
        </div>
      )}

      {/* Time slots for scheduling */}
      <div className="mt-6 border-t border-[rgba(244,208,63,0.1)] pt-4">
        <h4 className="text-sm font-medium text-[#B8BCC8] mb-3">Available Time Slots</h4>
        <div className="grid grid-cols-4 gap-2">
          {[6, 9, 12, 15, 18, 21].map(hour => {
            const hasEvent = dayEvents.some(event => 
              event.startTime.getHours() === hour
            );
            
            return (
              <Button
                key={hour}
                variant="ghost"
                size="sm"
                disabled={hasEvent}
                onClick={() => onTimeSlotClick?.(currentDate, hour)}
                className={`text-xs ${
                  hasEvent 
                    ? 'opacity-50 cursor-not-allowed' 
                    : 'text-[#B8BCC8] hover:text-[#F4D03F] hover:bg-[rgba(244,208,63,0.1)]'
                }`}
              >
                {hour.toString().padStart(2, '0')}:00
              </Button>
            );
          })}
        </div>
      </div>
    </div>
  );
};

// Week View Component
const WeekView = ({ currentDate, events, onEventClick, onTimeSlotClick }: Omit<CalendarViewsProps, 'view'>) => {
  const weekDays = useMemo(() => getWeekDays(currentDate), [currentDate]);
  
  const weekEvents = useMemo(() => {
    return weekDays.map(day => ({
      date: day,
      events: events.filter(event => isSameDay(event.startTime, day))
        .sort((a, b) => a.startTime.getTime() - b.startTime.getTime())
    }));
  }, [events, weekDays]);

  const totalEvents = weekEvents.reduce((sum, day) => sum + day.events.length, 0);

  return (
    <div className="calendar-week-view space-y-4">
      <div className="text-center mb-4">
        <h3 className="text-lg font-semibold text-white mb-2">
          Week of {weekDays[0].toLocaleDateString('en-US', { month: 'long', day: 'numeric' })}
        </h3>
        <Badge variant="outline" className="border-[rgba(244,208,63,0.3)] text-[#F4D03F]">
          {totalEvents} events this week
        </Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-7 gap-4">
        {weekEvents.map(({ date, events: dayEvents }, index) => {
          const isToday = isSameDay(date, new Date());
          
          return (
            <div 
              key={index}
              className={`p-3 rounded-lg border transition-colors ${
                isToday 
                  ? 'bg-[rgba(244,208,63,0.1)] border-[rgba(244,208,63,0.3)]' 
                  : 'bg-[rgba(255,255,255,0.02)] border-[rgba(255,255,255,0.1)] hover:border-[rgba(244,208,63,0.2)]'
              }`}
            >
              <div className="text-center mb-3">
                <div className={`text-xs font-medium ${isToday ? 'text-[#F4D03F]' : 'text-[#B8BCC8]'}`}>
                  {date.toLocaleDateString('en-US', { weekday: 'short' })}
                </div>
                <div className={`text-lg font-bold ${isToday ? 'text-[#F4D03F]' : 'text-white'}`}>
                  {date.getDate()}
                </div>
              </div>
              
              <div className="space-y-1 min-h-[120px]">
                {dayEvents.length === 0 ? (
                  <div className="text-center py-4">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onTimeSlotClick?.(date, 9)}
                      className="text-xs text-[#6B7280] hover:text-[#F4D03F] w-full"
                    >
                      + Add event
                    </Button>
                  </div>
                ) : (
                  dayEvents.slice(0, 3).map(event => (
                    <EventCard 
                      key={event.id} 
                      event={event} 
                      compact={true}
                      onClick={() => onEventClick?.(event)}
                    />
                  ))
                )}
                
                {dayEvents.length > 3 && (
                  <Button
                    variant="ghost"
                    size="sm"
                    className="w-full text-xs text-[#6B7280] hover:text-[#F4D03F]"
                  >
                    +{dayEvents.length - 3} more
                  </Button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// Month View Component
const MonthView = ({ currentDate, events, onEventClick, onTimeSlotClick }: Omit<CalendarViewsProps, 'view'>) => {
  const monthDays = useMemo(() => getMonthDays(currentDate), [currentDate]);
  const currentMonth = currentDate.getMonth();
  
  const monthEvents = useMemo(() => {
    return monthDays.map(day => ({
      date: day,
      isCurrentMonth: day.getMonth() === currentMonth,
      events: events.filter(event => isSameDay(event.startTime, day))
        .sort((a, b) => a.startTime.getTime() - b.startTime.getTime())
    }));
  }, [events, monthDays, currentMonth]);

  const totalEvents = monthEvents
    .filter(day => day.isCurrentMonth)
    .reduce((sum, day) => sum + day.events.length, 0);

  return (
    <div className="calendar-month-view space-y-4">
      <div className="text-center mb-4">
        <h3 className="text-lg font-semibold text-white mb-2">
          {currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
        </h3>
        <Badge variant="outline" className="border-[rgba(244,208,63,0.3)] text-[#F4D03F]">
          {totalEvents} events this month
        </Badge>
      </div>

      {/* Week headers */}
      <div className="grid grid-cols-7 gap-2 mb-2">
        {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
          <div key={day} className="text-center text-xs font-medium text-[#B8BCC8] py-2">
            {day}
          </div>
        ))}
      </div>

      {/* Calendar grid */}
      <div className="grid grid-cols-7 gap-2">
        {monthEvents.map(({ date, isCurrentMonth, events: dayEvents }, index) => {
          const isToday = isSameDay(date, new Date());
          
          return (
            <div 
              key={index}
              className={`p-2 rounded-lg border min-h-[80px] transition-colors cursor-pointer ${
                !isCurrentMonth 
                  ? 'opacity-30 bg-[rgba(255,255,255,0.01)]' 
                  : isToday 
                  ? 'bg-[rgba(244,208,63,0.1)] border-[rgba(244,208,63,0.3)]' 
                  : 'bg-[rgba(255,255,255,0.02)] border-[rgba(255,255,255,0.1)] hover:border-[rgba(244,208,63,0.2)]'
              }`}
              onClick={() => onTimeSlotClick?.(date, 9)}
            >
              <div className={`text-right text-sm font-medium mb-1 ${
                !isCurrentMonth ? 'text-[#6B7280]' : isToday ? 'text-[#F4D03F]' : 'text-white'
              }`}>
                {date.getDate()}
              </div>
              
              <div className="space-y-1">
                {dayEvents.slice(0, 2).map(event => (
                  <div
                    key={event.id}
                    className="text-xs p-1 rounded truncate cursor-pointer hover:bg-[rgba(244,208,63,0.1)]"
                    style={{ backgroundColor: `${event.pillarColor}20`, color: event.pillarColor }}
                    onClick={(e) => {
                      e.stopPropagation();
                      onEventClick?.(event);
                    }}
                  >
                    {event.title}
                  </div>
                ))}
                
                {dayEvents.length > 2 && (
                  <div className="text-xs text-[#6B7280] text-center">
                    +{dayEvents.length - 2}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// Main Calendar Views Component
export default function CalendarViews({
  view,
  currentDate,
  events,
  onEventClick,
  onTimeSlotClick
}: CalendarViewsProps) {
  switch (view) {
    case 'day':
      return (
        <DayView 
          currentDate={currentDate}
          events={events}
          onEventClick={onEventClick}
          onTimeSlotClick={onTimeSlotClick}
        />
      );
    case 'week':
      return (
        <WeekView 
          currentDate={currentDate}
          events={events}
          onEventClick={onEventClick}
          onTimeSlotClick={onTimeSlotClick}
        />
      );
    case 'month':
      return (
        <MonthView 
          currentDate={currentDate}
          events={events}
          onEventClick={onEventClick}
          onTimeSlotClick={onTimeSlotClick}
        />
      );
    default:
      return null;
  }
}