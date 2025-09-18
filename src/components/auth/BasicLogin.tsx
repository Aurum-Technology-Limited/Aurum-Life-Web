import { useState } from 'react';
import { Eye, EyeOff, Mail, Lock, ArrowRight, Target, User, Calendar, Loader2 } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import aurumLogo from 'figma:asset/a76e299ce637adb8c75472e2d4c5e50cfbb65bac.png';

interface LoginProps {
  onSignUp: (data: { email: string; password: string; name: string }) => Promise<{ success: boolean; error?: string }>;
  onSignIn: (data: { email: string; password: string }) => Promise<{ success: boolean; error?: string }>;
  isLoading?: boolean;
  error?: string | null;
}

export default function BasicLogin({ onSignUp, onSignIn, isLoading: externalLoading, error: externalError }: LoginProps) {
  const [showPassword, setShowPassword] = useState(false);
  const [activeTab, setActiveTab] = useState('login');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  
  // Simple form states
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setFormError(null);
    
    try {
      if (activeTab === 'login') {
        const result = await onSignIn({ email, password });
        if (!result.success && result.error) {
          setFormError(result.error);
        }
      } else {
        if (password !== confirmPassword) {
          setFormError('Passwords do not match');
          return;
        }
        if (password.length < 6) {
          setFormError('Password must be at least 6 characters long');
          return;
        }
        const result = await onSignUp({ email, password, name });
        if (!result.success && result.error) {
          setFormError(result.error);
        }
      }
    } catch (error) {
      console.error('Auth error:', error);
      setFormError('An unexpected error occurred. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const isLoading = externalLoading || isSubmitting;

  return (
    <div className="min-h-screen bg-[#0B0D14] flex">
      {/* Left Panel - Welcome & Features */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-[#1A1D29] via-[#0B0D14] to-[#1A1D29]" />
        <div className="absolute inset-0 opacity-20" style={{
          backgroundImage: `radial-gradient(circle at 25% 25%, rgba(244, 208, 63, 0.1) 0%, transparent 50%), 
                           radial-gradient(circle at 75% 75%, rgba(244, 208, 63, 0.05) 0%, transparent 50%)`
        }} />
        
        <div className="relative z-10 flex flex-col justify-center px-12 py-16">
          <div className="mb-12">
            <div className="flex items-center space-x-3 mb-6">
              <img src={aurumLogo} alt="Aurum Life" className="w-12 h-12" />
              <h1 className="aurum-text-gradient">Aurum Life</h1>
            </div>
            <p className="text-xl text-[#B8BCC8] leading-relaxed">
              Transform your daily actions into strategic steps toward your life vision
            </p>
          </div>

          <div className="space-y-8">
            <div className="glassmorphism-panel p-6 rounded-xl">
              <div className="flex items-start space-x-4">
                <Target className="w-6 h-6 text-[#F4D03F] flex-shrink-0" />
                <div>
                  <h3 className="text-white mb-2">Strategic Hierarchy</h3>
                  <p className="text-[#B8BCC8] text-sm">
                    Align every task with your life pillars through Areas → Projects → Tasks
                  </p>
                </div>
              </div>
            </div>

            <div className="glassmorphism-panel p-6 rounded-xl">
              <div className="flex items-start space-x-4">
                <Calendar className="w-6 h-6 text-[#F4D03F] flex-shrink-0" />
                <div>
                  <h3 className="text-white mb-2">Daily Alignment</h3>
                  <p className="text-[#B8BCC8] text-sm">
                    See how today's work connects to your bigger picture and long-term goals
                  </p>
                </div>
              </div>
            </div>

            <div className="glassmorphism-panel p-6 rounded-xl">
              <div className="flex items-start space-x-4">
                <User className="w-6 h-6 text-[#F4D03F] flex-shrink-0" />
                <div>
                  <h3 className="text-white mb-2">Personal Operating System</h3>
                  <p className="text-[#B8BCC8] text-sm">
                    A complete system for managing your life with intention and purpose
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Right Panel - Auth Forms */}
      <div className="flex-1 flex items-center justify-center p-8">
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

                <TabsContent value="login" className="space-y-6 mt-6">
                  <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="space-y-2">
                      <Label htmlFor="email" className="text-[#F4D03F]">Email</Label>
                      <div className="relative">
                        <Mail className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-[#B8BCC8]" />
                        <Input
                          id="email"
                          type="email"
                          placeholder="Enter your email"
                          value={email}
                          onChange={(e) => setEmail(e.target.value)}
                          className="glassmorphism-panel border-[rgba(244,208,63,0.2)] bg-[rgba(26,29,41,0.4)] text-white placeholder:text-[#6B7280] focus:border-[#F4D03F] pl-10 h-12"
                          required
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="password" className="text-[#F4D03F]">Password</Label>
                      <div className="relative">
                        <Lock className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-[#B8BCC8]" />
                        <Input
                          id="password"
                          type={showPassword ? 'text' : 'password'}
                          placeholder="Enter your password"
                          value={password}
                          onChange={(e) => setPassword(e.target.value)}
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

                    {(externalError || formError) && (
                      <div className="bg-[rgba(239,68,68,0.1)] border border-[rgba(239,68,68,0.2)] rounded-lg p-3">
                        <p className="text-[#EF4444] text-sm">{externalError || formError}</p>
                      </div>
                    )}

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
                  </form>
                </TabsContent>

                <TabsContent value="signup" className="space-y-6 mt-6">
                  <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="space-y-2">
                      <Label htmlFor="name" className="text-[#F4D03F]">Full Name</Label>
                      <div className="relative">
                        <User className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-[#B8BCC8]" />
                        <Input
                          id="name"
                          placeholder="Enter your full name"
                          value={name}
                          onChange={(e) => setName(e.target.value)}
                          className="glassmorphism-panel border-[rgba(244,208,63,0.2)] bg-[rgba(26,29,41,0.4)] text-white placeholder:text-[#6B7280] focus:border-[#F4D03F] pl-10 h-12"
                          required
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="signup-email" className="text-[#F4D03F]">Email</Label>
                      <div className="relative">
                        <Mail className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-[#B8BCC8]" />
                        <Input
                          id="signup-email"
                          type="email"
                          placeholder="Enter your email"
                          value={email}
                          onChange={(e) => setEmail(e.target.value)}
                          className="glassmorphism-panel border-[rgba(244,208,63,0.2)] bg-[rgba(26,29,41,0.4)] text-white placeholder:text-[#6B7280] focus:border-[#F4D03F] pl-10 h-12"
                          required
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="signup-password" className="text-[#F4D03F]">Password</Label>
                      <div className="relative">
                        <Lock className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-[#B8BCC8]" />
                        <Input
                          id="signup-password"
                          type={showPassword ? 'text' : 'password'}
                          placeholder="Create a password"
                          value={password}
                          onChange={(e) => setPassword(e.target.value)}
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

                    <div className="space-y-2">
                      <Label htmlFor="confirmPassword" className="text-[#F4D03F]">Confirm Password</Label>
                      <div className="relative">
                        <Lock className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-[#B8BCC8]" />
                        <Input
                          id="confirmPassword"
                          type="password"
                          placeholder="Confirm your password"
                          value={confirmPassword}
                          onChange={(e) => setConfirmPassword(e.target.value)}
                          className="glassmorphism-panel border-[rgba(244,208,63,0.2)] bg-[rgba(26,29,41,0.4)] text-white placeholder:text-[#6B7280] focus:border-[#F4D03F] pl-10 h-12"
                          required
                        />
                      </div>
                    </div>

                    {(externalError || formError) && (
                      <div className="bg-[rgba(239,68,68,0.1)] border border-[rgba(239,68,68,0.2)] rounded-lg p-3">
                        <p className="text-[#EF4444] text-sm">{externalError || formError}</p>
                      </div>
                    )}

                    <Button
                      type="submit"
                      disabled={isLoading}
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
                          <ArrowRight className="w-4 h-4" />
                        </div>
                      )}
                    </Button>
                  </form>
                </TabsContent>
              </Tabs>

              <div className="mt-6 text-center space-y-3">
                <p className="text-sm text-[#6B7280]">
                  Start your journey toward intentional living
                </p>
                <div className="pt-3 border-t border-[rgba(244,208,63,0.1)]">
                  <p className="text-xs text-[#6B7280] mb-2">Quick Demo Access:</p>
                  <button
                    type="button"
                    onClick={() => {
                      setActiveTab('login');
                      setEmail('demo@aurumlife.com');
                      setPassword('demo123');
                    }}
                    className="text-xs text-[#F4D03F] hover:text-[#F7DC6F] underline"
                  >
                    Fill Demo Credentials
                  </button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}