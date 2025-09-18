import { useState, useEffect } from 'react';
import { useEnhancedFeaturesStore } from '../../stores/enhancedFeaturesStore';

interface DebugEvent {
  timestamp: Date;
  type: string;
  message: string;
  data?: any;
}

export default function TodayButtonDebug() {
  const [isVisible, setIsVisible] = useState(false);
  const [events, setEvents] = useState<DebugEvent[]>([]);
  
  const {
    getAllTasks,
    getAllProjects,
    timeBlocks,
    pillars
  } = useEnhancedFeaturesStore();

  // Log store state changes
  useEffect(() => {
    const allTasks = getAllTasks();
    const allProjects = getAllProjects();
    
    addEvent('STORE_STATE', 'Store state updated', {
      tasksCount: allTasks.length,
      projectsCount: allProjects.length,
      timeBlocksCount: timeBlocks.length,
      pillarsCount: pillars.length
    });
  }, [getAllTasks, getAllProjects, timeBlocks, pillars]);

  // Listen for custom debug events instead of patching console.log
  useEffect(() => {
    const handleDebugEvent = (event: CustomEvent) => {
      try {
        const { type, message, data } = event.detail;
        addEvent(type || 'DEBUG_EVENT', message, data);
      } catch (error) {
        console.log('Debug event handler error (non-critical):', error);
      }
    };

    // Listen for custom debug events
    window.addEventListener('aurumDebugEvent', handleDebugEvent);

    return () => {
      window.removeEventListener('aurumDebugEvent', handleDebugEvent);
    };
  }, []);

  const addEvent = (type: string, message: string, data?: any) => {
    setEvents(prev => [{
      timestamp: new Date(),
      type,
      message,
      data
    }, ...prev.slice(0, 9)]); // Keep last 10 events
  };

  const clearEvents = () => setEvents([]);

  // Toggle visibility with keyboard shortcut
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.shiftKey && e.key === 'D') {
        setIsVisible(prev => !prev);
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, []);

  if (!isVisible) {
    return (
      <div 
        className="fixed bottom-4 left-4 z-50 bg-[#F4D03F] text-[#0B0D14] px-3 py-1 rounded text-xs cursor-pointer"
        onClick={() => setIsVisible(true)}
      >
        Debug (Ctrl+Shift+D)
      </div>
    );
  }

  return (
    <div className="fixed bottom-4 left-4 z-50 w-96 max-h-80 bg-[#1A1D29] border border-[#F4D03F33] rounded-lg p-4 text-white text-xs overflow-hidden">
      <div className="flex justify-between items-center mb-3">
        <h3 className="font-semibold text-[#F4D03F]">Today Button Debug</h3>
        <div className="flex space-x-2">
          <button 
            onClick={clearEvents}
            className="bg-[#F4D03F] text-[#0B0D14] px-2 py-1 rounded text-xs"
          >
            Clear
          </button>
          <button 
            onClick={() => setIsVisible(false)}
            className="text-[#B8BCC8] hover:text-white"
          >
            ✕
          </button>
        </div>
      </div>

      <div className="space-y-2 max-h-48 overflow-y-auto">
        <div className="grid grid-cols-2 gap-2 text-xs bg-[#0B0D14] p-2 rounded">
          <div>Tasks: {getAllTasks().length}</div>
          <div>Projects: {getAllProjects().length}</div>
          <div>Time Blocks: {timeBlocks.length}</div>
          <div>Pillars: {pillars.length}</div>
        </div>

        <div className="font-semibold text-[#F4D03F]">Recent Events:</div>
        
        {events.length === 0 ? (
          <div className="text-[#B8BCC8] italic">No events yet. Try clicking buttons on Today screen.</div>
        ) : (
          events.map((event, index) => (
            <div key={index} className="border-l-2 border-[#F4D03F33] pl-2 pb-2">
              <div className="flex justify-between">
                <span className={`font-semibold ${
                  event.type === 'CONSOLE_LOG' ? 'text-[#10B981]' : 
                  event.type === 'STORE_STATE' ? 'text-[#3B82F6]' : 
                  'text-[#F59E0B]'
                }`}>
                  {event.type}
                </span>
                <span className="text-[#B8BCC8]">
                  {event.timestamp.toLocaleTimeString()}
                </span>
              </div>
              <div className="text-white">{event.message}</div>
              {event.data && (
                <div className="text-[#B8BCC8] text-xs mt-1">
                  {typeof event.data === 'object' ? 
                    JSON.stringify(event.data, null, 2).slice(0, 100) + '...' : 
                    String(event.data)
                  }
                </div>
              )}
            </div>
          ))
        )}
      </div>

      <div className="mt-3 pt-2 border-t border-[#F4D03F33] text-xs text-[#B8BCC8]">
        Press Ctrl+Shift+D to toggle. Click buttons on Today screen to see debug info.
      </div>
    </div>
  );
}