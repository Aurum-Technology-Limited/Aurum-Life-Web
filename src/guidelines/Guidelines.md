# Aurum Life Personal Operating System - Development Guidelines

## 🌟 Core Philosophy

Aurum Life is a sophisticated Personal Operating System that helps users align daily actions with long-term life vision through the PAPT Framework (Pillars → Areas → Projects → Tasks). Every design and development decision should support this core mission.

## 🎨 Design System Guidelines

### Color Palette (Dark Mode Only)
- **Primary Background**: `#0B0D14` (var(--aurum-primary-bg))
- **Secondary Background**: `#1A1D29` (var(--aurum-secondary-bg))
- **Accent Gold**: `#F4D03F` (var(--aurum-accent-gold))
- **Text Primary**: `#FFFFFF` (var(--aurum-text-primary))
- **Text Secondary**: `#B8BCC8` (var(--aurum-text-secondary))
- **Glass Border**: `rgba(244, 208, 63, 0.2)` (var(--aurum-glass-border))

**Rules:**
- NEVER implement light mode - Aurum Life is exclusively dark mode
- Always use CSS custom properties, not hardcoded colors
- Gold accent (#F4D03F) is reserved for primary actions and hierarchy emphasis
- Use glassmorphism effects for all card components

### Glassmorphism System
```css
/* Standard card - use this for most components */
.glassmorphism-card

/* Subtle overlay - use for nested content */
.glassmorphism-panel

/* Strong emphasis - use for modals and important sections */
.glassmorphism-strong

/* Header/navigation - use for fixed headers */
.glassmorphism-header
```

**Rules:**
- All cards MUST use glassmorphism styling
- Never use solid backgrounds except for the main body
- Always include hover effects with gold accent transitions
- Use backdrop-filter: blur() for proper glassmorphism effect

### PAPT Hierarchy Visual System
```css
.hierarchy-pillar    /* Gold left border (4px) */
.hierarchy-area      /* Blue left border (3px) */
.hierarchy-project   /* Green left border (2px) */
.hierarchy-task      /* Purple left border (2px) */
```

**Rules:**
- Hierarchy levels MUST be visually distinct with colored left borders
- Progress bars should use gold gradient for consistency
- Always show hierarchy breadcrumbs for navigation context
- Maintain visual hierarchy through border thickness and color

## 📱 Mobile-First Responsive Guidelines

### Mobile Layout Rules
- Design for mobile first, enhance for desktop
- Use bottom navigation on mobile (hidden on desktop)
- Implement floating action button for primary actions on mobile
- Ensure all touch targets are minimum 44px (48px preferred)
- Use pull-to-refresh on mobile content areas

### Touch Targets
```css
.touch-target        /* Standard 44px minimum */
.touch-target-large  /* 48px for primary actions */
.touch-feedback      /* Ripple effect on touch */
```

### One-Handed Use Optimization
- Keep primary actions in thumb-reach zone (bottom 6rem)
- Use floating action button positioned for thumb access
- Implement swipe gestures where appropriate
- Ensure content doesn't hide behind mobile navigation

## 🧩 Component Architecture

### Component Naming Convention
- **Sections**: `Dashboard.tsx`, `Today.tsx`, `Analytics.tsx`
- **Shared Components**: `HierarchyCard.tsx`, `LoadingScreen.tsx`
- **Enhanced Features**: `IntelligentLifeCoachAI.tsx`, `FloatingActionButton.tsx`
- **UI Components**: Follow shadcn/ui naming in `/components/ui/`

### State Management Rules
- Use Zustand for all global state management
- Keep stores focused and single-responsibility
- Use individual selector functions to prevent re-render issues
- Implement proper error handling with circuit breakers

### Error Handling Standards
```tsx
// Always wrap sections in error boundaries
<TimeoutErrorBoundary>
  <SimpleErrorBoundary>
    <YourComponent />
  </SimpleErrorBoundary>
</TimeoutErrorBoundary>

// Use circuit breakers for API calls
CircuitBreaker.execute(apiCall)

// Filter non-critical errors (timeouts, WebSocket, etc.)
const isNonCritical = error.includes('timeout') || 
                     error.includes('WebSocket') ||
                     error.includes('Failed to fetch');
```

## 🎭 Animation and Interaction Guidelines

### Motion System
- Use `motion/react` for animations (NOT framer-motion)
- Respect `prefers-reduced-motion` settings
- Implement smooth hover transitions (0.3s ease)
- Use subtle transform effects (translateY(-2px)) for interactive elements

### Loading States
- Always show skeleton loading for better perceived performance
- Use shimmer animations for content areas
- Implement timeout protection (maximum 8 seconds)
- Provide fallback states for failed loads

## 🔧 Technical Implementation Rules

### TypeScript Standards
- Use strict TypeScript configuration
- Define proper interfaces for all data structures
- Avoid `any` types - use proper type definitions
- Implement comprehensive error type definitions

### Performance Optimization
- Lazy load all section components
- Implement proper memoization for expensive calculations
- Use React.Suspense for component loading
- Optimize bundle size with proper imports

### Accessibility Requirements (WCAG 2.1 AA)
- All interactive elements must be keyboard accessible
- Provide proper ARIA labels and roles
- Ensure color contrast ratios meet standards
- Implement screen reader friendly announcements
- Support assistive technologies

## 📊 Data and API Guidelines

### PAPT Framework Data Structure
```typescript
interface Pillar {
  id: string;
  title: string;
  description: string;
  color: string;
  progress: number;
  areas: Area[];
}

interface Area {
  id: string;
  title: string;
  description: string;
  pillarId: string;
  projects: Project[];
}

interface Project {
  id: string;
  title: string;
  description: string;
  areaId: string;
  status: 'not_started' | 'in_progress' | 'completed';
  priority: 'low' | 'medium' | 'high';
  tasks: Task[];
}

interface Task {
  id: string;
  title: string;
  description: string;
  projectId: string;
  completed: boolean;
  dueDate?: string;
}
```

### API Integration Rules
- Use Supabase for backend integration
- Implement proper error handling and retry logic
- Use environment variables for sensitive data
- Implement offline-first data synchronization

## 🤖 AI and Enhanced Features

### AI Coaching Integration
- Use RAG (Retrieval Augmented Generation) for contextual insights
- Implement conversational AI interface with chat-like experience
- Provide personalized recommendations based on user patterns
- Respect privacy settings and data usage preferences

### Team Collaboration Features
- Implement real-time updates using WebSocket connections
- Provide granular privacy controls for shared content
- Support multiple user roles (admin, member, viewer)
- Enable goal sharing and collaborative progress tracking

## 🔒 Privacy and Security

### Data Protection Rules
- Implement granular privacy controls
- Provide clear data usage transparency
- Support user data export and deletion
- Use audit logging for sensitive operations
- Never expose sensitive data in AI requests

### Authentication Standards
- Use Supabase Auth for user management
- Implement timeout-resistant authentication
- Provide demo account for testing
- Support social login providers (with proper setup)

## 📝 Content and Copy Guidelines

### Writing Style
- Use clear, actionable language
- Maintain professional but friendly tone
- Provide helpful contextual information
- Use consistent terminology throughout the app

### Educational Content (PAPT Framework)
- Explain concepts before implementation
- Use visual diagrams and interactive examples
- Provide real-world benefits and use cases
- Make onboarding comprehensive but engaging

## 🧪 Testing Standards

### Test Coverage Requirements
- Unit tests: 85%+ coverage
- Integration tests for all user workflows
- Accessibility tests (WCAG 2.1 AA compliance)
- Visual regression tests for UI consistency
- End-to-end tests for complete user journeys

### Testing Patterns
```typescript
// Component testing pattern
describe('ComponentName', () => {
  it('renders correctly with required props', () => {
    // Test implementation
  });
  
  it('handles user interactions properly', () => {
    // Test user events
  });
  
  it('maintains accessibility standards', () => {
    // Test keyboard navigation, ARIA, etc.
  });
});
```

## 🚀 Deployment and Performance

### Build Optimization
- Optimize bundle size with proper code splitting
- Implement service worker for offline functionality
- Use proper image optimization and lazy loading
- Monitor Core Web Vitals and performance metrics

### SEO and Meta Tags
- Implement proper meta tags for sharing
- Use structured data for better indexing
- Optimize for search engines while maintaining UX
- Implement proper robots.txt and sitemap

## ⚡ Development Workflow

### Code Quality Standards
- Use ESLint and Prettier for consistent formatting
- Implement pre-commit hooks for quality checks
- Follow semantic commit message conventions
- Maintain comprehensive documentation

### Version Control
- Use feature branches for all development
- Implement proper code review processes
- Tag releases with semantic versioning
- Maintain detailed changelog

## 🎯 Specific Component Guidelines

### HierarchyCard Component
- Always include progress indication
- Implement proper hover effects
- Support drag-and-drop for reordering
- Provide quick action buttons
- Show hierarchy level with visual indicators

### Navigation Component
- Highlight active section with gold accent
- Support keyboard navigation
- Implement breadcrumb navigation
- Show notification indicators
- Adapt layout for mobile vs desktop

### Dashboard Components
- Use grid layout for responsive design
- Implement skeleton loading states
- Show real-time data updates
- Provide quick action capabilities
- Maintain consistent card spacing

### AI Interface Components
- Use conversational design patterns
- Implement typing indicators for responses
- Provide context-aware suggestions
- Support voice input where appropriate
- Show confidence levels for AI insights

## 📱 Mobile-Specific Guidelines

### Bottom Navigation
- Maximum 5 navigation items
- Use recognizable icons with labels
- Highlight active state clearly
- Implement haptic feedback on supported devices
- Maintain consistent touch target sizes

### Floating Action Button
- Position for one-handed use (right side, thumb reach)
- Use primary gold color for visibility
- Implement proper animation states
- Support long-press for additional actions
- Hide appropriately when keyboard is open

### Pull-to-Refresh
- Implement on main content areas only
- Use custom spinner with Aurum Life branding
- Provide haptic feedback during refresh
- Show clear loading state
- Handle offline scenarios gracefully

---

## 🎯 Summary: Golden Rules for Aurum Life

1. **Dark Mode Only** - Never implement light themes
2. **Mobile First** - Design for mobile, enhance for desktop
3. **Glassmorphism Always** - Use glass effects for all cards
4. **PAPT Hierarchy** - Maintain visual hierarchy with borders and colors
5. **Gold Accent Sacred** - Reserve #F4D03F for primary elements only
6. **Accessibility First** - WCAG 2.1 AA compliance is non-negotiable
7. **Performance Matters** - Lazy load everything, optimize aggressively
8. **Error Handling** - Implement comprehensive error boundaries and recovery
9. **Privacy Respect** - Granular controls and transparent data usage
10. **Test Everything** - 85%+ coverage across all test types

**Remember: Every component should feel like it belongs in a premium Personal Operating System that empowers users to achieve their life goals through the PAPT Framework.**