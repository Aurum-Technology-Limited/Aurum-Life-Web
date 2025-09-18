import { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  Rocket, 
  GraduationCap, 
  Briefcase, 
  Heart, 
  Flower2, 
  Trophy, 
  ArrowRight, 
  ArrowLeft,
  CheckCircle,
  Lightbulb,
  User,
  Eye
} from 'lucide-react';
import { Button } from '../../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../ui/card';
import { Badge } from '../../ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '../../ui/dialog';
import { useOnboardingStore } from '../../../stores/onboardingStore';
import OnboardingLayout from '../OnboardingLayout';

interface Template {
  id: string;
  name: string;
  emoji: string;
  icon: React.ReactNode;
  description: string;
  detailedDescription: string;
  includes: string[];
  pillars: string[];
  color: string;
  matchScore: number;
}

interface Question {
  id: string;
  question: string;
  options: Array<{
    text: string;
    value: any;
    key: string;
  }>;
  type: 'single' | 'multiple';
}

export default function IntelligentTemplateSelection() {
  const { 
    userData, 
    selectedTemplate, 
    questionResponses, 
    setSelectedTemplate, 
    updateQuestionResponses, 
    nextStep, 
    previousStep 
  } = useOnboardingStore();
  
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [showRecommendation, setShowRecommendation] = useState(false);
  const [recommendedTemplate, setRecommendedTemplate] = useState<Template | null>(null);
  const [previewTemplate, setPreviewTemplate] = useState<Template | null>(null);
  const [showAllTemplates, setShowAllTemplates] = useState(false);

  const templates: Template[] = [
    {
      id: 'entrepreneur',
      name: 'Entrepreneur',
      emoji: '🚀',
      icon: <Rocket className="w-8 h-8" />,
      description: 'Built for innovators and business builders',
      detailedDescription: 'Perfect for entrepreneurs, startup founders, and business innovators who need to balance multiple ventures while maintaining personal growth.',
      includes: ['Business goal tracking', 'Network management', 'Innovation pipeline', 'Risk assessment tools'],
      pillars: ['Business Growth', 'Personal Development', 'Health & Energy', 'Relationships & Network'],
      color: 'from-orange-500 to-red-500',
      matchScore: 0
    },
    {
      id: 'student',
      name: 'Student',
      emoji: '🎓',
      icon: <GraduationCap className="w-8 h-8" />,
      description: 'Designed for academic excellence and growth',
      detailedDescription: 'Tailored for students at any level who want to excel academically while building skills for their future career.',
      includes: ['Study schedule optimization', 'Grade tracking', 'Career preparation', 'Social life balance'],
      pillars: ['Education & Learning', 'Career Preparation', 'Health & Wellness', 'Social Life'],
      color: 'from-blue-500 to-indigo-500',
      matchScore: 0
    },
    {
      id: 'professional',
      name: 'Professional',
      emoji: '💼',
      icon: <Briefcase className="w-8 h-8" />,
      description: 'Focused on career advancement and leadership',
      detailedDescription: 'Designed for working professionals who want to advance their careers while maintaining work-life balance.',
      includes: ['Career milestone tracking', 'Skill development plans', 'Leadership growth', 'Work-life integration'],
      pillars: ['Career Excellence', 'Leadership Development', 'Health & Wellness', 'Family & Relationships'],
      color: 'from-emerald-500 to-teal-500',
      matchScore: 0
    },
    {
      id: 'family',
      name: 'Family-Focused',
      emoji: '👨‍👩‍👧‍👦',
      icon: <Heart className="w-8 h-8" />,
      description: 'Centered around family life and relationships',
      detailedDescription: 'Perfect for parents and family-oriented individuals who prioritize relationships and household harmony.',
      includes: ['Family time optimization', 'Parenting goal tracking', 'Household management', 'Relationship building'],
      pillars: ['Family & Relationships', 'Personal Growth', 'Health & Wellness', 'Home & Environment'],
      color: 'from-pink-500 to-rose-500',
      matchScore: 0
    },
    {
      id: 'wellness',
      name: 'Wellness Seeker',
      emoji: '🧘',
      icon: <Flower2 className="w-8 h-8" />,
      description: 'Focused on holistic health and mindfulness',
      detailedDescription: 'Ideal for those prioritizing mental, physical, and spiritual wellness in their daily lives.',
      includes: ['Mindfulness tracking', 'Physical wellness goals', 'Emotional intelligence', 'Spiritual practices'],
      pillars: ['Mental Health', 'Physical Wellness', 'Spiritual Growth', 'Meaningful Relationships'],
      color: 'from-green-500 to-emerald-500',
      matchScore: 0
    },
    {
      id: 'achiever',
      name: 'High Achiever',
      emoji: '🏆',
      icon: <Trophy className="w-8 h-8" />,
      description: 'Built for ambitious goal pursuit and optimization',
      detailedDescription: 'Designed for high-performers who juggle multiple ambitious goals and want to optimize every aspect of their lives.',
      includes: ['Multi-goal optimization', 'Performance analytics', 'Habit stacking', 'Productivity systems'],
      pillars: ['Peak Performance', 'Success Metrics', 'Health Optimization', 'Continuous Growth'],
      color: 'from-yellow-500 to-orange-500',
      matchScore: 0
    }
  ];

  const questions: Question[] = [
    {
      id: 'education_status',
      question: 'Are you currently a student?',
      options: [
        { text: 'Yes, I\'m actively studying', value: true, key: 'isStudent' },
        { text: 'No, I\'m not currently a student', value: false, key: 'isStudent' }
      ],
      type: 'single'
    },
    {
      id: 'career_building',
      question: 'Are you actively building or advancing your career?',
      options: [
        { text: 'Yes, I\'m focused on career growth', value: true, key: 'isBuildingCareer' },
        { text: 'No, career isn\'t my main focus right now', value: false, key: 'isBuildingCareer' }
      ],
      type: 'single'
    },
    {
      id: 'entrepreneurship',
      question: 'Do you own a business or have entrepreneurial aspirations?',
      options: [
        { text: 'Yes, I\'m an entrepreneur or want to be one', value: true, key: 'isEntrepreneur' },
        { text: 'No, I prefer traditional employment', value: false, key: 'isEntrepreneur' }
      ],
      type: 'single'
    },
    {
      id: 'family_situation',
      question: 'Do you have a family or are family relationships a top priority?',
      options: [
        { text: 'Yes, family is very important to me', value: true, key: 'hasFamily' },
        { text: 'No, family isn\'t my main focus right now', value: false, key: 'hasFamily' }
      ],
      type: 'single'
    },
    {
      id: 'wellness_focus',
      question: 'Is health and wellness a primary focus in your life?',
      options: [
        { text: 'Yes, wellness is very important to me', value: true, key: 'prioritizesWellness' },
        { text: 'No, I don\'t prioritize wellness as much', value: false, key: 'prioritizesWellness' }
      ],
      type: 'single'
    },
    {
      id: 'achievement_level',
      question: 'Would you describe yourself as a high achiever with ambitious goals?',
      options: [
        { text: 'Yes, I\'m very ambitious and goal-oriented', value: true, key: 'isHighAchiever' },
        { text: 'No, I prefer a more balanced approach', value: false, key: 'isHighAchiever' }
      ],
      type: 'single'
    }
  ];

  const handleAnswerQuestion = (option: any) => {
    // Update store with the new response
    updateQuestionResponses({ [option.key]: option.value });
    
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    } else {
      // All questions answered, calculate recommendation
      calculateRecommendation({ ...questionResponses, [option.key]: option.value });
    }
  };

  const calculateRecommendation = (responses = questionResponses) => {
    const templatesWithScores = templates.map(template => ({
      ...template,
      matchScore: calculateMatchScore(template.id, responses)
    }));

    const bestMatch = templatesWithScores.reduce((best, current) => 
      current.matchScore > best.matchScore ? current : best
    );

    setRecommendedTemplate(bestMatch);
    setShowRecommendation(true);
  };

  const calculateMatchScore = (templateId: string, responses: any): number => {
    let score = 10; // Base score to avoid 0 scores

    switch (templateId) {
      case 'student':
        if (responses.isStudent === true) score += 50;
        if (responses.isBuildingCareer === true) score += 20;
        if (responses.hasFamily === false) score += 15;
        if (responses.isEntrepreneur === false) score += 10;
        break;

      case 'entrepreneur':
        if (responses.isEntrepreneur === true) score += 50;
        if (responses.isHighAchiever === true) score += 30;
        if (responses.isBuildingCareer === true) score += 15;
        if (responses.isStudent === false) score += 10;
        break;

      case 'professional':
        if (responses.isBuildingCareer === true) score += 40;
        if (responses.isStudent === false) score += 25;
        if (responses.isEntrepreneur === false) score += 20;
        if (responses.isHighAchiever === true) score += 15;
        break;

      case 'family':
        if (responses.hasFamily === true) score += 50;
        if (responses.isStudent === false) score += 20;
        if (responses.isHighAchiever === false) score += 15;
        if (responses.prioritizesWellness === true) score += 10;
        break;

      case 'wellness':
        if (responses.prioritizesWellness === true) score += 50;
        if (responses.isHighAchiever === false) score += 20;
        if (responses.isEntrepreneur === false) score += 15;
        if (responses.hasFamily === true) score += 10;
        break;

      case 'achiever':
        if (responses.isHighAchiever === true) score += 50;
        if (responses.isEntrepreneur === true) score += 25;
        if (responses.isBuildingCareer === true) score += 20;
        if (responses.prioritizesWellness === false) score += 10;
        break;
    }

    return score;
  };

  const handleAcceptRecommendation = () => {
    if (recommendedTemplate) {
      const templateData = {
        id: recommendedTemplate.id,
        name: recommendedTemplate.name,
        description: recommendedTemplate.description,
        pillars: recommendedTemplate.pillars
      };
      setSelectedTemplate(templateData);
      nextStep();
    }
  };

  const handleSeeAllTemplates = () => {
    setShowAllTemplates(true);
  };

  const handleSelectDifferentTemplate = (template: Template) => {
    const templateData = {
      id: template.id,
      name: template.name,
      description: template.description,
      pillars: template.pillars
    };
    setSelectedTemplate(templateData);
    setShowAllTemplates(false);
    nextStep();
  };

  const currentQuestion = questions[currentQuestionIndex];

  // Safety check
  if (!currentQuestion && !showRecommendation) {
    return (
      <OnboardingLayout>
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h2 className="text-4xl font-bold text-white mb-4">Loading...</h2>
          <p className="text-xl text-[#B8BCC8]">Preparing your questions...</p>
        </div>
      </OnboardingLayout>
    );
  }

  if (showRecommendation && recommendedTemplate) {
    return (
      <OnboardingLayout>
        <div className="max-w-4xl mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center mb-8"
          >
            <div className="flex items-center justify-center mb-4">
              <Lightbulb className="w-8 h-8 text-[#F4D03F] mr-3" />
              <h2 className="text-4xl font-bold text-white">Perfect Match Found!</h2>
            </div>
            <p className="text-xl text-[#B8BCC8] max-w-2xl mx-auto">
              Based on your answers, {userData.firstName}, we recommend the <strong>{recommendedTemplate.name}</strong> template for your Life OS.
            </p>
          </motion.div>

          {/* Recommended Template Card */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="mb-8"
          >
            <Card className="glassmorphism-card border-2 border-[#F4D03F] shadow-lg shadow-[#F4D03F]/20">
              <CardHeader className="text-center">
                <div className={`w-20 h-20 mx-auto mb-4 rounded-2xl bg-gradient-to-br ${recommendedTemplate.color} p-5 text-white`}>
                  {recommendedTemplate.icon}
                </div>
                
                <div className="absolute top-4 right-4 flex items-center space-x-2">
                  <Badge className="bg-[#F4D03F] text-[#0B0D14] font-semibold">
                    {Math.round(recommendedTemplate.matchScore)}% Match
                  </Badge>
                  <div className="w-8 h-8 bg-[#F4D03F] rounded-full flex items-center justify-center">
                    <CheckCircle className="w-5 h-5 text-[#0B0D14]" />
                  </div>
                </div>

                <CardTitle className="text-white text-2xl mb-2">{recommendedTemplate.name}</CardTitle>
                <CardDescription className="text-[#B8BCC8] text-lg">
                  {recommendedTemplate.detailedDescription}
                </CardDescription>
              </CardHeader>
              
              <CardContent className="space-y-6">
                {/* What's Included */}
                <div>
                  <h4 className="text-[#F4D03F] font-semibold mb-3">What's Included:</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {recommendedTemplate.includes.map((item, idx) => (
                      <div key={idx} className="flex items-center text-[#B8BCC8]">
                        <CheckCircle className="w-4 h-4 text-[#F4D03F] mr-2" />
                        {item}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Life Pillars */}
                <div>
                  <h4 className="text-[#F4D03F] font-semibold mb-3">Your Life Pillars:</h4>
                  <div className="flex flex-wrap gap-2">
                    {recommendedTemplate.pillars.map((pillar) => (
                      <Badge
                        key={pillar}
                        className="bg-[rgba(244,208,63,0.2)] text-[#F4D03F] border-[rgba(244,208,63,0.3)]"
                      >
                        {pillar}
                      </Badge>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Action Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="flex flex-col sm:flex-row gap-4 justify-center"
          >
            <Button
              onClick={handleAcceptRecommendation}
              size="lg"
              className="px-8 py-4 text-lg font-semibold bg-[#F4D03F] hover:bg-[#F7DC6F] text-[#0B0D14] group"
            >
              Perfect! Let's Use This Template
              <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
            </Button>
            
            <Button
              onClick={handleSeeAllTemplates}
              variant="outline"
              size="lg"
              className="px-8 py-4 text-lg border-[rgba(244,208,63,0.3)] text-[#F4D03F] hover:bg-[rgba(244,208,63,0.1)]"
            >
              <Eye className="w-5 h-5 mr-2" />
              See All Templates
            </Button>
          </motion.div>

          {/* All Templates Modal */}
          <Dialog open={showAllTemplates} onOpenChange={setShowAllTemplates}>
            <DialogContent className="max-w-6xl glassmorphism-card border-0 max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle className="text-white text-2xl">All Available Templates</DialogTitle>
                <DialogDescription className="text-[#B8BCC8] text-lg">
                  Choose a different template if none of these better suit your needs.
                </DialogDescription>
              </DialogHeader>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {templates.map((template) => (
                  <Card 
                    key={template.id}
                    className="glassmorphism-panel border-[rgba(244,208,63,0.2)] hover:border-[rgba(244,208,63,0.4)] cursor-pointer transition-all h-full"
                    onClick={() => handleSelectDifferentTemplate(template)}
                  >
                    <CardHeader className="text-center pb-4">
                      <div className={`w-12 h-12 mx-auto mb-3 rounded-xl bg-gradient-to-br ${template.color} p-3 text-white`}>
                        {template.icon}
                      </div>
                      <CardTitle className="text-white text-lg">{template.name}</CardTitle>
                      <CardDescription className="text-[#B8BCC8] text-sm">
                        {template.description}
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="pt-2">
                      <Button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleSelectDifferentTemplate(template);
                        }}
                        className="w-full bg-[rgba(244,208,63,0.1)] text-[#F4D03F] hover:bg-[rgba(244,208,63,0.2)] border border-[rgba(244,208,63,0.3)] px-4 py-2"
                      >
                        Select This Template
                      </Button>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </OnboardingLayout>
    );
  }

  return (
    <OnboardingLayout>
      <div className="max-w-4xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-8"
        >
          <div className="flex items-center justify-center mb-4">
            <User className="w-8 h-8 text-[#F4D03F] mr-3" />
            <h2 className="text-4xl font-bold text-white">Let's Personalize Your Experience</h2>
          </div>
          <p className="text-xl text-[#B8BCC8] max-w-2xl mx-auto">
            Hi {userData.firstName}! I'll ask you a few quick questions to recommend the perfect template for your Life OS.
          </p>
        </motion.div>

        {/* Progress Indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mb-8"
        >
          <div className="flex items-center justify-center mb-4">
            <span className="text-[#F4D03F] font-semibold">
              Question {currentQuestionIndex + 1} of {questions.length}
            </span>
          </div>
          <div className="w-full bg-[#1A1D29] rounded-full h-2">
            <div 
              className="bg-[#F4D03F] h-2 rounded-full transition-all duration-300"
              style={{ width: `${((currentQuestionIndex + 1) / questions.length) * 100}%` }}
            />
          </div>
        </motion.div>

        {/* Current Question */}
        {currentQuestion && (
          <Card className="glassmorphism-card border-[rgba(244,208,63,0.2)] mb-8">
            <CardHeader className="text-center">
              <CardTitle className="text-white text-2xl mb-4">
                {currentQuestion.question}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {currentQuestion.options.map((option, index) => (
                  <Button
                    key={`${currentQuestionIndex}-${index}`}
                    onClick={() => handleAnswerQuestion(option)}
                    variant="outline"
                    size="lg"
                    className="w-full p-6 text-left justify-start border-[rgba(244,208,63,0.2)] text-[#B8BCC8] hover:border-[#F4D03F] hover:bg-[rgba(244,208,63,0.1)] hover:text-white transition-all"
                  >
                    <div className="flex items-center">
                      <div className="w-4 h-4 border-2 border-[#F4D03F] rounded-full mr-4" />
                      <span className="text-lg">{option.text}</span>
                    </div>
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Navigation */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="flex justify-between"
        >
          <Button
            onClick={previousStep}
            variant="outline"
            size="lg"
            className="border-[rgba(244,208,63,0.2)] text-[#F4D03F] hover:bg-[rgba(244,208,63,0.1)]"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            Back
          </Button>

          {currentQuestionIndex > 0 && (
            <Button
              onClick={() => setCurrentQuestionIndex(currentQuestionIndex - 1)}
              variant="outline"
              size="lg"
              className="border-[rgba(244,208,63,0.2)] text-[#F4D03F] hover:bg-[rgba(244,208,63,0.1)]"
            >
              Previous Question
            </Button>
          )}
        </motion.div>
      </div>
    </OnboardingLayout>
  );
}