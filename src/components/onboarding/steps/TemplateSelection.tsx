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
  Check, 
  Eye,
  Plus
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
}

export default function TemplateSelection() {
  const { selectedTemplate, setSelectedTemplate, nextStep } = useOnboardingStore();
  const [previewTemplate, setPreviewTemplate] = useState<Template | null>(null);

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
      color: 'from-orange-500 to-red-500'
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
      color: 'from-blue-500 to-indigo-500'
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
      color: 'from-emerald-500 to-teal-500'
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
      color: 'from-pink-500 to-rose-500'
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
      color: 'from-green-500 to-emerald-500'
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
      color: 'from-yellow-500 to-orange-500'
    }
  ];

  const handleSelectTemplate = (template: Template) => {
    setSelectedTemplate(template);
  };

  const handleContinue = () => {
    if (selectedTemplate) {
      nextStep();
    }
  };

  const handlePreview = (template: Template) => {
    setPreviewTemplate(template);
  };

  const handleCreateCustom = () => {
    // Set a custom template
    setSelectedTemplate({
      id: 'custom',
      name: 'Custom Template',
      description: 'Build your own personalized template',
      pillars: []
    });
    nextStep();
  };

  return (
    <OnboardingLayout>
      <div className="max-w-6xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h2 className="text-4xl font-bold text-white mb-4">Choose Your Starting Template</h2>
          <p className="text-xl text-[#B8BCC8] max-w-2xl mx-auto">
            We'll customize your experience based on your lifestyle. Don't worry - you can always modify this later.
          </p>
        </motion.div>

        {/* Template Grid */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8"
        >
          {templates.map((template, index) => (
            <motion.div
              key={template.id}
              initial={{ opacity: 0, y: 20, scale: 0.9 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ duration: 0.5, delay: 0.3 + index * 0.1 }}
            >
              <Card 
                className={`glassmorphism-card border-2 transition-all duration-300 cursor-pointer h-full ${
                  selectedTemplate?.id === template.id
                    ? 'border-[#F4D03F] shadow-lg shadow-[#F4D03F]/20 scale-105'
                    : 'border-[rgba(244,208,63,0.2)] hover:border-[rgba(244,208,63,0.4)] hover:shadow-md'
                }`}
                onClick={() => handleSelectTemplate(template)}
              >
                <CardHeader className="text-center">
                  {/* Template Icon with Background */}
                  <div className={`w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br ${template.color} p-4 text-white`}>
                    {template.icon}
                  </div>
                  
                  {/* Selection Check */}
                  <AnimatePresence>
                    {selectedTemplate?.id === template.id && (
                      <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        exit={{ scale: 0 }}
                        className="absolute top-4 right-4 w-8 h-8 bg-[#F4D03F] rounded-full flex items-center justify-center"
                      >
                        <Check className="w-5 h-5 text-[#0B0D14]" />
                      </motion.div>
                    )}
                  </AnimatePresence>

                  <CardTitle className="text-white text-xl mb-2">{template.name}</CardTitle>
                  <CardDescription className="text-[#B8BCC8]">
                    {template.description}
                  </CardDescription>
                </CardHeader>
                
                <CardContent className="space-y-4">
                  {/* What's Included Preview */}
                  <div>
                    <h4 className="text-[#F4D03F] font-medium mb-2">What's Included:</h4>
                    <ul className="text-[#B8BCC8] text-sm space-y-1">
                      {template.includes.slice(0, 3).map((item, idx) => (
                        <li key={idx} className="flex items-center">
                          <div className="w-1.5 h-1.5 bg-[#F4D03F] rounded-full mr-2" />
                          {item}
                        </li>
                      ))}
                      {template.includes.length > 3 && (
                        <li className="text-[#F4D03F] text-xs">
                          +{template.includes.length - 3} more features
                        </li>
                      )}
                    </ul>
                  </div>

                  {/* Pillars Preview */}
                  <div>
                    <h4 className="text-[#F4D03F] font-medium mb-2">Life Pillars:</h4>
                    <div className="flex flex-wrap gap-1">
                      {template.pillars.map((pillar) => (
                        <Badge
                          key={pillar}
                          className="bg-[rgba(244,208,63,0.1)] text-[#F4D03F] border-[rgba(244,208,63,0.3)] text-xs"
                        >
                          {pillar}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex space-x-2 pt-2">
                    <Button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleSelectTemplate(template);
                      }}
                      className={`flex-1 ${
                        selectedTemplate?.id === template.id
                          ? 'bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]'
                          : 'bg-[rgba(244,208,63,0.1)] text-[#F4D03F] hover:bg-[rgba(244,208,63,0.2)] border border-[rgba(244,208,63,0.3)]'
                      }`}
                    >
                      {selectedTemplate?.id === template.id ? 'Selected' : 'Select'}
                    </Button>
                    
                    <Button
                      onClick={(e) => {
                        e.stopPropagation();
                        handlePreview(template);
                      }}
                      variant="outline"
                      size="sm"
                      className="border-[rgba(244,208,63,0.2)] text-[#F4D03F] hover:bg-[rgba(244,208,63,0.05)]"
                    >
                      <Eye className="w-4 h-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </motion.div>

        {/* Create Custom Option */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.8 }}
          className="text-center mb-8"
        >
          <Button
            onClick={handleCreateCustom}
            variant="outline"
            size="lg"
            className="border-[rgba(244,208,63,0.3)] text-[#F4D03F] hover:bg-[rgba(244,208,63,0.1)] px-8 py-4"
          >
            <Plus className="w-5 h-5 mr-2" />
            Create Custom Template
          </Button>
        </motion.div>

        {/* Continue Button */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 1.0 }}
          className="text-center"
        >
          <Button
            onClick={handleContinue}
            disabled={!selectedTemplate}
            size="lg"
            className={`px-8 py-4 text-lg font-semibold transition-all duration-200 group ${
              selectedTemplate
                ? 'bg-[#F4D03F] hover:bg-[#F7DC6F] text-[#0B0D14]'
                : 'bg-[#1A1D29] text-[#B8BCC8] cursor-not-allowed'
            }`}
          >
            Continue with {selectedTemplate?.name || 'Selection'}
            <ArrowRight className={`w-5 h-5 ml-2 transition-transform ${selectedTemplate ? 'group-hover:translate-x-1' : ''}`} />
          </Button>
        </motion.div>

        {/* Preview Modal */}
        <Dialog open={!!previewTemplate} onOpenChange={() => setPreviewTemplate(null)}>
          <DialogContent className="max-w-2xl glassmorphism-card border-0">
            {previewTemplate && (
              <>
                <DialogHeader>
                  <DialogTitle className="text-white flex items-center space-x-3">
                    <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${previewTemplate.color} p-3 text-white`}>
                      {previewTemplate.icon}
                    </div>
                    <span>{previewTemplate.name} Template</span>
                  </DialogTitle>
                  <DialogDescription className="text-[#B8BCC8] text-lg">
                    {previewTemplate.detailedDescription}
                  </DialogDescription>
                </DialogHeader>
                
                <div className="space-y-6">
                  {/* Complete Features List */}
                  <div>
                    <h4 className="text-[#F4D03F] font-semibold mb-3">Complete Feature Set:</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {previewTemplate.includes.map((feature, idx) => (
                        <div key={idx} className="flex items-center text-[#B8BCC8]">
                          <Check className="w-4 h-4 text-[#F4D03F] mr-2" />
                          {feature}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Life Pillars */}
                  <div>
                    <h4 className="text-[#F4D03F] font-semibold mb-3">Your Life Pillars:</h4>
                    <div className="grid grid-cols-2 gap-3">
                      {previewTemplate.pillars.map((pillar, idx) => (
                        <div key={idx} className="glassmorphism-subtle p-3 rounded-lg">
                          <div className="text-white font-medium">{pillar}</div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex space-x-4 pt-4">
                    <Button
                      onClick={() => {
                        handleSelectTemplate(previewTemplate);
                        setPreviewTemplate(null);
                      }}
                      className="flex-1 bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
                    >
                      Select This Template
                    </Button>
                    <Button
                      onClick={() => setPreviewTemplate(null)}
                      variant="outline"
                      className="border-[rgba(244,208,63,0.2)] text-[#F4D03F]"
                    >
                      Close Preview
                    </Button>
                  </div>
                </div>
              </>
            )}
          </DialogContent>
        </Dialog>
      </div>
    </OnboardingLayout>
  );
}