import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { 
  Sparkles, 
  Check, 
  ArrowRight, 
  Share2, 
  Download, 
  Calendar,
  Star,
  Trophy,
  Heart
} from 'lucide-react';
import { Button } from '../../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../../ui/card';
import { Badge } from '../../ui/badge';
import { Input } from '../../ui/input';
import { Textarea } from '../../ui/textarea';
import { Label } from '../../ui/label';
import { Separator } from '../../ui/separator';
import { useOnboardingStore } from '../../../stores/onboardingStore';
import OnboardingLayout from '../OnboardingLayout';

export default function ReadyToLaunch() {
  const { 
    userData, 
    selectedTemplate, 
    customPillars, 
    aiPreferences, 
    completeOnboarding 
  } = useOnboardingStore();
  
  const [setupTime] = useState(() => {
    // Simulate setup time calculation
    return Math.floor(Math.random() * 3) + 4; // 4-6 minutes
  });
  
  const [showConfetti, setShowConfetti] = useState(false);
  const [feedback, setFeedback] = useState({ rating: 0, suggestion: '', email: '' });

  useEffect(() => {
    setShowConfetti(true);
    const timer = setTimeout(() => setShowConfetti(false), 3000);
    return () => clearTimeout(timer);
  }, []);

  const handleRating = (rating: number) => {
    setFeedback(prev => ({ ...prev, rating }));
  };

  const handleLaunch = () => {
    completeOnboarding();
  };

  const confettiPieces = Array.from({ length: 50 }, (_, i) => ({
    id: i,
    delay: Math.random() * 2,
    duration: 2 + Math.random() * 2,
    x: Math.random() * 100,
    color: ['#F4D03F', '#F7DC6F', '#F8C471', '#F9E79F'][Math.floor(Math.random() * 4)],
  }));

  return (
    <OnboardingLayout showProgress={false} showBack={false}>
      <div className="max-w-4xl mx-auto px-6 text-center relative">
        {/* Confetti Animation */}
        {showConfetti && (
          <div className="absolute inset-0 pointer-events-none overflow-hidden">
            {confettiPieces.map((piece) => (
              <motion.div
                key={piece.id}
                className="absolute w-2 h-2 rounded-full"
                style={{
                  backgroundColor: piece.color,
                  left: `${piece.x}%`,
                  top: '-10px',
                }}
                animate={{
                  y: ['0vh', '110vh'],
                  rotate: [0, 360, 720],
                  opacity: [1, 1, 0],
                }}
                transition={{
                  duration: piece.duration,
                  delay: piece.delay,
                  ease: 'easeOut',
                }}
              />
            ))}
          </div>
        )}

        {/* Success Animation */}
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.6, type: "spring", stiffness: 200 }}
          className="mb-8"
        >
          <div className="inline-flex items-center justify-center w-24 h-24 aurum-gradient rounded-full mb-6 relative">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.4, delay: 0.2 }}
            >
              <Check className="w-12 h-12 text-[#0B0D14]" />
            </motion.div>
            
            {/* Success Ring Animation */}
            <motion.div
              className="absolute inset-0 border-4 border-[#F4D03F] rounded-full"
              initial={{ scale: 1, opacity: 1 }}
              animate={{ scale: 1.5, opacity: 0 }}
              transition={{ duration: 1, delay: 0.5 }}
            />
          </div>
        </motion.div>

        {/* Main Success Message */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
          className="mb-8"
        >
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-4">
            Your <span className="aurum-text-gradient">Life OS</span> is Ready!
          </h1>
          <p className="text-xl text-[#B8BCC8] mb-4">
            Congratulations, {userData.firstName}! You've built your personalized life operating system.
          </p>
          <Badge className="bg-[rgba(244,208,63,0.2)] text-[#F4D03F] text-lg px-4 py-2">
            Setup completed in {setupTime} minutes ⚡
          </Badge>
        </motion.div>

        {/* Setup Summary */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.5 }}
          className="mb-12"
        >
          <Card className="glassmorphism-card border-[rgba(244,208,63,0.2)] max-w-2xl mx-auto">
            <CardHeader>
              <CardTitle className="text-white text-2xl">Your Setup Summary</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Template Badge */}
              {selectedTemplate && (
                <div className="flex items-center justify-center">
                  <Badge className="bg-[#F4D03F] text-[#0B0D14] text-lg px-4 py-2">
                    {selectedTemplate.name} Template
                  </Badge>
                </div>
              )}

              <Separator className="bg-[rgba(244,208,63,0.1)]" />

              {/* Pillars Count */}
              <div className="flex items-center justify-center space-x-4">
                <div className="text-center">
                  <div className="text-3xl font-bold text-[#F4D03F]">{customPillars.length}</div>
                  <div className="text-[#B8BCC8] text-sm">Life Pillars Created</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-[#F4D03F]">{userData.motivations.length}</div>
                  <div className="text-[#B8BCC8] text-sm">Goals Selected</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-[#F4D03F]">
                    {aiPreferences.enabledFeatures ? 
                      Object.values(aiPreferences.enabledFeatures).filter(Boolean).length : 5
                    }
                  </div>
                  <div className="text-[#B8BCC8] text-sm">AI Features Enabled</div>
                </div>
              </div>

              <Separator className="bg-[rgba(244,208,63,0.1)]" />

              {/* Quick Preview of Pillars */}
              <div>
                <Label className="text-[#F4D03F] text-sm font-medium">Your Life Pillars:</Label>
                <div className="flex flex-wrap gap-2 mt-2 justify-center">
                  {customPillars.slice(0, 4).map((pillar) => (
                    <Badge
                      key={pillar.id}
                      className="bg-[rgba(244,208,63,0.1)] text-[#F4D03F] border-[rgba(244,208,63,0.3)]"
                    >
                      {pillar.icon} {pillar.name}
                    </Badge>
                  ))}
                  {customPillars.length > 4 && (
                    <Badge className="bg-[rgba(244,208,63,0.1)] text-[#F4D03F]">
                      +{customPillars.length - 4} more
                    </Badge>
                  )}
                </div>
              </div>

              <div className="text-center">
                <p className="text-[#B8BCC8] text-sm">
                  You can edit these preferences anytime in Settings
                </p>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Launch Options */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.7 }}
          className="space-y-6 mb-12"
        >
          <Button
            onClick={handleLaunch}
            size="lg"
            className="bg-[#F4D03F] hover:bg-[#F7DC6F] text-[#0B0D14] px-12 py-4 text-xl font-bold group shadow-lg shadow-[#F4D03F]/20"
          >
            Start Using Aurum Life
            <ArrowRight className="w-6 h-6 ml-3 group-hover:translate-x-1 transition-transform" />
          </Button>

          <div className="flex flex-wrap gap-4 justify-center">
            <Button
              variant="outline"
              className="border-[rgba(244,208,63,0.2)] text-[#F4D03F] hover:bg-[rgba(244,208,63,0.1)]"
            >
              <Share2 className="w-4 h-4 mr-2" />
              Invite Friends
            </Button>
            
            <Button
              variant="outline"
              className="border-[rgba(244,208,63,0.2)] text-[#F4D03F] hover:bg-[rgba(244,208,63,0.1)]"
            >
              <Calendar className="w-4 h-4 mr-2" />
              Connect Calendar
            </Button>
            
            <Button
              variant="outline"
              className="border-[rgba(244,208,63,0.2)] text-[#F4D03F] hover:bg-[rgba(244,208,63,0.1)]"
            >
              <Download className="w-4 h-4 mr-2" />
              Get Mobile App
            </Button>
          </div>
        </motion.div>

        {/* Next Steps Preview */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.9 }}
          className="mb-12"
        >
          <h3 className="text-2xl font-semibold text-white mb-6">What's Next?</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                icon: <Trophy className="w-8 h-8 text-[#F4D03F]" />,
                title: "Create Your First Goals",
                description: "Transform your pillars into actionable goals",
                time: "2 minutes"
              },
              {
                icon: <Heart className="w-8 h-8 text-[#F4D03F]" />,
                title: "Log Your First Journal Entry",
                description: "Start tracking your emotional patterns",
                time: "3 minutes"
              },
              {
                icon: <Sparkles className="w-8 h-8 text-[#F4D03F]" />,
                title: "Get AI Insights",
                description: "Your coach will have insights after a few days",
                time: "Automatic"
              }
            ].map((step, index) => (
              <motion.div
                key={step.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 1.1 + index * 0.1 }}
              >
                <Card className="glassmorphism-subtle border-[rgba(244,208,63,0.1)] text-center p-6">
                  <div className="mb-4">{step.icon}</div>
                  <h4 className="text-white font-semibold mb-2">{step.title}</h4>
                  <p className="text-[#B8BCC8] text-sm mb-2">{step.description}</p>
                  <Badge className="bg-[rgba(244,208,63,0.1)] text-[#F4D03F] text-xs">
                    {step.time}
                  </Badge>
                </Card>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Optional Feedback */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 1.1 }}
          className="max-w-xl mx-auto"
        >
          <Card className="glassmorphism-card border-[rgba(244,208,63,0.1)]">
            <CardHeader>
              <CardTitle className="text-white text-lg">How was your onboarding experience?</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Star Rating */}
              <div className="flex justify-center space-x-2">
                {[1, 2, 3, 4, 5].map((star) => (
                  <Button
                    key={star}
                    variant="ghost"
                    size="sm"
                    onClick={() => handleRating(star)}
                    className={`p-1 ${
                      star <= feedback.rating 
                        ? 'text-[#F4D03F]' 
                        : 'text-[#B8BCC8] hover:text-[#F4D03F]'
                    }`}
                  >
                    <Star className={`w-6 h-6 ${star <= feedback.rating ? 'fill-current' : ''}`} />
                  </Button>
                ))}
              </div>

              {/* Optional Feedback */}
              <div className="space-y-3">
                <Textarea
                  placeholder="Any suggestions for improvement? (optional)"
                  value={feedback.suggestion}
                  onChange={(e) => setFeedback(prev => ({ ...prev, suggestion: e.target.value }))}
                  className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white text-sm"
                  rows={2}
                />
                
                <div className="flex items-center space-x-3">
                  <Input
                    type="email"
                    placeholder="Email for updates (optional)"
                    value={feedback.email}
                    onChange={(e) => setFeedback(prev => ({ ...prev, email: e.target.value }))}
                    className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white text-sm"
                  />
                  <Button
                    size="sm"
                    className="bg-[rgba(244,208,63,0.2)] text-[#F4D03F] hover:bg-[rgba(244,208,63,0.3)]"
                  >
                    Submit
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </OnboardingLayout>
  );
}