import React, { useState } from 'react';
import { X, ArrowRight, ArrowLeft, CheckCircle, User, Briefcase, GraduationCap, Sparkles } from 'lucide-react';
import { ONBOARDING_TEMPLATES } from '../data/onboardingTemplates';
import { api } from '../services/api';
import { useDataContext } from '../contexts/DataContext';
import HierarchyIntroduction from './HierarchyIntroduction';

const OnboardingWizard = ({ onComplete, onClose }) => {
  const { onDataMutation } = useDataContext();
  const [currentStep, setCurrentStep] = useState(0);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [isApplying, setIsApplying] = useState(false);
  const [error, setError] = useState('');

  // Wizard steps
  const steps = [
    'hierarchy-introduction',  // New first step
    'welcome',
    'template-selection',
    'confirmation',
    'applying'
  ];

  const templateOptions = [
    {
      key: 'student',
      ...ONBOARDING_TEMPLATES.student,
      description: 'Perfect for students balancing academics, career prep, and personal growth'
    },
    {
      key: 'entrepreneur', 
      ...ONBOARDING_TEMPLATES.entrepreneur,
      description: 'Ideal for founders and entrepreneurs building businesses while maintaining personal life'
    },
    {
      key: 'busy_employee',
      ...ONBOARDING_TEMPLATES.busy_employee,
      description: 'Great for working professionals seeking career advancement and work-life balance'
    }
  ];

  const applyTemplate = async (templateData) => {
    try {
      setIsApplying(true);
      setError('');
      console.log('🎯 Onboarding: Starting template application...', templateData.name);

      // Create entities in the correct hierarchical order
      for (const pillarData of templateData.pillars) {
        // 1. Create Pillar
        console.log('🏛️ Creating pillar:', pillarData.name);
        const pillarResponse = await api.post('/pillars', {
          name: pillarData.name,
          description: pillarData.description,
          icon: pillarData.icon,
          color: pillarData.color,
          time_allocation_percentage: pillarData.time_allocation_percentage || null
        });
        
        const pillarId = pillarResponse.data.id;
        onDataMutation('pillar', 'create', pillarResponse.data);

        // 2. Create Areas within this Pillar
        for (const areaData of pillarData.areas) {
          console.log('🎯 Creating area:', areaData.name);
          const areaResponse = await api.post('/areas', {
            name: areaData.name,
            description: areaData.description,
            icon: areaData.icon,
            color: areaData.color,
            importance: areaData.importance,
            pillar_id: pillarId
          });
          
          const areaId = areaResponse.data.id;
          onDataMutation('area', 'create', areaResponse.data);

          // 3. Create Projects within this Area
          for (const projectData of areaData.projects) {
            console.log('📁 Creating project:', projectData.name);
            const projectResponse = await api.post('/projects', {
              name: projectData.name,
              description: projectData.description,
              icon: projectData.icon,
              priority: projectData.priority,
              importance: projectData.importance,
              status: 'Not Started',
              area_id: areaId
            });
            
            const projectId = projectResponse.data.id;
            onDataMutation('project', 'create', projectResponse.data);

            // 4. Create Tasks within this Project
            for (const taskData of projectData.tasks) {
              console.log('✅ Creating task:', taskData.name);
              const taskResponse = await api.post('/tasks', {
                name: taskData.name,
                description: taskData.description,
                priority: taskData.priority,
                status: 'todo',
                project_id: projectId
              });
              
              onDataMutation('task', 'create', taskResponse.data);
            }
          }
        }
      }

      console.log('🎉 Onboarding: Template application completed successfully!');
      
      // Mark onboarding as completed in backend
      try {
        await api.post('/api/auth/complete-onboarding');
        console.log('✅ Onboarding marked as completed in backend');
      } catch (onboardingError) {
        console.error('⚠️ Failed to mark onboarding as completed:', onboardingError);
        // Don't fail the entire onboarding for this
      }
      
      // Move to completion step
      setCurrentStep(steps.length - 1);
      
      // Complete onboarding after a brief delay
      setTimeout(async () => {
        try {
          console.log('🚀 Calling onComplete callback...');
          await onComplete();
          console.log('✅ OnComplete callback finished successfully');
        } catch (callbackError) {
          console.error('🚨 Error in onComplete callback:', callbackError);
          // Still try to continue even if callback fails
          const callbackErrorMessage = 'Onboarding completed but there was an error navigating. You can close this dialog.';
          setError(String(callbackErrorMessage));
        }
      }, 2000);

    } catch (err) {
      console.error('🚨 Onboarding: Template application failed:', err);
      
      // Extract user-friendly error message from API response
      let errorMessage = 'Failed to apply template. Please try again.';
      
      if (err.response?.data) {
        const responseData = err.response.data;
        
        // Handle 422 validation errors (Pydantic validation response)
        if (err.response.status === 422 && responseData.detail) {
          if (Array.isArray(responseData.detail)) {
            // Extract first validation error message
            const firstError = responseData.detail[0];
            if (firstError && firstError.msg) {
              errorMessage = `Validation error: ${firstError.msg}`;
            } else {
              errorMessage = 'There was a validation error with the template data. Please try again.';
            }
          } else if (typeof responseData.detail === 'string') {
            errorMessage = responseData.detail;
          }
        }
        // Handle other error types
        else if (responseData.message) {
          errorMessage = responseData.message;
        } else if (typeof responseData.detail === 'string') {
          errorMessage = responseData.detail;
        }
      }
      
      // Ensure error is always a string for React rendering
      setError(String(errorMessage));
      setIsApplying(false);
    }
  };

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleTemplateSelect = (templateKey) => {
    setSelectedTemplate(templateKey);
  };

  const handleConfirm = () => {
    if (selectedTemplate) {
      setCurrentStep(3); // Move to applying step
      applyTemplate(ONBOARDING_TEMPLATES[selectedTemplate]);
    }
  };

  const renderWelcomeStep = () => (
    <div className="text-center space-y-6">
      <div className="mx-auto w-20 h-20 bg-gradient-to-r from-yellow-400 to-yellow-600 rounded-full flex items-center justify-center mb-6">
        <Sparkles className="w-10 h-10 text-white" />
      </div>
      
      <div>
        <h2 className="text-3xl font-bold text-white mb-4">
          Welcome to Your Growth Journey!
        </h2>
        <p className="text-gray-400 text-lg max-w-2xl mx-auto leading-relaxed">
          Let's get you started with a personalized structure that matches your goals and lifestyle. 
          We'll set up your pillars, areas, projects, and tasks so you can dive right into productive organization.
        </p>
      </div>

      <div className="bg-gradient-to-r from-blue-900/30 to-purple-900/30 rounded-lg p-6 border border-blue-800/30">
        <h3 className="text-xl font-semibold text-white mb-3">What we'll create for you:</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div className="text-center">
            <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center mx-auto mb-2">
              <div className="text-2xl">🏛️</div>
            </div>
            <div className="text-white font-medium">3 Pillars</div>
            <div className="text-gray-400">Life domains</div>
          </div>
          <div className="text-center">
            <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center mx-auto mb-2">
              <div className="text-2xl">🎯</div>
            </div>
            <div className="text-white font-medium">9 Areas</div>
            <div className="text-gray-400">Focus areas</div>
          </div>
          <div className="text-center">
            <div className="w-12 h-12 bg-yellow-500/20 rounded-lg flex items-center justify-center mx-auto mb-2">
              <div className="text-2xl">📁</div>
            </div>
            <div className="text-white font-medium">9 Projects</div>
            <div className="text-gray-400">Concrete goals</div>
          </div>
          <div className="text-center">
            <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center mx-auto mb-2">
              <div className="text-2xl">✅</div>
            </div>
            <div className="text-white font-medium">27 Tasks</div>
            <div className="text-gray-400">Action items</div>
          </div>
        </div>
      </div>

      <div className="flex justify-center space-x-4">
        <button
          onClick={onClose}
          className="flex items-center space-x-2 px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
        >
          <span>Skip Onboarding</span>
        </button>
        <button
          onClick={handleNext}
          className="flex items-center space-x-2 px-8 py-3 bg-yellow-500 hover:bg-yellow-600 text-black font-semibold rounded-lg transition-colors"
        >
          <span>Let's Get Started</span>
          <ArrowRight className="w-5 h-5" />
        </button>
      </div>
    </div>
  );

  const renderTemplateSelection = () => (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-white mb-4">
          Choose Your Template
        </h2>
        <p className="text-gray-400 text-lg">
          Select the template that best matches your current life situation
        </p>
      </div>

      <div className="grid gap-6">
        {templateOptions.map((template) => (
          <div
            key={template.key}
            onClick={() => handleTemplateSelect(template.key)}
            className={`p-6 rounded-xl border-2 cursor-pointer transition-all duration-200 ${
              selectedTemplate === template.key
                ? 'border-yellow-400 bg-yellow-400/10'
                : 'border-gray-700 bg-gray-800/50 hover:border-gray-600 hover:bg-gray-800/70'
            }`}
          >
            <div className="flex items-start space-x-4">
              <div 
                className="w-16 h-16 rounded-xl flex items-center justify-center text-2xl flex-shrink-0"
                style={{ backgroundColor: template.color + '20' }}
              >
                {template.icon}
              </div>
              
              <div className="flex-1">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-xl font-semibold text-white">{template.name}</h3>
                  {selectedTemplate === template.key && (
                    <CheckCircle className="w-6 h-6 text-yellow-400" />
                  )}
                </div>
                
                <p className="text-gray-400 mb-4 leading-relaxed">
                  {template.description}
                </p>

                <div className="grid grid-cols-3 gap-4 text-sm">
                  {template.pillars.map((pillar, index) => (
                    <div key={index} className="text-center">
                      <div className="text-lg mb-1">{pillar.icon}</div>
                      <div className="text-white font-medium">{pillar.name}</div>
                      <div className="text-gray-500">{pillar.areas.length} areas</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="flex justify-between">
        <div className="flex space-x-3">
          <button
            onClick={handleBack}
            className="flex items-center space-x-2 px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Back</span>
          </button>
          <button
            onClick={onClose}
            className="flex items-center space-x-2 px-6 py-3 bg-gray-600 hover:bg-gray-500 text-white rounded-lg transition-colors"
          >
            <span>Skip Onboarding</span>
          </button>
        </div>
        
        <button
          onClick={handleNext}
          disabled={!selectedTemplate}
          className={`flex items-center space-x-2 px-8 py-3 rounded-lg font-semibold transition-colors ${
            selectedTemplate
              ? 'bg-yellow-500 hover:bg-yellow-600 text-black'
              : 'bg-gray-600 text-gray-400 cursor-not-allowed'
          }`}
        >
          <span>Continue</span>
          <ArrowRight className="w-5 h-5" />
        </button>
      </div>
    </div>
  );

  const renderConfirmation = () => {
    const template = ONBOARDING_TEMPLATES[selectedTemplate];
    
    return (
      <div className="space-y-6">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to Set Up Your System?
          </h2>
          <p className="text-gray-400 text-lg">
            We'll create your personalized structure based on the <strong className="text-yellow-400">{template.name}</strong>
          </p>
        </div>

        <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
          <div className="flex items-center space-x-4 mb-6">
            <div 
              className="w-16 h-16 rounded-xl flex items-center justify-center text-2xl"
              style={{ backgroundColor: template.color + '20' }}
            >
              {template.icon}
            </div>
            <div>
              <h3 className="text-2xl font-bold text-white">{template.name}</h3>
              <p className="text-gray-400">{template.description}</p>
            </div>
          </div>

          <div className="space-y-4">
            {template.pillars.map((pillar, index) => (
              <div key={index} className="border border-gray-700 rounded-lg p-4">
                <div className="flex items-center space-x-3 mb-3">
                  <span className="text-xl">{pillar.icon}</span>
                  <h4 className="text-lg font-semibold text-white">{pillar.name}</h4>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {pillar.areas.map((area, areaIndex) => (
                    <div key={areaIndex} className="bg-gray-900/50 rounded-lg p-3">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className="text-sm">{area.icon}</span>
                        <span className="text-white font-medium text-sm">{area.name}</span>
                      </div>
                      <div className="text-xs text-gray-400">
                        {area.projects.length} project{area.projects.length !== 1 ? 's' : ''} • {' '}
                        {area.projects.reduce((sum, project) => sum + project.tasks.length, 0)} tasks
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {error && (
          <div className="bg-red-900/20 border border-red-600 rounded-lg p-4">
            <p className="text-red-400">{error}</p>
          </div>
        )}

        <div className="flex justify-between">
          <button
            onClick={handleBack}
            disabled={isApplying}
            className="flex items-center space-x-2 px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors disabled:opacity-50"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Back</span>
          </button>
          
          <button
            onClick={handleConfirm}
            disabled={isApplying}
            className="flex items-center space-x-2 px-8 py-3 bg-yellow-500 hover:bg-yellow-600 text-black font-semibold rounded-lg transition-colors disabled:opacity-50"
          >
            {isApplying ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-black"></div>
                <span>Setting Up...</span>
              </>
            ) : (
              <>
                <span>Create My System</span>
                <ArrowRight className="w-5 h-5" />
              </>
            )}
          </button>
        </div>
      </div>
    );
  };

  const renderApplying = () => (
    <div className="text-center space-y-6">
      <div className="mx-auto w-20 h-20 bg-gradient-to-r from-yellow-400 to-yellow-600 rounded-full flex items-center justify-center mb-6">
        <CheckCircle className="w-10 h-10 text-white" />
      </div>
      
      <div>
        <h2 className="text-3xl font-bold text-white mb-4">
          🎉 Your System is Ready!
        </h2>
        <p className="text-gray-400 text-lg max-w-2xl mx-auto leading-relaxed">
          We've successfully created your personalized structure. You now have pillars, areas, projects, and tasks 
          ready to help you achieve your goals. Let's start your growth journey!
        </p>
      </div>

      <div className="bg-gradient-to-r from-green-900/30 to-blue-900/30 rounded-lg p-6 border border-green-800/30">
        <h3 className="text-xl font-semibold text-white mb-3">What's next?</h3>
        <div className="space-y-2 text-gray-300">
          <p>✅ Explore your dashboard and see your new structure</p>
          <p>✅ Start working on your first tasks</p>
          <p>✅ Use the AI Coach for personalized guidance</p>
          <p>✅ Begin your daily reflection habit tomorrow</p>
        </div>
      </div>

      <div className="animate-pulse">
        <p className="text-gray-500">Taking you to your dashboard...</p>
      </div>
    </div>
  );

  const renderCurrentStep = () => {
    switch (steps[currentStep]) {
      case 'hierarchy-introduction':
        return <HierarchyIntroduction onContinue={handleNext} />;
      case 'welcome':
        return renderWelcomeStep();
      case 'template-selection':
        return renderTemplateSelection();
      case 'confirmation':
        return renderConfirmation();
      case 'applying':
        return renderApplying();
      default:
        return <HierarchyIntroduction onContinue={handleNext} />;
    }
  };

  return (
    <div className="fixed inset-0 bg-[#0B0D14] flex flex-col z-50">
      <style>{`
        .onboarding-scroll::-webkit-scrollbar {
          display: none;
        }
        .onboarding-scroll {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
      `}</style>
      <div className="w-full h-full overflow-y-auto onboarding-scroll">
        {/* Header */}
        <div className="flex-shrink-0 flex items-center justify-between p-6 border-b border-gray-800/50 bg-gray-900/30 backdrop-blur-sm">
          <div className="flex items-center space-x-3">
            <div className="bg-yellow-500 text-black px-3 py-1 rounded-lg font-bold text-lg">
              AL
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">Smart Onboarding</h1>
              <p className="text-gray-400 text-sm">
                Step {currentStep + 1} of {steps.length}
              </p>
            </div>
          </div>
          
          {/* Progress Bar */}
          <div className="flex-1 mx-6">
            <div className="bg-gray-700 rounded-full h-2">
              <div 
                className="bg-yellow-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
              />
            </div>
          </div>

          {/* Close/Skip button - always available */}
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-white rounded-lg hover:bg-gray-800 transition-colors"
            title={currentStep === 0 ? "Close" : "Skip Onboarding"}
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto onboarding-scroll p-8 min-h-0">
          <div className="max-w-4xl mx-auto">
            {renderCurrentStep()}
          </div>
        </div>
      </div>
    </div>
  );
};

export default OnboardingWizard;