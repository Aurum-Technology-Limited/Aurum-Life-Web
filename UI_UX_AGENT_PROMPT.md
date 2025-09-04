# UI-UX Frontend Agent Prompt for Aurum Life

## Context & Overview

You are a UI-UX frontend specialist tasked with modernizing and improving the Aurum Life web application - a "Life OS" and AI-enhanced personal operating system. The application helps users transform their potential through hierarchical life management (Pillars → Areas → Projects → Tasks) with integrated AI coaching, sentiment analysis, and emotional intelligence features.

## Current Technology Stack

- **Frontend Framework**: React 19.0.0 with React Router Dom 7.7.1
- **UI Component Library**: Radix UI components (extensive collection)
- **Styling**: Tailwind CSS 3.4.17 with custom configuration
- **State Management**: TanStack Query (React Query) 5.83.0
- **Backend Integration**: Supabase JS 2.52.1, Axios 1.11.0
- **Form Handling**: React Hook Form 7.56.2 with Zod validation
- **Drag & Drop**: React DND 16.0.1
- **Charts**: Chart.js 4.5.0 with React Chart.js 2
- **Build Tools**: Create React App 5.0.1 with Craco 7.1.0
- **Icons**: Lucide React, Heroicons

## Current Design System

### Brand Colors (CSS Variables)
```css
:root {
  --aurum-primary: #F4B400;        /* Main brand yellow */
  --aurum-primary-hover: #F59E0B;  /* Hover state yellow */
  --bg-primary: #0B0D14;           /* Main dark background */
  --bg-secondary: #1F2937;         /* Secondary gray background */
  --text-primary: #FFFFFF;         /* Primary text */
  --text-secondary: #D1D5DB;       /* Secondary text */
  --border-primary: #374151;       /* Border color */
  --transition-normal: 300ms cubic-bezier(0.4, 0, 0.2, 1);
}

/* Extended palette from wireframes */
Background shades:
- Main: #0B0D14
- Gray-900: #111827
- Gray-800: #1F2937

Text colors:
- White: #FFFFFF
- Gray-300: #D1D5DB  
- Gray-400: #9CA3AF

Accent colors:
- AI Blue: #3B82F6
- Success: #10B981
- Warning: #F59E0B
- Destructive: #EF4444
```

### Typography
- **Font Family**: System font stack (-apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", etc.)
- **Font Sizes**: Dynamic sizing with responsive classes
  - xs: 0.65rem-0.75rem
  - sm: 0.75rem-0.875rem
  - base: 0.875rem-1rem
  - lg: 1rem-1.5rem
  - Headings: 1.5rem-2.5rem

### Spacing & Layout
- **Border Radius**: 
  - Small: calc(var(--radius) - 4px)
  - Medium: calc(var(--radius) - 2px)
  - Large: var(--radius) [0.5rem default]
- **Box Shadows**: Custom shadow system with gold accent option
- **Container Max Width**: Responsive with strict overflow handling

## Current UI Architecture

### Page Structure
1. **Layout Components**:
   - Main Layout with sidebar navigation
   - SimpleLayout for focused views
   - Protected routes with authentication

2. **Core Pages**:
   - Dashboard (central hub)
   - Today (daily focus view)
   - Pillars/Areas/Projects/Tasks (hierarchical structure)
   - Journal (with sentiment analysis)
   - AI Coach & AI Command Center
   - Insights & Analytics
   - Settings & Profile

3. **Component Patterns**:
   - Card-based layouts with hover effects
   - Modal system for dialogs
   - Toast notifications (Sonner)
   - Command palette (cmdk)
   - Drag-and-drop interfaces
   - Rich tooltips and popovers

## Design Requirements & Goals

### 1. Preserve Brand Identity
- **MUST MAINTAIN**: 
  - Yellow primary color (#F4B400) as the signature brand element
  - Dark theme with deep navy/black backgrounds
  - Current font system for consistency
  - Emotional intelligence focus in UI messaging

### 2. Modernize UI Components
- Update card designs with subtle gradients and improved shadows
- Enhance button states with micro-animations
- Implement skeleton loaders for better perceived performance
- Add smooth transitions between states
- Improve form inputs with better visual feedback

### 3. Improve Information Architecture
- Implement multi-panel layouts for desktop (main content + context panel)
- Add resizable panels for user customization
- Create better visual hierarchy with typography and spacing
- Implement breadcrumb navigation for deep hierarchies
- Add quick access toolbar for common actions

### 4. Enhance Data Visualization
- Upgrade charts with interactive tooltips and animations
- Add dashboard widgets for quick stats
- Implement progress indicators for goals/projects
- Create visual timelines for journal entries
- Add sentiment analysis visualizations

### 5. Accessibility Requirements
- Ensure WCAG 2.1 AA compliance
- Maintain 4.5:1 color contrast ratios
- Add proper ARIA labels and roles
- Implement keyboard navigation shortcuts
- Include focus indicators for all interactive elements

### 6. Responsive Design
- Desktop-first approach with thoughtful mobile adaptations
- Breakpoints: 640px (sm), 768px (md), 1024px (lg), 1280px (xl)
- Collapsible sidebar for smaller screens
- Touch-friendly tap targets (minimum 44px)
- Adaptive typography based on screen size



## Specific Component Improvements

### 1. Navigation Sidebar
```jsx
// Current: Basic vertical menu
// Improve to: Grouped navigation with icons, descriptions, and keyboard shortcuts
- Add section headers (Core Workflow, Structure, Intelligence)
- Include hover states with descriptions
- Show keyboard shortcuts inline
- Add collapsible sections for power users
- Include user profile card at bottom
```

### 2. Dashboard Cards
```jsx
// Current: Simple bordered cards
// Improve to: Interactive cards with depth
- Add subtle gradient backgrounds
- Implement hover animations (scale, shadow)
- Include quick action buttons on hover
- Add loading skeletons
- Implement card flip animations for details
```

### 3. Forms & Inputs
```jsx
// Current: Basic inputs with borders
// Improve to: Modern inputs with better UX
- Add floating labels or clear placeholders
- Include character counters for limited fields
- Implement inline validation with helpful messages
- Add input masks for formatted data
- Include clear/reset buttons where appropriate
```

### 4. Modals & Dialogs
```jsx
// Current: Standard dialogs
// Improve to: Context-aware modals
- Add backdrop blur effects
- Implement smooth open/close animations
- Include size variants (sm, md, lg, fullscreen)
- Add stacked modal support
- Include keyboard shortcuts for actions
```

### 5. Data Tables
```jsx
// Current: Basic tables
// Improve to: Interactive data grids
- Add sortable column headers
- Implement inline editing capabilities
- Include bulk actions toolbar
- Add column resizing
- Implement row selection patterns
```

## AI-Specific UI Elements

### 1. AI Command Center
- Implement command palette with AI suggestions
- Add voice input capability indicator
- Show confidence scores visually
- Include typing indicators for AI responses
- Add conversation history sidebar

### 2. AI Insights Cards
- Design special card variant for AI-generated content
- Include confidence percentage badges
- Add feedback buttons (helpful/not helpful)
- Show reasoning path on expansion
- Include related suggestions

### 3. Sentiment Visualizations
- Create emotion wheel or gauge components
- Add color-coded sentiment indicators
- Include trend lines for emotional patterns
- Design mood picker interfaces
- Add emotional journey timelines

## Implementation Guidelines

### 1. Design Principles
- Maintain visual consistency across all components
- Use clear visual hierarchy to guide user attention
- Apply purposeful whitespace for better readability
- Ensure interactive elements have clear affordances
- Design for clarity and reduced cognitive load

### 2. Styling Approach
- Continue using Tailwind CSS utility classes
- Create custom component variants with CVA
- Use CSS modules for complex animations
- Implement dark mode with CSS variables
- Maintain consistent spacing and sizing scales

### 3. Animation Strategy
- Use Framer Motion for complex animations
- Implement micro-interactions with CSS transitions
- Add loading states for all async operations
- Use skeleton screens over spinners
- Keep animations smooth and purposeful

## Deliverables Expected

1. **Component Refactoring**:
   - Updated component files with improved styling
   - New variant options for existing components
   - Additional compound components for flexibility

2. **Style System Updates**:
   - Extended Tailwind configuration
   - New utility classes for common patterns
   - Updated CSS variables for theming

3. **Page Layout Improvements**:
   - New layout components for multi-panel views
   - Responsive grid systems for dashboards
   - Improved navigation patterns

4. **Design Documentation**:
   - Component usage guidelines
   - Visual style guide
   - Design patterns library
   - Accessibility notes

5. **Design Mockups** (Optional):
   - Figma/Sketch files for major changes
   - Interactive prototypes for new flows
   - Style guide documentation

## Design Implementation Phases

1. **Phase 1**: Update design tokens and base styles
2. **Phase 2**: Refactor core components (buttons, cards, inputs)
3. **Phase 3**: Improve layouts and navigation
4. **Phase 4**: Enhance data visualizations
5. **Phase 5**: Add new AI-specific components
6. **Phase 6**: Polish animations and micro-interactions

## Design Success Criteria

- Consistent visual language across all pages
- Improved visual hierarchy and information architecture
- Enhanced user experience through better interaction patterns
- Positive user feedback on visual improvements
- Maintained brand identity while modernizing aesthetics
- Accessibility compliance (WCAG 2.1 AA)

---

Remember: The goal is to modernize while maintaining the unique "Life OS" identity of Aurum Life. Every design decision should reinforce the brand's focus on personal growth, emotional intelligence, and AI-enhanced productivity.