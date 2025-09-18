import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Eye, EyeOff, Mail, Lock, ArrowRight, Target, User, Calendar, Loader2, CheckCircle } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Separator } from '../ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Checkbox } from '../ui/checkbox';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import aurumLogo from 'figma:asset/a76e299ce637adb8c75472e2d4c5e50cfbb65bac.png';

interface LoginProps {
  onLogin: () => void;
  isLoading?: boolean;
  error?: string | null;
}

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      duration: 0.8,
      staggerChildren: 0.1,
    }
  }
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5 }
  }
};

const featureVariants = {
  hidden: { opacity: 0, scale: 0.8 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: { duration: 0.6, delay: 0.3 }
  }
};

export default function SimpleEnhancedLogin({ onLogin, isLoading: externalLoading, error: externalError }: LoginProps) {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [activeTab, setActiveTab] = useState('login');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Login form state
  const [loginData, setLoginData] = useState(() => ({
    email: '',
    password: '',
    rememberMe: false,
  }));

  // Signup form state
  const [signupData, setSignupData] = useState(() => ({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    acceptTerms: false,
  }));

  const handleLoginSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      // Simulate form processing
      await new Promise(resolve => setTimeout(resolve, 500));
      onLogin();
    } finally {
      setIsSubmitting(false);
    }
  }, [onLogin]);

  const handleSignupSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      // Simulate form processing
      await new Promise(resolve => setTimeout(resolve, 500));
      onLogin();
    } finally {
      setIsSubmitting(false);
    }
  }, [onLogin]);

  const isLoading = externalLoading || isSubmitting;

  return (
    <div className="min-h-screen bg-[#0B0D14] flex">
      {/* Left Panel - Welcome & Features */}
      <motion.div 
        className="hidden lg:flex lg:w-1/2 relative overflow-hidden"
        initial="hidden"
        animate="visible"
        variants={containerVariants}
      >
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-[#1A1D29] via-[#0B0D14] to-[#1A1D29]" />
        <div className="absolute inset-0" style={{
          backgroundImage: `radial-gradient(circle at 25% 25%, rgba(244, 208, 63, 0.1) 0%, transparent 50%), 
                           radial-gradient(circle at 75% 75%, rgba(244, 208, 63, 0.05) 0%, transparent 50%)`,
          opacity: 0.3
        }} />
        
        <div className="relative z-10 flex flex-col justify-center px-12 py-16">
          <motion.div variants={itemVariants} className="mb-12">
            <div className="flex items-center space-x-3 mb-6">
              <img src={aurumLogo} alt="Aurum Life" className="w-12 h-12" />
              <h1 className="aurum-text-gradient">Aurum Life</h1>
            </div>
            <p className="text-xl text-[#B8BCC8] leading-relaxed">
              Transform your daily actions into strategic steps toward your life vision
            </p>
          </motion.div>

          <motion.div variants={itemVariants} className="space-y-8">
            <motion.div 
              variants={featureVariants}
              className="glassmorphism-panel p-6 rounded-xl"
            >
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <Target className="w-6 h-6 text-[#F4D03F]" />
                </div>
                <div>
                  <h3 className="text-white mb-2">Strategic Hierarchy</h3>
                  <p className="text-[#B8BCC8] text-sm">
                    Align every task with your life pillars through Areas → Projects → Tasks
                  </p>
                </div>
              </div>
            </motion.div>

            <motion.div 
              variants={featureVariants}
              className="glassmorphism-panel p-6 rounded-xl"
            >
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <Calendar className="w-6 h-6 text-[#F4D03F]" />
                </div>
                <div>
                  <h3 className="text-white mb-2">Daily Alignment</h3>
                  <p className="text-[#B8BCC8] text-sm">
                    See how today's work connects to your bigger picture and long-term goals
                  </p>
                </div>
              </div>
            </motion.div>

            <motion.div 
              variants={featureVariants}
              className="glassmorphism-panel p-6 rounded-xl"
            >
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <User className="w-6 h-6 text-[#F4D03F]" />
                </div>
                <div>
                  <h3 className="text-white mb-2">Personal Operating System</h3>
                  <p className="text-[#B8BCC8] text-sm">
                    A complete system for managing your life with intention and purpose
                  </p>
                </div>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </motion.div>

      {/* Right Panel - Auth Forms */}
      <motion.div 
        className="flex-1 flex items-center justify-center p-8"
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.8, delay: 0.2 }}
      >
        <div className="w-full max-w-md">
          <Card className="glassmorphism-card border-0 bg-[rgba(26,29,41,0.6)] backdrop-blur-xl">
            <CardHeader className="text-center pb-6">
              <div className="lg:hidden flex items-center justify-center space-x-3 mb-4">
                <img src={aurumLogo} alt="Aurum Life" className="w-10 h-10" />
                <CardTitle className="aurum-text-gradient">Aurum Life</CardTitle>
              </div>
              <CardTitle className="text-white hidden lg:block">Welcome Back</CardTitle>
              <CardDescription className="text-[#B8BCC8]">
                {activeTab === 'login' 
                  ? 'Sign in to continue your journey' 
                  : 'Start your personal operating system'
                }
              </CardDescription>
            </CardHeader>

            <CardContent>
              <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                <TabsList className="grid w-full grid-cols-2 bg-[rgba(26,29,41,0.4)] border border-[rgba(244,208,63,0.2)]">
                  <TabsTrigger 
                    value="login" 
                    className="data-[state=active]:bg-[#F4D03F] data-[state=active]:text-[#0B0D14] text-[#B8BCC8]"
                  >
                    Sign In
                  </TabsTrigger>
                  <TabsTrigger 
                    value="signup" 
                    className="data-[state=active]:bg-[#F4D03F] data-[state=active]:text-[#0B0D14] text-[#B8BCC8]"
                  >
                    Sign Up
                  </TabsTrigger>
                </TabsList>

                <AnimatePresence mode="wait">
                  <motion.div
                    key={activeTab}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.2 }}
                  >
                    <TabsContent value="login" className="space-y-6 mt-6">
                      <form onSubmit={handleLoginSubmit} className="space-y-6">
                        <div className="space-y-2">
                          <Label htmlFor="email" className="text-[#F4D03F]">Email *</Label>
                          <div className="relative">
                            <Mail className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-[#B8BCC8]" />
                            <Input
                              id="email"
                              type="email"
                              placeholder="Enter your email"
                              value={loginData.email}
                              onChange={useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
                                setLoginData(prev => ({ ...prev, email: e.target.value }));
                              }, [])}
                              className="glassmorphism-panel border-[rgba(244,208,63,0.2)] bg-[rgba(26,29,41,0.4)] text-white placeholder:text-[#6B7280] focus:border-[#F4D03F] pl-10 h-12"
                              required
                            />
                          </div>
                        </div>

                        <div className="space-y-2">
                          <Label htmlFor="password" className="text-[#F4D03F]">Password *</Label>
                          <div className="relative">
                            <Lock className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-[#B8BCC8]" />
                            <Input
                              id="password"
                              type={showPassword ? 'text' : 'password'}
                              placeholder="Enter your password"
                              value={loginData.password}
                              onChange={(e) => setLoginData(prev => ({ ...prev, password: e.target.value }))}
                              className="glassmorphism-panel border-[rgba(244,208,63,0.2)] bg-[rgba(26,29,41,0.4)] text-white placeholder:text-[#6B7280] focus:border-[#F4D03F] pl-10 pr-10 h-12"
                              required
                            />
                            <button
                              type="button"
                              onClick={() => setShowPassword(!showPassword)}
                              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-[#B8BCC8] hover:text-[#F4D03F]"
                            >
                              {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                            </button>
                          </div>
                        </div>

                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <Checkbox
                              id="rememberMe"
                              checked={loginData.rememberMe}
                              onCheckedChange={(checked) => {
                                const isChecked = checked === true;
                                setLoginData(prev => ({ ...prev, rememberMe: isChecked }));
                              }}
                              className="border-[rgba(244,208,63,0.3)] data-[state=checked]:bg-[#F4D03F] data-[state=checked]:border-[#F4D03F]"
                            />
                            <Label htmlFor="rememberMe" className="text-sm text-[#B8BCC8]">
                              Remember me
                            </Label>
                          </div>
                          <Button
                            type="button"
                            variant="link"
                            className="text-[#F4D03F] hover:text-[#F7DC6F] p-0 h-auto"
                          >
                            Forgot password?
                          </Button>
                        </div>

                        {externalError && (
                          <div className="bg-[rgba(239,68,68,0.1)] border border-[rgba(239,68,68,0.2)] rounded-lg p-3">
                            <p className="text-[#EF4444] text-sm">{externalError}</p>
                          </div>
                        )}

                        <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                          <Button
                            type="submit"
                            disabled={isLoading}
                            className="w-full bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F] disabled:opacity-50 h-12"
                          >
                            {isLoading ? (
                              <div className="flex items-center space-x-2">
                                <Loader2 className="w-4 h-4 animate-spin" />
                                <span>Signing in...</span>
                              </div>
                            ) : (
                              <div className="flex items-center space-x-2">
                                <span>Sign In</span>
                                <ArrowRight className="w-4 h-4" />
                              </div>
                            )}
                          </Button>
                        </motion.div>
                      </form>
                    </TabsContent>

                    <TabsContent value="signup" className="space-y-6 mt-6">
                      <form onSubmit={handleSignupSubmit} className="space-y-6">
                        <div className="space-y-2">
                          <Label htmlFor="name" className="text-[#F4D03F]">Full Name *</Label>
                          <div className="relative">
                            <User className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-[#B8BCC8]" />
                            <Input
                              id="name"
                              placeholder="Enter your full name"
                              value={signupData.name}
                              onChange={(e) => setSignupData(prev => ({ ...prev, name: e.target.value }))}
                              className="glassmorphism-panel border-[rgba(244,208,63,0.2)] bg-[rgba(26,29,41,0.4)] text-white placeholder:text-[#6B7280] focus:border-[#F4D03F] pl-10 h-12"
                              required
                            />
                          </div>
                        </div>

                        <div className="space-y-2">
                          <Label htmlFor="signup-email" className="text-[#F4D03F]">Email *</Label>
                          <div className="relative">
                            <Mail className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-[#B8BCC8]" />
                            <Input
                              id="signup-email"
                              type="email"
                              placeholder="Enter your email"
                              value={signupData.email}
                              onChange={(e) => setSignupData(prev => ({ ...prev, email: e.target.value }))}
                              className="glassmorphism-panel border-[rgba(244,208,63,0.2)] bg-[rgba(26,29,41,0.4)] text-white placeholder:text-[#6B7280] focus:border-[#F4D03F] pl-10 h-12"
                              required
                            />
                          </div>
                        </div>

                        <div className="space-y-2">
                          <Label htmlFor="signup-password" className="text-[#F4D03F]">Password *</Label>
                          <div className="relative">
                            <Lock className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-[#B8BCC8]" />
                            <Input
                              id="signup-password"
                              type={showPassword ? 'text' : 'password'}
                              placeholder="Create a password"
                              value={signupData.password}
                              onChange={(e) => setSignupData(prev => ({ ...prev, password: e.target.value }))}
                              className="glassmorphism-panel border-[rgba(244,208,63,0.2)] bg-[rgba(26,29,41,0.4)] text-white placeholder:text-[#6B7280] focus:border-[#F4D03F] pl-10 pr-10 h-12"
                              required
                            />
                            <button
                              type="button"
                              onClick={() => setShowPassword(!showPassword)}
                              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-[#B8BCC8] hover:text-[#F4D03F]"
                            >
                              {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                            </button>
                          </div>
                          <p className="text-xs text-[#B8BCC8]">Must contain uppercase, lowercase, and a number</p>
                        </div>

                        <div className="space-y-2">
                          <Label htmlFor="confirmPassword" className="text-[#F4D03F]">Confirm Password *</Label>
                          <div className="relative">
                            <Lock className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-[#B8BCC8]" />
                            <Input
                              id="confirmPassword"
                              type={showConfirmPassword ? 'text' : 'password'}
                              placeholder="Confirm your password"
                              value={signupData.confirmPassword}
                              onChange={(e) => setSignupData(prev => ({ ...prev, confirmPassword: e.target.value }))}
                              className="glassmorphism-panel border-[rgba(244,208,63,0.2)] bg-[rgba(26,29,41,0.4)] text-white placeholder:text-[#6B7280] focus:border-[#F4D03F] pl-10 pr-10 h-12"
                              required
                            />
                            <button
                              type="button"
                              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-[#B8BCC8] hover:text-[#F4D03F]"
                            >
                              {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                            </button>
                          </div>
                        </div>

                        <div className="flex items-start space-x-2">
                          <Checkbox
                            id="acceptTerms"
                            checked={signupData.acceptTerms}
                            onCheckedChange={(checked) => {
                              const isChecked = checked === true;
                              setSignupData(prev => ({ ...prev, acceptTerms: isChecked }));
                            }}
                            className="border-[rgba(244,208,63,0.3)] data-[state=checked]:bg-[#F4D03F] data-[state=checked]:border-[#F4D03F] mt-0.5"
                          />
                          <Label htmlFor="acceptTerms" className="text-sm text-[#B8BCC8] leading-relaxed">
                            I accept the{' '}
                            <Button variant="link" className="text-[#F4D03F] hover:text-[#F7DC6F] p-0 h-auto text-sm">
                              Terms of Service
                            </Button>
                            {' '}and{' '}
                            <Button variant="link" className="text-[#F4D03F] hover:text-[#F7DC6F] p-0 h-auto text-sm">
                              Privacy Policy
                            </Button>
                          </Label>
                        </div>

                        <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                          <Button
                            type="submit"
                            disabled={isLoading || !signupData.acceptTerms}
                            className="w-full bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F] disabled:opacity-50 h-12"
                          >
                            {isLoading ? (
                              <div className="flex items-center space-x-2">
                                <Loader2 className="w-4 h-4 animate-spin" />
                                <span>Creating account...</span>
                              </div>
                            ) : (
                              <div className="flex items-center space-x-2">
                                <span>Create Account</span>
                                <CheckCircle className="w-4 h-4" />
                              </div>
                            )}
                          </Button>
                        </motion.div>
                      </form>
                    </TabsContent>
                  </motion.div>
                </AnimatePresence>
              </Tabs>

              <Separator className="my-6 bg-[rgba(244,208,63,0.2)]" />
              
              <div className="text-center">
                <p className="text-sm text-[#6B7280]">
                  Start your journey toward intentional living
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </motion.div>
    </div>
  );
}