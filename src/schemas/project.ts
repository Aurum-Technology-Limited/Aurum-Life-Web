import { z } from 'zod';

// Task Schema
export const taskSchema = z.object({
  title: z
    .string()
    .min(1, 'Task title is required')
    .max(80, 'Task title must be less than 80 characters'),
  description: z
    .string()
    .max(80, 'Description must be less than 80 characters')
    .optional(),
  priority: z.enum(['low', 'medium', 'high']).default('medium'),
  dueDate: z.date().optional(),
  timeEstimate: z
    .number()
    .min(5, 'Minimum estimate is 5 minutes')
    .max(480, 'Maximum estimate is 8 hours')
    .optional(),
  tags: z.array(z.string().max(20, 'Tag must be less than 20 characters')).max(10, 'Maximum 10 tags allowed').default([]),
  projectId: z.string().min(1, 'Project is required'),
});

export type TaskFormData = z.infer<typeof taskSchema>;

// Project Schema
export const projectSchema = z.object({
  title: z
    .string()
    .min(1, 'Project title is required')
    .max(60, 'Project title must be less than 60 characters'),
  description: z
    .string()
    .max(120, 'Description must be less than 120 characters')
    .optional(),
  priority: z.enum(['low', 'medium', 'high']).default('medium'),
  status: z.enum(['not-started', 'in-progress', 'completed', 'paused']).default('not-started'),
  dueDate: z.date().optional(),
  areaId: z.string().min(1, 'Area is required'),
});

export type ProjectFormData = z.infer<typeof projectSchema>;

// Area Schema
export const areaSchema = z.object({
  title: z
    .string()
    .min(1, 'Area title is required')
    .max(40, 'Area title must be less than 40 characters'),
  description: z
    .string()
    .max(150, 'Description must be less than 150 characters')
    .optional(),
  pillarId: z.string().min(1, 'Pillar is required'),
});

export type AreaFormData = z.infer<typeof areaSchema>;

// Pillar Schema
export const pillarSchema = z.object({
  title: z
    .string()
    .min(1, 'Pillar title is required')
    .max(50, 'Pillar title must be less than 50 characters'),
  description: z
    .string()
    .max(200, 'Description must be less than 200 characters')
    .optional(),
  color: z
    .string()
    .regex(/^#[0-9A-F]{6}$/i, 'Please select a valid color')
    .default('#F4D03F'),
});

export type PillarFormData = z.infer<typeof pillarSchema>;

// Journal Entry Schema
export const journalEntrySchema = z.object({
  title: z
    .string()
    .max(100, 'Title must be less than 100 characters')
    .optional(),
  content: z
    .string()
    .min(1, 'Journal content is required')
    .max(5000, 'Content must be less than 5000 characters'),
  mood: z.enum(['very-bad', 'bad', 'neutral', 'good', 'very-good']).optional(),
  tags: z.array(z.string().max(20, 'Tag must be less than 20 characters')).max(10, 'Maximum 10 tags allowed').default([]),
  isPrivate: z.boolean().default(true),
});

export type JournalEntryFormData = z.infer<typeof journalEntrySchema>;

// Goal Schema
export const goalSchema = z.object({
  title: z
    .string()
    .min(1, 'Goal title is required')
    .max(150, 'Goal title must be less than 150 characters'),
  description: z
    .string()
    .max(1000, 'Description must be less than 1000 characters')
    .optional(),
  type: z.enum(['outcome', 'habit', 'milestone']).default('outcome'),
  priority: z.enum(['low', 'medium', 'high']).default('medium'),
  targetDate: z.date().optional(),
  pillarId: z.string().min(1, 'Pillar is required'),
  measurable: z.boolean().default(false),
  targetValue: z.number().optional(),
  currentValue: z.number().default(0),
  unit: z.string().optional(),
});

export type GoalFormData = z.infer<typeof goalSchema>;