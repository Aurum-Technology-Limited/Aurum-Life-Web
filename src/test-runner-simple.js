#!/usr/bin/env node
/**
 * Simple Test Runner for Quick Verification
 */

const { execSync } = require('child_process');

console.log('🧪 Running Simple Test Verification...\n');

try {
  // Run a basic test to verify setup
  console.log('📋 Checking Jest Configuration...');
  
  const output = execSync('npx jest --listTests', { 
    encoding: 'utf-8',
    stdio: 'pipe'
  });
  
  const testFiles = output.trim().split('\n').filter(line => line.includes('.test.'));
  
  console.log(`✅ Found ${testFiles.length} test files:`);
  testFiles.forEach(file => {
    const relativePath = file.replace(process.cwd(), '.');
    console.log(`   - ${relativePath}`);
  });
  
  console.log('\n🔄 Running Basic Test Suite...');
  
  const testResult = execSync('npx jest --passWithNoTests --verbose --testTimeout=10000', { 
    encoding: 'utf-8',
    stdio: 'pipe'
  });
  
  console.log(testResult);
  console.log('\n✅ Basic test verification completed successfully!');
  
} catch (error) {
  console.error('❌ Test verification failed:');
  console.error(error.stdout || error.message);
  process.exit(1);
}