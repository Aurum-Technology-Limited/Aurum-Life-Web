import { Target, Plus, AlertTriangle } from 'lucide-react';
import { Button } from '../ui/button';
import { useEnhancedFeaturesStore } from '../../stores/enhancedFeaturesStore';
import { useAppStore } from '../../stores/basicAppStore';
import EmptyState from '../shared/EmptyState';

export default function SimplePillarsFallback() {
  let pillars = [];
  let setActiveSection = () => {};
  
  try {
    pillars = useEnhancedFeaturesStore(state => state.pillars) || [];
    setActiveSection = useAppStore(state => state.setActiveSection);
  } catch (error) {
    console.warn('SimplePillarsFallback store access failed:', error);
    pillars = [];
  }

  return (
    <div className="space-y-6">
      {/* Fallback notice */}
      <div className="glassmorphism-card p-4 border-l-4 border-[#F59E0B]">
        <div className="flex items-center space-x-3">
          <AlertTriangle className="w-5 h-5 text-[#F59E0B]" />
          <div>
            <p className="text-white font-medium">Simplified View</p>
            <p className="text-[#B8BCC8] text-sm">The full pillars interface took too long to load. This is a simplified view.</p>
          </div>
        </div>
      </div>
      
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Strategic Pillars</h1>
          <p className="text-[#B8BCC8]">Core life domains that form your strategic foundation</p>
        </div>
        <div className="flex space-x-2">
          <Button 
            variant="outline"
            className="border-[#F4D03F] text-[#F4D03F]"
            onClick={() => {
              // Try to refresh just the section
              setActiveSection('dashboard');
              setTimeout(() => setActiveSection('pillars'), 100);
            }}
          >
            <Plus className="w-4 h-4 mr-2" />
            Retry
          </Button>
          <Button 
            className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
            onClick={() => {
              // Simple refresh fallback
              window.location.reload();
            }}
          >
            <Plus className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Simple Pillars List or Empty State */}
      {pillars.length === 0 ? (
        <EmptyState
          icon={<Target className="w-12 h-12" />}
          title="No Strategic Pillars Yet"
          description="Strategic pillars form the foundation of your life framework. Refresh the page to try loading them again."
          actionLabel="Refresh Page"
          onAction={() => window.location.reload()}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {pillars.slice(0, 10).map((pillar, index) => {
            try {
              return (
                <div key={pillar?.id || `fallback-pillar-${index}`} className="glassmorphism-card p-6">
                  <div className="flex items-center space-x-3 mb-4">
                    <div 
                      className="w-10 h-10 rounded-lg flex items-center justify-center"
                      style={{ backgroundColor: pillar?.color ? `${pillar.color}20` : '#F4D03F20' }}
                    >
                      <Target className="w-5 h-5" style={{ color: pillar?.color || '#F4D03F' }} />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-white font-semibold">{pillar?.name || 'Untitled Pillar'}</h3>
                      <p className="text-[#B8BCC8] text-sm">{pillar?.healthScore || 0}% Progress</p>
                    </div>
                  </div>
                  {pillar?.description && (
                    <p className="text-[#B8BCC8] text-sm mb-4">{pillar.description}</p>
                  )}
                  <div className="text-center space-y-2">
                    <p className="text-xs text-[#6B7280]">{pillar?.areas?.length || 0} areas</p>
                    <Button
                      onClick={() => {
                        try {
                          // Try to navigate to the pillar
                          const navigateToPillar = useAppStore.getState().navigateToPillar;
                          if (navigateToPillar && pillar?.id && pillar?.name) {
                            navigateToPillar(pillar.id, pillar.name);
                          }
                        } catch (navError) {
                          console.warn('Navigation failed in fallback:', navError);
                          // Fallback to refresh
                          window.location.reload();
                        }
                      }}
                      variant="outline"
                      size="sm"
                      className="border-[#F4D03F] text-[#F4D03F] hover:bg-[#F4D03F] hover:text-[#0B0D14]"
                    >
                      View Details
                    </Button>
                  </div>
                </div>
              );
            } catch (renderError) {
              console.warn('Error rendering fallback pillar:', renderError);
              return (
                <div key={`error-pillar-${index}`} className="glassmorphism-card p-6 text-center">
                  <Target className="w-8 h-8 text-[#F59E0B] mx-auto mb-2" />
                  <p className="text-[#B8BCC8] text-sm">Error loading pillar</p>
                </div>
              );
            }
          })}
        </div>
      )}
    </div>
  );
}