/**
 * Navigation Component Tests
 * Testing navigation functionality and section switching
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Navigation from '../../components/layout/Navigation';

describe('Navigation Component', () => {
  const mockOnSectionChange = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders all navigation sections', () => {
    render(
      <Navigation 
        activeSection="dashboard" 
        onSectionChange={mockOnSectionChange} 
      />
    );

    // Check for main navigation items
    expect(screen.getByText(/dashboard/i)).toBeInTheDocument();
    expect(screen.getByText(/today/i)).toBeInTheDocument();
    expect(screen.getByText(/pillars/i)).toBeInTheDocument();
    expect(screen.getByText(/areas/i)).toBeInTheDocument();
    expect(screen.getByText(/projects/i)).toBeInTheDocument();
    expect(screen.getByText(/tasks/i)).toBeInTheDocument();
  });

  it('highlights active section', () => {
    render(
      <Navigation 
        activeSection="pillars" 
        onSectionChange={mockOnSectionChange} 
      />
    );

    const pillarsButton = screen.getByRole('button', { name: /pillars/i });
    expect(pillarsButton).toHaveClass('bg-primary/20');
  });

  it('calls onSectionChange when section is clicked', () => {
    render(
      <Navigation 
        activeSection="dashboard" 
        onSectionChange={mockOnSectionChange} 
      />
    );

    const projectsButton = screen.getByRole('button', { name: /projects/i });
    fireEvent.click(projectsButton);

    expect(mockOnSectionChange).toHaveBeenCalledWith('projects');
  });

  it('renders with proper accessibility attributes', () => {
    render(
      <Navigation 
        activeSection="dashboard" 
        onSectionChange={mockOnSectionChange} 
      />
    );

    // Check for proper ARIA labels
    const buttons = screen.getAllByRole('button');
    buttons.forEach(button => {
      expect(button).toHaveAttribute('aria-label');
    });
  });

  it('supports keyboard navigation', () => {
    render(
      <Navigation 
        activeSection="dashboard" 
        onSectionChange={mockOnSectionChange} 
      />
    );

    const firstButton = screen.getByRole('button', { name: /dashboard/i });
    firstButton.focus();

    // Simulate Tab key to move to next button
    fireEvent.keyDown(firstButton, { key: 'Tab' });
    
    expect(document.activeElement).toBe(firstButton);
  });

  it('handles settings section correctly', () => {
    render(
      <Navigation 
        activeSection="settings" 
        onSectionChange={mockOnSectionChange} 
      />
    );

    const settingsButton = screen.getByRole('button', { name: /settings/i });
    expect(settingsButton).toHaveClass('bg-primary/20');
  });

  it('displays Phase 4 features', () => {
    render(
      <Navigation 
        activeSection="dashboard" 
        onSectionChange={mockOnSectionChange} 
      />
    );

    // Check for Phase 4 feature sections
    expect(screen.getByText(/ai insights/i)).toBeInTheDocument();
    expect(screen.getByText(/team collaboration/i)).toBeInTheDocument();
    expect(screen.getByText(/analytics/i)).toBeInTheDocument();
    expect(screen.getByText(/integrations/i)).toBeInTheDocument();
  });

  it('handles section changes with settings subsections', () => {
    render(
      <Navigation 
        activeSection="settings" 
        onSectionChange={mockOnSectionChange} 
      />
    );

    const accountButton = screen.getByRole('button', { name: /account/i });
    fireEvent.click(accountButton);

    expect(mockOnSectionChange).toHaveBeenCalledWith('settings', 'account');
  });

  it('renders mobile-friendly layout', () => {
    // Mock mobile viewport
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375,
    });

    render(
      <Navigation 
        activeSection="dashboard" 
        onSectionChange={mockOnSectionChange} 
      />
    );

    // Should render without issues on mobile
    expect(screen.getByText(/dashboard/i)).toBeInTheDocument();
  });

  it('shows proper icons for each section', () => {
    render(
      <Navigation 
        activeSection="dashboard" 
        onSectionChange={mockOnSectionChange} 
      />
    );

    // Check that icons are rendered (Lucide React icons)
    const buttons = screen.getAllByRole('button');
    buttons.forEach(button => {
      const svg = button.querySelector('svg');
      expect(svg).toBeInTheDocument();
    });
  });

  it('handles rapid section changes', () => {
    render(
      <Navigation 
        activeSection="dashboard" 
        onSectionChange={mockOnSectionChange} 
      />
    );

    const buttons = screen.getAllByRole('button');
    
    // Rapidly click multiple buttons
    buttons.slice(0, 3).forEach(button => {
      fireEvent.click(button);
    });

    expect(mockOnSectionChange).toHaveBeenCalledTimes(3);
  });
});

describe('Navigation Integration Tests', () => {
  it('maintains state consistency across re-renders', () => {
    const { rerender } = render(
      <Navigation 
        activeSection="dashboard" 
        onSectionChange={jest.fn()} 
      />
    );

    rerender(
      <Navigation 
        activeSection="projects" 
        onSectionChange={jest.fn()} 
      />
    );

    const projectsButton = screen.getByRole('button', { name: /projects/i });
    expect(projectsButton).toHaveClass('bg-primary/20');
  });

  it('handles navigation within settings correctly', () => {
    const mockOnSectionChange = jest.fn();
    
    render(
      <Navigation 
        activeSection="settings" 
        onSectionChange={mockOnSectionChange} 
      />
    );

    // Navigate through settings subsections
    const privacyButton = screen.getByRole('button', { name: /privacy/i });
    fireEvent.click(privacyButton);

    expect(mockOnSectionChange).toHaveBeenCalledWith('settings', 'privacy');
  });
});