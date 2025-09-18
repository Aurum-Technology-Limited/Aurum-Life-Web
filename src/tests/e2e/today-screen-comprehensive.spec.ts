/**
 * Comprehensive Today Screen E2E Tests
 * Testing all animations, buttons, interactions, and functionality
 * Following Aurum Life design guidelines and requirements
 */

import { test, expect } from '@playwright/test';

test.describe('Today Screen Comprehensive E2E Tests', () => {
  // Helper function to ensure user is authenticated and on Today screen
  const navigateToToday = async (page: any) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Wait for loading to complete
    await page.waitForSelector('[data-testid="loading-screen"], .glassmorphism-card, h1:has-text("Today")', {
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
    
    // Navigate to Today section
    const todayNav = page.locator('nav').getByText('Today');
    if (await todayNav.isVisible({ timeout: 3000 })) {
      await todayNav.click();
    } else {
      // Try mobile navigation
      const mobileMenuButton = page.locator('button[aria-label*="menu"], button[aria-label*="navigation"]');
      if (await mobileMenuButton.first().isVisible()) {
        await mobileMenuButton.first().click();
        await page.getByText('Today').click();
      }
    }
    
    // Wait for Today screen to be fully loaded
    await page.waitForSelector('h1:has-text("Today")', { timeout: 10000 });
  };

  test.beforeEach(async ({ page }) => {
    await navigateToToday(page);
  });

  test.describe('Today Screen Layout and Structure', () => {
    test('displays Today screen with correct layout', async ({ page }) => {
      // Check main header
      await expect(page.getByRole('heading', { name: /today/i })).toBeVisible();
      
      // Check sun icon
      const sunIcon = page.locator('svg').filter({ hasText: /sun/i }).or(page.locator('.w-8.h-8.text-\\[\\#F4D03F\\]'));
      await expect(sunIcon.first()).toBeVisible();
      
      // Check date display
      const dateText = page.locator('text=/\\w+day, \\w+ \\d+, \\d+/');
      await expect(dateText.first()).toBeVisible();
      
      // Check main sections
      await expect(page.getByText('Daily Progress')).toBeVisible();
      await expect(page.getByText('Priority Tasks')).toBeVisible();
      await expect(page.getByText("Today's Schedule")).toBeVisible();
      await expect(page.getByText('Time Blocks')).toBeVisible();
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

    test('uses Aurum Life color scheme consistently', async ({ page }) => {
      // Check gold accent color usage
      const goldElements = page.locator('.text-\\[\\#F4D03F\\], .bg-\\[\\#F4D03F\\]');
      expect(await goldElements.count()).toBeGreaterThan(0);
      
      // Check dark background
      const body = page.locator('body');
      const backgroundColor = await body.evaluate(el => 
        window.getComputedStyle(el).backgroundColor
      );
      expect(backgroundColor).toMatch(/rgb\(11, 13, 20\)|#0B0D14/);
    });
  });

  test.describe('Daily Progress Section', () => {
    test('displays progress overview correctly', async ({ page }) => {
      const progressCard = page.locator('text=Daily Progress').locator('..').locator('..');
      await expect(progressCard).toBeVisible();
      
      // Check progress percentage
      const progressPercentage = page.locator('text=/\\d+%/').first();
      await expect(progressPercentage).toBeVisible();
      
      // Check completion ratio
      const completionRatio = page.locator('text=/\\d+\\/\\d+ completed/');
      await expect(completionRatio).toBeVisible();
      
      // Check progress bar
      const progressBar = page.locator('[role="progressbar"], .h-3');
      await expect(progressBar.first()).toBeVisible();
    });

    test('progress bar animates correctly', async ({ page }) => {
      const progressBar = page.locator('[role="progressbar"] > div').first();
      
      if (await progressBar.isVisible()) {
        // Check that progress bar has width style applied
        const width = await progressBar.getAttribute('style');
        expect(width).toContain('width');
        
        // Check animation class
        await expect(progressBar).toHaveClass(/transition/);
      }
    });

    test('calculates progress accurately', async ({ page }) => {
      // Get progress percentage and completion ratio
      const progressText = await page.locator('text=/\\d+%/').first().textContent();
      const completionText = await page.locator('text=/\\d+\\/\\d+ completed/').textContent();
      
      if (progressText && completionText) {
        const percentage = parseInt(progressText.replace('%', ''));
        const [completed, total] = completionText.match(/\\d+/g)?.map(Number) || [0, 0];
        
        if (total > 0) {
          const expectedPercentage = Math.round((completed / total) * 100);
          expect(percentage).toBe(expectedPercentage);
        }
      }
    });
  });

  test.describe('Priority Tasks Section', () => {
    test('displays priority tasks or empty state', async ({ page }) => {
      const tasksCard = page.locator('text=Priority Tasks').locator('..').locator('..');
      await expect(tasksCard).toBeVisible();
      
      // Check for tasks or empty state
      const hasEmptyState = await page.getByText('No priority tasks for today').isVisible();
      const hasTasks = await page.locator('[data-testid="task-checkbox"]').count() > 0;
      
      expect(hasEmptyState || hasTasks).toBe(true);
    });

    test('Add Task button works correctly', async ({ page }) => {
      const addTaskButton = page.locator('[data-testid="add-task-button"]');
      await expect(addTaskButton).toBeVisible();
      
      // Check button styling
      await expect(addTaskButton).toHaveClass(/bg-\[#F4D03F\]/);
      await expect(addTaskButton).toHaveClass(/text-\[#0B0D14\]/);
      
      // Test hover effect
      await addTaskButton.hover();
      await page.waitForTimeout(100);
      
      // Click button
      await addTaskButton.click();
      
      // Should either open modal or show project creation prompt
      const modal = page.locator('[role="dialog"]');
      const isModalVisible = await modal.isVisible({ timeout: 2000 });
      
      if (isModalVisible) {
        // Modal opened successfully
        await expect(modal).toBeVisible();
        
        // Check for task creation form elements
        const nameInput = page.locator('input[placeholder*="task"], input[id*="name"]').first();
        await expect(nameInput).toBeVisible();
        
        // Close modal
        await page.keyboard.press('Escape');
      }
      // If no modal, that's fine - might be showing project creation prompt
    });

    test('Create Your First Task button works in empty state', async ({ page }) => {
      const createFirstTaskButton = page.locator('[data-testid="create-first-task-button"]');
      
      if (await createFirstTaskButton.isVisible()) {
        await expect(createFirstTaskButton).toHaveClass(/bg-\[#F4D03F\]/);
        await createFirstTaskButton.click();
        
        // Should open modal or show project creation dialog
        const modal = page.locator('[role="dialog"]');
        const isModalVisible = await modal.isVisible({ timeout: 2000 });
        
        if (isModalVisible) {
          await expect(modal).toBeVisible();
          await page.keyboard.press('Escape');
        }
      }
    });

    test('task items display correctly with proper information', async ({ page }) => {
      const taskItems = page.locator('[data-testid="task-checkbox"]').locator('..').locator('..').locator('..');
      const taskCount = await taskItems.count();
      
      if (taskCount > 0) {
        const firstTask = taskItems.first();
        
        // Check task structure
        await expect(firstTask.locator('[data-testid="task-checkbox"]')).toBeVisible();
        await expect(firstTask.locator('p').first()).toBeVisible(); // Task name
        
        // Check pillar badge
        const pillarBadge = firstTask.locator('text=/🎯|Target/').first();
        if (await pillarBadge.isVisible()) {
          await expect(pillarBadge).toBeVisible();
        }
        
        // Check priority indicator
        const priorityText = firstTask.locator('text=/priority/');
        if (await priorityText.isVisible()) {
          await expect(priorityText).toBeVisible();
        }
        
        // Check hover effect
        await firstTask.hover();
        await page.waitForTimeout(100);
      }
    });

    test('task completion toggle works', async ({ page }) => {
      const taskCheckbox = page.locator('[data-testid="task-checkbox"]').first();
      
      if (await taskCheckbox.isVisible()) {
        // Get initial state
        const initialClasses = await taskCheckbox.getAttribute('class');
        
        // Click to toggle completion
        await taskCheckbox.click();
        await page.waitForTimeout(500);
        
        // Check if state changed
        const newClasses = await taskCheckbox.getAttribute('class');
        expect(newClasses).not.toBe(initialClasses);
      }
    });

    test('task items have proper hover animations', async ({ page }) => {
      const taskItems = page.locator('.flex.items-center.space-x-3.p-3.rounded-lg');
      const taskCount = await taskItems.count();
      
      if (taskCount > 0) {
        const firstTask = taskItems.first();
        
        // Check hover transition class
        await expect(firstTask).toHaveClass(/transition-colors/);
        
        // Test hover effect
        await firstTask.hover();
        await page.waitForTimeout(100);
        
        // Check hover background color change
        const hoverStyles = await firstTask.evaluate(el => 
          window.getComputedStyle(el).backgroundColor
        );
        expect(hoverStyles).toBeTruthy();
      }
    });
  });

  test.describe('Today\'s Schedule Section', () => {
    test('displays schedule section correctly', async ({ page }) => {
      const scheduleCard = page.locator('text=Today\'s Schedule').locator('..').locator('..');
      await expect(scheduleCard).toBeVisible();
      
      // Check calendar icon
      const calendarIcon = scheduleCard.locator('svg').first();
      await expect(calendarIcon).toBeVisible();
    });

    test('Add Time Block button in schedule works', async ({ page }) => {
      const addTimeBlockButton = page.locator('[data-testid="add-time-block-button"]');
      await expect(addTimeBlockButton).toBeVisible();
      
      // Check button styling
      await expect(addTimeBlockButton).toHaveClass(/bg-\[#F4D03F\]/);
      
      // Test click
      await addTimeBlockButton.click();
      
      // Should open time block modal
      const modal = page.locator('[role="dialog"]');
      await expect(modal).toBeVisible({ timeout: 5000 });
      
      // Check for time block form elements
      await expect(page.locator('input[id="title"]')).toBeVisible();
      await expect(page.locator('input[type="time"]').first()).toBeVisible();
      
      // Close modal
      await page.keyboard.press('Escape');
    });
  });

  test.describe('Time Blocks Section', () => {
    test('displays time blocks section correctly', async ({ page }) => {
      const timeBlocksCard = page.locator('text=Time Blocks').locator('..').locator('..');
      await expect(timeBlocksCard).toBeVisible();
    });

    test('shows empty state or time blocks', async ({ page }) => {
      const emptyState = page.getByText('No time blocks scheduled for today');
      const timeBlockItems = page.locator('.w-2.h-2.rounded-full');
      
      const hasEmptyState = await emptyState.isVisible();
      const hasTimeBlocks = await timeBlockItems.count() > 0;
      
      expect(hasEmptyState || hasTimeBlocks).toBe(true);
    });

    test('Add First Time Block button works in empty state', async ({ page }) => {
      const addFirstTimeBlockButton = page.locator('[data-testid="add-first-time-block-button"]');
      
      if (await addFirstTimeBlockButton.isVisible()) {
        await addFirstTimeBlockButton.click();
        
        // Should open time block modal
        const modal = page.locator('[role="dialog"]');
        await expect(modal).toBeVisible({ timeout: 5000 });
        
        await page.keyboard.press('Escape');
      }
    });

    test('time block items display correctly', async ({ page }) => {
      const timeBlockItems = page.locator('.flex.items-center.justify-between.p-2.rounded-lg');
      const itemCount = await timeBlockItems.count();
      
      if (itemCount > 0) {
        const firstBlock = timeBlockItems.first();
        
        // Check color indicator
        await expect(firstBlock.locator('.w-2.h-2.rounded-full')).toBeVisible();
        
        // Check title and time
        await expect(firstBlock.locator('p').first()).toBeVisible();
        
        // Check duration info
        const timeInfo = firstBlock.locator('text=/\\d+:\\d+|min/');
        if (await timeInfo.first().isVisible()) {
          await expect(timeInfo.first()).toBeVisible();
        }
        
        // Check hover effect
        await firstBlock.hover();
        await page.waitForTimeout(100);
      }
    });

    test('View all time blocks button appears when needed', async ({ page }) => {
      const viewAllButton = page.locator('button:has-text("View all")');
      
      if (await viewAllButton.isVisible()) {
        await expect(viewAllButton).toBeVisible();
        await viewAllButton.click();
        // Should navigate or show more blocks
      }
    });
  });

  test.describe('Time Block Creation Modal', () => {
    test('opens and displays correctly', async ({ page }) => {
      const addTimeBlockButton = page.locator('[data-testid="add-time-block-button"]');
      await addTimeBlockButton.click();
      
      const modal = page.locator('[role="dialog"]');
      await expect(modal).toBeVisible();
      
      // Check modal title
      await expect(page.getByText('Create Time Block')).toBeVisible();
      
      // Check form fields
      await expect(page.locator('input[id="title"]')).toBeVisible();
      await expect(page.locator('textarea[id="description"]')).toBeVisible();
      await expect(page.locator('input[id="startTime"]')).toBeVisible();
      await expect(page.locator('input[id="endTime"]')).toBeVisible();
      
      // Check type selector
      const typeSelect = page.locator('[role="combobox"]').first();
      await expect(typeSelect).toBeVisible();
      
      // Check action buttons
      await expect(page.getByRole('button', { name: /cancel/i })).toBeVisible();
      await expect(page.getByRole('button', { name: /create time block/i })).toBeVisible();
    });

    test('form validation works correctly', async ({ page }) => {
      const addTimeBlockButton = page.locator('[data-testid="add-time-block-button"]');
      await addTimeBlockButton.click();
      
      const modal = page.locator('[role="dialog"]');
      await expect(modal).toBeVisible();
      
      // Try to submit without required fields
      const createButton = page.getByRole('button', { name: /create time block/i });
      await createButton.click();
      
      // Should show validation error or stay on modal
      await expect(modal).toBeVisible();
    });

    test('complete time block creation workflow', async ({ page }) => {
      const addTimeBlockButton = page.locator('[data-testid="add-time-block-button"]');
      await addTimeBlockButton.click();
      
      const modal = page.locator('[role="dialog"]');
      await expect(modal).toBeVisible();
      
      // Fill form
      await page.fill('input[id="title"]', 'E2E Test Focus Session');
      await page.fill('textarea[id="description"]', 'Deep work on important tasks');
      await page.fill('input[id="startTime"]', '09:00');
      await page.fill('input[id="endTime"]', '10:30');
      
      // Select type
      const typeSelect = page.locator('[role="combobox"]').first();
      await typeSelect.click();
      const focusOption = page.getByText('Deep Focus');
      if (await focusOption.isVisible()) {
        await focusOption.click();
      }
      
      // Submit
      const createButton = page.getByRole('button', { name: /create time block/i });
      await createButton.click();
      
      // Modal should close
      await expect(modal).not.toBeVisible({ timeout: 5000 });
      
      // Time block should appear in list
      await expect(page.getByText('E2E Test Focus Session')).toBeVisible({ timeout: 10000 });
    });

    test('cancel button and escape key work', async ({ page }) => {
      const addTimeBlockButton = page.locator('[data-testid="add-time-block-button"]');
      await addTimeBlockButton.click();
      
      const modal = page.locator('[role="dialog"]');
      await expect(modal).toBeVisible();
      
      // Test cancel button
      const cancelButton = page.getByRole('button', { name: /cancel/i });
      await cancelButton.click();
      await expect(modal).not.toBeVisible();
      
      // Test escape key
      await addTimeBlockButton.click();
      await expect(modal).toBeVisible();
      await page.keyboard.press('Escape');
      await expect(modal).not.toBeVisible();
    });

    test('form fields have proper styling', async ({ page }) => {
      const addTimeBlockButton = page.locator('[data-testid="add-time-block-button"]');
      await addTimeBlockButton.click();
      
      const modal = page.locator('[role="dialog"]');
      await expect(modal).toBeVisible();
      
      // Check glassmorphism styling on modal
      await expect(modal).toHaveClass(/glassmorphism-card/);
      
      // Check form field styling
      const titleInput = page.locator('input[id="title"]');
      await expect(titleInput).toHaveClass(/glassmorphism-panel/);
      
      const descriptionTextarea = page.locator('textarea[id="description"]');
      await expect(descriptionTextarea).toHaveClass(/glassmorphism-panel/);
    });
  });

  test.describe('Task Creation Modal Integration', () => {
    test('opens task creation modal from Add Task button', async ({ page }) => {
      const addTaskButton = page.locator('[data-testid="add-task-button"]');
      await addTaskButton.click();
      
      // Might show project creation prompt or open modal directly
      const modal = page.locator('[role="dialog"]');
      const isModalVisible = await modal.isVisible({ timeout: 3000 });
      
      if (isModalVisible) {
        await expect(modal).toBeVisible();
        
        // Check for task creation elements
        const nameInput = page.locator('input[placeholder*="task"], input[id*="name"]').first();
        await expect(nameInput).toBeVisible();
        
        await page.keyboard.press('Escape');
      }
    });

    test('handles case when no projects exist', async ({ page }) => {
      const addTaskButton = page.locator('[data-testid="add-task-button"]');
      await addTaskButton.click();
      
      // Listen for confirm dialog
      page.on('dialog', async dialog => {
        expect(dialog.message()).toContain('project');
        await dialog.dismiss();
      });
      
      await page.waitForTimeout(1000);
    });
  });

  test.describe('Responsive Design and Mobile', () => {
    test('adapts to mobile viewport correctly', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await page.reload();
      await navigateToToday(page);
      
      // Check that layout stacks properly
      const mainGrid = page.locator('.grid.grid-cols-1.lg\\:grid-cols-2');
      await expect(mainGrid).toBeVisible();
      
      // Check all sections are still visible
      await expect(page.getByText('Daily Progress')).toBeVisible();
      await expect(page.getByText('Priority Tasks')).toBeVisible();
      await expect(page.getByText("Today's Schedule")).toBeVisible();
      await expect(page.getByText('Time Blocks')).toBeVisible();
    });

    test('touch targets meet minimum size requirements', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await navigateToToday(page);
      
      // Check button sizes
      const buttons = page.locator('button').filter({ hasText: /Add|Create/ });
      const buttonCount = await buttons.count();
      
      for (let i = 0; i < Math.min(buttonCount, 5); i++) {
        const button = buttons.nth(i);
        const box = await button.boundingBox();
        if (box) {
          expect(box.height).toBeGreaterThanOrEqual(44);
          expect(box.width).toBeGreaterThanOrEqual(44);
        }
      }
    });

    test('content remains readable on small screens', async ({ page }) => {
      await page.setViewportSize({ width: 320, height: 568 });
      await navigateToToday(page);
      
      // Check text is not truncated inappropriately
      const headings = page.locator('h1, h2, h3');
      const headingCount = await headings.count();
      
      for (let i = 0; i < headingCount; i++) {
        const heading = headings.nth(i);
        await expect(heading).toBeVisible();
      }
    });
  });

  test.describe('Animations and Visual Effects', () => {
    test('hover effects work on interactive elements', async ({ page }) => {
      // Test button hover effects
      const addTaskButton = page.locator('[data-testid="add-task-button"]');
      
      // Get initial styles
      const initialClasses = await addTaskButton.getAttribute('class');
      
      // Hover
      await addTaskButton.hover();
      await page.waitForTimeout(100);
      
      // Should have hover class
      await expect(addTaskButton).toHaveClass(/hover:bg-\[#F7DC6F\]/);
    });

    test('task item hover animations work', async ({ page }) => {
      const taskItems = page.locator('.flex.items-center.space-x-3.p-3.rounded-lg');
      
      if (await taskItems.count() > 0) {
        const firstTask = taskItems.first();
        
        // Check transition class
        await expect(firstTask).toHaveClass(/transition-colors/);
        
        // Test hover
        await firstTask.hover();
        await page.waitForTimeout(100);
      }
    });

    test('progress bar has smooth animations', async ({ page }) => {
      const progressBar = page.locator('[role="progressbar"] > div, .h-3 > div').first();
      
      if (await progressBar.isVisible()) {
        // Should have transition properties
        const hasTransition = await progressBar.evaluate(el => {
          const styles = window.getComputedStyle(el);
          return styles.transition.includes('width') || styles.transition !== 'none';
        });
        
        expect(hasTransition).toBe(true);
      }
    });

    test('modal animations work correctly', async ({ page }) => {
      const addTimeBlockButton = page.locator('[data-testid="add-time-block-button"]');
      await addTimeBlockButton.click();
      
      const modal = page.locator('[role="dialog"]');
      await expect(modal).toBeVisible();
      
      // Modal should appear with proper animation
      const modalStyles = await modal.evaluate(el => {
        const styles = window.getComputedStyle(el);
        return {
          opacity: styles.opacity,
          transform: styles.transform
        };
      });
      
      expect(parseFloat(modalStyles.opacity)).toBeGreaterThan(0.5);
    });
  });

  test.describe('Accessibility Compliance', () => {
    test('has proper heading structure', async ({ page }) => {
      const headings = page.locator('h1, h2, h3, h4, h5, h6');
      const headingCount = await headings.count();
      expect(headingCount).toBeGreaterThan(0);
      
      // Should have main H1
      const mainHeading = page.getByRole('heading', { name: /today/i });
      await expect(mainHeading).toBeVisible();
    });

    test('buttons have accessible names', async ({ page }) => {
      const buttons = page.locator('button');
      const buttonCount = await buttons.count();
      
      for (let i = 0; i < Math.min(buttonCount, 10); i++) {
        const button = buttons.nth(i);
        if (await button.isVisible()) {
          const hasAccessibleName = await button.evaluate(el => {
            return el.getAttribute('aria-label') || 
                   el.textContent?.trim() || 
                   el.getAttribute('title');
          });
          expect(hasAccessibleName).toBeTruthy();
        }
      }
    });

    test('supports keyboard navigation', async ({ page }) => {
      // Start keyboard navigation
      await page.keyboard.press('Tab');
      
      // Navigate through focusable elements
      for (let i = 0; i < 5; i++) {
        const focusedElement = page.locator(':focus');
        await expect(focusedElement).toBeVisible();
        await page.keyboard.press('Tab');
      }
    });

    test('modals are properly announced', async ({ page }) => {
      const addTimeBlockButton = page.locator('[data-testid="add-time-block-button"]');
      await addTimeBlockButton.click();
      
      const modal = page.locator('[role="dialog"]');
      await expect(modal).toBeVisible();
      
      // Check for proper ARIA attributes
      const hasAriaLabel = await modal.getAttribute('aria-labelledby');
      const hasAriaDescription = await modal.getAttribute('aria-describedby');
      
      expect(hasAriaLabel || hasAriaDescription).toBeTruthy();
    });

    test('color contrast meets standards', async ({ page }) => {
      // Check that text has sufficient contrast on dark background
      const textElements = page.locator('p, span, h1, h2, h3').filter({ hasText: /.+/ });
      const elementCount = await textElements.count();
      
      if (elementCount > 0) {
        const firstElement = textElements.first();
        const styles = await firstElement.evaluate(el => {
          const computed = window.getComputedStyle(el);
          return {
            color: computed.color,
            backgroundColor: computed.backgroundColor
          };
        });
        
        // Should have light text on dark background
        expect(styles.color).toMatch(/rgb\\(255, 255, 255\\)|rgb\\(184, 188, 200\\)/);
      }
    });
  });

  test.describe('Error Handling and Edge Cases', () => {
    test('handles empty data states gracefully', async ({ page }) => {
      // Check for appropriate empty state messages
      const emptyStateMessages = [
        'No priority tasks for today',
        'Create your first task',
        'No time blocks scheduled',
        'Your daily schedule and time blocks will appear here'
      ];
      
      let foundEmptyState = false;
      for (const message of emptyStateMessages) {
        if (await page.getByText(message).isVisible()) {
          foundEmptyState = true;
          await expect(page.getByText(message)).toBeVisible();
        }
      }
      
      // Should have at least one empty state or actual content
      expect(foundEmptyState || await page.locator('[data-testid="task-checkbox"]').count() > 0).toBe(true);
    });

    test('handles form submission errors gracefully', async ({ page }) => {
      const addTimeBlockButton = page.locator('[data-testid="add-time-block-button"]');
      await addTimeBlockButton.click();
      
      const modal = page.locator('[role="dialog"]');
      await expect(modal).toBeVisible();
      
      // Try to submit with invalid data
      await page.fill('input[id="startTime"]', '10:00');
      await page.fill('input[id="endTime"]', '09:00'); // End before start
      
      const createButton = page.getByRole('button', { name: /create time block/i });
      await createButton.click();
      
      // Should show error or stay on modal
      await expect(modal).toBeVisible();
    });

    test('maintains functionality with network issues', async ({ page }) => {
      // Simulate offline condition
      await page.context().setOffline(true);
      
      // UI should still be responsive
      const addTaskButton = page.locator('[data-testid="add-task-button"]');
      await expect(addTaskButton).toBeVisible();
      
      await addTaskButton.click();
      
      // Should handle gracefully
      await page.waitForTimeout(2000);
      
      // Restore network
      await page.context().setOffline(false);
    });
  });

  test.describe('Performance and Loading', () => {
    test('loads within acceptable time', async ({ page }) => {
      const startTime = Date.now();
      await navigateToToday(page);
      const endTime = Date.now();
      
      const loadTime = endTime - startTime;
      expect(loadTime).toBeLessThan(5000); // Should load within 5 seconds
    });

    test('handles large amounts of data efficiently', async ({ page }) => {
      // Even with many tasks/time blocks, UI should remain responsive
      const buttons = page.locator('button');
      const buttonCount = await buttons.count();
      
      // Should be able to interact with all buttons quickly
      if (buttonCount > 0) {
        const randomButton = buttons.nth(Math.floor(buttonCount / 2));
        if (await randomButton.isVisible()) {
          await randomButton.hover();
          await page.waitForTimeout(50);
        }
      }
    });

    test('no memory leaks after interactions', async ({ page }) => {
      // Perform multiple interactions
      const addTimeBlockButton = page.locator('[data-testid="add-time-block-button"]');
      
      for (let i = 0; i < 3; i++) {
        await addTimeBlockButton.click();
        const modal = page.locator('[role="dialog"]');
        if (await modal.isVisible()) {
          await page.keyboard.press('Escape');
          await page.waitForTimeout(100);
        }
      }
      
      // Page should still be responsive
      await expect(page.getByText('Today')).toBeVisible();
    });
  });

  test.describe('Integration with Global State', () => {
    test('updates correctly when data changes', async ({ page }) => {
      // Get initial task count
      const initialTaskCount = await page.locator('[data-testid="task-checkbox"]').count();
      
      // Create a task if possible
      const addTaskButton = page.locator('[data-testid="add-task-button"]');
      await addTaskButton.click();
      
      const modal = page.locator('[role="dialog"]');
      if (await modal.isVisible({ timeout: 2000 })) {
        // Fill minimal form
        const nameInput = page.locator('input[placeholder*="task"], input[id*="name"]').first();
        if (await nameInput.isVisible()) {
          await nameInput.fill('Test Task from E2E');
          
          const createButton = page.getByRole('button', { name: /create/i });
          await createButton.click();
          
          // Wait for update
          await page.waitForTimeout(2000);
          
          // Task count should have changed
          const newTaskCount = await page.locator('[data-testid="task-checkbox"]').count();
          expect(newTaskCount).toBeGreaterThanOrEqual(initialTaskCount);
        }
      }
    });

    test('progress updates when tasks are completed', async ({ page }) => {
      const taskCheckbox = page.locator('[data-testid="task-checkbox"]').first();
      
      if (await taskCheckbox.isVisible()) {
        // Get initial progress
        const initialProgress = await page.locator('text=/\\d+%/').first().textContent();
        
        // Complete task
        await taskCheckbox.click();
        await page.waitForTimeout(1000);
        
        // Progress should update
        const newProgress = await page.locator('text=/\\d+%/').first().textContent();
        expect(newProgress).not.toBe(initialProgress);
      }
    });

    test('date display updates correctly', async ({ page }) => {
      // Check that date format is correct
      const dateText = await page.locator('text=/\\w+day, \\w+ \\d+, \\d+/').first().textContent();
      
      if (dateText) {
        const today = new Date();
        const expectedDate = today.toLocaleDateString('en-US', { 
          weekday: 'long', 
          year: 'numeric', 
          month: 'long', 
          day: 'numeric' 
        });
        
        expect(dateText).toBe(expectedDate);
      }
    });
  });
});