/**
 * End-to-End User Workflow Tests
 * Complete user journey testing with Playwright
 */

import { test, expect } from '@playwright/test';

test.describe('Complete User Workflows', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('New user completes full onboarding flow', async ({ page }) => {
    // Wait for app to load
    await expect(page.getByText(/initializing aurum life/i)).toBeVisible();
    
    // Should eventually show login or go straight to onboarding
    await page.waitForSelector('[data-testid="login-screen"], [data-testid="onboarding-flow"]', {
      timeout: 10000
    });

    // If login screen appears, simulate demo login
    const loginScreen = page.locator('[data-testid="login-screen"]');
    if (await loginScreen.isVisible()) {
      await page.click('button:has-text("Sign In")');
      await page.waitForTimeout(2000); // Wait for auth
    }

    // Should now see onboarding flow
    await expect(page.getByText(/welcome to aurum life/i)).toBeVisible();

    // Step 1: Welcome Screen
    await page.click('button:has-text("Get Started")');

    // Step 2: PAPT Framework Explanation
    await expect(page.getByText(/papt framework/i)).toBeVisible();
    await page.click('button:has-text("Continue")');

    // Step 3: Profile Setup
    await expect(page.getByText(/tell us about yourself/i)).toBeVisible();
    await page.fill('input[placeholder*="name"]', 'E2E Test User');
    await page.click('button:has-text("Continue")');

    // Step 4: Pillar Creation
    await expect(page.getByText(/create your first pillar/i)).toBeVisible();
    await page.fill('input[placeholder*="pillar"]', 'Health & Wellness');
    await page.fill('textarea[placeholder*="description"]', 'Focus on physical and mental health');
    await page.click('button:has-text("Create Pillar")');

    // Step 5: Template Selection
    await expect(page.getByText(/choose a template/i)).toBeVisible();
    await page.click('button:has-text("Personal Development")');
    await page.click('button:has-text("Apply Template")');

    // Step 6: Ready to Launch
    await expect(page.getByText(/ready to launch/i)).toBeVisible();
    await page.click('button:has-text("Launch Aurum Life")');

    // Should now see main dashboard
    await expect(page.getByText(/welcome to your personal operating system/i)).toBeVisible();
    
    // Verify pillar was created
    await expect(page.getByText('Health & Wellness')).toBeVisible();
  });

  test('Existing user navigates through main sections', async ({ page }) => {
    // Skip to authenticated state
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // If on login screen, sign in
    const loginButton = page.locator('button:has-text("Sign In")');
    if (await loginButton.isVisible()) {
      await loginButton.click();
      await page.waitForTimeout(2000);
    }

    // Should see dashboard
    await expect(page.getByText(/welcome to your personal operating system/i)).toBeVisible();

    // Navigate to Today section
    await page.click('button:has-text("Today")');
    await expect(page.getByText(/today's agenda/i)).toBeVisible();

    // Navigate to Pillars section
    await page.click('button:has-text("Pillars")');
    await expect(page.getByText(/life pillars/i)).toBeVisible();

    // Navigate to Projects section
    await page.click('button:has-text("Projects")');
    await expect(page.getByText(/active projects/i)).toBeVisible();

    // Navigate to Tasks section
    await page.click('button:has-text("Tasks")');
    await expect(page.getByText(/task management/i)).toBeVisible();

    // Navigate to Journal section
    await page.click('button:has-text("Journal")');
    await expect(page.getByText(/journal entries/i)).toBeVisible();

    // Navigate to Analytics section
    await page.click('button:has-text("Analytics")');
    await expect(page.getByText(/life analytics/i)).toBeVisible();
  });

  test('User creates and manages a complete goal hierarchy', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Skip auth if needed
    const loginButton = page.locator('button:has-text("Sign In")');
    if (await loginButton.isVisible()) {
      await loginButton.click();
      await page.waitForTimeout(2000);
    }

    // Navigate to Pillars section
    await page.click('button:has-text("Pillars")');
    await expect(page.getByText(/life pillars/i)).toBeVisible();

    // Create a new pillar
    await page.click('button:has-text("Add Pillar")');
    await page.fill('input[placeholder*="title"]', 'Career Growth');
    await page.fill('textarea[placeholder*="description"]', 'Professional development and career advancement');
    await page.click('button[color="#3B82F6"]'); // Select blue color
    await page.click('button:has-text("Create")');

    // Verify pillar was created
    await expect(page.getByText('Career Growth')).toBeVisible();

    // Click on the pillar to expand areas
    await page.click('text=Career Growth');

    // Create an area within the pillar
    await page.click('button:has-text("Add Area")');
    await page.fill('input[placeholder*="area"]', 'Skill Development');
    await page.fill('textarea[placeholder*="description"]', 'Learning new technologies and improving existing skills');
    await page.click('button:has-text("Create Area")');

    // Navigate to the new area
    await page.click('text=Skill Development');

    // Create a project within the area
    await page.click('button:has-text("Add Project")');
    await page.fill('input[placeholder*="project"]', 'Learn React 18');
    await page.fill('textarea[placeholder*="description"]', 'Master React 18 new features and concurrent mode');
    await page.selectOption('select[name="priority"]', 'high');
    await page.click('button:has-text("Create Project")');

    // Navigate to the new project
    await page.click('text=Learn React 18');

    // Create tasks within the project
    await page.click('button:has-text("Add Task")');
    await page.fill('input[placeholder*="task"]', 'Complete React 18 tutorial series');
    await page.fill('textarea[placeholder*="description"]', 'Follow comprehensive React 18 tutorial');
    await page.fill('input[type="number"]', '120'); // Estimated duration
    await page.click('button:has-text("Create Task")');

    // Verify the complete hierarchy was created
    await expect(page.getByText('Learn React 18')).toBeVisible();
    await expect(page.getByText('Complete React 18 tutorial series')).toBeVisible();
  });

  test('User interacts with AI coaching features', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Skip auth if needed
    const loginButton = page.locator('button:has-text("Sign In")');
    if (await loginButton.isVisible()) {
      await loginButton.click();
      await page.waitForTimeout(2000);
    }

    // Navigate to AI Insights section
    await page.click('button:has-text("AI Insights")');
    await expect(page.getByText(/intelligent life coach/i)).toBeVisible();

    // Generate AI insights
    await page.click('button:has-text("Generate Insights")');
    await expect(page.getByText(/generating insights/i)).toBeVisible();

    // Wait for insights to load
    await page.waitForTimeout(3000);

    // Interact with AI chat
    const chatInput = page.locator('input[placeholder*="Ask your life coach"]');
    await chatInput.fill('How can I improve my productivity?');
    await page.click('button:has-text("Send")');

    // Wait for AI response
    await page.waitForTimeout(2000);
    await expect(page.getByText(/analyzing your question/i)).toBeVisible();

    // Check for AI recommendations
    await page.click('button:has-text("Get Recommendations")');
    await page.waitForTimeout(2000);
    await expect(page.getByText(/personalized recommendations/i)).toBeVisible();
  });

  test('User collaborates with team members', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Skip auth if needed
    const loginButton = page.locator('button:has-text("Sign In")');
    if (await loginButton.isVisible()) {
      await loginButton.click();
      await page.waitForTimeout(2000);
    }

    // Navigate to Team Collaboration
    await page.click('button:has-text("Team")');
    await expect(page.getByText(/team collaboration/i)).toBeVisible();

    // Share a goal with team
    await page.click('button:has-text("Share Goal")');
    await page.selectOption('select[name="goal"]', { index: 0 });
    await page.click('button:has-text("Share with Team")');

    // Send team message
    const messageInput = page.locator('input[placeholder*="Message your team"]');
    await messageInput.fill('Great progress everyone! Keep up the momentum.');
    await page.click('button:has-text("Send Message")');

    // Verify message was sent
    await expect(page.getByText(/great progress everyone/i)).toBeVisible();

    // Check team analytics
    await page.click('button:has-text("Team Analytics")');
    await expect(page.getByText(/team performance/i)).toBeVisible();
  });

  test('Mobile user experience workflow', async ({ page, isMobile }) => {
    test.skip(!isMobile, 'Mobile-specific test');

    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Skip auth if needed
    const loginButton = page.locator('button:has-text("Sign In")');
    if (await loginButton.isVisible()) {
      await loginButton.click();
      await page.waitForTimeout(2000);
    }

    // Should see mobile bottom navigation
    await expect(page.locator('[data-testid="bottom-navigation"]')).toBeVisible();

    // Test bottom navigation
    await page.click('[data-testid="nav-today"]');
    await expect(page.getByText(/today's agenda/i)).toBeVisible();

    await page.click('[data-testid="nav-tasks"]');
    await expect(page.getByText(/task management/i)).toBeVisible();

    // Test mobile menu
    await page.click('button[aria-label="Open mobile menu"]');
    await expect(page.getByRole('dialog')).toBeVisible();

    // Navigate via mobile menu
    await page.click('button:has-text("Journal")');
    await expect(page.getByText(/journal entries/i)).toBeVisible();

    // Test floating action button
    const fab = page.locator('[data-testid="floating-action-button"]');
    await expect(fab).toBeVisible();
    await fab.click();

    // Should open quick capture
    await expect(page.getByText(/quick capture/i)).toBeVisible();

    // Test swipe gesture (if supported)
    await page.touchscreen.tap(100, 300);
    await page.mouse.move(100, 300);
    await page.mouse.down();
    await page.mouse.move(300, 300);
    await page.mouse.up();
  });

  test('User manages settings and preferences', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Skip auth if needed
    const loginButton = page.locator('button:has-text("Sign In")');
    if (await loginButton.isVisible()) {
      await loginButton.click();
      await page.waitForTimeout(2000);
    }

    // Navigate to Settings
    await page.click('button:has-text("Settings")');
    await expect(page.getByText(/settings/i)).toBeVisible();

    // Test Account Settings
    await page.click('button:has-text("Account")');
    await expect(page.getByText(/account information/i)).toBeVisible();

    // Update profile
    await page.fill('input[name="displayName"]', 'Updated Test User');
    await page.click('button:has-text("Save Changes")');
    await expect(page.getByText(/saved successfully/i)).toBeVisible();

    // Test Preferences
    await page.click('button:has-text("Preferences")');
    await expect(page.getByText(/appearance/i)).toBeVisible();

    // Change font size
    await page.click('button:has-text("Large")');
    await expect(page.locator('html')).toHaveAttribute('style', /font-size.*18px/);

    // Test Privacy Settings
    await page.click('button:has-text("Privacy")');
    await expect(page.getByText(/privacy controls/i)).toBeVisible();

    // Update privacy settings
    await page.click('input[name="shareAnalytics"]');
    await page.click('button:has-text("Save Privacy Settings")');
    await expect(page.getByText(/privacy settings updated/i)).toBeVisible();

    // Test Notification Settings
    await page.click('button:has-text("Notifications")');
    await expect(page.getByText(/notification preferences/i)).toBeVisible();

    // Toggle notifications
    await page.click('input[name="emailNotifications"]');
    await page.click('button:has-text("Save Notification Settings")');
  });

  test('Accessibility workflow with keyboard navigation', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Skip auth if needed
    const loginButton = page.locator('button:has-text("Sign In")');
    if (await loginButton.isVisible()) {
      await loginButton.click();
      await page.waitForTimeout(2000);
    }

    // Test keyboard navigation
    await page.keyboard.press('Tab');
    await expect(page.locator(':focus')).toBeVisible();

    // Navigate through main sections with keyboard
    for (let i = 0; i < 5; i++) {
      await page.keyboard.press('Tab');
      const focusedElement = page.locator(':focus');
      await expect(focusedElement).toBeVisible();
    }

    // Test Enter key activation
    await page.keyboard.press('Enter');
    
    // Test Escape key to close modals
    await page.keyboard.press('Escape');

    // Test arrow key navigation in lists
    await page.click('button:has-text("Tasks")');
    await page.keyboard.press('ArrowDown');
    await page.keyboard.press('ArrowUp');

    // Verify screen reader announcements (aria-live regions)
    const liveRegions = page.locator('[aria-live]');
    await expect(liveRegions.first()).toBeVisible();
  });

  test('Error handling and recovery workflows', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Skip auth if needed
    const loginButton = page.locator('button:has-text("Sign In")');
    if (await loginButton.isVisible()) {
      await loginButton.click();
      await page.waitForTimeout(2000);
    }

    // Test network error recovery
    await page.route('**/api/**', route => route.abort('failed'));
    
    // Try to perform an action that requires network
    await page.click('button:has-text("Generate Insights")');
    
    // Should show error message
    await expect(page.getByText(/connection error|failed to load/i)).toBeVisible();
    
    // Should show retry option
    const retryButton = page.locator('button:has-text("Retry")');
    await expect(retryButton).toBeVisible();
    
    // Restore network and retry
    await page.unroute('**/api/**');
    await retryButton.click();

    // Test form validation errors
    await page.click('button:has-text("Add Task")');
    await page.click('button:has-text("Create Task")'); // Submit without filling required fields
    
    // Should show validation errors
    await expect(page.getByText(/required|cannot be empty/i)).toBeVisible();

    // Fill form correctly
    await page.fill('input[placeholder*="task"]', 'Test Task');
    await page.click('button:has-text("Create Task")');
    
    // Should succeed
    await expect(page.getByText('Test Task')).toBeVisible();
  });

  test('Performance and loading state workflows', async ({ page }) => {
    await page.goto('/');
    
    // Test loading states
    await expect(page.getByText(/initializing|loading/i)).toBeVisible();
    
    // Wait for app to fully load
    await page.waitForLoadState('networkidle');
    
    // Skip auth if needed
    const loginButton = page.locator('button:has-text("Sign In")');
    if (await loginButton.isVisible()) {
      await loginButton.click();
      await page.waitForTimeout(2000);
    }

    // Test lazy loading of sections
    await page.click('button:has-text("Analytics")');
    
    // Should show loading state initially
    await expect(page.locator('[data-testid="skeleton-loading"]')).toBeVisible();
    
    // Then load actual content
    await expect(page.getByText(/analytics dashboard/i)).toBeVisible();

    // Test infinite scroll or pagination
    const tasksList = page.locator('[data-testid="tasks-list"]');
    if (await tasksList.isVisible()) {
      // Scroll to bottom to trigger loading more items
      await tasksList.scrollIntoViewIfNeeded();
      await page.mouse.wheel(0, 1000);
      
      // Should show loading indicator for additional items
      await expect(page.getByText(/loading more/i)).toBeVisible();
    }
  });
});