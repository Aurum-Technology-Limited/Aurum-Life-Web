import { useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { 
  Calendar, 
  CheckSquare, 
  Clock, 
  Target, 
  TrendingUp,
  AlertCircle
} from 'lucide-react';

interface CalendarEvent {
  id: string;
  title: string;
  startTime: Date;
  endTime: Date;
  type: 'task' | 'event' | 'meeting' | 'deadline' | 'reminder';
  pillarId: string;
  pillarName: string;
  pillarColor: string;
  priority: 'low' | 'medium' | 'high';
  status: 'pending' | 'in-progress' | 'completed' | 'cancelled';
}

interface CalendarSummaryProps {
  events: CalendarEvent[];
  currentDate: Date;
  view: 'day' | 'week' | 'month';
  className?: string;
}

export default function CalendarSummary({
  events,
  currentDate,
  view,
  className = ''
}: CalendarSummaryProps) {
  const stats = useMemo(() => {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    
    // Filter events based on current view
    let viewEvents = events;
    if (view === 'day') {
      viewEvents = events.filter(event => {
        const eventDate = new Date(event.startTime.getFullYear(), event.startTime.getMonth(), event.startTime.getDate());
        const currentDateOnly = new Date(currentDate.getFullYear(), currentDate.getMonth(), currentDate.getDate());
        return eventDate.getTime() === currentDateOnly.getTime();
      });
    } else if (view === 'week') {
      const weekStart = new Date(currentDate);
      weekStart.setDate(currentDate.getDate() - currentDate.getDay());
      const weekEnd = new Date(weekStart);
      weekEnd.setDate(weekStart.getDate() + 6);
      
      viewEvents = events.filter(event => {
        const eventDate = new Date(event.startTime.getFullYear(), event.startTime.getMonth(), event.startTime.getDate());
        return eventDate >= weekStart && eventDate <= weekEnd;
      });
    } else if (view === 'month') {
      viewEvents = events.filter(event => {
        return event.startTime.getMonth() === currentDate.getMonth() &&
               event.startTime.getFullYear() === currentDate.getFullYear();
      });
    }

    const totalEvents = viewEvents.length;
    const completedEvents = viewEvents.filter(e => e.status === 'completed').length;
    const pendingEvents = viewEvents.filter(e => e.status === 'pending').length;
    const highPriorityEvents = viewEvents.filter(e => e.priority === 'high').length;
    const overdueEvents = viewEvents.filter(e => 
      e.status !== 'completed' && 
      e.startTime < now &&
      e.type === 'deadline'
    ).length;

    // Group by type
    const typeStats = {
      task: viewEvents.filter(e => e.type === 'task').length,
      event: viewEvents.filter(e => e.type === 'event').length,
      meeting: viewEvents.filter(e => e.type === 'meeting').length,
      deadline: viewEvents.filter(e => e.type === 'deadline').length,
      reminder: viewEvents.filter(e => e.type === 'reminder').length,
    };

    // Group by pillar
    const pillarStats = viewEvents.reduce((acc, event) => {
      const existing = acc.find(p => p.id === event.pillarId);
      if (existing) {
        existing.count++;
        if (event.status === 'completed') existing.completed++;
      } else {
        acc.push({
          id: event.pillarId,
          name: event.pillarName,
          color: event.pillarColor,
          count: 1,
          completed: event.status === 'completed' ? 1 : 0
        });
      }
      return acc;
    }, [] as Array<{ id: string; name: string; color: string; count: number; completed: number }>);

    const completionRate = totalEvents > 0 ? Math.round((completedEvents / totalEvents) * 100) : 0;

    return {
      totalEvents,
      completedEvents,
      pendingEvents,
      highPriorityEvents,
      overdueEvents,
      completionRate,
      typeStats,
      pillarStats
    };
  }, [events, currentDate, view]);

  const getViewLabel = () => {
    switch (view) {
      case 'day':
        return currentDate.toLocaleDateString('en-US', { 
          weekday: 'long', 
          month: 'short', 
          day: 'numeric' 
        });
      case 'week':
        const weekStart = new Date(currentDate);
        weekStart.setDate(currentDate.getDate() - currentDate.getDay());
        const weekEnd = new Date(weekStart);
        weekEnd.setDate(weekStart.getDate() + 6);
        return `${weekStart.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${weekEnd.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`;
      case 'month':
        return currentDate.toLocaleDateString('en-US', { 
          month: 'long', 
          year: 'numeric' 
        });
      default:
        return '';
    }
  };

  if (stats.totalEvents === 0) {
    return (
      <Card className={`glassmorphism-card border-0 ${className}`}>
        <CardContent className="p-4 text-center">
          <Calendar className="w-8 h-8 text-[#6B7280] mx-auto mb-2" />
          <p className="text-[#B8BCC8] text-sm">No events for {getViewLabel()}</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={`glassmorphism-card border-0 ${className}`}>
      <CardHeader className="pb-3">
        <CardTitle className="text-white text-lg flex items-center">
          <TrendingUp className="w-5 h-5 mr-2 text-[#F4D03F]" />
          {view.charAt(0).toUpperCase() + view.slice(1)} Summary
        </CardTitle>
        <p className="text-[#B8BCC8] text-sm">{getViewLabel()}</p>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Overall Progress */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-[#B8BCC8] text-sm">Completion Rate</span>
            <span className="text-[#F4D03F] font-semibold">{stats.completionRate}%</span>
          </div>
          <Progress value={stats.completionRate} className="h-2" />
          <div className="flex justify-between text-xs text-[#6B7280]">
            <span>{stats.completedEvents} completed</span>
            <span>{stats.pendingEvents} pending</span>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 gap-3">
          <div className="p-2 rounded-lg bg-[rgba(244,208,63,0.05)] border border-[rgba(244,208,63,0.1)]">
            <div className="flex items-center">
              <Target className="w-4 h-4 text-[#F4D03F] mr-2" />
              <span className="text-[#B8BCC8] text-sm">Total</span>
            </div>
            <div className="text-white font-bold text-lg">{stats.totalEvents}</div>
          </div>

          <div className="p-2 rounded-lg bg-[rgba(239,68,68,0.1)] border border-[rgba(239,68,68,0.2)]">
            <div className="flex items-center">
              <AlertCircle className="w-4 h-4 text-[#EF4444] mr-2" />
              <span className="text-[#B8BCC8] text-sm">High Priority</span>
            </div>
            <div className="text-white font-bold text-lg">{stats.highPriorityEvents}</div>
          </div>
        </div>

        {/* Overdue Alert */}
        {stats.overdueEvents > 0 && (
          <div className="p-3 rounded-lg bg-[rgba(239,68,68,0.1)] border border-[rgba(239,68,68,0.3)]">
            <div className="flex items-center">
              <AlertCircle className="w-4 h-4 text-[#EF4444] mr-2" />
              <span className="text-[#EF4444] font-medium text-sm">
                {stats.overdueEvents} overdue deadline{stats.overdueEvents > 1 ? 's' : ''}
              </span>
            </div>
          </div>
        )}

        {/* Event Types Breakdown */}
        <div className="space-y-2">
          <h4 className="text-[#B8BCC8] text-sm font-medium">Event Types</h4>
          <div className="space-y-1">
            {Object.entries(stats.typeStats).filter(([_, count]) => count > 0).map(([type, count]) => (
              <div key={type} className="flex items-center justify-between text-sm">
                <span className="text-[#B8BCC8] capitalize">{type}s</span>
                <Badge variant="outline" className="border-[rgba(244,208,63,0.3)] text-[#F4D03F] text-xs">
                  {count}
                </Badge>
              </div>
            ))}
          </div>
        </div>

        {/* Pillar Breakdown */}
        {stats.pillarStats.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-[#B8BCC8] text-sm font-medium">By Life Pillar</h4>
            <div className="space-y-2">
              {stats.pillarStats.slice(0, 3).map((pillar) => (
                <div key={pillar.id} className="space-y-1">
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center">
                      <div 
                        className="w-3 h-3 rounded-full mr-2"
                        style={{ backgroundColor: pillar.color }}
                      />
                      <span className="text-[#B8BCC8] truncate">{pillar.name}</span>
                    </div>
                    <span className="text-[#F4D03F] text-xs">
                      {pillar.completed}/{pillar.count}
                    </span>
                  </div>
                  <Progress 
                    value={pillar.count > 0 ? (pillar.completed / pillar.count) * 100 : 0} 
                    className="h-1" 
                  />
                </div>
              ))}
              {stats.pillarStats.length > 3 && (
                <div className="text-center text-xs text-[#6B7280]">
                  +{stats.pillarStats.length - 3} more pillars
                </div>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}