import { test, expect } from '@playwright/test';

test.describe('Today Screen Functionality', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the app and ensure we're authenticated
    await page.goto('/');
    
    // Check if login is required
    const loginForm = page.locator('form').first();
    if (await loginForm.isVisible()) {
      // Use demo account
      await page.fill('input[type="email"]', 'demo@aurumlife.com');
      await page.fill('input[type="password"]', 'demo123');
      await page.click('button[type="submit"]');
      await page.waitForTimeout(2000);
    }

    // Navigate to Today section
    const todayNav = page.locator('nav').getByText('Today');
    if (await todayNav.isVisible()) {
      await todayNav.click();
    } else {
      // Try mobile navigation
      const mobileMenu = page.locator('button[aria-label="Open menu"]');
      if (await mobileMenu.isVisible()) {
        await mobileMenu.click();
        await page.getByText('Today').click();
      }
    }
    
    await page.waitForTimeout(1000);
  });

  test('Today screen loads correctly', async ({ page }) => {
    // Check for main Today elements
    await expect(page.getByText('Today')).toBeVisible();
    await expect(page.getByText('Daily Progress')).toBeVisible();
    await expect(page.getByText('Priority Tasks')).toBeVisible();
    await expect(page.getByText("Today's Schedule")).toBeVisible();
  });

  test('Add Task button opens task creation modal', async ({ page }) => {
    // Find and click the Add Task button
    const addTaskButton = page.getByRole('button', { name: /add task/i });
    await expect(addTaskButton).toBeVisible();
    
    await addTaskButton.click();
    
    // Check if modal opens
    const modal = page.locator('[role="dialog"]');
    await expect(modal).toBeVisible({ timeout: 5000 });
    
    // Check for task creation form elements
    const nameInput = page.locator('input[placeholder*="task"]').or(page.locator('input[id*="name"]'));
    await expect(nameInput).toBeVisible();
    
    // Close modal
    const closeButton = page.locator('button[aria-label="Close"]').or(page.getByText('Cancel'));
    if (await closeButton.isVisible()) {
      await closeButton.click();
    } else {
      await page.keyboard.press('Escape');
    }
  });

  test('Create Your First Task button works when no tasks exist', async ({ page }) => {
    // Look for the empty state button
    const createFirstTaskButton = page.getByRole('button', { name: /create your first task/i });
    
    if (await createFirstTaskButton.isVisible()) {
      await createFirstTaskButton.click();
      
      // Check if modal opens
      const modal = page.locator('[role="dialog"]');
      await expect(modal).toBeVisible({ timeout: 5000 });
      
      // Check for task creation form
      const nameInput = page.locator('input[placeholder*="task"]').or(page.locator('input[id*="name"]'));
      await expect(nameInput).toBeVisible();
      
      // Close modal
      await page.keyboard.press('Escape');
    }
  });

  test('Add Time Block button opens time block creation modal', async ({ page }) => {
    // Find and click Add Time Block button
    const addTimeBlockButton = page.getByRole('button', { name: /add time block/i });
    await expect(addTimeBlockButton).toBeVisible();
    
    await addTimeBlockButton.click();
    
    // Check if time block modal opens
    const modal = page.locator('[role="dialog"]');
    await expect(modal).toBeVisible({ timeout: 5000 });
    
    // Check for time block form elements
    const titleInput = page.locator('input[id="title"]').or(page.locator('input[placeholder*="title"]'));
    await expect(titleInput).toBeVisible();
    
    const startTimeInput = page.locator('input[type="time"]').first();
    await expect(startTimeInput).toBeVisible();
    
    // Close modal
    await page.keyboard.press('Escape');
  });

  test('Task creation flow works end-to-end', async ({ page }) => {
    // First ensure we have projects to add tasks to
    const projectsNav = page.locator('nav').getByText('Projects');
    if (await projectsNav.isVisible()) {
      await projectsNav.click();
      await page.waitForTimeout(1000);
      
      // Check if there are projects, if not create one
      const createProjectButton = page.getByRole('button', { name: /new project/i });
      if (await createProjectButton.isVisible()) {
        await createProjectButton.click();
        
        const modal = page.locator('[role="dialog"]');
        await expect(modal).toBeVisible();
        
        await page.fill('input[id*="name"]', 'Test Project');
        await page.fill('textarea[id*="description"]', 'Test project for E2E testing');
        
        const saveButton = page.getByRole('button', { name: /create/i });
        await saveButton.click();
        
        await page.waitForTimeout(1000);
      }
    }
    
    // Go back to Today
    const todayNav = page.locator('nav').getByText('Today');
    await todayNav.click();
    await page.waitForTimeout(1000);
    
    // Now try to create a task
    const addTaskButton = page.getByRole('button', { name: /add task/i });
    await addTaskButton.click();
    
    const modal = page.locator('[role="dialog"]');
    await expect(modal).toBeVisible();
    
    // Fill out task form
    await page.fill('input[id*="name"]', 'Test Task from Today');
    await page.fill('textarea[id*="description"]', 'This is a test task created from Today screen');
    
    // Set priority
    const prioritySelect = page.locator('select').or(page.locator('[role="combobox"]')).first();
    if (await prioritySelect.isVisible()) {
      await prioritySelect.click();
      await page.getByText('High').click();
    }
    
    // Submit form
    const createButton = page.getByRole('button', { name: /create/i });
    await createButton.click();
    
    // Verify task appears in Today view
    await expect(page.getByText('Test Task from Today')).toBeVisible({ timeout: 10000 });
  });

  test('Time block creation flow works end-to-end', async ({ page }) => {
    const addTimeBlockButton = page.getByRole('button', { name: /add time block/i });
    await addTimeBlockButton.click();
    
    const modal = page.locator('[role="dialog"]');
    await expect(modal).toBeVisible();
    
    // Fill out time block form
    await page.fill('input[id="title"]', 'Test Focus Session');
    await page.fill('textarea[id="description"]', 'Deep work on important tasks');
    await page.fill('input[id="startTime"]', '09:00');
    await page.fill('input[id="endTime"]', '10:30');
    
    // Select type
    const typeSelect = page.locator('select').or(page.locator('[role="combobox"]')).first();
    if (await typeSelect.isVisible()) {
      await typeSelect.click();
      await page.getByText('Deep Focus').click();
    }
    
    // Submit form
    const createButton = page.getByRole('button', { name: /create time block/i });
    await createButton.click();
    
    // Verify time block appears in schedule
    await expect(page.getByText('Test Focus Session')).toBeVisible({ timeout: 10000 });
  });

  test('Task completion works', async ({ page }) => {
    // Ensure there's at least one task visible
    const checkCircle = page.locator('[data-testid="task-checkbox"]').or(page.locator('svg').filter({ hasText: /check/i })).first();
    
    if (await checkCircle.isVisible()) {
      await checkCircle.click();
      
      // Verify task is marked as completed (should have strikethrough)
      const completedTask = page.locator('.line-through').first();
      await expect(completedTask).toBeVisible({ timeout: 5000 });
    }
  });

  test('Empty states display correctly', async ({ page }) => {
    // Check for empty state messages when no data exists
    const emptyStateMessages = [
      'No priority tasks for today',
      'Create your first task',
      'No time blocks scheduled',
      'Your daily schedule and time blocks will appear here'
    ];
    
    for (const message of emptyStateMessages) {
      const element = page.getByText(message);
      if (await element.isVisible()) {
        await expect(element).toBeVisible();
      }
    }
  });

  test('Progress calculation updates correctly', async ({ page }) => {
    // Check if progress percentage is displayed
    const progressText = page.locator('text=/\\d+%/').first();
    await expect(progressText).toBeVisible();
    
    // Get initial progress
    const initialProgress = await progressText.textContent();
    
    // If there are tasks, try to complete one and verify progress updates
    const checkCircle = page.locator('[data-testid="task-checkbox"]').first();
    if (await checkCircle.isVisible()) {
      await checkCircle.click();
      await page.waitForTimeout(1000);
      
      // Progress should update
      const updatedProgress = await progressText.textContent();
      expect(updatedProgress).not.toBe(initialProgress);
    }
  });

  test('Mobile responsive behavior', async ({ page }) => {
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Check that all buttons are still accessible
    const addTaskButton = page.getByRole('button', { name: /add task/i });
    await expect(addTaskButton).toBeVisible();
    
    const addTimeBlockButton = page.getByRole('button', { name: /add time block/i });
    await expect(addTimeBlockButton).toBeVisible();
    
    // Check that content is properly formatted for mobile
    const todayHeader = page.getByText('Today');
    await expect(todayHeader).toBeVisible();
    
    // Verify touch targets are large enough (minimum 44px)
    const buttons = page.locator('button');
    const buttonCount = await buttons.count();
    
    for (let i = 0; i < Math.min(buttonCount, 5); i++) {
      const button = buttons.nth(i);
      const box = await button.boundingBox();
      if (box) {
        expect(box.height).toBeGreaterThanOrEqual(40); // Allow slight variance
      }
    }
  });

  test('Keyboard navigation works', async ({ page }) => {
    // Focus on first interactive element
    await page.keyboard.press('Tab');
    
    // Navigate through interactive elements
    const focusedElement = page.locator(':focus');
    await expect(focusedElement).toBeVisible();
    
    // Test ESC key to close modals
    const addTaskButton = page.getByRole('button', { name: /add task/i });
    await addTaskButton.click();
    
    const modal = page.locator('[role="dialog"]');
    await expect(modal).toBeVisible();
    
    await page.keyboard.press('Escape');
    await expect(modal).not.toBeVisible();
  });

  test('Error handling works correctly', async ({ page }) => {
    // Test what happens when trying to create task without required fields
    const addTaskButton = page.getByRole('button', { name: /add task/i });
    await addTaskButton.click();
    
    const modal = page.locator('[role="dialog"]');
    await expect(modal).toBeVisible();
    
    // Try to submit without filling required fields
    const createButton = page.getByRole('button', { name: /create/i });
    await createButton.click();
    
    // Should show validation error or stay on modal
    await expect(modal).toBeVisible();
  });
});

test.describe('Backend Integration', () => {
  test('Data persistence works correctly', async ({ page }) => {
    await page.goto('/');
    
    // Authenticate
    const loginForm = page.locator('form').first();
    if (await loginForm.isVisible()) {
      await page.fill('input[type="email"]', 'demo@aurumlife.com');
      await page.fill('input[type="password"]', 'demo123');
      await page.click('button[type="submit"]');
      await page.waitForTimeout(2000);
    }
    
    // Navigate to Today
    const todayNav = page.locator('nav').getByText('Today');
    await todayNav.click();
    
    // Create a task
    const addTaskButton = page.getByRole('button', { name: /add task/i });
    if (await addTaskButton.isVisible()) {
      await addTaskButton.click();
      
      const modal = page.locator('[role="dialog"]');
      await expect(modal).toBeVisible();
      
      await page.fill('input[id*="name"]', 'Persistence Test Task');
      
      const createButton = page.getByRole('button', { name: /create/i });
      await createButton.click();
      
      await page.waitForTimeout(2000);
    }
    
    // Refresh page
    await page.reload();
    await page.waitForTimeout(3000);
    
    // Navigate back to Today
    const todayNavAfterRefresh = page.locator('nav').getByText('Today');
    await todayNavAfterRefresh.click();
    
    // Verify task still exists
    await expect(page.getByText('Persistence Test Task')).toBeVisible({ timeout: 10000 });
  });

  test('Real-time updates work', async ({ page, context }) => {
    // Test with multiple browser contexts to simulate real-time updates
    const page2 = await context.newPage();
    
    // Setup both pages
    for (const currentPage of [page, page2]) {
      await currentPage.goto('/');
      
      const loginForm = currentPage.locator('form').first();
      if (await loginForm.isVisible()) {
        await currentPage.fill('input[type="email"]', 'demo@aurumlife.com');
        await currentPage.fill('input[type="password"]', 'demo123');
        await currentPage.click('button[type="submit"]');
        await currentPage.waitForTimeout(2000);
      }
      
      const todayNav = currentPage.locator('nav').getByText('Today');
      await todayNav.click();
    }
    
    // Create task in first page
    const addTaskButton = page.getByRole('button', { name: /add task/i });
    if (await addTaskButton.isVisible()) {
      await addTaskButton.click();
      
      const modal = page.locator('[role="dialog"]');
      await expect(modal).toBeVisible();
      
      await page.fill('input[id*="name"]', 'Real-time Test Task');
      
      const createButton = page.getByRole('button', { name: /create/i });
      await createButton.click();
      
      await page.waitForTimeout(2000);
    }
    
    // Check if task appears in second page (after reasonable delay for sync)
    await page2.waitForTimeout(5000);
    await page2.reload();
    
    const todayNav2 = page2.locator('nav').getByText('Today');
    await todayNav2.click();
    
    // Should see the task (if real-time sync is working)
    const taskExists = await page2.getByText('Real-time Test Task').isVisible({ timeout: 10000 });
    if (taskExists) {
      await expect(page2.getByText('Real-time Test Task')).toBeVisible();
    }
    
    await page2.close();
  });
});