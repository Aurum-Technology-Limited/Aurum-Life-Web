import { useState, useMemo } from 'react';
import { Target, Heart, Briefcase, Users, DollarSign, GraduationCap, Home, Plus, FolderKanban, Layers3, ChevronRight } from 'lucide-react';
import * as LucideIcons from 'lucide-react';
import { Button } from '../ui/button';
import { Progress } from '../ui/progress';
import { Badge } from '../ui/badge';
import { useAppStore } from '../../stores/basicAppStore';
import { useEnhancedFeaturesStore } from '../../stores/enhancedFeaturesStore';
import CreateEditModal from '../shared/CreateEditModal';
import DeleteConfirmModal from '../shared/DeleteConfirmModal';
import EmptyState from '../shared/EmptyState';
import SimplePillarsFallback from './SimplePillarsFallback';
import { Pillar } from '../../types/enhanced-features';
import { motion } from 'motion/react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from '../ui/dropdown-menu';
import { Edit, Trash2, MoreVertical } from 'lucide-react';

// Icon mapping for pillars
const getIconForPillar = (pillar: Pillar) => {
  // If pillar has a custom icon, use that
  if (pillar.icon) {
    const CustomIcon = (LucideIcons as any)[pillar.icon];
    if (CustomIcon) return CustomIcon;
  }
  
  // Fallback to name-based mapping
  switch (pillar.name.toLowerCase()) {
    case 'health & wellness': return Heart;
    case 'career & professional': return Briefcase;
    case 'relationships': return Users;
    case 'personal development': return GraduationCap;
    case 'financial wellness': return DollarSign;
    case 'home & environment': return Home;
    default: return Target;
  }
};

// Horizontal Pillar Card Component
function HorizontalPillarCard({ 
  pillar, 
  metrics, 
  onPillarClick, 
  onAreaClick, 
  onEdit, 
  onDelete
}: {
  pillar: Pillar;
  metrics: { areas: number; projects: number };
  onPillarClick: () => void;
  onAreaClick: (areaId: string, areaName: string) => void;
  onEdit: () => void;
  onDelete: () => void;
}) {
  const Icon = getIconForPillar(pillar);

  return (
    <motion.div
      whileHover={{ scale: 1.01, y: -2 }}
      whileTap={{ scale: 0.99 }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
      className="glassmorphism-card hierarchy-pillar group relative overflow-hidden cursor-pointer"
      onClick={onPillarClick}
    >
      {/* Main horizontal layout */}
      <div className="p-4 sm:p-6">
        {/* Header with badge and actions */}
        <div className="flex items-start justify-between mb-4">
          <Badge variant="outline" className="text-xs">
            {Math.round(pillar.healthScore || 0)}% Health
          </Badge>

          <div className="flex items-center space-x-1 flex-shrink-0">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-8 w-8 p-0 opacity-60 group-hover:opacity-100 transition-all duration-200 touch-target hover:bg-white/10"
                  onClick={(e) => e.stopPropagation()}
                >
                  <MoreVertical className="h-4 w-4 text-[#B8BCC8] hover:text-white transition-colors" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="glassmorphism-card border-0">
                <DropdownMenuItem onClick={(e) => { e.stopPropagation(); onEdit(); }}>
                  <Edit className="mr-2 h-4 w-4" />
                  Edit
                </DropdownMenuItem>
                <DropdownMenuSeparator className="bg-[rgba(244,208,63,0.1)]" />
                <DropdownMenuItem 
                  onClick={(e) => { e.stopPropagation(); onDelete(); }}
                  variant="destructive"
                >
                  <Trash2 className="mr-2 h-4 w-4" />
                  Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
            
            <div className="opacity-0 group-hover:opacity-100 transition-opacity">
              <div 
                className="w-8 h-8 rounded-full flex items-center justify-center touch-target"
                style={{ backgroundColor: 'rgba(244,208,63,0.15)' }}
              >
                <ChevronRight className="w-4 h-4" style={{ color: '#F4D03F' }} />
              </div>
            </div>
          </div>
        </div>

        {/* Main content - horizontal layout with proper spacing */}
        <div className="flex items-start gap-4 sm:gap-6">
          {/* Icon - properly sized container */}
          <div 
            className="w-12 h-12 sm:w-14 sm:h-14 rounded-lg flex items-center justify-center flex-shrink-0 shadow-sm"
            style={{ 
              backgroundColor: pillar.color ? `${pillar.color}20` : '#F4D03F20'
            }}
          >
            <div style={{ color: pillar.color || '#F4D03F' }}>
              <Icon className="w-5 h-5 sm:w-6 sm:h-6" />
            </div>
          </div>

          {/* Content with proper spacing */}
          <div className="flex-1 min-w-0">
            <h3 className="mb-2 break-words" style={{ color: 'var(--aurum-text-primary)' }}>
              {pillar.name}
            </h3>
            {pillar.description && (
              <p className="mb-4 break-words" style={{ color: 'var(--aurum-text-secondary)' }}>
                {pillar.description}
              </p>
            )}

            {/* Metrics row with proper spacing */}
            <div className="flex flex-wrap items-center gap-4 sm:gap-8 mb-4">
              <div className="flex items-center gap-3 min-w-0">
                <div 
                  className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                  style={{ backgroundColor: 'rgba(59, 130, 246, 0.1)' }}
                >
                  <FolderKanban className="w-4 h-4 flex-shrink-0" style={{ color: '#3B82F6' }} />
                </div>
                <div className="min-w-0">
                  <div 
                    className="font-semibold"
                    style={{ 
                      color: 'var(--aurum-text-primary)',
                      fontSize: '0.875rem'
                    }}
                  >
                    {metrics.areas}
                  </div>
                  <div 
                    style={{ 
                      color: 'var(--aurum-text-muted)',
                      fontSize: '0.75rem'
                    }}
                  >
                    Areas
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-3 min-w-0">
                <div 
                  className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                  style={{ backgroundColor: 'rgba(16, 185, 129, 0.1)' }}
                >
                  <Layers3 className="w-4 h-4 flex-shrink-0" style={{ color: '#10B981' }} />
                </div>
                <div className="min-w-0">
                  <div 
                    className="font-semibold"
                    style={{ 
                      color: 'var(--aurum-text-primary)',
                      fontSize: '0.875rem'
                    }}
                  >
                    {metrics.projects}
                  </div>
                  <div 
                    style={{ 
                      color: 'var(--aurum-text-muted)',
                      fontSize: '0.75rem'
                    }}
                  >
                    Projects
                  </div>
                </div>
              </div>
            </div>

            {/* Progress bar with proper spacing */}
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <span 
                  style={{ 
                    color: 'var(--aurum-text-secondary)',
                    fontSize: '0.875rem'
                  }}
                >
                  Progress
                </span>
                <span 
                  className="font-bold"
                  style={{ 
                    color: pillar.color || '#F4D03F',
                    fontSize: '0.875rem'
                  }}
                >
                  {Math.round(pillar.healthScore || 0)}%
                </span>
              </div>
              <Progress 
                value={pillar.healthScore || 0} 
                className="h-2 bg-white/10" 
                style={{
                  '--progress-foreground': pillar.color || '#F4D03F'
                } as React.CSSProperties}
              />
            </div>
          </div>
        </div>

        {/* Areas section */}
        {pillar.areas && pillar.areas.length > 0 && (
          <div className="border-t border-white/10 bg-white/5 -mx-4 sm:-mx-6 px-4 sm:px-6 py-4 mt-4">
            <div className="flex items-center justify-between mb-3">
              <h4 
                className="font-semibold uppercase tracking-wide"
                style={{ 
                  color: 'var(--aurum-text-secondary)',
                  fontSize: '0.875rem'
                }}
              >
                Focus Areas
              </h4>
              <span 
                className="bg-white/10 px-2 py-1 rounded-full"
                style={{ 
                  color: 'var(--aurum-text-muted)',
                  fontSize: '0.75rem'
                }}
              >
                {pillar.areas.length > 5 ? '5+' : pillar.areas.length}
              </span>
            </div>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
              {pillar.areas.slice(0, 5).map((area) => (
                <motion.div
                  key={area.id}
                  className="hierarchy-area px-3 py-2 rounded-lg bg-white/5 hover:bg-white/10 transition-all cursor-pointer group border border-white/10 hover:border-opacity-30"
                  onClick={(e) => {
                    e.stopPropagation();
                    onAreaClick(area.id, area.name);
                  }}
                  whileHover={{ scale: 1.01, x: 2 }}
                  whileTap={{ scale: 0.99 }}
                >
                  <div className="flex items-center justify-between">
                    <span 
                      className="break-words flex-1 group-hover:text-opacity-90 pr-2"
                      style={{ 
                        color: 'var(--aurum-text-primary)',
                        fontSize: '0.875rem'
                      }}
                    >
                      {area.name}
                    </span>
                    <div className="flex items-center space-x-2 ml-2 flex-shrink-0">
                      <span 
                        className="font-medium px-2 py-1 rounded-full bg-white/10"
                        style={{ 
                          color: '#3B82F6',
                          fontSize: '0.75rem'
                        }}
                      >
                        {Math.round(area.healthScore || 0)}%
                      </span>
                      <ChevronRight 
                        className="w-3 h-3 opacity-0 group-hover:opacity-70 transition-opacity" 
                        style={{ color: '#3B82F6' }}
                      />
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
            
            {pillar.areas.length > 5 && (
              <div className="text-center pt-2 border-t border-white/10 mt-3">
                <span 
                  style={{ 
                    color: 'var(--aurum-text-muted)',
                    fontSize: '0.75rem'
                  }}
                >
                  +{pillar.areas.length - 5} more areas
                </span>
              </div>
            )}
          </div>
        )}
      </div>
    </motion.div>
  );
}

export default function Pillars() {
  // ALL hooks must be called at the top before any conditional logic
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [selectedPillar, setSelectedPillar] = useState<Pillar | null>(null);

  try {
    const navigateToPillar = useAppStore(state => state.navigateToPillar);
    const { 
      pillars, 
      getAllProjects, 
      deletePillar 
    } = useEnhancedFeaturesStore();

    // Only show fallback if pillars data is genuinely not available
    if (!pillars || pillars.length === undefined) {
      return <SimplePillarsFallback />;
    }
  
    // Calculate metrics for each pillar - exactly like Areas component
    const getPillarMetrics = (pillarId: string) => {
      const allProjects = getAllProjects();
      
      // Get the current pillar
      const currentPillar = pillars.find(p => p.id === pillarId);
      if (!currentPillar) {
        return { areas: 0, projects: 0 };
      }
      
      // Get projects for this pillar's areas
      const pillarProjects = allProjects.filter(project => 
        currentPillar.areas.some(area => area.id === project.areaId)
      );
      
      return {
        areas: currentPillar.areas.length,
        projects: pillarProjects.length
      };
    };
  
    const averageProgress = useMemo(() => {
      if (pillars.length === 0) return 0;
      try {
        return Math.round(pillars.reduce((sum, pillar) => sum + pillar.healthScore, 0) / pillars.length);
      } catch (error) {
        console.warn('Error calculating average progress:', error);
        return 0;
      }
    }, [pillars]);

    const handlePillarClick = (pillar: typeof pillars[0]) => {
      console.log('🏛️ [PILLARS] Pillar clicked:', pillar.name, 'ID:', pillar.id);
      console.log('🏛️ [PILLARS] Pillar has areas:', pillar.areas.length, 'areas:', pillar.areas.map(a => a.name));
      
      // Direct navigation without delays or resets
      console.log('🔗 [PILLARS] Direct navigation to pillar:', pillar.name);
      navigateToPillar(pillar.id, pillar.name);
      
      // Immediate verification
      const currentState = useAppStore.getState();
      console.log('🔍 [PILLARS] Immediate post-navigation state:', {
        activeSection: currentState.activeSection,
        pillarId: currentState.hierarchyContext.pillarId,
        pillarName: currentState.hierarchyContext.pillarName,
        navigationSuccess: currentState.hierarchyContext.pillarId === pillar.id && currentState.activeSection === 'areas'
      });
      
      if (currentState.hierarchyContext.pillarId !== pillar.id) {
        console.log('❌ [PILLARS] Navigation failed! Retrying...');
        // Retry once if failed
        setTimeout(() => navigateToPillar(pillar.id, pillar.name), 10);
      }
    };

    const handleAreaClick = (areaId: string, areaName: string, pillar: Pillar) => {
      console.log('🎯 Area clicked from pillar section:', areaName, 'ID:', areaId, 'Pillar:', pillar.name);
      const navigateToAreaFromPillar = useAppStore.getState().navigateToAreaFromPillar;
      navigateToAreaFromPillar(pillar.id, pillar.name, areaId, areaName);
    };

    const handleEdit = (pillar: Pillar) => {
      setSelectedPillar(pillar);
      setEditModalOpen(true);
    };

    const handleDelete = (pillar: Pillar) => {
      setSelectedPillar(pillar);
      setDeleteModalOpen(true);
    };



    const confirmDelete = () => {
      if (selectedPillar) {
        deletePillar(selectedPillar.id);
        setDeleteModalOpen(false);
        setSelectedPillar(null);
      }
    };

    const getChildrenCount = (pillar: Pillar) => {
      return pillar.areas.length;
    };

    return (
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-white mb-2" style={{ fontSize: '2.25rem', fontWeight: '700' }}>
              Strategic Pillars
            </h1>
            <p style={{ color: 'var(--aurum-text-secondary)' }}>
              Core life domains that form your strategic foundation
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <div 
                className="font-bold"
                style={{ 
                  color: '#F4D03F',
                  fontSize: '1.5rem'
                }}
              >
                {averageProgress}%
              </div>
              <div 
                style={{ 
                  color: 'var(--aurum-text-secondary)',
                  fontSize: '0.875rem'
                }}
              >
                Overall Progress
              </div>
            </div>
            <Button 
              className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
              onClick={() => setCreateModalOpen(true)}
            >
              <Plus className="w-4 h-4 mr-2" />
              New Pillar
            </Button>
          </div>
        </div>

        {/* Horizontal Pillars List */}
        {pillars.length === 0 ? (
          <EmptyState
            icon={<Target className="w-12 h-12" />}
            title="No Strategic Pillars Yet"
            description="Strategic pillars form the foundation of your life framework. Create your first pillar to start organizing your goals and projects."
            actionLabel="Create Your First Pillar"
            onAction={() => setCreateModalOpen(true)}
          />
        ) : (
          <div className="space-y-6">
            {/* One pillar per row - horizontal layout */}
            {pillars.slice(0, 10).map(pillar => {
              const metrics = getPillarMetrics(pillar.id);
              
              return (
                <HorizontalPillarCard
                  key={pillar.id}
                  pillar={pillar}
                  metrics={metrics}
                  onPillarClick={() => handlePillarClick(pillar)}
                  onAreaClick={(areaId, areaName) => handleAreaClick(areaId, areaName, pillar)}
                  onEdit={() => handleEdit(pillar)}
                  onDelete={() => handleDelete(pillar)}
                />
              );
            })}
            
            {/* Overflow indicator when there are more than 10 pillars */}
            {pillars.length > 10 && (
              <div className="text-center pt-4 border-t border-[rgba(244,208,63,0.1)]">
                <p 
                  style={{ 
                    color: 'var(--aurum-text-muted)',
                    fontSize: '0.875rem'
                  }}
                >
                  Showing 10 of {pillars.length} pillars
                </p>
                <p 
                  style={{ 
                    color: 'var(--aurum-text-muted)',
                    fontSize: '0.75rem'
                  }}
                  className="mt-1"
                >
                  +{pillars.length - 10} more pillars not displayed
                </p>
              </div>
            )}
          </div>
        )}

        {/* Modals */}
        <CreateEditModal
          isOpen={createModalOpen}
          onClose={() => setCreateModalOpen(false)}
          mode="create"
          type="pillar"
          onSuccess={() => setCreateModalOpen(false)}
        />

        <CreateEditModal
          isOpen={editModalOpen}
          onClose={() => {
            setEditModalOpen(false);
            setSelectedPillar(null);
          }}
          mode="edit"
          type="pillar"
          item={selectedPillar || undefined}
          onSuccess={() => {
            setEditModalOpen(false);
            setSelectedPillar(null);
          }}
        />

        <DeleteConfirmModal
          isOpen={deleteModalOpen}
          onClose={() => {
            setDeleteModalOpen(false);
            setSelectedPillar(null);
          }}
          onConfirm={confirmDelete}
          title={`Are you sure you want to delete this pillar?`}
          itemName={selectedPillar?.name || ''}
          type="pillar"
          childrenCount={selectedPillar ? getChildrenCount(selectedPillar) : 0}
        />
      </div>
    );
  } catch (error) {
    console.error('Error in Pillars component:', error);
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="glassmorphism-card p-8 text-center max-w-md">
          <Target className="w-12 h-12 text-[#F59E0B] mx-auto mb-4" />
          <h3 
            className="font-semibold mb-2"
            style={{ 
              color: 'var(--aurum-text-primary)',
              fontSize: '1.25rem'
            }}
          >
            Something went wrong
          </h3>
          <p 
            className="mb-6"
            style={{ color: 'var(--aurum-text-secondary)' }}
          >
            There was an error loading your pillars. Please try refreshing the page.
          </p>
          <Button
            onClick={() => window.location.reload()}
            className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
          >
            Refresh
          </Button>
        </div>
      </div>
    );
  }
}