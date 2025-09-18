import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { User, ArrowRight, Check, Calendar } from 'lucide-react';
import { Button } from '../../ui/button';
import { Input } from '../../ui/input';
import { Label } from '../../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../ui/select';
import { Badge } from '../../ui/badge';
import { Avatar, AvatarFallback } from '../../ui/avatar';
import { useOnboardingStore } from '../../../stores/onboardingStore';
import OnboardingLayout from '../OnboardingLayout';

export default function ProfileSetup() {
  const { userData, updateUserData, nextStep } = useOnboardingStore();
  
  const [formData, setFormData] = useState({
    firstName: userData.firstName || '',
    lastName: userData.lastName || '',
    birthDate: userData.birthDate || '',
    howDidYouHear: userData.howDidYouHear || '',
    motivations: userData.motivations || [],
  });

  const [isValid, setIsValid] = useState(false);

  const motivationOptions = [
    'Better Focus',
    'Goal Achievement', 
    'Emotional Wellness',
    'Productivity',
    'Life Balance',
    'Habit Building',
    'Stress Management',
    'Personal Growth',
    'Career Success',
    'Relationship Improvement'
  ];

  const hearAboutOptions = [
    'Friend or Family',
    'Social Media',
    'Search Engine',
    'Advertisement',
    'Blog or Article',
    'Podcast',
    'YouTube',
    'Other'
  ];

  useEffect(() => {
    const isFormValid = formData.firstName.trim().length >= 2 && 
                       formData.lastName.trim().length >= 2 &&
                       formData.birthDate.length > 0 &&
                       formData.howDidYouHear.length > 0 &&
                       formData.motivations.length > 0;
    setIsValid(isFormValid);
  }, [formData]);

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const toggleMotivation = (motivation: string) => {
    setFormData(prev => ({
      ...prev,
      motivations: prev.motivations.includes(motivation)
        ? prev.motivations.filter(m => m !== motivation)
        : [...prev.motivations, motivation]
    }));
  };

  const handleContinue = () => {
    updateUserData({
      firstName: formData.firstName,
      lastName: formData.lastName,
      displayName: `${formData.firstName} ${formData.lastName}`.trim(),
      birthDate: formData.birthDate,
      howDidYouHear: formData.howDidYouHear,
      motivations: formData.motivations,
    });
    nextStep();
  };

  const getInitials = (firstName: string, lastName: string) => {
    const first = firstName.charAt(0).toUpperCase();
    const last = lastName.charAt(0).toUpperCase();
    return first + (last || '');
  };

  return (
    <OnboardingLayout>
      <div className="max-w-2xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="glassmorphism-card p-8 rounded-2xl"
        >
          {/* Header */}
          <div className="text-center mb-8">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="inline-flex items-center justify-center w-16 h-16 aurum-gradient rounded-xl mb-4"
            >
              <User className="w-8 h-8 text-[#0B0D14]" />
            </motion.div>
            
            <h2 className="text-3xl font-bold text-white mb-2">Let's Get to Know You</h2>
            <p className="text-[#B8BCC8]">Help us personalize your Aurum Life experience</p>
          </div>

          <div className="space-y-8">
            {/* Name Section */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
            >
              <Label className="text-white text-lg mb-4 block">What's your name?</Label>
              <div className="flex flex-col space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label className="text-[#B8BCC8] text-sm mb-2 block">First Name</Label>
                    <Input
                      placeholder="Enter your first name"
                      value={formData.firstName}
                      onChange={(e) => handleInputChange('firstName', e.target.value)}
                      className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white p-3 focus:border-[#F4D03F] transition-colors"
                    />
                  </div>
                  <div>
                    <Label className="text-[#B8BCC8] text-sm mb-2 block">Last Name</Label>
                    <Input
                      placeholder="Enter your last name"
                      value={formData.lastName}
                      onChange={(e) => handleInputChange('lastName', e.target.value)}
                      className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white p-3 focus:border-[#F4D03F] transition-colors"
                    />
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <Avatar className="w-12 h-12">
                    <AvatarFallback className="bg-[#F4D03F] text-[#0B0D14] font-bold">
                      {formData.firstName || formData.lastName ? getInitials(formData.firstName, formData.lastName) : '?'}
                    </AvatarFallback>
                  </Avatar>
                  {(formData.firstName || formData.lastName) && (
                    <motion.p
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="text-[#F4D03F] text-sm"
                    >
                      Hi {formData.firstName} {formData.lastName}!
                    </motion.p>
                  )}
                </div>
              </div>
            </motion.div>

            {/* Birth Date Section */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.35 }}
            >
              <Label className="text-white text-lg mb-4 block">When's your birthday?</Label>
              <p className="text-[#B8BCC8] text-sm mb-3">
                This helps us provide age-appropriate life planning recommendations
              </p>
              <Input
                type="date"
                value={formData.birthDate}
                onChange={(e) => handleInputChange('birthDate', e.target.value)}
                className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white p-3 focus:border-[#F4D03F] transition-colors"
                max={new Date().toISOString().split('T')[0]} // Prevent future dates
              />
            </motion.div>

            {/* How did you hear about us */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.45 }}
            >
              <Label className="text-white text-lg mb-4 block">How did you hear about us?</Label>
              <Select value={formData.howDidYouHear} onValueChange={(value) => handleInputChange('howDidYouHear', value)}>
                <SelectTrigger className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white text-lg p-4 focus:border-[#F4D03F]">
                  <SelectValue placeholder="Select an option" />
                </SelectTrigger>
                <SelectContent className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)]">
                  {hearAboutOptions.map((option) => (
                    <SelectItem key={option} value={option} className="text-white hover:bg-[rgba(244,208,63,0.1)]">
                      {option}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </motion.div>

            {/* Motivations */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.55 }}
            >
              <Label className="text-white text-lg mb-4 block">What brings you to Aurum Life?</Label>
              <p className="text-[#B8BCC8] text-sm mb-4">Select all that apply</p>
              
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {motivationOptions.map((motivation, index) => (
                  <motion.div
                    key={motivation}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.3, delay: 0.65 + index * 0.05 }}
                  >
                    <Button
                      variant={formData.motivations.includes(motivation) ? "default" : "outline"}
                      onClick={() => toggleMotivation(motivation)}
                      className={`w-full p-3 text-sm transition-all duration-200 ${
                        formData.motivations.includes(motivation)
                          ? 'bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F] border-[#F4D03F]'
                          : 'border-[rgba(244,208,63,0.2)] text-[#B8BCC8] hover:text-[#F4D03F] hover:border-[#F4D03F] hover:bg-[rgba(244,208,63,0.05)]'
                      }`}
                    >
                      <span className="flex items-center justify-between w-full">
                        {motivation}
                        {formData.motivations.includes(motivation) && (
                          <Check className="w-4 h-4 ml-2" />
                        )}
                      </span>
                    </Button>
                  </motion.div>
                ))}
              </div>

              {formData.motivations.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-4"
                >
                  <p className="text-[#F4D03F] text-sm mb-2">Selected:</p>
                  <div className="flex flex-wrap gap-2">
                    {formData.motivations.map((motivation) => (
                      <Badge
                        key={motivation}
                        className="bg-[rgba(244,208,63,0.2)] text-[#F4D03F] border-[rgba(244,208,63,0.3)]"
                      >
                        {motivation}
                      </Badge>
                    ))}
                  </div>
                </motion.div>
              )}
            </motion.div>
          </div>

          {/* Continue Button */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.9 }}
            className="mt-8 flex justify-center"
          >
            <Button
              onClick={handleContinue}
              disabled={!isValid}
              size="lg"
              className={`px-8 py-4 text-lg font-semibold transition-all duration-200 group ${
                isValid
                  ? 'bg-[#F4D03F] hover:bg-[#F7DC6F] text-[#0B0D14]'
                  : 'bg-[#1A1D29] text-[#B8BCC8] cursor-not-allowed'
              }`}
            >
              Continue
              <ArrowRight className={`w-5 h-5 ml-2 transition-transform ${isValid ? 'group-hover:translate-x-1' : ''}`} />
            </Button>
          </motion.div>

          {/* Form Validation Feedback */}
          {!isValid && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mt-4 text-center"
            >
              <p className="text-[#B8BCC8] text-sm">
                Please fill in your name, birth date, how you heard about us, and select at least one motivation to continue.
              </p>
            </motion.div>
          )}
        </motion.div>
      </div>
    </OnboardingLayout>
  );
}