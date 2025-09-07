// Mock data for Aurum Life application

export const mockHabits = [
  {
    id: '1',
    name: 'Morning Meditation',
    description: 'Start the day with mindful breathing',
    streak: 12,
    target: 30,
    completed: true,
    category: 'mindfulness',
    color: '#F4B400'
  },
  {
    id: '2',
    name: 'Read 30 Minutes',
    description: 'Daily reading for personal growth',
    streak: 8,
    target: 21,
    completed: false,
    category: 'learning',
    color: '#F4B400'
  },
  {
    id: '3',
    name: 'Exercise',
    description: 'Physical fitness routine',
    streak: 15,
    target: 60,
    completed: true,
    category: 'health',
    color: '#F4B400'
  },
  {
    id: '4',
    name: 'Gratitude Journal',
    description: 'Write 3 things I\'m grateful for',
    streak: 6,
    target: 14,
    completed: false,
    category: 'reflection',
    color: '#F4B400'
  }
];

export const mockJournalEntries = [
  {
    id: '1',
    title: 'Reflections on Growth',
    content: 'Today I realized the importance of consistency in building habits. Small daily actions compound into significant changes over time...',
    date: '2025-07-15',
    mood: 'optimistic',
    tags: ['growth', 'habits', 'consistency']
  },
  {
    id: '2',
    title: 'Overcoming Challenges',
    content: 'Faced some difficulties with time management today. Learning to prioritize what truly matters and saying no to distractions...',
    date: '2025-07-14',
    mood: 'reflective',
    tags: ['challenges', 'time-management', 'focus']
  },
  {
    id: '3',
    title: 'Moments of Clarity',
    content: 'The meditation session this morning brought such clarity. I feel more connected to my purpose and excited about the journey ahead...',
    date: '2025-07-13',
    mood: 'inspired',
    tags: ['meditation', 'clarity', 'purpose']
  }
];

export const mockTasks = [
  {
    id: '1',
    title: 'Complete mindfulness course module 3',
    description: 'Focus on breathing techniques and body awareness',
    priority: 'high',
    completed: false,
    dueDate: '2025-07-16',
    category: 'learning'
  },
  {
    id: '2',
    title: 'Schedule coaching session',
    description: 'Book next session with personal development coach',
    priority: 'medium',
    completed: false,
    dueDate: '2025-07-17',
    category: 'coaching'
  },
  {
    id: '3',
    title: 'Update habit tracker',
    description: 'Review and adjust daily habits based on progress',
    priority: 'low',
    completed: true,
    dueDate: '2025-07-15',
    category: 'planning'
  },
  {
    id: '4',
    title: 'Practice gratitude meditation',
    description: '15-minute guided gratitude practice',
    priority: 'high',
    completed: false,
    dueDate: '2025-07-16',
    category: 'mindfulness'
  }
];

export const mockCourses = [
  {
    id: '1',
    title: 'Mindful Leadership',
    description: 'Develop leadership skills through mindfulness practices',
    progress: 65,
    instructor: 'Dr. Sarah Johnson',
    duration: '8 weeks',
    category: 'leadership',
    image: 'https://images.unsplash.com/photo-1573164713714-d95e436ab8d6?w=400&h=250&fit=crop'
  },
  {
    id: '2',
    title: 'Emotional Intelligence Mastery',
    description: 'Build emotional awareness and regulation skills',
    progress: 40,
    instructor: 'Prof. Michael Chen',
    duration: '6 weeks',
    category: 'emotional-intelligence',
    image: 'https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=400&h=250&fit=crop'
  },
  {
    id: '3',
    title: 'Productivity & Flow States',
    description: 'Master deep work and achieve peak performance',
    progress: 85,
    instructor: 'Alex Rodriguez',
    duration: '4 weeks',
    category: 'productivity',
    image: 'https://images.unsplash.com/photo-1551836022-deb4988cc6c0?w=400&h=250&fit=crop'
  }
];

export const mockBadges = [
  {
    id: '1',
    name: 'Consistency Champion',
    description: 'Maintained habits for 30 consecutive days',
    earned: true,
    earnedDate: '2025-07-10',
    icon: '🏆',
    rarity: 'gold'
  },
  {
    id: '2',
    name: 'Mindfulness Master',
    description: 'Completed 100 meditation sessions',
    earned: true,
    earnedDate: '2025-07-05',
    icon: '🧘',
    rarity: 'silver'
  },
  {
    id: '3',
    name: 'Learning Enthusiast',
    description: 'Finished 3 courses in personal development',
    earned: false,
    progress: 67,
    icon: '📚',
    rarity: 'bronze'
  },
  {
    id: '4',
    name: 'Reflection Sage',
    description: 'Wrote 50 journal entries',
    earned: false,
    progress: 84,
    icon: '✍️',
    rarity: 'gold'
  }
];

export const mockChatMessages = [
  {
    id: '1',
    type: 'ai',
    content: 'Good morning! I noticed you\'ve been consistent with your meditation practice. How are you feeling about your progress?',
    timestamp: '2025-07-15T09:00:00Z'
  },
  {
    id: '2',
    type: 'user',
    content: 'I\'m feeling more centered lately, but sometimes I struggle with maintaining focus during longer sessions.',
    timestamp: '2025-07-15T09:02:00Z'
  },
  {
    id: '3',
    type: 'ai',
    content: 'That\'s completely normal! Even experienced meditators face this. Would you like me to suggest some techniques specifically for improving sustained attention?',
    timestamp: '2025-07-15T09:03:00Z'
  },
  {
    id: '4',
    type: 'user',
    content: 'Yes, that would be helpful!',
    timestamp: '2025-07-15T09:04:00Z'
  },
  {
    id: '5',
    type: 'ai',
    content: 'Great! Try the "noting" technique: when your mind wanders, simply note "thinking" and gently return to your breath. Also, consider shorter sessions (10-15 minutes) with full focus rather than longer distracted ones. Would you like me to set a reminder for your next practice?',
    timestamp: '2025-07-15T09:05:00Z'
  }
];

export const mockStats = {
  totalHabits: 4,
  habitsCompleted: 2,
  currentStreak: 15,
  journalEntries: 3,
  coursesInProgress: 2,
  coursesCompleted: 1,
  badgesEarned: 2,
  totalPoints: 1250,
  level: 7
};

export const getStoredData = (key, defaultValue) => {
  try {
    const stored = localStorage.getItem(`aurum_${key}`);
    return stored ? JSON.parse(stored) : defaultValue;
  } catch {
    return defaultValue;
  }
};

export const setStoredData = (key, value) => {
  try {
    localStorage.setItem(`aurum_${key}`, JSON.stringify(value));
  } catch (error) {
    console.error('Error storing data:', error);
  }
};