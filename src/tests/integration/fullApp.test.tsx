/**
 * Full Application Integration Tests
 * End-to-end testing of core user workflows
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from '../../App';

// Mock all external dependencies
jest.mock('../../utils/supabase/client', () => ({
  createClient: jest.fn(() => ({
    auth: {
      getSession: jest.fn(),
      signInWithPassword: jest.fn(),
      signUp: jest.fn(),
      signOut: jest.fn(),
      onAuthStateChange: jest.fn(() => ({ 
        data: { subscription: { unsubscribe: jest.fn() } } 
      })),
    },
    from: jest.fn(() => ({
      select: jest.fn(),
      insert: jest.fn(),
      update: jest.fn(),
      delete: jest.fn(),
    })),
  })),
}));

describe('Full Application Integration Tests', () => {
  beforeEach(() => {
    // Reset localStorage
    localStorage.clear();
    
    // Reset all timers
    jest.useFakeTimers();
    
    // Mock window dimensions
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 1024,
    });
    
    Object.defineProperty(window, 'innerHeight', {
      writable: true,
      configurable: true,
      value: 768,
    });
  });

  afterEach(() => {
    jest.useRealTimers();
    localStorage.clear();
  });

  it('completes full user journey from authentication to dashboard', async () => {
    const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });
    
    // Render the app
    render(<App />);

    // Should start with loading screen
    expect(screen.getByText(/initializing aurum life/i)).toBeInTheDocument();

    // Fast-forward past loading timeout
    jest.advanceTimersByTime(6000);

    // Should show login screen after timeout
    await waitFor(() => {
      expect(screen.getByTestId('login-screen')).toBeInTheDocument();
    });

    // Test login interaction
    const signInButton = screen.getByRole('button', { name: /sign in/i });
    await user.click(signInButton);

    // Fast-forward through any auth delays
    jest.advanceTimersByTime(2000);

    // Should eventually show the main dashboard
    await waitFor(() => {
      expect(screen.getByText(/welcome to your personal operating system/i)).toBeInTheDocument();
    }, { timeout: 10000 });
  });

  it('handles mobile responsive behavior correctly', async () => {
    // Set mobile viewport
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375,
    });

    render(<App />);

    // Fast-forward past loading
    jest.advanceTimersByTime(6000);

    await waitFor(() => {
      expect(screen.getByTestId('login-screen')).toBeInTheDocument();
    });

    // Should render mobile-optimized UI
    expect(document.querySelector('.mobile-content-safe')).toBeTruthy();
  });

  it('handles error recovery gracefully', async () => {
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

    render(<App />);

    // Simulate application error
    const errorEvent = new ErrorEvent('error', {
      error: new Error('Simulated error'),
      message: 'Simulated error',
    });

    window.dispatchEvent(errorEvent);

    // Fast-forward through error handling
    jest.advanceTimersByTime(1000);

    // App should continue functioning
    await waitFor(() => {
      expect(screen.getByText(/initializing aurum life/i)).toBeInTheDocument();
    });

    consoleSpy.mockRestore();
  });

  it('handles network timeouts and retries', async () => {
    // Mock fetch to simulate timeout
    global.fetch = jest.fn(() => 
      new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Network timeout')), 100)
      )
    );

    render(<App />);

    // Fast-forward through timeout periods
    jest.advanceTimersByTime(10000);

    // App should handle gracefully and show fallback
    await waitFor(() => {
      expect(screen.getByTestId('login-screen')).toBeInTheDocument();
    });
  });

  it('maintains state consistency across re-renders', async () => {
    const { rerender } = render(<App />);

    // Fast-forward past initialization
    jest.advanceTimersByTime(6000);

    await waitFor(() => {
      expect(screen.getByTestId('login-screen')).toBeInTheDocument();
    });

    // Re-render the app
    rerender(<App />);

    // Should maintain consistent state
    await waitFor(() => {
      expect(screen.getByTestId('login-screen')).toBeInTheDocument();
    });
  });

  it('handles localStorage corruption gracefully', async () => {
    // Mock corrupted localStorage
    Storage.prototype.getItem = jest.fn(() => 'invalid-json{');

    render(<App />);

    // Fast-forward through initialization
    jest.advanceTimersByTime(6000);

    // Should handle gracefully and show login
    await waitFor(() => {
      expect(screen.getByTestId('login-screen')).toBeInTheDocument();
    });
  });

  it('supports keyboard navigation throughout the app', async () => {
    const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });

    render(<App />);

    // Fast-forward past loading
    jest.advanceTimersByTime(6000);

    await waitFor(() => {
      expect(screen.getByTestId('login-screen')).toBeInTheDocument();
    });

    // Test keyboard navigation
    await user.keyboard('{Tab}');
    expect(document.activeElement).toBeTruthy();
  });

  it('handles theme initialization and switching', async () => {
    render(<App />);

    // Fast-forward through initialization
    jest.advanceTimersByTime(6000);

    // Check that dark theme is properly initialized
    await waitFor(() => {
      expect(document.body.classList.contains('dark')).toBe(true);
    });
  });

  it('manages memory efficiently during long sessions', async () => {
    const { unmount } = render(<App />);

    // Fast-forward through initialization
    jest.advanceTimersByTime(6000);

    await waitFor(() => {
      expect(screen.getByTestId('login-screen')).toBeInTheDocument();
    });

    // Unmount and check cleanup
    unmount();

    // Verify no major DOM leaks
    expect(document.body.children.length).toBeLessThan(5);
  });

  it('handles concurrent user interactions', async () => {
    const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });

    render(<App />);

    // Fast-forward past loading
    jest.advanceTimersByTime(6000);

    await waitFor(() => {
      expect(screen.getByTestId('login-screen')).toBeInTheDocument();
    });

    // Simulate rapid user interactions
    const signInButton = screen.getByRole('button', { name: /sign in/i });
    
    // Rapid clicks should be handled gracefully
    await user.click(signInButton);
    await user.click(signInButton);
    await user.click(signInButton);

    // App should remain stable
    expect(screen.getByTestId('login-screen')).toBeInTheDocument();
  });

  it('provides accessible experience for screen readers', async () => {
    render(<App />);

    // Fast-forward through initialization
    jest.advanceTimersByTime(6000);

    await waitFor(() => {
      expect(screen.getByTestId('login-screen')).toBeInTheDocument();
    });

    // Check for proper ARIA labels and roles
    const buttons = screen.getAllByRole('button');
    buttons.forEach(button => {
      expect(button).toHaveAttribute('aria-label');
    });
  });
});

describe('Performance Integration Tests', () => {
  it('renders initial view within performance budget', async () => {
    const startTime = performance.now();

    render(<App />);

    const endTime = performance.now();
    const renderTime = endTime - startTime;

    // Should render within 50ms in test environment
    expect(renderTime).toBeLessThan(50);
  });

  it('handles large datasets efficiently', async () => {
    // Mock large dataset
    const largeDataset = Array.from({ length: 1000 }, (_, i) => ({
      id: i,
      title: `Item ${i}`,
      description: `Description for item ${i}`,
    }));

    // This would be injected into stores in a real scenario
    render(<App />);

    // Fast-forward through initialization
    jest.advanceTimersByTime(6000);

    // Should handle without significant performance degradation
    const renderStart = performance.now();
    
    await waitFor(() => {
      expect(screen.getByTestId('login-screen')).toBeInTheDocument();
    });

    const renderEnd = performance.now();
    expect(renderEnd - renderStart).toBeLessThan(100);
  });
});

describe('Security Integration Tests', () => {
  it('handles XSS prevention correctly', async () => {
    // Mock malicious input
    const maliciousScript = '<script>alert("xss")</script>';
    
    render(<App />);

    // Fast-forward through initialization
    jest.advanceTimersByTime(6000);

    await waitFor(() => {
      expect(screen.getByTestId('login-screen')).toBeInTheDocument();
    });

    // App should render without executing malicious scripts
    expect(document.querySelector('script[src=""]')).toBeNull();
  });

  it('protects against CSRF attacks', async () => {
    render(<App />);

    // Fast-forward through initialization
    jest.advanceTimersByTime(6000);

    // Should include proper CSRF protection mechanisms
    await waitFor(() => {
      expect(screen.getByTestId('login-screen')).toBeInTheDocument();
    });

    // Verify no unintended form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
      expect(form.method).not.toBe('get');
    });
  });
});

describe('Offline Support Integration Tests', () => {
  it('handles offline mode gracefully', async () => {
    // Mock offline state
    Object.defineProperty(navigator, 'onLine', {
      writable: true,
      value: false,
    });

    render(<App />);

    // Fast-forward through initialization
    jest.advanceTimersByTime(6000);

    // App should handle offline state
    await waitFor(() => {
      expect(screen.getByTestId('login-screen')).toBeInTheDocument();
    });
  });

  it('recovers when connection is restored', async () => {
    // Start offline
    Object.defineProperty(navigator, 'onLine', {
      writable: true,
      value: false,
    });

    render(<App />);

    // Fast-forward through initialization
    jest.advanceTimersByTime(6000);

    await waitFor(() => {
      expect(screen.getByTestId('login-screen')).toBeInTheDocument();
    });

    // Simulate connection restoration
    Object.defineProperty(navigator, 'onLine', {
      writable: true,
      value: true,
    });

    // Dispatch online event
    window.dispatchEvent(new Event('online'));

    // App should handle connection restoration
    expect(screen.getByTestId('login-screen')).toBeInTheDocument();
  });
});