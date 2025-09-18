import { useState } from 'react';
import { motion } from 'motion/react';
import { Play, ArrowRight } from 'lucide-react';
import { Button } from '../../ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../../ui/dialog';
import { useOnboardingStore } from '../../../stores/onboardingStore';
import OnboardingLayout from '../OnboardingLayout';
import aurumLogo from 'figma:asset/a76e299ce637adb8c75472e2d4c5e50cfbb65bac.png';

export default function WelcomeScreen() {
  const [showVideo, setShowVideo] = useState(false);
  const { nextStep, completeOnboarding } = useOnboardingStore();



  return (
    <OnboardingLayout showProgress={false} showBack={false} showSkip={false}>
      <div className="max-w-4xl mx-auto px-6 text-center">

        {/* Main Content */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          {/* Logo */}
          <motion.div
            className="mb-8"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.6, delay: 0.4, type: "spring", stiffness: 200 }}
          >
            <img 
              src={aurumLogo} 
              alt="Aurum Life Logo" 
              className="w-36 h-36 object-contain mx-auto mb-6"
            />
          </motion.div>

          {/* Main Headline */}
          <motion.h1
            className="text-5xl md:text-6xl lg:text-7xl font-bold text-white mb-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
          >
            Welcome to Your{' '}
            <span className="aurum-text-gradient">Life OS</span>
          </motion.h1>

          {/* Subheading */}
          <motion.p
            className="text-xl md:text-2xl text-[#B8BCC8] mb-8 max-w-2xl mx-auto leading-relaxed"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.8 }}
          >
            Transform how you think, feel, and achieve with a personal operating system 
            that aligns your daily actions with your deepest values.
          </motion.p>

          {/* Journey Preview */}
          <motion.div
            className="mb-12 max-w-md mx-auto"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.9 }}
          >
            <div className="glassmorphism-subtle p-6 rounded-xl">
              <p className="text-[#F4D03F] font-medium mb-3">What's Next?</p>
              <div className="space-y-2 text-sm text-[#B8BCC8]">
                <div className="flex items-center space-x-3">
                  <span className="w-2 h-2 bg-[#F4D03F] rounded-full"></span>
                  <span>Learn the PAPT Framework (3 min)</span>
                </div>
                <div className="flex items-center space-x-3">
                  <span className="w-2 h-2 bg-[#3B82F6] rounded-full"></span>
                  <span>Discover Life OS benefits (2 min)</span>
                </div>
                <div className="flex items-center space-x-3">
                  <span className="w-2 h-2 bg-[#10B981] rounded-full"></span>
                  <span>Personalize your setup (5 min)</span>
                </div>
              </div>
              <p className="text-xs text-[#6B7280] mt-4">Total time: 7-10 minutes</p>
            </div>
          </motion.div>

          {/* Video Preview */}
          <motion.div
            className="mb-12"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 1.0 }}
          >
            <div className="relative max-w-md mx-auto">
              <div className="glassmorphism-card p-8 rounded-2xl">
                <div className="relative">
                  <div className="w-64 h-36 bg-gradient-to-br from-[#F4D03F] to-[#F7DC6F] rounded-lg flex items-center justify-center mx-auto mb-4">
                    <Button
                      onClick={() => setShowVideo(true)}
                      size="lg"
                      className="w-16 h-16 rounded-full bg-white/20 hover:bg-white/30 backdrop-blur-sm border-2 border-white/30"
                    >
                      <Play className="w-8 h-8 text-white ml-1" />
                    </Button>
                  </div>
                  <p className="text-[#B8BCC8] text-sm">
                    Watch: How Aurum Life Works (30 seconds)
                  </p>
                </div>
              </div>
            </div>
          </motion.div>

          {/* CTA Buttons */}
          <motion.div
            className="space-y-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 1.2 }}
          >
            <Button
              onClick={nextStep}
              size="lg"
              className="bg-[#F4D03F] hover:bg-[#F7DC6F] text-[#0B0D14] px-8 py-4 text-lg font-semibold group"
            >
              Let's Start Learning
              <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
            </Button>
            
            <div>
              <Button
                onClick={completeOnboarding}
                variant="link"
                className="text-[#B8BCC8] hover:text-white text-sm"
              >
                Skip to App
              </Button>
            </div>
          </motion.div>

          {/* Feature Highlights */}
          <motion.div
            className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-3xl mx-auto"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 1.4 }}
          >
            {[
              { icon: '🎯', title: 'Goal Alignment', desc: 'Connect daily actions to life vision' },
              { icon: '🧠', title: 'AI Coaching', desc: 'Personalized insights and guidance' },
              { icon: '💫', title: 'Emotional Intelligence', desc: 'Track patterns and grow mindfully' },
            ].map((feature, index) => (
              <motion.div
                key={feature.title}
                className="glassmorphism-subtle p-6 rounded-xl text-center"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 1.6 + index * 0.1 }}
              >
                <div className="text-3xl mb-2">{feature.icon}</div>
                <h3 className="text-white font-semibold mb-2">{feature.title}</h3>
                <p className="text-[#B8BCC8] text-sm">{feature.desc}</p>
              </motion.div>
            ))}
          </motion.div>
        </motion.div>

        {/* Video Modal */}
        <Dialog open={showVideo} onOpenChange={setShowVideo}>
          <DialogContent className="max-w-3xl glassmorphism-card border-0">
            <DialogHeader>
              <DialogTitle className="text-white">How Aurum Life Works</DialogTitle>
            </DialogHeader>
            <div className="aspect-video bg-gradient-to-br from-[#F4D03F] to-[#F7DC6F] rounded-lg flex items-center justify-center">
              <div className="text-center text-[#0B0D14]">
                <Play className="w-16 h-16 mx-auto mb-4 opacity-50" />
                <p className="text-lg font-medium">Demo Video</p>
                <p className="text-sm opacity-75">30-second explainer video would play here</p>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </OnboardingLayout>
  );
}