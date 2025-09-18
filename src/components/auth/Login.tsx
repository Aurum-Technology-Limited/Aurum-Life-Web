import { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { useForm } from 'react-hook-form@7.55.0';
import { zodResolver } from '@hookform/resolvers/zod';
import { Eye, EyeOff, Mail, Lock, ArrowRight, Target, User, Calendar, Loader2 } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Separator } from '../ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Checkbox } from '../ui/checkbox';
import { Label } from '../ui/label';
import { Input } from '../ui/input';
import FormField from '../forms/FormField';
import AnimatedInput from '../forms/AnimatedInput';
import { loginSchema, signupSchema, LoginFormData, SignupFormData } from '../../schemas/auth';
import aurumLogo from 'figma:asset/a76e299ce637adb8c75472e2d4c5e50cfbb65bac.png';

interface LoginProps {
  onLogin: () => void;
  isLoading?: boolean;
  error?: string | null;
}

export default function Login({ onLogin, isLoading: externalLoading, error: externalError }: LoginProps) {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('login');
  const [loginData, setLoginData] = useState({
    email: '',
    password: ''
  });
  const [signupData, setSignupData] = useState({
    firstName: '',
    lastName: '',
    username: '',
    dateOfBirth: '',
    email: '',
    password: '',
    confirmPassword: ''
  });

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Use external loading state if provided
    if (externalLoading !== undefined) {
      onLogin();
    } else {
      setIsLoading(true);
      setTimeout(() => {
        setIsLoading(false);
        onLogin();
      }, 1500);
    }
  };

  const handleSignupSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    // Basic validation
    if (signupData.password !== signupData.confirmPassword) {
      alert('Passwords do not match');
      setIsLoading(false);
      return;
    }
    
    // Simulate account creation
    setTimeout(() => {
      setIsLoading(false);
      onLogin();
    }, 2000);
  };

  const handleLoginInputChange = (field: string, value: string) => {
    setLoginData(prev => ({ ...prev, [field]: value }));
  };

  const handleSignupInputChange = (field: string, value: string) => {
    setSignupData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="min-h-screen bg-[#0B0D14] dark flex items-center justify-center p-6">
      {/* Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#F4D03F] opacity-5 rounded-full blur-3xl"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-[#F4D03F] opacity-3 rounded-full blur-3xl"></div>
      </div>

      {/* Auth Card */}
      <Card className="glassmorphism-card border-0 w-full max-w-md relative z-10">
        <CardHeader className="text-center pb-6">
          {/* Logo */}
          <div className="flex justify-center mb-6">
            <div className="w-30 h-30 rounded-xl flex items-center justify-center">
              <img 
                src={aurumLogo} 
                alt="Aurum Life Logo" 
                className="w-24 h-24 object-contain"
              />
            </div>
          </div>
          
          <CardTitle className="text-2xl font-bold text-white mb-2">
            Aurum Life
          </CardTitle>
          <CardDescription className="text-[#B8BCC8] text-base">
            Transform your potential into gold
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-6">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-2 bg-[#1A1D29] border border-[rgba(244,208,63,0.2)]">
              <TabsTrigger 
                value="login" 
                className="text-[#B8BCC8] data-[state=active]:bg-[#F4D03F] data-[state=active]:text-[#0B0D14] data-[state=active]:font-medium"
              >
                Login
              </TabsTrigger>
              <TabsTrigger 
                value="signup" 
                className="text-[#B8BCC8] data-[state=active]:bg-[#F4D03F] data-[state=active]:text-[#0B0D14] data-[state=active]:font-medium"
              >
                Sign Up
              </TabsTrigger>
            </TabsList>

            <TabsContent value="login" className="space-y-6 mt-6">
              {/* Already have account link */}
              <div className="text-center mb-4">
                <p className="text-[#6B7280] text-sm">
                  Already have an account?{' '}
                  <Button
                    variant="link"
                    onClick={() => setActiveTab('signup')}
                    className="text-[#F4D03F] hover:text-[#F7DC6F] p-0 h-auto font-medium"
                  >
                    Sign in instead
                  </Button>
                </p>
              </div>

              <form onSubmit={handleLoginSubmit} className="space-y-4">
                {/* Email Field */}
                <div className="space-y-2">
                  <Label htmlFor="login-email" className="text-[#B8BCC8]">
                    Email Address
                  </Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-[#6B7280]" />
                    <Input
                      id="login-email"
                      type="email"
                      placeholder="Enter your email"
                      value={loginData.email}
                      onChange={(e) => handleLoginInputChange('email', e.target.value)}
                      className="pl-10 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white placeholder:text-[#6B7280] focus:border-[#F4D03F] focus:ring-[#F4D03F]"
                      required
                    />
                  </div>
                </div>

                {/* Password Field */}
                <div className="space-y-2">
                  <Label htmlFor="login-password" className="text-[#B8BCC8]">
                    Password
                  </Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-[#6B7280]" />
                    <Input
                      id="login-password"
                      type={showPassword ? 'text' : 'password'}
                      placeholder="Enter your password"
                      value={loginData.password}
                      onChange={(e) => handleLoginInputChange('password', e.target.value)}
                      className="pl-10 pr-10 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white placeholder:text-[#6B7280] focus:border-[#F4D03F] focus:ring-[#F4D03F]"
                      required
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      className="absolute right-0 top-0 h-full px-3 text-[#6B7280] hover:text-[#F4D03F]"
                      onClick={() => setShowPassword(!showPassword)}
                      tabIndex={-1}
                    >
                      {showPassword ? (
                        <EyeOff className="w-4 h-4" />
                      ) : (
                        <Eye className="w-4 h-4" />
                      )}
                    </Button>
                  </div>
                </div>

                {/* Remember & Forgot */}
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="remember"
                      className="w-4 h-4 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] rounded focus:ring-[#F4D03F] focus:ring-2"
                    />
                    <Label htmlFor="remember" className="text-[#B8BCC8] cursor-pointer">
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

                {/* Login Button */}
                {/* Error Display */}
                {externalError && (
                  <div className="bg-[rgba(239,68,68,0.1)] border border-[rgba(239,68,68,0.2)] rounded-lg p-3">
                    <p className="text-[#EF4444] text-sm">{externalError}</p>
                  </div>
                )}

                <Button
                  type="submit"
                  disabled={(externalLoading ?? isLoading) || !loginData.email || !loginData.password}
                  className="w-full bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F] disabled:opacity-50 disabled:cursor-not-allowed h-12"
                >
                  {(externalLoading ?? (isLoading && activeTab === 'login')) ? (
                    <div className="flex items-center space-x-2">
                      <div className="w-4 h-4 border-2 border-[#0B0D14] border-t-transparent rounded-full animate-spin"></div>
                      <span>Signing in...</span>
                    </div>
                  ) : (
                    <div className="flex items-center space-x-2">
                      <span>Sign In</span>
                      <ArrowRight className="w-4 h-4" />
                    </div>
                  )}
                </Button>
              </form>

              <div className="space-y-3 mt-6">
                <div className="relative">
                  <Separator className="bg-[rgba(244,208,63,0.1)]" />
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="bg-[#1A1D29] px-4 text-[#6B7280] text-sm">Or continue with</span>
                  </div>
                </div>

                <Button
                  variant="outline"
                  className="w-full border-[rgba(244,208,63,0.2)] text-[#B8BCC8] hover:bg-[rgba(244,208,63,0.05)] hover:border-[rgba(244,208,63,0.3)]"
                >
                  <svg className="w-4 h-4 mr-2" viewBox="0 0 24 24">
                    <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                  </svg>
                  Sign in with Google
                </Button>
              </div>
            </TabsContent>

            <TabsContent value="signup" className="space-y-6 mt-6">
              {/* Already have account link */}
              <div className="text-center mb-4">
                <p className="text-[#6B7280] text-sm">
                  Already have an account?{' '}
                  <Button
                    variant="link"
                    onClick={() => setActiveTab('login')}
                    className="text-[#F4D03F] hover:text-[#F7DC6F] p-0 h-auto font-medium"
                  >
                    Sign in instead
                  </Button>
                </p>
              </div>

              <form onSubmit={handleSignupSubmit} className="space-y-4">
                {/* Name Fields */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="firstName" className="text-[#B8BCC8]">
                      First Name
                    </Label>
                    <Input
                      id="firstName"
                      type="text"
                      placeholder="John"
                      value={signupData.firstName}
                      onChange={(e) => handleSignupInputChange('firstName', e.target.value)}
                      className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white placeholder:text-[#6B7280] focus:border-[#F4D03F] focus:ring-[#F4D03F]"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="lastName" className="text-[#B8BCC8]">
                      Last Name
                    </Label>
                    <Input
                      id="lastName"
                      type="text"
                      placeholder="Doe"
                      value={signupData.lastName}
                      onChange={(e) => handleSignupInputChange('lastName', e.target.value)}
                      className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white placeholder:text-[#6B7280] focus:border-[#F4D03F] focus:ring-[#F4D03F]"
                      required
                    />
                  </div>
                </div>

                {/* Username Field */}
                <div className="space-y-2">
                  <Label htmlFor="username" className="text-[#B8BCC8]">
                    Username
                  </Label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-[#6B7280]" />
                    <Input
                      id="username"
                      type="text"
                      placeholder="johndoe (optional)"
                      value={signupData.username}
                      onChange={(e) => handleSignupInputChange('username', e.target.value)}
                      className="pl-10 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white placeholder:text-[#6B7280] focus:border-[#F4D03F] focus:ring-[#F4D03F]"
                    />
                  </div>
                </div>

                {/* Date of Birth */}
                <div className="space-y-2">
                  <Label htmlFor="dateOfBirth" className="text-[#B8BCC8]">
                    Date of Birth
                  </Label>
                  <div className="relative">
                    <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-[#6B7280]" />
                    <Input
                      id="dateOfBirth"
                      type="date"
                      value={signupData.dateOfBirth}
                      onChange={(e) => handleSignupInputChange('dateOfBirth', e.target.value)}
                      className="pl-10 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white placeholder:text-[#6B7280] focus:border-[#F4D03F] focus:ring-[#F4D03F] [color-scheme:dark]"
                      required
                    />
                  </div>
                </div>

                {/* Email Field */}
                <div className="space-y-2">
                  <Label htmlFor="signup-email" className="text-[#B8BCC8]">
                    Email Address
                  </Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-[#6B7280]" />
                    <Input
                      id="signup-email"
                      type="email"
                      placeholder="Enter your email"
                      value={signupData.email}
                      onChange={(e) => handleSignupInputChange('email', e.target.value)}
                      className="pl-10 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white placeholder:text-[#6B7280] focus:border-[#F4D03F] focus:ring-[#F4D03F]"
                      required
                    />
                  </div>
                </div>

                {/* Password Field */}
                <div className="space-y-2">
                  <Label htmlFor="signup-password" className="text-[#B8BCC8]">
                    Password
                  </Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-[#6B7280]" />
                    <Input
                      id="signup-password"
                      type={showPassword ? 'text' : 'password'}
                      placeholder="Enter your password"
                      value={signupData.password}
                      onChange={(e) => handleSignupInputChange('password', e.target.value)}
                      className="pl-10 pr-10 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white placeholder:text-[#6B7280] focus:border-[#F4D03F] focus:ring-[#F4D03F]"
                      required
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      className="absolute right-0 top-0 h-full px-3 text-[#6B7280] hover:text-[#F4D03F]"
                      onClick={() => setShowPassword(!showPassword)}
                      tabIndex={-1}
                    >
                      {showPassword ? (
                        <EyeOff className="w-4 h-4" />
                      ) : (
                        <Eye className="w-4 h-4" />
                      )}
                    </Button>
                  </div>
                </div>

                {/* Confirm Password Field */}
                <div className="space-y-2">
                  <Label htmlFor="confirmPassword" className="text-[#B8BCC8]">
                    Confirm Password
                  </Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-[#6B7280]" />
                    <Input
                      id="confirmPassword"
                      type={showConfirmPassword ? 'text' : 'password'}
                      placeholder="Confirm your password"
                      value={signupData.confirmPassword}
                      onChange={(e) => handleSignupInputChange('confirmPassword', e.target.value)}
                      className="pl-10 pr-10 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white placeholder:text-[#6B7280] focus:border-[#F4D03F] focus:ring-[#F4D03F]"
                      required
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      className="absolute right-0 top-0 h-full px-3 text-[#6B7280] hover:text-[#F4D03F]"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      tabIndex={-1}
                    >
                      {showConfirmPassword ? (
                        <EyeOff className="w-4 h-4" />
                      ) : (
                        <Eye className="w-4 h-4" />
                      )}
                    </Button>
                  </div>
                </div>

                {/* Create Account Button */}
                <Button
                  type="submit"
                  disabled={isLoading || !signupData.firstName || !signupData.lastName || !signupData.email || !signupData.password || !signupData.confirmPassword}
                  className="w-full bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F] disabled:opacity-50 disabled:cursor-not-allowed h-12"
                >
                  {isLoading && activeTab === 'signup' ? (
                    <div className="flex items-center space-x-2">
                      <div className="w-4 h-4 border-2 border-[#0B0D14] border-t-transparent rounded-full animate-spin"></div>
                      <span>Creating Account...</span>
                    </div>
                  ) : (
                    'Create Account'
                  )}
                </Button>
              </form>

              <div className="space-y-3 mt-6">
                <div className="relative">
                  <Separator className="bg-[rgba(244,208,63,0.1)]" />
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="bg-[#1A1D29] px-4 text-[#6B7280] text-sm">Or continue with</span>
                  </div>
                </div>

                <Button
                  variant="outline"
                  className="w-full border-[rgba(244,208,63,0.2)] text-[#B8BCC8] hover:bg-[rgba(244,208,63,0.05)] hover:border-[rgba(244,208,63,0.3)]"
                >
                  <svg className="w-4 h-4 mr-2" viewBox="0 0 24 24">
                    <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                  </svg>
                  Sign up with Google
                </Button>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Feature Highlights */}
      <div className="absolute bottom-8 left-8 right-8 flex justify-center">
        <div className="glassmorphism-panel px-6 py-3 max-w-2xl">
          <div className="flex items-center justify-center space-x-8 text-sm">
            <div className="flex items-center space-x-2 text-[#B8BCC8]">
              <Target className="w-4 h-4 text-[#F4D03F]" />
              <span>Strategic Alignment</span>
            </div>
            <div className="flex items-center space-x-2 text-[#B8BCC8]">
              <div className="w-4 h-4 rounded bg-[#F4D03F]"></div>
              <span>Premium Experience</span>
            </div>
            <div className="flex items-center space-x-2 text-[#B8BCC8]">
              <div className="w-4 h-4 rounded-full bg-gradient-to-r from-[#F4D03F] to-[#F7DC6F]"></div>
              <span>Intentional Living</span>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Welcome Message */}
      {activeTab === 'signup' && (
        <div className="absolute bottom-32 left-8 right-8 flex justify-center">
          <p className="text-[#6B7280] text-sm">
            Welcome to your personal growth journey
          </p>
        </div>
      )}
    </div>
  );
}