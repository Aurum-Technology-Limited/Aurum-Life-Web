/**
 * Mock Service Worker (MSW) Server Setup
 * Provides realistic API mocking for testing
 */

import { setupServer } from 'msw/node';
import { rest } from 'msw';
import { 
  createMockUser, 
  createMockPillar, 
  createMockArea, 
  createMockProject, 
  createMockTask,
  createMockJournalEntry 
} from '../setup';

// Mock data stores
const mockUsers = [createMockUser()];
const mockPillars = [
  createMockPillar({ id: '1', title: 'Health & Wellness', color: '#10B981' }),
  createMockPillar({ id: '2', title: 'Career & Finance', color: '#F59E0B' }),
  createMockPillar({ id: '3', title: 'Relationships', color: '#EF4444' }),
];
const mockAreas = [
  createMockArea({ id: '1', pillar_id: '1', title: 'Fitness' }),
  createMockArea({ id: '2', pillar_id: '1', title: 'Nutrition' }),
  createMockArea({ id: '3', pillar_id: '2', title: 'Skill Development' }),
];
const mockProjects = [
  createMockProject({ id: '1', area_id: '1', title: 'Morning Workout Routine' }),
  createMockProject({ id: '2', area_id: '2', title: 'Meal Prep System' }),
];
const mockTasks = [
  createMockTask({ id: '1', project_id: '1', title: 'Go for a 30-minute run' }),
  createMockTask({ id: '2', project_id: '1', title: 'Complete strength training' }),
  createMockTask({ id: '3', project_id: '2', title: 'Plan weekly meals' }),
];
const mockJournalEntries = [
  createMockJournalEntry({ id: '1', title: 'Daily Reflection' }),
  createMockJournalEntry({ id: '2', title: 'Goal Setting Session' }),
];

// Mock handlers
export const handlers = [
  // Auth endpoints
  rest.post('/auth/signup', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        user: createMockUser(),
        session: { access_token: 'mock-token' },
      })
    );
  }),

  rest.post('/auth/signin', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        user: mockUsers[0],
        session: { access_token: 'mock-token' },
      })
    );
  }),

  rest.post('/auth/signout', (req, res, ctx) => {
    return res(ctx.status(200));
  }),

  rest.get('/auth/session', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        user: mockUsers[0],
        session: { access_token: 'mock-token' },
      })
    );
  }),

  // Pillars endpoints
  rest.get('/api/pillars', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json(mockPillars)
    );
  }),

  rest.post('/api/pillars', (req, res, ctx) => {
    const newPillar = createMockPillar({
      id: String(mockPillars.length + 1),
      ...(req.body as any),
    });
    mockPillars.push(newPillar);
    return res(
      ctx.status(201),
      ctx.json(newPillar)
    );
  }),

  rest.put('/api/pillars/:id', (req, res, ctx) => {
    const { id } = req.params;
    const pillarIndex = mockPillars.findIndex(p => p.id === id);
    if (pillarIndex === -1) {
      return res(ctx.status(404));
    }
    mockPillars[pillarIndex] = { ...mockPillars[pillarIndex], ...(req.body as any) };
    return res(
      ctx.status(200),
      ctx.json(mockPillars[pillarIndex])
    );
  }),

  rest.delete('/api/pillars/:id', (req, res, ctx) => {
    const { id } = req.params;
    const pillarIndex = mockPillars.findIndex(p => p.id === id);
    if (pillarIndex === -1) {
      return res(ctx.status(404));
    }
    mockPillars.splice(pillarIndex, 1);
    return res(ctx.status(200));
  }),

  // Areas endpoints
  rest.get('/api/areas', (req, res, ctx) => {
    const pillarId = req.url.searchParams.get('pillar_id');
    const filteredAreas = pillarId 
      ? mockAreas.filter(a => a.pillar_id === pillarId)
      : mockAreas;
    return res(
      ctx.status(200),
      ctx.json(filteredAreas)
    );
  }),

  rest.post('/api/areas', (req, res, ctx) => {
    const newArea = createMockArea({
      id: String(mockAreas.length + 1),
      ...(req.body as any),
    });
    mockAreas.push(newArea);
    return res(
      ctx.status(201),
      ctx.json(newArea)
    );
  }),

  // Projects endpoints
  rest.get('/api/projects', (req, res, ctx) => {
    const areaId = req.url.searchParams.get('area_id');
    const filteredProjects = areaId 
      ? mockProjects.filter(p => p.area_id === areaId)
      : mockProjects;
    return res(
      ctx.status(200),
      ctx.json(filteredProjects)
    );
  }),

  rest.post('/api/projects', (req, res, ctx) => {
    const newProject = createMockProject({
      id: String(mockProjects.length + 1),
      ...(req.body as any),
    });
    mockProjects.push(newProject);
    return res(
      ctx.status(201),
      ctx.json(newProject)
    );
  }),

  // Tasks endpoints
  rest.get('/api/tasks', (req, res, ctx) => {
    const projectId = req.url.searchParams.get('project_id');
    const status = req.url.searchParams.get('status');
    let filteredTasks = mockTasks;
    
    if (projectId) {
      filteredTasks = filteredTasks.filter(t => t.project_id === projectId);
    }
    if (status) {
      filteredTasks = filteredTasks.filter(t => t.status === status);
    }
    
    return res(
      ctx.status(200),
      ctx.json(filteredTasks)
    );
  }),

  rest.post('/api/tasks', (req, res, ctx) => {
    const newTask = createMockTask({
      id: String(mockTasks.length + 1),
      ...(req.body as any),
    });
    mockTasks.push(newTask);
    return res(
      ctx.status(201),
      ctx.json(newTask)
    );
  }),

  rest.put('/api/tasks/:id', (req, res, ctx) => {
    const { id } = req.params;
    const taskIndex = mockTasks.findIndex(t => t.id === id);
    if (taskIndex === -1) {
      return res(ctx.status(404));
    }
    mockTasks[taskIndex] = { ...mockTasks[taskIndex], ...(req.body as any) };
    return res(
      ctx.status(200),
      ctx.json(mockTasks[taskIndex])
    );
  }),

  // Journal endpoints
  rest.get('/api/journal-entries', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json(mockJournalEntries)
    );
  }),

  rest.post('/api/journal-entries', (req, res, ctx) => {
    const newEntry = createMockJournalEntry({
      id: String(mockJournalEntries.length + 1),
      ...(req.body as any),
    });
    mockJournalEntries.push(newEntry);
    return res(
      ctx.status(201),
      ctx.json(newEntry)
    );
  }),

  // AI endpoints
  rest.post('/api/ai/categorize', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        category: 'health',
        confidence: 0.95,
        suggestions: ['fitness', 'nutrition', 'wellness'],
      })
    );
  }),

  rest.post('/api/ai/analyze', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        insights: ['Focus on consistency', 'Consider setting smaller goals'],
        score: 85,
        recommendations: ['Schedule specific workout times', 'Track progress weekly'],
      })
    );
  }),

  // Analytics endpoints
  rest.get('/api/analytics/overview', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        totalTasks: 25,
        completedTasks: 18,
        activePillars: 3,
        weeklyProgress: 72,
        trends: {
          productivity: 'up',
          wellness: 'stable',
          learning: 'up',
        },
      })
    );
  }),

  // File upload endpoints
  rest.post('/api/upload', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        url: 'https://example.com/uploaded-file.pdf',
        filename: 'document.pdf',
        size: 1024,
      })
    );
  }),

  // Error simulation for testing error handling
  rest.get('/api/error-test', (req, res, ctx) => {
    return res(
      ctx.status(500),
      ctx.json({ error: 'Internal server error' })
    );
  }),

  rest.get('/api/timeout-test', (req, res, ctx) => {
    return res(
      ctx.delay(10000), // 10 second delay to simulate timeout
      ctx.status(200),
      ctx.json({ message: 'This should timeout' })
    );
  }),

  // Catch-all handler for unhandled requests
  rest.get('*', (req, res, ctx) => {
    console.warn(`Unhandled ${req.method} request to ${req.url.href}`);
    return res(
      ctx.status(404),
      ctx.json({ error: 'Not found' })
    );
  }),
];

// Create the server
export const server = setupServer(...handlers);