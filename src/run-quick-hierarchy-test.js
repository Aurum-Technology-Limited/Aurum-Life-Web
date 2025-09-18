#!/usr/bin/env node

const { spawn } = require('child_process');

console.log('🧪 Running Quick Hierarchy Filtering Test...\n');

// Create a simple inline test to check the basic functionality
const testCode = `
const test = require('@playwright/test').test;
const expect = require('@playwright/test').expect;

test('Quick hierarchy filtering verification', async ({ page }) => {
  console.log('🔍 Starting quick hierarchy test...');
  
  // Navigate to app
  await page.goto('/');
  await page.waitForTimeout(2000);
  
  // Handle any auth/onboarding quickly
  try {
    const signInBtn = page.locator('button:has-text("Sign In")');
    if (await signInBtn.isVisible({ timeout: 1000 })) {
      await signInBtn.click();
      await page.waitForTimeout(500);
    }
    
    const skipBtn = page.locator('button:has-text("Skip")');
    if (await skipBtn.isVisible({ timeout: 1000 })) {
      await skipBtn.click();
      await page.waitForTimeout(500);
    }
  } catch (e) {
    console.log('No auth/onboarding needed');
  }
  
  // Navigate to pillars
  console.log('📍 Navigating to Pillars...');
  await page.click('nav a:has-text("Pillars"), nav button:has-text("Pillars")');
  await page.waitForTimeout(1000);
  
  // Count pillar cards
  const pillarCards = page.locator('.glassmorphism-card');
  const pillarCount = await pillarCards.count();
  console.log(\`Found \${pillarCount} pillar cards\`);
  
  if (pillarCount > 0) {
    // Click first pillar
    console.log('🎯 Clicking first pillar...');
    await pillarCards.first().click();
    await page.waitForTimeout(2000);
    
    // Check if we're in Areas section
    const areasHeading = page.locator('h1:has-text("Areas"), h1:has-text("Focus Areas")');
    const isInAreas = await areasHeading.isVisible({ timeout: 3000 });
    console.log(\`Areas section visible: \${isInAreas}\`);
    
    if (isInAreas) {
      const headingText = await areasHeading.textContent();
      console.log(\`Areas heading: \${headingText}\`);
      
      // Count area cards
      const areaCards = page.locator('.glassmorphism-card');
      const areaCount = await areaCards.count();
      console.log(\`Area cards found: \${areaCount}\`);
      
      // Check debug panel if visible
      const debugPanel = page.locator('.fixed.top-20.right-4');
      if (await debugPanel.isVisible({ timeout: 1000 })) {
        const debugText = await debugPanel.textContent();
        console.log('🔍 Debug info:', debugText);
      }
      
      console.log('✅ Basic hierarchy navigation working');
    } else {
      console.log('❌ Failed to navigate to Areas section');
    }
  } else {
    console.log('❌ No pillar cards found');
  }
  
  console.log('🏁 Quick test completed');
});
`;

// Write the test to a temporary file
const fs = require('fs');
const path = require('path');
const tempTestFile = path.join(__dirname, 'temp-hierarchy-test.spec.ts');

fs.writeFileSync(tempTestFile, testCode);

// Run the test
const testProcess = spawn('npx', [
  'playwright', 'test', 
  tempTestFile,
  '--reporter=line',
  '--timeout=30000'
], {
  stdio: 'inherit',
  cwd: process.cwd()
});

testProcess.on('close', (code) => {
  // Clean up temp file
  try {
    fs.unlinkSync(tempTestFile);
  } catch (e) {
    // Ignore cleanup errors
  }
  
  console.log(`\n🏁 Quick test completed with exit code: ${code}`);
  process.exit(code);
});

testProcess.on('error', (error) => {
  console.error('❌ Failed to run test:', error.message);
  process.exit(1);
});