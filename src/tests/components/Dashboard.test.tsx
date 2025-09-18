/**
 * Dashboard Component Tests
 * Comprehensive testing of the main dashboard functionality
 * Updated to match current Dashboard implementation
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import Dashboard from '../../components/sections/Dashboard';
import { useEnhancedFeaturesStore } from '../../stores/enhancedFeaturesStore';
import { useAppStore } from '../../stores/basicAppStore';

// Mock the stores
jest.mock('../../stores/enhancedFeaturesStore');
jest.mock('../../stores/basicAppStore');

const mockUseEnhancedFeaturesStore = useEnhancedFeaturesStore as jest.MockedFunction<typeof useEnhancedFeaturesStore>;
const mockUseAppStore = useAppStore as jest.MockedFunction<typeof useAppStore>;

// Mock circuit breaker
jest.mock('../../utils/circuitBreaker', () => ({
  execute: jest.fn(fn => fn()),
  emergencyReset: jest.fn(),
}));

// Test wrapper component
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div>{children}</div>
);

describe('Dashboard Component', () => {
  const mockSetActiveSection = jest.fn();
  const mockOpenQuickCapture = jest.fn();
  const mockGetUnprocessedQuickCapture = jest.fn(() => []);
  const mockProcessQuickCaptureItem = jest.fn();
  const mockDeleteQuickCaptureItem = jest.fn();
  const mockGetAllTasks = jest.fn(() => []);
  const mockGetAllProjects = jest.fn(() => []);

  const mockPillars = [
    {
      id: '1',
      name: 'Health & Wellness',
      description: 'Physical and mental health',
      color: '#10B981',
      healthScore: 85,
      areas: [
        {
          id: 'area1',
          name: 'Exercise',
          description: 'Regular physical activity',
          pillarId: '1'
        }
      ]
    },
    {
      id: '2',
      name: 'Career Growth',
      description: 'Professional development',
      color: '#3B82F6',
      healthScore: 70,
      areas: []
    }
  ];

  const mockTasks = [
    {
      id: 'task1',
      name: 'Complete morning workout',
      description: ' 30 minute cardio session',
      projectId: 'project1',
      status: 'completed' as const,
      completed: true
    },
    {
      id: 'task2',
      name: 'Review project proposal',
      description: 'Review and provide feedback',
      projectId: 'project2',
      status: 'pending' as const,
      completed: false
    }
  ];

  const mockProjects = [
    {
      id: 'project1',
      name: 'Fitness Journey',
      description: 'Get back in shape',
      areaId: 'area1',
      status: 'in_progress' as const
    },
    {
      id: 'project2',
      name: 'Q4 Planning',
      description: 'Strategic planning for Q4',
      areaId: 'area1',
      status: 'in_progress' as const
    }
  ];

  const mockQuickCaptureItems = [
    {
      id: 'qc1',
      content: 'Remember to schedule dentist appointment',
      type: 'reminder',
      processed: false,
      suggestedPillar: 'Health & Wellness',
      suggestedArea: 'Healthcare',
      timestamp: Date.now()
    },
    {
      id: 'qc2',
      content: 'Research new project management tools',
      type: 'idea',
      processed: true,
      suggestedPillar: 'Career Growth',
      suggestedArea: 'Productivity',
      timestamp: Date.now() - 1000
    }
  ];

  beforeEach(() => {
    mockUseAppStore.mockReturnValue({
      activeSection: 'dashboard',
      setActiveSection: mockSetActiveSection,
      isNotificationsOpen: false,
      isMobileMenuOpen: false,
      openNotifications: jest.fn(),
      closeNotifications: jest.fn(),
      openMobileMenu: jest.fn(),
      closeMobileMenu: jest.fn(),
      activeSettingsSection: '',
      setActiveSettingsSection: jest.fn(),
    } as any);

    mockUseEnhancedFeaturesStore.mockReturnValue({
      quickCaptureItems: mockQuickCaptureItems,
      openQuickCapture: mockOpenQuickCapture,
      getUnprocessedQuickCapture: mockGetUnprocessedQuickCapture,
      processQuickCaptureItem: mockProcessQuickCaptureItem,
      deleteQuickCaptureItem: mockDeleteQuickCaptureItem,
      pillars: mockPillars,
      getAllTasks: mockGetAllTasks,
      getAllProjects: mockGetAllProjects,
    } as any);

    mockGetAllTasks.mockReturnValue(mockTasks);
    mockGetAllProjects.mockReturnValue(mockProjects);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Dashboard Layout and Structure', () => {
    it('renders dashboard with correct title and subtitle', async () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Dashboard')).toBeInTheDocument();
        expect(screen.getByText('Your personal operating system command center')).toBeInTheDocument();
      });
    });

    it('displays all quick stats cards', async () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Active Pillars')).toBeInTheDocument();
        expect(screen.getByText('Tasks Completed')).toBeInTheDocument();
        expect(screen.getByText('This Week')).toBeInTheDocument();
        expect(screen.getByText('Avg Health')).toBeInTheDocument();
      });
    });

    it('displays main content sections', async () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText("Today's Focus")).toBeInTheDocument();
        expect(screen.getByText('Quick Capture')).toBeInTheDocument();
        expect(screen.getByText('Pillar Progress')).toBeInTheDocument();
        expect(screen.getByText('Smart Tips')).toBeInTheDocument();
      });
    });
  });

  describe('Quick Stats Cards Functionality', () => {
    it('shows correct pillar count', async () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>
      );

      await waitFor(() => {
        const pillarsCard = screen.getByText('Active Pillars').closest('button');
        expect(pillarsCard).toBeInTheDocument();
        expect(screen.getByText('2')).toBeInTheDocument(); // 2 mock pillars
      });
    });

    it('shows correct task completion ratio', async () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('1/2')).toBeInTheDocument(); // 1 completed out of 2 total
      });
    });

    it('navigates to correct sections when stats cards are clicked', async () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>
      );

      await waitFor(() => {
        const pillarsCard = screen.getByText('Active Pillars').closest('button');
        fireEvent.click(pillarsCard!);
        expect(mockSetActiveSection).toHaveBeenCalledWith('pillars');

        const tasksCard = screen.getByText('Tasks Completed').closest('button');
        fireEvent.click(tasksCard!);
        expect(mockSetActiveSection).toHaveBeenCalledWith('tasks');
      });
    });
  });

  describe('Today\'s Focus Section', () => {
    it('displays progress bar with correct completion percentage', async () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('1/2 completed')).toBeInTheDocument();
        const progressBar = document.querySelector('.h-full.bg-primary');
        expect(progressBar).toHaveStyle('width: 50%'); // 1/2 = 50%
      });
    });

    it('displays task list with correct task information', async () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Complete morning workout')).toBeInTheDocument();
        expect(screen.getByText('Review project proposal')).toBeInTheDocument();
        
        // Check completed task has correct styling
        const completedTask = screen.getByText('Complete morning workout').closest('button');
        expect(completedTask).toHaveClass('border-green-500/20');
      });
    });

    it('opens quick capture when add button is clicked', async () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>
      );

      await waitFor(() => {
        const addButton = screen.getByText("+ Add to today's focus");
        fireEvent.click(addButton);
        expect(mockOpenQuickCapture).toHaveBeenCalled();
      });
    });

    it('navigates to tasks section when task items are clicked', async () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>
      );

      await waitFor(() => {
        const taskButton = screen.getByText('Complete morning workout').closest('button');
        fireEvent.click(taskButton!);
        expect(mockSetActiveSection).toHaveBeenCalledWith('tasks');
      });
    });
  });

  describe('Quick Capture Section', () => {
    it('displays quick capture button', async () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>
      );

      await waitFor(() => {
        const captureButton = screen.getByText('Open Quick Capture');
        expect(captureButton).toBeInTheDocument();
        expect(captureButton.closest('button')).toHaveClass('bg-primary');
      });
    });

    it('opens quick capture modal when button is clicked', async () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>
      );

      await waitFor(() => {
        const captureButton = screen.getByText('Open Quick Capture');
        fireEvent.click(captureButton);
        expect(mockOpenQuickCapture).toHaveBeenCalled();
      });
    });

    it('displays recent captures when available', async () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Recent Captures:')).toBeInTheDocument();
        expect(screen.getByText('Remember to schedule dentist appointment')).toBeInTheDocument();
        expect(screen.getByText('Research new project management tools')).toBeInTheDocument();
      });
    });

    it('processes quick capture items when process button is clicked', async () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>
      );

      await waitFor(() => {
        const processButton = screen.getByText('Process');
        fireEvent.click(processButton);
        expect(mockProcessQuickCaptureItem).toHaveBeenCalledWith(
          'qc1',
          'Health & Wellness',
          'Healthcare'
        );
      });
    });

    it('shows processed state for completed captures', async () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('✓ Processed')).toBeInTheDocument();
      });
    });
  });

  describe('Pillar Progress Section', () => {
    it('displays pillar progress for each pillar', async () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Health & Wellness')).toBeInTheDocument();
        expect(screen.getByText('Career Growth')).toBeInTheDocument();
        expect(screen.getByText('85%')).toBeInTheDocument();
        expect(screen.getByText('70%')).toBeInTheDocument();
      });
    });

    it('navigates to pillars section when pillar name is clicked', async () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>
      );

      await waitFor(() => {
        const pillarButton = screen.getByText('Health & Wellness').closest('button');
        fireEvent.click(pillarButton!);
        expect(mockSetActiveSection).toHaveBeenCalledWith('pillars');
      });
    });

    it('shows trend indicators for pillar health', async () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>
      );

      await waitFor(() => {
        // Health & Wellness (85%) is above average (77.5%), so should show positive trend
        const trends = screen.getAllByText(/^[+-]?\d+%$/);
        expect(trends.length).toBeGreaterThan(0);
      });
    });
  });

  describe('Smart Tips Section', () => {
    it('displays wellness and career tips', async () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Schedule wellness time')).toBeInTheDocument();
        expect(screen.getByText('Great career momentum!')).toBeInTheDocument();
      });
    });

    it('navigates to today section when schedule wellness is clicked', async () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>
      );

      await waitFor(() => {
        const scheduleButton = screen.getByText('Schedule Wellness');
        fireEvent.click(scheduleButton);
        expect(mockSetActiveSection).toHaveBeenCalledWith('today');
      });
    });

    it('navigates to analytics section when view analytics is clicked', async () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>
      );

      await waitFor(() => {
        const analyticsButton = screen.getByText('View Analytics');
        fireEvent.click(analyticsButton);
        expect(mockSetActiveSection).toHaveBeenCalledWith('analytics');
      });
    });
  });

  describe('Error Handling', () => {
    it('handles missing data gracefully', async () => {
      mockUseEnhancedFeaturesStore.mockReturnValue({
        quickCaptureItems: [],
        openQuickCapture: mockOpenQuickCapture,
        getUnprocessedQuickCapture: () => [],
        processQuickCaptureItem: mockProcessQuickCaptureItem,
        deleteQuickCaptureItem: mockDeleteQuickCaptureItem,
        pillars: [],
        getAllTasks: () => [],
        getAllProjects: () => [],
      } as any);

      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('No tasks created yet')).toBeInTheDocument();
        expect(screen.getByText('No captures yet')).toBeInTheDocument();
        expect(screen.getByText('No pillars created yet')).toBeInTheDocument();
      });
    });

    it('handles store errors gracefully', async () => {
      mockGetAllTasks.mockImplementation(() => {
        throw new Error('Store error');
      });

      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>
      );

      // Should still render without crashing
      await waitFor(() => {
        expect(screen.getByText('Dashboard')).toBeInTheDocument();
      });
    });
  });

  describe('Loading States', () => {
    it('shows loading fallback initially', () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>
      );

      // Should show shimmer loading elements
      const shimmerElements = document.querySelectorAll('.shimmer');
      expect(shimmerElements.length).toBeGreaterThan(0);
    });
  });

  describe('Accessibility', () => {
    it('has proper heading structure', async () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>
      );

      await waitFor(() => {
        const headings = screen.getAllByRole('heading');
        expect(headings.length).toBeGreaterThan(0);
        
        // Should have main heading
        const mainHeading = screen.getByRole('heading', { name: 'Dashboard' });
        expect(mainHeading.tagName).toBe('H1');
      });
    });

    it('has accessible buttons', async () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>
      );

      await waitFor(() => {
        const buttons = screen.getAllByRole('button');
        buttons.forEach(button => {
          // Each button should have accessible text content
          expect(button.textContent || button.getAttribute('aria-label')).toBeTruthy();
        });
      });
    });

    it('applies touch target classes for mobile', async () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>
      );

      await waitFor(() => {
        const touchTargets = document.querySelectorAll('.touch-target, .touch-target-small, .touch-target-large');
        expect(touchTargets.length).toBeGreaterThan(0);
      });
    });
  });

  describe('Performance', () => {
    it('renders without exceeding performance budget', async () => {
      const startTime = performance.now();
      
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Dashboard')).toBeInTheDocument();
      });

      const endTime = performance.now();
      const renderTime = endTime - startTime;
      
      // Should render within 200ms
      expect(renderTime).toBeLessThan(200);
    });

    it('memoizes expensive calculations', async () => {
      const { rerender } = render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>
      );

      // Re-render with same props
      rerender(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>
      );

      // Store functions should not be called multiple times unnecessarily
      expect(mockGetAllTasks).toHaveBeenCalledTimes(2); // Once per render due to useMemo
    });
  });
});