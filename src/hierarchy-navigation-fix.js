#!/usr/bin/env node

// Quick diagnostic test for hierarchy navigation
console.log('🔍 Diagnosing Hierarchy Navigation Issues...\n');

const fs = require('fs');

// Check critical files for common issues
const criticalFiles = [
  '/components/sections/Pillars.tsx',
  '/components/sections/Areas.tsx', 
  '/stores/basicAppStore.ts',
  '/stores/enhancedFeaturesStore.ts'
];

console.log('📁 Checking critical files...');

criticalFiles.forEach(file => {
  try {
    const content = fs.readFileSync(`.${file}`, 'utf8');
    
    console.log(`\n📄 ${file}:`);
    
    // Check for navigation function calls
    if (content.includes('navigateToPillar')) {
      console.log('  ✅ navigateToPillar function found');
    } else {
      console.log('  ❌ navigateToPillar function MISSING');
    }
    
    // Check for hierarchy context usage
    if (content.includes('hierarchyContext')) {
      console.log('  ✅ hierarchyContext usage found');
    } else {
      console.log('  ❌ hierarchyContext usage MISSING');
    }
    
    // Check for filtering logic
    if (content.includes('filteredAreas') || content.includes('getAreasByPillarId')) {
      console.log('  ✅ Area filtering logic found');
    } else if (file.includes('Areas.tsx')) {
      console.log('  ❌ Area filtering logic MISSING');
    }
    
    // Check for store subscriptions
    if (content.includes('useAppStore') || content.includes('useEnhancedFeaturesStore')) {
      console.log('  ✅ Store subscriptions found');
    } else {
      console.log('  ❌ Store subscriptions MISSING');
    }
    
  } catch (error) {
    console.log(`  ❌ Error reading ${file}: ${error.message}`);
  }
});

console.log('\n🔧 Issues identified. Creating comprehensive fix...\n');