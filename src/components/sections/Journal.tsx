import React, { useState, useEffect } from 'react';
import { 
  BookOpen, 
  Plus, 
  Calendar, 
  Search, 
  Filter, 
  Grid3X3, 
  List, 
  BarChart3,
  Settings,
  Eye,
  ChevronDown,
  SortAsc,
  SortDesc
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Input } from '../ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '../ui/dialog';
import { useJournalStore } from '../../stores/journalStore';
import { useEnhancedFeaturesStore } from '../../stores/enhancedFeaturesStore';
import JournalEntryModal from '../journal/JournalEntryModal';
import JournalAnalytics from '../journal/JournalAnalytics';
import TemplateSelector from '../journal/TemplateSelector';

export default function Journal() {
  const {
    getFilteredEntries,
    getStats,
    searchQuery,
    setSearchQuery,
    selectedMoodFilter,
    setMoodFilter,
    selectedPillarFilter,
    setPillarFilter,
    selectedTagFilter,
    setTagFilter,
    sortBy,
    setSortBy,
    sortOrder,
    setSortOrder,
    viewMode,
    setViewMode,
    openEntryModal,
    getAllTags,
    getMoodColors,
    generateInsights
  } = useJournalStore();

  const { pillars } = useEnhancedFeaturesStore();
  
  const [isTemplateModalOpen, setIsTemplateModalOpen] = useState(false);
  const [showFilters, setShowFilters] = useState(false);

  const entries = getFilteredEntries();
  const stats = getStats();
  const allTags = getAllTags();

  // Generate insights when component mounts or entries change
  useEffect(() => {
    generateInsights();
  }, [entries.length, generateInsights]);

  const handleCreateNewEntry = () => {
    setIsTemplateModalOpen(true);
  };

  const handleSelectTemplate = (template: any) => {
    setIsTemplateModalOpen(false);
    openEntryModal(undefined, template);
  };

  const handleCreateBlank = () => {
    setIsTemplateModalOpen(false);
    openEntryModal();
  };

  const formatDate = (date: Date) => {
    return new Date(date).toLocaleDateString('en-US', { 
      weekday: 'long', 
      month: 'short', 
      day: 'numeric',
      year: 'numeric'
    });
  };

  const formatTimeAgo = (date: Date) => {
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - new Date(date).getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return 'Today';
    if (diffDays === 2) return 'Yesterday';
    if (diffDays <= 7) return `${diffDays - 1} days ago`;
    if (diffDays <= 30) return `${Math.ceil(diffDays / 7)} weeks ago`;
    return `${Math.ceil(diffDays / 30)} months ago`;
  };

  const EntryCard = ({ entry }: { entry: any }) => {
    const moodColors = getMoodColors(entry.mood);
    const associatedPillar = entry.pillarId ? pillars.find(p => p.id === entry.pillarId) : null;

    return (
      <Card 
        className="glassmorphism-card border-0 cursor-pointer hover:scale-[1.02] transition-all duration-200"
        onClick={() => openEntryModal(entry)}
      >
        <CardContent className="p-4">
          <div className="flex items-start justify-between mb-3">
            <div className="flex items-center space-x-2">
              <Calendar className="w-4 h-4 text-primary" />
              <span className="text-sm text-muted-foreground">
                {formatTimeAgo(entry.date)}
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${moodColors.bg}`} />
              <span className={`text-xs font-medium capitalize ${moodColors.text}`}>
                {entry.mood}
              </span>
            </div>
          </div>
          
          <h3 className="font-semibold mb-2 line-clamp-2">{entry.title}</h3>
          <p className="text-muted-foreground text-sm mb-3 line-clamp-3">{entry.content}</p>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              {entry.tags.slice(0, 3).map((tag: string) => (
                <Badge 
                  key={tag}
                  variant="secondary"
                  className="text-xs glassmorphism-subtle"
                >
                  {tag}
                </Badge>
              ))}
              {entry.tags.length > 3 && (
                <Badge variant="secondary" className="text-xs">
                  +{entry.tags.length - 3}
                </Badge>
              )}
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-xs text-muted-foreground">{entry.wordCount} words</span>
              {associatedPillar && (
                <Badge 
                  variant="outline" 
                  className="text-xs border-primary/30 text-primary"
                >
                  {associatedPillar.name}
                </Badge>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold mb-2">Journal</h1>
          <p className="text-muted-foreground">Personal reflection and insights for continuous growth</p>
        </div>
        <Button 
          onClick={handleCreateNewEntry}
          className="bg-primary text-primary-foreground hover:bg-primary/90"
        >
          <Plus className="w-4 h-4 mr-2" />
          New Entry
        </Button>
      </div>

      <Tabs defaultValue="entries" className="w-full">
        <TabsList className="glassmorphism-card border-0 bg-card mb-6">
          <TabsTrigger value="entries" className="flex items-center space-x-2">
            <List className="w-4 h-4" />
            <span>Entries ({entries.length})</span>
          </TabsTrigger>
          <TabsTrigger value="analytics" className="flex items-center space-x-2">
            <BarChart3 className="w-4 h-4" />
            <span>Analytics</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="entries" className="space-y-6">
          {/* Search and Filters */}
          <Card className="glassmorphism-card border-0">
            <CardContent className="p-4">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground" />
                    <Input
                      placeholder="Search entries..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-9 glassmorphism-card border-0 bg-input"
                    />
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowFilters(!showFilters)}
                    className="glassmorphism-card border-0"
                  >
                    <Filter className="w-4 h-4 mr-2" />
                    Filters
                    <ChevronDown className={`w-4 h-4 ml-1 transition-transform ${showFilters ? 'rotate-180' : ''}`} />
                  </Button>
                  
                  <Select value={`${sortBy}-${sortOrder}`} onValueChange={(value) => {
                    const [newSortBy, newSortOrder] = value.split('-');
                    setSortBy(newSortBy as any);
                    setSortOrder(newSortOrder as any);
                  }}>
                    <SelectTrigger className="w-32 glassmorphism-card border-0 bg-input">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="glassmorphism-card border-0 bg-card">
                      <SelectItem value="date-desc">Newest</SelectItem>
                      <SelectItem value="date-asc">Oldest</SelectItem>
                      <SelectItem value="title-asc">A-Z</SelectItem>
                      <SelectItem value="title-desc">Z-A</SelectItem>
                      <SelectItem value="wordCount-desc">Most Words</SelectItem>
                      <SelectItem value="wordCount-asc">Fewest Words</SelectItem>
                    </SelectContent>
                  </Select>

                  <div className="flex border rounded-md glassmorphism-card border-0 bg-input">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setViewMode('list')}
                      className={`border-0 ${viewMode === 'list' ? 'bg-primary text-primary-foreground' : ''}`}
                    >
                      <List className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setViewMode('grid')}
                      className={`border-0 ${viewMode === 'grid' ? 'bg-primary text-primary-foreground' : ''}`}
                    >
                      <Grid3X3 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </div>

              {/* Expandable Filters */}
              {showFilters && (
                <div className="mt-4 pt-4 border-t border-border">
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <Select value={selectedMoodFilter || 'all'} onValueChange={(value) => setMoodFilter(value === 'all' ? null : value)}>
                      <SelectTrigger className="glassmorphism-card border-0 bg-input">
                        <SelectValue placeholder="Filter by mood..." />
                      </SelectTrigger>
                      <SelectContent className="glassmorphism-card border-0 bg-card">
                        <SelectItem value="all">All moods</SelectItem>
                        <SelectItem value="excited">😆 Excited</SelectItem>
                        <SelectItem value="positive">😊 Positive</SelectItem>
                        <SelectItem value="neutral">😐 Neutral</SelectItem>
                        <SelectItem value="thoughtful">🤔 Thoughtful</SelectItem>
                        <SelectItem value="challenging">😤 Challenging</SelectItem>
                        <SelectItem value="grateful">🙏 Grateful</SelectItem>
                        <SelectItem value="motivated">💪 Motivated</SelectItem>
                        <SelectItem value="accomplished">🎯 Accomplished</SelectItem>
                        <SelectItem value="peaceful">☮️ Peaceful</SelectItem>
                        <SelectItem value="energized">⚡ Energized</SelectItem>
                      </SelectContent>
                    </Select>

                    <Select value={selectedTagFilter || 'all'} onValueChange={(value) => setTagFilter(value === 'all' ? null : value)}>
                      <SelectTrigger className="glassmorphism-card border-0 bg-input">
                        <SelectValue placeholder="Filter by tag..." />
                      </SelectTrigger>
                      <SelectContent className="glassmorphism-card border-0 bg-card">
                        <SelectItem value="all">All tags</SelectItem>
                        {allTags.map((tag) => (
                          <SelectItem key={tag} value={tag}>{tag}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>

                    <Select value={selectedPillarFilter || 'all'} onValueChange={(value) => setPillarFilter(value === 'all' ? null : value)}>
                      <SelectTrigger className="glassmorphism-card border-0 bg-input">
                        <SelectValue placeholder="Filter by pillar..." />
                      </SelectTrigger>
                      <SelectContent className="glassmorphism-card border-0 bg-card">
                        <SelectItem value="all">All pillars</SelectItem>
                        {pillars.map((pillar) => (
                          <SelectItem key={pillar.id} value={pillar.id}>
                            <div className="flex items-center space-x-2">
                              <div 
                                className="w-3 h-3 rounded-full"
                                style={{ backgroundColor: pillar.color }}
                              />
                              <span>{pillar.name}</span>
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Entries Display */}
          {entries.length > 0 ? (
            <div className={
              viewMode === 'grid' 
                ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" 
                : "space-y-4"
            }>
              {entries.map((entry) => (
                <EntryCard key={entry.id} entry={entry} />
              ))}
            </div>
          ) : (
            <Card className="glassmorphism-card border-0">
              <CardContent className="p-12 text-center">
                <BookOpen className="w-16 h-16 mx-auto mb-4 text-muted-foreground/30" />
                <h3 className="text-lg font-medium mb-2">No entries found</h3>
                <p className="text-muted-foreground mb-4">
                  {searchQuery || selectedMoodFilter || selectedTagFilter || selectedPillarFilter
                    ? "Try adjusting your filters or search terms."
                    : "Start your journaling journey by creating your first entry."
                  }
                </p>
                <Button onClick={handleCreateNewEntry} className="bg-primary text-primary-foreground hover:bg-primary/90">
                  <Plus className="w-4 h-4 mr-2" />
                  Create First Entry
                </Button>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="analytics">
          <JournalAnalytics />
        </TabsContent>
      </Tabs>

      {/* Template Selection Modal */}
      <Dialog open={isTemplateModalOpen} onOpenChange={setIsTemplateModalOpen}>
        <DialogContent 
          className="glassmorphism-card border-0 bg-card text-card-foreground max-w-6xl max-h-[90vh] p-0 overflow-hidden"
          aria-describedby="template-selector-description"
        >
          <DialogHeader className="sr-only">
            <DialogTitle>Choose Journal Template</DialogTitle>
            <DialogDescription id="template-selector-description">
              Select a journal template to guide your reflection, or start with a blank entry
            </DialogDescription>
          </DialogHeader>
          <div className="max-h-[90vh] overflow-y-auto">
            <TemplateSelector 
              onSelectTemplate={handleSelectTemplate}
              onCreateBlank={handleCreateBlank}
            />
          </div>
        </DialogContent>
      </Dialog>

      {/* Journal Entry Modal */}
      <JournalEntryModal />
    </div>
  );
}