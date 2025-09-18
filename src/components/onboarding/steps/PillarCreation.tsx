import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  Plus, 
  GripVertical, 
  Edit3, 
  Trash2, 
  ArrowRight, 
  Sparkles,
  Target,
  Heart,
  Brain,
  Briefcase,
  Home,
  Dumbbell
} from 'lucide-react';
import { Button } from '../../ui/button';
import { Input } from '../../ui/input';
import { Textarea } from '../../ui/textarea';
import { Label } from '../../ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '../../ui/card';
import { Badge } from '../../ui/badge';
import { useOnboardingStore } from '../../../stores/onboardingStore';
import OnboardingLayout from '../OnboardingLayout';

interface Pillar {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
}

const suggestedPillars = [
  { icon: '🎯', name: 'Career Growth', description: 'Professional development and success', color: 'from-blue-500 to-indigo-500' },
  { icon: '💪', name: 'Health & Fitness', description: 'Physical wellness and energy', color: 'from-green-500 to-emerald-500' },
  { icon: '🧠', name: 'Learning & Growth', description: 'Knowledge and skill development', color: 'from-purple-500 to-violet-500' },
  { icon: '❤️', name: 'Relationships', description: 'Family, friends, and connections', color: 'from-pink-500 to-rose-500' },
  { icon: '💰', name: 'Financial Freedom', description: 'Money management and wealth building', color: 'from-yellow-500 to-orange-500' },
  { icon: '🏠', name: 'Home & Environment', description: 'Living space and surroundings', color: 'from-brown-500 to-amber-500' },
  { icon: '🧘', name: 'Spiritual Wellness', description: 'Inner peace and meaning', color: 'from-teal-500 to-cyan-500' },
  { icon: '🎨', name: 'Creativity', description: 'Creative expression and hobbies', color: 'from-indigo-500 to-purple-500' }
];

export default function PillarCreation() {
  const { selectedTemplate, customPillars, updatePillars, nextStep } = useOnboardingStore();
  const [pillars, setPillars] = useState<Pillar[]>([]);
  const [editingPillar, setEditingPillar] = useState<string | null>(null);
  const [newPillar, setNewPillar] = useState({ name: '', description: '', icon: '⭐', color: 'from-gold-500 to-yellow-500' });

  useEffect(() => {
    // Initialize pillars from template or existing custom pillars
    if (customPillars.length > 0) {
      setPillars(customPillars);
    } else if (selectedTemplate && selectedTemplate.pillars) {
      const templatePillars: Pillar[] = selectedTemplate.pillars.map((pillarName, index) => {
        const suggested = suggestedPillars.find(s => s.name.toLowerCase().includes(pillarName.toLowerCase().split(' ')[0]));
        return {
          id: `pillar-${index}`,
          name: pillarName,
          description: suggested?.description || `Focus on ${pillarName.toLowerCase()}`,
          icon: suggested?.icon || '⭐',
          color: suggested?.color || 'from-gold-500 to-yellow-500'
        };
      });
      setPillars(templatePillars);
    }
  }, [customPillars, selectedTemplate]);

  const addPillar = (pillarData?: { name: string; description: string; icon: string; color: string }) => {
    const data = pillarData || newPillar;
    if (data.name.trim() && pillars.length < 6) {
      const pillar: Pillar = {
        id: `pillar-${Date.now()}`,
        ...data
      };
      setPillars([...pillars, pillar]);
      setNewPillar({ name: '', description: '', icon: '⭐', color: 'from-gold-500 to-yellow-500' });
    }
  };

  const updatePillar = (id: string, updates: Partial<Pillar>) => {
    setPillars(pillars.map(p => p.id === id ? { ...p, ...updates } : p));
    setEditingPillar(null);
  };

  const removePillar = (id: string) => {
    setPillars(pillars.filter(p => p.id !== id));
  };

  const addSuggestedPillar = (suggested: typeof suggestedPillars[0]) => {
    if (pillars.length < 6 && !pillars.some(p => p.name === suggested.name)) {
      addPillar(suggested);
    }
  };

  const handleContinue = () => {
    updatePillars(pillars);
    nextStep();
  };

  const isValid = pillars.length >= 3;

  return (
    <OnboardingLayout>
      <div className="max-w-6xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-8"
        >
          <h2 className="text-4xl font-bold text-white mb-4">
            {selectedTemplate?.name === 'Custom Template' ? 'Create' : 'Customize'} Your Life Pillars
          </h2>
          <p className="text-xl text-[#B8BCC8] max-w-3xl mx-auto">
            {selectedTemplate?.name === 'Custom Template' 
              ? 'Build your personalized pillar system from scratch'
              : `Based on your ${selectedTemplate?.name} template, we've suggested some pillars. Feel free to modify them.`
            }
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Pillar Creation Area */}
          <div className="lg:col-span-2 space-y-6">
            {/* Current Pillars */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-2xl font-semibold text-white">Your Life Pillars</h3>
                <Badge className="bg-[rgba(244,208,63,0.2)] text-[#F4D03F]">
                  {pillars.length}/6 pillars
                </Badge>
              </div>

              <div className="space-y-4">
                <AnimatePresence>
                  {pillars.map((pillar, index) => (
                    <motion.div
                      key={pillar.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <Card className="glassmorphism-card border-[rgba(244,208,63,0.2)]">
                        <CardContent className="p-4">
                          {editingPillar === pillar.id ? (
                            // Edit Mode
                            <div className="space-y-3">
                              <div className="flex items-center space-x-3">
                                <div className="text-2xl">{pillar.icon}</div>
                                <Input
                                  value={pillar.name}
                                  onChange={(e) => updatePillar(pillar.id, { name: e.target.value })}
                                  className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white"
                                  placeholder="Pillar name"
                                />
                              </div>
                              <Textarea
                                value={pillar.description}
                                onChange={(e) => updatePillar(pillar.id, { description: e.target.value })}
                                className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white"
                                placeholder="Describe what this pillar means to you..."
                                rows={2}
                              />
                              <div className="flex space-x-2">
                                <Button
                                  onClick={() => setEditingPillar(null)}
                                  size="sm"
                                  className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
                                >
                                  Save
                                </Button>
                                <Button
                                  onClick={() => setEditingPillar(null)}
                                  variant="outline"
                                  size="sm"
                                  className="border-[rgba(244,208,63,0.2)] text-[#F4D03F]"
                                >
                                  Cancel
                                </Button>
                              </div>
                            </div>
                          ) : (
                            // Display Mode
                            <div className="flex items-center space-x-4">
                              <div className="flex items-center space-x-3 flex-1">
                                <GripVertical className="w-5 h-5 text-[#B8BCC8] cursor-grab" />
                                <div className="text-2xl">{pillar.icon}</div>
                                <div className="flex-1">
                                  <h4 className="text-white font-semibold">{pillar.name}</h4>
                                  <p className="text-[#B8BCC8] text-sm">{pillar.description}</p>
                                </div>
                              </div>
                              <div className="flex space-x-2">
                                <Button
                                  onClick={() => setEditingPillar(pillar.id)}
                                  variant="ghost"
                                  size="sm"
                                  className="text-[#B8BCC8] hover:text-[#F4D03F]"
                                >
                                  <Edit3 className="w-4 h-4" />
                                </Button>
                                <Button
                                  onClick={() => removePillar(pillar.id)}
                                  variant="ghost"
                                  size="sm"
                                  className="text-[#B8BCC8] hover:text-[#EF4444]"
                                >
                                  <Trash2 className="w-4 h-4" />
                                </Button>
                              </div>
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    </motion.div>
                  ))}
                </AnimatePresence>

                {/* Add New Pillar */}
                {pillars.length < 6 && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.4 }}
                  >
                    <Card className="glassmorphism-card border-[rgba(244,208,63,0.2)] border-dashed">
                      <CardContent className="p-4">
                        <div className="space-y-3">
                          <div className="flex items-center space-x-3">
                            <div className="text-2xl">{newPillar.icon}</div>
                            <Input
                              value={newPillar.name}
                              onChange={(e) => setNewPillar({ ...newPillar, name: e.target.value })}
                              className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white"
                              placeholder="Add a new pillar..."
                            />
                          </div>
                          {newPillar.name && (
                            <Textarea
                              value={newPillar.description}
                              onChange={(e) => setNewPillar({ ...newPillar, description: e.target.value })}
                              className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white"
                              placeholder="What does this pillar represent in your life?"
                              rows={2}
                            />
                          )}
                          {newPillar.name && (
                            <Button
                              onClick={() => addPillar()}
                              size="sm"
                              className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
                            >
                              <Plus className="w-4 h-4 mr-2" />
                              Add Pillar
                            </Button>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                )}
              </div>
            </motion.div>

            {/* Validation Message */}
            {!isValid && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-center p-4 glassmorphism-card border-[rgba(239,68,68,0.3)]"
              >
                <p className="text-[#EF4444]">
                  Please create at least 3 pillars to continue. We recommend 4-6 pillars for the best experience.
                </p>
              </motion.div>
            )}
          </div>

          {/* AI Suggestions Panel */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="lg:col-span-1"
          >
            <Card className="glassmorphism-card border-[rgba(244,208,63,0.2)] sticky top-4">
              <CardHeader>
                <CardTitle className="text-white flex items-center space-x-2">
                  <Sparkles className="w-5 h-5 text-[#F4D03F]" />
                  <span>AI Recommendations</span>
                </CardTitle>
                <p className="text-[#B8BCC8] text-sm">
                  Based on your template and goals, here are some pillar suggestions:
                </p>
              </CardHeader>
              <CardContent className="space-y-3">
                {suggestedPillars
                  .filter(suggested => !pillars.some(p => p.name === suggested.name))
                  .slice(0, 6)
                  .map((suggested, index) => (
                    <motion.div
                      key={suggested.name}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3, delay: 0.5 + index * 0.1 }}
                      className="glassmorphism-subtle p-3 rounded-lg hover:bg-[rgba(244,208,63,0.1)] transition-colors cursor-pointer"
                      onClick={() => addSuggestedPillar(suggested)}
                    >
                      <div className="flex items-center space-x-3">
                        <div className="text-xl">{suggested.icon}</div>
                        <div className="flex-1">
                          <h4 className="text-white font-medium text-sm">{suggested.name}</h4>
                          <p className="text-[#B8BCC8] text-xs">{suggested.description}</p>
                        </div>
                        <Button
                          size="sm"
                          variant="ghost"
                          className="text-[#F4D03F] hover:bg-[rgba(244,208,63,0.2)]"
                        >
                          <Plus className="w-4 h-4" />
                        </Button>
                      </div>
                    </motion.div>
                  ))}
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Continue Button */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="text-center mt-8"
        >
          <Button
            onClick={handleContinue}
            disabled={!isValid}
            size="lg"
            className={`px-8 py-4 text-lg font-semibold transition-all duration-200 group ${
              isValid
                ? 'bg-[#F4D03F] hover:bg-[#F7DC6F] text-[#0B0D14]'
                : 'bg-[#1A1D29] text-[#B8BCC8] cursor-not-allowed'
            }`}
          >
            Continue to AI Setup
            <ArrowRight className={`w-5 h-5 ml-2 transition-transform ${isValid ? 'group-hover:translate-x-1' : ''}`} />
          </Button>
        </motion.div>
      </div>
    </OnboardingLayout>
  );
}