/**
 * Team Collaboration Hub Component Tests
 * Comprehensive testing for Phase 4 team collaboration features
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import TeamCollaborationHub from '../../../components/enhanced/TeamCollaborationHub';

// Mock real-time service
jest.mock('../../../services/realTimeDataService', () => ({
  subscribeToTeamUpdates: jest.fn(),
  sendTeamMessage: jest.fn(),
  shareGoalWithTeam: jest.fn(),
  inviteTeamMember: jest.fn(),
}));

describe('TeamCollaborationHub Component', () => {
  const mockUser = {
    id: '1',
    email: 'test@aurumlife.com',
    name: 'Test User',
    role: 'admin',
  };

  const mockTeam = {
    id: 'team-1',
    name: 'Development Team',
    members: [
      { id: '1', name: 'Test User', role: 'admin', status: 'online' },
      { id: '2', name: 'Jane Doe', role: 'member', status: 'away' },
      { id: '3', name: 'John Smith', role: 'member', status: 'offline' },
    ],
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Team Management', () => {
    it('displays team overview correctly', async () => {
      render(<TeamCollaborationHub user={mockUser} team={mockTeam} />);

      expect(screen.getByText('Development Team')).toBeInTheDocument();
      expect(screen.getByText('3 members')).toBeInTheDocument();
      expect(screen.getByText(/team collaboration/i)).toBeInTheDocument();
    });

    it('shows team member status indicators', async () => {
      render(<TeamCollaborationHub user={mockUser} team={mockTeam} />);

      expect(screen.getByText('Test User')).toBeInTheDocument();
      expect(screen.getByText('Jane Doe')).toBeInTheDocument();
      expect(screen.getByText('John Smith')).toBeInTheDocument();

      // Check status indicators
      expect(screen.getByText(/online/i)).toBeInTheDocument();
      expect(screen.getByText(/away/i)).toBeInTheDocument();
      expect(screen.getByText(/offline/i)).toBeInTheDocument();
    });

    it('allows admin to invite new team members', async () => {
      const { inviteTeamMember } = require('../../../services/realTimeDataService');
      inviteTeamMember.mockResolvedValue({ success: true });

      render(<TeamCollaborationHub user={mockUser} team={mockTeam} />);

      const inviteButton = screen.getByRole('button', { name: /invite member/i });
      await userEvent.click(inviteButton);

      const emailInput = screen.getByPlaceholderText(/enter email/i);
      await userEvent.type(emailInput, 'newmember@aurumlife.com');

      const sendInviteButton = screen.getByRole('button', { name: /send invitation/i });
      await userEvent.click(sendInviteButton);

      await waitFor(() => {
        expect(inviteTeamMember).toHaveBeenCalledWith('team-1', 'newmember@aurumlife.com');
      });
    });

    it('restricts member actions for non-admin users', async () => {
      const memberUser = { ...mockUser, role: 'member' };
      render(<TeamCollaborationHub user={memberUser} team={mockTeam} />);

      expect(screen.queryByRole('button', { name: /invite member/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /remove member/i })).not.toBeInTheDocument();
    });
  });

  describe('Goal Sharing and Collaboration', () => {
    it('allows sharing goals with team members', async () => {
      const { shareGoalWithTeam } = require('../../../services/realTimeDataService');
      shareGoalWithTeam.mockResolvedValue({ success: true });

      const mockGoal = {
        id: 'goal-1',
        title: 'Complete Q4 Project',
        description: 'Finish development by end of quarter',
        progress: 75,
      };

      render(<TeamCollaborationHub user={mockUser} team={mockTeam} />);

      const shareButton = screen.getByRole('button', { name: /share goal/i });
      await userEvent.click(shareButton);

      const goalSelector = screen.getByRole('combobox', { name: /select goal/i });
      await userEvent.click(goalSelector);
      await userEvent.click(screen.getByText('Complete Q4 Project'));

      const confirmShare = screen.getByRole('button', { name: /share with team/i });
      await userEvent.click(confirmShare);

      await waitFor(() => {
        expect(shareGoalWithTeam).toHaveBeenCalledWith('team-1', 'goal-1');
      });
    });

    it('displays shared team goals', async () => {
      const sharedGoals = [
        {
          id: 'shared-1',
          title: 'Team Fitness Challenge',
          sharedBy: 'Jane Doe',
          participants: ['1', '2'],
          progress: 60,
        },
      ];

      render(<TeamCollaborationHub user={mockUser} team={mockTeam} sharedGoals={sharedGoals} />);

      expect(screen.getByText('Team Fitness Challenge')).toBeInTheDocument();
      expect(screen.getByText('Shared by Jane Doe')).toBeInTheDocument();
      expect(screen.getByText('60%')).toBeInTheDocument();
    });

    it('allows joining shared goals', async () => {
      const sharedGoals = [
        {
          id: 'shared-1',
          title: 'Team Fitness Challenge',
          sharedBy: 'Jane Doe',
          participants: ['2'],
          progress: 60,
        },
      ];

      render(<TeamCollaborationHub user={mockUser} team={mockTeam} sharedGoals={sharedGoals} />);

      const joinButton = screen.getByRole('button', { name: /join goal/i });
      await userEvent.click(joinButton);

      await waitFor(() => {
        expect(screen.getByText(/joined team fitness challenge/i)).toBeInTheDocument();
      });
    });
  });

  describe('Real-time Communication', () => {
    it('displays team activity feed', async () => {
      const activities = [
        {
          id: 'activity-1',
          type: 'goal_completed',
          user: 'Jane Doe',
          message: 'completed their morning workout goal',
          timestamp: new Date().toISOString(),
        },
        {
          id: 'activity-2',
          type: 'goal_shared',
          user: 'John Smith',
          message: 'shared a new reading goal with the team',
          timestamp: new Date().toISOString(),
        },
      ];

      render(<TeamCollaborationHub user={mockUser} team={mockTeam} activities={activities} />);

      expect(screen.getByText(/team activity/i)).toBeInTheDocument();
      expect(screen.getByText(/jane doe/i)).toBeInTheDocument();
      expect(screen.getByText(/completed their morning workout/i)).toBeInTheDocument();
      expect(screen.getByText(/john smith/i)).toBeInTheDocument();
      expect(screen.getByText(/shared a new reading goal/i)).toBeInTheDocument();
    });

    it('supports team messaging', async () => {
      const { sendTeamMessage } = require('../../../services/realTimeDataService');
      sendTeamMessage.mockResolvedValue({ success: true });

      render(<TeamCollaborationHub user={mockUser} team={mockTeam} />);

      const messageInput = screen.getByPlaceholderText(/message your team/i);
      await userEvent.type(messageInput, 'Great job everyone on this week\'s progress!');

      const sendButton = screen.getByRole('button', { name: /send message/i });
      await userEvent.click(sendButton);

      await waitFor(() => {
        expect(sendTeamMessage).toHaveBeenCalledWith('team-1', 'Great job everyone on this week\'s progress!');
      });
    });

    it('shows real-time message notifications', async () => {
      const { subscribeToTeamUpdates } = require('../../../services/realTimeDataService');
      let updateCallback: any;

      subscribeToTeamUpdates.mockImplementation((teamId, callback) => {
        updateCallback = callback;
        return { unsubscribe: jest.fn() };
      });

      render(<TeamCollaborationHub user={mockUser} team={mockTeam} />);

      // Simulate real-time message
      const newMessage = {
        id: 'msg-1',
        from: 'Jane Doe',
        message: 'Just finished my workout!',
        timestamp: new Date().toISOString(),
      };

      if (updateCallback) {
        updateCallback({ type: 'message', data: newMessage });
      }

      await waitFor(() => {
        expect(screen.getByText(/jane doe/i)).toBeInTheDocument();
        expect(screen.getByText(/just finished my workout/i)).toBeInTheDocument();
      });
    });
  });

  describe('Team Analytics and Insights', () => {
    it('displays team progress overview', async () => {
      const teamStats = {
        totalGoals: 25,
        completedGoals: 18,
        activeMembers: 3,
        weeklyProgress: 85,
      };

      render(<TeamCollaborationHub user={mockUser} team={mockTeam} stats={teamStats} />);

      expect(screen.getByText('25')).toBeInTheDocument(); // Total goals
      expect(screen.getByText('18')).toBeInTheDocument(); // Completed goals
      expect(screen.getByText('85%')).toBeInTheDocument(); // Weekly progress
    });

    it('shows team member leaderboard', async () => {
      const leaderboard = [
        { name: 'Jane Doe', points: 1250, goals: 8 },
        { name: 'Test User', points: 1100, goals: 7 },
        { name: 'John Smith', points: 950, goals: 5 },
      ];

      render(<TeamCollaborationHub user={mockUser} team={mockTeam} leaderboard={leaderboard} />);

      expect(screen.getByText(/leaderboard/i)).toBeInTheDocument();
      expect(screen.getByText('Jane Doe')).toBeInTheDocument();
      expect(screen.getByText('1250 points')).toBeInTheDocument();
    });

    it('provides team performance insights', async () => {
      render(<TeamCollaborationHub user={mockUser} team={mockTeam} />);

      expect(screen.getByText(/team insights/i)).toBeInTheDocument();
      expect(screen.getByText(/most active day/i)).toBeInTheDocument();
      expect(screen.getByText(/collaboration score/i)).toBeInTheDocument();
    });
  });

  describe('Privacy and Permissions', () => {
    it('respects goal privacy settings', async () => {
      const privateGoal = {
        id: 'goal-private',
        title: 'Personal Development',
        isPrivate: true,
        owner: '1',
      };

      render(<TeamCollaborationHub user={mockUser} team={mockTeam} />);

      // Private goal should not be visible in sharing options
      const shareButton = screen.getByRole('button', { name: /share goal/i });
      await userEvent.click(shareButton);

      expect(screen.queryByText('Personal Development')).not.toBeInTheDocument();
    });

    it('allows users to control their visibility status', async () => {
      render(<TeamCollaborationHub user={mockUser} team={mockTeam} />);

      const statusButton = screen.getByRole('button', { name: /status: online/i });
      await userEvent.click(statusButton);

      expect(screen.getByText(/away/i)).toBeInTheDocument();
      expect(screen.getByText(/do not disturb/i)).toBeInTheDocument();
    });

    it('filters sensitive data from team sharing', async () => {
      const sensitiveGoal = {
        id: 'goal-sensitive',
        title: 'Health Recovery',
        tags: ['medical', 'private'],
        details: 'Confidential medical information',
      };

      render(<TeamCollaborationHub user={mockUser} team={mockTeam} />);

      // Should not expose sensitive details
      expect(screen.queryByText(/confidential medical/i)).not.toBeInTheDocument();
    });
  });

  describe('Accessibility and Usability', () => {
    it('provides screen reader announcements for team updates', async () => {
      render(<TeamCollaborationHub user={mockUser} team={mockTeam} />);

      const liveRegion = screen.getByRole('log', { name: /team updates/i });
      expect(liveRegion).toHaveAttribute('aria-live', 'polite');
    });

    it('supports keyboard navigation for team actions', async () => {
      render(<TeamCollaborationHub user={mockUser} team={mockTeam} />);

      const firstButton = screen.getAllByRole('button')[0];
      firstButton.focus();

      fireEvent.keyDown(firstButton, { key: 'Tab' });
      expect(document.activeElement).not.toBe(firstButton);
    });

    it('provides clear role and permission indicators', async () => {
      render(<TeamCollaborationHub user={mockUser} team={mockTeam} />);

      expect(screen.getByText(/admin/i)).toBeInTheDocument();
      expect(screen.getByText(/member/i)).toBeInTheDocument();
    });

    it('handles offline mode gracefully', async () => {
      // Mock offline state
      Object.defineProperty(navigator, 'onLine', {
        writable: true,
        value: false,
      });

      render(<TeamCollaborationHub user={mockUser} team={mockTeam} />);

      expect(screen.getByText(/offline mode/i)).toBeInTheDocument();
      expect(screen.getByText(/changes will sync/i)).toBeInTheDocument();
    });
  });

  describe('Performance and Scalability', () => {
    it('handles large team sizes efficiently', async () => {
      const largeTeam = {
        ...mockTeam,
        members: Array.from({ length: 100 }, (_, i) => ({
          id: `user-${i}`,
          name: `User ${i}`,
          role: 'member',
          status: 'online',
        })),
      };

      render(<TeamCollaborationHub user={mockUser} team={largeTeam} />);

      // Should virtualize or paginate large member lists
      const memberElements = screen.getAllByText(/user \d+/i);
      expect(memberElements.length).toBeLessThanOrEqual(20); // Should limit visible items
    });

    it('debounces real-time updates to prevent spam', async () => {
      const { subscribeToTeamUpdates } = require('../../../services/realTimeDataService');
      let updateCallback: any;

      subscribeToTeamUpdates.mockImplementation((teamId, callback) => {
        updateCallback = callback;
        return { unsubscribe: jest.fn() };
      });

      render(<TeamCollaborationHub user={mockUser} team={mockTeam} />);

      // Simulate rapid updates
      if (updateCallback) {
        updateCallback({ type: 'activity', data: { message: 'Update 1' } });
        updateCallback({ type: 'activity', data: { message: 'Update 2' } });
        updateCallback({ type: 'activity', data: { message: 'Update 3' } });
      }

      // Should batch or debounce updates
      await waitFor(() => {
        const updates = screen.queryAllByText(/update \d/i);
        expect(updates.length).toBeLessThanOrEqual(1);
      });
    });

    it('cleans up subscriptions on unmount', async () => {
      const { subscribeToTeamUpdates } = require('../../../services/realTimeDataService');
      const unsubscribeMock = jest.fn();

      subscribeToTeamUpdates.mockReturnValue({
        unsubscribe: unsubscribeMock,
      });

      const { unmount } = render(<TeamCollaborationHub user={mockUser} team={mockTeam} />);

      unmount();

      expect(unsubscribeMock).toHaveBeenCalled();
    });
  });
});