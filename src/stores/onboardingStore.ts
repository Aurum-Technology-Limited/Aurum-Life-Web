import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface OnboardingState {
  // Flow control
  isOnboardingComplete: boolean;
  currentStep: number;
  totalSteps: number;
  
  // User data collected during onboarding
  userData: {
    firstName: string;
    lastName: string;
    displayName: string;
    birthDate: string;
    howDidYouHear: string;
    motivations: string[];
  };
  
  // Template selection
  selectedTemplate: {
    id: string;
    name: string;
    description: string;
    pillars: string[];
  } | null;
  
  // Question-based template matching
  questionResponses: {
    isStudent: boolean | null;
    isBuildingCareer: boolean | null;
    hasFamily: boolean | null;
    isEntrepreneur: boolean | null;
    prioritizesWellness: boolean | null;
    isHighAchiever: boolean | null;
    careerStage: string;
    primaryFocus: string[];
    lifePhase: string;
  };
  
  // Pillar creation
  customPillars: Array<{
    id: string;
    name: string;
    description: string;
    icon: string;
    color: string;
  }>;
  
  // AI preferences
  aiPreferences: {
    personality: string;
    frequency: string;
    timing: string;
    communicationStyle: string;
    focusAreas: string[];
    enabledFeatures: {
      smartPrioritization: boolean;
      progressTracking: boolean;
      emotionalRecognition: boolean;
      habitSuggestions: boolean;
      focusOptimization: boolean;
    };
  };
  
  // Emotional baseline
  emotionalBaseline: {
    currentMood: string;
    energyLevel: number;
    stressLevel: number;
    emotionalGoals: string[];
    patterns: {
      productiveTime: string;
      moodFactors: string[];
      processingStyle: string;
    };
  };
  
  // PAPT Framework Understanding
  paptUnderstanding: {
    hasViewedExplanation: boolean;
    completedQuiz: boolean;
    skippedEducation: boolean;
    timeSpentOnEducation: number;
  };
  
  // Tour progress
  tourProgress: {
    completedSections: string[];
    skippedTour: boolean;
  };
  
  // Actions
  nextStep: () => void;
  previousStep: () => void;
  goToStep: (step: number) => void;
  updateUserData: (data: Partial<OnboardingState['userData']>) => void;
  setSelectedTemplate: (template: OnboardingState['selectedTemplate']) => void;
  updateQuestionResponses: (responses: Partial<OnboardingState['questionResponses']>) => void;
  updatePillars: (pillars: OnboardingState['customPillars']) => void;
  updateAIPreferences: (preferences: Partial<OnboardingState['aiPreferences']>) => void;
  updateEmotionalBaseline: (baseline: Partial<OnboardingState['emotionalBaseline']>) => void;
  updatePAPTUnderstanding: (understanding: Partial<OnboardingState['paptUnderstanding']>) => void;
  updateTourProgress: (progress: Partial<OnboardingState['tourProgress']>) => void;
  completeOnboarding: () => void;
  resetOnboarding: () => void;
  initializeFromUser: (user: { email: string }) => void;
}

const initialState = {
  isOnboardingComplete: false,
  currentStep: 1,
  totalSteps: 6, // Adjusted for user data existing + 2 new educational steps
  userData: {
    firstName: '', // Will be populated during onboarding
    lastName: '',
    displayName: '',
    birthDate: '',
    howDidYouHear: '',
    motivations: [],
  },
  selectedTemplate: null,
  questionResponses: {
    isStudent: null,
    isBuildingCareer: null,
    hasFamily: null,
    isEntrepreneur: null,
    prioritizesWellness: null,
    isHighAchiever: null,
    careerStage: '',
    primaryFocus: [],
    lifePhase: '',
  },
  customPillars: [],
  aiPreferences: {
    personality: 'supportive',
    frequency: 'daily',
    timing: 'morning',
    communicationStyle: 'detailed',
    focusAreas: [],
    enabledFeatures: {
      smartPrioritization: true,
      progressTracking: true,
      emotionalRecognition: true,
      habitSuggestions: true,
      focusOptimization: false,
    },
  },
  emotionalBaseline: {
    currentMood: '',
    energyLevel: 5,
    stressLevel: 5,
    emotionalGoals: [],
    patterns: {
      productiveTime: '',
      moodFactors: [],
      processingStyle: '',
    },
  },
  paptUnderstanding: {
    hasViewedExplanation: false,
    completedQuiz: false,
    skippedEducation: false,
    timeSpentOnEducation: 0,
  },
  tourProgress: {
    completedSections: [],
    skippedTour: false,
  },
};

export const useOnboardingStore = create<OnboardingState>()(
  persist(
    (set, get) => ({
      ...initialState,
      
      nextStep: () => {
        const { currentStep, totalSteps } = get();
        if (currentStep < totalSteps) {
          set({ currentStep: currentStep + 1 });
        }
      },
      
      previousStep: () => {
        const { currentStep } = get();
        if (currentStep > 1) {
          set({ currentStep: currentStep - 1 });
        }
      },
      
      goToStep: (step: number) => {
        const { totalSteps } = get();
        if (step >= 1 && step <= totalSteps) {
          set({ currentStep: step });
        }
      },
      
      updateUserData: (data) => {
        set((state) => ({
          userData: { ...state.userData, ...data }
        }));
      },
      
      setSelectedTemplate: (template) => {
        set({ selectedTemplate: template });
      },
      
      updateQuestionResponses: (responses) => {
        set((state) => ({
          questionResponses: { ...state.questionResponses, ...responses }
        }));
      },
      
      updatePillars: (pillars) => {
        set({ customPillars: pillars });
      },
      
      updateAIPreferences: (preferences) => {
        set((state) => ({
          aiPreferences: { ...state.aiPreferences, ...preferences }
        }));
      },
      
      updateEmotionalBaseline: (baseline) => {
        set((state) => ({
          emotionalBaseline: { ...state.emotionalBaseline, ...baseline }
        }));
      },
      
      updatePAPTUnderstanding: (understanding) => {
        set((state) => ({
          paptUnderstanding: { ...state.paptUnderstanding, ...understanding }
        }));
      },
      
      updateTourProgress: (progress) => {
        set((state) => ({
          tourProgress: { ...state.tourProgress, ...progress }
        }));
      },
      
      completeOnboarding: () => {
        set({ isOnboardingComplete: true });
      },
      
      resetOnboarding: () => {
        set(initialState);
      },
      
      initializeFromUser: (user) => {
        // No longer initialize name from user since it will be collected in onboarding
        // This method can be used for other user-specific initialization if needed in the future
        console.log('User initialized for onboarding:', user.email);
      },
    }),
    {
      name: 'aurum-onboarding',
      partialize: (state) => ({
        isOnboardingComplete: state.isOnboardingComplete,
        userData: state.userData,
        selectedTemplate: state.selectedTemplate,
        questionResponses: state.questionResponses,
        customPillars: state.customPillars,
        aiPreferences: state.aiPreferences,
        emotionalBaseline: state.emotionalBaseline,
        paptUnderstanding: state.paptUnderstanding,
      }),
    }
  )
);