/**
 * Intelligent Life Coach AI Component Tests
 * Comprehensive testing for Phase 4 AI coaching features
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import IntelligentLifeCoachAI from '../../../components/enhanced/IntelligentLifeCoachAI';

// Mock AI service
jest.mock('../../../services/ragCategorization', () => ({
  generateInsight: jest.fn(),
  categorizeLifeData: jest.fn(),
  generateActionableRecommendations: jest.fn(),
}));

describe('IntelligentLifeCoachAI Component', () => {
  const mockUser = {
    id: '1',
    email: 'test@aurumlife.com',
    name: 'Test User',
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('AI Insights Generation', () => {
    it('renders AI insights dashboard correctly', async () => {
      render(<IntelligentLifeCoachAI user={mockUser} />);

      expect(screen.getByText(/intelligent life coach/i)).toBeInTheDocument();
      expect(screen.getByText(/personalized insights/i)).toBeInTheDocument();
    });

    it('generates contextual life insights based on user data', async () => {
      const { generateInsight } = require('../../../services/ragCategorization');
      generateInsight.mockResolvedValue({
        insight: 'Based on your recent patterns, consider focusing on morning routines for better productivity.',
        confidence: 0.92,
        category: 'productivity',
        actionItems: ['Set consistent wake time', 'Create morning ritual'],
      });

      render(<IntelligentLifeCoachAI user={mockUser} />);

      const generateButton = screen.getByRole('button', { name: /generate insights/i });
      await userEvent.click(generateButton);

      await waitFor(() => {
        expect(screen.getByText(/morning routines/i)).toBeInTheDocument();
        expect(screen.getByText(/92%/i)).toBeInTheDocument();
      });
    });

    it('handles AI service errors gracefully', async () => {
      const { generateInsight } = require('../../../services/ragCategorization');
      generateInsight.mockRejectedValue(new Error('AI service unavailable'));

      render(<IntelligentLifeCoachAI user={mockUser} />);

      const generateButton = screen.getByRole('button', { name: /generate insights/i });
      await userEvent.click(generateButton);

      await waitFor(() => {
        expect(screen.getByText(/unable to generate insights/i)).toBeInTheDocument();
      });
    });

    it('provides personalized coaching recommendations', async () => {
      const { generateActionableRecommendations } = require('../../../services/ragCategorization');
      generateActionableRecommendations.mockResolvedValue({
        recommendations: [
          {
            title: 'Optimize Your Morning Routine',
            description: 'Start your day with intention',
            priority: 'high',
            estimatedImpact: 8.5,
            timeframe: '2 weeks',
            steps: ['Wake at consistent time', 'Add meditation', 'Review daily goals'],
          },
        ],
      });

      render(<IntelligentLifeCoachAI user={mockUser} />);

      const recommendButton = screen.getByRole('button', { name: /get recommendations/i });
      await userEvent.click(recommendButton);

      await waitFor(() => {
        expect(screen.getByText(/optimize your morning routine/i)).toBeInTheDocument();
        expect(screen.getByText(/impact: 8.5/i)).toBeInTheDocument();
      });
    });
  });

  describe('Conversational AI Interface', () => {
    it('supports natural language queries', async () => {
      render(<IntelligentLifeCoachAI user={mockUser} />);

      const chatInput = screen.getByPlaceholderText(/ask your life coach/i);
      await userEvent.type(chatInput, 'How can I improve my work-life balance?');

      const sendButton = screen.getByRole('button', { name: /send/i });
      await userEvent.click(sendButton);

      await waitFor(() => {
        expect(screen.getByText(/analyzing your question/i)).toBeInTheDocument();
      });
    });

    it('maintains conversation context', async () => {
      render(<IntelligentLifeCoachAI user={mockUser} />);

      // First message
      const chatInput = screen.getByPlaceholderText(/ask your life coach/i);
      await userEvent.type(chatInput, 'I want to be more productive');
      fireEvent.click(screen.getByRole('button', { name: /send/i }));

      await waitFor(() => {
        expect(screen.getByText(/productivity goals/i)).toBeInTheDocument();
      });

      // Follow-up message should reference context
      await userEvent.clear(chatInput);
      await userEvent.type(chatInput, 'How do I start?');
      fireEvent.click(screen.getByRole('button', { name: /send/i }));

      await waitFor(() => {
        expect(screen.getByText(/based on your productivity goal/i)).toBeInTheDocument();
      });
    });

    it('provides relevant follow-up questions', async () => {
      render(<IntelligentLifeCoachAI user={mockUser} />);

      const chatInput = screen.getByPlaceholderText(/ask your life coach/i);
      await userEvent.type(chatInput, 'I feel stressed lately');
      fireEvent.click(screen.getByRole('button', { name: /send/i }));

      await waitFor(() => {
        expect(screen.getByText(/what's causing stress/i)).toBeInTheDocument();
        expect(screen.getByText(/tried any relaxation/i)).toBeInTheDocument();
      });
    });
  });

  describe('Goal Achievement Coaching', () => {
    it('tracks progress toward life goals', async () => {
      const mockGoals = [
        { id: '1', title: 'Exercise 3x/week', progress: 65, target: 100 },
        { id: '2', title: 'Read 12 books/year', progress: 45, target: 100 },
      ];

      render(<IntelligentLifeCoachAI user={mockUser} goals={mockGoals} />);

      expect(screen.getByText(/goal progress/i)).toBeInTheDocument();
      expect(screen.getByText(/exercise 3x\/week/i)).toBeInTheDocument();
      expect(screen.getByText(/65%/i)).toBeInTheDocument();
    });

    it('suggests course corrections for struggling goals', async () => {
      const strugglingGoal = {
        id: '1',
        title: 'Exercise 3x/week',
        progress: 25,
        target: 100,
        daysStagnant: 14,
      };

      render(<IntelligentLifeCoachAI user={mockUser} goals={[strugglingGoal]} />);

      await waitFor(() => {
        expect(screen.getByText(/struggling with exercise/i)).toBeInTheDocument();
        expect(screen.getByText(/suggested adjustments/i)).toBeInTheDocument();
      });
    });

    it('celebrates achievements and milestones', async () => {
      const achievedGoal = {
        id: '1',
        title: 'Read 12 books/year',
        progress: 100,
        target: 100,
        completedAt: new Date().toISOString(),
      };

      render(<IntelligentLifeCoachAI user={mockUser} goals={[achievedGoal]} />);

      expect(screen.getByText(/congratulations/i)).toBeInTheDocument();
      expect(screen.getByText(/completed reading goal/i)).toBeInTheDocument();
    });
  });

  describe('Behavioral Pattern Analysis', () => {
    it('identifies productivity patterns', async () => {
      const mockPatterns = {
        peakProductivity: '9:00 AM - 11:00 AM',
        lowEnergyPeriods: ['2:00 PM - 3:00 PM'],
        mostProductiveDays: ['Tuesday', 'Wednesday'],
        recommendations: ['Schedule important tasks in morning', 'Take breaks during low energy'],
      };

      render(<IntelligentLifeCoachAI user={mockUser} patterns={mockPatterns} />);

      expect(screen.getByText(/productivity patterns/i)).toBeInTheDocument();
      expect(screen.getByText(/9:00 AM - 11:00 AM/i)).toBeInTheDocument();
    });

    it('suggests habit modifications based on patterns', async () => {
      render(<IntelligentLifeCoachAI user={mockUser} />);

      const analyzeButton = screen.getByRole('button', { name: /analyze patterns/i });
      await userEvent.click(analyzeButton);

      await waitFor(() => {
        expect(screen.getByText(/habit recommendations/i)).toBeInTheDocument();
        expect(screen.getByText(/based on your patterns/i)).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('provides screen reader friendly AI responses', async () => {
      render(<IntelligentLifeCoachAI user={mockUser} />);

      const chatMessages = screen.getAllByRole('log');
      expect(chatMessages.length).toBeGreaterThan(0);

      chatMessages.forEach(message => {
        expect(message).toHaveAttribute('aria-live');
      });
    });

    it('supports keyboard navigation for AI interactions', async () => {
      render(<IntelligentLifeCoachAI user={mockUser} />);

      const chatInput = screen.getByPlaceholderText(/ask your life coach/i);
      chatInput.focus();

      fireEvent.keyDown(chatInput, { key: 'Enter' });
      await waitFor(() => {
        expect(chatInput.value).toBe('');
      });
    });

    it('provides alternative text for AI-generated charts', async () => {
      render(<IntelligentLifeCoachAI user={mockUser} />);

      const charts = screen.getAllByRole('img');
      charts.forEach(chart => {
        expect(chart).toHaveAttribute('alt');
        expect(chart.getAttribute('alt')).not.toBe('');
      });
    });
  });

  describe('Performance and Error Handling', () => {
    it('handles slow AI responses gracefully', async () => {
      const { generateInsight } = require('../../../services/ragCategorization');
      generateInsight.mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve({
          insight: 'Delayed response',
          confidence: 0.8,
        }), 3000))
      );

      render(<IntelligentLifeCoachAI user={mockUser} />);

      const generateButton = screen.getByRole('button', { name: /generate insights/i });
      await userEvent.click(generateButton);

      // Should show loading state
      expect(screen.getByText(/generating insights/i)).toBeInTheDocument();
    });

    it('respects rate limits for AI requests', async () => {
      render(<IntelligentLifeCoachAI user={mockUser} />);

      const generateButton = screen.getByRole('button', { name: /generate insights/i });
      
      // Rapid clicking should be handled
      await userEvent.click(generateButton);
      await userEvent.click(generateButton);
      await userEvent.click(generateButton);

      // Should only make one request or show rate limit message
      await waitFor(() => {
        const loadingElements = screen.queryAllByText(/generating/i);
        expect(loadingElements.length).toBeLessThanOrEqual(1);
      });
    });

    it('maintains conversation history efficiently', async () => {
      render(<IntelligentLifeCoachAI user={mockUser} />);

      // Simulate long conversation
      const chatInput = screen.getByPlaceholderText(/ask your life coach/i);
      
      for (let i = 0; i < 20; i++) {
        await userEvent.type(chatInput, `Message ${i}`);
        fireEvent.click(screen.getByRole('button', { name: /send/i }));
        await userEvent.clear(chatInput);
      }

      // Should handle memory efficiently
      const messages = screen.getAllByRole('listitem');
      expect(messages.length).toBeLessThanOrEqual(10); // Should limit history
    });
  });

  describe('Privacy and Security', () => {
    it('does not expose sensitive user data in AI requests', async () => {
      const { generateInsight } = require('../../../services/ragCategorization');
      
      render(<IntelligentLifeCoachAI user={mockUser} />);

      const generateButton = screen.getByRole('button', { name: /generate insights/i });
      await userEvent.click(generateButton);

      // Check that sensitive data is filtered
      expect(generateInsight).toHaveBeenCalledWith(
        expect.not.objectContaining({
          email: expect.any(String),
          password: expect.any(String),
          ssn: expect.any(String),
        })
      );
    });

    it('provides data usage transparency', async () => {
      render(<IntelligentLifeCoachAI user={mockUser} />);

      expect(screen.getByText(/data usage/i)).toBeInTheDocument();
      expect(screen.getByText(/privacy settings/i)).toBeInTheDocument();
    });
  });
});