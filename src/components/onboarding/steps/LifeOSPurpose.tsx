import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  Compass,
  Scale,
  Rocket,
  Brain,
  TrendingUp,
  CheckCircle2,
  Quote,
  Star,
  Award,
  Users,
  ChevronLeft,
  ChevronRight,
  Play,
  Pause
} from 'lucide-react';
import { Button } from '../../ui/button';
import { Card } from '../../ui/card';
import { Badge } from '../../ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '../../ui/avatar';
import OnboardingLayout from '../OnboardingLayout';
import { useOnboardingStore } from '../../../stores/onboardingStore';

const BENEFITS = [
  {
    id: 'clarity',
    icon: Compass,
    title: 'Never wonder what to focus on',
    description: 'See exactly how your daily actions connect to your biggest life goals',
    stat: 'Users report 73% less decision fatigue',
    color: '#F4D03F'
  },
  {
    id: 'balance',
    icon: Scale,
    title: 'Balance all areas of life automatically',
    description: 'Built-in system ensures no pillar gets neglected while you focus on priorities',
    stat: '87% achieve better work-life integration',
    color: '#3B82F6'
  },
  {
    id: 'progress',
    icon: Rocket,
    title: 'Make meaningful progress faster',
    description: 'Organized approach eliminates wasted effort and maximizes impact',
    stat: '3x faster goal achievement on average',
    color: '#10B981'
  },
  {
    id: 'control',
    icon: Brain,
    title: 'Feel in control of your life',
    description: 'Transform chaos into calm with clear structure and automated prioritization',
    stat: '94% report feeling more in control',
    color: '#8B5CF6'
  }
];

const BEFORE_AFTER = {
  before: [
    'Scattered to-do lists everywhere',
    'Unclear priorities and direction',
    'Neglecting important life areas',
    'Feeling overwhelmed and reactive',
    'Goals that never get achieved',
    'Work-life balance struggles'
  ],
  after: [
    'Single source of truth for everything',
    'Crystal clear daily priorities',
    'Balanced attention across all pillars',
    'Calm, intentional decision-making',
    'Consistent progress on meaningful goals',
    'Harmonious life integration'
  ]
};

const TESTIMONIALS = [
  {
    id: 1,
    name: 'Sarah Chen',
    role: 'Tech Founder',
    duration: '8 months',
    avatar: '/avatars/sarah.jpg',
    quote: 'I went from managing 47 different apps and lists to one clear system. My productivity doubled, but more importantly, I\'m finally present with my family.',
    badges: ['🎯 Goals Master', '⚖️ Life Balance Pro']
  },
  {
    id: 2,
    name: 'Marcus Johnson',
    role: 'MBA Student',
    duration: '6 months',
    avatar: '/avatars/marcus.jpg',
    quote: 'The PAPT framework helped me organize not just my studies, but my entire college experience. I\'m getting better grades while having more fun.',
    badges: ['🎓 Academic Excellence', '🌟 Well-Rounded Life']
  },
  {
    id: 3,
    name: 'Lisa Martinez',
    role: 'Marketing Director & Mom of 2',
    duration: '1 year',
    avatar: '/avatars/lisa.jpg',
    quote: 'Finally, a system that works with my chaotic life instead of against it. I\'m advancing my career while being the parent I want to be.',
    badges: ['👨‍👩‍👧‍👦 Family Focus', '💼 Career Growth']
  }
];

export default function LifeOSPurpose() {
  const { nextStep } = useOnboardingStore();
  const [currentTestimonial, setCurrentTestimonial] = useState(0);
  const [isAutoPlaying, setIsAutoPlaying] = useState(true);

  // Auto-rotate testimonials
  useEffect(() => {
    if (!isAutoPlaying) return;
    
    const interval = setInterval(() => {
      setCurrentTestimonial(prev => (prev + 1) % TESTIMONIALS.length);
    }, 5000);

    return () => clearInterval(interval);
  }, [isAutoPlaying]);

  const nextTestimonial = () => {
    setCurrentTestimonial(prev => (prev + 1) % TESTIMONIALS.length);
    setIsAutoPlaying(false);
  };

  const previousTestimonial = () => {
    setCurrentTestimonial(prev => (prev - 1 + TESTIMONIALS.length) % TESTIMONIALS.length);
    setIsAutoPlaying(false);
  };

  const toggleAutoPlay = () => {
    setIsAutoPlaying(!isAutoPlaying);
  };

  const handleContinue = () => {
    nextStep();
  };

  return (
    <OnboardingLayout>
      <div className="w-full max-w-7xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Why the Life OS Approach Changes Everything
          </h1>
          <p className="text-lg text-[#B8BCC8] max-w-3xl mx-auto">
            Move from scattered productivity to intentional living. See how the PAPT framework 
            creates alignment, reduces overwhelm, and accelerates progress.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-16">
          {/* Benefits Section */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <h2 className="text-2xl font-bold text-white mb-8 text-center lg:text-left">
              Core Benefits
            </h2>
            <div className="space-y-6">
              {BENEFITS.map((benefit, index) => (
                <motion.div
                  key={benefit.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 + index * 0.1 }}
                >
                  <Card className="glassmorphism-card hover:scale-[1.02] transition-all duration-300">
                    <div className="p-6">
                      <div className="flex items-start space-x-4">
                        <div 
                          className="p-3 rounded-xl flex-shrink-0"
                          style={{ backgroundColor: `${benefit.color}20` }}
                        >
                          <benefit.icon 
                            className="w-6 h-6" 
                            style={{ color: benefit.color }}
                          />
                        </div>
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold text-white mb-2">
                            {benefit.title}
                          </h3>
                          <p className="text-[#B8BCC8] text-sm mb-3">
                            {benefit.description}
                          </p>
                          <div className="bg-[rgba(244,208,63,0.1)] border border-[rgba(244,208,63,0.2)] rounded-lg p-3">
                            <p className="text-[#F4D03F] text-sm font-medium">
                              {benefit.stat}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </Card>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Transformation Section */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
          >
            <h2 className="text-2xl font-bold text-white mb-8 text-center lg:text-left">
              Your Transformation
            </h2>
            
            <div className="space-y-8">
              {/* Before Section */}
              <div className="relative">
                <div className="absolute left-0 top-0 bottom-0 w-1 bg-[#EF4444] rounded-full"></div>
                <div className="pl-6">
                  <h3 className="text-lg font-semibold text-[#EF4444] mb-4 flex items-center">
                    😰 Before Aurum Life
                  </h3>
                  <ul className="space-y-3">
                    {BEFORE_AFTER.before.map((item, index) => (
                      <motion.li
                        key={index}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.5 + index * 0.1 }}
                        className="text-[#B8BCC8] text-sm flex items-center opacity-70"
                      >
                        <span className="text-[#EF4444] mr-3">•</span>
                        {item}
                      </motion.li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Transformation Arrow */}
              <div className="flex justify-center">
                <motion.div
                  initial={{ opacity: 0, scale: 0 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 1.2 }}
                  className="bg-[#F4D03F] rounded-full p-3"
                >
                  <TrendingUp className="w-6 h-6 text-[#0B0D14]" />
                </motion.div>
              </div>

              {/* After Section */}
              <div className="relative">
                <div className="absolute left-0 top-0 bottom-0 w-1 bg-[#F4D03F] rounded-full"></div>
                <div className="pl-6">
                  <h3 className="text-lg font-semibold text-[#F4D03F] mb-4 flex items-center">
                    ✨ After Aurum Life
                  </h3>
                  <ul className="space-y-3">
                    {BEFORE_AFTER.after.map((item, index) => (
                      <motion.li
                        key={index}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 1.3 + index * 0.1 }}
                        className="text-white text-sm flex items-center"
                      >
                        <CheckCircle2 className="w-4 h-4 text-[#10B981] mr-3 flex-shrink-0" />
                        {item}
                      </motion.li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Success Stories Section */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="mb-16"
        >
          <h2 className="text-2xl font-bold text-white mb-8 text-center">
            Success Stories
          </h2>
          
          <div className="relative max-w-4xl mx-auto">
            <Card className="glassmorphism-card">
              <div className="p-8">
                <AnimatePresence mode="wait">
                  <motion.div
                    key={currentTestimonial}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.3 }}
                  >
                    <div className="flex items-start space-x-6">
                      <Avatar className="w-16 h-16 flex-shrink-0">
                        <AvatarImage src={TESTIMONIALS[currentTestimonial].avatar} />
                        <AvatarFallback className="bg-[#F4D03F] text-[#0B0D14] text-lg font-semibold">
                          {TESTIMONIALS[currentTestimonial].name.split(' ').map(n => n[0]).join('')}
                        </AvatarFallback>
                      </Avatar>
                      
                      <div className="flex-1">
                        <Quote className="w-8 h-8 text-[#F4D03F] opacity-50 mb-4" />
                        
                        <blockquote className="text-white text-lg mb-6 leading-relaxed">
                          "{TESTIMONIALS[currentTestimonial].quote}"
                        </blockquote>
                        
                        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                          <div>
                            <div className="text-[#F4D03F] font-semibold">
                              {TESTIMONIALS[currentTestimonial].name}
                            </div>
                            <div className="text-[#B8BCC8] text-sm">
                              {TESTIMONIALS[currentTestimonial].role} • User for {TESTIMONIALS[currentTestimonial].duration}
                            </div>
                          </div>
                          
                          <div className="flex flex-wrap gap-2">
                            {TESTIMONIALS[currentTestimonial].badges.map((badge, index) => (
                              <Badge 
                                key={index}
                                variant="outline" 
                                className="border-[rgba(244,208,63,0.3)] text-[#F4D03F] text-xs"
                              >
                                {badge}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                </AnimatePresence>
                
                {/* Testimonial Controls */}
                <div className="flex items-center justify-between mt-8 pt-6 border-t border-[rgba(244,208,63,0.1)]">
                  <div className="flex items-center space-x-4">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={previousTestimonial}
                      className="text-[#B8BCC8] hover:text-[#F4D03F]"
                    >
                      <ChevronLeft className="w-4 h-4" />
                    </Button>
                    
                    <div className="flex space-x-2">
                      {TESTIMONIALS.map((_, index) => (
                        <button
                          key={index}
                          onClick={() => {
                            setCurrentTestimonial(index);
                            setIsAutoPlaying(false);
                          }}
                          className={`w-2 h-2 rounded-full transition-all ${
                            index === currentTestimonial 
                              ? 'bg-[#F4D03F] w-6' 
                              : 'bg-[rgba(244,208,63,0.3)]'
                          }`}
                        />
                      ))}
                    </div>
                    
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={nextTestimonial}
                      className="text-[#B8BCC8] hover:text-[#F4D03F]"
                    >
                      <ChevronRight className="w-4 h-4" />
                    </Button>
                  </div>
                  
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={toggleAutoPlay}
                    className="text-[#B8BCC8] hover:text-[#F4D03F]"
                  >
                    {isAutoPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                  </Button>
                </div>
              </div>
            </Card>
            
            <div className="text-center mt-4">
              <p className="text-[#6B7280] text-xs">Results may vary based on individual effort and commitment</p>
            </div>
          </div>
        </motion.div>

        {/* Transition to Next Step */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="text-center"
        >
          <div className="bg-[rgba(244,208,63,0.1)] border border-[rgba(244,208,63,0.2)] rounded-xl p-8 mb-8">
            <h3 className="text-2xl font-bold text-[#F4D03F] mb-4">
              Now Let's Personalize Your Life OS
            </h3>
            <p className="text-[#B8BCC8] mb-6">
              You understand how the PAPT framework works. Now we'll customize it for your 
              unique life situation, goals, and preferences.
            </p>
            
            <div className="flex flex-wrap justify-center gap-4 text-sm text-[#B8BCC8]">
              <div className="flex items-center space-x-2">
                <span className="w-2 h-2 bg-[#F4D03F] rounded-full"></span>
                <span>📝 Tell us about yourself</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="w-2 h-2 bg-[#3B82F6] rounded-full"></span>
                <span>🎯 Choose your starting template</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="w-2 h-2 bg-[#10B981] rounded-full"></span>
                <span>🏛️ Set up your personal pillars</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="w-2 h-2 bg-[#8B5CF6] rounded-full"></span>
                <span>🤖 Configure your AI coach</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="w-2 h-2 bg-[#F59E0B] rounded-full"></span>
                <span>✨ Launch your Life OS</span>
              </div>
            </div>
          </div>
          
          <Button
            onClick={handleContinue}
            className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F] px-8 py-3 text-lg"
          >
            Ready to get started?
          </Button>
          
          <div className="mt-4">
            <button
              onClick={handleContinue}
              className="text-[#B8BCC8] text-sm hover:text-white underline"
            >
              I need to see more
            </button>
          </div>
        </motion.div>
      </div>
    </OnboardingLayout>
  );
}