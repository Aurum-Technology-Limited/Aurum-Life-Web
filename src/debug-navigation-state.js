#!/usr/bin/env node

// Simple browser-based debugging tool for navigation state
const debugScript = `
// Add this to browser console to debug navigation state
(function() {
  console.log('🔍 Navigation State Debugger Loaded');
  
  // Monitor store changes
  let lastState = null;
  
  const checkState = () => {
    try {
      // Check if stores are available
      const appStore = window.useAppStore?.getState();
      const enhancedStore = window.useEnhancedFeaturesStore?.getState();
      
      if (!appStore) {
        console.log('❌ App store not found');
        return;
      }
      
      const currentState = {
        activeSection: appStore.activeSection,
        hierarchyContext: appStore.hierarchyContext,
        pillarsCount: enhancedStore?.pillars?.length || 0,
        timestamp: new Date().toISOString()
      };
      
      // Only log if state changed
      if (JSON.stringify(currentState) !== JSON.stringify(lastState)) {
        console.log('🔄 State Change Detected:', {
          ...currentState,
          changed: lastState ? 'Updated' : 'Initial'
        });
        
        if (currentState.hierarchyContext.pillarId) {
          console.log('🎯 Pillar Context Active:', {
            pillarId: currentState.hierarchyContext.pillarId,
            pillarName: currentState.hierarchyContext.pillarName,
            section: currentState.activeSection
          });
          
          // Check if we can find the pillar
          if (enhancedStore?.pillars) {
            const targetPillar = enhancedStore.pillars.find(p => p.id === currentState.hierarchyContext.pillarId);
            if (targetPillar) {
              console.log('✅ Target pillar found:', {
                name: targetPillar.name,
                areasCount: targetPillar.areas?.length || 0,
                areaNames: targetPillar.areas?.map(a => a.name) || []
              });
            } else {
              console.log('❌ Target pillar NOT found in store');
            }
          }
        }
        
        lastState = currentState;
      }
    } catch (error) {
      console.log('❌ Error checking state:', error);
    }
  };
  
  // Check state every 500ms
  setInterval(checkState, 500);
  
  // Initial check
  checkState();
  
  // Add manual navigation test function
  window.testNavigation = () => {
    console.log('🧪 Testing Manual Navigation...');
    
    try {
      const appStore = window.useAppStore?.getState();
      const enhancedStore = window.useEnhancedFeaturesStore?.getState();
      
      if (!appStore || !enhancedStore) {
        console.log('❌ Stores not available');
        return;
      }
      
      const firstPillar = enhancedStore.pillars[0];
      if (!firstPillar) {
        console.log('❌ No pillars found');
        return;
      }
      
      console.log('🔗 Manually navigating to pillar:', firstPillar.name);
      appStore.navigateToPillar(firstPillar.id, firstPillar.name);
      
      setTimeout(() => {
        const updatedState = window.useAppStore?.getState();
        console.log('🔍 State after manual navigation:', {
          activeSection: updatedState.activeSection,
          hierarchyContext: updatedState.hierarchyContext,
          success: updatedState.hierarchyContext.pillarId === firstPillar.id
        });
      }, 100);
      
    } catch (error) {
      console.log('❌ Manual navigation failed:', error);
    }
  };
  
  console.log('✅ Debug tools ready! Run testNavigation() to test manually');
  
})();
`;

console.log('🔍 Navigation State Debugger');
console.log('Copy and paste this script into your browser console:\n');
console.log('=====================================');
console.log(debugScript);
console.log('=====================================\n');
console.log('📝 Instructions:');
console.log('1. Open browser dev tools (F12)');
console.log('2. Go to Console tab');
console.log('3. Paste the script above');
console.log('4. Press Enter to load the debugger');
console.log('5. Click on pillars to see navigation state changes');
console.log('6. Run testNavigation() to test manual navigation');
console.log('7. Check the debug panel in the UI (top right)');

// Also save to file for easy copy
const fs = require('fs');
fs.writeFileSync('./browser-debug-script.js', debugScript);
console.log('\n💾 Script also saved to browser-debug-script.js');