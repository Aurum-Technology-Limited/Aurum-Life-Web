import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Mic, MicOff, Send, Sparkles, Brain, X, Tag, Clock, AlertTriangle, Target, ThumbsUp, ThumbsDown, Lightbulb, TrendingUp } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '../ui/dialog';
import { Button } from '../ui/button';
import { Textarea } from '../ui/textarea';
import { Badge } from '../ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Separator } from '../ui/separator';
import { useEnhancedFeaturesStore } from '../../stores/enhancedFeaturesStore';
import { ragCategorizationService, CategorizationResult, ContextualData } from '../../services/ragCategorization';
import { showSuccess, showError } from '../../utils/toast';

interface FeedbackData {
  wasCorrect: boolean;
  actualCategory: {
    pillar: string;
    area?: string;
    project?: string;
  };
}

export default function QuickCaptureModal() {
  const {
    isQuickCaptureOpen,
    isVoiceRecording,
    pillars,
    closeQuickCapture,
    addQuickCaptureItem,
    startVoiceRecording,
    stopVoiceRecording,
    getAllAreas,
    getAllProjects,
    getUnprocessedQuickCapture
  } = useEnhancedFeaturesStore();

  const [content, setContent] = useState('');
  const [contentType, setContentType] = useState<'idea' | 'task' | 'note' | 'goal'>('idea');
  const [categorizationResult, setCategorizationResult] = useState<CategorizationResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [selectedPillar, setSelectedPillar] = useState<string>('');
  const [selectedArea, setSelectedArea] = useState<string>('');
  const [selectedProject, setSelectedProject] = useState<string>('');
  const [speechError, setSpeechError] = useState<string>('');
  const [showAlternatives, setShowAlternatives] = useState(false);
  const [feedbackGiven, setFeedbackGiven] = useState(false);
  const [isLoadingContext, setIsLoadingContext] = useState(false);

  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const recognitionRef = useRef<any>(null);

  // Initialize speech recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      try {
        const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
        recognitionRef.current = new SpeechRecognition();
        recognitionRef.current.continuous = true;
        recognitionRef.current.interimResults = true;
        recognitionRef.current.lang = 'en-US';

        recognitionRef.current.onresult = (event: any) => {
          let finalTranscript = '';
          let interimTranscript = '';

          for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
              finalTranscript += transcript + ' ';
            } else {
              interimTranscript += transcript;
            }
          }

          if (finalTranscript) {
            setContent(prev => prev + finalTranscript);
          }
        };

        recognitionRef.current.onerror = (event: any) => {
          console.error('Speech recognition error:', event.error);
          
          // Handle different error types
          switch (event.error) {
            case 'not-allowed':
              setSpeechError('Microphone access denied. Please allow microphone permissions and try again.');
              break;
            case 'no-speech':
              setSpeechError('No speech detected. Please speak clearly and try again.');
              break;
            case 'network':
              setSpeechError('Network error. Please check your connection and try again.');
              break;
            default:
              setSpeechError('Speech recognition failed. Please try again.');
          }
          
          stopVoiceRecording();
          
          // Clear error after 5 seconds
          setTimeout(() => setSpeechError(''), 5000);
        };

        recognitionRef.current.onend = () => {
          stopVoiceRecording();
        };
      } catch (error) {
        console.error('Speech recognition initialization failed:', error);
      }
    }
  }, [stopVoiceRecording]);

  // Handle voice recording
  useEffect(() => {
    if (isVoiceRecording && recognitionRef.current) {
      recognitionRef.current.start();
    } else if (!isVoiceRecording && recognitionRef.current) {
      recognitionRef.current.stop();
    }
  }, [isVoiceRecording]);

  // Real AI Analysis using RAG categorization
  useEffect(() => {
    if (content.length > 20) {
      setIsAnalyzing(true);
      
      const analyzeContent = async () => {
        try {
          // Gather contextual data from current user state
          const contextualData = gatherContextualData();
          
          // Use the RAG categorization service
          const result = await ragCategorizationService.categorizeContent(
            content,
            contentType,
            contextualData
          );
          
          setCategorizationResult(result);
          setIsAnalyzing(false);
        } catch (error) {
          console.error('Failed to analyze content:', error);
          setIsAnalyzing(false);
          // Fall back to simple categorization if RAG fails
          const fallbackResult = createFallbackCategorization(content);
          setCategorizationResult(fallbackResult);
        }
      };

      const timer = setTimeout(analyzeContent, 1000); // Slight delay for better UX
      return () => clearTimeout(timer);
    } else {
      setCategorizationResult(null);
    }
  }, [content, contentType]);

  // Reset speech error when modal closes
  useEffect(() => {
    if (!isQuickCaptureOpen) {
      setSpeechError('');
      setContent('');
      setCategorizationResult(null);
      setSelectedPillar('');
      setSelectedArea('');
      setSelectedProject('');
      setIsAnalyzing(false);
      setShowAlternatives(false);
      setFeedbackGiven(false);
    }
  }, [isQuickCaptureOpen]);

  // Gather contextual data from current user state
  const gatherContextualData = (): ContextualData => {
    const allAreas = getAllAreas();
    const allProjects = getAllProjects();
    const quickCaptureItems = getUnprocessedQuickCapture();
    
    // Recent items from quick capture
    const recentItems = quickCaptureItems.slice(0, 10).map(item => ({
      content: item.content,
      pillar: item.suggestedPillar || 'Personal Development',
      area: item.suggestedArea,
      timestamp: new Date(item.createdAt).getTime()
    }));

    // User preferences based on pillar usage
    const pillarFrequency = pillars.reduce((acc, pillar) => {
      acc[pillar.name] = pillar.areas.length + pillar.areas.reduce((sum, area) => sum + area.projects.length, 0);
      return acc;
    }, {} as Record<string, number>);
    
    const frequentPillars = Object.entries(pillarFrequency)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 3)
      .map(([pillar]) => pillar);

    // Current context
    const now = new Date();
    const timeOfDay = getTimeOfDay(now);
    const dayOfWeek = now.toLocaleDateString('en-US', { weekday: 'long' });
    
    const currentProjects = allProjects
      .filter(project => project.status === 'active')
      .map(project => project.name);

    return {
      recentItems,
      userPreferences: {
        frequentPillars,
        workingHours: { start: '09:00', end: '17:00' }, // Default working hours
        focusAreas: allAreas.slice(0, 5).map(area => area.name)
      },
      currentContext: {
        timeOfDay,
        dayOfWeek,
        currentProjects
      }
    };
  };

  // Helper to determine time of day
  const getTimeOfDay = (date: Date): 'morning' | 'afternoon' | 'evening' | 'night' => {
    const hour = date.getHours();
    if (hour >= 5 && hour < 12) return 'morning';
    if (hour >= 12 && hour < 17) return 'afternoon';
    if (hour >= 17 && hour < 22) return 'evening';
    return 'night';
  };

  // Create fallback categorization if RAG fails
  const createFallbackCategorization = (text: string): CategorizationResult => {
    const keywords = text.toLowerCase();
    let pillar = 'Personal Development';
    let area = 'Learning & Growth';
    
    // Simple keyword matching for fallback
    if (keywords.includes('workout') || keywords.includes('exercise') || keywords.includes('gym')) {
      pillar = 'Health & Fitness';
      area = 'Physical Health';
    } else if (keywords.includes('work') || keywords.includes('project') || keywords.includes('meeting')) {
      pillar = 'Career & Professional';
      area = 'Current Projects';
    } else if (keywords.includes('family') || keywords.includes('friend') || keywords.includes('relationship')) {
      pillar = 'Relationships';
      area = 'Family & Friends';
    }

    return {
      pillar,
      area,
      confidence: 0.6,
      reasoning: 'Fallback categorization using keyword matching',
      alternatives: [],
      metadata: {
        sentiment: 'neutral',
        urgency: 'low',
        complexity: 'simple',
        keywords: text.split(' ').filter(word => word.length > 3).slice(0, 5),
        entities: [],
        suggestedTags: [contentType],
        priority: 'medium'
      }
    };
  };

  // Handle user feedback on AI categorization
  const handleFeedback = (isCorrect: boolean, actualCategory?: { pillar: string; area?: string; project?: string }) => {
    if (categorizationResult && content) {
      const finalCategory = actualCategory || {
        pillar: categorizationResult.pillar,
        area: categorizationResult.area,
        project: categorizationResult.project
      };
      
      try {
        ragCategorizationService.learnFromFeedback(content, finalCategory, isCorrect);
        setFeedbackGiven(true);
        
        if (isCorrect) {
          showSuccess('Thanks for the feedback! AI will improve with your input.');
        } else {
          showSuccess('Feedback recorded. AI will learn from this correction.');
        }
      } catch (error) {
        console.error('Failed to record feedback:', error);
        showError('Failed to record feedback');
      }
    }
  };

  // Handle alternative selection
  const handleAlternativeSelect = (alternative: { pillar: string; area?: string; confidence: number }) => {
    if (categorizationResult) {
      setCategorizationResult({
        ...categorizationResult,
        pillar: alternative.pillar,
        area: alternative.area,
        confidence: alternative.confidence,
        reasoning: `User selected alternative: ${alternative.pillar}${alternative.area ? ` > ${alternative.area}` : ''}`
      });
      setShowAlternatives(false);
    }
  };

  const handleSubmit = () => {
    if (!content.trim()) return;

    try {
      // If user hasn't given feedback on AI suggestion and we have a categorization result, assume it's correct
      if (categorizationResult && !feedbackGiven) {
        handleFeedback(true);
      }

      addQuickCaptureItem({
        content: content.trim(),
        type: contentType,
        suggestedPillar: categorizationResult?.pillar || selectedPillar || 'Personal Development',
        suggestedArea: categorizationResult?.area || selectedArea || 'Learning & Growth',
        suggestedProject: categorizationResult?.project || selectedProject || undefined,
        confidence: categorizationResult?.confidence || 0.5,
        processed: false
      });

      // Show success message with enhanced details
      const successMessage = categorizationResult
        ? `${contentType.charAt(0).toUpperCase() + contentType.slice(1)} captured and categorized under ${categorizationResult.pillar}!`
        : `${contentType.charAt(0).toUpperCase() + contentType.slice(1)} captured successfully!`;
      
      showSuccess(successMessage);

      // Reset form
      setContent('');
      setCategorizationResult(null);
      setSelectedPillar('');
      setSelectedArea('');
      setSelectedProject('');
      setSpeechError('');
      setShowAlternatives(false);
      setFeedbackGiven(false);
      closeQuickCapture();
    } catch (error) {
      console.error('Failed to add quick capture item:', error);
      showError('Failed to save item. Please try again.');
      setSpeechError('Failed to save item. Please try again.');
      setTimeout(() => setSpeechError(''), 3000);
    }
  };

  const toggleVoiceRecording = async () => {
    if (isVoiceRecording) {
      stopVoiceRecording();
    } else {
      // Clear any previous errors
      setSpeechError('');
      
      // Check for microphone permissions first
      try {
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
          await navigator.mediaDevices.getUserMedia({ audio: true });
        }
        startVoiceRecording();
      } catch (error) {
        setSpeechError('Microphone access denied. Please allow microphone permissions to use voice recording.');
        setTimeout(() => setSpeechError(''), 5000);
      }
    }
  };

  return (
    <Dialog open={isQuickCaptureOpen} onOpenChange={closeQuickCapture}>
      <DialogContent className="glassmorphism-card border-0 bg-[#1A1D29] text-white max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-2">
            <Sparkles className="w-5 h-5 text-[#F4D03F]" />
            <span>Quick Capture</span>
          </DialogTitle>
          <DialogDescription className="text-[#B8BCC8]">
            Quickly capture ideas, tasks, notes, or goals. AI will automatically suggest the best pillar and area for organization.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Content Type Selection */}
          <div className="flex space-x-2">
            {(['idea', 'task', 'note', 'goal'] as const).map((type) => (
              <Button
                key={type}
                variant={contentType === type ? 'default' : 'outline'}
                size="sm"
                onClick={() => setContentType(type)}
                className={contentType === type ? 'aurum-gradient text-[#0B0D14]' : 'border-[rgba(244,208,63,0.3)] text-[#B8BCC8]'}
              >
                <Tag className="w-4 h-4 mr-1" />
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </Button>
            ))}
          </div>

          {/* Content Input */}
          <div className="relative">
            <Textarea
              ref={textareaRef}
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="What's on your mind? Speak or type your thoughts..."
              className="min-h-[120px] bg-[#0B0D14] border-[rgba(244,208,63,0.2)] text-white placeholder:text-[#6B7280] focus:border-[#F4D03F] resize-none"
            />
            
            {/* Voice Recording Button */}
            <Button
              size="sm"
              variant="ghost"
              onClick={toggleVoiceRecording}
              className={`absolute bottom-3 right-3 w-8 h-8 rounded-full ${
                isVoiceRecording 
                  ? 'bg-red-500 hover:bg-red-600 text-white' 
                  : 'hover:bg-[rgba(244,208,63,0.1)] text-[#B8BCC8]'
              }`}
            >
              {isVoiceRecording ? (
                <MicOff className="w-4 h-4" />
              ) : (
                <Mic className="w-4 h-4" />
              )}
            </Button>

            {isVoiceRecording && (
              <motion.div
                className="absolute -top-2 -right-2 w-3 h-3 bg-red-500 rounded-full"
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 1, repeat: Infinity }}
              />
            )}
          </div>

          {/* Speech Error Display */}
          {speechError && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="bg-red-500/10 border border-red-500/20 rounded-lg p-3"
            >
              <p className="text-red-400 text-sm">{speechError}</p>
            </motion.div>
          )}

          {/* Enhanced AI Analysis */}
          <AnimatePresence>
            {isAnalyzing && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="glassmorphism-panel p-4 rounded-lg"
              >
                <div className="flex items-center space-x-2 mb-2">
                  <Brain className="w-4 h-4 text-[#F4D03F] animate-pulse" />
                  <span className="text-sm text-[#B8BCC8]">RAG AI is analyzing your content...</span>
                </div>
                <div className="w-full h-1 bg-[rgba(244,208,63,0.1)] rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-[#F4D03F] rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: '100%' }}
                    transition={{ duration: 1.5 }}
                  />
                </div>
                <p className="text-xs text-[#6B7280] mt-2">
                  Analyzing context, keywords, sentiment, and user patterns...
                </p>
              </motion.div>
            )}

            {categorizationResult && !isAnalyzing && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="glassmorphism-panel p-4 rounded-lg space-y-4"
              >
                {/* Header with confidence and feedback */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Brain className="w-4 h-4 text-[#F4D03F]" />
                    <span className="text-sm text-white">AI Categorization</span>
                    <Badge variant="outline" className="text-xs border-[#F4D03F] text-[#F4D03F]">
                      {Math.round(categorizationResult.confidence * 100)}% confident
                    </Badge>
                  </div>
                  
                  {!feedbackGiven && (
                    <div className="flex items-center space-x-1">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleFeedback(true)}
                        className="text-green-400 hover:bg-green-400/10 h-7 w-7 p-0"
                      >
                        <ThumbsUp className="w-3 h-3" />
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleFeedback(false, { pillar: selectedPillar || categorizationResult.pillar, area: selectedArea, project: selectedProject })}
                        className="text-red-400 hover:bg-red-400/10 h-7 w-7 p-0"
                      >
                        <ThumbsDown className="w-3 h-3" />
                      </Button>
                    </div>
                  )}
                </div>
                
                {/* Main categorization */}
                <div className="space-y-3">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-[#B8BCC8]">Pillar:</span>
                    <Badge className="aurum-gradient text-[#0B0D14]">
                      {categorizationResult.pillar}
                    </Badge>
                  </div>
                  
                  {categorizationResult.area && (
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-[#B8BCC8]">Area:</span>
                      <Badge variant="outline" className="border-[rgba(244,208,63,0.3)] text-[#F4D03F]">
                        {categorizationResult.area}
                      </Badge>
                    </div>
                  )}
                  
                  {categorizationResult.project && (
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-[#B8BCC8]">Project:</span>
                      <Badge variant="outline" className="border-[rgba(59,130,246,0.3)] text-[#3B82F6]">
                        {categorizationResult.project}
                      </Badge>
                    </div>
                  )}
                </div>

                {/* Metadata */}
                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div className="flex items-center space-x-2">
                    <AlertTriangle className="w-3 h-3 text-[#B8BCC8]" />
                    <span className="text-[#B8BCC8]">Urgency:</span>
                    <Badge 
                      variant="outline" 
                      className={`text-xs ${
                        categorizationResult.metadata.urgency === 'high' ? 'border-red-400 text-red-400' :
                        categorizationResult.metadata.urgency === 'medium' ? 'border-yellow-400 text-yellow-400' :
                        'border-green-400 text-green-400'
                      }`}
                    >
                      {categorizationResult.metadata.urgency}
                    </Badge>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Target className="w-3 h-3 text-[#B8BCC8]" />
                    <span className="text-[#B8BCC8]">Complexity:</span>
                    <Badge variant="outline" className="text-xs border-[rgba(244,208,63,0.3)] text-[#F4D03F]">
                      {categorizationResult.metadata.complexity}
                    </Badge>
                  </div>

                  {categorizationResult.metadata.estimatedDuration && (
                    <div className="flex items-center space-x-2">
                      <Clock className="w-3 h-3 text-[#B8BCC8]" />
                      <span className="text-[#B8BCC8]">Duration:</span>
                      <span className="text-[#F4D03F] text-xs">{categorizationResult.metadata.estimatedDuration}</span>
                    </div>
                  )}

                  {categorizationResult.metadata.priority && (
                    <div className="flex items-center space-x-2">
                      <TrendingUp className="w-3 h-3 text-[#B8BCC8]" />
                      <span className="text-[#B8BCC8]">Priority:</span>
                      <Badge 
                        variant="outline" 
                        className={`text-xs ${
                          categorizationResult.metadata.priority === 'high' ? 'border-red-400 text-red-400' :
                          categorizationResult.metadata.priority === 'medium' ? 'border-yellow-400 text-yellow-400' :
                          'border-blue-400 text-blue-400'
                        }`}
                      >
                        {categorizationResult.metadata.priority}
                      </Badge>
                    </div>
                  )}
                </div>

                {/* Tags */}
                {categorizationResult.metadata.suggestedTags.length > 0 && (
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <Tag className="w-3 h-3 text-[#B8BCC8]" />
                      <span className="text-xs text-[#B8BCC8]">Suggested Tags:</span>
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {categorizationResult.metadata.suggestedTags.slice(0, 6).map((tag, index) => (
                        <Badge key={index} variant="outline" className="text-xs border-[rgba(244,208,63,0.2)] text-[#B8BCC8]">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {/* Reasoning */}
                <div className="space-y-2">
                  <p className="text-xs text-[#6B7280] italic">
                    {categorizationResult.reasoning}
                  </p>
                </div>

                {/* Alternatives */}
                {categorizationResult.alternatives.length > 0 && (
                  <div className="space-y-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setShowAlternatives(!showAlternatives)}
                      className="text-[#B8BCC8] hover:text-white hover:bg-[rgba(244,208,63,0.1)] h-6 text-xs"
                    >
                      <Lightbulb className="w-3 h-3 mr-1" />
                      {showAlternatives ? 'Hide' : 'Show'} Alternatives ({categorizationResult.alternatives.length})
                    </Button>
                    
                    <AnimatePresence>
                      {showAlternatives && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          exit={{ opacity: 0, height: 0 }}
                          className="space-y-1"
                        >
                          {categorizationResult.alternatives.map((alt, index) => (
                            <motion.div
                              key={index}
                              className="flex items-center justify-between p-2 bg-[rgba(255,255,255,0.05)] rounded cursor-pointer hover:bg-[rgba(244,208,63,0.1)] transition-colors"
                              onClick={() => handleAlternativeSelect(alt)}
                            >
                              <div className="flex items-center space-x-2">
                                <Badge variant="outline" className="text-xs border-[rgba(244,208,63,0.3)] text-[#F4D03F]">
                                  {alt.pillar}
                                </Badge>
                                {alt.area && (
                                  <Badge variant="outline" className="text-xs border-[rgba(59,130,246,0.3)] text-[#3B82F6]">
                                    {alt.area}
                                  </Badge>
                                )}
                              </div>
                              <Badge variant="outline" className="text-xs border-[rgba(244,208,63,0.2)] text-[#B8BCC8]">
                                {Math.round(alt.confidence * 100)}%
                              </Badge>
                            </motion.div>
                          ))}
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                )}

                {feedbackGiven && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="flex items-center space-x-2 text-green-400 text-xs"
                  >
                    <ThumbsUp className="w-3 h-3" />
                    <span>Thank you for the feedback!</span>
                  </motion.div>
                )}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Manual Override - only show when no AI categorization or when user wants to override */}
          {(!categorizationResult || (categorizationResult && showAlternatives)) && (
            <div className="space-y-3">
              {categorizationResult && (
                <div className="text-xs text-[#B8BCC8] flex items-center space-x-2">
                  <span>Manual Override:</span>
                </div>
              )}
              <div className="grid grid-cols-3 gap-3">
                <Select value={selectedPillar} onValueChange={setSelectedPillar}>
                  <SelectTrigger className="bg-[#0B0D14] border-[rgba(244,208,63,0.2)] text-white">
                    <SelectValue placeholder="Pillar" />
                  </SelectTrigger>
                  <SelectContent className="glassmorphism-card border-0 bg-[#1A1D29] text-white">
                    {pillars.map((pillar) => (
                      <SelectItem key={pillar.id} value={pillar.name}>
                        {pillar.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>

                <Select value={selectedArea} onValueChange={setSelectedArea}>
                  <SelectTrigger className="bg-[#0B0D14] border-[rgba(244,208,63,0.2)] text-white">
                    <SelectValue placeholder="Area" />
                  </SelectTrigger>
                  <SelectContent className="glassmorphism-card border-0 bg-[#1A1D29] text-white">
                    <SelectItem value="general">General</SelectItem>
                    {/* TODO: Add dynamic areas based on selected pillar */}
                  </SelectContent>
                </Select>

                <Select value={selectedProject} onValueChange={setSelectedProject}>
                  <SelectTrigger className="bg-[#0B0D14] border-[rgba(244,208,63,0.2)] text-white">
                    <SelectValue placeholder="Project" />
                  </SelectTrigger>
                  <SelectContent className="glassmorphism-card border-0 bg-[#1A1D29] text-white">
                    <SelectItem value="none">No Project</SelectItem>
                    {/* TODO: Add dynamic projects based on selected area */}
                  </SelectContent>
                </Select>
              </div>
            </div>
          )}

          {/* RAG Learning Stats (Optional Debug Info) */}
          {process.env.NODE_ENV === 'development' && (
            <div className="glassmorphism-subtle p-3 rounded-lg">
              <div className="text-xs text-[#B8BCC8] space-y-1">
                <div className="flex items-center justify-between">
                  <span>RAG Learning Progress:</span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      const stats = ragCategorizationService.getLearningStats();
                      console.log('RAG Stats:', stats);
                      showSuccess(`${stats.totalItems} items learned, ${Math.round(stats.accuracy * 100)}% accuracy`);
                    }}
                    className="text-[#B8BCC8] hover:text-white h-5 text-xs px-2"
                  >
                    View Stats
                  </Button>
                </div>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex items-center justify-between">
            <Button
              variant="ghost"
              onClick={closeQuickCapture}
              className="text-[#B8BCC8] hover:text-white hover:bg-[rgba(244,208,63,0.1)]"
            >
              <X className="w-4 h-4 mr-2" />
              Cancel
            </Button>

            <Button
              onClick={handleSubmit}
              disabled={!content.trim()}
              className="aurum-gradient text-[#0B0D14] hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed min-w-[100px]"
            >
              <Send className="w-4 h-4 mr-2" />
              Capture
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}