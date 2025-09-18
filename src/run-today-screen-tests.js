#!/usr/bin/env node

/**
 * Comprehensive test runner for Today screen functionality
 * Tests both frontend button interactions and backend integration
 */

const { exec, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🚀 Starting Comprehensive Today Screen E2E Testing\n');

// Test configuration
const testConfig = {
  timeout: 120000,
  retries: 2,
  browsers: ['chromium'], // Start with just chromium for faster testing
  verbose: true
};

// Create test results directory
const resultsDir = './test-results';
if (!fs.existsSync(resultsDir)) {
  fs.mkdirSync(resultsDir, { recursive: true });
}

// Function to run command with promise
function runCommand(command, options = {}) {
  return new Promise((resolve, reject) => {
    console.log(`\n📋 Running: ${command}`);
    
    const process = exec(command, {
      ...options,
      timeout: testConfig.timeout
    }, (error, stdout, stderr) => {
      if (error) {
        console.error(`❌ Error: ${error.message}`);
        reject(error);
        return;
      }
      
      if (stderr && !stderr.includes('Warning')) {
        console.error(`⚠️ Stderr: ${stderr}`);
      }
      
      console.log(`✅ Command completed successfully`);
      resolve(stdout);
    });

    // Stream output in real-time
    if (testConfig.verbose) {
      process.stdout?.on('data', (data) => {
        console.log(data.toString().trim());
      });
      
      process.stderr?.on('data', (data) => {
        const errorText = data.toString().trim();
        if (!errorText.includes('Warning') && !errorText.includes('deprecated')) {
          console.error(`📢 ${errorText}`);
        }
      });
    }
  });
}

// Function to check if dev server is running
function checkDevServer() {
  return new Promise((resolve, reject) => {
    const http = require('http');
    const req = http.get('http://localhost:3000', (res) => {
      resolve(true);
    });
    
    req.on('error', () => {
      resolve(false);
    });
    
    req.setTimeout(5000, () => {
      req.destroy();
      resolve(false);
    });
  });
}

// Main test execution function
async function runTests() {
  try {
    console.log('🔍 Checking prerequisites...\n');
    
    // Check if package.json exists
    if (!fs.existsSync('./package.json')) {
      throw new Error('package.json not found. Are you in the project root directory?');
    }
    
    // Check if Playwright is installed
    try {
      await runCommand('npx playwright --version');
    } catch (error) {
      console.log('📦 Installing Playwright...');
      await runCommand('npm install @playwright/test');
      await runCommand('npx playwright install');
    }
    
    // Start dev server if not running
    const isServerRunning = await checkDevServer();
    let serverProcess = null;
    
    if (!isServerRunning) {
      console.log('🚀 Starting development server...');
      serverProcess = spawn('npm', ['run', 'dev'], {
        detached: false,
        stdio: 'pipe'
      });
      
      // Wait for server to start
      await new Promise((resolve) => {
        const checkServer = async () => {
          if (await checkDevServer()) {
            console.log('✅ Development server is ready');
            resolve(true);
          } else {
            setTimeout(checkServer, 2000);
          }
        };
        setTimeout(checkServer, 3000);
      });
    } else {
      console.log('✅ Development server is already running');
    }
    
    console.log('\n🧪 Running Today Screen E2E Tests...\n');
    
    // Run the specific Today screen tests
    await runCommand('npx playwright test tests/e2e/today-screen.spec.ts --reporter=html --reporter=json', {
      env: {
        ...process.env,
        CI: 'false',
        PWTEST_SKIP_TEST_OUTPUT: 'true'
      }
    });
    
    console.log('\n📊 Generating Test Summary...\n');
    
    // Check if test results exist and generate summary
    const jsonResultPath = './test-results/results.json';
    if (fs.existsSync(jsonResultPath)) {
      const results = JSON.parse(fs.readFileSync(jsonResultPath, 'utf8'));
      
      console.log('📈 TEST RESULTS SUMMARY:');
      console.log('========================');
      console.log(`Total Tests: ${results.suites.reduce((acc, suite) => acc + suite.specs.length, 0)}`);
      console.log(`Passed: ${results.stats.passed}`);
      console.log(`Failed: ${results.stats.failed}`);
      console.log(`Skipped: ${results.stats.skipped}`);
      console.log(`Duration: ${Math.round(results.stats.duration / 1000)}s`);
      
      if (results.stats.failed > 0) {
        console.log('\n❌ FAILED TESTS:');
        results.suites.forEach(suite => {
          suite.specs.forEach(spec => {
            spec.tests.forEach(test => {
              if (test.results.some(r => r.status === 'failed')) {
                console.log(`- ${test.title}`);
                test.results.forEach(result => {
                  if (result.status === 'failed' && result.error) {
                    console.log(`  Error: ${result.error.message}`);
                  }
                });
              }
            });
          });
        });
      }
    }
    
    // Cleanup
    if (serverProcess) {
      console.log('\n🛑 Stopping development server...');
      serverProcess.kill('SIGTERM');
    }
    
    console.log('\n✅ Testing completed! Check test-results/index.html for detailed report.');
    
  } catch (error) {
    console.error(`\n❌ Test execution failed: ${error.message}`);
    process.exit(1);
  }
}

// Button-specific test function
async function testButtonFunctionality() {
  console.log('\n🔘 Testing Button Functionality Specifically...\n');
  
  const buttonTests = [
    {
      name: 'Add Task Button',
      testId: 'add-task-button',
      expectedAction: 'Opens task creation modal'
    },
    {
      name: 'Create Your First Task Button',
      testId: 'create-first-task-button',
      expectedAction: 'Opens task creation modal'
    },
    {
      name: 'Add Time Block Button',
      testId: 'add-time-block-button',
      expectedAction: 'Opens time block creation modal'
    },
    {
      name: 'Add First Time Block Button',
      testId: 'add-first-time-block-button',
      expectedAction: 'Opens time block creation modal'
    }
  ];
  
  // Create a specific button test file
  const buttonTestContent = `
import { test, expect } from '@playwright/test';

test.describe('Today Screen Button Functionality', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    
    // Handle authentication
    const loginForm = page.locator('form').first();
    if (await loginForm.isVisible()) {
      await page.fill('input[type="email"]', 'demo@aurumlife.com');
      await page.fill('input[type="password"]', 'demo123');
      await page.click('button[type="submit"]');
      await page.waitForTimeout(2000);
    }

    // Navigate to Today
    const todayNav = page.locator('nav').getByText('Today');
    if (await todayNav.isVisible()) {
      await todayNav.click();
    }
    await page.waitForTimeout(1000);
  });

  ${buttonTests.map(button => `
  test('${button.name} should work correctly', async ({ page }) => {
    console.log('Testing ${button.name}...');
    
    const button = page.locator('[data-testid="${button.testId}"]');
    
    // Check if button exists and is visible
    await expect(button).toBeVisible({ timeout: 10000 });
    
    // Check if button is clickable
    await expect(button).toBeEnabled();
    
    // Click the button and verify action
    await button.click();
    
    // Wait for modal or expected UI change
    await page.waitForTimeout(1000);
    
    // For task buttons, expect modal to open
    ${button.testId.includes('task') ? `
    const modal = page.locator('[role="dialog"]');
    await expect(modal).toBeVisible({ timeout: 5000 });
    
    // Close modal
    await page.keyboard.press('Escape');
    ` : ''}
    
    // For time block buttons, expect modal to open
    ${button.testId.includes('time-block') ? `
    const modal = page.locator('[role="dialog"]');
    await expect(modal).toBeVisible({ timeout: 5000 });
    
    // Verify it's the time block modal
    await expect(page.getByText('Create Time Block')).toBeVisible();
    
    // Close modal
    await page.keyboard.press('Escape');
    ` : ''}
    
    console.log('✅ ${button.name} test passed');
  });
  `).join('')}
});
`;
  
  // Write the button test file
  fs.writeFileSync('./tests/e2e/button-functionality.spec.ts', buttonTestContent);
  
  try {
    // Run the button-specific tests
    await runCommand('npx playwright test tests/e2e/button-functionality.spec.ts --reporter=list');
    console.log('✅ All button functionality tests completed');
  } catch (error) {
    console.error('❌ Button functionality tests failed:', error.message);
  }
}

// Run the tests
if (require.main === module) {
  console.log(`
╔══════════════════════════════════════════════════════════════╗
║                   🧪 AURUM LIFE E2E TESTING                  ║
║              Today Screen Comprehensive Test Suite           ║
╚══════════════════════════════════════════════════════════════╝
`);

  Promise.resolve()
    .then(() => runTests())
    .then(() => testButtonFunctionality())
    .then(() => {
      console.log(`
╔══════════════════════════════════════════════════════════════╗
║                     ✅ TESTING COMPLETE                      ║
║          Check ./test-results/ for detailed reports         ║
╚══════════════════════════════════════════════════════════════╝
`);
    })
    .catch((error) => {
      console.error(`
╔══════════════════════════════════════════════════════════════╗
║                      ❌ TESTING FAILED                       ║
║                   ${error.message.padEnd(50)} ║
╚══════════════════════════════════════════════════════════════╝
`);
      process.exit(1);
    });
}

module.exports = { runTests, testButtonFunctionality };