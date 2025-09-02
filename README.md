# 🧠 Aurum Life - AI-Enhanced Personal Operating System

Transform your potential into gold with the world's first intelligent life operating system featuring hierarchical AI reasoning, semantic content discovery, and strategic goal coaching.

## 🌟 **What Makes Aurum Life Unique**

### **🎯 Intelligent Hierarchical Reasoning**
- **AI-powered goal alignment** connecting daily tasks to life vision
- **Confidence-scored recommendations** with transparent reasoning paths
- **Strategic coaching** for goal planning and obstacle resolution
- **Cross-content semantic search** across all personal productivity data

### **⚡ Unified AI Ecosystem**
- **My AI Insights**: Browse what AI has learned about your productivity patterns
- **AI Quick Actions**: Fast AI assistance and productivity overview  
- **Goal Planner**: Strategic planning with AI coaching for goal achievement
- **Today View**: AI-enhanced daily focus with priority scoring

### **🏗️ Complete Life Structure**
- **Pillars** → **Areas** → **Projects** → **Tasks** hierarchy
- **Smart onboarding** with persona-based templates
- **Real-time alignment tracking** with AI-powered insights
- **Daily engagement hub** with reflection and planning tools

---

## 🚀 **Quick Start**

### **1. System Requirements**
- Node.js 18+ and Python 3.11+
- PostgreSQL with pgvector extension
- Supabase account for authentication and database
- OpenAI API key for AI features

### **2. Environment Setup**

```bash
# Backend environment variables
cat > backend/.env << 'EOF'
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-5-nano
JWT_SECRET_KEY=your_jwt_secret
EOF

# Frontend environment variables  
cat > frontend/.env << 'EOF'
REACT_APP_BACKEND_URL=your_backend_url
EOF
```

### **3. Installation & Deployment**

```bash
# Install dependencies
cd backend && pip install -r requirements.txt
cd ../frontend && yarn install

# Set up database (run in Supabase SQL Editor)
-- Execute migration files 001-009 in sequence
-- Enable pgvector: CREATE EXTENSION IF NOT EXISTS vector;

# Start services
sudo supervisorctl restart all
```

---

## 🎯 **Core Features**

### **📊 AI-Enhanced Productivity**
- **Hierarchical AI Reasoning**: Connect daily actions to life goals
- **Confidence Scoring**: 80%+ accuracy on AI recommendations
- **Semantic Search**: Find related content across journal, tasks, projects
- **Strategic Coaching**: AI-powered goal decomposition and planning

### **🏗️ Structured Life Management**
- **Pillars**: Core life domains (Career, Health, Relationships, etc.)
- **Areas**: Focus categories within each pillar
- **Projects**: Specific initiatives and deliverables
- **Tasks**: Individual actionable items with AI priority scoring

### **⚡ Daily Productivity Tools**
- **Today View**: AI-curated daily focus with priority explanations
- **Journal System**: Personal reflection with AI insight potential
- **Dashboard**: Central hub with alignment tracking and calendar planning
- **Templates**: Pre-built project structures for faster setup

---

## 🧠 **AI Architecture**

### **Hierarchical Reasoning Model (HRM)**
```
🎯 Entity Analysis: Analyze any level (global, pillar, area, project, task)
🧠 LLM Integration: OpenAI GPT-5 nano for cost-efficient reasoning
📊 Confidence Scoring: 0-100% confidence on all AI recommendations
🔍 Pattern Recognition: Cross-hierarchy insights and relationships
💬 Feedback Loop: User feedback improves AI recommendations
⚡ Real-time Processing: Background analysis with intelligent caching
```

### **Blackboard System**
```
🗄️ Centralized Repository: All AI insights stored with metadata
🔄 Cross-Component Access: Insights available throughout application
📈 Statistics Tracking: AI performance and learning analytics
🎯 Priority Management: Critical, high, medium, low insight categorization
📌 User Management: Pin important insights, provide feedback
🔍 Advanced Search: Find insights by entity, type, confidence, tags
```

### **Semantic Search & RAG**
```
🔍 pgvector Integration: Advanced vector similarity search
📝 Multi-Content Types: Journal entries, tasks, projects, daily reflections
🤖 OpenAI Embeddings: text-embedding-3-small for high-quality vectors
⚡ Fast Performance: ~1.1s average response time, 94.7% success rate
🎯 Context-Aware: AI references historical context for recommendations
```

---

## 🎨 **User Experience Design**

### **🧭 Optimized Navigation (12 Screens)**

#### **Strategic Structure**
- 🏛️ **Pillars**: Core life domains & priorities
- 🎯 **Areas**: Focus categories within pillars  
- 📁 **Projects**: Initiatives & deliverables (includes Templates)
- ✅ **Tasks**: Individual action items

#### **Daily Operations**
- 🏠 **Dashboard**: Overview & daily planning hub
- 📅 **Today**: Focus tasks & daily engagement
- 📝 **Journal**: Personal reflection & notes

#### **AI Intelligence Ecosystem**  
- 🧠 **My AI Insights**: Browse AI observations about you
- ⚡ **AI Quick Actions**: Fast AI help & overview
- 🎯 **Goal Planner**: Plan & achieve goals with AI

#### **Analysis & Support**
- 📊 **Intelligence Hub**: Analytics & AI insights dashboard
- 💬 **Feedback**: Share suggestions & report issues

### **🎪 User-Intent Based Design**
Every screen includes clear purpose descriptions:
- **Eliminates navigation confusion** with obvious section purposes
- **Reduces decision friction** for AI feature selection
- **Enhances feature discovery** through descriptive navigation
- **Improves user onboarding** with self-explanatory interface

---

## 🔧 **Technical Architecture**

### **Backend Stack**
- **Framework**: FastAPI with async/await patterns
- **Database**: PostgreSQL + Supabase + pgvector extension
- **AI Integration**: OpenAI GPT-5 nano + text-embedding-3-small
- **Authentication**: Supabase Auth + JWT tokens
- **Security**: Row Level Security (RLS) + API protection

### **Frontend Stack**
- **Framework**: React 18 with modern hooks and patterns
- **State Management**: TanStack Query for server state
- **Styling**: Tailwind CSS with dark theme optimization
- **Components**: Modular, reusable AI-enhanced components
- **Performance**: Optimized with lazy loading and caching

### **AI Technology Stack**
- **Primary LLM**: OpenAI GPT-5 nano (cost-efficient reasoning)
- **Embeddings**: OpenAI text-embedding-3-small (semantic search)
- **Vector Database**: pgvector for similarity search
- **Processing**: Hierarchical reasoning with context awareness
- **Learning**: User feedback loop for continuous improvement

---

## 📊 **API Reference**

### **🧠 HRM (Hierarchical Reasoning Model) Endpoints**
```
POST /api/hrm/analyze                 - Analyze any entity with AI reasoning
GET  /api/hrm/insights               - Retrieve filtered AI insights  
GET  /api/hrm/statistics             - AI performance analytics
POST /api/hrm/prioritize-today       - Enhanced daily task priorities
GET  /api/hrm/preferences            - User AI preferences
PUT  /api/hrm/preferences            - Update AI settings
```

### **🔍 Semantic Search Endpoints**
```
GET  /api/semantic/search            - Multi-content semantic search
GET  /api/semantic/similar/{type}/{id} - Find similar content
```

### **🎯 AI Coaching Endpoints**
```
GET  /api/ai/quota                   - AI usage quota management
GET  /api/ai/task-why-statements     - Task priority explanations
GET  /api/ai/suggest-focus           - AI-curated focus recommendations
GET  /api/alignment/dashboard        - Goal alignment with AI insights
```

---

## 🔧 **Development**

### **Local Development Setup**
```bash
# Start backend services
cd backend
sudo supervisorctl restart backend

# Start frontend development
cd frontend  
sudo supervisorctl restart frontend
```

### **Testing**
```bash
# Backend API testing
curl -H "Authorization: Bearer TOKEN" https://api.aurumlife.com/api/hrm/statistics

# Frontend testing  
# Navigate to app and test AI features:
# - Cmd+K for AI Quick Actions
# - My AI Insights for analysis review
# - Goal Planner for strategic coaching
```

---

## 📚 **Documentation**

- [Implementation Summary](IMPLEMENTATION_SUMMARY.md) - Technical implementation details
- [MVP Gap Analysis](MVP_GAP_ANALYSIS_REPORT.md) - Feature completeness analysis
- [Technical Documentation](TECHNICAL_DOCS.md) - Architecture and API reference
- [Environment Setup](ENVIRONMENT_SETUP.md) - Detailed configuration guide
- [Deployment Guide](DEPLOYMENT.md) - Production deployment instructions

---

## 🎯 **Key Differentiators**

### **🧠 Intelligent AI Reasoning**
Unlike other productivity tools, Aurum Life's AI understands the **complete context** of your life structure, providing insights that connect daily tasks to your highest-level goals with confidence scores and transparent reasoning.

### **⚡ Unified AI Ecosystem**
Three specialized AI tools work together seamlessly:
- **Review** what AI learned about you
- **Quick access** to AI assistance  
- **Strategic planning** with AI coaching

### **🎯 Transparent AI**
Every AI recommendation includes:
- Confidence score (0-100%)
- Detailed reasoning path
- Connection to your life hierarchy
- Opportunity for user feedback

---

## 🤝 **Support & Community**

### **🚨 Getting Help**
- **Documentation**: Comprehensive guides for all features
- **API Reference**: Complete endpoint documentation with examples
- **Issue Reporting**: Built-in feedback system for bug reports
- **Feature Requests**: Integrated suggestion system

### **🔧 Technical Support**
- **Logs**: Check supervisor logs for debugging
- **Performance**: Monitor AI response times and quota usage
- **Database**: Verify pgvector extension and migration completion
- **Authentication**: Test Supabase integration and JWT handling

---

## 🎉 **Vision Realized**

**Aurum Life successfully transforms potential into gold by connecting every action to your highest aspirations through intelligent AI reasoning.**

**Join the productivity revolution with the world's first AI-enhanced personal operating system.** ⚡

---

**Built with ❤️ by the Aurum Life Team**  
**Powered by OpenAI GPT-5 nano • Secured by Supabase • Optimized for humans**