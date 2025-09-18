import { useAppStore } from '../../stores/basicAppStore';
import { useEnhancedFeaturesStore } from '../../stores/enhancedFeaturesStore';

export default function HierarchyDebug() {
  const hierarchyContext = useAppStore(state => state.hierarchyContext);
  const activeSection = useAppStore(state => state.activeSection);
  const { pillars, getAreasByPillarId, getAllAreas } = useEnhancedFeaturesStore();
  
  const filteredAreas = hierarchyContext.pillarId 
    ? getAreasByPillarId(hierarchyContext.pillarId)
    : getAllAreas();
  
  return (
    <div className="fixed top-20 right-4 z-50 bg-black/90 text-white p-4 rounded-lg text-xs max-w-sm">
      <h4 className="text-yellow-400 font-bold mb-2">🔍 Hierarchy Debug</h4>
      
      <div className="space-y-1">
        <div><strong>Active Section:</strong> {activeSection}</div>
        <div><strong>Pillar ID:</strong> {hierarchyContext.pillarId || 'None'}</div>
        <div><strong>Pillar Name:</strong> {hierarchyContext.pillarName || 'None'}</div>
        <div><strong>Area ID:</strong> {hierarchyContext.areaId || 'None'}</div>
        <div><strong>Area Name:</strong> {hierarchyContext.areaName || 'None'}</div>
      </div>
      
      <div className="border-t border-gray-600 mt-2 pt-2">
        <div><strong>Total Pillars:</strong> {pillars.length}</div>
        <div><strong>Total Areas:</strong> {getAllAreas().length}</div>
        <div><strong>Filtered Areas:</strong> {filteredAreas.length}</div>
      </div>
      
      {hierarchyContext.pillarId && (
        <div className="border-t border-gray-600 mt-2 pt-2">
          <div className="text-green-400">
            <strong>Filtering Active:</strong><br/>
            Pillar: {hierarchyContext.pillarName}<br/>
            Areas: {filteredAreas.map(a => a.name).join(', ')}
          </div>
        </div>
      )}
      
      {!hierarchyContext.pillarId && activeSection === 'areas' && (
        <div className="border-t border-gray-600 mt-2 pt-2">
          <div className="text-red-400">
            <strong>⚠️ No Filtering:</strong><br/>
            Showing all areas without pillar context
          </div>
        </div>
      )}
    </div>
  );
}