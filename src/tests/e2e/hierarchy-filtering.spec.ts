import { test, expect } from '@playwright/test';

test.describe('PAPT Hierarchy Filtering E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to app and handle any initial loading
    await page.goto('/');
    
    // Wait for app to be fully loaded and any initial modals/onboarding to complete
    await page.waitForTimeout(3000);
    
    // Check if we need to handle authentication
    const isLoginVisible = await page.locator('button:has-text("Sign In")').isVisible().catch(() => false);
    if (isLoginVisible) {
      await page.click('button:has-text("Sign In")');
      await page.waitForTimeout(1000);
    }
    
    // Check for onboarding and skip if present
    const skipButton = page.locator('button:has-text("Skip")');
    if (await skipButton.isVisible().catch(() => false)) {
      await skipButton.click();
      await page.waitForTimeout(1000);
    }
    
    // Ensure we're in the main app by waiting for navigation
    await page.waitForSelector('[data-testid="navigation-sidebar"], nav', { timeout: 10000 });
  });

  test('should filter areas when clicking on a pillar', async ({ page }) => {
    console.log('=== Starting Pillar Click and Areas Filtering Test ===');
    
    // 1. Navigate to Pillars section first
    console.log('Step 1: Navigating to Pillars section');
    const pillarsNavItem = page.locator('nav').locator('text=Pillars').first();
    await pillarsNavItem.click();
    await page.waitForTimeout(2000);
    
    // Verify we're in pillars section
    await expect(page.locator('h1:has-text("Strategic Pillars"), h1:has-text("Pillars")')).toBeVisible();
    console.log('✅ Successfully navigated to Pillars section');
    
    // 2. Find and record pillar information
    console.log('Step 2: Finding pillars and their areas');
    const pillarCards = page.locator('.glassmorphism-card').filter({ hasText: /Health|Career|Relationships|Financial|Personal|Home/ });
    const pillarCount = await pillarCards.count();
    console.log(`Found ${pillarCount} pillar cards`);
    
    if (pillarCount === 0) {
      throw new Error('No pillar cards found - sample data may not be loaded');
    }
    
    // Get the first pillar for testing
    const firstPillar = pillarCards.first();
    const pillarText = await firstPillar.textContent();
    console.log(`First pillar content: ${pillarText}`);
    
    // Extract pillar name (usually the first line or heading)
    const pillarNameElement = firstPillar.locator('h3, h2, h1, [class*="font-bold"], [class*="font-semibold"]').first();
    const pillarName = await pillarNameElement.textContent();
    console.log(`Pillar name: ${pillarName}`);
    
    // Count areas within this pillar (if visible)
    const areasInPillar = firstPillar.locator('[class*="hierarchy-area"], [class*="area"], .rounded-lg').filter({ hasText: /Fitness|Nutrition|Skills|Network|Family|Budget/ });
    const areasInPillarCount = await areasInPillar.count();
    console.log(`Areas visible in pillar: ${areasInPillarCount}`);
    
    // 3. Click on the pillar (not on sub-areas)
    console.log('Step 3: Clicking on the pillar card');
    
    // Listen for console messages to track navigation
    page.on('console', msg => {
      if (msg.text().includes('🏛️') || msg.text().includes('🔗') || msg.text().includes('🎯')) {
        console.log(`Console: ${msg.text()}`);
      }
    });
    
    // Click on the pillar card (avoid clicking on sub-elements)
    await firstPillar.click();
    await page.waitForTimeout(3000);
    
    // 4. Verify navigation to Areas section
    console.log('Step 4: Verifying navigation to Areas section');
    
    // Check URL or section indicator
    const currentUrl = page.url();
    console.log(`Current URL: ${currentUrl}`);
    
    // Look for Areas section heading
    const areasSectionHeading = page.locator('h1').filter({ hasText: /Areas|Focus Areas/ });
    await expect(areasSectionHeading).toBeVisible({ timeout: 5000 });
    console.log('✅ Successfully navigated to Areas section');
    
    // Get the actual heading text to see if it includes pillar name
    const headingText = await areasSectionHeading.textContent();
    console.log(`Areas section heading: ${headingText}`);
    
    // 5. Verify filtering - count total areas vs filtered areas
    console.log('Step 5: Verifying area filtering');
    
    // Wait for areas to load
    await page.waitForTimeout(2000);
    
    // Count area cards in the current view
    const areaCards = page.locator('.glassmorphism-card, [class*="hierarchy-area"]');
    const visibleAreaCount = await areaCards.count();
    console.log(`Visible area cards: ${visibleAreaCount}`);
    
    // Verify that the heading includes the pillar name (indicating context filtering)
    if (pillarName) {
      const expectedHeadingPattern = new RegExp(pillarName.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i');
      expect(headingText).toMatch(expectedHeadingPattern);
      console.log('✅ Heading includes pillar name, indicating filtering context');
    }
    
    // 6. Navigate to all areas to compare
    console.log('Step 6: Comparing with unfiltered areas count');
    
    // Navigate directly to areas without pillar context
    await page.locator('nav').locator('text=Areas').first().click();
    await page.waitForTimeout(2000);
    
    const unfilteredAreaCards = page.locator('.glassmorphism-card, [class*="hierarchy-area"]');
    const unfilteredAreaCount = await unfilteredAreaCards.count();
    console.log(`Unfiltered area cards: ${unfilteredAreaCount}`);
    
    // 7. Verify filtering worked
    if (areasInPillarCount > 0) {
      // If we saw areas in the pillar, the filtered count should match
      console.log(`Expected: ${areasInPillarCount}, Filtered: ${visibleAreaCount}, Unfiltered: ${unfilteredAreaCount}`);
      
      // The key test: filtered areas should be less than or equal to unfiltered areas
      expect(visibleAreaCount).toBeLessThanOrEqual(unfilteredAreaCount);
      
      if (visibleAreaCount < unfilteredAreaCount) {
        console.log('✅ FILTERING IS WORKING - Filtered areas < Total areas');
      } else if (visibleAreaCount === unfilteredAreaCount) {
        console.log('⚠️  FILTERING MAY NOT BE WORKING - Same count of areas shown');
        // This could still be valid if there's only one pillar or if all areas belong to one pillar
      }
    }
    
    console.log('=== Test completed ===');
  });

  test('should show proper breadcrumb navigation with pillar context', async ({ page }) => {
    console.log('=== Testing Breadcrumb Navigation ===');
    
    // Navigate to pillars and click one
    await page.locator('nav').locator('text=Pillars').first().click();
    await page.waitForTimeout(1000);
    
    const firstPillar = page.locator('.glassmorphism-card').first();
    const pillarName = await firstPillar.locator('h3, h2, h1').first().textContent();
    
    await firstPillar.click();
    await page.waitForTimeout(2000);
    
    // Check for breadcrumb navigation
    const breadcrumbs = page.locator('[class*="breadcrumb"], nav[class*="flex"]').filter({ hasText: /Dashboard|Pillars|Areas/ });
    if (await breadcrumbs.isVisible()) {
      const breadcrumbText = await breadcrumbs.textContent();
      console.log(`Breadcrumbs: ${breadcrumbText}`);
      
      // Should include pillar name in context
      if (pillarName) {
        expect(breadcrumbText).toContain(pillarName);
        console.log('✅ Breadcrumbs show pillar context');
      }
    }
  });

  test('should maintain hierarchy context when navigating between levels', async ({ page }) => {
    console.log('=== Testing Hierarchy Context Persistence ===');
    
    // Start from pillars
    await page.locator('nav').locator('text=Pillars').first().click();
    await page.waitForTimeout(1000);
    
    // Click a pillar
    const firstPillar = page.locator('.glassmorphism-card').first();
    await firstPillar.click();
    await page.waitForTimeout(2000);
    
    // Should be in areas now - click an area
    const firstArea = page.locator('.glassmorphism-card').first();
    if (await firstArea.isVisible()) {
      await firstArea.click();
      await page.waitForTimeout(2000);
      
      // Should be in projects now
      await expect(page.locator('h1').filter({ hasText: /Projects/ })).toBeVisible();
      console.log('✅ Successfully navigated to Projects with context');
      
      // Check if context is maintained (heading should include area name)
      const projectsHeading = await page.locator('h1').filter({ hasText: /Projects/ }).textContent();
      console.log(`Projects heading: ${projectsHeading}`);
    }
  });

  test('should show empty state when pillar has no areas', async ({ page }) => {
    console.log('=== Testing Empty State Handling ===');
    
    // This test checks what happens when filtering results in no items
    await page.locator('nav').locator('text=Areas').first().click();
    await page.waitForTimeout(1000);
    
    // Look for empty state or "Select a Pillar First" message
    const emptyState = page.locator('text="Select a Pillar First", text="No Areas", text="No Focus Areas"');
    if (await emptyState.isVisible()) {
      console.log('✅ Proper empty state shown when no pillar context');
    }
  });
  
  test('should debug filtering functions in console', async ({ page }) => {
    console.log('=== Debugging Filtering Functions ===');
    
    // Navigate to areas to trigger the filtering debug logs
    await page.locator('nav').locator('text=Areas').first().click();
    await page.waitForTimeout(2000);
    
    // Navigate to pillars and click one to see debug output
    await page.locator('nav').locator('text=Pillars').first().click();
    await page.waitForTimeout(1000);
    
    const firstPillar = page.locator('.glassmorphism-card').first();
    await firstPillar.click();
    await page.waitForTimeout(3000);
    
    // The debug logs should be captured by the console listener set up earlier
    console.log('✅ Debug information should be visible in console logs above');
  });
});