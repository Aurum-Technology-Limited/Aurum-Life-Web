#!/usr/bin/env node
/**
 * Aurum Life Test Suite Runner
 * Comprehensive test execution with detailed reporting
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🧪 AURUM LIFE - COMPREHENSIVE TEST SUITE EXECUTION');
console.log('==================================================\n');

// Test execution functions
const runTests = (command, description) => {
  console.log(`\n🔄 ${description}`);
  console.log('-'.repeat(50));
  
  try {
    const startTime = Date.now();
    const output = execSync(command, { 
      encoding: 'utf-8',
      stdio: 'pipe',
      timeout: 120000 // 2 minutes timeout
    });
    const endTime = Date.now();
    const duration = ((endTime - startTime) / 1000).toFixed(2);
    
    console.log(output);
    console.log(`✅ ${description} completed in ${duration}s`);
    return { success: true, duration, output };
  } catch (error) {
    console.error(`❌ ${description} failed:`);
    console.error(error.stdout || error.message);
    return { success: false, error: error.message, output: error.stdout };
  }
};

const analyzeTestResults = (results) => {
  console.log('\n📊 TEST SUITE ANALYSIS');
  console.log('=====================\n');
  
  const totalTests = results.reduce((sum, result) => {
    if (result.success && result.output) {
      const testMatch = result.output.match(/(\d+) tests?/);
      return sum + (testMatch ? parseInt(testMatch[1]) : 0);
    }
    return sum;
  }, 0);
  
  const passedSuites = results.filter(r => r.success).length;
  const failedSuites = results.filter(r => !r.success).length;
  
  console.log(`📋 Total Test Suites: ${results.length}`);
  console.log(`✅ Passed Suites: ${passedSuites}`);
  console.log(`❌ Failed Suites: ${failedSuites}`);
  console.log(`🎯 Estimated Total Tests: ${totalTests}`);
  
  const totalDuration = results.reduce((sum, result) => sum + (result.duration || 0), 0);
  console.log(`⏱️  Total Execution Time: ${totalDuration.toFixed(2)}s`);
  
  return {
    totalSuites: results.length,
    passedSuites,
    failedSuites,
    estimatedTotalTests: totalTests,
    totalDuration: totalDuration.toFixed(2)
  };
};

const generateTestReport = (results, analysis) => {
  const report = {
    timestamp: new Date().toISOString(),
    summary: analysis,
    results: results.map(result => ({
      description: result.description,
      success: result.success,
      duration: result.duration,
      error: result.error || null
    }))
  };
  
  try {
    fs.writeFileSync('./test-results.json', JSON.stringify(report, null, 2));
    console.log('\n📄 Test report saved to test-results.json');
  } catch (error) {
    console.error('Failed to save test report:', error.message);
  }
  
  return report;
};

// Main test execution
const main = async () => {
  const startTime = Date.now();
  const results = [];
  
  console.log('🚀 Starting comprehensive test suite...\n');
  
  // 1. Unit Tests
  const unitTestResult = runTests('npm test -- --testPathPattern="test" --verbose', 'Unit Tests');
  results.push({ ...unitTestResult, description: 'Unit Tests' });
  
  // 2. Coverage Report
  const coverageResult = runTests('npm run test:coverage -- --testPathPattern="test" --silent', 'Coverage Analysis');
  results.push({ ...coverageResult, description: 'Coverage Analysis' });
  
  // 3. Type Checking
  const typeCheckResult = runTests('npm run type-check', 'TypeScript Type Checking');
  results.push({ ...typeCheckResult, description: 'TypeScript Type Checking' });
  
  // 4. Linting
  const lintResult = runTests('npm run lint', 'ESLint Code Quality Check');
  results.push({ ...lintResult, description: 'ESLint Code Quality Check' });
  
  // 5. Security Audit
  const auditResult = runTests('npm audit --audit-level=moderate', 'Security Vulnerability Audit');
  results.push({ ...auditResult, description: 'Security Vulnerability Audit' });
  
  // Analyze and report results
  const analysis = analyzeTestResults(results);
  generateTestReport(results, analysis);
  
  const totalTime = ((Date.now() - startTime) / 1000).toFixed(2);
  
  console.log('\n🎉 TEST SUITE EXECUTION COMPLETE');
  console.log('=================================');
  console.log(`⏱️  Total Runtime: ${totalTime}s`);
  console.log(`📊 Success Rate: ${((analysis.passedSuites / analysis.totalSuites) * 100).toFixed(1)}%`);
  
  if (analysis.failedSuites === 0) {
    console.log('\n✨ ALL TESTS PASSED! Your Aurum Life application is ready for production.');
    process.exit(0);
  } else {
    console.log(`\n⚠️  ${analysis.failedSuites} test suite(s) failed. Please review the output above.`);
    process.exit(1);
  }
};

// Execute if run directly
if (require.main === module) {
  main().catch(error => {
    console.error('❌ Test suite execution failed:', error);
    process.exit(1);
  });
}

module.exports = { runTests, analyzeTestResults, generateTestReport };