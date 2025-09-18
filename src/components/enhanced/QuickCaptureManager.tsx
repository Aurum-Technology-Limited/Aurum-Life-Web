import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Check, X, Brain, Tag, Clock, AlertTriangle, Target, TrendingUp, MoreHorizontal, Trash2, Edit } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '../ui/dropdown-menu';
import { useEnhancedFeaturesStore } from '../../stores/enhancedFeaturesStore';
import { ragCategorizationService } from '../../services/ragCategorization';
import { showSuccess, showError } from '../../utils/toast';
import { QuickCaptureItem } from '../../types/enhanced-features';

interface ProcessedItem extends QuickCaptureItem {
  isProcessing?: boolean;
  processingError?: string;
}

export default function QuickCaptureManager() {
  const {
    quickCaptureItems,
    pillars,
    processQuickCaptureItem,
    deleteQuickCaptureItem,
    getUnprocessedQuickCapture,
    getAllAreas,
    getAllProjects
  } = useEnhancedFeaturesStore();

  const [items, setItems] = useState<ProcessedItem[]>([]);
  const [selectedPillar, setSelectedPillar] = useState<Record<string, string>>({});
  const [selectedArea, setSelectedArea] = useState<Record<string, string>>({});
  const [selectedProject, setSelectedProject] = useState<Record<string, string>>({});

  useEffect(() => {
    // Load unprocessed items
    const unprocessed = getUnprocessedQuickCapture();
    setItems(unprocessed);
  }, [quickCaptureItems, getUnprocessedQuickCapture]);

  const handleProcessItem = async (item: QuickCaptureItem) => {
    const pillar = selectedPillar[item.id] || item.suggestedPillar || 'Personal Development';
    const area = selectedArea[item.id] || item.suggestedArea;
    const project = selectedProject[item.id] || item.suggestedProject;

    setItems(prev => prev.map(i => 
      i.id === item.id ? { ...i, isProcessing: true, processingError: undefined } : i
    ));

    try {
      // Record feedback to RAG service
      if (item.suggestedPillar && pillar !== item.suggestedPillar) {
        // User corrected the AI suggestion
        ragCategorizationService.learnFromFeedback(
          item.content,
          { pillar, area, project },
          false
        );
      } else if (item.suggestedPillar === pillar) {
        // User accepted the AI suggestion
        ragCategorizationService.learnFromFeedback(
          item.content,
          { pillar, area, project },
          true
        );
      }

      // Process the item
      processQuickCaptureItem(item.id, pillar, area, project);
      
      // Remove from local state
      setItems(prev => prev.filter(i => i.id !== item.id));
      
      showSuccess(`Item processed and added to ${pillar}!`);
    } catch (error) {
      console.error('Failed to process item:', error);
      setItems(prev => prev.map(i => 
        i.id === item.id ? { ...i, isProcessing: false, processingError: 'Failed to process' } : i
      ));
      showError('Failed to process item');
    }
  };

  const handleDeleteItem = (itemId: string) => {
    deleteQuickCaptureItem(itemId);
    setItems(prev => prev.filter(i => i.id !== itemId));
    showSuccess('Item deleted');
  };

  const handlePillarChange = (itemId: string, pillar: string) => {
    setSelectedPillar(prev => ({ ...prev, [itemId]: pillar }));
    // Reset area and project when pillar changes
    setSelectedArea(prev => ({ ...prev, [itemId]: '' }));
    setSelectedProject(prev => ({ ...prev, [itemId]: '' }));
  };

  const getAreasForPillar = (pillarName: string) => {
    const pillar = pillars.find(p => p.name === pillarName);
    return pillar ? pillar.areas : [];
  };

  const getProjectsForArea = (areaId: string) => {
    const allAreas = getAllAreas();
    const area = allAreas.find(a => a.id === areaId);
    return area ? area.projects : [];
  };

  const formatTimeAgo = (date: Date) => {
    const now = new Date();
    const diffMs = now.getTime() - new Date(date).getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  if (items.length === 0) {
    return (
      <Card className="glassmorphism-card border-0 bg-card text-card-foreground">
        <CardContent className="p-6 text-center">
          <Brain className="w-12 h-12 text-[#F4D03F] mx-auto mb-4 opacity-50" />
          <h3 className="text-lg font-medium text-white mb-2">No items to process</h3>
          <p className="text-[#B8BCC8]">
            Items you capture will appear here for review and organization.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-white">Quick Capture Items</h2>
          <p className="text-[#B8BCC8] text-sm">
            Review and organize your captured items
          </p>
        </div>
        <Badge variant="outline" className="border-[#F4D03F] text-[#F4D03F]">
          {items.length} pending
        </Badge>
      </div>

      <div className="grid gap-4">
        <AnimatePresence>
          {items.map((item) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="glassmorphism-card p-4 space-y-4"
            >
              {/* Header */}
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <Badge className="aurum-gradient text-[#0B0D14]">
                      {item.type}
                    </Badge>
                    <span className="text-xs text-[#6B7280]">
                      {formatTimeAgo(item.createdAt)}
                    </span>
                    {item.confidence && (
                      <Badge variant="outline" className="text-xs border-[#F4D03F] text-[#F4D03F]">
                        {Math.round(item.confidence * 100)}% confident
                      </Badge>
                    )}
                  </div>
                  <p className="text-white text-sm leading-relaxed">
                    {item.content}
                  </p>
                </div>

                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                      <MoreHorizontal className="w-4 h-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent className="glassmorphism-card border-0 bg-[#1A1D29] text-white">
                    <DropdownMenuItem 
                      onClick={() => handleDeleteItem(item.id)}
                      className="text-red-400 hover:text-red-300"
                    >
                      <Trash2 className="w-4 h-4 mr-2" />
                      Delete
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>

              {/* AI Suggestion Display */}
              {item.suggestedPillar && (
                <div className="glassmorphism-panel p-3 rounded-lg space-y-2">
                  <div className="flex items-center space-x-2 mb-2">
                    <Brain className="w-4 h-4 text-[#F4D03F]" />
                    <span className="text-sm text-white">AI Suggestion</span>
                  </div>
                  
                  <div className="flex flex-wrap gap-2">
                    <Badge className="aurum-gradient text-[#0B0D14]">
                      {item.suggestedPillar}
                    </Badge>
                    {item.suggestedArea && (
                      <Badge variant="outline" className="border-[rgba(244,208,63,0.3)] text-[#F4D03F]">
                        {item.suggestedArea}
                      </Badge>
                    )}
                    {item.suggestedProject && (
                      <Badge variant="outline" className="border-[rgba(59,130,246,0.3)] text-[#3B82F6]">
                        {item.suggestedProject}
                      </Badge>
                    )}
                  </div>
                </div>
              )}

              {/* Manual Selection */}
              <div className="space-y-3">
                <div className="text-sm text-[#B8BCC8]">Review and adjust categorization:</div>
                
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <Select 
                    value={selectedPillar[item.id] || item.suggestedPillar || ''} 
                    onValueChange={(value) => handlePillarChange(item.id, value)}
                  >
                    <SelectTrigger className="bg-[#0B0D14] border-[rgba(244,208,63,0.2)] text-white">
                      <SelectValue placeholder="Select Pillar" />
                    </SelectTrigger>
                    <SelectContent className="glassmorphism-card border-0 bg-[#1A1D29] text-white">
                      {pillars.map((pillar) => (
                        <SelectItem key={pillar.id} value={pillar.name}>
                          {pillar.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>

                  <Select 
                    value={selectedArea[item.id] || item.suggestedArea || ''} 
                    onValueChange={(value) => setSelectedArea(prev => ({ ...prev, [item.id]: value }))}
                    disabled={!selectedPillar[item.id] && !item.suggestedPillar}
                  >
                    <SelectTrigger className="bg-[#0B0D14] border-[rgba(244,208,63,0.2)] text-white">
                      <SelectValue placeholder="Select Area" />
                    </SelectTrigger>
                    <SelectContent className="glassmorphism-card border-0 bg-[#1A1D29] text-white">
                      {getAreasForPillar(selectedPillar[item.id] || item.suggestedPillar || '').map((area) => (
                        <SelectItem key={area.id} value={area.name}>
                          {area.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>

                  <Select 
                    value={selectedProject[item.id] || item.suggestedProject || ''} 
                    onValueChange={(value) => setSelectedProject(prev => ({ ...prev, [item.id]: value }))}
                  >
                    <SelectTrigger className="bg-[#0B0D14] border-[rgba(244,208,63,0.2)] text-white">
                      <SelectValue placeholder="No Project" />
                    </SelectTrigger>
                    <SelectContent className="glassmorphism-card border-0 bg-[#1A1D29] text-white">
                      <SelectItem value="">No Project</SelectItem>
                      {/* TODO: Add dynamic projects based on selected area */}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {/* Processing Error */}
              {item.processingError && (
                <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3">
                  <p className="text-red-400 text-sm">{item.processingError}</p>
                </div>
              )}

              {/* Actions */}
              <div className="flex items-center justify-end space-x-2 pt-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleDeleteItem(item.id)}
                  className="text-red-400 hover:text-red-300 hover:bg-red-400/10"
                >
                  <X className="w-4 h-4 mr-1" />
                  Delete
                </Button>
                
                <Button
                  size="sm"
                  onClick={() => handleProcessItem(item)}
                  disabled={item.isProcessing || (!selectedPillar[item.id] && !item.suggestedPillar)}
                  className="aurum-gradient text-[#0B0D14] hover:shadow-lg disabled:opacity-50"
                >
                  {item.isProcessing ? (
                    <>
                      <div className="w-4 h-4 mr-1 border-2 border-[#0B0D14] border-t-transparent rounded-full animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <Check className="w-4 h-4 mr-1" />
                      Process
                    </>
                  )}
                </Button>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}