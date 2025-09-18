import { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { useForm } from 'react-hook-form@7.55.0';
import { zodResolver } from '@hookform/resolvers/zod';
import { Eye, EyeOff, Mail, Lock, ArrowRight, Target, User, Calendar, Loader2, CheckCircle } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Separator } from '../ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Checkbox } from '../ui/checkbox';
import FormField from '../forms/FormField';
import AnimatedInput from '../forms/AnimatedInput';
import { loginSchema, signupSchema, LoginFormData, SignupFormData } from '../../schemas/auth';
import { useAuthStore } from '../../stores/authStore';
import { projectId, publicAnonKey } from '../../utils/supabase/info';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '../ui/dialog';
import TermsOfService from '../legal/TermsOfService';
import PrivacyPolicy from '../legal/PrivacyPolicy';


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

export default function EnhancedLogin({ onLogin, isLoading: externalLoading, error: externalError }: LoginProps) {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [activeTab, setActiveTab] = useState('login');
  const [isDemoLoading, setIsDemoLoading] = useState(false);
  const [switchedFromSignup, setSwitchedFromSignup] = useState(false);
  const [showTerms, setShowTerms] = useState(false);
  const [showPrivacy, setShowPrivacy] = useState(false);

  // Auth store
  const { signIn, signUp, demoLogin, isLoading: authLoading, error: authError, clearError } = useAuthStore();

  // Login form
  const loginForm = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
      rememberMe: false,
    },
  });

  // Signup form
  const signupForm = useForm<SignupFormData>({
    resolver: zodResolver(signupSchema),
    defaultValues: {
      name: '',
      email: '',
      password: '',
      confirmPassword: '',
      acceptTerms: false,
    },
  });

  const onLoginSubmit = async (data: LoginFormData) => {
    clearError();
    await signIn({
      email: data.email,
      password: data.password,
    });
    onLogin();
  };

  const onSignupSubmit = async (data: SignupFormData) => {
    clearError();
    const result = await signUp({
      email: data.email,
      password: data.password,
      name: data.name,
    });
    
    // Check if signup was successful (no error in auth store)
    if (!authError) {
      onLogin();
    }
  };

  const onDemoLogin = async () => {
    clearError();
    setIsDemoLoading(true);
    
    try {
      console.log('EnhancedLogin: Starting demo login...');
      
      // Try demo login with timeout
      const demoLoginPromise = demoLogin();
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Demo login timed out')), 2000);
      });
      
      await Promise.race([demoLoginPromise, timeoutPromise]);
      
      // Small delay to ensure state is updated
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // Check auth state directly after demoLogin completes
      const currentAuthState = useAuthStore.getState();
      if (currentAuthState.isAuthenticated && !currentAuthState.error) {
        console.log('EnhancedLogin: Demo login successful, calling onLogin');
        onLogin();
      } else if (currentAuthState.error) {
        console.error('EnhancedLogin: Demo login failed with error:', currentAuthState.error);
      } else {
        console.warn('EnhancedLogin: Demo login completed but user not authenticated');
      }
      
    } catch (error) {
      console.error('EnhancedLogin: Demo login exception:', error);
      
      // Final fallback: Direct local authentication
      console.log('EnhancedLogin: Attempting direct local demo auth...');
      try {
        const directDemoUser = {
          id: 'direct-demo-' + Date.now(),
          email: 'demo@aurumlife.com',
          name: 'Demo User',
          avatar_url: null,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        };
        
        // Directly update auth store
        useAuthStore.setState({
          user: directDemoUser,
          isAuthenticated: true,
          isFirstTimeUser: true,
          isLoading: false,
          error: null
        });
        
        console.log('EnhancedLogin: Direct demo auth successful');
        onLogin();
      } catch (fallbackError) {
        console.error('EnhancedLogin: Even fallback demo auth failed:', fallbackError);
      }
    } finally {
      setIsDemoLoading(false);
    }
  };

  const isLoading = externalLoading || authLoading || loginForm.formState.isSubmitting || signupForm.formState.isSubmitting || isDemoLoading;
  const displayError = externalError || authError;

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
        
        <div className="relative z-10 flex flex-col justify-center items-center h-full px-12 py-16">
          <motion.div variants={itemVariants} className="mb-12 text-center">
            <div className="flex flex-col items-center space-y-6 mb-8">
              <img src={aurumLogo} alt="Aurum Life" className="w-60 h-60" />
              <h1 className="aurum-text-gradient text-6xl font-bold">Aurum Life</h1>
            </div>
            <p className="text-xl text-[#B8BCC8] leading-relaxed text-center max-w-md mx-auto">
              Transform your daily actions into strategic steps toward your life vision
            </p>
          </motion.div>

          <motion.div variants={itemVariants} className="space-y-8 w-full max-w-md">
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
              <CardTitle className="text-white hidden lg:block">
                {activeTab === 'login' ? 'Welcome Back' : 'Get Started'}
              </CardTitle>
              <CardDescription className="text-[#B8BCC8]">
                {activeTab === 'login' 
                  ? 'Sign in to continue your journey' 
                  : 'Start your personal operating system'
                }
              </CardDescription>
            </CardHeader>

            <CardContent>
              <Tabs value={activeTab} onValueChange={(value) => {
                setActiveTab(value);
                setSwitchedFromSignup(false);
                clearError();
              }} className="w-full">
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
                      {switchedFromSignup && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          className="bg-[rgba(244,208,63,0.1)] border border-[rgba(244,208,63,0.2)] rounded-lg p-3 mb-4"
                        >
                          <p className="text-[#F4D03F] text-sm">
                            An account with this email already exists. Please sign in with your password.
                          </p>
                        </motion.div>
                      )}
                      <form onSubmit={loginForm.handleSubmit(onLoginSubmit)} className="space-y-6">
                        <FormField
                          label="Email"
                          error={loginForm.formState.errors.email}
                          required
                        >
                          <AnimatedInput
                            {...loginForm.register('email')}
                            type="email"
                            placeholder="Enter your email"
                            icon={<Mail className="w-4 h-4" />}
                            error={!!loginForm.formState.errors.email}
                            autoComplete="email"
                          />
                        </FormField>

                        <FormField
                          label="Password"
                          error={loginForm.formState.errors.password}
                          required
                        >
                          <AnimatedInput
                            {...loginForm.register('password')}
                            type={showPassword ? 'text' : 'password'}
                            placeholder="Enter your password"
                            icon={<Lock className="w-4 h-4" />}
                            rightIcon={
                              <motion.button
                                type="button"
                                onClick={() => setShowPassword(!showPassword)}
                                className="text-[#B8BCC8] hover:text-[#F4D03F] transition-colors"
                                whileHover={{ scale: 1.1 }}
                                whileTap={{ scale: 0.95 }}
                              >
                                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                              </motion.button>
                            }
                            error={!!loginForm.formState.errors.password}
                            autoComplete="current-password"
                          />
                        </FormField>

                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <Checkbox
                              id="rememberMe"
                              checked={loginForm.watch('rememberMe')}
                              onCheckedChange={(checked) => loginForm.setValue('rememberMe', checked as boolean)}
                              className="border-[rgba(244,208,63,0.3)] data-[state=checked]:bg-[#F4D03F] data-[state=checked]:border-[#F4D03F]"
                            />
                            <label htmlFor="rememberMe" className="text-sm text-[#B8BCC8]">
                              Remember me
                            </label>
                          </div>
                          <Button
                            type="button"
                            variant="link"
                            className="text-[#F4D03F] hover:text-[#F7DC6F] p-0 h-auto"
                          >
                            Forgot password?
                          </Button>
                        </div>

                        {displayError && (
                          <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            className="bg-[rgba(239,68,68,0.1)] border border-[rgba(239,68,68,0.2)] rounded-lg p-3"
                          >
                            <p className="text-[#EF4444] text-sm">{displayError}</p>
                          </motion.div>
                        )}

                        <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                          <Button
                            type="submit"
                            disabled={isLoading || !loginForm.formState.isValid}
                            className="w-full bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F] disabled:opacity-50 disabled:cursor-not-allowed h-12"
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

                        <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                          <Button
                            type="button"
                            onClick={onDemoLogin}
                            disabled={isLoading}
                            variant="outline"
                            className="w-full border-[rgba(244,208,63,0.3)] text-[#F4D03F] hover:bg-[rgba(244,208,63,0.1)] hover:border-[#F4D03F] disabled:opacity-50 disabled:cursor-not-allowed h-12 mt-3"
                          >
                            {isDemoLoading ? (
                              <div className="flex items-center space-x-2">
                                <Loader2 className="w-4 h-4 animate-spin" />
                                <span>Setting up demo...</span>
                              </div>
                            ) : isLoading ? (
                              <div className="flex items-center space-x-2">
                                <Loader2 className="w-4 h-4 animate-spin" />
                                <span>Loading...</span>
                              </div>
                            ) : (
                              <div className="flex items-center space-x-2">
                                <span>Try Demo Account</span>
                                <Target className="w-4 h-4" />
                              </div>
                            )}
                          </Button>

                          {/* Fallback manual demo login */}
                          {displayError && (displayError.includes('Demo login failed') || displayError.includes('timed out')) && (
                            <motion.div
                              initial={{ opacity: 0, height: 0 }}
                              animate={{ opacity: 1, height: 'auto' }}
                              className="mt-3"
                            >
                              <Button
                                type="button"
                                onClick={async () => {
                                  console.log('Manual fallback demo login initiated...');
                                  clearError();
                                  
                                  try {
                                    // Direct local demo user creation
                                    const localDemoUser = {
                                      id: 'local-demo-' + Date.now(),
                                      email: 'demo@aurumlife.com',
                                      name: 'Demo User',
                                      avatar_url: null,
                                      created_at: new Date().toISOString(),
                                      updated_at: new Date().toISOString()
                                    };
                                    
                                    // Save to localStorage
                                    localStorage.setItem('supabase_user', JSON.stringify(localDemoUser));
                                    localStorage.setItem('supabase_access_token', 'local-demo-token-' + Date.now());
                                    localStorage.removeItem('aurum-onboarding'); // Fresh start
                                    
                                    // Update auth store directly
                                    useAuthStore.setState({
                                      user: localDemoUser,
                                      isAuthenticated: true,
                                      isFirstTimeUser: true,
                                      isLoading: false,
                                      error: null
                                    });
                                    
                                    console.log('Manual demo login successful');
                                    onLogin();
                                  } catch (error) {
                                    console.error('Manual demo login failed:', error);
                                  }
                                }}
                                disabled={isLoading}
                                variant="outline"
                                className="w-full border-[rgba(59,130,246,0.3)] text-[#3B82F6] hover:bg-[rgba(59,130,246,0.1)] hover:border-[#3B82F6] disabled:opacity-50 disabled:cursor-not-allowed h-10 text-sm"
                              >
                                Create Local Demo
                              </Button>
                              <p className="text-xs text-[#6B7280] text-center mt-1">
                                Works completely offline with sample data
                              </p>
                            </motion.div>
                          )}
                        </motion.div>
                        
                        <p className="text-xs text-[#6B7280] text-center mt-2">
                          Experience Aurum Life with pre-loaded sample data
                        </p>
                      </form>
                    </TabsContent>

                    <TabsContent value="signup" className="space-y-6 mt-6">
                      <form onSubmit={signupForm.handleSubmit(onSignupSubmit)} className="space-y-6">
                        <FormField
                          label="Full Name"
                          error={signupForm.formState.errors.name}
                          required
                        >
                          <AnimatedInput
                            {...signupForm.register('name')}
                            placeholder="Enter your full name"
                            icon={<User className="w-4 h-4" />}
                            error={!!signupForm.formState.errors.name}
                            autoComplete="name"
                          />
                        </FormField>

                        <FormField
                          label="Email"
                          error={signupForm.formState.errors.email}
                          required
                        >
                          <AnimatedInput
                            {...signupForm.register('email')}
                            type="email"
                            placeholder="Enter your email"
                            icon={<Mail className="w-4 h-4" />}
                            error={!!signupForm.formState.errors.email}
                            autoComplete="email"
                          />
                        </FormField>

                        <FormField
                          label="Password"
                          error={signupForm.formState.errors.password}
                          required
                          description="Must contain uppercase, lowercase, and a number"
                        >
                          <AnimatedInput
                            {...signupForm.register('password')}
                            type={showPassword ? 'text' : 'password'}
                            placeholder="Create a password"
                            icon={<Lock className="w-4 h-4" />}
                            rightIcon={
                              <motion.button
                                type="button"
                                onClick={() => setShowPassword(!showPassword)}
                                className="text-[#B8BCC8] hover:text-[#F4D03F] transition-colors"
                                whileHover={{ scale: 1.1 }}
                                whileTap={{ scale: 0.95 }}
                              >
                                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                              </motion.button>
                            }
                            error={!!signupForm.formState.errors.password}
                            autoComplete="new-password"
                          />
                        </FormField>

                        <FormField
                          label="Confirm Password"
                          error={signupForm.formState.errors.confirmPassword}
                          required
                        >
                          <AnimatedInput
                            {...signupForm.register('confirmPassword')}
                            type={showConfirmPassword ? 'text' : 'password'}
                            placeholder="Confirm your password"
                            icon={<Lock className="w-4 h-4" />}
                            rightIcon={
                              <motion.button
                                type="button"
                                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                                className="text-[#B8BCC8] hover:text-[#F4D03F] transition-colors"
                                whileHover={{ scale: 1.1 }}
                                whileTap={{ scale: 0.95 }}
                              >
                                {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                              </motion.button>
                            }
                            error={!!signupForm.formState.errors.confirmPassword}
                            autoComplete="new-password"
                          />
                        </FormField>

                        <div className="flex items-start space-x-2">
                          <Checkbox
                            id="acceptTerms"
                            checked={signupForm.watch('acceptTerms')}
                            onCheckedChange={(checked) => signupForm.setValue('acceptTerms', checked as boolean)}
                            className="border-[rgba(244,208,63,0.3)] data-[state=checked]:bg-[#F4D03F] data-[state=checked]:border-[#F4D03F] mt-0.5"
                          />
                          <label htmlFor="acceptTerms" className="text-sm text-[#B8BCC8] leading-relaxed">
                            I accept the{' '}
                            <Button 
                              type="button"
                              variant="link" 
                              onClick={() => setShowTerms(true)}
                              className="text-[#F4D03F] hover:text-[#F7DC6F] p-0 h-auto text-sm"
                            >
                              Terms of Service
                            </Button>
                            {' '}and{' '}
                            <Button 
                              type="button"
                              variant="link" 
                              onClick={() => setShowPrivacy(true)}
                              className="text-[#F4D03F] hover:text-[#F7DC6F] p-0 h-auto text-sm"
                            >
                              Privacy Policy
                            </Button>
                          </label>
                        </div>

                        {signupForm.formState.errors.acceptTerms && (
                          <p className="text-sm text-[#EF4444]">
                            {signupForm.formState.errors.acceptTerms.message}
                          </p>
                        )}

                        {displayError && (
                          <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            className="bg-[rgba(239,68,68,0.1)] border border-[rgba(239,68,68,0.2)] rounded-lg p-3"
                          >
                            <p className="text-[#EF4444] text-sm">{displayError}</p>
                            {displayError.includes('already exists') && (
                              <motion.div className="mt-2">
                                <Button
                                  type="button"
                                  variant="link"
                                  onClick={() => {
                                    // Pre-fill the email in login form
                                    const currentEmail = signupForm.getValues('email');
                                    if (currentEmail) {
                                      loginForm.setValue('email', currentEmail);
                                    }
                                    setActiveTab('login');
                                    setSwitchedFromSignup(true);
                                    clearError();
                                  }}
                                  className="text-[#F4D03F] hover:text-[#F7DC6F] p-0 h-auto text-sm"
                                >
                                  Sign in instead →
                                </Button>
                              </motion.div>
                            )}
                          </motion.div>
                        )}

                        <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                          <Button
                            type="submit"
                            disabled={isLoading || !signupForm.formState.isValid}
                            className="w-full bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F] disabled:opacity-50 disabled:cursor-not-allowed h-12"
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

              <div className="text-center mt-6">
                <p className="text-sm text-[#6B7280]">
                  Start your journey toward intentional living
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </motion.div>

      {/* Terms of Service Modal */}
      <Dialog open={showTerms} onOpenChange={setShowTerms}>
        <DialogContent className="glassmorphism-card border-0 bg-card text-card-foreground max-w-4xl">
          <DialogHeader>
            <DialogTitle className="text-primary">Terms of Service</DialogTitle>
            <DialogDescription>
              Review the terms and conditions for using Aurum Life
            </DialogDescription>
          </DialogHeader>
          <TermsOfService />
        </DialogContent>
      </Dialog>

      {/* Privacy Policy Modal */}
      <Dialog open={showPrivacy} onOpenChange={setShowPrivacy}>
        <DialogContent className="glassmorphism-card border-0 bg-card text-card-foreground max-w-4xl">
          <DialogHeader>
            <DialogTitle className="text-primary">Privacy Policy</DialogTitle>
            <DialogDescription>
              Learn how we collect, use, and protect your personal information
            </DialogDescription>
          </DialogHeader>
          <PrivacyPolicy />
        </DialogContent>
      </Dialog>
    </div>
  );
}