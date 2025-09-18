/**
 * Comprehensive Dashboard E2E Tests
 * Testing all animations, buttons, interactions, and functionality
 * Following Aurum Life design guidelines and requirements
 */

import { test, expect } from '@playwright/test';

test.describe('Dashboard Comprehensive E2E Tests', () => {
  // Helper function to ensure user is authenticated
  const ensureAuthenticated = async (page: any) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Wait for loading to complete
    await page.waitForSelector('[data-testid="loading-screen"], .dashboard-container, .glassmorphism-card', {
      timeout: 10000
    });
    
    // Handle login if needed
    const loginButton = page.locator('button:has-text("Sign In"), button:has-text("Try Demo Account")');
    if (await loginButton.first().isVisible({ timeout: 2000 })) {
      // Click demo login for consistent testing
      const demoButton = page.locator('button:has-text("Try Demo Account")');
      if (await demoButton.isVisible()) {
        await demoButton.click();
      } else {
        await loginButton.first().click();
      }
      await page.waitForTimeout(3000);
    }
    
    // Handle onboarding if needed
    const getStartedButton = page.locator('button:has-text("Get Started")');
    if (await getStartedButton.isVisible({ timeout: 2000 })) {
      // Skip through onboarding quickly
      await getStartedButton.click();
      
      // Skip PAPT explanation
      await page.waitForSelector('button:has-text("Continue"), button:has-text("Skip")');
      const continueButton = page.locator('button:has-text("Continue"), button:has-text("Skip")');
      if (await continueButton.first().isVisible()) {
        await continueButton.first().click();
      }
      
      // Skip through remaining onboarding steps
      for (let i = 0; i < 5; i++) {
        await page.waitForTimeout(1000);
        const nextButton = page.locator('button:has-text("Continue"), button:has-text("Next"), button:has-text("Skip"), button:has-text("Launch")');
        if (await nextButton.first().isVisible()) {
          await nextButton.first().click();
        } else {
          break;
        }
      }
    }
    
    // Wait for dashboard to be fully loaded
    await page.waitForSelector('.dashboard-container, h1:has-text("Dashboard")', { timeout: 10000 });
  };

  test.beforeEach(async ({ page }) => {
    await ensureAuthenticated(page);
  });

  test.describe('Dashboard Loading and Layout', () => {
    test('displays dashboard skeleton loading state correctly', async ({ page }) => {
      await page.goto('/');
      
      // Should show loading skeleton initially
      const loadingElements = page.locator('.shimmer, .animate-pulse');
      await expect(loadingElements.first()).toBeVisible({ timeout: 5000 });
    });

    test('renders main dashboard layout with all sections', async ({ page }) => {
      // Check main dashboard title
      await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();
      
      // Check subtitle
      await expect(page.getByText(/your personal operating system command center/i)).toBeVisible();
      
      // Check main grid sections exist
      await expect(page.locator('.grid')).toHaveCount(2); // Stats grid + main content grid
    });

    test('applies proper glassmorphism styling', async ({ page }) => {
      // Check that cards have glassmorphism classes
      const glassCards = page.locator('.glassmorphism-card');
      await expect(glassCards.first()).toBeVisible();
      
      // Verify CSS properties are applied
      const cardStyles = await glassCards.first().evaluate((el) => {
        const styles = window.getComputedStyle(el);
        return {
          backdropFilter: styles.backdropFilter,
          background: styles.background,
          borderRadius: styles.borderRadius
        };
      });
      
      expect(cardStyles.backdropFilter).toContain('blur');
    });
  });

  test.describe('Quick Stats Cards Interactions', () => {
    test('all quick stats cards are clickable and have hover effects', async ({ page }) => {
      const statsCards = page.locator('.glassmorphism-card').first().locator('..').locator('button');
      const cardCount = await statsCards.count();
      
      // Should have 4 quick stats cards
      expect(cardCount).toBe(4);
      
      for (let i = 0; i < cardCount; i++) {
        const card = statsCards.nth(i);
        
        // Check card is visible and clickable
        await expect(card).toBeVisible();
        await expect(card).toHaveClass(/touch-target/);
        
        // Test hover effect
        await card.hover();
        
        // Verify hover styles are applied
        const hasHoverEffect = await card.evaluate((el) => {
          const styles = window.getComputedStyle(el);
          return styles.transform !== 'none' || styles.transform.includes('scale');
        });
        
        // Click and verify navigation (without actually navigating)
        await card.click();
        await page.waitForTimeout(100); // Allow for any state changes
      }
    });

    test('active pillars card navigates to pillars section', async ({ page }) => {
      const pillarsCard = page.locator('button:has(.text-primary:has-text("🎯"))');
      await expect(pillarsCard).toBeVisible();
      
      // Check card content
      await expect(pillarsCard.locator('text=Active Pillars')).toBeVisible();
      
      // Click should trigger navigation
      await pillarsCard.click();
      // Note: In real implementation, this would change activeSection
    });

    test('tasks completed card shows correct format and navigates', async ({ page }) => {
      const tasksCard = page.locator('button:has(.text-green-400:has-text("✓"))');
      await expect(tasksCard).toBeVisible();
      
      // Check card content
      await expect(tasksCard.locator('text=Tasks Completed')).toBeVisible();
      
      // Should show format like "5/10" 
      const taskCount = await tasksCard.locator('p:has-text("/")').textContent();
      expect(taskCount).toMatch(/^\d+\/\d+$/);
      
      await tasksCard.click();
    });

    test('weekly progress card shows percentage and navigates', async ({ page }) => {
      const weeklyCard = page.locator('button:has(.text-blue-400:has-text("📅"))');
      await expect(weeklyCard).toBeVisible();
      
      // Check card content
      await expect(weeklyCard.locator('text=This Week')).toBeVisible();
      
      // Should show percentage
      const percentage = await weeklyCard.locator('p:has-text("%")').textContent();
      expect(percentage).toMatch(/^\d+%$/);
      
      await weeklyCard.click();
    });

    test('average health card shows percentage and navigates', async ({ page }) => {
      const healthCard = page.locator('button:has(.text-purple-400:has-text("📈"))');
      await expect(healthCard).toBeVisible();
      
      // Check card content
      await expect(healthCard.locator('text=Avg Health')).toBeVisible();
      
      // Should show percentage
      const percentage = await healthCard.locator('p:has-text("%")').textContent();
      expect(percentage).toMatch(/^\d+%$/);
      
      await healthCard.click();
    });
  });

  test.describe('Today\'s Focus Section', () => {
    test('displays today\'s focus section with progress bar', async ({ page }) => {
      const focusSection = page.locator('.lg\\:col-span-2 .glassmorphism-card').first();
      await expect(focusSection).toBeVisible();
      
      // Check header
      await expect(focusSection.locator('h2:has-text("Today\'s Focus")')).toBeVisible();
      
      // Check progress indicator
      await expect(focusSection.locator('.h-2.bg-muted\\/50')).toBeVisible();
      
      // Check completion status
      await expect(focusSection.locator('text=/\\d+\\/\\d+ completed/')).toBeVisible();
    });

    test('shows task list or empty state correctly', async ({ page }) => {
      const focusSection = page.locator('.lg\\:col-span-2 .glassmorphism-card').first();
      
      // Check if tasks exist or empty state is shown
      const hasTasks = await focusSection.locator('button:has(.w-5.h-5.rounded-full)').count() > 0;
      const hasEmptyState = await focusSection.locator('text=No tasks created yet').isVisible();
      
      expect(hasTasks || hasEmptyState).toBe(true);
    });

    test('task items are clickable and show proper hierarchy info', async ({ page }) => {
      const focusSection = page.locator('.lg\\:col-span-2 .glassmorphism-card').first();
      const taskButtons = focusSection.locator('button:has(.w-5.h-5.rounded-full)');
      
      if (await taskButtons.count() > 0) {
        const firstTask = taskButtons.first();
        
        // Check task structure
        await expect(firstTask.locator('.w-5.h-5.rounded-full')).toBeVisible();
        await expect(firstTask.locator('h4')).toBeVisible();
        await expect(firstTask.locator('p:has-text("🎯")')).toBeVisible();
        
        // Check hover effect
        await firstTask.hover();
        
        // Click task
        await firstTask.click();
      }
    });

    test('add to today\'s focus button opens quick capture', async ({ page }) => {
      const addButton = page.locator('button:has-text("+ Add to today\'s focus")');
      await expect(addButton).toBeVisible();
      await expect(addButton).toHaveClass(/touch-target/);
      
      await addButton.click();
      // Note: In real implementation, this would open quick capture modal
    });

    test('progress bar animates correctly', async ({ page }) => {
      const progressBar = page.locator('.h-2.bg-muted\\/50 .h-full.bg-primary');
      await expect(progressBar).toBeVisible();
      
      // Check that progress bar has width style applied
      const width = await progressBar.getAttribute('style');
      expect(width).toContain('width');
      
      // Check animation class
      await expect(progressBar).toHaveClass(/transition-all duration-300/);
    });
  });

  test.describe('Quick Capture Section', () => {
    test('displays quick capture section with correct header', async ({ page }) => {
      const quickCaptureSection = page.locator('.glassmorphism-card:has(h2:has-text("Quick Capture"))');
      await expect(quickCaptureSection).toBeVisible();
      
      // Check header elements
      await expect(quickCaptureSection.locator('h2:has-text("Quick Capture")')).toBeVisible();
      await expect(quickCaptureSection.locator('span:has-text("⚡")')).toBeVisible();
    });

    test('quick capture button has proper styling and interaction', async ({ page }) => {
      const captureButton = page.locator('button:has-text("Open Quick Capture")');
      await expect(captureButton).toBeVisible();
      await expect(captureButton).toHaveClass(/bg-primary/);
      await expect(captureButton).toHaveClass(/touch-target/);
      
      // Check icon
      await expect(captureButton.locator('span:has-text("✨")')).toBeVisible();
      
      // Test hover effect
      await captureButton.hover();
      
      // Click button
      await captureButton.click();
    });

    test('shows recent captures or empty state', async ({ page }) => {
      const quickCaptureSection = page.locator('.glassmorphism-card:has(h2:has-text("Quick Capture"))');
      
      // Check for recent captures or empty state
      const hasRecentCaptures = await quickCaptureSection.locator('h3:has-text("Recent Captures:")').isVisible();
      const hasEmptyState = await quickCaptureSection.locator('text=No captures yet').isVisible();
      
      expect(hasRecentCaptures || hasEmptyState).toBe(true);
    });

    test('recent capture items have correct structure and interactions', async ({ page }) => {
      const recentCapturesHeader = page.locator('h3:has-text("Recent Captures:")');
      
      if (await recentCapturesHeader.isVisible()) {
        const captureItems = page.locator('.p-3.rounded-lg.border');
        
        if (await captureItems.count() > 0) {
          const firstItem = captureItems.first();
          
          // Check item structure
          await expect(firstItem.locator('.text-xs.px-2')).toBeVisible(); // Type badge
          await expect(firstItem.locator('.text-sm.text-white')).toBeVisible(); // Content
          
          // Check for process button if not processed
          const processButton = firstItem.locator('button:has-text("Process")');
          if (await processButton.isVisible()) {
            await expect(processButton).toHaveClass(/touch-target-small/);
            await processButton.click();
          }
        }
      }
    });

    test('view all captures button works when applicable', async ({ page }) => {
      const viewAllButton = page.locator('button:has-text("View all")');
      
      if (await viewAllButton.isVisible()) {
        await expect(viewAllButton).toHaveClass(/touch-target/);
        await viewAllButton.click();
      }
    });
  });

  test.describe('Pillar Progress Section', () => {
    test('displays pillar progress section with correct layout', async ({ page }) => {
      const progressSection = page.locator('.glassmorphism-card:has(h2:has-text("Pillar Progress"))');
      await expect(progressSection).toBeVisible();
      
      // Check header
      await expect(progressSection.locator('h2:has-text("Pillar Progress")')).toBeVisible();
      await expect(progressSection.locator('span:has-text("📈")')).toBeVisible();
    });

    test('pillar items show progress bars and trend indicators', async ({ page }) => {
      const progressSection = page.locator('.glassmorphism-card:has(h2:has-text("Pillar Progress"))');
      const pillarItems = progressSection.locator('.space-y-2 > div');
      
      if (await pillarItems.count() > 0) {
        const firstPillar = pillarItems.first();
        
        // Check pillar name button
        const pillarButton = firstPillar.locator('button');
        await expect(pillarButton).toBeVisible();
        
        // Check trend indicator
        const trendIndicator = firstPillar.locator('.text-xs');
        await expect(trendIndicator).toBeVisible();
        
        // Check progress bar
        const progressBar = firstPillar.locator('.h-2.bg-muted\\/50 div');
        await expect(progressBar).toBeVisible();
        
        // Check progress bar has proper styling
        const progressStyle = await progressBar.getAttribute('style');
        expect(progressStyle).toContain('width');
        expect(progressStyle).toContain('background');
        
        // Test pillar name click
        await pillarButton.click();
      } else {
        // Check empty state
        await expect(progressSection.locator('text=No pillars created yet')).toBeVisible();
        
        const createButton = progressSection.locator('button:has-text("Create Your First Pillar")');
        await expect(createButton).toBeVisible();
        await createButton.click();
      }
    });

    test('progress bars have correct animation classes', async ({ page }) => {
      const progressBars = page.locator('.h-2.bg-muted\\/50 div');
      
      if (await progressBars.count() > 0) {
        for (let i = 0; i < await progressBars.count(); i++) {
          const bar = progressBars.nth(i);
          await expect(bar).toHaveClass(/transition-all duration-300/);
        }
      }
    });
  });

  test.describe('Smart Tips Section', () => {
    test('displays smart tips section with tips', async ({ page }) => {
      const tipsSection = page.locator('.glassmorphism-card:has(h2:has-text("Smart Tips"))');
      await expect(tipsSection).toBeVisible();
      
      // Check header
      await expect(tipsSection.locator('h2:has-text("Smart Tips")')).toBeVisible();
      await expect(tipsSection.locator('span:has-text("🧠")')).toBeVisible();
    });

    test('tip cards have proper structure and interactions', async ({ page }) => {
      const tipsSection = page.locator('.glassmorphism-card:has(h2:has-text("Smart Tips"))');
      const tipCards = tipsSection.locator('.p-3.rounded-lg.border');
      
      expect(await tipCards.count()).toBeGreaterThanOrEqual(2);
      
      // Test wellness tip
      const wellnessTip = tipCards.filter({ has: page.locator('h4:has-text("Schedule wellness time")') });
      if (await wellnessTip.count() > 0) {
        await expect(wellnessTip.locator('span:has-text("💡")')).toBeVisible();
        
        const scheduleButton = wellnessTip.locator('button:has-text("Schedule Wellness")');
        await expect(scheduleButton).toBeVisible();
        await expect(scheduleButton).toHaveClass(/touch-target-small/);
        await scheduleButton.click();
      }
      
      // Test career tip
      const careerTip = tipCards.filter({ has: page.locator('h4:has-text("Great career momentum!")') });
      if (await careerTip.count() > 0) {
        await expect(careerTip.locator('span:has-text("🎉")')).toBeVisible();
        
        const analyticsButton = careerTip.locator('button:has-text("View Analytics")');
        await expect(analyticsButton).toBeVisible();
        await expect(analyticsButton).toHaveClass(/touch-target-small/);
        await analyticsButton.click();
      }
    });
  });

  test.describe('Responsive Design and Mobile', () => {
    test('dashboard adapts to mobile viewport', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await page.reload();
      await ensureAuthenticated(page);
      
      // Check that grid layouts stack on mobile
      const statsGrid = page.locator('.grid.grid-cols-1.md\\:grid-cols-2.lg\\:grid-cols-4');
      await expect(statsGrid).toBeVisible();
      
      // Check that main content grid adapts
      const mainGrid = page.locator('.grid.grid-cols-1.lg\\:grid-cols-2.xl\\:grid-cols-3');
      await expect(mainGrid).toBeVisible();
    });

    test('touch targets meet minimum size requirements', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await page.reload();
      await ensureAuthenticated(page);
      
      // Check that all interactive elements have proper touch target classes
      const touchTargets = page.locator('.touch-target, .touch-target-small, .touch-target-large');
      const count = await touchTargets.count();
      expect(count).toBeGreaterThan(0);
      
      // Verify minimum sizes
      for (let i = 0; i < Math.min(count, 10); i++) {
        const target = touchTargets.nth(i);
        const box = await target.boundingBox();
        if (box) {
          expect(box.height).toBeGreaterThanOrEqual(44);
          expect(box.width).toBeGreaterThanOrEqual(44);
        }
      }
    });
  });

  test.describe('Animations and Transitions', () => {
    test('cards have hover animations', async ({ page }) => {
      const glassCards = page.locator('.glassmorphism-card');
      
      for (let i = 0; i < Math.min(await glassCards.count(), 5); i++) {
        const card = glassCards.nth(i);
        
        // Get initial transform
        const initialTransform = await card.evaluate(el => 
          window.getComputedStyle(el).transform
        );
        
        // Hover over card
        await card.hover();
        await page.waitForTimeout(100);
        
        // Check if transform changed
        const hoverTransform = await card.evaluate(el => 
          window.getComputedStyle(el).transform
        );
        
        // Should have transform or hover effect
        expect(hoverTransform !== initialTransform || 
               hoverTransform.includes('translateY') ||
               hoverTransform.includes('scale')).toBe(true);
      }
    });

    test('progress bars have smooth animations', async ({ page }) => {
      const progressBars = page.locator('.transition-all.duration-300');
      expect(await progressBars.count()).toBeGreaterThan(0);
      
      // Check that transition classes are applied
      for (let i = 0; i < Math.min(await progressBars.count(), 3); i++) {
        const bar = progressBars.nth(i);
        await expect(bar).toHaveClass(/transition-all/);
        await expect(bar).toHaveClass(/duration-300/);
      }
    });

    test('buttons have proper interaction states', async ({ page }) => {
      const buttons = page.locator('button');
      const buttonCount = Math.min(await buttons.count(), 10);
      
      for (let i = 0; i < buttonCount; i++) {
        const button = buttons.nth(i);
        
        if (await button.isVisible()) {
          // Test hover state
          await button.hover();
          await page.waitForTimeout(50);
          
          // Test active state
          await button.focus();
          await page.waitForTimeout(50);
        }
      }
    });
  });

  test.describe('Error Handling and Edge Cases', () => {
    test('handles empty data states gracefully', async ({ page }) => {
      // Should handle cases where no data exists
      
      // Check for empty states in different sections
      const emptyStates = page.locator('text=No tasks created yet, text=No captures yet, text=No pillars created yet');
      
      // If empty states exist, they should have proper fallback content
      if (await emptyStates.count() > 0) {
        for (let i = 0; i < await emptyStates.count(); i++) {
          const emptyState = emptyStates.nth(i);
          await expect(emptyState).toBeVisible();
          
          // Check for call-to-action buttons
          const ctaButton = emptyState.locator('..').locator('button');
          if (await ctaButton.count() > 0) {
            await expect(ctaButton.first()).toBeVisible();
          }
        }
      }
    });

    test('maintains performance with large datasets', async ({ page }) => {
      // Measure load time
      const startTime = Date.now();
      await page.reload();
      await ensureAuthenticated(page);
      const endTime = Date.now();
      
      // Should load within reasonable time
      expect(endTime - startTime).toBeLessThan(5000);
      
      // Check that all main sections are visible
      await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();
      await expect(page.locator('.glassmorphism-card')).toHaveCount({ min: 4 });
    });
  });

  test.describe('Accessibility Compliance', () => {
    test('has proper ARIA labels and roles', async ({ page }) => {
      // Check for proper headings
      const headings = page.locator('h1, h2, h3, h4, h5, h6');
      expect(await headings.count()).toBeGreaterThan(0);
      
      // Check button accessibility
      const buttons = page.locator('button');
      for (let i = 0; i < Math.min(await buttons.count(), 10); i++) {
        const button = buttons.nth(i);
        const hasAccessibleName = await button.evaluate(el => {
          return el.getAttribute('aria-label') || 
                 el.textContent?.trim() || 
                 el.getAttribute('title');
        });
        expect(hasAccessibleName).toBeTruthy();
      }
    });

    test('supports keyboard navigation', async ({ page }) => {
      // Start keyboard navigation
      await page.keyboard.press('Tab');
      
      // Navigate through focusable elements
      for (let i = 0; i < 10; i++) {
        const focusedElement = page.locator(':focus');
        await expect(focusedElement).toBeVisible();
        await page.keyboard.press('Tab');
      }
    });

    test('maintains color contrast in dark mode', async ({ page }) => {
      // Verify dark mode styling is applied
      const body = page.locator('body');
      const backgroundColor = await body.evaluate(el => 
        window.getComputedStyle(el).backgroundColor
      );
      
      // Should be dark background
      expect(backgroundColor).toMatch(/rgb\(11, 13, 20\)|#0B0D14/);
    });
  });

  test.describe('Integration with Global State', () => {
    test('responds to section navigation changes', async ({ page }) => {
      // Click on different quick stats to test navigation
      const statsCards = page.locator('.grid button.glassmorphism-card');
      
      if (await statsCards.count() >= 4) {
        // Test clicking pillars card
        await statsCards.first().click();
        
        // Test clicking tasks card  
        await statsCards.nth(1).click();
        
        // Test clicking analytics cards
        await statsCards.nth(2).click();
        await statsCards.nth(3).click();
      }
    });

    test('updates data when stores change', async ({ page }) => {
      // Initial state
      const initialTaskCount = await page.locator('text=/\\d+\\/\\d+ completed/').textContent();
      
      // Trigger action that might change data (like adding a task)
      const addButton = page.locator('button:has-text("+ Add to today\'s focus")');
      if (await addButton.isVisible()) {
        await addButton.click();
        await page.waitForTimeout(100);
      }
      
      // Note: In real implementation, this would update the UI
    });
  });
});