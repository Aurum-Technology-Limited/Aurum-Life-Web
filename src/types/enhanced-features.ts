export interface Pillar {
  id: string;
  name: string;
  description: string;
  color: string;
  icon?: string; // Lucide icon name
  healthScore: number; // 0-100
  weeklyTimeTarget: number; // hours
  weeklyTimeActual: number; // hours
  streak: number; // consecutive days/weeks
  lastUpdated: Date;
  areas: Area[];
}

export interface Area {
  id: string;
  pillarId: string;
  name: string;
  description: string;
  color?: string;
  icon?: string; // Lucide icon name
  healthScore: number;
  projects: Project[];
}

export interface ProjectAttachment {
  id: string;
  fileName: string;
  originalName: string;
  fileSize: number; // in bytes
  fileType: string; // MIME type
  uploadedAt: Date;
  uploadedBy?: string; // user ID
  url?: string; // file URL if stored externally
  thumbnail?: string; // thumbnail URL for images
}

export interface Project {
  id: string;
  areaId: string;
  name: string;
  description: string;
  status: 'planning' | 'active' | 'paused' | 'completed' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  color?: string;
  icon?: string; // Lucide icon name
  dueDate?: Date;
  completedAt?: Date;
  tasks: Task[];
  impactScore: number; // 1-10
  attachments: ProjectAttachment[];
}

export interface Task {
  id: string;
  projectId: string;
  name: string;
  description?: string;
  status: 'todo' | 'in-progress' | 'completed' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  color?: string;
  icon?: string; // Lucide icon name
  estimatedHours?: number;
  actualHours?: number;
  dueDate?: Date;
  completedAt?: Date;
  energyLevel?: 'low' | 'medium' | 'high';
  tags: string[];
}

export interface QuickCaptureItem {
  id: string;
  content: string;
  type: 'idea' | 'task' | 'note' | 'goal';
  suggestedPillar?: string;
  suggestedArea?: string;
  suggestedProject?: string;
  confidence?: number; // AI confidence in categorization
  createdAt: Date;
  processed: boolean;
}

export interface ProgressSnapshot {
  id: string;
  date: Date;
  pillarHealthScores: Record<string, number>;
  totalTasksCompleted: number;
  totalHoursLogged: number;
  energyLevels: Record<string, number>; // time -> energy level
  achievements: Achievement[];
}

export interface Achievement {
  id: string;
  title: string;
  description: string;
  type: 'streak' | 'completion' | 'milestone' | 'improvement';
  pillarId?: string;
  earnedAt: Date;
  icon: string;
}

export interface ReviewSession {
  id: string;
  type: 'weekly' | 'monthly' | 'quarterly';
  date: Date;
  reflections: Record<string, string>; // prompt -> response
  wins: string[];
  improvements: string[];
  nextWeekFocus: string[];
  pillarAdjustments: Record<string, number>; // pillarId -> new time allocation
  completed: boolean;
}

export interface TimeBlock {
  id: string;
  title: string;
  pillarId: string;
  projectId?: string;
  taskIds: string[];
  startTime: Date;
  endTime: Date;
  energyLevel: 'low' | 'medium' | 'high';
  actualStartTime?: Date;
  actualEndTime?: Date;
  notes?: string;
  completed: boolean;
}

export interface EnergyPattern {
  userId: string;
  hourOfDay: number; // 0-23
  dayOfWeek: number; // 0-6
  averageEnergyLevel: number; // 1-10
  sampleSize: number;
  lastUpdated: Date;
}

export interface SmartSuggestion {
  id: string;
  type: 'scheduling' | 'prioritization' | 'energy-optimization' | 'time-allocation';
  title: string;
  description: string;
  confidence: number;
  actionData: any;
  dismissed: boolean;
  createdAt: Date;
}