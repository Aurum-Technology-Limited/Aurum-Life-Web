#!/usr/bin/env node

// This file is for debugging hierarchy filtering tests
// Run: node run-hierarchy-filtering-tests.js

const { spawn } = require('child_process');

console.log('🧪 Running Hierarchy Filtering E2E Tests...\n');

const testProcess = spawn('npx', [
  'playwright', 'test', 
  'tests/e2e/hierarchy-filtering.spec.ts',
  '--reporter=line',
  '--workers=1',
  '--timeout=60000'
], {
  stdio: 'inherit',
  cwd: process.cwd()
});

testProcess.on('close', (code) => {
  console.log(`\n🏁 Hierarchy filtering tests completed with exit code: ${code}`);
  process.exit(code);
});

testProcess.on('error', (error) => {
  console.error('❌ Failed to run tests:', error.message);
  process.exit(1);
});