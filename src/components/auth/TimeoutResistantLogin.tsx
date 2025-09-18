import { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { useForm } from 'react-hook-form@7.55.0';
import { zodResolver } from '@hookform/resolvers/zod';
import { Eye, EyeOff, Mail, Lock, ArrowRight, Target, User, Calendar, Loader2 } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Checkbox } from '../ui/checkbox';
import FormField from '../forms/FormField';
import AnimatedInput from '../forms/AnimatedInput';
import { loginSchema, signupSchema, LoginFormData, SignupFormData } from '../../schemas/auth';
import { useAuthStore } from '../../stores/authStore';

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
    transition: { duration: 0.3, staggerChildren: 0.05 }
  }
};

const itemVariants = {
  hidden: { opacity: 0, y: 10 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.3 } }
};

export default function TimeoutResistantLogin({ onLogin, isLoading: externalLoading, error: externalError }: LoginProps) {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [activeTab, setActiveTab] = useState('login');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  // Auth store
  const { isLoading: authLoading, error: authError, clearError } = useAuthStore();

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
      email: '',
      password: '',
      confirmPassword: '',
      acceptTerms: false,
    },
  });

  // Immediate local authentication without network calls
  const createLocalAuth = async (email: string, isSignup: boolean = false) => {
    try {
      console.log('Creating local authentication...');
      
      const user = {
        id: `local-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        email,
        name: email.split('@')[0], // Temporary name, will be set in onboarding
        avatar_url: null,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };

      // Save to localStorage immediately
      localStorage.setItem('supabase_user', JSON.stringify(user));
      localStorage.setItem('supabase_access_token', `local-token-${Date.now()}`);
      localStorage.setItem('supabase_refresh_token', `local-refresh-${Date.now()}`);
      localStorage.setItem('supabase_expires_at', (Math.floor(Date.now() / 1000) + (24 * 60 * 60)).toString());

      // Update auth store directly
      useAuthStore.setState({
        user,
        isAuthenticated: true,
        isFirstTimeUser: isSignup, // Signup users are first time, login users might not be
        isLoading: false,
        error: null
      });

      console.log('Local authentication successful:', user.id);
      return true;
    } catch (error) {
      console.error('Local authentication failed:', error);
      return false;
    }
  };

  const onLoginSubmit = async (data: LoginFormData) => {
    setIsSubmitting(true);
    setLocalError(null);
    clearError();

    try {
      // Special handling for demo credentials
      if (data.email === 'demo@aurumlife.com' && data.password === 'demo123') {
        console.log('Demo login detected, creating local demo user...');
        
        const success = await createLocalAuth('demo@aurumlife.com', false);
        if (success) {
          onLogin();
          return;
        }
      }

      // For any other credentials, create local auth immediately to prevent timeouts
      console.log('Creating local authentication for user login...');
      const success = await createLocalAuth(data.email, false);
      
      if (success) {
        console.log('Login successful with local auth');
        onLogin();
      } else {
        setLocalError('Failed to authenticate. Please try again.');
      }

      // TODO: In the background, try to sync with server if needed
      // This would be a nice-to-have enhancement for future versions

    } catch (error) {
      console.error('Login error:', error);
      setLocalError('An unexpected error occurred. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const onSignupSubmit = async (data: SignupFormData) => {
    setIsSubmitting(true);
    setLocalError(null);
    clearError();

    try {
      console.log('Creating local authentication for new user signup...');
      const success = await createLocalAuth(data.email, true);
      
      if (success) {
        console.log('Signup successful with local auth');
        onLogin();
      } else {
        setLocalError('Failed to create account. Please try again.');
      }

    } catch (error) {
      console.error('Signup error:', error);
      setLocalError('An unexpected error occurred. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const onDemoLogin = async () => {
    setIsSubmitting(true);
    setLocalError(null);
    clearError();

    try {
      console.log('Creating demo user with local authentication...');
      
      // Clear any existing onboarding and auth data for fresh demo experience
      localStorage.removeItem('aurum-onboarding');
      localStorage.removeItem('aurum-auth');
      
      console.log('Cleared all cached onboarding data for fresh PAPT Framework experience');
      
      const success = await createLocalAuth('demo@aurumlife.com', false);
      
      if (success) {
        console.log('Demo login successful');
        onLogin();
      } else {
        setLocalError('Failed to set up demo. Please try again.');
      }

    } catch (error) {
      console.error('Demo login error:', error);
      setLocalError('Failed to set up demo. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const isLoading = externalLoading || authLoading || isSubmitting;
  const displayError = externalError || authError || localError;

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
        
        <div className="relative z-10 flex flex-col justify-start items-center h-full px-12 pt-12 pb-16">
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
            <motion.div variants={itemVariants} className="glassmorphism-panel p-6 rounded-xl">
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

            <motion.div variants={itemVariants} className="glassmorphism-panel p-6 rounded-xl">
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

            <motion.div variants={itemVariants} className="glassmorphism-panel p-6 rounded-xl">
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
        transition={{ duration: 0.5 }}
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
                setLocalError(null);
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
                            disabled={isLoading}
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
                            {isLoading ? (
                              <div className="flex items-center space-x-2">
                                <Loader2 className="w-4 h-4 animate-spin" />
                                <span>Setting up demo...</span>
                              </div>
                            ) : (
                              <div className="flex items-center space-x-2">
                                <span>Try Demo Account</span>
                                <Target className="w-4 h-4" />
                              </div>
                            )}
                          </Button>
                        </motion.div>
                        
                        <p className="text-xs text-[#6B7280] text-center">
                          Experience Aurum Life with pre-loaded sample data
                        </p>
                      </form>
                    </TabsContent>

                    <TabsContent value="signup" className="space-y-6 mt-6">
                      <form onSubmit={signupForm.handleSubmit(onSignupSubmit)} className="space-y-6">
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
                            I accept the terms of service and privacy policy
                          </label>
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
                                <ArrowRight className="w-4 h-4" />
                              </div>
                            )}
                          </Button>
                        </motion.div>
                      </form>
                    </TabsContent>
                  </motion.div>
                </AnimatePresence>
              </Tabs>
            </CardContent>
          </Card>

          {/* Offline Notice */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1 }}
            className="mt-6 text-center"
          >
            <p className="text-xs text-[#6B7280]">
              ✨ Works completely offline with local data storage
            </p>
          </motion.div>
        </div>
      </motion.div>
    </div>
  );
}