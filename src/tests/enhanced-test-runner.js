#!/usr/bin/env node
/**
 * Enhanced Test Suite Runner for Aurum Life
 * Comprehensive testing with all recommended enhancements
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🚀 AURUM LIFE - ENHANCED TEST SUITE EXECUTION');
console.log('=============================================\n');

// Test execution with enhanced error handling and reporting
const runEnhancedTests = (command, description, options = {}) => {
  console.log(`\n🔄 ${description}`);
  console.log('-'.repeat(60));
  
  const startTime = Date.now();
  
  try {
    const output = execSync(command, {
      encoding: 'utf-8',
      stdio: 'pipe',
      timeout: options.timeout || 180000, // 3 minutes default
      maxBuffer: 1024 * 1024 * 10, // 10MB buffer
    });
    
    const endTime = Date.now();
    const duration = ((endTime - startTime) / 1000).toFixed(2);
    
    console.log(output);
    console.log(`✅ ${description} completed successfully in ${duration}s`);
    
    return {
      success: true,
      duration: parseFloat(duration),
      output,
      command,
      description,
    };
  } catch (error) {
    const endTime = Date.now();
    const duration = ((endTime - startTime) / 1000).toFixed(2);
    
    console.error(`❌ ${description} failed after ${duration}s:`);
    console.error(error.stdout || error.message);
    
    if (error.stderr) {
      console.error('STDERR:', error.stderr);
    }
    
    return {
      success: false,
      duration: parseFloat(duration),
      error: error.message,
      stdout: error.stdout,
      stderr: error.stderr,
      command,
      description,
    };
  }
};

// Generate comprehensive test report
const generateEnhancedReport = (results) => {
  const now = new Date();
  const timestamp = now.toISOString();
  
  const summary = {
    totalSuites: results.length,
    passedSuites: results.filter(r => r.success).length,
    failedSuites: results.filter(r => !r.success).length,
    totalDuration: results.reduce((sum, r) => sum + (r.duration || 0), 0),
    timestamp,
    environment: {
      node: process.version,
      platform: process.platform,
      arch: process.arch,
      ci: !!process.env.CI,
    },
  };

  const report = {
    summary,
    results,
    recommendations: generateRecommendations(results),
    nextSteps: generateNextSteps(results),
  };

  // Save detailed JSON report
  try {
    fs.writeFileSync(
      path.join(process.cwd(), 'enhanced-test-results.json'),
      JSON.stringify(report, null, 2)
    );
    console.log('\n📄 Enhanced test report saved to enhanced-test-results.json');
  } catch (error) {
    console.error('❌ Failed to save enhanced test report:', error.message);
  }

  return report;
};

// Generate intelligent recommendations based on test results
const generateRecommendations = (results) => {
  const recommendations = [];
  const failedTests = results.filter(r => !r.success);
  
  if (failedTests.length > 0) {
    recommendations.push({
      type: 'critical',
      title: 'Failed Tests Need Attention',
      description: `${failedTests.length} test suite(s) failed. Review error messages and fix issues before deployment.`,
      action: 'Review failed test output and address root causes',
    });
  }

  const slowTests = results.filter(r => r.duration > 60);
  if (slowTests.length > 0) {
    recommendations.push({
      type: 'performance',
      title: 'Slow Test Execution',
      description: `${slowTests.length} test suite(s) took longer than 60 seconds to complete.`,
      action: 'Consider optimizing slow tests or running them separately',
    });
  }

  if (results.every(r => r.success)) {
    recommendations.push({
      type: 'success',
      title: 'Excellent Test Coverage',
      description: 'All test suites passed successfully. Your application is well-tested and ready for production.',
      action: 'Consider adding more edge case tests or performance benchmarks',
    });
  }

  return recommendations;
};

// Generate actionable next steps
const generateNextSteps = (results) => {
  const steps = [];
  
  if (results.every(r => r.success)) {
    steps.push('✅ All tests passing - ready for production deployment');
    steps.push('🚀 Consider setting up continuous integration');
    steps.push('📈 Add performance monitoring and alerts');
    steps.push('🔄 Schedule regular test suite maintenance');
  } else {
    steps.push('🔧 Fix failing tests before deployment');
    steps.push('📝 Update documentation for any changed functionality');
    steps.push('🧪 Add regression tests for fixed issues');
    steps.push('⚡ Optimize slow-running test suites');
  }

  return steps;
};

// Display comprehensive results summary
const displayEnhancedSummary = (report) => {
  const { summary, recommendations, nextSteps } = report;
  
  console.log('\n🎯 ENHANCED TEST EXECUTION SUMMARY');
  console.log('=================================');
  console.log(`📊 Total Test Suites: ${summary.totalSuites}`);
  console.log(`✅ Passed: ${summary.passedSuites}`);
  console.log(`❌ Failed: ${summary.failedSuites}`);
  console.log(`⏱️  Total Duration: ${summary.totalDuration.toFixed(2)}s`);
  console.log(`📅 Executed: ${new Date(summary.timestamp).toLocaleString()}`);
  console.log(`🖥️  Environment: Node ${summary.environment.node} on ${summary.environment.platform}`);
  
  if (recommendations.length > 0) {
    console.log('\n💡 RECOMMENDATIONS');
    console.log('==================');
    recommendations.forEach((rec, index) => {
      const icon = rec.type === 'critical' ? '🚨' : 
                  rec.type === 'performance' ? '⚡' : 
                  rec.type === 'success' ? '🎉' : '📝';
      console.log(`${index + 1}. ${icon} ${rec.title}`);
      console.log(`   ${rec.description}`);
      console.log(`   Action: ${rec.action}\n`);
    });
  }

  if (nextSteps.length > 0) {
    console.log('🎯 NEXT STEPS');
    console.log('=============');
    nextSteps.forEach(step => {
      console.log(`${step}`);
    });
  }

  const successRate = ((summary.passedSuites / summary.totalSuites) * 100).toFixed(1);
  console.log(`\n🏆 SUCCESS RATE: ${successRate}%`);
  
  if (summary.failedSuites === 0) {
    console.log('\n🎉 OUTSTANDING! All test suites passed. Aurum Life is production-ready! ✨');
  } else {
    console.log(`\n⚠️  ${summary.failedSuites} test suite(s) need attention before deployment.`);
  }
};

// Main enhanced test execution
const main = async () => {
  console.log('🏁 Starting enhanced comprehensive test suite...\n');
  
  const startTime = Date.now();
  const results = [];

  // 1. Enhanced Unit Tests with coverage
  results.push(runEnhancedTests(
    'npx jest --testPathPattern="test" --coverage --verbose --ci --maxWorkers=50%',
    '🧪 Enhanced Unit Tests with Coverage',
    { timeout: 240000 }
  ));

  // 2. Phase 4 Feature Tests
  results.push(runEnhancedTests(
    'npx jest --testPathPattern="phase4" --verbose --ci',
    '🤖 Phase 4 AI & Collaboration Features Tests',
    { timeout: 180000 }
  ));

  // 3. Comprehensive Accessibility Tests
  results.push(runEnhancedTests(
    'npx jest --testPathPattern="accessibility" --verbose --ci',
    '♿ Comprehensive Accessibility (WCAG 2.1 AA) Tests',
    { timeout: 180000 }
  ));

  // 4. Visual Regression Tests
  results.push(runEnhancedTests(
    'npx jest --testPathPattern="visual" --verbose --ci',
    '🎨 Visual Regression Tests',
    { timeout: 300000 }
  ));

  // 5. End-to-End Playwright Tests
  results.push(runEnhancedTests(
    'npx playwright test --reporter=html',
    '🌐 End-to-End User Workflow Tests (Playwright)',
    { timeout: 600000 }
  ));

  // 6. TypeScript Type Checking
  results.push(runEnhancedTests(
    'npx tsc --noEmit --skipLibCheck',
    '📝 TypeScript Type Safety Verification',
    { timeout: 120000 }
  ));

  // 7. ESLint Code Quality
  results.push(runEnhancedTests(
    'npx eslint . --ext .ts,.tsx --format=json --output-file=eslint-results.json || npx eslint . --ext .ts,.tsx',
    '🔍 ESLint Code Quality Analysis',
    { timeout: 120000 }
  ));

  // 8. Security Audit
  results.push(runEnhancedTests(
    'npm audit --audit-level=moderate --json > security-audit.json || npm audit --audit-level=moderate',
    '🔒 Security Vulnerability Audit',
    { timeout: 120000 }
  ));

  // 9. Bundle Analysis
  results.push(runEnhancedTests(
    'npm run build && npx vite-bundle-analyzer dist',
    '📦 Bundle Size Analysis',
    { timeout: 180000 }
  ));

  // 10. Performance Lighthouse Audit
  results.push(runEnhancedTests(
    'npm run build && npx lighthouse http://localhost:4173 --chrome-flags="--headless" --output=json --output-path=./lighthouse-report.json',
    '⚡ Performance Lighthouse Audit',
    { timeout: 300000 }
  ));

  const totalTime = ((Date.now() - startTime) / 1000).toFixed(2);
  
  console.log(`\n⏱️  Total execution time: ${totalTime} seconds`);
  
  // Generate and display enhanced report
  const report = generateEnhancedReport(results);
  displayEnhancedSummary(report);

  // Exit with appropriate code
  const hasFailures = results.some(r => !r.success);
  process.exit(hasFailures ? 1 : 0);
};

// Handle process signals
process.on('SIGINT', () => {
  console.log('\n\n🛑 Test execution interrupted by user');
  process.exit(1);
});

process.on('SIGTERM', () => {
  console.log('\n\n🛑 Test execution terminated');
  process.exit(1);
});

// Execute if run directly
if (require.main === module) {
  main().catch(error => {
    console.error('\n❌ Enhanced test suite execution failed:', error);
    process.exit(1);
  });
}

module.exports = {
  runEnhancedTests,
  generateEnhancedReport,
  displayEnhancedSummary,
};