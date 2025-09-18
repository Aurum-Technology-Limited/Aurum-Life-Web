import { useEffect } from 'react';
import { useEnhancedFeaturesStore } from '../../stores/enhancedFeaturesStore';
import { Pillar, Area, Project, Task } from '../../types/enhanced-features';

export default function SampleDataInitializer() {
  const { 
    addPillar, 
    addAchievement, 
    addSmartSuggestion, 
    updateEnergyPattern,
    addTimeBlock,
    pillars 
  } = useEnhancedFeaturesStore();

  useEffect(() => {
    // Only add sample data if no pillars exist
    if (pillars.length === 0) {
      // Create comprehensive hierarchical data structure
      const healthPillarId = crypto.randomUUID();
      const careerPillarId = crypto.randomUUID();
      const relationshipsPillarId = crypto.randomUUID();
      const personalDevPillarId = crypto.randomUUID();
      const financialPillarId = crypto.randomUUID();
      const homePillarId = crypto.randomUUID();

      // Health & Wellness Areas
      const fitnessAreaId = crypto.randomUUID();
      const nutritionAreaId = crypto.randomUUID();
      const mentalHealthAreaId = crypto.randomUUID();
      const sleepAreaId = crypto.randomUUID();

      // Career Areas
      const skillDevAreaId = crypto.randomUUID();
      const networkingAreaId = crypto.randomUUID();
      const leadershipAreaId = crypto.randomUUID();

      // Relationships Areas
      const familyAreaId = crypto.randomUUID();
      const friendsAreaId = crypto.randomUUID();

      // Personal Development Areas
      const technicalSkillsAreaId = crypto.randomUUID();
      const personalGrowthAreaId = crypto.randomUUID();

      // Financial Areas
      const budgetingAreaId = crypto.randomUUID();
      const investmentsAreaId = crypto.randomUUID();
      const emergencyFundAreaId = crypto.randomUUID();

      // Home Areas
      const organizationAreaId = crypto.randomUUID();
      const sustainabilityAreaId = crypto.randomUUID();

      // Projects - Health & Wellness
      const marathonProjectId = crypto.randomUUID();
      const strengthTrainingProjectId = crypto.randomUUID();
      const yogaProjectId = crypto.randomUUID();
      const mealPrepProjectId = crypto.randomUUID();
      const nutritionTrackingProjectId = crypto.randomUUID();
      const meditationProjectId = crypto.randomUUID();
      const therapyProjectId = crypto.randomUUID();
      const sleepOptimizationProjectId = crypto.randomUUID();
      const recoveryProjectId = crypto.randomUUID();

      // Projects - Career & Professional
      const reactAppProjectId = crypto.randomUUID();
      const certificationProjectId = crypto.randomUUID();
      const conferenceProjectId = crypto.randomUUID();
      const mentorshipProjectId = crypto.randomUUID();
      const teamLeadershipProjectId = crypto.randomUUID();
      const presentationProjectId = crypto.randomUUID();

      // Projects - Relationships
      const familyDinnersProjectId = crypto.randomUUID();
      const dateNightProjectId = crypto.randomUUID();
      const friendsReconnectProjectId = crypto.randomUUID();
      const socialEventsProjectId = crypto.randomUUID();

      // Projects - Personal Development
      const mlCourseProjectId = crypto.randomUUID();
      const readingProjectId = crypto.randomUUID();
      const languageProjectId = crypto.randomUUID();
      const reflectionProjectId = crypto.randomUUID();

      // Projects - Financial Wellness
      const budgetSystemProjectId = crypto.randomUUID();
      const debtPayoffProjectId = crypto.randomUUID();
      const portfolioProjectId = crypto.randomUUID();
      const retirementProjectId = crypto.randomUUID();
      const emergencyFundProjectId = crypto.randomUUID();
      const insuranceProjectId = crypto.randomUUID();

      // Projects - Home & Environment
      const officeSetupProjectId = crypto.randomUUID();
      const bedroomOrgProjectId = crypto.randomUUID();
      const solarProjectId = crypto.randomUUID();
      const gardenProjectId = crypto.randomUUID();

      // Create tasks for projects
      const createTasks = (projectId: string, taskData: Array<{name: string, description?: string, status?: 'todo' | 'in-progress' | 'completed', priority?: 'low' | 'medium' | 'high' | 'urgent', estimatedHours?: number, tags?: string[]}>) => {
        return taskData.map(task => ({
          id: crypto.randomUUID(),
          projectId,
          name: task.name,
          description: task.description || '',
          status: task.status || 'todo',
          priority: task.priority || 'medium',
          estimatedHours: task.estimatedHours || 1,
          actualHours: task.status === 'completed' ? (task.estimatedHours || 1) : undefined,
          dueDate: new Date(Date.now() + Math.random() * 30 * 24 * 60 * 60 * 1000), // Random date in next 30 days
          completedAt: task.status === 'completed' ? new Date() : undefined,
          tags: task.tags || []
        } as Task));
      };

      // Create sample attachments for demonstration
      const createSampleAttachments = (projectName: string) => {
        const sampleAttachments = {
          'React Native Mobile App': [
            {
              id: crypto.randomUUID(),
              fileName: 'app-wireframes.pdf',
              originalName: 'App Wireframes and Design.pdf',
              fileSize: 2457600, // ~2.4MB
              fileType: 'application/pdf',
              uploadedAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000), // 5 days ago
              uploadedBy: 'current-user'
            },
            {
              id: crypto.randomUUID(),
              fileName: 'api-documentation.md',
              originalName: 'API Documentation.md',
              fileSize: 15360, // ~15KB
              fileType: 'text/markdown',
              uploadedAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000), // 2 days ago
              uploadedBy: 'current-user'
            }
          ],
          'Quarterly Presentation': [
            {
              id: crypto.randomUUID(),
              fileName: 'q3-metrics.xlsx',
              originalName: 'Q3 Team Metrics.xlsx',
              fileSize: 524288, // 512KB
              fileType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
              uploadedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000), // 1 day ago
              uploadedBy: 'current-user'
            }
          ],
          'Meal Prep System': [
            {
              id: crypto.randomUUID(),
              fileName: 'meal-plan-template.png',
              originalName: 'Weekly Meal Plan Template.png',
              fileSize: 1048576, // 1MB
              fileType: 'image/png',
              uploadedAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000), // 3 days ago
              uploadedBy: 'current-user'
            }
          ]
        };
        
        return sampleAttachments[projectName as keyof typeof sampleAttachments] || [];
      };

      // Create Projects with Tasks
      const createProjects = (areaId: string, projectData: Array<{name: string, description: string, status?: 'planning' | 'active' | 'paused' | 'completed', priority?: 'low' | 'medium' | 'high' | 'urgent', tasks: Array<any>}>) => {
        const projectIdMap: Record<string, string> = {
          'Marathon Training Program': marathonProjectId,
          'Strength Training Routine': strengthTrainingProjectId,
          'Morning Yoga Practice': yogaProjectId,
          'Meal Prep System': mealPrepProjectId,
          'Nutrition Tracking': nutritionTrackingProjectId,
          'Daily Meditation Practice': meditationProjectId,
          'Therapy Sessions': therapyProjectId,
          'Sleep Optimization': sleepOptimizationProjectId,
          'Recovery Protocol': recoveryProjectId,
          'React Native Mobile App': reactAppProjectId,
          'AWS Cloud Certification': certificationProjectId,
          'Tech Conference Speaking': conferenceProjectId,
          'Mentorship Program': mentorshipProjectId,
          'Team Leadership Development': teamLeadershipProjectId,
          'Quarterly Presentation': presentationProjectId,
          'Weekly Family Dinners': familyDinnersProjectId,
          'Monthly Date Nights': dateNightProjectId,
          'Friends Reconnection': friendsReconnectProjectId,
          'Social Events Planning': socialEventsProjectId,
          'Machine Learning Course': mlCourseProjectId,
          'Reading Challenge': readingProjectId,
          'Spanish Learning': languageProjectId,
          'Daily Reflection': reflectionProjectId,
          'Budget Management System': budgetSystemProjectId,
          'Debt Payoff Plan': debtPayoffProjectId,
          'Investment Portfolio Review': portfolioProjectId,
          'Retirement Planning': retirementProjectId,
          'Emergency Fund Building': emergencyFundProjectId,
          'Insurance Review': insuranceProjectId,
          'Home Office Setup': officeSetupProjectId,
          'Bedroom Organization': bedroomOrgProjectId,
          'Solar Panel Installation': solarProjectId,
          'Vegetable Garden': gardenProjectId
        };

        return projectData.map(project => ({
          id: projectIdMap[project.name] || crypto.randomUUID(),
          areaId,
          name: project.name,
          description: project.description,
          status: project.status || 'active',
          priority: project.priority || 'medium',
          dueDate: new Date(Date.now() + Math.random() * 90 * 24 * 60 * 60 * 1000), // Random date in next 90 days
          completedAt: project.status === 'completed' ? new Date() : undefined,
          tasks: project.tasks,
          impactScore: Math.floor(Math.random() * 6) + 5, // 5-10
          attachments: createSampleAttachments(project.name) // Add sample attachments for demo
        } as Project));
      };

      // Create Areas with Projects
      const createAreas = (pillarId: string, areaData: Array<{name: string, description: string, projects: Array<any>}>) => {
        return areaData.map(area => ({
          id: area.name === 'Fitness & Exercise' ? fitnessAreaId :
              area.name === 'Nutrition' ? nutritionAreaId :
              area.name === 'Mental Health' ? mentalHealthAreaId :
              area.name === 'Sleep & Recovery' ? sleepAreaId :
              area.name === 'Skill Development' ? skillDevAreaId :
              area.name === 'Network Building' ? networkingAreaId :
              area.name === 'Leadership' ? leadershipAreaId :
              area.name === 'Family' ? familyAreaId :
              area.name === 'Friends' ? friendsAreaId :
              area.name === 'Technical Skills' ? technicalSkillsAreaId :
              area.name === 'Personal Growth' ? personalGrowthAreaId :
              area.name === 'Budgeting' ? budgetingAreaId :
              area.name === 'Investments' ? investmentsAreaId :
              area.name === 'Emergency Fund' ? emergencyFundAreaId :
              area.name === 'Organization' ? organizationAreaId :
              area.name === 'Sustainability' ? sustainabilityAreaId :
              crypto.randomUUID(),
          pillarId,
          name: area.name,
          description: area.description,
          healthScore: Math.floor(Math.random() * 30) + 70, // 70-100
          projects: area.projects
        } as Area));
      };

      // Build the complete data structure
      const samplePillars: Omit<Pillar, 'id' | 'lastUpdated'>[] = [
        {
          name: 'Health & Wellness',
          description: 'Physical and mental well-being foundation',
          color: '#10B981',
          icon: 'Heart',
          healthScore: 85,
          weeklyTimeTarget: 10,
          weeklyTimeActual: 8.5,
          streak: 12,
          areas: createAreas(healthPillarId, [
            {
              name: 'Fitness & Exercise',
              description: 'Physical fitness and workout routines',
              projects: createProjects(fitnessAreaId, [
                {
                  name: 'Marathon Training Program',
                  description: 'Complete 26.2 mile marathon in 6 months',
                  status: 'active',
                  priority: 'high',
                  tasks: createTasks(marathonProjectId, [
                    { name: 'Week 8: 5km morning run', status: 'completed', priority: 'medium', estimatedHours: 1, tags: ['running', 'cardio'] },
                    { name: 'Week 8: Long run 15km', status: 'in-progress', priority: 'high', estimatedHours: 2, tags: ['running', 'endurance'] },
                    { name: 'Strength training session', status: 'todo', priority: 'medium', estimatedHours: 1, tags: ['strength', 'gym'] },
                    { name: 'Rest day with light stretching', status: 'todo', priority: 'low', estimatedHours: 0.5, tags: ['recovery', 'stretching'] },
                    { name: 'Week 9: Hill training intervals', status: 'todo', priority: 'high', estimatedHours: 1.5, tags: ['running', 'intervals'] },
                    { name: 'Update running log and metrics', status: 'todo', priority: 'low', estimatedHours: 0.25, tags: ['tracking', 'analysis'] }
                  ])
                },
                {
                  name: 'Strength Training Routine',
                  description: 'Build muscle mass and overall strength',
                  status: 'active',
                  priority: 'medium',
                  tasks: createTasks(strengthTrainingProjectId, [
                    { name: 'Upper body workout - chest & triceps', status: 'completed', priority: 'medium', estimatedHours: 1, tags: ['strength', 'upper-body'] },
                    { name: 'Lower body workout - legs & glutes', status: 'todo', priority: 'medium', estimatedHours: 1, tags: ['strength', 'lower-body'] },
                    { name: 'Core strength session', status: 'todo', priority: 'medium', estimatedHours: 0.5, tags: ['strength', 'core'] },
                    { name: 'Progressive overload planning', status: 'todo', priority: 'low', estimatedHours: 0.5, tags: ['planning', 'progression'] }
                  ])
                },
                {
                  name: 'Morning Yoga Practice',
                  description: 'Daily yoga for flexibility and mindfulness',
                  status: 'active',
                  priority: 'medium',
                  tasks: createTasks(yogaProjectId, [
                    { name: '20-minute morning flow', status: 'completed', priority: 'medium', estimatedHours: 0.33, tags: ['yoga', 'flexibility'] },
                    { name: 'Evening restorative yoga', status: 'todo', priority: 'low', estimatedHours: 0.5, tags: ['yoga', 'relaxation'] },
                    { name: 'Weekend longer yoga session', status: 'todo', priority: 'medium', estimatedHours: 1, tags: ['yoga', 'deep-practice'] }
                  ])
                }
              ])
            },
            {
              name: 'Nutrition',
              description: 'Healthy eating habits and meal planning',
              projects: createProjects(nutritionAreaId, [
                {
                  name: 'Meal Prep System',
                  description: 'Establish weekly meal preparation routine',
                  status: 'active',
                  priority: 'medium',
                  tasks: createTasks(mealPrepProjectId, [
                    { name: 'Plan weekly meals', status: 'completed', priority: 'medium', estimatedHours: 1, tags: ['planning', 'nutrition'] },
                    { name: 'Grocery shopping', status: 'todo', priority: 'medium', estimatedHours: 1.5, tags: ['shopping', 'nutrition'] },
                    { name: 'Sunday meal prep session', status: 'todo', priority: 'high', estimatedHours: 3, tags: ['cooking', 'prep'] },
                    { name: 'Prep healthy snacks for week', status: 'todo', priority: 'medium', estimatedHours: 0.5, tags: ['prep', 'snacks'] },
                    { name: 'Clean and organize meal prep containers', status: 'todo', priority: 'low', estimatedHours: 0.25, tags: ['organization', 'cleaning'] }
                  ])
                },
                {
                  name: 'Nutrition Tracking',
                  description: 'Monitor daily macros and nutritional intake',
                  status: 'active',
                  priority: 'low',
                  tasks: createTasks(nutritionTrackingProjectId, [
                    { name: 'Log breakfast macros', status: 'completed', priority: 'low', estimatedHours: 0.1, tags: ['tracking', 'macros'] },
                    { name: 'Log lunch and snacks', status: 'in-progress', priority: 'low', estimatedHours: 0.1, tags: ['tracking', 'macros'] },
                    { name: 'Weekly nutrition review', status: 'todo', priority: 'medium', estimatedHours: 0.5, tags: ['review', 'analysis'] },
                    { name: 'Adjust meal plan based on results', status: 'todo', priority: 'medium', estimatedHours: 0.5, tags: ['planning', 'optimization'] }
                  ])
                }
              ])
            },
            {
              name: 'Mental Health',
              description: 'Emotional well-being and stress management',
              projects: createProjects(mentalHealthAreaId, [
                {
                  name: 'Daily Meditation Practice',
                  description: 'Establish consistent mindfulness routine',
                  status: 'active',
                  priority: 'medium',
                  tasks: createTasks(meditationProjectId, [
                    { name: '10-minute morning meditation', status: 'completed', priority: 'medium', estimatedHours: 0.25, tags: ['meditation', 'mindfulness'] },
                    { name: 'Evening gratitude journal', status: 'todo', priority: 'low', estimatedHours: 0.25, tags: ['gratitude', 'journaling'] },
                    { name: 'Breathing exercise before meetings', status: 'in-progress', priority: 'medium', estimatedHours: 0.1, tags: ['breathing', 'stress-relief'] },
                    { name: 'Weekend longer meditation session', status: 'todo', priority: 'low', estimatedHours: 0.5, tags: ['meditation', 'deep-practice'] }
                  ])
                },
                {
                  name: 'Therapy Sessions',
                  description: 'Regular mental health check-ins with therapist',
                  status: 'active',
                  priority: 'high',
                  tasks: createTasks(therapyProjectId, [
                    { name: 'Schedule next therapy appointment', status: 'completed', priority: 'high', estimatedHours: 0.1, tags: ['therapy', 'scheduling'] },
                    { name: 'Prepare topics for discussion', status: 'todo', priority: 'medium', estimatedHours: 0.25, tags: ['therapy', 'preparation'] },
                    { name: 'Practice homework exercises', status: 'todo', priority: 'medium', estimatedHours: 0.5, tags: ['therapy', 'practice'] },
                    { name: 'Reflect on session insights', status: 'todo', priority: 'low', estimatedHours: 0.25, tags: ['therapy', 'reflection'] }
                  ])
                }
              ])
            },
            {
              name: 'Sleep & Recovery',
              description: 'Quality sleep and recovery optimization',
              projects: createProjects(sleepAreaId, [
                {
                  name: 'Sleep Optimization',
                  description: 'Improve sleep quality and consistency',
                  status: 'active',
                  priority: 'high',
                  tasks: createTasks(sleepOptimizationProjectId, [
                    { name: 'Set consistent bedtime routine', status: 'in-progress', priority: 'high', estimatedHours: 0.25, tags: ['sleep', 'routine'] },
                    { name: 'Remove screens 1 hour before bed', status: 'todo', priority: 'medium', estimatedHours: 0, tags: ['sleep', 'hygiene'] },
                    { name: 'Track sleep with fitness tracker', status: 'completed', priority: 'low', estimatedHours: 0.1, tags: ['sleep', 'tracking'] },
                    { name: 'Create optimal bedroom environment', status: 'todo', priority: 'medium', estimatedHours: 1, tags: ['sleep', 'environment'] }
                  ])
                },
                {
                  name: 'Recovery Protocol',
                  description: 'Active recovery and rest days management',
                  status: 'active',
                  priority: 'medium',
                  tasks: createTasks(recoveryProjectId, [
                    { name: 'Foam rolling session', status: 'todo', priority: 'medium', estimatedHours: 0.25, tags: ['recovery', 'mobility'] },
                    { name: 'Ice bath or cold shower', status: 'todo', priority: 'low', estimatedHours: 0.1, tags: ['recovery', 'cold-therapy'] },
                    { name: 'Schedule massage appointment', status: 'todo', priority: 'low', estimatedHours: 0.1, tags: ['recovery', 'massage'] }
                  ])
                }
              ])
            }
          ])
        },
        {
          name: 'Career & Professional',
          description: 'Professional growth, skills, and achievements',
          color: '#3B82F6',
          icon: 'Briefcase',
          healthScore: 72,
          weeklyTimeTarget: 40,
          weeklyTimeActual: 42,
          streak: 5,
          areas: createAreas(careerPillarId, [
            {
              name: 'Skill Development',
              description: 'Learning new technologies and frameworks',
              projects: createProjects(skillDevAreaId, [
                {
                  name: 'React Native Mobile App',
                  description: 'Build and deploy iOS/Android productivity app',
                  status: 'active',
                  priority: 'high',
                  tasks: createTasks(reactAppProjectId, [
                    { name: 'Complete React component refactoring', status: 'in-progress', priority: 'high', estimatedHours: 4, tags: ['development', 'refactoring'] },
                    { name: 'Implement user authentication', status: 'todo', priority: 'high', estimatedHours: 6, tags: ['auth', 'security'] },
                    { name: 'Build notification system', status: 'todo', priority: 'medium', estimatedHours: 3, tags: ['notifications', 'mobile'] },
                    { name: 'App store submission prep', status: 'todo', priority: 'medium', estimatedHours: 2, tags: ['deployment', 'mobile'] },
                    { name: 'Write unit tests for core features', status: 'todo', priority: 'medium', estimatedHours: 4, tags: ['testing', 'quality'] },
                    { name: 'Performance optimization', status: 'todo', priority: 'low', estimatedHours: 3, tags: ['performance', 'optimization'] }
                  ])
                },
                {
                  name: 'AWS Cloud Certification',
                  description: 'Study for AWS Solutions Architect certification',
                  status: 'active',
                  priority: 'medium',
                  tasks: createTasks(certificationProjectId, [
                    { name: 'Complete EC2 and VPC modules', status: 'completed', priority: 'high', estimatedHours: 3, tags: ['aws', 'study'] },
                    { name: 'Practice labs for IAM and S3', status: 'in-progress', priority: 'high', estimatedHours: 2, tags: ['aws', 'hands-on'] },
                    { name: 'Take practice exam #1', status: 'todo', priority: 'high', estimatedHours: 2, tags: ['aws', 'exam'] },
                    { name: 'Review weak areas from practice exam', status: 'todo', priority: 'medium', estimatedHours: 2, tags: ['aws', 'review'] },
                    { name: 'Schedule certification exam', status: 'todo', priority: 'medium', estimatedHours: 0.25, tags: ['aws', 'scheduling'] }
                  ])
                }
              ])
            },
            {
              name: 'Network Building',
              description: 'Professional networking and relationships',
              projects: createProjects(networkingAreaId, [
                {
                  name: 'Tech Conference Speaking',
                  description: 'Present at major tech conference on React best practices',
                  status: 'active',
                  priority: 'high',
                  tasks: createTasks(conferenceProjectId, [
                    { name: 'Finalize presentation outline', status: 'completed', priority: 'high', estimatedHours: 2, tags: ['speaking', 'preparation'] },
                    { name: 'Create slide deck', status: 'in-progress', priority: 'high', estimatedHours: 4, tags: ['speaking', 'slides'] },
                    { name: 'Practice presentation with team', status: 'todo', priority: 'medium', estimatedHours: 1, tags: ['speaking', 'practice'] },
                    { name: 'Book travel and accommodation', status: 'todo', priority: 'medium', estimatedHours: 0.5, tags: ['logistics', 'travel'] },
                    { name: 'Prepare networking strategy for event', status: 'todo', priority: 'low', estimatedHours: 0.5, tags: ['networking', 'strategy'] }
                  ])
                },
                {
                  name: 'Mentorship Program',
                  description: 'Mentor junior developers and expand network',
                  status: 'active',
                  priority: 'medium',
                  tasks: createTasks(mentorshipProjectId, [
                    { name: 'Weekly 1:1 with mentee Alex', status: 'completed', priority: 'high', estimatedHours: 1, tags: ['mentoring', 'weekly'] },
                    { name: 'Review mentee\'s code and provide feedback', status: 'todo', priority: 'medium', estimatedHours: 0.5, tags: ['mentoring', 'code-review'] },
                    { name: 'Connect mentee with team leads', status: 'todo', priority: 'low', estimatedHours: 0.25, tags: ['mentoring', 'networking'] },
                    { name: 'Plan career development discussion', status: 'todo', priority: 'medium', estimatedHours: 0.5, tags: ['mentoring', 'career'] }
                  ])
                }
              ])
            },
            {
              name: 'Leadership',
              description: 'Leadership skills and team management',
              projects: createProjects(leadershipAreaId, [
                {
                  name: 'Team Leadership Development',
                  description: 'Develop skills to lead engineering team effectively',
                  status: 'active',
                  priority: 'high',
                  tasks: createTasks(teamLeadershipProjectId, [
                    { name: 'Read "The Manager\'s Path" chapter 3', status: 'completed', priority: 'medium', estimatedHours: 1, tags: ['reading', 'leadership'] },
                    { name: 'Conduct team retrospective meeting', status: 'todo', priority: 'high', estimatedHours: 1, tags: ['leadership', 'meetings'] },
                    { name: 'Plan individual career conversations', status: 'todo', priority: 'high', estimatedHours: 0.5, tags: ['leadership', 'career'] },
                    { name: 'Implement new sprint planning process', status: 'in-progress', priority: 'medium', estimatedHours: 2, tags: ['leadership', 'process'] }
                  ])
                },
                {
                  name: 'Quarterly Presentation',
                  description: 'Present team achievements to executive leadership',
                  status: 'planning',
                  priority: 'high',
                  tasks: createTasks(presentationProjectId, [
                    { name: 'Gather team metrics and achievements', status: 'todo', priority: 'high', estimatedHours: 1, tags: ['presentation', 'data'] },
                    { name: 'Create executive summary deck', status: 'todo', priority: 'high', estimatedHours: 2, tags: ['presentation', 'slides'] },
                    { name: 'Practice presentation delivery', status: 'todo', priority: 'medium', estimatedHours: 0.5, tags: ['presentation', 'practice'] },
                    { name: 'Schedule presentation with executives', status: 'todo', priority: 'medium', estimatedHours: 0.1, tags: ['presentation', 'scheduling'] }
                  ])
                }
              ])
            }
          ])
        },
        {
          name: 'Relationships',
          description: 'Personal and professional connections',
          color: '#EC4899',
          icon: 'Users',
          healthScore: 90,
          weeklyTimeTarget: 15,
          weeklyTimeActual: 16,
          streak: 8,
          areas: createAreas(relationshipsPillarId, [
            {
              name: 'Family',
              description: 'Quality time and relationships with family',
              projects: createProjects(familyAreaId, [
                {
                  name: 'Weekly Family Dinners',
                  description: 'Establish regular family connection time',
                  status: 'active',
                  priority: 'high',
                  tasks: createTasks(familyDinnersProjectId, [
                    { name: 'Call mom for birthday celebration', status: 'todo', priority: 'high', estimatedHours: 1, tags: ['family', 'birthday'] },
                    { name: 'Plan Sunday family dinner', status: 'todo', priority: 'medium', estimatedHours: 0.5, tags: ['family', 'planning'] },
                    { name: 'Organize family game night', status: 'todo', priority: 'medium', estimatedHours: 1, tags: ['family', 'fun'] },
                    { name: 'Coordinate with siblings for reunion', status: 'in-progress', priority: 'medium', estimatedHours: 0.5, tags: ['family', 'reunion'] },
                    { name: 'Create family photo album', status: 'todo', priority: 'low', estimatedHours: 2, tags: ['family', 'memories'] }
                  ])
                },
                {
                  name: 'Monthly Date Nights',
                  description: 'Regular quality time with partner',
                  status: 'active',
                  priority: 'high',
                  tasks: createTasks(dateNightProjectId, [
                    { name: 'Plan romantic dinner at home', status: 'completed', priority: 'medium', estimatedHours: 1, tags: ['relationship', 'romance'] },
                    { name: 'Book tickets for concert', status: 'todo', priority: 'medium', estimatedHours: 0.25, tags: ['relationship', 'entertainment'] },
                    { name: 'Try new hiking trail together', status: 'todo', priority: 'low', estimatedHours: 3, tags: ['relationship', 'adventure'] },
                    { name: 'Schedule couples massage', status: 'todo', priority: 'low', estimatedHours: 0.1, tags: ['relationship', 'relaxation'] }
                  ])
                }
              ])
            },
            {
              name: 'Friends',
              description: 'Friendships and social connections',
              projects: createProjects(friendsAreaId, [
                {
                  name: 'Friends Reconnection',
                  description: 'Reconnect with old friends and maintain relationships',
                  status: 'active',
                  priority: 'medium',
                  tasks: createTasks(friendsReconnectProjectId, [
                    { name: 'Call college friend Sarah', status: 'completed', priority: 'medium', estimatedHours: 0.5, tags: ['friends', 'reconnect'] },
                    { name: 'Organize group chat with high school friends', status: 'todo', priority: 'low', estimatedHours: 0.25, tags: ['friends', 'group'] },
                    { name: 'Plan weekend meetup with local friends', status: 'in-progress', priority: 'medium', estimatedHours: 0.5, tags: ['friends', 'planning'] },
                    { name: 'Send birthday cards to close friends', status: 'todo', priority: 'low', estimatedHours: 0.5, tags: ['friends', 'birthday'] }
                  ])
                },
                {
                  name: 'Social Events Planning',
                  description: 'Host and organize social gatherings',
                  status: 'active',
                  priority: 'low',
                  tasks: createTasks(socialEventsProjectId, [
                    { name: 'Plan board game night at home', status: 'todo', priority: 'medium', estimatedHours: 1, tags: ['social', 'games'] },
                    { name: 'Organize potluck dinner party', status: 'todo', priority: 'low', estimatedHours: 1.5, tags: ['social', 'hosting'] },
                    { name: 'Create group hiking event', status: 'todo', priority: 'low', estimatedHours: 0.5, tags: ['social', 'outdoor'] }
                  ])
                }
              ])
            }
          ])
        },
        {
          name: 'Personal Development',
          description: 'Learning, skills, and personal growth',
          color: '#F59E0B',
          icon: 'BookOpen',
          healthScore: 65,
          weeklyTimeTarget: 8,
          weeklyTimeActual: 6,
          streak: 3,
          areas: createAreas(personalDevPillarId, [
            {
              name: 'Technical Skills',
              description: 'Programming and technology expertise',
              projects: createProjects(technicalSkillsAreaId, [
                {
                  name: 'Machine Learning Course',
                  description: 'Complete Stanford ML specialization',
                  status: 'active',
                  priority: 'medium',
                  tasks: createTasks(mlCourseProjectId, [
                    { name: 'Week 3: Linear Regression assignment', status: 'completed', priority: 'medium', estimatedHours: 4, tags: ['ml', 'learning'] },
                    { name: 'Week 4: Logistic Regression', status: 'in-progress', priority: 'medium', estimatedHours: 4, tags: ['ml', 'learning'] },
                    { name: 'Final project proposal', status: 'todo', priority: 'high', estimatedHours: 2, tags: ['ml', 'project'] },
                    { name: 'Neural networks deep dive', status: 'todo', priority: 'medium', estimatedHours: 6, tags: ['ml', 'neural-networks'] },
                    { name: 'Complete capstone project', status: 'todo', priority: 'high', estimatedHours: 10, tags: ['ml', 'capstone'] }
                  ])
                },
                {
                  name: 'Spanish Learning',
                  description: 'Become conversationally fluent in Spanish',
                  status: 'active',
                  priority: 'low',
                  tasks: createTasks(languageProjectId, [
                    { name: 'Complete Duolingo daily lesson', status: 'completed', priority: 'medium', estimatedHours: 0.25, tags: ['spanish', 'daily'] },
                    { name: 'Practice speaking with language partner', status: 'todo', priority: 'high', estimatedHours: 1, tags: ['spanish', 'speaking'] },
                    { name: 'Watch Spanish Netflix show with subtitles', status: 'todo', priority: 'low', estimatedHours: 1, tags: ['spanish', 'entertainment'] },
                    { name: 'Review vocabulary flashcards', status: 'todo', priority: 'medium', estimatedHours: 0.25, tags: ['spanish', 'vocabulary'] }
                  ])
                }
              ])
            },
            {
              name: 'Personal Growth',
              description: 'Self-improvement and life skills',
              projects: createProjects(personalGrowthAreaId, [
                {
                  name: 'Reading Challenge',
                  description: 'Read 24 books this year across various topics',
                  status: 'active',
                  priority: 'medium',
                  tasks: createTasks(readingProjectId, [
                    { name: 'Finish "Atomic Habits" by James Clear', status: 'in-progress', priority: 'medium', estimatedHours: 3, tags: ['reading', 'habits'] },
                    { name: 'Start "The Power of Now" by Eckhart Tolle', status: 'todo', priority: 'low', estimatedHours: 4, tags: ['reading', 'mindfulness'] },
                    { name: 'Update reading log and notes', status: 'todo', priority: 'low', estimatedHours: 0.25, tags: ['reading', 'tracking'] },
                    { name: 'Write book review for blog', status: 'todo', priority: 'low', estimatedHours: 1, tags: ['reading', 'writing'] }
                  ])
                },
                {
                  name: 'Daily Reflection',
                  description: 'Daily journaling and self-reflection practice',
                  status: 'active',
                  priority: 'medium',
                  tasks: createTasks(reflectionProjectId, [
                    { name: 'Morning intention setting', status: 'completed', priority: 'medium', estimatedHours: 0.1, tags: ['reflection', 'morning'] },
                    { name: 'Evening gratitude practice', status: 'todo', priority: 'medium', estimatedHours: 0.1, tags: ['reflection', 'gratitude'] },
                    { name: 'Weekly life review and planning', status: 'todo', priority: 'high', estimatedHours: 0.5, tags: ['reflection', 'planning'] },
                    { name: 'Monthly goal assessment', status: 'todo', priority: 'medium', estimatedHours: 0.25, tags: ['reflection', 'goals'] }
                  ])
                }
              ])
            }
          ])
        },
        {
          name: 'Financial Wellness',
          description: 'Financial planning, investments, and security',
          color: '#8B5CF6',
          icon: 'DollarSign',
          healthScore: 78,
          weeklyTimeTarget: 5,
          weeklyTimeActual: 4.5,
          streak: 15,
          areas: createAreas(financialPillarId, [
            {
              name: 'Budgeting',
              description: 'Monthly budget planning and tracking',
              projects: createProjects(budgetingAreaId, [
                {
                  name: 'Budget Management System',
                  description: 'Create and maintain comprehensive budget tracking',
                  status: 'active',
                  priority: 'high',
                  tasks: createTasks(budgetSystemProjectId, [
                    { name: 'Set up automated expense categorization', status: 'completed', priority: 'high', estimatedHours: 2, tags: ['budgeting', 'automation'] },
                    { name: 'Review and categorize last month expenses', status: 'in-progress', priority: 'medium', estimatedHours: 1, tags: ['budgeting', 'review'] },
                    { name: 'Create next month budget plan', status: 'todo', priority: 'high', estimatedHours: 1, tags: ['budgeting', 'planning'] },
                    { name: 'Set up spending alerts and limits', status: 'todo', priority: 'medium', estimatedHours: 0.5, tags: ['budgeting', 'alerts'] }
                  ])
                },
                {
                  name: 'Debt Payoff Plan',
                  description: 'Systematic approach to eliminating all debt',
                  status: 'active',
                  priority: 'high',
                  tasks: createTasks(debtPayoffProjectId, [
                    { name: 'List all debts with interest rates', status: 'completed', priority: 'high', estimatedHours: 0.5, tags: ['debt', 'planning'] },
                    { name: 'Create debt avalanche strategy', status: 'completed', priority: 'high', estimatedHours: 1, tags: ['debt', 'strategy'] },
                    { name: 'Make extra payment to highest interest debt', status: 'todo', priority: 'high', estimatedHours: 0.1, tags: ['debt', 'payment'] },
                    { name: 'Track progress and adjust plan', status: 'todo', priority: 'medium', estimatedHours: 0.25, tags: ['debt', 'tracking'] }
                  ])
                }
              ])
            },
            {
              name: 'Investments',
              description: 'Portfolio management and wealth building',
              projects: createProjects(investmentsAreaId, [
                {
                  name: 'Investment Portfolio Review',
                  description: 'Quarterly analysis and rebalancing',
                  status: 'active',
                  priority: 'high',
                  tasks: createTasks(portfolioProjectId, [
                    { name: 'Review investment portfolio allocation', status: 'todo', priority: 'high', estimatedHours: 2, tags: ['finance', 'review'] },
                    { name: 'Rebalance asset allocation', status: 'todo', priority: 'medium', estimatedHours: 1, tags: ['finance', 'investments'] },
                    { name: 'Update investment strategy', status: 'todo', priority: 'medium', estimatedHours: 1.5, tags: ['finance', 'strategy'] },
                    { name: 'Research new investment opportunities', status: 'todo', priority: 'low', estimatedHours: 2, tags: ['finance', 'research'] },
                    { name: 'Calculate tax implications', status: 'todo', priority: 'medium', estimatedHours: 1, tags: ['finance', 'taxes'] }
                  ])
                },
                {
                  name: 'Retirement Planning',
                  description: 'Long-term retirement savings and planning',
                  status: 'active',
                  priority: 'medium',
                  tasks: createTasks(retirementProjectId, [
                    { name: 'Maximize 401k contribution for this year', status: 'completed', priority: 'high', estimatedHours: 0.25, tags: ['retirement', '401k'] },
                    { name: 'Open Roth IRA account', status: 'in-progress', priority: 'medium', estimatedHours: 1, tags: ['retirement', 'ira'] },
                    { name: 'Calculate retirement needs projection', status: 'todo', priority: 'medium', estimatedHours: 2, tags: ['retirement', 'planning'] },
                    { name: 'Review beneficiary designations', status: 'todo', priority: 'low', estimatedHours: 0.5, tags: ['retirement', 'beneficiaries'] }
                  ])
                }
              ])
            },
            {
              name: 'Emergency Fund',
              description: 'Building and maintaining emergency savings',
              projects: createProjects(emergencyFundAreaId, [
                {
                  name: 'Emergency Fund Building',
                  description: 'Build 6-month emergency fund in high-yield savings',
                  status: 'active',
                  priority: 'high',
                  tasks: createTasks(emergencyFundProjectId, [
                    { name: 'Calculate monthly expense baseline', status: 'completed', priority: 'high', estimatedHours: 1, tags: ['emergency', 'calculation'] },
                    { name: 'Open high-yield savings account', status: 'completed', priority: 'high', estimatedHours: 0.5, tags: ['emergency', 'account'] },
                    { name: 'Set up automatic monthly transfer', status: 'in-progress', priority: 'high', estimatedHours: 0.25, tags: ['emergency', 'automation'] },
                    { name: 'Track progress toward 6-month goal', status: 'todo', priority: 'medium', estimatedHours: 0.1, tags: ['emergency', 'tracking'] }
                  ])
                },
                {
                  name: 'Insurance Review',
                  description: 'Annual review of all insurance policies',
                  status: 'planning',
                  priority: 'medium',
                  tasks: createTasks(insuranceProjectId, [
                    { name: 'Review health insurance coverage', status: 'todo', priority: 'medium', estimatedHours: 1, tags: ['insurance', 'health'] },
                    { name: 'Compare auto insurance rates', status: 'todo', priority: 'low', estimatedHours: 1, tags: ['insurance', 'auto'] },
                    { name: 'Evaluate life insurance needs', status: 'todo', priority: 'medium', estimatedHours: 1.5, tags: ['insurance', 'life'] },
                    { name: 'Update beneficiaries on all policies', status: 'todo', priority: 'low', estimatedHours: 0.5, tags: ['insurance', 'beneficiaries'] }
                  ])
                }
              ])
            }
          ])
        },
        {
          name: 'Home & Environment',
          description: 'Living space and environment optimization',
          color: '#06B6D4',
          icon: 'Home',
          healthScore: 55,
          weeklyTimeTarget: 3,
          weeklyTimeActual: 2.5,
          streak: 2,
          areas: createAreas(homePillarId, [
            {
              name: 'Organization',
              description: 'Home organization and decluttering',
              projects: createProjects(organizationAreaId, [
                {
                  name: 'Home Office Setup',
                  description: 'Create productive workspace environment',
                  status: 'active',
                  priority: 'medium',
                  tasks: createTasks(officeSetupProjectId, [
                    { name: 'Set up ergonomic desk setup', status: 'todo', priority: 'medium', estimatedHours: 2, tags: ['setup', 'ergonomics'] },
                    { name: 'Organize cable management', status: 'todo', priority: 'low', estimatedHours: 1, tags: ['organization', 'tech'] },
                    { name: 'Install proper lighting', status: 'todo', priority: 'medium', estimatedHours: 1.5, tags: ['lighting', 'productivity'] },
                    { name: 'Add plants for air quality', status: 'todo', priority: 'low', estimatedHours: 0.5, tags: ['plants', 'environment'] },
                    { name: 'Install whiteboard for planning', status: 'todo', priority: 'low', estimatedHours: 0.5, tags: ['planning', 'setup'] }
                  ])
                },
                {
                  name: 'Bedroom Organization',
                  description: 'Create calm and organized sleeping environment',
                  status: 'active',
                  priority: 'low',
                  tasks: createTasks(bedroomOrgProjectId, [
                    { name: 'Declutter nightstand drawers', status: 'completed', priority: 'low', estimatedHours: 0.5, tags: ['organization', 'declutter'] },
                    { name: 'Organize closet by season', status: 'in-progress', priority: 'medium', estimatedHours: 2, tags: ['organization', 'closet'] },
                    { name: 'Install blackout curtains', status: 'todo', priority: 'medium', estimatedHours: 1, tags: ['sleep', 'environment'] },
                    { name: 'Create peaceful reading corner', status: 'todo', priority: 'low', estimatedHours: 1, tags: ['relaxation', 'setup'] }
                  ])
                }
              ])
            },
            {
              name: 'Sustainability',
              description: 'Eco-friendly living practices',
              projects: createProjects(sustainabilityAreaId, [
                {
                  name: 'Solar Panel Installation',
                  description: 'Install residential solar system to reduce carbon footprint',
                  status: 'planning',
                  priority: 'medium',
                  tasks: createTasks(solarProjectId, [
                    { name: 'Get solar installation quotes', status: 'completed', priority: 'high', estimatedHours: 2, tags: ['solar', 'quotes'] },
                    { name: 'Research solar financing options', status: 'in-progress', priority: 'high', estimatedHours: 3, tags: ['solar', 'financing'] },
                    { name: 'Schedule roof inspection', status: 'todo', priority: 'high', estimatedHours: 0.25, tags: ['solar', 'inspection'] },
                    { name: 'Apply for solar rebates and permits', status: 'todo', priority: 'medium', estimatedHours: 2, tags: ['solar', 'permits'] },
                    { name: 'Schedule installation date', status: 'todo', priority: 'medium', estimatedHours: 0.25, tags: ['solar', 'scheduling'] }
                  ])
                },
                {
                  name: 'Vegetable Garden',
                  description: 'Grow organic vegetables for sustainable living',
                  status: 'active',
                  priority: 'low',
                  tasks: createTasks(gardenProjectId, [
                    { name: 'Prepare soil for spring planting', status: 'completed', priority: 'medium', estimatedHours: 3, tags: ['gardening', 'soil'] },
                    { name: 'Plant spring vegetables (lettuce, spinach)', status: 'completed', priority: 'medium', estimatedHours: 2, tags: ['gardening', 'planting'] },
                    { name: 'Set up drip irrigation system', status: 'todo', priority: 'medium', estimatedHours: 4, tags: ['gardening', 'irrigation'] },
                    { name: 'Weekly garden maintenance and watering', status: 'todo', priority: 'medium', estimatedHours: 1, tags: ['gardening', 'maintenance'] },
                    { name: 'Start compost bin for kitchen scraps', status: 'todo', priority: 'low', estimatedHours: 1, tags: ['gardening', 'compost'] }
                  ])
                }
              ])
            }
          ])
        }
      ];

      // Add all pillars with their nested data
      samplePillars.forEach(pillar => {
        // Set the correct pillar ID
        const pillarWithId = {
          ...pillar,
          id: pillar.name === 'Health & Wellness' ? healthPillarId :
              pillar.name === 'Career & Professional' ? careerPillarId :
              pillar.name === 'Relationships' ? relationshipsPillarId :
              pillar.name === 'Personal Development' ? personalDevPillarId :
              pillar.name === 'Financial Wellness' ? financialPillarId :
              pillar.name === 'Home & Environment' ? homePillarId :
              crypto.randomUUID()
        };
        addPillar(pillarWithId);
      });

      // Add sample achievements
      const achievements = [
        {
          title: 'Fitness Streak Master',
          description: 'Completed 7 consecutive workout sessions',
          type: 'streak' as const,
          icon: '🏃‍♂️'
        },
        {
          title: 'Project Completion',
          description: 'Successfully completed Q4 strategic planning',
          type: 'completion' as const,
          icon: '✅'
        },
        {
          title: 'Learning Milestone',
          description: 'Finished advanced TypeScript course',
          type: 'milestone' as const,
          icon: '📚'
        }
      ];

      achievements.forEach(achievement => addAchievement(achievement));

      // Add sample smart suggestions
      const suggestions = [
        {
          type: 'scheduling' as const,
          title: 'Optimize morning workout time',
          description: 'Your energy levels are highest at 7-9 AM. Consider moving your workout to this window.',
          confidence: 0.85,
          actionData: { suggestedTime: '07:00', pillar: 'Health & Fitness' },
          dismissed: false
        },
        {
          type: 'energy-optimization' as const,
          title: 'Schedule creative work in the afternoon',
          description: 'You show peak creativity between 2-4 PM. Block this time for important projects.',
          confidence: 0.78,
          actionData: { timeWindow: '14:00-16:00', type: 'creative' },
          dismissed: false
        },
        {
          type: 'time-allocation' as const,
          title: 'Increase relationship time',
          description: 'You\'re 20% below your weekly relationship goal. Consider scheduling a family dinner.',
          confidence: 0.92,
          actionData: { pillar: 'Relationships', deficit: 3 },
          dismissed: false
        }
      ];

      suggestions.forEach(suggestion => addSmartSuggestion(suggestion));

      // Add sample energy patterns
      const energyPatterns = [
        { hour: 7, day: 1, energy: 8 },
        { hour: 8, day: 1, energy: 9 },
        { hour: 9, day: 1, energy: 8 },
        { hour: 14, day: 1, energy: 7 },
        { hour: 15, day: 1, energy: 8 },
        { hour: 16, day: 1, energy: 6 },
        { hour: 20, day: 1, energy: 4 },
      ];

      energyPatterns.forEach(({ hour, day, energy }) => {
        updateEnergyPattern(hour, day, energy);
      });

      // Add sample time blocks for today
      const now = new Date();
      const tomorrow = new Date(now);
      tomorrow.setDate(now.getDate() + 1);

      const morningWorkout = new Date(tomorrow);
      morningWorkout.setHours(7, 0, 0, 0);
      const morningWorkoutEnd = new Date(tomorrow);
      morningWorkoutEnd.setHours(8, 0, 0, 0);

      const deepWork = new Date(tomorrow);
      deepWork.setHours(9, 0, 0, 0);
      const deepWorkEnd = new Date(tomorrow);
      deepWorkEnd.setHours(11, 0, 0, 0);

      const familyTime = new Date(tomorrow);
      familyTime.setHours(18, 0, 0, 0);
      const familyTimeEnd = new Date(tomorrow);
      familyTimeEnd.setHours(19, 30, 0, 0);

      const sampleTimeBlocks = [
        {
          title: 'Morning Workout',
          pillarId: samplePillars[0].name, // Health & Fitness
          taskIds: [],
          startTime: morningWorkout,
          endTime: morningWorkoutEnd,
          energyLevel: 'high' as const,
          completed: false
        },
        {
          title: 'Deep Work - Project Planning',
          pillarId: samplePillars[1].name, // Career
          taskIds: [],
          startTime: deepWork,
          endTime: deepWorkEnd,
          energyLevel: 'high' as const,
          completed: false
        },
        {
          title: 'Family Dinner & Quality Time',
          pillarId: samplePillars[2].name, // Relationships
          taskIds: [],
          startTime: familyTime,
          endTime: familyTimeEnd,
          energyLevel: 'medium' as const,
          completed: false
        }
      ];

      sampleTimeBlocks.forEach(block => addTimeBlock(block));
    }
  }, [pillars.length, addPillar, addAchievement, addSmartSuggestion, updateEnergyPattern, addTimeBlock]);

  return null;
}