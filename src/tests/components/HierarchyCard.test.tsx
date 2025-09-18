/**
 * HierarchyCard Component Tests
 * Testing the core hierarchy display component
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import HierarchyCard from '../../components/shared/HierarchyCard';

const mockPillar = {
  id: '1',
  title: 'Health & Wellness',
  description: 'Physical and mental well-being',
  color: '#10B981',
  icon: 'heart',
  progress: 75,
  created_at: '2023-01-01T00:00:00Z',
  areas: [
    {
      id: 'a1',
      title: 'Fitness',
      description: 'Regular exercise',
      progress: 80,
    },
    {
      id: 'a2',
      title: 'Nutrition',
      description: 'Healthy eating',
      progress: 70,
    },
  ],
};

const mockArea = {
  id: 'a1',
  title: 'Fitness',
  description: 'Regular exercise and activity',
  color: '#3B82F6',
  progress: 80,
  projects: [
    {
      id: 'p1',
      title: 'Morning Routine',
      description: 'Daily morning workout',
      status: 'in_progress',
      progress: 60,
    },
  ],
};

const mockProject = {
  id: 'p1',
  title: 'Morning Workout Routine',
  description: 'Establish consistent morning exercise',
  status: 'in_progress',
  priority: 'high',
  progress: 60,
  tasks: [
    {
      id: 't1',
      title: '30-minute run',
      description: 'Morning cardio session',
      status: 'pending',
      priority: 'medium',
    },
  ],
};

const mockTask = {
  id: 't1',
  title: 'Go for a 30-minute run',
  description: 'Complete outdoor running session',
  status: 'pending',
  priority: 'medium',
  due_date: '2023-12-01T10:00:00Z',
  estimated_duration: 30,
};

describe('HierarchyCard Component', () => {
  const mockOnClick = jest.fn();
  const mockOnEdit = jest.fn();
  const mockOnDelete = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Pillar Display', () => {
    it('renders pillar card correctly', () => {
      render(
        <HierarchyCard
          type="pillar"
          data={mockPillar}
          onClick={mockOnClick}
          onEdit={mockOnEdit}
          onDelete={mockOnDelete}
        />
      );

      expect(screen.getByText('Health & Wellness')).toBeInTheDocument();
      expect(screen.getByText('Physical and mental well-being')).toBeInTheDocument();
      expect(screen.getByText('75%')).toBeInTheDocument();
    });

    it('displays pillar hierarchy styling', () => {
      render(
        <HierarchyCard
          type="pillar"
          data={mockPillar}
          onClick={mockOnClick}
        />
      );

      const card = screen.getByRole('article');
      expect(card).toHaveClass('hierarchy-pillar');
    });

    it('shows pillar sub-items (areas)', () => {
      render(
        <HierarchyCard
          type="pillar"
          data={mockPillar}
          onClick={mockOnClick}
          showSubItems={true}
        />
      );

      expect(screen.getByText('Fitness')).toBeInTheDocument();
      expect(screen.getByText('Nutrition')).toBeInTheDocument();
    });

    it('handles pillar click events', () => {
      render(
        <HierarchyCard
          type="pillar"
          data={mockPillar}
          onClick={mockOnClick}
        />
      );

      const card = screen.getByRole('article');
      fireEvent.click(card);

      expect(mockOnClick).toHaveBeenCalledWith(mockPillar);
    });
  });

  describe('Area Display', () => {
    it('renders area card correctly', () => {
      render(
        <HierarchyCard
          type="area"
          data={mockArea}
          onClick={mockOnClick}
        />
      );

      expect(screen.getByText('Fitness')).toBeInTheDocument();
      expect(screen.getByText('Regular exercise and activity')).toBeInTheDocument();
      expect(screen.getByText('80%')).toBeInTheDocument();
    });

    it('displays area hierarchy styling', () => {
      render(
        <HierarchyCard
          type="area"
          data={mockArea}
          onClick={mockOnClick}
        />
      );

      const card = screen.getByRole('article');
      expect(card).toHaveClass('hierarchy-area');
    });
  });

  describe('Project Display', () => {
    it('renders project card correctly', () => {
      render(
        <HierarchyCard
          type="project"
          data={mockProject}
          onClick={mockOnClick}
        />
      );

      expect(screen.getByText('Morning Workout Routine')).toBeInTheDocument();
      expect(screen.getByText('Establish consistent morning exercise')).toBeInTheDocument();
      expect(screen.getByText('60%')).toBeInTheDocument();
    });

    it('displays project status', () => {
      render(
        <HierarchyCard
          type="project"
          data={mockProject}
          onClick={mockOnClick}
        />
      );

      expect(screen.getByText('In Progress')).toBeInTheDocument();
    });

    it('displays project priority', () => {
      render(
        <HierarchyCard
          type="project"
          data={mockProject}
          onClick={mockOnClick}
        />
      );

      expect(screen.getByText('High')).toBeInTheDocument();
    });
  });

  describe('Task Display', () => {
    it('renders task card correctly', () => {
      render(
        <HierarchyCard
          type="task"
          data={mockTask}
          onClick={mockOnClick}
        />
      );

      expect(screen.getByText('Go for a 30-minute run')).toBeInTheDocument();
      expect(screen.getByText('Complete outdoor running session')).toBeInTheDocument();
    });

    it('displays task status', () => {
      render(
        <HierarchyCard
          type="task"
          data={mockTask}
          onClick={mockOnClick}
        />
      );

      expect(screen.getByText('Pending')).toBeInTheDocument();
    });

    it('displays task duration', () => {
      render(
        <HierarchyCard
          type="task"
          data={mockTask}
          onClick={mockOnClick}
        />
      );

      expect(screen.getByText('30 min')).toBeInTheDocument();
    });

    it('displays due date', () => {
      render(
        <HierarchyCard
          type="task"
          data={mockTask}
          onClick={mockOnClick}
        />
      );

      expect(screen.getByText(/Dec 1/)).toBeInTheDocument();
    });
  });

  describe('Interactive Features', () => {
    it('handles edit button click', () => {
      render(
        <HierarchyCard
          type="pillar"
          data={mockPillar}
          onClick={mockOnClick}
          onEdit={mockOnEdit}
        />
      );

      const editButton = screen.getByRole('button', { name: /edit/i });
      fireEvent.click(editButton);

      expect(mockOnEdit).toHaveBeenCalledWith(mockPillar);
      expect(mockOnClick).not.toHaveBeenCalled();
    });

    it('handles delete button click', () => {
      render(
        <HierarchyCard
          type="pillar"
          data={mockPillar}
          onClick={mockOnClick}
          onDelete={mockOnDelete}
        />
      );

      const deleteButton = screen.getByRole('button', { name: /delete/i });
      fireEvent.click(deleteButton);

      expect(mockOnDelete).toHaveBeenCalledWith(mockPillar);
      expect(mockOnClick).not.toHaveBeenCalled();
    });

    it('expands/collapses sub-items', () => {
      render(
        <HierarchyCard
          type="pillar"
          data={mockPillar}
          onClick={mockOnClick}
          showSubItems={true}
        />
      );

      const expandButton = screen.getByRole('button', { name: /collapse/i });
      fireEvent.click(expandButton);

      // Sub-items should be hidden
      expect(screen.queryByText('Fitness')).not.toBeInTheDocument();
    });

    it('handles keyboard navigation', () => {
      render(
        <HierarchyCard
          type="pillar"
          data={mockPillar}
          onClick={mockOnClick}
        />
      );

      const card = screen.getByRole('article');
      fireEvent.keyDown(card, { key: 'Enter' });

      expect(mockOnClick).toHaveBeenCalledWith(mockPillar);
    });

    it('handles space key activation', () => {
      render(
        <HierarchyCard
          type="pillar"
          data={mockPillar}
          onClick={mockOnClick}
        />
      );

      const card = screen.getByRole('article');
      fireEvent.keyDown(card, { key: ' ' });

      expect(mockOnClick).toHaveBeenCalledWith(mockPillar);
    });
  });

  describe('Progress Display', () => {
    it('renders progress bar correctly', () => {
      render(
        <HierarchyCard
          type="pillar"
          data={mockPillar}
          onClick={mockOnClick}
        />
      );

      const progressBar = screen.getByRole('progressbar');
      expect(progressBar).toHaveAttribute('aria-valuenow', '75');
      expect(progressBar).toHaveAttribute('aria-valuemin', '0');
      expect(progressBar).toHaveAttribute('aria-valuemax', '100');
    });

    it('handles zero progress', () => {
      const zeroProgressData = { ...mockPillar, progress: 0 };
      
      render(
        <HierarchyCard
          type="pillar"
          data={zeroProgressData}
          onClick={mockOnClick}
        />
      );

      expect(screen.getByText('0%')).toBeInTheDocument();
    });

    it('handles 100% progress', () => {
      const completeData = { ...mockPillar, progress: 100 };
      
      render(
        <HierarchyCard
          type="pillar"
          data={completeData}
          onClick={mockOnClick}
        />
      );

      expect(screen.getByText('100%')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA labels', () => {
      render(
        <HierarchyCard
          type="pillar"
          data={mockPillar}
          onClick={mockOnClick}
        />
      );

      const card = screen.getByRole('article');
      expect(card).toHaveAttribute('aria-label');
      expect(card).toHaveAttribute('tabIndex', '0');
    });

    it('provides screen reader friendly content', () => {
      render(
        <HierarchyCard
          type="pillar"
          data={mockPillar}
          onClick={mockOnClick}
        />
      );

      // Should have accessible progress description
      expect(screen.getByText('75% complete')).toBeInTheDocument();
    });

    it('supports high contrast mode', () => {
      document.body.classList.add('high-contrast');
      
      render(
        <HierarchyCard
          type="pillar"
          data={mockPillar}
          onClick={mockOnClick}
        />
      );

      const card = screen.getByRole('article');
      expect(card).toBeInTheDocument();
      
      document.body.classList.remove('high-contrast');
    });
  });

  describe('Responsive Design', () => {
    it('adapts to mobile viewport', () => {
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      });

      render(
        <HierarchyCard
          type="pillar"
          data={mockPillar}
          onClick={mockOnClick}
        />
      );

      expect(screen.getByText('Health & Wellness')).toBeInTheDocument();
    });

    it('handles compact mode', () => {
      document.body.classList.add('compact-mode');
      
      render(
        <HierarchyCard
          type="pillar"
          data={mockPillar}
          onClick={mockOnClick}
        />
      );

      expect(screen.getByText('Health & Wellness')).toBeInTheDocument();
      
      document.body.classList.remove('compact-mode');
    });
  });

  describe('Error Handling', () => {
    it('handles missing data gracefully', () => {
      const incompleteData = { id: '1', title: 'Test' };
      
      render(
        <HierarchyCard
          type="pillar"
          data={incompleteData}
          onClick={mockOnClick}
        />
      );

      expect(screen.getByText('Test')).toBeInTheDocument();
    });

    it('handles invalid progress values', () => {
      const invalidProgressData = { ...mockPillar, progress: -10 };
      
      render(
        <HierarchyCard
          type="pillar"
          data={invalidProgressData}
          onClick={mockOnClick}
        />
      );

      // Should clamp to valid range
      expect(screen.getByText('0%')).toBeInTheDocument();
    });

    it('handles overflow progress values', () => {
      const overflowProgressData = { ...mockPillar, progress: 150 };
      
      render(
        <HierarchyCard
          type="pillar"
          data={overflowProgressData}
          onClick={mockOnClick}
        />
      );

      // Should clamp to valid range
      expect(screen.getByText('100%')).toBeInTheDocument();
    });
  });
});