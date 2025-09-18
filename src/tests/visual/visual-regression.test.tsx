/**
 * Visual Regression Tests
 * Automated visual consistency testing for UI components
 */

import React from 'react';
import { render } from '@testing-library/react';
import { toMatchImageSnapshot } from 'jest-image-snapshot';

// Import components for visual testing
import Dashboard from '../../components/sections/Dashboard';
import Navigation from '../../components/layout/Navigation';
import HierarchyCard from '../../components/shared/HierarchyCard';
import IntelligentLifeCoachAI from '../../components/enhanced/IntelligentLifeCoachAI';
import TeamCollaborationHub from '../../components/enhanced/TeamCollaborationHub';

// Extend Jest with image snapshot matcher
expect.extend({ toMatchImageSnapshot });

// Mock dependencies for visual tests
jest.mock('../../stores/authStore', () => ({
  useAuthStore: jest.fn(() => ({
    user: { id: '1', email: 'test@aurumlife.com', name: 'Test User' },
    isAuthenticated: true,
    isLoading: false,
  })),
}));

// Mock canvas for chart rendering
HTMLCanvasElement.prototype.getContext = jest.fn(() => ({
  fillRect: jest.fn(),
  clearRect: jest.fn(),
  getImageData: jest.fn(() => ({ data: new Array(4) })),
  putImageData: jest.fn(),
  createImageData: jest.fn(() => ({ data: new Array(4) })),
  setTransform: jest.fn(),
  drawImage: jest.fn(),
  save: jest.fn(),
  fillText: jest.fn(),
  restore: jest.fn(),
  beginPath: jest.fn(),
  moveTo: jest.fn(),
  lineTo: jest.fn(),
  closePath: jest.fn(),
  stroke: jest.fn(),
  translate: jest.fn(),
  scale: jest.fn(),
  rotate: jest.fn(),
  arc: jest.fn(),
  fill: jest.fn(),
})) as any;

describe('Visual Regression Tests', () => {
  beforeEach(() => {
    // Set consistent viewport for screenshots
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      value: 1280,
    });
    Object.defineProperty(window, 'innerHeight', {
      writable: true,
      value: 720,
    });
    
    // Mock dates for consistent screenshots
    jest.useFakeTimers();
    jest.setSystemTime(new Date('2024-01-15T10:00:00Z'));
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  describe('Core Components Visual Tests', () => {
    it('Dashboard renders consistently', async () => {
      const { container } = render(<Dashboard />);
      
      // Wait for any async rendering
      await new Promise(resolve => setTimeout(resolve, 100));
      
      expect(container.firstChild).toMatchImageSnapshot({
        customSnapshotIdentifier: 'dashboard-default',
        failureThreshold: 0.02,
        failureThresholdType: 'percent',
      });
    });

    it('Navigation renders consistently across different active sections', async () => {
      const sections = ['dashboard', 'today', 'pillars', 'projects', 'tasks'];
      
      for (const section of sections) {
        const { container } = render(
          <Navigation activeSection={section} onSectionChange={jest.fn()} />
        );
        
        await new Promise(resolve => setTimeout(resolve, 50));
        
        expect(container.firstChild).toMatchImageSnapshot({
          customSnapshotIdentifier: `navigation-${section}`,
          failureThreshold: 0.02,
          failureThresholdType: 'percent',
        });
      }
    });

    it('HierarchyCard renders consistently for different hierarchy types', async () => {
      const mockPillar = {
        id: '1',
        title: 'Health & Wellness',
        description: 'Physical and mental well-being focus',
        color: '#10B981',
        progress: 75,
      };

      const mockArea = {
        id: '2',
        title: 'Fitness Training',
        description: 'Regular exercise and strength building',
        color: '#3B82F6',
        progress: 80,
      };

      const mockProject = {
        id: '3',
        title: 'Morning Routine',
        description: 'Daily morning workout and meditation',
        status: 'in_progress',
        priority: 'high',
        progress: 60,
      };

      const hierarchyItems = [
        { type: 'pillar', data: mockPillar },
        { type: 'area', data: mockArea },
        { type: 'project', data: mockProject },
      ];

      for (const item of hierarchyItems) {
        const { container } = render(
          <HierarchyCard
            type={item.type as any}
            data={item.data}
            onClick={jest.fn()}
          />
        );
        
        await new Promise(resolve => setTimeout(resolve, 50));
        
        expect(container.firstChild).toMatchImageSnapshot({
          customSnapshotIdentifier: `hierarchy-card-${item.type}`,
          failureThreshold: 0.02,
          failureThresholdType: 'percent',
        });
      }
    });
  });

  describe('Phase 4 Features Visual Tests', () => {
    it('AI Coach interface renders consistently', async () => {
      const mockUser = { id: '1', email: 'test@aurumlife.com', name: 'Test User' };
      const { container } = render(<IntelligentLifeCoachAI user={mockUser} />);
      
      await new Promise(resolve => setTimeout(resolve, 200));
      
      expect(container.firstChild).toMatchImageSnapshot({
        customSnapshotIdentifier: 'ai-coach-default',
        failureThreshold: 0.03,
        failureThresholdType: 'percent',
      });
    });

    it('Team Collaboration Hub renders consistently', async () => {
      const mockUser = { id: '1', name: 'Test User', role: 'admin' };
      const mockTeam = {
        id: 'team-1',
        name: 'Development Team',
        members: [
          { id: '1', name: 'Test User', role: 'admin', status: 'online' },
          { id: '2', name: 'Jane Doe', role: 'member', status: 'away' },
        ],
      };

      const { container } = render(
        <TeamCollaborationHub user={mockUser} team={mockTeam} />
      );
      
      await new Promise(resolve => setTimeout(resolve, 200));
      
      expect(container.firstChild).toMatchImageSnapshot({
        customSnapshotIdentifier: 'team-collaboration-default',
        failureThreshold: 0.03,
        failureThresholdType: 'percent',
      });
    });
  });

  describe('Responsive Visual Tests', () => {
    it('Dashboard renders correctly on mobile viewport', async () => {
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        value: 375,
      });
      Object.defineProperty(window, 'innerHeight', {
        writable: true,
        value: 667,
      });

      const { container } = render(<Dashboard />);
      
      await new Promise(resolve => setTimeout(resolve, 100));
      
      expect(container.firstChild).toMatchImageSnapshot({
        customSnapshotIdentifier: 'dashboard-mobile',
        failureThreshold: 0.03,
        failureThresholdType: 'percent',
      });
    });

    it('Navigation renders correctly on tablet viewport', async () => {
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        value: 768,
      });
      Object.defineProperty(window, 'innerHeight', {
        writable: true,
        value: 1024,
      });

      const { container } = render(
        <Navigation activeSection="dashboard" onSectionChange={jest.fn()} />
      );
      
      await new Promise(resolve => setTimeout(resolve, 100));
      
      expect(container.firstChild).toMatchImageSnapshot({
        customSnapshotIdentifier: 'navigation-tablet',
        failureThreshold: 0.03,
        failureThresholdType: 'percent',
      });
    });
  });

  describe('Theme and Appearance Visual Tests', () => {
    it('Components render consistently with high contrast mode', async () => {
      document.body.classList.add('high-contrast');
      
      const { container } = render(<Dashboard />);
      
      await new Promise(resolve => setTimeout(resolve, 100));
      
      expect(container.firstChild).toMatchImageSnapshot({
        customSnapshotIdentifier: 'dashboard-high-contrast',
        failureThreshold: 0.05,
        failureThresholdType: 'percent',
      });
      
      document.body.classList.remove('high-contrast');
    });

    it('Components render consistently with compact mode', async () => {
      document.body.classList.add('compact-mode');
      
      const { container } = render(<Dashboard />);
      
      await new Promise(resolve => setTimeout(resolve, 100));
      
      expect(container.firstChild).toMatchImageSnapshot({
        customSnapshotIdentifier: 'dashboard-compact',
        failureThreshold: 0.05,
        failureThresholdType: 'percent',
      });
      
      document.body.classList.remove('compact-mode');
    });

    it('Components render consistently with different font sizes', async () => {
      const fontSizes = ['14px', '16px', '18px'];
      
      for (const fontSize of fontSizes) {
        document.documentElement.style.fontSize = fontSize;
        
        const { container } = render(<Dashboard />);
        
        await new Promise(resolve => setTimeout(resolve, 100));
        
        expect(container.firstChild).toMatchImageSnapshot({
          customSnapshotIdentifier: `dashboard-font-${fontSize}`,
          failureThreshold: 0.05,
          failureThresholdType: 'percent',
        });
      }
      
      document.documentElement.style.fontSize = '';
    });
  });

  describe('State-based Visual Tests', () => {
    it('Components render loading states consistently', async () => {
      // Mock loading state
      const LoadingDashboard = () => {
        const [isLoading, setIsLoading] = React.useState(true);
        
        React.useEffect(() => {
          const timer = setTimeout(() => setIsLoading(false), 50);
          return () => clearTimeout(timer);
        }, []);

        if (isLoading) {
          return (
            <div className="space-y-6 p-6">
              <div className="animate-pulse space-y-4">
                <div className="h-8 bg-muted rounded w-3/4"></div>
                <div className="h-4 bg-muted rounded w-1/2"></div>
                <div className="grid grid-cols-3 gap-4">
                  <div className="h-20 bg-muted rounded"></div>
                  <div className="h-20 bg-muted rounded"></div>
                  <div className="h-20 bg-muted rounded"></div>
                </div>
              </div>
            </div>
          );
        }
        
        return <Dashboard />;
      };

      const { container } = render(<LoadingDashboard />);
      
      // Capture loading state
      expect(container.firstChild).toMatchImageSnapshot({
        customSnapshotIdentifier: 'dashboard-loading',
        failureThreshold: 0.02,
        failureThresholdType: 'percent',
      });
    });

    it('Components render error states consistently', async () => {
      const ErrorDashboard = () => (
        <div className="flex items-center justify-center min-h-screen p-6">
          <div className="text-center space-y-4">
            <div className="text-6xl">⚠️</div>
            <h2 className="text-2xl font-semibold text-destructive">
              Something went wrong
            </h2>
            <p className="text-muted-foreground">
              We encountered an error loading your dashboard.
            </p>
            <button className="px-4 py-2 bg-primary text-primary-foreground rounded-md">
              Try Again
            </button>
          </div>
        </div>
      );

      const { container } = render(<ErrorDashboard />);
      
      expect(container.firstChild).toMatchImageSnapshot({
        customSnapshotIdentifier: 'dashboard-error',
        failureThreshold: 0.02,
        failureThresholdType: 'percent',
      });
    });

    it('Components render empty states consistently', async () => {
      const EmptyDashboard = () => (
        <div className="flex items-center justify-center min-h-screen p-6">
          <div className="text-center space-y-4">
            <div className="text-6xl opacity-50">📊</div>
            <h2 className="text-2xl font-semibold">
              Welcome to Aurum Life
            </h2>
            <p className="text-muted-foreground max-w-md">
              Start by creating your first pillar to begin organizing your life goals.
            </p>
            <button className="px-4 py-2 bg-primary text-primary-foreground rounded-md">
              Create First Pillar
            </button>
          </div>
        </div>
      );

      const { container } = render(<EmptyDashboard />);
      
      expect(container.firstChild).toMatchImageSnapshot({
        customSnapshotIdentifier: 'dashboard-empty',
        failureThreshold: 0.02,
        failureThresholdType: 'percent',
      });
    });
  });

  describe('Interactive State Visual Tests', () => {
    it('Buttons render hover and focus states consistently', async () => {
      const ButtonStates = () => (
        <div className="space-y-4 p-6">
          <button className="px-4 py-2 bg-primary text-primary-foreground rounded-md">
            Default Button
          </button>
          <button className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90">
            Hovered Button
          </button>
          <button className="px-4 py-2 bg-primary text-primary-foreground rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2">
            Focused Button
          </button>
          <button 
            className="px-4 py-2 bg-secondary text-secondary-foreground rounded-md opacity-50 cursor-not-allowed"
            disabled
          >
            Disabled Button
          </button>
        </div>
      );

      const { container } = render(<ButtonStates />);
      
      expect(container.firstChild).toMatchImageSnapshot({
        customSnapshotIdentifier: 'button-states',
        failureThreshold: 0.02,
        failureThresholdType: 'percent',
      });
    });

    it('Form inputs render different states consistently', async () => {
      const InputStates = () => (
        <div className="space-y-4 p-6 max-w-md">
          <input
            type="text"
            placeholder="Default input"
            className="w-full px-3 py-2 border border-border rounded-md"
          />
          <input
            type="text"
            value="Filled input"
            readOnly
            className="w-full px-3 py-2 border border-border rounded-md"
          />
          <input
            type="text"
            placeholder="Focused input"
            className="w-full px-3 py-2 border border-primary rounded-md ring-2 ring-primary ring-opacity-50"
          />
          <input
            type="text"
            placeholder="Error input"
            className="w-full px-3 py-2 border border-destructive rounded-md"
          />
          <input
            type="text"
            placeholder="Disabled input"
            disabled
            className="w-full px-3 py-2 border border-border rounded-md opacity-50"
          />
        </div>
      );

      const { container } = render(<InputStates />);
      
      expect(container.firstChild).toMatchImageSnapshot({
        customSnapshotIdentifier: 'input-states',
        failureThreshold: 0.02,
        failureThresholdType: 'percent',
      });
    });
  });

  describe('Component Variation Visual Tests', () => {
    it('Cards render different variants consistently', async () => {
      const CardVariants = () => (
        <div className="grid grid-cols-2 gap-4 p-6 max-w-4xl">
          <div className="glassmorphism-card p-4">
            <h3 className="font-semibold mb-2">Glassmorphism Card</h3>
            <p className="text-sm text-muted-foreground">
              Standard glassmorphism styling with blur effect
            </p>
          </div>
          
          <div className="glassmorphism-card hierarchy-pillar p-4">
            <h3 className="font-semibold mb-2">Pillar Card</h3>
            <p className="text-sm text-muted-foreground">
              Pillar hierarchy styling with gold accent
            </p>
          </div>
          
          <div className="glassmorphism-card hierarchy-area p-4">
            <h3 className="font-semibold mb-2">Area Card</h3>
            <p className="text-sm text-muted-foreground">
              Area hierarchy styling with blue accent
            </p>
          </div>
          
          <div className="glassmorphism-card hierarchy-project p-4">
            <h3 className="font-semibold mb-2">Project Card</h3>
            <p className="text-sm text-muted-foreground">
              Project hierarchy styling with green accent
            </p>
          </div>
        </div>
      );

      const { container } = render(<CardVariants />);
      
      expect(container.firstChild).toMatchImageSnapshot({
        customSnapshotIdentifier: 'card-variants',
        failureThreshold: 0.02,
        failureThresholdType: 'percent',
      });
    });

    it('Progress indicators render consistently', async () => {
      const ProgressVariants = () => (
        <div className="space-y-6 p-6 max-w-md">
          <div>
            <div className="flex justify-between text-sm mb-2">
              <span>Low Progress</span>
              <span>25%</span>
            </div>
            <div className="w-full bg-muted rounded-full h-2">
              <div className="bg-primary h-2 rounded-full" style={{width: '25%'}}></div>
            </div>
          </div>
          
          <div>
            <div className="flex justify-between text-sm mb-2">
              <span>Medium Progress</span>
              <span>60%</span>
            </div>
            <div className="w-full bg-muted rounded-full h-2">
              <div className="bg-primary h-2 rounded-full" style={{width: '60%'}}></div>
            </div>
          </div>
          
          <div>
            <div className="flex justify-between text-sm mb-2">
              <span>High Progress</span>
              <span>85%</span>
            </div>
            <div className="w-full bg-muted rounded-full h-2">
              <div className="bg-primary h-2 rounded-full" style={{width: '85%'}}></div>
            </div>
          </div>
          
          <div>
            <div className="flex justify-between text-sm mb-2">
              <span>Complete</span>
              <span>100%</span>
            </div>
            <div className="w-full bg-muted rounded-full h-2">
              <div className="bg-success h-2 rounded-full" style={{width: '100%'}}></div>
            </div>
          </div>
        </div>
      );

      const { container } = render(<ProgressVariants />);
      
      expect(container.firstChild).toMatchImageSnapshot({
        customSnapshotIdentifier: 'progress-variants',
        failureThreshold: 0.02,
        failureThresholdType: 'percent',
      });
    });
  });

  describe('Cross-browser Visual Consistency', () => {
    it('Glassmorphism effects render consistently', async () => {
      const GlassmorphismShowcase = () => (
        <div className="min-h-screen bg-background p-6 space-y-6">
          <div className="glassmorphism-card p-6">
            <h2 className="text-xl font-semibold mb-4">Standard Glassmorphism</h2>
            <p className="text-muted-foreground">
              Semi-transparent background with blur effect and subtle borders.
            </p>
          </div>
          
          <div className="glassmorphism-panel p-4">
            <h3 className="font-medium mb-2">Panel Variant</h3>
            <p className="text-sm text-muted-foreground">
              Lighter glassmorphism for nested content areas.
            </p>
          </div>
          
          <div className="glassmorphism-header p-4">
            <h3 className="font-medium">Header Variant</h3>
          </div>
        </div>
      );

      const { container } = render(<GlassmorphismShowcase />);
      
      await new Promise(resolve => setTimeout(resolve, 100));
      
      expect(container.firstChild).toMatchImageSnapshot({
        customSnapshotIdentifier: 'glassmorphism-effects',
        failureThreshold: 0.05, // Higher threshold for complex visual effects
        failureThresholdType: 'percent',
      });
    });
  });
});