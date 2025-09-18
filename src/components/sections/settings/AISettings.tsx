import { useState } from 'react';
import { Brain, Sparkles, Target, MessageCircle, Shield, RotateCcw, CheckCircle2, AlertCircle, Info } from 'lucide-react';
import { Button } from '../../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../ui/card';
import { Label } from '../../ui/label';
import { Switch } from '../../ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../ui/select';
import { Separator } from '../../ui/separator';
import { Slider } from '../../ui/slider';
import { Alert, AlertDescription } from '../../ui/alert';
import { Badge } from '../../ui/badge';
import { motion } from 'motion/react';
import { useForm, Controller } from 'react-hook-form@7.55.0';
import { zodResolver } from '@hookform/resolvers/zod';
import { aiSettingsSchema, type AISettingsData } from '../../../schemas/settings';
import { useSettingsStore } from '../../../stores/settingsStore';
import { useAppStore } from '../../../stores/basicAppStore';
import { toast } from 'sonner@2.0.3';

export default function AISettings() {
  const [showDataUsageInfo, setShowDataUsageInfo] = useState(false);

  // Store integration
  const { aiSettings, setAISettings, isLoading, errors, setLoading, setError, setLastSaved, resetAISettings } = useSettingsStore();
  const addNotification = useAppStore(state => state.addNotification);

  // Form setup
  const form = useForm<AISettingsData>({
    resolver: zodResolver(aiSettingsSchema),
    defaultValues: aiSettings,
    mode: 'onChange',
  });

  // Watch values for dynamic UI updates
  const watchedValues = form.watch();

  // Handle form submission
  const handleSave = async (data: AISettingsData) => {
    setLoading('ai', true);
    setError('ai', null);

    try {
      // Simulate API call - replace with actual backend call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Update store
      setAISettings(data);
      setLastSaved('ai', new Date());
      
      toast.success('AI settings saved successfully');
      addNotification({
        type: 'success',
        title: 'Settings Updated',
        message: 'Your AI preferences have been saved.',
        isRead: false,
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to save AI settings';
      setError('ai', errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading('ai', false);
    }
  };

  // Handle reset
  const handleReset = async () => {
    if (!confirm('Are you sure you want to reset all AI settings to default values?')) {
      return;
    }

    setLoading('ai', true);
    
    try {
      // Simulate API call - replace with actual backend call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      resetAISettings();
      form.reset();
      
      toast.success('AI settings reset to defaults');
      addNotification({
        type: 'info',
        title: 'Settings Reset',
        message: 'AI settings have been restored to default values.',
        isRead: false,
      });
    } catch (error) {
      toast.error('Failed to reset AI settings');
    } finally {
      setLoading('ai', false);
    }
  };

  // Get automation level label
  const getAutomationLabel = (level: string) => {
    switch (level) {
      case 'minimal': return 'Minimal - AI suggests, you decide';
      case 'balanced': return 'Balanced - Some automation with oversight';
      case 'aggressive': return 'Aggressive - Full automation where possible';
      default: return 'Balanced';
    }
  };

  // Get insight style label
  const getInsightStyleLabel = (style: string) => {
    switch (style) {
      case 'brief': return 'Brief - Quick highlights only';
      case 'detailed': return 'Detailed - Comprehensive analysis';
      case 'comprehensive': return 'Comprehensive - In-depth insights with recommendations';
      default: return 'Detailed';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
      className="space-y-6"
    >
      {/* Error Alert */}
      {errors.ai && (
        <Alert className="border-[#EF4444] bg-[rgba(239,68,68,0.1)]">
          <AlertCircle className="w-4 h-4 text-[#EF4444]" />
          <AlertDescription className="text-[#EF4444]">
            {errors.ai}
          </AlertDescription>
        </Alert>
      )}

      {/* Last Saved Indicator */}
      {useSettingsStore.getState().lastSaved.ai && (
        <div className="flex items-center space-x-2 text-sm text-[#10B981]">
          <CheckCircle2 className="w-4 h-4" />
          <span>Last saved: {new Date(useSettingsStore.getState().lastSaved.ai!).toLocaleString()}</span>
        </div>
      )}

      <form onSubmit={form.handleSubmit(handleSave)} className="space-y-6">
        {/* AI Features Overview */}
        <Card className="glassmorphism-card border-0">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <Brain className="w-5 h-5 text-[#F4D03F]" />
              <span>AI Features</span>
            </CardTitle>
            <CardDescription className="text-[#B8BCC8]">
              Enable and configure AI-powered assistance throughout Aurum Life
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white">Smart Suggestions</Label>
                  <p className="text-[#B8BCC8] text-sm">Get AI-powered task and goal suggestions</p>
                </div>
                <Controller
                  name="aiFeatures.smartSuggestions"
                  control={form.control}
                  render={({ field }) => (
                    <Switch checked={field.value} onCheckedChange={field.onChange} />
                  )}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white">Auto Tagging</Label>
                  <p className="text-[#B8BCC8] text-sm">Automatically categorize and tag your tasks</p>
                </div>
                <Controller
                  name="aiFeatures.autoTagging"
                  control={form.control}
                  render={({ field }) => (
                    <Switch checked={field.value} onCheckedChange={field.onChange} />
                  )}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white">Priority Prediction</Label>
                  <p className="text-[#B8BCC8] text-sm">AI determines task priority based on context</p>
                </div>
                <Controller
                  name="aiFeatures.priorityPrediction"
                  control={form.control}
                  render={({ field }) => (
                    <Switch checked={field.value} onCheckedChange={field.onChange} />
                  )}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white">Insight Generation</Label>
                  <p className="text-[#B8BCC8] text-sm">Personalized insights about your productivity</p>
                </div>
                <Controller
                  name="aiFeatures.insightGeneration"
                  control={form.control}
                  render={({ field }) => (
                    <Switch checked={field.value} onCheckedChange={field.onChange} />
                  )}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white">Natural Language Processing</Label>
                  <p className="text-[#B8BCC8] text-sm">Create tasks and goals using natural language</p>
                </div>
                <Controller
                  name="aiFeatures.naturalLanguageProcessing"
                  control={form.control}
                  render={({ field }) => (
                    <Switch checked={field.value} onCheckedChange={field.onChange} />
                  )}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Automation Settings */}
        <Card className="glassmorphism-card border-0">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <Target className="w-5 h-5 text-[#F4D03F]" />
              <span>Automation</span>
            </CardTitle>
            <CardDescription className="text-[#B8BCC8]">
              Configure AI automation for different aspects of your workflow
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white">Auto Scheduling</Label>
                  <p className="text-[#B8BCC8] text-sm">Automatically schedule tasks based on availability</p>
                </div>
                <Controller
                  name="automation.autoScheduling"
                  control={form.control}
                  render={({ field }) => (
                    <Switch checked={field.value} onCheckedChange={field.onChange} />
                  )}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white">Smart Deadlines</Label>
                  <p className="text-[#B8BCC8] text-sm">AI suggests realistic deadlines for tasks</p>
                </div>
                <Controller
                  name="automation.smartDeadlines"
                  control={form.control}
                  render={({ field }) => (
                    <Switch checked={field.value} onCheckedChange={field.onChange} />
                  )}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white">Progress Tracking</Label>
                  <p className="text-[#B8BCC8] text-sm">Automatically track and update progress</p>
                </div>
                <Controller
                  name="automation.progressTracking"
                  control={form.control}
                  render={({ field }) => (
                    <Switch checked={field.value} onCheckedChange={field.onChange} />
                  )}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white">Contextual Reminders</Label>
                  <p className="text-[#B8BCC8] text-sm">Smart reminders based on location and time</p>
                </div>
                <Controller
                  name="automation.contextualReminders"
                  control={form.control}
                  render={({ field }) => (
                    <Switch checked={field.value} onCheckedChange={field.onChange} />
                  )}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* AI Preferences */}
        <Card className="glassmorphism-card border-0">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <Sparkles className="w-5 h-5 text-[#F4D03F]" />
              <span>AI Preferences</span>
            </CardTitle>
            <CardDescription className="text-[#B8BCC8]">
              Customize how AI assists you throughout your workflow
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <Label htmlFor="suggestionFrequency" className="text-white">Suggestion Frequency</Label>
              <Controller
                name="preferences.suggestionFrequency"
                control={form.control}
                render={({ field }) => (
                  <Select value={field.value} onValueChange={field.onChange}>
                    <SelectTrigger className="mt-2 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                      <SelectValue placeholder="Select frequency" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">Low - Minimal suggestions</SelectItem>
                      <SelectItem value="medium">Medium - Regular suggestions</SelectItem>
                      <SelectItem value="high">High - Frequent suggestions</SelectItem>
                    </SelectContent>
                  </Select>
                )}
              />
            </div>

            <div>
              <Label htmlFor="automationLevel" className="text-white">Automation Level</Label>
              <Controller
                name="preferences.automationLevel"
                control={form.control}
                render={({ field }) => (
                  <Select value={field.value} onValueChange={field.onChange}>
                    <SelectTrigger className="mt-2 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                      <SelectValue placeholder="Select automation level" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="minimal">Minimal</SelectItem>
                      <SelectItem value="balanced">Balanced</SelectItem>
                      <SelectItem value="aggressive">Aggressive</SelectItem>
                    </SelectContent>
                  </Select>
                )}
              />
              <p className="text-[#B8BCC8] text-sm mt-1">
                {getAutomationLabel(watchedValues.preferences?.automationLevel || 'balanced')}
              </p>
            </div>

            <div>
              <Label htmlFor="insightStyle" className="text-white">Insight Style</Label>
              <Controller
                name="preferences.insightStyle"
                control={form.control}
                render={({ field }) => (
                  <Select value={field.value} onValueChange={field.onChange}>
                    <SelectTrigger className="mt-2 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                      <SelectValue placeholder="Select insight style" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="brief">Brief</SelectItem>
                      <SelectItem value="detailed">Detailed</SelectItem>
                      <SelectItem value="comprehensive">Comprehensive</SelectItem>
                    </SelectContent>
                  </Select>
                )}
              />
              <p className="text-[#B8BCC8] text-sm mt-1">
                {getInsightStyleLabel(watchedValues.preferences?.insightStyle || 'detailed')}
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Privacy Settings */}
        <Card className="glassmorphism-card border-0">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <Shield className="w-5 h-5 text-[#F4D03F]" />
              <span>AI Privacy & Data</span>
            </CardTitle>
            <CardDescription className="text-[#B8BCC8]">
              Control how AI uses your data to provide personalized experiences
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white">Data Usage Consent</Label>
                  <p className="text-[#B8BCC8] text-sm">Allow AI to analyze your data for personalization</p>
                </div>
                <Controller
                  name="privacy.dataUsageConsent"
                  control={form.control}
                  render={({ field }) => (
                    <Switch checked={field.value} onCheckedChange={field.onChange} />
                  )}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white">Improvement Program</Label>
                  <p className="text-[#B8BCC8] text-sm">Help improve AI by sharing usage patterns</p>
                </div>
                <Controller
                  name="privacy.improvementProgram"
                  control={form.control}
                  render={({ field }) => (
                    <Switch checked={field.value} onCheckedChange={field.onChange} />
                  )}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white">Anonymous Analytics</Label>
                  <p className="text-[#B8BCC8] text-sm">Share anonymous usage data to improve features</p>
                </div>
                <Controller
                  name="privacy.anonymousAnalytics"
                  control={form.control}
                  render={({ field }) => (
                    <Switch checked={field.value} onCheckedChange={field.onChange} />
                  )}
                />
              </div>
            </div>

            <Separator className="bg-[rgba(244,208,63,0.1)]" />

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <Label className="text-white">Data Usage Information</Label>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowDataUsageInfo(!showDataUsageInfo)}
                  className="text-[#F4D03F] hover:text-[#F7DC6F]"
                >
                  <Info className="w-4 h-4 mr-1" />
                  {showDataUsageInfo ? 'Hide' : 'Show'} Details
                </Button>
              </div>

              {showDataUsageInfo && (
                <Alert className="border-[rgba(244,208,63,0.2)] bg-[rgba(244,208,63,0.05)]">
                  <Info className="w-4 h-4 text-[#F4D03F]" />
                  <AlertDescription className="text-[#B8BCC8]">
                    <div className="space-y-2">
                      <p className="font-medium text-white">AI uses the following data to improve your experience:</p>
                      <ul className="text-sm space-y-1 ml-4">
                        <li>• Task completion patterns and timing</li>
                        <li>• Goal progress and achievement data</li>
                        <li>• App usage and interaction patterns</li>
                        <li>• Journal entries (metadata only, not content)</li>
                        <li>• Time tracking and productivity metrics</li>
                      </ul>
                      <p className="text-sm mt-2">
                        <strong className="text-white">Your privacy is important:</strong> All data is encrypted, 
                        processed locally when possible, and never shared with third parties without explicit consent.
                      </p>
                    </div>
                  </AlertDescription>
                </Alert>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <div className="flex space-x-4">
          <Button 
            type="submit"
            className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
            disabled={isLoading.ai || !form.formState.isDirty}
          >
            {isLoading.ai && <CheckCircle2 className="w-4 h-4 mr-2 animate-spin" />}
            Save AI Settings
          </Button>
          <Button 
            type="button"
            variant="outline" 
            className="border-[rgba(244,208,63,0.2)] text-[#F4D03F]"
            onClick={() => form.reset()}
            disabled={isLoading.ai}
          >
            Reset Changes
          </Button>
          <Button 
            type="button"
            variant="outline" 
            className="border-[rgba(239,68,68,0.3)] text-[#EF4444] hover:bg-[rgba(239,68,68,0.1)]"
            onClick={handleReset}
            disabled={isLoading.ai}
          >
            <RotateCcw className="w-4 h-4 mr-2" />
            Reset to Defaults
          </Button>
        </div>
      </form>
    </motion.div>
  );
}