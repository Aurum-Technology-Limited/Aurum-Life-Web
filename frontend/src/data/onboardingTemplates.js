/**
 * Smart Onboarding Templates for Aurum Life
 * Static JSON data for MVP implementation
 * Three segment-specific templates: Student, Entrepreneur, Busy Employee
 */

export const ONBOARDING_TEMPLATES = {
  student: {
    name: "Student Template",
    description: "Designed for academic and personal life alignment",
    icon: "🎓",
    color: "#3B82F6",
    pillars: [
      {
        name: "Academics",
        description: "Academic excellence and learning goals",
        icon: "📚",
        color: "#3B82F6",
        areas: [
          {
            name: "Coursework",
            description: "Current semester courses and assignments",
            icon: "📝",
            color: "#3B82F6",
            importance: 5,
            projects: [
              {
                name: "Complete 'Intro to Python' Final Project",
                description: "Comprehensive Python programming project for CS101",
                icon: "💻",
                priority: "high",
                importance: 5,
                tasks: [
                  {
                    name: "Research project requirements and scope",
                    description: "Review syllabus and understand project expectations",
                    priority: "high"
                  },
                  {
                    name: "Design project architecture and flow",
                    description: "Create wireframes and plan code structure",
                    priority: "medium"
                  },
                  {
                    name: "Implement core functionality and testing",
                    description: "Write, debug, and test the main project code",
                    priority: "high"
                  }
                ]
              }
            ]
          },
          {
            name: "Career Planning",
            description: "Internships, networking, and future career preparation",
            icon: "🚀",
            color: "#10B981",
            importance: 4,
            projects: [
              {
                name: "Secure Summer Internship",
                description: "Find and apply for relevant summer internship opportunities",
                icon: "🏢",
                priority: "high",
                importance: 5,
                tasks: [
                  {
                    name: "Update resume with recent projects and skills",
                    description: "Revise resume to highlight relevant coursework and experience",
                    priority: "high"
                  },
                  {
                    name: "Research and identify target companies",
                    description: "Create list of 20+ companies offering internships",
                    priority: "medium"
                  },
                  {
                    name: "Submit applications and follow up",
                    description: "Apply to positions and track application status",
                    priority: "high"
                  }
                ]
              }
            ]
          },
          {
            name: "Extracurriculars",
            description: "Student organizations, clubs, and leadership activities",
            icon: "🎯",
            color: "#F59E0B",
            importance: 3,
            projects: [
              {
                name: "Organize Fall Hackathon",
                description: "Plan and execute student hackathon event",
                icon: "⚡",
                priority: "medium",
                importance: 4,
                tasks: [
                  {
                    name: "Form organizing committee and assign roles",
                    description: "Recruit team members and define responsibilities",
                    priority: "high"
                  },
                  {
                    name: "Secure venue, sponsors, and resources",
                    description: "Book location and arrange funding/prizes",
                    priority: "medium"
                  },
                  {
                    name: "Promote event and manage registrations",
                    description: "Market hackathon and handle participant sign-ups",
                    priority: "medium"
                  }
                ]
              }
            ]
          }
        ]
      },
      {
        name: "Well-being",
        description: "Physical and mental health maintenance",
        icon: "💪",
        color: "#10B981",
        areas: [
          {
            name: "Physical Health",
            description: "Exercise, nutrition, and physical wellness",
            icon: "🏃",
            color: "#10B981",
            importance: 4,
            projects: [
              {
                name: "Start a Running Routine",
                description: "Build consistent running habit for fitness",
                icon: "🏃‍♂️",
                priority: "medium",
                importance: 4,
                tasks: [
                  {
                    name: "Get proper running shoes and gear",
                    description: "Purchase appropriate equipment for safe running",
                    priority: "medium"
                  },
                  {
                    name: "Plan weekly running schedule (3x/week)",
                    description: "Set specific days and times for running sessions",
                    priority: "high"
                  },
                  {
                    name: "Track progress and gradually increase distance",
                    description: "Monitor runs and slowly build endurance",
                    priority: "low"
                  }
                ]
              }
            ]
          },
          {
            name: "Mental Health",
            description: "Stress management, mindfulness, and emotional wellness",
            icon: "🧘",
            color: "#8B5CF6",
            importance: 5,
            projects: [
              {
                name: "Develop a Meditation Practice",
                description: "Establish daily meditation for stress management",
                icon: "🧘‍♀️",
                priority: "medium",
                importance: 4,
                tasks: [
                  {
                    name: "Download meditation app and explore options",
                    description: "Research and choose meditation platform",
                    priority: "low"
                  },
                  {
                    name: "Start with 5-minute daily sessions",
                    description: "Begin small meditation routine after waking up",
                    priority: "high"
                  },
                  {
                    name: "Gradually increase to 15-minute sessions",
                    description: "Expand meditation time as habit strengthens",
                    priority: "low"
                  }
                ]
              }
            ]
          },
          {
            name: "Social Life",
            description: "Friendships, social activities, and community involvement",
            icon: "👥",
            color: "#EC4899",
            importance: 3,
            projects: [
              {
                name: "Reconnect with Old Friends",
                description: "Maintain and strengthen existing friendships",
                icon: "💬",
                priority: "low",
                importance: 3,
                tasks: [
                  {
                    name: "Make list of friends to reconnect with",
                    description: "Identify friends you want to stay in touch with",
                    priority: "low"
                  },
                  {
                    name: "Schedule regular catch-up calls or meetups",
                    description: "Plan monthly or weekly social interactions",
                    priority: "medium"
                  },
                  {
                    name: "Organize group activities or study sessions",
                    description: "Create opportunities for group bonding",
                    priority: "low"
                  }
                ]
              }
            ]
          }
        ]
      },
      {
        name: "Finances",
        description: "Financial literacy and money management",
        icon: "💰",
        color: "#F59E0B",
        areas: [
          {
            name: "Budgeting",
            description: "Monthly budget planning and expense tracking",
            icon: "📊",
            color: "#F59E0B",
            importance: 4,
            projects: [
              {
                name: "Set Up Monthly Budget",
                description: "Create and maintain student budget system",
                icon: "📈",
                priority: "high",
                importance: 4,
                tasks: [
                  {
                    name: "Track all income sources and amounts",
                    description: "List jobs, family support, scholarships, etc.",
                    priority: "high"
                  },
                  {
                    name: "Categorize and monitor monthly expenses",
                    description: "Track spending in food, housing, books, entertainment",
                    priority: "high"
                  },
                  {
                    name: "Use budgeting app or spreadsheet system",
                    description: "Choose and implement budget tracking tool",
                    priority: "medium"
                  }
                ]
              }
            ]
          },
          {
            name: "Income",
            description: "Part-time work and earning opportunities",
            icon: "💼",
            color: "#6366F1",
            importance: 3,
            projects: [
              {
                name: "Find a Part-Time Job",
                description: "Secure flexible work to support expenses",
                icon: "🛠️",
                priority: "medium",
                importance: 3,
                tasks: [
                  {
                    name: "Research on-campus and flexible job options",
                    description: "Look for student-friendly work opportunities",
                    priority: "medium"
                  },
                  {
                    name: "Prepare application materials and references",
                    description: "Update resume and gather recommendation contacts",
                    priority: "medium"
                  },
                  {
                    name: "Apply to positions and interview",
                    description: "Submit applications and attend interviews",
                    priority: "high"
                  }
                ]
              }
            ]
          },
          {
            name: "Financial Education",
            description: "Learning about personal finance and investing",
            icon: "📚",
            color: "#EF4444",
            importance: 2,
            projects: [
              {
                name: "Read 1 Book on Personal Finance",
                description: "Build foundational financial literacy knowledge",
                icon: "📖",
                priority: "low",
                importance: 2,
                tasks: [
                  {
                    name: "Choose beginner-friendly finance book",
                    description: "Research and select appropriate book for students",
                    priority: "low"
                  },
                  {
                    name: "Set reading schedule (1 chapter/week)",
                    description: "Plan consistent reading routine",
                    priority: "low"
                  },
                  {
                    name: "Take notes and apply key concepts",
                    description: "Implement learning into personal finances",
                    priority: "medium"
                  }
                ]
              }
            ]
          }
        ]
      }
    ]
  },

  entrepreneur: {
    name: "Entrepreneur Template",
    description: "For individuals building businesses while managing personal responsibilities",
    icon: "🚀",
    color: "#EF4444",
    pillars: [
      {
        name: "Business Development",
        description: "Strategic planning and business growth",
        icon: "📈",
        color: "#EF4444",
        areas: [
          {
            name: "Strategy",
            description: "Business planning, goal setting, and strategic initiatives",
            icon: "🎯",
            color: "#EF4444",
            importance: 5,
            projects: [
              {
                name: "Define 2025 Q3 Goals",
                description: "Set quarterly objectives and key results",
                icon: "📋",
                priority: "high",
                importance: 5,
                tasks: [
                  {
                    name: "Review Q2 performance and lessons learned",
                    description: "Analyze previous quarter metrics and outcomes",
                    priority: "high"
                  },
                  {
                    name: "Set 3-5 SMART goals for Q3",
                    description: "Define specific, measurable quarterly objectives",
                    priority: "high"
                  },
                  {
                    name: "Break down goals into monthly milestones",
                    description: "Create actionable monthly targets and checkpoints",
                    priority: "medium"
                  }
                ]
              }
            ]
          },
          {
            name: "Fundraising",
            description: "Investment, capital raising, and investor relations",
            icon: "💰",
            color: "#F59E0B",
            importance: 4,
            projects: [
              {
                name: "Prepare Seed Round Pitch Deck",
                description: "Create compelling investor presentation",
                icon: "📊",
                priority: "high",
                importance: 5,
                tasks: [
                  {
                    name: "Research pitch deck best practices and examples",
                    description: "Study successful pitch decks in your industry",
                    priority: "medium"
                  },
                  {
                    name: "Compile financial projections and metrics",
                    description: "Gather revenue, growth, and market data",
                    priority: "high"
                  },
                  {
                    name: "Design and practice pitch presentation",
                    description: "Create slides and rehearse delivery",
                    priority: "high"
                  }
                ]
              }
            ]
          },
          {
            name: "Operations",
            description: "Day-to-day business operations and processes",
            icon: "⚙️",
            color: "#6366F1",
            importance: 4,
            projects: [
              {
                name: "Formalize Accounting System",
                description: "Implement proper financial tracking and reporting",
                icon: "🧾",
                priority: "medium",
                importance: 4,
                tasks: [
                  {
                    name: "Choose accounting software (QuickBooks, Xero, etc.)",
                    description: "Research and select appropriate accounting platform",
                    priority: "medium"
                  },
                  {
                    name: "Set up chart of accounts and categories",
                    description: "Configure account structure for business needs",
                    priority: "high"
                  },
                  {
                    name: "Establish monthly bookkeeping routine",
                    description: "Create process for regular financial maintenance",
                    priority: "medium"
                  }
                ]
              }
            ]
          }
        ]
      },
      {
        name: "Product",
        description: "Product development and user experience",
        icon: "🛠️",
        color: "#10B981",
        areas: [
          {
            name: "Product Roadmap",
            description: "Feature planning and development priorities",
            icon: "🗺️",
            color: "#10B981",
            importance: 5,
            projects: [
              {
                name: "Launch MVP for Feedback",
                description: "Release minimum viable product to early users",
                icon: "🚀",
                priority: "high",
                importance: 5,
                tasks: [
                  {
                    name: "Finalize core features for MVP release",
                    description: "Define essential functionality for launch",
                    priority: "high"
                  },
                  {
                    name: "Set up analytics and feedback collection",
                    description: "Implement user tracking and feedback systems",
                    priority: "medium"
                  },
                  {
                    name: "Deploy to production and monitor performance",
                    description: "Launch MVP and track user engagement",
                    priority: "high"
                  }
                ]
              }
            ]
          },
          {
            name: "User Feedback",
            description: "Customer research and feedback analysis",
            icon: "💬",
            color: "#8B5CF6",
            importance: 4,
            projects: [
              {
                name: "Conduct 10 User Interviews",
                description: "Gather qualitative feedback from target users",
                icon: "🎤",
                priority: "high",
                importance: 4,
                tasks: [
                  {
                    name: "Identify and recruit target user segments",
                    description: "Find representative users for interviews",
                    priority: "high"
                  },
                  {
                    name: "Prepare interview script and questions",
                    description: "Develop structured interview framework",
                    priority: "medium"
                  },
                  {
                    name: "Conduct interviews and analyze insights",
                    description: "Execute interviews and extract key learnings",
                    priority: "high"
                  }
                ]
              }
            ]
          },
          {
            name: "Technical Debt",
            description: "Code quality, refactoring, and technical improvements",
            icon: "🔧",
            color: "#EF4444",
            importance: 3,
            projects: [
              {
                name: "Refactor Core Authentication Module",
                description: "Improve security and maintainability of auth system",
                icon: "🔐",
                priority: "medium",
                importance: 3,
                tasks: [
                  {
                    name: "Audit current authentication implementation",
                    description: "Review existing auth code for security issues",
                    priority: "high"
                  },
                  {
                    name: "Implement improved auth patterns and tests",
                    description: "Refactor with best practices and unit tests",
                    priority: "medium"
                  },
                  {
                    name: "Deploy and monitor auth system improvements",
                    description: "Release changes with careful monitoring",
                    priority: "low"
                  }
                ]
              }
            ]
          }
        ]
      },
      {
        name: "Personal Life",
        description: "Work-life balance and personal development",
        icon: "🏠",
        color: "#F59E0B",
        areas: [
          {
            name: "Mental Clarity",
            description: "Stress management and mental wellness for entrepreneurs",
            icon: "🧘",
            color: "#8B5CF6",
            importance: 5,
            projects: [
              {
                name: "Adopt a Morning Routine",
                description: "Create consistent morning ritual for productivity",
                icon: "🌅",
                priority: "medium",
                importance: 4,
                tasks: [
                  {
                    name: "Design ideal morning routine structure",
                    description: "Plan sequence of morning activities and timing",
                    priority: "low"
                  },
                  {
                    name: "Start with 2-3 core morning habits",
                    description: "Begin with meditation, exercise, or journaling",
                    priority: "high"
                  },
                  {
                    name: "Track consistency and adjust as needed",
                    description: "Monitor routine adherence and make improvements",
                    priority: "low"
                  }
                ]
              }
            ]
          },
          {
            name: "Family & Friends",
            description: "Maintaining relationships while building business",
            icon: "❤️",
            color: "#EC4899",
            importance: 4,
            projects: [
              {
                name: "Plan Weekly Family Dinner",
                description: "Prioritize quality time with family",
                icon: "🍽️",
                priority: "low",
                importance: 3,
                tasks: [
                  {
                    name: "Block calendar time for family dinner",
                    description: "Reserve weekly time slot for family meals",
                    priority: "medium"
                  },
                  {
                    name: "Rotate dinner planning and cooking duties",
                    description: "Share meal preparation responsibilities",
                    priority: "low"
                  },
                  {
                    name: "Create phone-free dinner environment",
                    description: "Establish rules for focused family time",
                    priority: "low"
                  }
                ]
              }
            ]
          },
          {
            name: "Skill Development",
            description: "Personal learning and professional growth",
            icon: "📚",
            color: "#3B82F6",
            importance: 3,
            projects: [
              {
                name: "Complete a New Course",
                description: "Learn new skills relevant to business",
                icon: "🎓",
                priority: "low",
                importance: 2,
                tasks: [
                  {
                    name: "Choose course aligned with business goals",
                    description: "Research courses in marketing, leadership, or technical skills",
                    priority: "low"
                  },
                  {
                    name: "Schedule weekly study sessions",
                    description: "Block time for consistent learning",
                    priority: "medium"
                  },
                  {
                    name: "Apply learnings to current business challenges",
                    description: "Implement new knowledge in real projects",
                    priority: "low"
                  }
                ]
              }
            ]
          }
        ]
      }
    ]
  },

  busy_employee: {
    name: "Busy Employee Template",
    description: "For ambitious professionals seeking work-life integration",
    icon: "💼",
    color: "#6366F1",
    pillars: [
      {
        name: "Career",
        description: "Professional development and career advancement",
        icon: "📊",
        color: "#6366F1",
        areas: [
          {
            name: "Professional Development",
            description: "Skills, certifications, and career growth",
            icon: "🎯",
            color: "#6366F1",
            importance: 5,
            projects: [
              {
                name: "Obtain PMP Certification",
                description: "Get Project Management Professional certification",
                icon: "🏆",
                priority: "high",
                importance: 5,
                tasks: [
                  {
                    name: "Complete PMP prerequisite training hours",
                    description: "Fulfill 35 hours of project management education",
                    priority: "high"
                  },
                  {
                    name: "Study for PMP exam using prep materials",
                    description: "Use PMBOK guide and practice exams for preparation",
                    priority: "high"
                  },
                  {
                    name: "Schedule and take PMP certification exam",
                    description: "Book exam date and complete certification",
                    priority: "medium"
                  }
                ]
              }
            ]
          },
          {
            name: "Work Projects",
            description: "Current work assignments and deliverables",
            icon: "💻",
            color: "#10B981",
            importance: 5,
            projects: [
              {
                name: "Launch Q4 Client Campaign",
                description: "Execute major marketing campaign for key client",
                icon: "📢",
                priority: "high",
                importance: 5,
                tasks: [
                  {
                    name: "Finalize campaign strategy and creative assets",
                    description: "Complete campaign planning and creative development",
                    priority: "high"
                  },
                  {
                    name: "Coordinate with media and vendor partners",
                    description: "Manage external partnerships and deliveries",
                    priority: "medium"
                  },
                  {
                    name: "Monitor campaign performance and optimize",
                    description: "Track metrics and make real-time adjustments",
                    priority: "high"
                  }
                ]
              }
            ]
          },
          {
            name: "Networking",
            description: "Professional relationships and industry connections",
            icon: "🤝",
            color: "#F59E0B",
            importance: 3,
            projects: [
              {
                name: "Expand Professional Network",
                description: "Build strategic industry relationships",
                icon: "🌐",
                priority: "medium",
                importance: 3,
                tasks: [
                  {
                    name: "Attend 2 industry events or conferences monthly",
                    description: "Participate in professional development events",
                    priority: "medium"
                  },
                  {
                    name: "Schedule monthly coffee chats with colleagues",
                    description: "Build relationships with internal and external contacts",
                    priority: "low"
                  },
                  {
                    name: "Maintain LinkedIn and professional profiles",
                    description: "Keep professional presence updated and active",
                    priority: "low"
                  }
                ]
              }
            ]
          }
        ]
      },
      {
        name: "Health & Wellness",
        description: "Physical and mental well-being",
        icon: "💪",
        color: "#10B981",
        areas: [
          {
            name: "Fitness",
            description: "Physical exercise and activity",
            icon: "🏃‍♂️",
            color: "#10B981",
            importance: 4,
            projects: [
              {
                name: "Hit 10k Steps Daily",
                description: "Maintain consistent daily movement goal",
                icon: "👟",
                priority: "medium",
                importance: 4,
                tasks: [
                  {
                    name: "Track daily steps with smartwatch or app",
                    description: "Set up step tracking system for accountability",
                    priority: "low"
                  },
                  {
                    name: "Take walking meetings when possible",
                    description: "Incorporate movement into work schedule",
                    priority: "medium"
                  },
                  {
                    name: "Plan evening walks or lunchtime exercise",
                    description: "Schedule movement breaks during workday",
                    priority: "high"
                  }
                ]
              }
            ]
          },
          {
            name: "Nutrition",
            description: "Healthy eating and meal planning",
            icon: "🥗",
            color: "#EF4444",
            importance: 4,
            projects: [
              {
                name: "Meal Prep for the Week",
                description: "Plan and prepare healthy meals in advance",
                icon: "🍱",
                priority: "medium",
                importance: 4,
                tasks: [
                  {
                    name: "Plan weekly menu with balanced nutrition",
                    description: "Design meal plan with proteins, vegetables, and grains",
                    priority: "medium"
                  },
                  {
                    name: "Shop for ingredients on weekends",
                    description: "Purchase fresh ingredients for meal prep",
                    priority: "low"
                  },
                  {
                    name: "Batch cook and portion meals for the week",
                    description: "Prepare and store ready-to-eat healthy meals",
                    priority: "high"
                  }
                ]
              }
            ]
          },
          {
            name: "Sleep",
            description: "Sleep quality and rest optimization",
            icon: "😴",
            color: "#8B5CF6",
            importance: 5,
            projects: [
              {
                name: "Improve Sleep Quality",
                description: "Optimize sleep schedule and environment",
                icon: "🌙",
                priority: "high",
                importance: 5,
                tasks: [
                  {
                    name: "Establish consistent bedtime routine",
                    description: "Create calming pre-sleep ritual and schedule",
                    priority: "high"
                  },
                  {
                    name: "Optimize bedroom for better sleep",
                    description: "Adjust lighting, temperature, and noise levels",
                    priority: "medium"
                  },
                  {
                    name: "Track sleep patterns and quality",
                    description: "Monitor sleep metrics to identify improvements",
                    priority: "low"
                  }
                ]
              }
            ]
          }
        ]
      },
      {
        name: "Relationships",
        description: "Personal relationships and social connections",
        icon: "❤️",
        color: "#EC4899",
        areas: [
          {
            name: "Family",
            description: "Family time and relationships",
            icon: "👨‍👩‍👧‍👦",
            color: "#EC4899",
            importance: 5,
            projects: [
              {
                name: "Plan a Fun Family Weekend",
                description: "Create quality family bonding time",
                icon: "🎉",
                priority: "medium",
                importance: 4,
                tasks: [
                  {
                    name: "Choose family-friendly activities for weekend",
                    description: "Research and select activities everyone enjoys",
                    priority: "low"
                  },
                  {
                    name: "Plan and book necessary reservations",
                    description: "Make arrangements for activities or dining",
                    priority: "medium"
                  },
                  {
                    name: "Create phone-free family time blocks",
                    description: "Establish dedicated time for focused family interaction",
                    priority: "high"
                  }
                ]
              }
            ]
          },
          {
            name: "Friends",
            description: "Friendships and social life",
            icon: "👥",
            color: "#F59E0B",
            importance: 3,
            projects: [
              {
                name: "Reconnect with Old Friends",
                description: "Maintain and strengthen friendships",
                icon: "💬",
                priority: "low",
                importance: 3,
                tasks: [
                  {
                    name: "Reach out to 3 friends you haven't spoken to recently",
                    description: "Send messages or calls to reconnect",
                    priority: "low"
                  },
                  {
                    name: "Schedule monthly friend catch-up activities",
                    description: "Plan regular social activities or dinners",
                    priority: "medium"
                  },
                  {
                    name: "Remember and celebrate friends' important events",
                    description: "Track birthdays and milestones for friends",
                    priority: "low"
                  }
                ]
              }
            ]
          },
          {
            name: "Personal Time",
            description: "Self-care and personal interests",
            icon: "🧘‍♀️",
            color: "#3B82F6",
            importance: 4,
            projects: [
              {
                name: "Schedule Personal Time",
                description: "Protect time for hobbies and self-care",
                icon: "⏰",
                priority: "medium",
                importance: 4,
                tasks: [
                  {
                    name: "Block 2 hours weekly for personal hobbies",
                    description: "Reserve calendar time for activities you enjoy",
                    priority: "high"
                  },
                  {
                    name: "Try one new activity or hobby monthly",
                    description: "Explore new interests and experiences",
                    priority: "low"
                  },
                  {
                    name: "Practice saying no to non-essential commitments",
                    description: "Protect personal time by setting boundaries",
                    priority: "medium"
                  }
                ]
              }
            ]
          }
        ]
      }
    ]
  }
};

export default ONBOARDING_TEMPLATES;