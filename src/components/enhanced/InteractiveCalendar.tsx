import { useState, useMemo, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Input } from '../ui/input';
import { Progress } from '../ui/progress';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '../ui/collapsible';
import { 
  Calendar, 
  ChevronLeft, 
  ChevronRight, 
  Filter, 
  Plus, 
  Search,
  Target,
  Folder,
  FolderKanban,
  CheckSquare,
  Clock,
  Users,
  AlertCircle,
  X,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import CalendarViews from './CalendarViews';
import EventModal from './EventModal';
import QuickEventCreator from './QuickEventCreator';

// Types for calendar events and filters
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

interface FilterState {
  pillars: string[];
  areas: string[];
  projects: string[];
  types: string[];
  searchQuery: string;
}

interface CalendarProps {
  className?: string;
}

// Mock data for demonstration
const mockPillars = [
  { id: '1', name: 'Health & Fitness', color: '#10B981', eventCount: 12 },
  { id: '2', name: 'Career Growth', color: '#3B82F6', eventCount: 18 },
  { id: '3', name: 'Relationships', color: '#EF4444', eventCount: 8 },
  { id: '4', name: 'Personal Finance', color: '#F59E0B', eventCount: 6 },
  { id: '5', name: 'Learning & Growth', color: '#8B5CF6', eventCount: 15 }
];

const mockAreas = [
  { id: '1', name: 'Training', pillarId: '1', eventCount: 8 },
  { id: '2', name: 'Nutrition', pillarId: '1', eventCount: 4 },
  { id: '3', name: 'Skills Development', pillarId: '2', eventCount: 12 },
  { id: '4', name: 'Leadership', pillarId: '2', eventCount: 6 },
  { id: '5', name: 'Family Time', pillarId: '3', eventCount: 5 },
  { id: '6', name: 'Friendships', pillarId: '3', eventCount: 3 },
];

const mockProjects = [
  { id: '1', name: '30-Day Running Challenge', areaId: '1', status: 'active', progress: 75 },
  { id: '2', name: 'Meal Prep System', areaId: '2', status: 'active', progress: 60 },
  { id: '3', name: 'React Certification', areaId: '3', status: 'active', progress: 85 },
  { id: '4', name: 'Team Leadership Course', areaId: '4', status: 'active', progress: 40 },
];

const mockEvents: CalendarEvent[] = [
  {
    id: '1',
    title: 'Morning Run - 5K',
    startTime: new Date(2024, 11, 15, 6, 0),
    endTime: new Date(2024, 11, 15, 7, 0),
    type: 'task',
    pillarId: '1',
    pillarName: 'Health & Fitness',
    pillarColor: '#10B981',
    areaId: '1',
    areaName: 'Training',
    projectId: '1',
    projectName: '30-Day Running Challenge',
    priority: 'high',
    status: 'pending'
  },
  {
    id: '2',
    title: 'React Component Review',
    startTime: new Date(2024, 11, 15, 9, 0),
    endTime: new Date(2024, 11, 15, 10, 30),
    type: 'meeting',
    pillarId: '2',
    pillarName: 'Career Growth',
    pillarColor: '#3B82F6',
    areaId: '3',
    areaName: 'Skills Development',
    projectId: '3',
    projectName: 'React Certification',
    priority: 'high',
    status: 'pending',
    attendees: ['John Doe', 'Jane Smith']
  },
  {
    id: '3',
    title: 'Family Dinner',
    startTime: new Date(2024, 11, 15, 18, 0),
    endTime: new Date(2024, 11, 15, 19, 30),
    type: 'event',
    pillarId: '3',
    pillarName: 'Relationships',
    pillarColor: '#EF4444',
    areaId: '5',
    areaName: 'Family Time',
    priority: 'medium',
    status: 'pending'
  },
  {
    id: '4',
    title: 'Investment Portfolio Review',
    startTime: new Date(2024, 11, 16, 14, 0),
    endTime: new Date(2024, 11, 16, 15, 0),
    type: 'deadline',
    pillarId: '4',
    pillarName: 'Personal Finance',
    pillarColor: '#F59E0B',
    priority: 'high',
    status: 'pending'
  }
];

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

export default function InteractiveCalendar({ className = '' }: CalendarProps) {
  const [view, setView] = useState<'day' | 'week' | 'month'>('day');
  const [currentDate, setCurrentDate] = useState(new Date());
  const [showFilters, setShowFilters] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState<CalendarEvent | null>(null);
  const [showEventModal, setShowEventModal] = useState(false);
  const [showQuickCreator, setShowQuickCreator] = useState(false);
  const [selectedTimeSlot, setSelectedTimeSlot] = useState<{ date: Date; hour: number } | null>(null);
  const [expandedFilterSections, setExpandedFilterSections] = useState({
    pillars: true,
    areas: false,
    projects: false,
    quickFilters: true
  });
  
  const [filters, setFilters] = useState<FilterState>({
    pillars: [],
    areas: [],
    projects: [],
    types: ['task', 'event', 'meeting', 'deadline', 'reminder'],
    searchQuery: ''
  });

  // Filter logic
  const filteredEvents = useMemo(() => {
    return mockEvents.filter(event => {
      // Pillar filter
      if (filters.pillars.length > 0 && !filters.pillars.includes(event.pillarId)) {
        return false;
      }
      
      // Area filter
      if (filters.areas.length > 0 && event.areaId && !filters.areas.includes(event.areaId)) {
        return false;
      }
      
      // Project filter
      if (filters.projects.length > 0 && event.projectId && !filters.projects.includes(event.projectId)) {
        return false;
      }
      
      // Type filter
      if (!filters.types.includes(event.type)) {
        return false;
      }
      
      // Search query
      if (filters.searchQuery && !event.title.toLowerCase().includes(filters.searchQuery.toLowerCase())) {
        return false;
      }
      
      return true;
    });
  }, [filters]);

  // Get available areas based on selected pillars
  const availableAreas = useMemo(() => {
    if (filters.pillars.length === 0) return mockAreas;
    return mockAreas.filter(area => filters.pillars.includes(area.pillarId));
  }, [filters.pillars]);

  // Get available projects based on selected areas
  const availableProjects = useMemo(() => {
    if (filters.areas.length === 0) return mockProjects;
    return mockProjects.filter(project => filters.areas.includes(project.areaId));
  }, [filters.areas]);

  // Active filter count
  const activeFilterCount = useMemo(() => {
    let count = 0;
    if (filters.pillars.length > 0) count++;
    if (filters.areas.length > 0) count++;
    if (filters.projects.length > 0) count++;
    if (filters.types.length < 5) count++; // Not all types selected
    if (filters.searchQuery) count++;
    return count;
  }, [filters]);

  // Navigation handlers
  const navigateDate = useCallback((direction: 'prev' | 'next') => {
    const newDate = new Date(currentDate);
    
    if (view === 'day') {
      newDate.setDate(newDate.getDate() + (direction === 'next' ? 1 : -1));
    } else if (view === 'week') {
      newDate.setDate(newDate.getDate() + (direction === 'next' ? 7 : -7));
    } else if (view === 'month') {
      newDate.setMonth(newDate.getMonth() + (direction === 'next' ? 1 : -1));
    }
    
    setCurrentDate(newDate);
  }, [currentDate, view]);

  const goToToday = useCallback(() => {
    setCurrentDate(new Date());
  }, []);

  // Filter handlers
  const togglePillarFilter = useCallback((pillarId: string) => {
    setFilters(prev => ({
      ...prev,
      pillars: prev.pillars.includes(pillarId)
        ? prev.pillars.filter(id => id !== pillarId)
        : [...prev.pillars, pillarId]
    }));
  }, []);

  const toggleAreaFilter = useCallback((areaId: string) => {
    setFilters(prev => ({
      ...prev,
      areas: prev.areas.includes(areaId)
        ? prev.areas.filter(id => id !== areaId)
        : [...prev.areas, areaId]
    }));
  }, []);

  const toggleProjectFilter = useCallback((projectId: string) => {
    setFilters(prev => ({
      ...prev,
      projects: prev.projects.includes(projectId)
        ? prev.projects.filter(id => id !== projectId)
        : [...prev.projects, projectId]
    }));
  }, []);

  const toggleTypeFilter = useCallback((type: string) => {
    setFilters(prev => ({
      ...prev,
      types: prev.types.includes(type)
        ? prev.types.filter(t => t !== type)
        : [...prev.types, type]
    }));
  }, []);

  const clearAllFilters = useCallback(() => {
    setFilters({
      pillars: [],
      areas: [],
      projects: [],
      types: ['task', 'event', 'meeting', 'deadline', 'reminder'],
      searchQuery: ''
    });
  }, []);

  const removeFilter = useCallback((type: string, value: string) => {
    setFilters(prev => ({
      ...prev,
      [type]: prev[type as keyof FilterState].filter((item: any) => item !== value)
    }));
  }, []);

  // Format date for display
  const formatDateDisplay = useCallback(() => {
    const options: Intl.DateTimeFormatOptions = 
      view === 'day' 
        ? { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }
        : view === 'week'
        ? { year: 'numeric', month: 'long', day: 'numeric' }
        : { year: 'numeric', month: 'long' };
    
    return currentDate.toLocaleDateString('en-US', options);
  }, [currentDate, view]);

  const toggleFilterSection = useCallback((section: keyof typeof expandedFilterSections) => {
    setExpandedFilterSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  }, []);

  // Event handlers
  const handleEventClick = useCallback((event: CalendarEvent) => {
    setSelectedEvent(event);
    setShowEventModal(true);
  }, []);

  const handleTimeSlotClick = useCallback((date: Date, hour: number) => {
    setSelectedTimeSlot({ date, hour });
    setShowQuickCreator(true);
  }, []);

  const handleEventEdit = useCallback((event: CalendarEvent) => {
    // This would open an edit modal
    console.log('Edit event:', event);
    setShowEventModal(false);
  }, []);

  const handleEventDelete = useCallback((eventId: string) => {
    // This would delete the event
    console.log('Delete event:', eventId);
    setShowEventModal(false);
  }, []);

  const handleEventDuplicate = useCallback((event: CalendarEvent) => {
    // This would duplicate the event
    console.log('Duplicate event:', event);
    setShowEventModal(false);
  }, []);

  const handleEventComplete = useCallback((eventId: string) => {
    // This would mark the event as completed
    console.log('Complete event:', eventId);
    setShowEventModal(false);
  }, []);

  const handleCreateEvent = useCallback((eventData: any) => {
    // This would add the event to the events list
    console.log('Create new event:', eventData);
    setShowQuickCreator(false);
  }, []);

  return (
    <Card className={`glassmorphism-card border-0 ${className}`}>
      <CardHeader className="pb-4">
        {/* Calendar Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <CardTitle className="text-white text-xl">Life Calendar</CardTitle>
          
          <div className="flex items-center gap-2">
            {/* Filter Toggle */}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowFilters(!showFilters)}
              className={`text-[#B8BCC8] hover:text-[#F4D03F] ${activeFilterCount > 0 ? 'bg-[rgba(244,208,63,0.1)]' : ''}`}
            >
              <Filter className="w-4 h-4 mr-2" />
              Filters {activeFilterCount > 0 && `(${activeFilterCount})`}
            </Button>
            
            {/* Add Event Button */}
            <Button 
              className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
              onClick={() => {
                setSelectedTimeSlot({ date: currentDate, hour: 9 });
                setShowQuickCreator(true);
              }}
            >
              <Plus className="w-4 h-4 mr-2" />
              Add Event
            </Button>
          </div>
        </div>

        {/* View Controls and Navigation */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mt-4">
          {/* View Toggle */}
          <div className="flex items-center bg-[rgba(244,208,63,0.1)] rounded-lg p-1">
            {(['day', 'week', 'month'] as const).map((viewOption) => (
              <Button
                key={viewOption}
                size="sm"
                variant={view === viewOption ? "default" : "ghost"}
                onClick={() => setView(viewOption)}
                className={view === viewOption 
                  ? "bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]" 
                  : "text-[#B8BCC8] hover:text-[#F4D03F]"
                }
              >
                {viewOption.charAt(0).toUpperCase() + viewOption.slice(1)}
              </Button>
            ))}
          </div>

          {/* Date Navigation */}
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigateDate('prev')}
              className="text-[#B8BCC8] hover:text-[#F4D03F]"
            >
              <ChevronLeft className="w-4 h-4" />
            </Button>
            
            <Button
              variant="ghost"
              onClick={goToToday}
              className="text-white hover:text-[#F4D03F] min-w-[120px] text-center"
            >
              {formatDateDisplay()}
            </Button>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigateDate('next')}
              className="text-[#B8BCC8] hover:text-[#F4D03F]"
            >
              <ChevronRight className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Filter Panel */}
        <AnimatePresence>
          {showFilters && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.2 }}
              className="filter-panel bg-[rgba(255,255,255,0.05)] border border-[rgba(244,208,63,0.1)] rounded-lg p-4 space-y-4"
            >
              {/* Search */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-[#B8BCC8]" />
                <Input
                  placeholder="Search events..."
                  value={filters.searchQuery}
                  onChange={(e) => setFilters(prev => ({ ...prev, searchQuery: e.target.value }))}
                  className="pl-10 bg-[rgba(255,255,255,0.05)] border-[rgba(244,208,63,0.2)] text-white placeholder:text-[#6B7280]"
                />
              </div>

              {/* Pillar Filters */}
              <Collapsible 
                open={expandedFilterSections.pillars} 
                onOpenChange={() => toggleFilterSection('pillars')}
              >
                <CollapsibleTrigger asChild>
                  <Button variant="ghost" className="w-full justify-between text-[#B8BCC8] hover:text-[#F4D03F]">
                    <div className="flex items-center">
                      <Target className="w-4 h-4 mr-2" />
                      Filter by Life Pillars
                    </div>
                    {expandedFilterSections.pillars ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </Button>
                </CollapsibleTrigger>
                <CollapsibleContent className="space-y-2 mt-2">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {mockPillars.map(pillar => (
                      <Button
                        key={pillar.id}
                        variant="ghost"
                        onClick={() => togglePillarFilter(pillar.id)}
                        className={`pillar-filter-chip justify-start h-auto p-3 ${
                          filters.pillars.includes(pillar.id)
                            ? 'bg-[rgba(244,208,63,0.2)] border-[#F4D03F] transform scale-[1.02]'
                            : 'bg-[rgba(255,255,255,0.05)] border-[rgba(255,255,255,0.1)] hover:bg-[rgba(244,208,63,0.1)]'
                        }`}
                        style={{ borderLeft: `4px solid ${pillar.color}` }}
                      >
                        <div className="flex items-center justify-between w-full">
                          <span className="text-white font-medium">{pillar.name}</span>
                          <Badge variant="outline" className="border-[rgba(244,208,63,0.3)] text-[#B8BCC8] text-xs">
                            {pillar.eventCount}
                          </Badge>
                        </div>
                      </Button>
                    ))}
                  </div>
                </CollapsibleContent>
              </Collapsible>

              {/* Area Filters */}
              <Collapsible 
                open={expandedFilterSections.areas} 
                onOpenChange={() => toggleFilterSection('areas')}
              >
                <CollapsibleTrigger asChild>
                  <Button variant="ghost" className="w-full justify-between text-[#B8BCC8] hover:text-[#F4D03F]">
                    <div className="flex items-center">
                      <Folder className="w-4 h-4 mr-2" />
                      Filter by Areas
                    </div>
                    {expandedFilterSections.areas ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </Button>
                </CollapsibleTrigger>
                <CollapsibleContent className="space-y-2 mt-2">
                  <div className="space-y-1 ml-4">
                    {availableAreas.map(area => {
                      const parentPillar = mockPillars.find(p => p.id === area.pillarId);
                      return (
                        <Button
                          key={area.id}
                          variant="ghost"
                          onClick={() => toggleAreaFilter(area.id)}
                          className={`justify-start h-auto p-2 w-full ${
                            filters.areas.includes(area.id)
                              ? 'bg-[rgba(244,208,63,0.2)] text-[#F4D03F]'
                              : 'text-[#B8BCC8] hover:text-[#F4D03F]'
                          }`}
                        >
                          <div className="flex items-center justify-between w-full">
                            <span className="text-sm">{area.name}</span>
                            <Badge variant="outline" className="border-[rgba(244,208,63,0.3)] text-[#6B7280] text-xs">
                              {area.eventCount}
                            </Badge>
                          </div>
                        </Button>
                      );
                    })}
                  </div>
                </CollapsibleContent>
              </Collapsible>

              {/* Project Filters */}
              <Collapsible 
                open={expandedFilterSections.projects} 
                onOpenChange={() => toggleFilterSection('projects')}
              >
                <CollapsibleTrigger asChild>
                  <Button variant="ghost" className="w-full justify-between text-[#B8BCC8] hover:text-[#F4D03F]">
                    <div className="flex items-center">
                      <FolderKanban className="w-4 h-4 mr-2" />
                      Filter by Projects
                    </div>
                    {expandedFilterSections.projects ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </Button>
                </CollapsibleTrigger>
                <CollapsibleContent className="space-y-2 mt-2">
                  <div className="space-y-1 ml-4">
                    {availableProjects.map(project => (
                      <Button
                        key={project.id}
                        variant="ghost"
                        onClick={() => toggleProjectFilter(project.id)}
                        className={`justify-start h-auto p-2 w-full ${
                          filters.projects.includes(project.id)
                            ? 'bg-[rgba(244,208,63,0.2)] text-[#F4D03F]'
                            : 'text-[#B8BCC8] hover:text-[#F4D03F]'
                        }`}
                      >
                        <div className="flex items-center justify-between w-full">
                          <div className="flex-1 text-left">
                            <div className="text-sm">{project.name}</div>
                            <Progress value={project.progress} className="h-1 mt-1" />
                          </div>
                          <Badge 
                            variant="outline" 
                            className={`border-[rgba(244,208,63,0.3)] text-xs ml-2 ${
                              project.status === 'active' ? 'text-[#10B981]' : 'text-[#6B7280]'
                            }`}
                          >
                            {project.status}
                          </Badge>
                        </div>
                      </Button>
                    ))}
                  </div>
                </CollapsibleContent>
              </Collapsible>

              {/* Quick Filters */}
              <Collapsible 
                open={expandedFilterSections.quickFilters} 
                onOpenChange={() => toggleFilterSection('quickFilters')}
              >
                <CollapsibleTrigger asChild>
                  <Button variant="ghost" className="w-full justify-between text-[#B8BCC8] hover:text-[#F4D03F]">
                    <div className="flex items-center">
                      <Filter className="w-4 h-4 mr-2" />
                      Quick Filters
                    </div>
                    {expandedFilterSections.quickFilters ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </Button>
                </CollapsibleTrigger>
                <CollapsibleContent className="space-y-2 mt-2">
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(eventTypeIcons).map(([type, IconComponent]) => (
                      <Button
                        key={type}
                        variant="ghost"
                        size="sm"
                        onClick={() => toggleTypeFilter(type)}
                        className={`quick-filter-chip ${
                          filters.types.includes(type)
                            ? 'bg-[#F4D03F] text-[#1a1d29] font-semibold'
                            : 'bg-[rgba(255,255,255,0.05)] border border-[rgba(255,255,255,0.1)] text-[#B8BCC8] hover:bg-[rgba(244,208,63,0.1)]'
                        }`}
                      >
                        <IconComponent className="w-3 h-3 mr-1" />
                        {type.charAt(0).toUpperCase() + type.slice(1)}
                      </Button>
                    ))}
                  </div>
                </CollapsibleContent>
              </Collapsible>

              {/* Clear Filters */}
              {activeFilterCount > 0 && (
                <div className="flex justify-end">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={clearAllFilters}
                    className="text-[#EF4444] hover:text-[#F87171]"
                  >
                    Clear All Filters
                  </Button>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Active Filter Chips */}
        {activeFilterCount > 0 && (
          <div className="flex flex-wrap gap-2">
            {filters.pillars.map(pillarId => {
              const pillar = mockPillars.find(p => p.id === pillarId);
              return pillar ? (
                <Badge
                  key={pillarId}
                  variant="outline"
                  className="active-filter-chip bg-[rgba(244,208,63,0.2)] border-[#F4D03F] text-[#F4D03F]"
                >
                  {pillar.name}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeFilter('pillars', pillarId)}
                    className="ml-2 h-4 w-4 p-0 hover:bg-transparent"
                  >
                    <X className="w-3 h-3" />
                  </Button>
                </Badge>
              ) : null;
            })}
            
            {filters.areas.map(areaId => {
              const area = mockAreas.find(a => a.id === areaId);
              return area ? (
                <Badge
                  key={areaId}
                  variant="outline"
                  className="active-filter-chip bg-[rgba(244,208,63,0.2)] border-[#F4D03F] text-[#F4D03F]"
                >
                  {area.name}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeFilter('areas', areaId)}
                    className="ml-2 h-4 w-4 p-0 hover:bg-transparent"
                  >
                    <X className="w-3 h-3" />
                  </Button>
                </Badge>
              ) : null;
            })}

            {filters.searchQuery && (
              <Badge
                variant="outline"
                className="active-filter-chip bg-[rgba(244,208,63,0.2)] border-[#F4D03F] text-[#F4D03F]"
              >
                Search: "{filters.searchQuery}"
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setFilters(prev => ({ ...prev, searchQuery: '' }))}
                  className="ml-2 h-4 w-4 p-0 hover:bg-transparent"
                >
                  <X className="w-3 h-3" />
                </Button>
              </Badge>
            )}
          </div>
        )}

        {/* Calendar Views */}
        <CalendarViews
          view={view}
          currentDate={currentDate}
          events={filteredEvents}
          onEventClick={handleEventClick}
          onTimeSlotClick={handleTimeSlotClick}
        />

        {/* Results Summary */}
        {filteredEvents.length > 0 && (
          <div className="text-center text-sm text-[#6B7280] pt-2 border-t border-[rgba(244,208,63,0.1)]">
            Showing {filteredEvents.length} of {mockEvents.length} events
            {activeFilterCount > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={clearAllFilters}
                className="ml-2 text-[#F4D03F] hover:text-[#F7DC6F]"
              >
                View all events
              </Button>
            )}
          </div>
        )}
      </CardContent>

      {/* Event Modal */}
      <EventModal
        event={selectedEvent}
        isOpen={showEventModal}
        onClose={() => setShowEventModal(false)}
        onEdit={handleEventEdit}
        onDelete={handleEventDelete}
        onDuplicate={handleEventDuplicate}
        onComplete={handleEventComplete}
      />

      {/* Quick Event Creator */}
      <QuickEventCreator
        isOpen={showQuickCreator}
        onClose={() => setShowQuickCreator(false)}
        selectedDate={selectedTimeSlot?.date || null}
        selectedHour={selectedTimeSlot?.hour}
        onCreateEvent={handleCreateEvent}
      />
    </Card>
  );
}