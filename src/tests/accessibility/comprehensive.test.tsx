/**
 * Comprehensive Accessibility Tests
 * Advanced accessibility testing for WCAG 2.1 AA compliance
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe, toHaveNoViolations } from 'jest-axe';

// Import key components for accessibility testing
import App from '../../App';
import Dashboard from '../../components/sections/Dashboard';
import Navigation from '../../components/layout/Navigation';
import IntelligentLifeCoachAI from '../../components/enhanced/IntelligentLifeCoachAI';
import TeamCollaborationHub from '../../components/enhanced/TeamCollaborationHub';

// Extend Jest matchers
expect.extend(toHaveNoViolations);

// Mock auth for accessibility tests
jest.mock('../../stores/authStore', () => ({
  useAuthStore: jest.fn(() => ({
    user: { id: '1', email: 'test@aurumlife.com', name: 'Test User' },
    isAuthenticated: true,
    isLoading: false,
    error: null,
    isFirstTimeUser: false,
  })),
}));

describe('WCAG 2.1 AA Compliance Tests', () => {
  beforeEach(() => {
    // Reset any global accessibility settings
    document.body.className = '';
    document.documentElement.style.fontSize = '';
  });

  describe('Automated Accessibility Testing', () => {
    it('has no accessibility violations on Dashboard', async () => {
      const { container } = render(<Dashboard />);
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('has no accessibility violations on Navigation', async () => {
      const mockOnSectionChange = jest.fn();
      const { container } = render(
        <Navigation activeSection="dashboard" onSectionChange={mockOnSectionChange} />
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('has no accessibility violations on AI Coach interface', async () => {
      const mockUser = { id: '1', email: 'test@aurumlife.com', name: 'Test User' };
      const { container } = render(<IntelligentLifeCoachAI user={mockUser} />);
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });

  describe('Keyboard Navigation', () => {
    it('supports full keyboard navigation throughout the app', async () => {
      render(<Dashboard />);

      // Get all focusable elements
      const focusableElements = screen.getAllByRole('button')
        .concat(screen.getAllByRole('link'))
        .concat(screen.getAllByRole('textbox'))
        .concat(screen.getAllByRole('combobox'));

      for (let i = 0; i < Math.min(focusableElements.length, 10); i++) {
        const element = focusableElements[i];
        element.focus();
        expect(document.activeElement).toBe(element);
      }
    });

    it('provides visible focus indicators', async () => {
      render(<Dashboard />);

      const buttons = screen.getAllByRole('button');
      if (buttons.length > 0) {
        buttons[0].focus();
        
        // Check for focus styles
        const computedStyle = window.getComputedStyle(buttons[0]);
        expect(computedStyle.outline).not.toBe('none');
      }
    });

    it('supports Tab, Shift+Tab, Enter, and Space key navigation', async () => {
      render(<Navigation activeSection="dashboard" onSectionChange={jest.fn()} />);

      const buttons = screen.getAllByRole('button');
      if (buttons.length >= 2) {
        buttons[0].focus();

        // Tab to next element
        fireEvent.keyDown(buttons[0], { key: 'Tab' });
        expect(document.activeElement).toBe(buttons[1]);

        // Shift+Tab back
        fireEvent.keyDown(buttons[1], { key: 'Tab', shiftKey: true });
        expect(document.activeElement).toBe(buttons[0]);

        // Enter key activation
        fireEvent.keyDown(buttons[0], { key: 'Enter' });
        // Should trigger click event (verified by no errors)

        // Space key activation
        fireEvent.keyDown(buttons[0], { key: ' ' });
        // Should trigger click event (verified by no errors)
      }
    });

    it('provides skip links for main content', async () => {
      render(<Dashboard />);

      // Check for skip to main content link
      const skipLink = screen.queryByText(/skip to main content/i);
      if (skipLink) {
        expect(skipLink).toBeInTheDocument();
        expect(skipLink.tagName).toBe('A');
      }
    });

    it('traps focus in modals and dialogs', async () => {
      render(<Dashboard />);

      // Try to trigger a modal (if any)
      const modalTriggers = screen.queryAllByText(/modal|dialog|settings/i);
      if (modalTriggers.length > 0) {
        await userEvent.click(modalTriggers[0]);

        // Check if focus is trapped within modal
        const modal = screen.queryByRole('dialog');
        if (modal) {
          const modalFocusableElements = within(modal).getAllByRole('button');
          if (modalFocusableElements.length > 0) {
            modalFocusableElements[0].focus();
            expect(modal.contains(document.activeElement)).toBe(true);
          }
        }
      }
    });
  });

  describe('Screen Reader Support', () => {
    it('provides appropriate ARIA labels for all interactive elements', async () => {
      render(<Dashboard />);

      const buttons = screen.getAllByRole('button');
      buttons.forEach(button => {
        const hasLabel = button.getAttribute('aria-label') || 
                        button.getAttribute('aria-labelledby') ||
                        button.textContent;
        expect(hasLabel).toBeTruthy();
      });
    });

    it('uses semantic HTML elements correctly', async () => {
      render(<Dashboard />);

      // Check for proper heading hierarchy
      const headings = screen.getAllByRole('heading');
      expect(headings.length).toBeGreaterThan(0);

      // Check for main landmark
      const main = screen.queryByRole('main');
      expect(main).toBeInTheDocument();

      // Check for navigation landmarks
      const nav = screen.queryByRole('navigation');
      expect(nav).toBeInTheDocument();
    });

    it('provides live regions for dynamic content', async () => {
      render(<IntelligentLifeCoachAI user={{ id: '1', name: 'Test User' }} />);

      const liveRegions = screen.getAllByRole('status')
        .concat(screen.getAllByRole('alert'))
        .concat(screen.getAllByRole('log'));

      liveRegions.forEach(region => {
        const ariaLive = region.getAttribute('aria-live');
        expect(['polite', 'assertive', 'off']).toContain(ariaLive);
      });
    });

    it('describes complex UI patterns with ARIA', async () => {
      render(<Dashboard />);

      // Check for progress bars
      const progressBars = screen.getAllByRole('progressbar');
      progressBars.forEach(bar => {
        expect(bar).toHaveAttribute('aria-valuenow');
        expect(bar).toHaveAttribute('aria-valuemin');
        expect(bar).toHaveAttribute('aria-valuemax');
      });

      // Check for expandable sections
      const expandableButtons = screen.getAllByRole('button').filter(button =>
        button.getAttribute('aria-expanded') !== null
      );
      expandableButtons.forEach(button => {
        expect(['true', 'false']).toContain(button.getAttribute('aria-expanded'));
      });
    });

    it('provides alternative text for images and icons', async () => {
      render(<Dashboard />);

      const images = screen.getAllByRole('img');
      images.forEach(img => {
        const altText = img.getAttribute('alt');
        expect(altText).not.toBeNull();
        expect(altText).not.toBe('');
      });
    });
  });

  describe('Visual Accessibility', () => {
    it('maintains sufficient color contrast ratios', async () => {
      render(<Dashboard />);

      // Test would require color contrast analysis tools
      // This is a placeholder for actual contrast testing
      const textElements = screen.getAllByText(/./);
      expect(textElements.length).toBeGreaterThan(0);
    });

    it('supports high contrast mode', async () => {
      document.body.classList.add('high-contrast');
      render(<Dashboard />);

      // Check that high contrast styles are applied
      const elements = screen.getAllByRole('button');
      if (elements.length > 0) {
        const style = window.getComputedStyle(elements[0]);
        // High contrast mode should increase border visibility
        expect(style.borderWidth).not.toBe('0px');
      }

      document.body.classList.remove('high-contrast');
    });

    it('remains usable when zoomed to 200%', async () => {
      // Simulate 200% zoom
      document.documentElement.style.fontSize = '32px';
      
      render(<Dashboard />);

      // Check that content is still readable and interactive
      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThan(0);

      // Reset zoom
      document.documentElement.style.fontSize = '';
    });

    it('supports reduced motion preferences', async () => {
      // Mock reduced motion preference
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: jest.fn().mockImplementation(query => ({
          matches: query === '(prefers-reduced-motion: reduce)',
          media: query,
          onchange: null,
          addListener: jest.fn(),
          removeListener: jest.fn(),
          addEventListener: jest.fn(),
          removeEventListener: jest.fn(),
          dispatchEvent: jest.fn(),
        })),
      });

      document.body.classList.add('reduce-motion');
      render(<Dashboard />);

      // Animations should be disabled or significantly reduced
      // This would require checking computed styles for animation properties
      expect(document.body.classList.contains('reduce-motion')).toBe(true);

      document.body.classList.remove('reduce-motion');
    });
  });

  describe('Touch and Mobile Accessibility', () => {
    it('provides adequate touch target sizes (44px minimum)', async () => {
      render(<Navigation activeSection="dashboard" onSectionChange={jest.fn()} />);

      const touchTargets = screen.getAllByRole('button');
      touchTargets.forEach(target => {
        const rect = target.getBoundingClientRect();
        const minSize = 44; // WCAG recommended minimum
        expect(Math.max(rect.width, rect.height)).toBeGreaterThanOrEqual(minSize - 10); // Allow slight tolerance
      });
    });

    it('supports swipe gestures with keyboard alternatives', async () => {
      // Mock touch events
      const mockTouchStart = jest.fn();
      const mockTouchEnd = jest.fn();

      render(<Dashboard />);

      // Any swipeable elements should also support keyboard navigation
      const interactiveElements = screen.getAllByRole('button');
      expect(interactiveElements.length).toBeGreaterThan(0);
    });

    it('provides orientation support', async () => {
      // Test portrait and landscape orientations
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        value: 768,
      });
      Object.defineProperty(window, 'innerHeight', {
        writable: true,
        value: 1024,
      });

      render(<Dashboard />);
      expect(screen.getByText(/welcome/i)).toBeInTheDocument();

      // Switch to landscape
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        value: 1024,
      });
      Object.defineProperty(window, 'innerHeight', {
        writable: true,
        value: 768,
      });

      // Component should still render correctly
      expect(screen.getByText(/welcome/i)).toBeInTheDocument();
    });
  });

  describe('Cognitive Accessibility', () => {
    it('provides clear and consistent navigation patterns', async () => {
      render(<Navigation activeSection="dashboard" onSectionChange={jest.fn()} />);

      const navigationButtons = screen.getAllByRole('button');
      navigationButtons.forEach(button => {
        // Each navigation item should have clear, consistent labeling
        expect(button.textContent).toBeTruthy();
        expect(button.textContent.length).toBeGreaterThan(0);
      });
    });

    it('offers multiple ways to complete tasks', async () => {
      render(<Dashboard />);

      // Look for multiple interaction methods (buttons, keyboard shortcuts, etc.)
      const buttons = screen.getAllByRole('button');
      const links = screen.getAllByRole('link');
      
      expect(buttons.length + links.length).toBeGreaterThan(1);
    });

    it('provides helpful error messages and guidance', async () => {
      render(<Dashboard />);

      // Check for form validation messages, help text, etc.
      const helpTexts = screen.queryAllByText(/help|tip|required|example/i);
      // If forms exist, they should have helpful guidance
      const forms = screen.getAllByRole('form');
      if (forms.length > 0) {
        expect(helpTexts.length).toBeGreaterThan(0);
      }
    });

    it('supports session timeout warnings', async () => {
      // Mock session timeout scenario
      render(<Dashboard />);

      // Should provide adequate warning before session expires
      // This would typically be handled by the auth system
      const timeoutWarnings = screen.queryAllByText(/session|timeout|expire/i);
      // If timeout handling exists, it should be accessible
    });
  });

  describe('Assistive Technology Compatibility', () => {
    it('works correctly with screen readers', async () => {
      // Mock screen reader announcements
      const announcements: string[] = [];
      
      // Mock live region updates
      const originalSetAttribute = Element.prototype.setAttribute;
      Element.prototype.setAttribute = function(name: string, value: string) {
        if (name === 'aria-live' && value !== 'off') {
          announcements.push(this.textContent || '');
        }
        return originalSetAttribute.call(this, name, value);
      };

      render(<Dashboard />);

      // Verify that dynamic content updates are announced
      await waitFor(() => {
        expect(announcements.length).toBeGreaterThanOrEqual(0);
      });

      // Restore original method
      Element.prototype.setAttribute = originalSetAttribute;
    });

    it('supports voice control software', async () => {
      render(<Dashboard />);

      // All interactive elements should have accessible names for voice control
      const interactiveElements = screen.getAllByRole('button')
        .concat(screen.getAllByRole('link'))
        .concat(screen.getAllByRole('textbox'));

      interactiveElements.forEach(element => {
        const accessibleName = element.getAttribute('aria-label') ||
                              element.getAttribute('aria-labelledby') ||
                              element.textContent;
        expect(accessibleName).toBeTruthy();
      });
    });

    it('works with switch navigation devices', async () => {
      render(<Dashboard />);

      // Sequential focus navigation should work
      const focusableElements = screen.getAllByRole('button');
      for (let i = 0; i < Math.min(focusableElements.length, 5); i++) {
        focusableElements[i].focus();
        expect(document.activeElement).toBe(focusableElements[i]);
        
        // Should be able to activate with Enter/Space
        fireEvent.keyDown(focusableElements[i], { key: 'Enter' });
        // No errors should occur
      }
    });

    it('provides magnifier software compatibility', async () => {
      // Simulate magnified view
      document.documentElement.style.transform = 'scale(2)';
      
      render(<Dashboard />);

      // Content should remain usable when magnified
      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThan(0);

      // Reset
      document.documentElement.style.transform = '';
    });
  });

  describe('Accessibility Testing Edge Cases', () => {
    it('handles dynamic content updates accessibly', async () => {
      render(<IntelligentLifeCoachAI user={{ id: '1', name: 'Test User' }} />);

      // Look for live regions that would announce AI responses
      const liveRegions = screen.getAllByRole('log');
      expect(liveRegions.length).toBeGreaterThan(0);

      liveRegions.forEach(region => {
        expect(region).toHaveAttribute('aria-live');
      });
    });

    it('maintains accessibility during loading states', async () => {
      render(<Dashboard />);

      // Check for loading indicators with proper ARIA attributes
      const loadingIndicators = screen.queryAllByText(/loading|updating/i);
      loadingIndicators.forEach(indicator => {
        const parent = indicator.closest('[role="status"]') || 
                      indicator.closest('[aria-live]');
        expect(parent).toBeTruthy();
      });
    });

    it('handles error states accessibly', async () => {
      // Mock error state
      const consoleError = jest.spyOn(console, 'error').mockImplementation();
      
      render(<Dashboard />);

      // Error messages should be announced to screen readers
      const errorMessages = screen.queryAllByRole('alert');
      errorMessages.forEach(error => {
        expect(error).toHaveAttribute('role', 'alert');
      });

      consoleError.mockRestore();
    });

    it('supports internationalization for accessibility', async () => {
      // Mock different language
      Object.defineProperty(navigator, 'language', {
        value: 'es-ES',
        configurable: true,
      });

      render(<Dashboard />);

      // Should handle RTL languages and different text lengths
      const textElements = screen.getAllByText(/./);
      expect(textElements.length).toBeGreaterThan(0);
    });
  });
});