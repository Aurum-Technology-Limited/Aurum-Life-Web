import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  Target, 
  FolderKanban, 
  Layers3, 
  CheckSquare, 
  ChevronDown,
  ChevronRight,
  Compass,
  BarChart3,
  Clock,
  Building,
  Users,
  Heart,
  Briefcase,
  GraduationCap,
  Home,
  DollarSign,
  Brain
} from 'lucide-react';
import { Button } from '../../ui/button';
import { Card } from '../../ui/card';
import OnboardingLayout from '../OnboardingLayout';
import { useOnboardingStore } from '../../../stores/onboardingStore';

const PAPT_LEVELS = [
  {
    id: 'pillars',
    title: 'Pillars - Your Life\'s Foundation',
    icon: Target,
    description: 'The core areas that define your identity and values. These are the fundamental aspects of life that matter most to you.',
    color: '#F4D03F',
    examples: [
      { icon: Briefcase, label: 'Career & Success' },
      { icon: Users, label: 'Family & Relationships' },
      { icon: Heart, label: 'Health & Wellness' },
      { icon: DollarSign, label: 'Financial Freedom' },
      { icon: GraduationCap, label: 'Learning & Growth' },
      { icon: Brain, label: 'Spiritual & Personal' }
    ],
    explanation: 'Most people have 4-6 core pillars. These represent the major themes of your life - your non-negotiables that deserve intentional attention and energy.',
    hierarchy: 'These will be your pillars'
  },
  {
    id: 'areas',
    title: 'Areas - Your Life Domains',
    icon: Building,
    description: 'Specific roles, responsibilities, and domains within each pillar. Areas are ongoing aspects of your life that require continuous attention.',
    color: '#3B82F6',
    examples: [
      { parent: 'Health & Wellness', items: ['🏋️ Physical Fitness', '🥗 Nutrition & Diet', '😴 Sleep & Recovery', '🧠 Mental Health'] },
      { parent: 'Career & Success', items: ['💼 Current Job Performance', '📈 Skill Development', '🤝 Professional Network', '🎯 Career Advancement'] }
    ],
    explanation: 'Areas are like the rooms in your life\'s house. Each pillar contains 3-5 areas that need regular maintenance and improvement.',
    hierarchy: 'Areas organize your pillars'
  },
  {
    id: 'projects',
    title: 'Projects - Specific Outcomes',
    icon: FolderKanban,
    description: 'Time-bound initiatives with clear outcomes. Projects transform your areas from maintenance mode into growth mode.',
    color: '#10B981',
    examples: [
      { parent: 'Physical Fitness Area', items: ['🏃 Complete 5K Training Program (8 weeks)', '💪 Build Home Gym Setup (1 month)', '🎯 Improve Flexibility Routine (ongoing)'] },
      { parent: 'Career Development Area', items: ['📊 Complete Data Analytics Course (3 months)', '🤝 Attend 5 Industry Networking Events (6 months)', '📝 Update Resume & LinkedIn Profile (2 weeks)'] }
    ],
    explanation: 'Projects have specific start and end points. They\'re how you make measurable progress in your areas rather than just maintaining them.',
    hierarchy: 'Projects drive area growth'
  },
  {
    id: 'tasks',
    title: 'Tasks - Daily Actions',
    icon: CheckSquare,
    description: 'The specific, actionable steps that move your projects forward. Tasks are what you actually do each day.',
    color: '#8B5CF6',
    examples: [
      { 
        parent: 'Complete 5K Training Program Project', 
        items: [
          '✅ Research training plans online',
          '✅ Choose beginner-friendly program', 
          '🔄 Week 1: Run/walk intervals (3x this week)',
          '⏳ Track progress in fitness app',
          '⏳ Schedule weekly progress reviews',
          '⏳ Register for local 5K race'
        ]
      }
    ],
    explanation: 'Tasks are your daily to-dos, but they\'re not random. Every task connects to a project, which serves an area, which strengthens a pillar. This creates intentional, purposeful action.',
    hierarchy: 'Tasks are daily actions'
  }
];

const QUIZ_ITEMS = [
  { text: 'Complete morning workout', answer: 'task', level: 'Tasks' },
  { text: 'Health & Wellness', answer: 'pillar', level: 'Pillars' },
  { text: 'Physical Fitness', answer: 'area', level: 'Areas' },
  { text: 'Train for Marathon', answer: 'project', level: 'Projects' },
  { text: 'Review quarterly goals', answer: 'task', level: 'Tasks' },
  { text: 'Career Development', answer: 'area', level: 'Areas' }
];

export default function PAPTFrameworkExplanation() {
  const { nextStep, updatePAPTUnderstanding } = useOnboardingStore();
  const [expandedLevel, setExpandedLevel] = useState<string | null>(null);
  const [startTime] = useState(Date.now());
  const [showQuiz, setShowQuiz] = useState(false);
  const [quizAnswers, setQuizAnswers] = useState<{ [key: string]: string }>({});
  const [quizCompleted, setQuizCompleted] = useState(false);
  const [showConnections, setShowConnections] = useState(false);

  // Track time spent on educational content
  useEffect(() => {
    return () => {
      const timeSpent = Math.round((Date.now() - startTime) / 1000);
      updatePAPTUnderstanding({
        timeSpentOnEducation: timeSpent,
      });
    };
  }, [startTime, updatePAPTUnderstanding]);

  const handleLevelClick = (levelId: string) => {
    setExpandedLevel(expandedLevel === levelId ? null : levelId);
  };

  const handleQuizAnswer = (itemText: string, answer: string) => {
    const newAnswers = { ...quizAnswers, [itemText]: answer };
    setQuizAnswers(newAnswers);
    
    // Check if all questions are answered correctly
    const allCorrect = QUIZ_ITEMS.every(item => 
      newAnswers[item.text] === item.answer
    );
    
    if (allCorrect && Object.keys(newAnswers).length === QUIZ_ITEMS.length) {
      setQuizCompleted(true);
    }
  };

  const isQuizItemCorrect = (itemText: string) => {
    const item = QUIZ_ITEMS.find(q => q.text === itemText);
    return item && quizAnswers[itemText] === item.answer;
  };

  const handleContinue = () => {
    updatePAPTUnderstanding({
      hasViewedExplanation: true,
      completedQuiz: quizCompleted,
    });
    nextStep();
  };

  const handleShowConnections = () => {
    setShowConnections(true);
    setTimeout(() => {
      setShowQuiz(true);
    }, 2000);
  };

  return (
    <OnboardingLayout showSkip onSkip={nextStep}>
      <div className="w-full max-w-6xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            The PAPT Framework: Your Life Operating System
          </h1>
          <p className="text-lg text-[#B8BCC8] max-w-3xl mx-auto">
            Aurum Life organizes your entire life using a proven hierarchy that brings clarity, 
            focus, and intentional progress to everything you do.
          </p>
        </motion.div>

        {/* PAPT Hierarchy Diagram */}
        <div className="mb-12">
          <motion.div 
            className="relative max-w-4xl mx-auto"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            {/* Connecting Lines */}
            <div className="absolute left-1/2 top-0 bottom-0 w-0.5 bg-gradient-to-b from-[#F4D03F] via-[#3B82F6] via-[#10B981] to-[#8B5CF6] transform -translate-x-px opacity-30" />
            
            {/* PAPT Levels */}
            <div className="space-y-6">
              {PAPT_LEVELS.map((level, index) => (
                <motion.div
                  key={level.id}
                  initial={{ opacity: 0, x: index % 2 === 0 ? -50 : 50 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.5 + index * 0.2 }}
                >
                  <Card 
                    className={`glassmorphism-card cursor-pointer transition-all duration-300 hover:scale-[1.02] ${
                      expandedLevel === level.id ? 'border-2 bg-[rgba(244,208,63,0.1)]' : ''
                    }`}
                    style={{ borderColor: expandedLevel === level.id ? level.color : undefined }}
                    onClick={() => handleLevelClick(level.id)}
                  >
                    <div className="p-6">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div 
                            className="p-3 rounded-xl"
                            style={{ backgroundColor: `${level.color}20` }}
                          >
                            <level.icon 
                              className="w-8 h-8" 
                              style={{ color: level.color }}
                            />
                          </div>
                          <div>
                            <h3 className="text-xl font-semibold text-white">{level.title}</h3>
                            <p className="text-[#B8BCC8] text-sm mt-1">{level.description}</p>
                          </div>
                        </div>
                        {expandedLevel === level.id ? (
                          <ChevronDown className="w-5 h-5 text-[#B8BCC8]" />
                        ) : (
                          <ChevronRight className="w-5 h-5 text-[#B8BCC8]" />
                        )}
                      </div>

                      <AnimatePresence>
                        {expandedLevel === level.id && (
                          <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                            transition={{ duration: 0.3 }}
                            className="mt-6 pt-6 border-t border-[rgba(244,208,63,0.1)]"
                          >
                            {/* Examples */}
                            <div className="mb-6">
                              {level.id === 'pillars' && (
                                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                                  {level.examples.map((example) => (
                                    <div 
                                      key={example.label}
                                      className="flex items-center space-x-2 p-3 rounded-lg bg-[rgba(244,208,63,0.05)] border border-[rgba(244,208,63,0.1)]"
                                    >
                                      <example.icon className="w-5 h-5 text-[#F4D03F]" />
                                      <span className="text-white text-sm">{example.label}</span>
                                    </div>
                                  ))}
                                </div>
                              )}
                              
                              {(level.id === 'areas' || level.id === 'projects' || level.id === 'tasks') && (
                                <div className="space-y-4">
                                  {level.examples.map((example, idx) => (
                                    <div key={idx} className="bg-[rgba(244,208,63,0.02)] p-4 rounded-lg border border-[rgba(244,208,63,0.1)]">
                                      <h4 className="text-[#F4D03F] font-medium mb-2">{example.parent}:</h4>
                                      <ul className="space-y-1">
                                        {example.items.map((item, itemIdx) => (
                                          <li key={itemIdx} className="text-white text-sm pl-3 border-l-2 border-[rgba(244,208,63,0.3)]">
                                            {item}
                                          </li>
                                        ))}
                                      </ul>
                                    </div>
                                  ))}
                                </div>
                              )}
                            </div>

                            {/* Explanation */}
                            <div className="bg-[rgba(244,208,63,0.05)] p-4 rounded-lg border border-[rgba(244,208,63,0.1)]">
                              <p className="text-[#B8BCC8] text-sm">{level.explanation}</p>
                            </div>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>
                  </Card>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Show Connections Button */}
        {!showConnections && (
          <div className="text-center mb-8">
            <Button
              onClick={handleShowConnections}
              className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F] px-8 py-3"
            >
              <Compass className="w-5 h-5 mr-2" />
              Show me how this works together
            </Button>
          </div>
        )}

        {/* Connection Animation */}
        <AnimatePresence>
          {showConnections && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="mb-12"
            >
              <div className="text-center bg-[rgba(244,208,63,0.1)] border border-[rgba(244,208,63,0.2)] rounded-xl p-8">
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.5 }}
                >
                  <h3 className="text-2xl font-bold text-[#F4D03F] mb-4">Perfect Alignment</h3>
                  <p className="text-white text-lg mb-6">
                    Every daily task connects to a project → which serves an area → which strengthens a pillar
                  </p>
                  <div className="flex items-center justify-center space-x-4 text-sm">
                    <span className="text-[#8B5CF6]">Daily Tasks</span>
                    <span className="text-[#B8BCC8]">→</span>
                    <span className="text-[#10B981]">Project Goals</span>
                    <span className="text-[#B8BCC8]">→</span>
                    <span className="text-[#3B82F6]">Life Areas</span>
                    <span className="text-[#B8BCC8]">→</span>
                    <span className="text-[#F4D03F]">Core Values</span>
                  </div>
                </motion.div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Understanding Quiz */}
        <AnimatePresence>
          {showQuiz && (
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-12"
            >
              <div className="bg-[rgba(244,208,63,0.05)] border border-[rgba(244,208,63,0.2)] rounded-xl p-8">
                <h3 className="text-2xl font-bold text-white mb-4 text-center">
                  Let's make sure you've got it!
                </h3>
                <p className="text-[#B8BCC8] text-center mb-8">
                  Match these examples to the right PAPT level:
                </p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {QUIZ_ITEMS.map((item) => (
                    <div key={item.text} className="space-y-3">
                      <div className="bg-[rgba(26,29,41,0.6)] p-4 rounded-lg border border-[rgba(244,208,63,0.1)]">
                        <p className="text-white font-medium mb-3">"{item.text}"</p>
                        <div className="grid grid-cols-2 gap-2">
                          {['Pillar', 'Area', 'Project', 'Task'].map((level) => (
                            <button
                              key={level}
                              onClick={() => handleQuizAnswer(item.text, level.toLowerCase())}
                              className={`p-2 rounded text-sm transition-all ${
                                quizAnswers[item.text] === level.toLowerCase()
                                  ? isQuizItemCorrect(item.text)
                                    ? 'bg-[#10B981] text-white'
                                    : 'bg-[#EF4444] text-white'
                                  : 'bg-[rgba(244,208,63,0.1)] text-[#B8BCC8] hover:bg-[rgba(244,208,63,0.2)]'
                              }`}
                            >
                              {level}
                            </button>
                          ))}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {quizCompleted && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="text-center mt-8 p-6 bg-[rgba(16,185,129,0.1)] border border-[rgba(16,185,129,0.3)] rounded-lg"
                  >
                    <CheckSquare className="w-12 h-12 text-[#10B981] mx-auto mb-4" />
                    <h4 className="text-xl font-bold text-[#10B981] mb-2">Perfect! You understand the framework</h4>
                    <p className="text-[#B8BCC8]">You're ready to build your personalized Life OS</p>
                  </motion.div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Continue Button */}
        <div className="text-center">
          <Button
            onClick={handleContinue}
            className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F] px-8 py-3 text-lg"
            disabled={showQuiz && !quizCompleted}
          >
            {showQuiz && !quizCompleted ? 'Complete the quiz above' : 'I understand, continue'}
          </Button>
          
          {!showQuiz && (
            <div className="mt-4">
              <button
                onClick={() => {
                  updatePAPTUnderstanding({
                    hasViewedExplanation: true,
                    skippedEducation: true,
                  });
                  nextStep();
                }}
                className="text-[#B8BCC8] text-sm hover:text-white underline"
              >
                Skip introduction
              </button>
            </div>
          )}
        </div>
      </div>
    </OnboardingLayout>
  );
}