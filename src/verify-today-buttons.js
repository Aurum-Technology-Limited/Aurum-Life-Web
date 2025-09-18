#!/usr/bin/env node

/**
 * Quick verification script for Today screen button functionality
 * This runs basic checks without full E2E testing
 */

const fs = require('fs');
const path = require('path');

console.log('🔍 Verifying Today Screen Button Implementation...\n');

// Check if Today.tsx exists and has the expected button handlers
function verifyTodayComponent() {
  const todayPath = './components/sections/Today.tsx';
  
  if (!fs.existsSync(todayPath)) {
    console.error('❌ Today.tsx not found');
    return false;
  }
  
  const content = fs.readFileSync(todayPath, 'utf8');
  
  const checks = [
    { name: 'Add Task Button Handler', pattern: /handleQuickTaskCreate/, found: false },
    { name: 'Add Task Button Click Handler', pattern: /onClick.*handleQuickTaskCreate/, found: false },
    { name: 'Time Block Modal State', pattern: /createTimeBlockModalOpen/, found: false },
    { name: 'Time Block Button Handler', pattern: /setCreateTimeBlockModalOpen\(true\)/, found: false },
    { name: 'Task Completion Handler', pattern: /handleTaskComplete/, found: false },
    { name: 'Debug Logging', pattern: /console\.log.*button clicked/, found: false },
    { name: 'Test IDs', pattern: /data-testid=/, found: false },
    { name: 'Modal Integration', pattern: /CreateEditModal/, found: false },
    { name: 'Time Block Modal', pattern: /TimeBlockModal/, found: false },
    { name: 'Enhanced Features Store', pattern: /useEnhancedFeaturesStore/, found: false }
  ];
  
  checks.forEach(check => {
    check.found = check.pattern.test(content);
  });
  
  console.log('📋 Today.tsx Component Checks:');
  checks.forEach(check => {
    console.log(`${check.found ? '✅' : '❌'} ${check.name}`);
  });
  
  const passed = checks.filter(c => c.found).length;
  const total = checks.length;
  
  console.log(`\n📊 Component Check Results: ${passed}/${total} passed (${Math.round(passed/total*100)}%)\n`);
  
  return passed === total;
}

// Check if enhanced features store has necessary functions
function verifyEnhancedStore() {
  const storePath = './stores/enhancedFeaturesStore.ts';
  
  if (!fs.existsSync(storePath)) {
    console.error('❌ enhancedFeaturesStore.ts not found');
    return false;
  }
  
  const content = fs.readFileSync(storePath, 'utf8');
  
  const functions = [
    'getAllTasks',
    'getAllProjects', 
    'addTimeBlock',
    'getTodaysTimeBlocks',
    'completeTask',
    'addTask'
  ];
  
  console.log('📋 Enhanced Features Store Checks:');
  functions.forEach(func => {
    const found = content.includes(func);
    console.log(`${found ? '✅' : '❌'} ${func} function`);
  });
  
  const foundFunctions = functions.filter(func => content.includes(func)).length;
  console.log(`\n📊 Store Function Results: ${foundFunctions}/${functions.length} found (${Math.round(foundFunctions/functions.length*100)}%)\n`);
  
  return foundFunctions === functions.length;
}

// Check if CreateEditModal exists and supports tasks
function verifyCreateEditModal() {
  const modalPath = './components/shared/CreateEditModal.tsx';
  
  if (!fs.existsSync(modalPath)) {
    console.error('❌ CreateEditModal.tsx not found');
    return false;
  }
  
  const content = fs.readFileSync(modalPath, 'utf8');
  
  const checks = [
    { name: 'Task Type Support', pattern: /type.*task/, found: false },
    { name: 'Modal Props Interface', pattern: /CreateEditModalProps/, found: false },
    { name: 'Form Submission', pattern: /handleSubmit/, found: false },
    { name: 'Parent ID Support', pattern: /parentId/, found: false }
  ];
  
  checks.forEach(check => {
    check.found = check.pattern.test(content);
  });
  
  console.log('📋 CreateEditModal Checks:');
  checks.forEach(check => {
    console.log(`${check.found ? '✅' : '❌'} ${check.name}`);
  });
  
  const passed = checks.filter(c => c.found).length;
  console.log(`\n📊 Modal Check Results: ${passed}/${checks.length} passed (${Math.round(passed/checks.length*100)}%)\n`);
  
  return passed === checks.length;
}

// Main verification
async function runVerification() {
  console.log('🚀 Starting Today Screen Button Verification\n');
  
  const results = {
    component: verifyTodayComponent(),
    store: verifyEnhancedStore(),
    modal: verifyCreateEditModal()
  };
  
  const allPassed = Object.values(results).every(r => r);
  
  console.log('🎯 FINAL VERIFICATION RESULTS:');
  console.log('================================');
  console.log(`Today Component: ${results.component ? '✅ PASS' : '❌ FAIL'}`);
  console.log(`Enhanced Store: ${results.store ? '✅ PASS' : '❌ FAIL'}`);
  console.log(`CreateEdit Modal: ${results.modal ? '✅ PASS' : '❌ FAIL'}`);
  console.log('--------------------------------');
  console.log(`Overall: ${allPassed ? '✅ ALL CHECKS PASSED' : '❌ SOME CHECKS FAILED'}`);
  
  if (allPassed) {
    console.log(`
🎉 SUCCESS! All button functionality appears correctly implemented.

Next steps:
1. Start your dev server: npm run dev
2. Open http://localhost:3000 in your browser  
3. Navigate to Today section
4. Test the buttons manually
5. Check browser console for debug logs

Or run the automated E2E tests:
node run-today-screen-tests.js
`);
  } else {
    console.log(`
⚠️ ISSUES FOUND! Some functionality may not work correctly.

Please review the failed checks above and ensure:
1. All button handlers are properly implemented
2. Modal integration is working
3. Store functions are available
4. Debug logging is in place
`);
  }
  
  return allPassed;
}

// Run verification
if (require.main === module) {
  runVerification()
    .then(success => {
      process.exit(success ? 0 : 1);
    })
    .catch(error => {
      console.error('❌ Verification failed:', error);
      process.exit(1);
    });
}

module.exports = { runVerification };