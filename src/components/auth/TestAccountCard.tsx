import { motion } from 'motion/react';
import { Eye, Copy, CheckCircle, User, Lock, Sparkles } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { useState } from 'react';

interface TestAccountCardProps {
  onDemoLogin: () => Promise<void>;
  isLoading?: boolean;
}

export default function TestAccountCard({ onDemoLogin, isLoading = false }: TestAccountCardProps) {
  const [showCredentials, setShowCredentials] = useState(false);
  const [copiedField, setCopiedField] = useState<string | null>(null);

  const demoCredentials = {
    email: 'demo@aurumlife.com',
    password: 'demo123'
  };

  const copyToClipboard = async (text: string, field: string) => {
    try {
      // Try modern Clipboard API first
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
        setCopiedField(field);
        setTimeout(() => setCopiedField(null), 2000);
        return;
      }
      
      // Fallback to legacy method
      const textArea = document.createElement('textarea');
      textArea.value = text;
      textArea.style.position = 'fixed';
      textArea.style.opacity = '0';
      textArea.style.left = '-999999px';
      textArea.style.top = '-999999px';
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      
      const successful = document.execCommand('copy');
      document.body.removeChild(textArea);
      
      if (successful) {
        setCopiedField(field);
        setTimeout(() => setCopiedField(null), 2000);
      } else {
        throw new Error('Copy command failed');
      }
    } catch (error) {
      console.error('Copy failed:', error);
      // Show text selection instead of copying
      setCopiedField(`error-${field}`);
      setTimeout(() => setCopiedField(null), 3000);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="w-full"
    >
      <Card className="glassmorphism-card border-[rgba(244,208,63,0.3)] bg-[rgba(26,29,41,0.6)] backdrop-blur-xl">
        <CardHeader className="text-center pb-4">
          <div className="flex items-center justify-center space-x-2 mb-2">
            <Sparkles className="w-5 h-5 text-[#F4D03F]" />
            <CardTitle className="text-[#F4D03F]">Test Account</CardTitle>
            <Sparkles className="w-5 h-5 text-[#F4D03F]" />
          </div>
          <CardDescription className="text-[#B8BCC8]">
            Experience the full PAPT Framework education and smart onboarding flow
          </CardDescription>
          <Badge variant="outline" className="border-[#F4D03F] text-[#F4D03F] mx-auto mt-2 w-fit">
            Fresh Educational Experience
          </Badge>
        </CardHeader>

        <CardContent className="space-y-4">
          {/* Quick Demo Login Button */}
          <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
            <Button
              onClick={onDemoLogin}
              disabled={isLoading}
              className="w-full bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F] disabled:opacity-50 disabled:cursor-not-allowed h-12"
            >
              {isLoading ? (
                <div className="flex items-center space-x-2">
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    className="w-4 h-4 border-2 border-[#0B0D14] border-t-transparent rounded-full"
                  />
                  <span>Setting up demo...</span>
                </div>
              ) : (
                <div className="flex items-center space-x-2">
                  <User className="w-4 h-4" />
                  <span>Login with Demo Account</span>
                  <Sparkles className="w-4 h-4" />
                </div>
              )}
            </Button>
          </motion.div>

          {/* Credentials Toggle */}
          <div className="space-y-3">
            <Button
              type="button"
              variant="outline"
              onClick={() => setShowCredentials(!showCredentials)}
              className="w-full border-[rgba(244,208,63,0.3)] text-[#B8BCC8] hover:bg-[rgba(244,208,63,0.1)] hover:border-[#F4D03F] hover:text-[#F4D03F]"
            >
              <Eye className="w-4 h-4 mr-2" />
              {showCredentials ? 'Hide' : 'Show'} Demo Credentials
            </Button>

            {/* Credentials Display */}
            <motion.div
              initial={false}
              animate={{ 
                height: showCredentials ? 'auto' : 0,
                opacity: showCredentials ? 1 : 0 
              }}
              transition={{ duration: 0.3 }}
              className="overflow-hidden"
            >
              {showCredentials && (
                <div className="space-y-3 pt-2 border-t border-[rgba(244,208,63,0.2)]">
                  {/* Email Field */}
                  <div className="glassmorphism-panel p-3 rounded-lg">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <User className="w-4 h-4 text-[#B8BCC8]" />
                        <span className="text-sm text-[#B8BCC8]">Email:</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <code 
                          className={`text-[#F4D03F] bg-[rgba(244,208,63,0.1)] px-2 py-1 rounded text-sm transition-all ${
                            copiedField === 'error-email' ? 'select-all bg-[rgba(244,208,63,0.2)] ring-1 ring-[#F4D03F]' : 'select-text'
                          }`}
                        >
                          {demoCredentials.email}
                        </code>
                        <Button
                          type="button"
                          size="sm"
                          variant="ghost"
                          onClick={() => copyToClipboard(demoCredentials.email, 'email')}
                          className="h-6 w-6 p-0 text-[#B8BCC8] hover:text-[#F4D03F]"
                          title={copiedField === 'error-email' ? 'Copy failed - select text manually' : copiedField === 'email' ? 'Copied!' : 'Copy email'}
                        >
                          {copiedField === 'email' ? (
                            <CheckCircle className="w-3 h-3 text-green-400" />
                          ) : copiedField === 'error-email' ? (
                            <Eye className="w-3 h-3 text-yellow-400" />
                          ) : (
                            <Copy className="w-3 h-3" />
                          )}
                        </Button>
                      </div>
                    </div>
                  </div>

                  {/* Password Field */}
                  <div className="glassmorphism-panel p-3 rounded-lg">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Lock className="w-4 h-4 text-[#B8BCC8]" />
                        <span className="text-sm text-[#B8BCC8]">Password:</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <code 
                          className={`text-[#F4D03F] bg-[rgba(244,208,63,0.1)] px-2 py-1 rounded text-sm transition-all ${
                            copiedField === 'error-password' ? 'select-all bg-[rgba(244,208,63,0.2)] ring-1 ring-[#F4D03F]' : 'select-text'
                          }`}
                        >
                          {demoCredentials.password}
                        </code>
                        <Button
                          type="button"
                          size="sm"
                          variant="ghost"
                          onClick={() => copyToClipboard(demoCredentials.password, 'password')}
                          className="h-6 w-6 p-0 text-[#B8BCC8] hover:text-[#F4D03F]"
                          title={copiedField === 'error-password' ? 'Copy failed - select text manually' : copiedField === 'password' ? 'Copied!' : 'Copy password'}
                        >
                          {copiedField === 'password' ? (
                            <CheckCircle className="w-3 h-3 text-green-400" />
                          ) : copiedField === 'error-password' ? (
                            <Eye className="w-3 h-3 text-yellow-400" />
                          ) : (
                            <Copy className="w-3 h-3" />
                          )}
                        </Button>
                      </div>
                    </div>
                  </div>

                  <div className="text-xs text-center pt-2">
                    {(copiedField === 'error-email' || copiedField === 'error-password') ? (
                      <p className="text-yellow-400 mb-2">
                        Copy blocked - text is highlighted for manual selection
                      </p>
                    ) : (
                      <p className="text-[#6B7280]">
                        These credentials can be used for manual login if needed
                      </p>
                    )}
                  </div>
                </div>
              )}
            </motion.div>
          </div>

          {/* Demo Account Features */}
          <div className="glassmorphism-panel p-4 rounded-lg space-y-2">
            <h4 className="text-sm text-[#F4D03F] mb-2">What's included:</h4>
            <ul className="text-xs text-[#B8BCC8] space-y-1">
              <li className="flex items-center space-x-2">
                <div className="w-1 h-1 bg-[#F4D03F] rounded-full"></div>
                <span>Interactive PAPT Framework education</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-1 h-1 bg-[#F4D03F] rounded-full"></div>
                <span>Sample life pillars, areas, and projects</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-1 h-1 bg-[#F4D03F] rounded-full"></div>
                <span>Demo tasks and journal entries</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-1 h-1 bg-[#F4D03F] rounded-full"></div>
                <span>All features unlocked and ready to explore</span>
              </li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}