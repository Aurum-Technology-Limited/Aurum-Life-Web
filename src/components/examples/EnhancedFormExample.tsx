import { useState } from 'react';
import { motion } from 'motion/react';
import { Save, Sparkles } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { EnhancedFormField, useFormAutoSave } from '../enhanced/FormEnhancements';
import { ContentHierarchy } from '../enhanced/VisualHierarchy';
import { TouchOptimizedButton } from '../enhanced/MobileEnhancements';

const passwordValidationRules = [
  {
    test: (value: string) => value.length >= 8,
    message: 'At least 8 characters long',
    severity: 'error' as const
  },
  {
    test: (value: string) => /[A-Z]/.test(value),
    message: 'Contains uppercase letter',
    severity: 'error' as const
  },
  {
    test: (value: string) => /[a-z]/.test(value),
    message: 'Contains lowercase letter',
    severity: 'error' as const
  },
  {
    test: (value: string) => /\d/.test(value),
    message: 'Contains at least one number',
    severity: 'error' as const
  },
  {
    test: (value: string) => /[!@#$%^&*(),.?":{}|<>]/.test(value),
    message: 'Contains special character (recommended)',
    severity: 'warning' as const
  }
];

const emailValidationRules = [
  {
    test: (value: string) => value.length > 0,
    message: 'Email is required',
    severity: 'error' as const
  },
  {
    test: (value: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
    message: 'Must be a valid email address',
    severity: 'error' as const
  }
];

const nameValidationRules = [
  {
    test: (value: string) => value.length >= 2,
    message: 'At least 2 characters long',
    severity: 'error' as const
  },
  {
    test: (value: string) => /^[a-zA-Z\s]+$/.test(value),
    message: 'Only letters and spaces allowed',
    severity: 'error' as const
  }
];

export default function EnhancedFormExample() {
  const { data, updateField, saveData, isSaving } = useFormAutoSave('profile', {
    name: '',
    email: '',
    bio: '',
    password: ''
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      await saveData(data);
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      console.log('Form submitted:', data);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <ContentHierarchy
      level={2}
      title="Enhanced Form Example"
      subtitle="Showcasing auto-save, smart validation, and contextual help"
    >
      <div className="max-w-2xl mx-auto">
        <Card className="glassmorphism-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-primary" />
              Profile Settings
            </CardTitle>
          </CardHeader>

          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <EnhancedFormField
                label="Full Name"
                value={data.name}
                onChange={(value) => updateField('name', value)}
                required
                validation={nameValidationRules}
                help={{
                  content: "Enter your full legal name as you'd like it to appear on your profile",
                  examples: [
                    "John Smith", 
                    "Mary Jane Watson", 
                    "Dr. Elizabeth Johnson"
                  ],
                  tips: [
                    "Use your real name for better professional networking",
                    "You can update this anytime in settings"
                  ]
                }}
                autoSave={{
                  onSave: async (value) => {
                    updateField('name', value);
                    await saveData({ ...data, name: value });
                  },
                  saveKey: 'profile-name'
                }}
              />

              <EnhancedFormField
                label="Email Address"
                value={data.email}
                onChange={(value) => updateField('email', value)}
                type="email"
                required
                validation={emailValidationRules}
                help={{
                  content: "We'll use this email for important account notifications and communication",
                  tips: [
                    "Use a professional email address",
                    "Make sure you have access to this email",
                    "We'll never share your email with third parties"
                  ]
                }}
                autoSave={{
                  onSave: async (value) => {
                    updateField('email', value);
                    await saveData({ ...data, email: value });
                  },
                  saveKey: 'profile-email'
                }}
              />

              <EnhancedFormField
                label="Bio"
                value={data.bio}
                onChange={(value) => updateField('bio', value)}
                type="textarea"
                help={{
                  content: "Write a brief description about yourself, your interests, or professional background",
                  examples: [
                    "Product manager passionate about user experience",
                    "Software developer with 5 years of experience in React",
                    "Life coach helping people achieve their goals"
                  ],
                  tips: [
                    "Keep it concise but engaging",
                    "Mention your key skills or interests",
                    "This will be visible on your public profile"
                  ]
                }}
                autoSave={{
                  onSave: async (value) => {
                    updateField('bio', value);
                    await saveData({ ...data, bio: value });
                  },
                  saveKey: 'profile-bio'
                }}
              />

              <EnhancedFormField
                label="Password"
                value={data.password}
                onChange={(value) => updateField('password', value)}
                type="password"
                validation={passwordValidationRules}
                help={{
                  content: "Create a strong password to secure your account",
                  tips: [
                    "Use a mix of uppercase, lowercase, numbers, and symbols",
                    "Avoid common words or personal information",
                    "Consider using a password manager"
                  ]
                }}
              />

              <div className="pt-4 border-t border-border/50">
                <div className="flex gap-3">
                  <TouchOptimizedButton
                    onClick={() => window.history.back()}
                    variant="secondary"
                    disabled={isSubmitting || isSaving}
                  >
                    Cancel
                  </TouchOptimizedButton>
                  
                  <TouchOptimizedButton
                    onClick={handleSubmit}
                    variant="primary"
                    disabled={isSubmitting || isSaving}
                    className="flex-1"
                  >
                    {isSubmitting ? (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="flex items-center gap-2"
                      >
                        <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                        Saving Profile...
                      </motion.div>
                    ) : (
                      <div className="flex items-center gap-2">
                        <Save className="w-4 h-4" />
                        Save Profile
                      </div>
                    )}
                  </TouchOptimizedButton>
                </div>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </ContentHierarchy>
  );
}