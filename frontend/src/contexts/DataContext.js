import React, { createContext, useContext, useState, useCallback } from 'react';

// Create the context
const DataContext = createContext();

// Context provider component
export const DataProvider = ({ children }) => {
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Function to trigger insights data refresh
  const refreshInsightsData = useCallback(() => {
    console.log('🔄 DataContext: Triggering insights data refresh');
    setIsRefreshing(true);
    
    // Increment the refresh trigger to notify consumers
    setRefreshTrigger(prev => prev + 1);
    
    // Reset refreshing state after a short delay
    setTimeout(() => {
      setIsRefreshing(false);
    }, 500);
  }, []);

  // Function to be called when data mutations occur
  const pendingIdsRef = React.useRef(new Set());

  const onDataMutation = useCallback((type, action, data) => {
    console.log(`📝 DataContext: Data mutation - ${type} ${action}`, data);
    // Guard: if mutation references a taskId, ensure it's truthy before triggering refresh
    const maybeId = data && (data.taskId || data.id);
    if (maybeId === null || maybeId === undefined || maybeId === 'null' || maybeId === 'undefined') {
      console.warn('⏭️ Skipping refresh due to invalid task id:', maybeId);
      return;
    }
    // Debounce consecutive refreshes for the same id briefly
    if (maybeId) {
      if (pendingIdsRef.current.has(maybeId)) {
        console.log('⏳ Debounced duplicate refresh for id', maybeId);
        return;
      }
      pendingIdsRef.current.add(maybeId);
      setTimeout(() => pendingIdsRef.current.delete(maybeId), 600);
    }
    refreshInsightsData();
  }, [refreshInsightsData]);

  const value = {
    refreshTrigger,
    isRefreshing,
    refreshInsightsData,
    onDataMutation
  };

  return (
    <DataContext.Provider value={value}>
      {children}
    </DataContext.Provider>
  );
};

// Hook to use the data context
export const useDataContext = () => {
  const context = useContext(DataContext);
  if (!context) {
    throw new Error('useDataContext must be used within a DataProvider');
  }
  return context;
};

export default DataContext;