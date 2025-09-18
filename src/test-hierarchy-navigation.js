#!/usr/bin/env node

const { spawn } = require('child_process');

console.log('🧪 Testing Hierarchy Navigation Fixes...\n');

// Create a comprehensive test
const testCode = `
import { test, expect } from '@playwright/test';

test.describe('Fixed Hierarchy Navigation Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to app
    await page.goto('/');
    await page.waitForTimeout(2000);
    
    // Handle auth/onboarding quickly
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
    
    // Wait for app to be ready
    await page.waitForSelector('[data-testid="navigation-sidebar"], nav', { timeout: 10000 });
  });

  test('should navigate from pillar to filtered areas', async ({ page }) => {
    console.log('=== Testing Fixed Pillar → Areas Navigation ===');
    
    // Step 1: Navigate to Pillars
    console.log('Step 1: Navigating to Pillars section');
    await page.click('nav a:has-text("Pillars"), nav button:has-text("Pillars")');
    await page.waitForTimeout(1000);
    
    // Step 2: Verify pillars are loaded
    const pillarCards = page.locator('.glassmorphism-card');
    const pillarCount = await pillarCards.count();
    console.log(\`Found \${pillarCount} pillar cards\`);
    
    if (pillarCount === 0) {
      throw new Error('No pillar cards found - sample data issue');
    }
    
    // Step 3: Get first pillar info
    const firstPillar = pillarCards.first();
    const pillarNameElement = firstPillar.locator('h3, h2, [class*="font-bold"]').first();
    const pillarName = await pillarNameElement.textContent();
    console.log(\`First pillar name: \${pillarName}\`);
    
    // Step 4: Click the pillar
    console.log('Step 4: Clicking pillar to navigate to areas');
    await firstPillar.click();
    await page.waitForTimeout(3000);
    
    // Step 5: Verify navigation to Areas section
    console.log('Step 5: Verifying navigation to Areas section');
    const areasHeading = page.locator('h1').filter({ hasText: /Areas|Focus Areas/ });
    await expect(areasHeading).toBeVisible({ timeout: 5000 });
    
    const headingText = await areasHeading.textContent();
    console.log(\`Areas heading: \${headingText}\`);
    
    // Step 6: Verify pillar name is in heading (indicating filtering)
    if (pillarName) {
      expect(headingText).toContain(pillarName);
      console.log('✅ Pillar name found in areas heading - filtering active');
    }
    
    // Step 7: Check debug panel if visible
    const debugPanel = page.locator('.fixed.top-20.right-4');
    if (await debugPanel.isVisible({ timeout: 1000 })) {
      const debugText = await debugPanel.textContent();
      console.log('🔍 Debug panel info:', debugText);
      
      // Verify debug panel shows correct context
      expect(debugText).toContain('Pillar ID:');
      expect(debugText).toContain('Filtering Active:');
    }
    
    // Step 8: Count area cards
    const areaCards = page.locator('.glassmorphism-card');
    const areaCount = await areaCards.count();
    console.log(\`Found \${areaCount} area cards in filtered view\`);
    
    // Step 9: Navigate to all areas to compare
    console.log('Step 9: Comparing with unfiltered areas');
    await page.click('nav a:has-text("Areas"), nav button:has-text("Areas")');
    await page.waitForTimeout(2000);
    
    const unfilteredAreaCards = page.locator('.glassmorphism-card');
    const unfilteredCount = await unfilteredAreaCards.count();
    console.log(\`Found \${unfilteredCount} total area cards\`);
    
    // Step 10: Verify filtering worked
    if (areaCount > 0 && unfilteredCount > 0) {
      // Filtering should show fewer or equal areas
      expect(areaCount).toBeLessThanOrEqual(unfilteredCount);
      
      if (areaCount < unfilteredCount) {
        console.log('✅ FILTERING IS WORKING - Filtered areas < Total areas');
      } else {
        console.log('⚠️  All areas shown - might be single pillar or all areas belong to this pillar');
      }
    }
    
    console.log('✅ Navigation test completed successfully');
  });

  test('should show correct breadcrumbs and context', async ({ page }) => {
    console.log('=== Testing Breadcrumbs and Context ===');
    
    // Navigate through hierarchy
    await page.click('nav button:has-text("Pillars")');
    await page.waitForTimeout(1000);
    
    const firstPillar = page.locator('.glassmorphism-card').first();
    await firstPillar.click();
    await page.waitForTimeout(2000);
    
    // Check for breadcrumbs
    const breadcrumbs = page.locator('[class*="breadcrumb"], nav[class*="flex"]');
    if (await breadcrumbs.isVisible({ timeout: 1000 })) {
      const breadcrumbText = await breadcrumbs.textContent();
      console.log(\`Breadcrumbs: \${breadcrumbText}\`);
      
      // Should show navigation path
      expect(breadcrumbText).toMatch(/Dashboard|Pillars|Areas/);
      console.log('✅ Breadcrumbs showing navigation path');
    }
  });
});
`;

// Write test file
const fs = require('fs');
const testFile = './test-navigation-fix.spec.ts';
fs.writeFileSync(testFile, testCode);

// Run the test
const testProcess = spawn('npx', [
  'playwright', 'test', 
  testFile,
  '--reporter=line',
  '--timeout=30000'
], {
  stdio: 'inherit',
  cwd: process.cwd()
});

testProcess.on('close', (code) => {
  // Clean up
  try {
    fs.unlinkSync(testFile);
  } catch (e) {}
  
  console.log(\`\\n🏁 Navigation test completed with exit code: \${code}\`);
  
  if (code === 0) {
    console.log('✅ Navigation fixes verified successfully!');
  } else {
    console.log('❌ Navigation issues still present - check console logs');
  }
  
  process.exit(code);
});

testProcess.on('error', (error) => {
  console.error('❌ Failed to run test:', error.message);
  process.exit(1);
});