import { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Calendar, CheckCircle, Target, TrendingUp, Plus, X, Save, Sparkles, Award, ArrowRight } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog';
import { Button } from '../ui/button';
import { Textarea } from '../ui/textarea';
import { Input } from '../ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Progress } from '../ui/progress';
import { useEnhancedFeaturesStore } from '../../stores/enhancedFeaturesStore';

const REFLECTION_PROMPTS = {
  weekly: [
    "What were your top 3 wins this week?",
    "What challenges did you face and how did you overcome them?",
    "Which pillar needs more attention next week?",
    "What would you do differently if you could repeat this week?",
    "How did you feel about your energy levels this week?"
  ],
  monthly: [
    "What major milestones did you achieve this month?",
    "How has your overall life balance shifted?",
    "What patterns do you notice in your productivity?",
    "What skills or habits would you like to develop next month?",
    "How aligned were your daily actions with your long-term vision?"
  ],
  quarterly: [
    "What transformative changes have you made this quarter?",
    "How have your priorities evolved?",
    "What systems or processes are working well for you?",
    "What would you like to experiment with next quarter?",
    "How has your definition of success changed?"
  ]
};

export default function ReviewSystem() {
  const {
    isReviewModalOpen,
    currentReview,
    reviewSessions,
    pillars,
    achievements,
    startReview,
    updateReviewReflection,
    addReviewWin,
    addReviewImprovement,
    addNextWeekFocus,
    completeReview,
    closeReviewModal
  } = useEnhancedFeaturesStore();

  const [currentPromptIndex, setCurrentPromptIndex] = useState(0);
  const [currentResponse, setCurrentResponse] = useState('');
  const [newWin, setNewWin] = useState('');
  const [newImprovement, setNewImprovement] = useState('');
  const [newFocus, setNewFocus] = useState('');
  const [activeTab, setActiveTab] = useState('reflections');

  const handleResponseSubmit = () => {
    if (!currentReview || !currentResponse.trim()) return;
    
    const prompts = REFLECTION_PROMPTS[currentReview.type];
    const currentPrompt = prompts[currentPromptIndex];
    
    updateReviewReflection(currentPrompt, currentResponse.trim());
    setCurrentResponse('');
    
    if (currentPromptIndex < prompts.length - 1) {
      setCurrentPromptIndex(currentPromptIndex + 1);
    } else {
      setActiveTab('wins');
    }
  };

  const handleAddWin = () => {
    if (!newWin.trim()) return;
    addReviewWin(newWin.trim());
    setNewWin('');
  };

  const handleAddImprovement = () => {
    if (!newImprovement.trim()) return;
    addReviewImprovement(newImprovement.trim());
    setNewImprovement('');
  };

  const handleAddFocus = () => {
    if (!newFocus.trim()) return;
    addNextWeekFocus(newFocus.trim());
    setNewFocus('');
  };

  const getReviewTypeLabel = (type: string) => {
    return type.charAt(0).toUpperCase() + type.slice(1) + ' Review';
  };

  const getNextReviewDate = (type: 'weekly' | 'monthly' | 'quarterly') => {
    const now = new Date();
    switch (type) {
      case 'weekly':
        const nextWeek = new Date(now);
        nextWeek.setDate(now.getDate() + 7);
        return nextWeek;
      case 'monthly':
        const nextMonth = new Date(now);
        nextMonth.setMonth(now.getMonth() + 1);
        return nextMonth;
      case 'quarterly':
        const nextQuarter = new Date(now);
        nextQuarter.setMonth(now.getMonth() + 3);
        return nextQuarter;
    }
  };

  const recentReviews = reviewSessions.slice(0, 3);
  const thisWeekAchievements = achievements.filter(achievement => {
    const weekAgo = new Date();
    weekAgo.setDate(weekAgo.getDate() - 7);
    return new Date(achievement.earnedAt) > weekAgo;
  });

  return (
    <div className="space-y-6">
      {/* Review Actions */}
      <Card className="glassmorphism-card border-0 bg-[#1A1D29] text-white">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Calendar className="w-5 h-5 text-[#F4D03F]" />
            <span>Review & Reflection</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {(['weekly', 'monthly', 'quarterly'] as const).map((type) => (
              <motion.div
                key={type}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Button
                  onClick={() => startReview(type)}
                  className="w-full h-24 glassmorphism-panel border-[rgba(244,208,63,0.2)] text-white hover:border-[rgba(244,208,63,0.4)] hover:bg-[rgba(244,208,63,0.05)] flex flex-col items-center justify-center space-y-2"
                  variant="outline"
                >
                  <div className="text-lg font-semibold">{getReviewTypeLabel(type)}</div>
                  <div className="text-xs text-[#B8BCC8]">
                    Next: {getNextReviewDate(type).toLocaleDateString()}
                  </div>
                </Button>
              </motion.div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Recent Reviews */}
      {recentReviews.length > 0 && (
        <Card className="glassmorphism-card border-0 bg-[#1A1D29] text-white">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <CheckCircle className="w-5 h-5 text-[#F4D03F]" />
              <span>Recent Reviews</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentReviews.map((review) => (
                <motion.div
                  key={review.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="glassmorphism-panel p-4 rounded-lg"
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      <Badge className="aurum-gradient text-[#0B0D14]">
                        {getReviewTypeLabel(review.type)}
                      </Badge>
                      <span className="text-sm text-[#B8BCC8]">
                        {new Date(review.date).toLocaleDateString()}
                      </span>
                    </div>
                    {review.completed && (
                      <CheckCircle className="w-5 h-5 text-green-400" />
                    )}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                    <div>
                      <div className="font-medium text-white mb-1">Wins</div>
                      <div className="text-[#B8BCC8]">{review.wins.length} items</div>
                    </div>
                    <div>
                      <div className="font-medium text-white mb-1">Improvements</div>
                      <div className="text-[#B8BCC8]">{review.improvements.length} items</div>
                    </div>
                    <div>
                      <div className="font-medium text-white mb-1">Next Focus</div>
                      <div className="text-[#B8BCC8]">{review.nextWeekFocus.length} items</div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* This Week's Achievements */}
      {thisWeekAchievements.length > 0 && (
        <Card className="glassmorphism-card border-0 bg-[#1A1D29] text-white">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Award className="w-5 h-5 text-[#F4D03F]" />
              <span>This Week's Achievements</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {thisWeekAchievements.map((achievement) => (
                <motion.div
                  key={achievement.id}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="flex items-center space-x-3 p-3 glassmorphism-panel rounded-lg"
                >
                  <div className="text-2xl">{achievement.icon}</div>
                  <div className="flex-1">
                    <div className="font-medium text-white">{achievement.title}</div>
                    <div className="text-sm text-[#B8BCC8]">{achievement.description}</div>
                  </div>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Review Modal */}
      <Dialog open={isReviewModalOpen} onOpenChange={closeReviewModal}>
        <DialogContent className="glassmorphism-card border-0 bg-[#1A1D29] text-white max-w-4xl max-h-[90vh] overflow-hidden">
          <DialogHeader>
            <DialogTitle className="flex items-center space-x-2">
              <Sparkles className="w-5 h-5 text-[#F4D03F]" />
              <span>{currentReview && getReviewTypeLabel(currentReview.type)}</span>
            </DialogTitle>
          </DialogHeader>

          {currentReview && (
            <Tabs value={activeTab} onValueChange={setActiveTab} className="flex flex-col h-full">
              <TabsList className="bg-[#0B0D14] border-[rgba(244,208,63,0.2)] mb-6">
                <TabsTrigger value="reflections" className="text-[#B8BCC8] data-[state=active]:text-[#F4D03F]">
                  Reflections
                </TabsTrigger>
                <TabsTrigger value="wins" className="text-[#B8BCC8] data-[state=active]:text-[#F4D03F]">
                  Wins
                </TabsTrigger>
                <TabsTrigger value="improvements" className="text-[#B8BCC8] data-[state=active]:text-[#F4D03F]">
                  Improvements
                </TabsTrigger>
                <TabsTrigger value="focus" className="text-[#B8BCC8] data-[state=active]:text-[#F4D03F]">
                  Next Focus
                </TabsTrigger>
              </TabsList>

              <div className="flex-1 overflow-auto">
                <TabsContent value="reflections" className="mt-0">
                  <div className="space-y-6">
                    {/* Progress */}
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-[#B8BCC8]">
                          Question {currentPromptIndex + 1} of {REFLECTION_PROMPTS[currentReview.type].length}
                        </span>
                        <span className="text-sm text-[#F4D03F]">
                          {Math.round(((currentPromptIndex + 1) / REFLECTION_PROMPTS[currentReview.type].length) * 100)}%
                        </span>
                      </div>
                      <Progress 
                        value={((currentPromptIndex + 1) / REFLECTION_PROMPTS[currentReview.type].length) * 100}
                        className="h-2 bg-[rgba(244,208,63,0.1)]"
                      />
                    </div>

                    {/* Current Prompt */}
                    <div className="glassmorphism-panel p-6 rounded-lg">
                      <h3 className="text-lg font-semibold text-white mb-4">
                        {REFLECTION_PROMPTS[currentReview.type][currentPromptIndex]}
                      </h3>
                      <Textarea
                        value={currentResponse}
                        onChange={(e) => setCurrentResponse(e.target.value)}
                        placeholder="Take your time to reflect deeply..."
                        className="min-h-[120px] bg-[#0B0D14] border-[rgba(244,208,63,0.2)] text-white placeholder:text-[#6B7280] focus:border-[#F4D03F] resize-none"
                      />
                      <div className="flex justify-end mt-4">
                        <Button
                          onClick={handleResponseSubmit}
                          disabled={!currentResponse.trim()}
                          className="aurum-gradient text-[#0B0D14]"
                        >
                          {currentPromptIndex < REFLECTION_PROMPTS[currentReview.type].length - 1 ? (
                            <>Next Question <ArrowRight className="w-4 h-4 ml-2" /></>
                          ) : (
                            <>Continue <ArrowRight className="w-4 h-4 ml-2" /></>
                          )}
                        </Button>
                      </div>
                    </div>

                    {/* Previous Responses */}
                    {Object.keys(currentReview.reflections).length > 0 && (
                      <div className="space-y-3">
                        <h4 className="font-medium text-white">Previous Responses</h4>
                        {Object.entries(currentReview.reflections).map(([prompt, response]) => (
                          <div key={prompt} className="glassmorphism-panel p-4 rounded-lg">
                            <div className="font-medium text-[#F4D03F] mb-2 text-sm">{prompt}</div>
                            <div className="text-[#B8BCC8] text-sm">{response}</div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </TabsContent>

                <TabsContent value="wins" className="mt-0">
                  <div className="space-y-4">
                    <div className="flex space-x-2">
                      <Input
                        value={newWin}
                        onChange={(e) => setNewWin(e.target.value)}
                        placeholder="Add a win from this period..."
                        className="flex-1 bg-[#0B0D14] border-[rgba(244,208,63,0.2)] text-white placeholder:text-[#6B7280] focus:border-[#F4D03F]"
                        onKeyPress={(e) => e.key === 'Enter' && handleAddWin()}
                      />
                      <Button onClick={handleAddWin} className="aurum-gradient text-[#0B0D14]">
                        <Plus className="w-4 h-4" />
                      </Button>
                    </div>
                    
                    <div className="space-y-2">
                      {currentReview.wins.map((win, index) => (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="flex items-center space-x-3 p-3 glassmorphism-panel rounded-lg"
                        >
                          <CheckCircle className="w-5 h-5 text-green-400" />
                          <span className="flex-1 text-white">{win}</span>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="improvements" className="mt-0">
                  <div className="space-y-4">
                    <div className="flex space-x-2">
                      <Input
                        value={newImprovement}
                        onChange={(e) => setNewImprovement(e.target.value)}
                        placeholder="What could be improved next time?"
                        className="flex-1 bg-[#0B0D14] border-[rgba(244,208,63,0.2)] text-white placeholder:text-[#6B7280] focus:border-[#F4D03F]"
                        onKeyPress={(e) => e.key === 'Enter' && handleAddImprovement()}
                      />
                      <Button onClick={handleAddImprovement} className="aurum-gradient text-[#0B0D14]">
                        <Plus className="w-4 h-4" />
                      </Button>
                    </div>
                    
                    <div className="space-y-2">
                      {currentReview.improvements.map((improvement, index) => (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="flex items-center space-x-3 p-3 glassmorphism-panel rounded-lg"
                        >
                          <TrendingUp className="w-5 h-5 text-[#F4D03F]" />
                          <span className="flex-1 text-white">{improvement}</span>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="focus" className="mt-0">
                  <div className="space-y-4">
                    <div className="flex space-x-2">
                      <Input
                        value={newFocus}
                        onChange={(e) => setNewFocus(e.target.value)}
                        placeholder="What will you focus on next?"
                        className="flex-1 bg-[#0B0D14] border-[rgba(244,208,63,0.2)] text-white placeholder:text-[#6B7280] focus:border-[#F4D03F]"
                        onKeyPress={(e) => e.key === 'Enter' && handleAddFocus()}
                      />
                      <Button onClick={handleAddFocus} className="aurum-gradient text-[#0B0D14]">
                        <Plus className="w-4 h-4" />
                      </Button>
                    </div>
                    
                    <div className="space-y-2">
                      {currentReview.nextWeekFocus.map((focus, index) => (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="flex items-center space-x-3 p-3 glassmorphism-panel rounded-lg"
                        >
                          <Target className="w-5 h-5 text-[#F4D03F]" />
                          <span className="flex-1 text-white">{focus}</span>
                        </motion.div>
                      ))}
                    </div>

                    <div className="flex justify-end space-x-3 mt-6 pt-6 border-t border-[rgba(244,208,63,0.2)]">
                      <Button
                        variant="outline"
                        onClick={closeReviewModal}
                        className="border-[rgba(244,208,63,0.3)] text-[#B8BCC8] hover:text-white hover:bg-[rgba(244,208,63,0.1)]"
                      >
                        Save Draft
                      </Button>
                      <Button
                        onClick={completeReview}
                        className="aurum-gradient text-[#0B0D14]"
                      >
                        <Save className="w-4 h-4 mr-2" />
                        Complete Review
                      </Button>
                    </div>
                  </div>
                </TabsContent>
              </div>
            </Tabs>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}