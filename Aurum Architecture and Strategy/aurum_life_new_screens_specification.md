# New Screen Specifications: Aurum Life Enhanced AI Architecture

## 🎯 Overview

This document details new screens and significant redesigns for Aurum Life's enhanced AI architecture, with specifications for both web and mobile platforms.

---

## 1. AI Command Center (Universal Search & Command)

### Purpose
Universal AI-powered interface for natural language navigation, task creation, and insights - accessible from anywhere in the app.

### Web Layout
```
┌─────────────────────────────────────────────────┐
│ ⌘K  [🔍 Ask AI anything or type a command...]  │
├─────────────────────────────────────────────────┤
│ 💡 Suggestions based on current context:        │
│                                                 │
│ → "Show tasks blocking MVP launch"             │
│ → "What should I work on after lunch?"         │
│ → "Create task: Review PRD with team"          │
│ → "Analyze my work-life balance"               │
│                                                 │
│ Recent Commands:                                │
│ • Generated daily plan (2 hours ago)            │
│ • Found high-priority tasks (Yesterday)         │
└─────────────────────────────────────────────────┘
```

### Mobile Layout
```
┌─────────────────────────┐
│ [🎤] [Ask AI...] [📷]  │
├─────────────────────────┤
│ Quick Actions:          │
│ ┌──────┐ ┌──────┐      │
│ │ Add  │ │ Find │      │
│ │ Task │ │ Task │      │
│ └──────┘ └──────┘      │
│ ┌──────┐ ┌──────┐      │
│ │ Plan │ │What's│      │
│ │ Day  │ │ Next │      │
│ └──────┘ └──────┘      │
│                         │
│ Recent:                 │
│ • "Add grocery task"    │
│ • "Show today's plan"   │
└─────────────────────────┘
```

### Features
- **Natural Language Processing**: Understands intent and context
- **Voice Input**: Speak commands (mobile primary, web secondary)
- **Smart Suggestions**: Context-aware command predictions
- **Multi-Modal Input**: Text, voice, image (receipt → task)
- **Command History**: Recent and frequent commands
- **Keyboard Navigation**: Arrow keys to select, Tab to autocomplete

### Key Interactions
- **Trigger**: Cmd/Ctrl+K (web), Swipe down (mobile)
- **Voice**: Hold spacebar (web), tap mic (mobile)
- **Quick Actions**: Single tap shortcuts for common commands
- **Escape**: Closes without action

---

## 2. AI Insights Dashboard (Enhanced)

### Purpose
Central hub for all AI-generated insights, reasoning paths, and system learning progress.

### Web Layout
```
┌─────────────────────────────────────────────────────────┐
│ AI Intelligence Center         [Settings] [Help]         │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │
│ │ Confidence  │ │ Insights    │ │ Learning    │        │
│ │    87%      │ │    156      │ │  +12% ↑     │        │
│ │ This Week   │ │ Generated   │ │ This Month  │        │
│ └─────────────┘ └─────────────┘ └─────────────┘        │
│                                                         │
│ [All] [Priority] [Alignment] [Obstacles] [Patterns]     │
│                                                         │
│ ┌─────────────────────────────────────────────────┐    │
│ │ 🎯 High Priority Insight                        │    │
│ │ Your "Launch MVP" project is at risk           │    │
│ │ 3 blocking tasks haven't moved in a week       │    │
│ │ [View Details] [Take Action] [Dismiss]          │    │
│ └─────────────────────────────────────────────────┘    │
│                                                         │
│ ┌─────────────────────────────────────────────────┐    │
│ │ 🔄 Pattern Detected                             │    │
│ │ You're most productive Tue-Thu mornings        │    │
│ │ Consider scheduling deep work during these      │    │
│ │ [Apply to Schedule] [Learn More]                │    │
│ └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### Mobile Layout
```
┌─────────────────────────┐
│ AI Insights      [⚙️]   │
├─────────────────────────┤
│ ┌───────────────────┐   │
│ │ 87% Confidence    │   │
│ │ 156 Insights      │   │
│ │ +12% Learning     │   │
│ └───────────────────┘   │
│                         │
│ [All] [Priority] [...]  │
│                         │
│ ┌───────────────────┐   │
│ │ 🎯 Project Risk   │   │
│ │ MVP is blocked    │   │
│ │ [→ View] [✓ Act] │   │
│ └───────────────────┘   │
│                         │
│ ┌───────────────────┐   │
│ │ 🔄 Pattern Found  │   │
│ │ Tue-Thu mornings  │   │
│ │ are your peak     │   │
│ │ [Apply] [More]    │   │
│ └───────────────────┘   │
└─────────────────────────┘
```

### Features
- **Insight Cards**: Prioritized by impact and relevance
- **Confidence Metrics**: Visual indicators of AI certainty
- **Learning Progress**: Shows AI improvement over time
- **Filter System**: By type, date, confidence, entity
- **Batch Actions**: Apply multiple insights at once
- **Export Reports**: PDF/CSV for external sharing

---

## 3. Quick Capture (Mobile-First)

### Purpose
Lightning-fast task/idea capture with minimal friction, optimized for on-the-go use.

### Mobile Layout (Primary)
```
┌─────────────────────────┐
│        Quick Add        │
├─────────────────────────┤
│                         │
│ [🎤 Hold to speak...]   │
│                         │
│ OR type:                │
│ [________________]      │
│                         │
│ Capture as:             │
│ ┌─────┐ ┌─────┐ ┌────┐│
│ │Task │ │Idea │ │Note││
│ └─────┘ └─────┘ └────┘│
│                         │
│ AI Suggests:            │
│ Project: [Current ▼]    │
│ Priority: [Medium ▼]    │
│ Due: [Tomorrow ▼]       │
│                         │
│ [📷 Add Photo]          │
│                         │
│ [Save & Add Another]    │
│ [Save & Close]          │
└─────────────────────────┘
```

### Web Layout (Floating Widget)
```
┌─────────────────────────────┐
│ ➕ Quick Capture      [X]   │
├─────────────────────────────│
│ [What's on your mind?...]   │
│                             │
│ 🎤 📷 📎  [Task ▼]          │
│                             │
│ AI: Sounds like a task for  │
│ your "Product Launch" proj   │
│                             │
│ [Create] [Create & Another]  │
└─────────────────────────────┘
```

### Features
- **Voice-First**: Tap and speak for instant capture
- **Smart Parsing**: AI extracts task, project, deadline from natural language
- **Photo Capture**: Receipt/whiteboard → structured task
- **Offline Support**: Queue for sync when connected
- **Quick Shortcuts**: Swipe patterns for common captures
- **AI Classification**: Automatic categorization

---

## 4. Focus Mode (Productivity Screen)

### Purpose
Distraction-free environment for deep work with AI-powered support.

### Web Layout
```
┌─────────────────────────────────────────────────────────┐
│                     FOCUS MODE                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│              Write Product Requirements Doc              │
│                    Project: MVP Launch                   │
│                                                         │
│                    ⏱️ 01:23:45                          │
│                 ████████████░░░░░░                      │
│                  Suggested: 2 hours                      │
│                                                         │
│    [⏸️ Pause]  [✓ Complete]  [❌ Exit Focus]           │
│                                                         │
│ ┌─────────────────────────────────────────────────┐    │
│ │ 🤖 AI Coach: You're in your peak focus hours.   │    │
│ │ Last time this took 1h 45m. You're on track!    │    │
│ └─────────────────────────────────────────────────┘    │
│                                                         │
│ Related Context:                                         │
│ • Previous version took 1h 45m                          │
│ • Team meeting notes attached                           │
│ • Similar tasks: Design Doc (1h 30m)                   │
└─────────────────────────────────────────────────────────┘
```

### Mobile Layout
```
┌─────────────────────────┐
│    ⏱️ 01:23:45         │
│  ████████████░░░░░░     │
├─────────────────────────┤
│                         │
│  Write Product          │
│  Requirements Doc       │
│                         │
│  MVP Launch             │
│                         │
├─────────────────────────┤
│ 🤖 On track! Last time │
│ this took 1h 45m        │
├─────────────────────────┤
│ [⏸️]  [✓]  [❌]        │
└─────────────────────────┘
```

### Features
- **Distraction Blocking**: Hides all navigation
- **AI Time Estimates**: Based on historical data
- **Contextual Encouragement**: Personalized coaching
- **Break Reminders**: Pomodoro-style with AI timing
- **Progress Tracking**: Visual and statistical
- **Background Music**: Optional focus soundscapes

---

## 5. Daily Planning Ritual

### Purpose
Guided morning planning session with AI assistance for optimal day structure.

### Web Layout
```
┌─────────────────────────────────────────────────────────┐
│              Good Morning! Let's Plan Your Day          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ 1. How's your energy today?                            │
│    [😴 Low] [😐 Medium] [😊 High] [🚀 Peak]           │
│                                                         │
│ 2. Available time blocks: (AI detected from calendar)   │
│    ✓ 9:00-10:30  (90 min) - Deep work window          │
│    ✓ 11:00-12:00 (60 min) - Medium focus              │
│    ✓ 2:00-3:30   (90 min) - Post-lunch block          │
│                                                         │
│ 3. AI Recommended Schedule:                             │
│ ┌─────────────────────────────────────────────────┐    │
│ │ 9:00  │ 🎯 Write PRD (Deep work)                │    │
│ │       │    Aligns with MVP launch goal          │    │
│ ├───────┼─────────────────────────────────────────┤    │
│ │ 11:00 │ 📧 Process emails & messages            │    │
│ │       │    Lower energy requirement             │    │
│ ├───────┼─────────────────────────────────────────┤    │
│ │ 2:00  │ 🤝 Review with team                     │    │
│ │       │    Collaborative energy                 │    │
│ └─────────────────────────────────────────────────┘    │
│                                                         │
│ [Adjust Schedule] [Accept & Start Day] [Skip Planning]  │
└─────────────────────────────────────────────────────────┘
```

### Mobile Layout
```
┌─────────────────────────┐
│ Good Morning! 👋        │
├─────────────────────────┤
│ Energy today?           │
│ [😴][😐][😊][🚀]       │
├─────────────────────────┤
│ Your optimal schedule:  │
│                         │
│ 9:00 - Write PRD 🎯    │
│ ↳ Deep work window      │
│                         │
│ 11:00 - Emails 📧       │
│ ↳ Low energy task       │
│                         │
│ 2:00 - Team Review 🤝   │
│ ↳ Collaboration time    │
│                         │
│ [Adjust] [Start Day]    │
└─────────────────────────┘
```

### Features
- **Energy Check-in**: Adapts plan to current state
- **Calendar Integration**: Finds available time blocks
- **Smart Scheduling**: Matches tasks to energy/time
- **Drag to Adjust**: Reorder suggested schedule
- **One-Tap Accept**: Start day with AI plan
- **Learning System**: Improves suggestions over time

---

## 6. AI Memory & Preferences

### Purpose
Manage what the AI remembers about you and how it behaves.

### Web Layout
```
┌─────────────────────────────────────────────────────────┐
│                    AI Preferences & Memory              │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────┐ ┌─────────────────────────────┐│
│ │ AI Personality      │ │ What AI Knows About You    ││
│ │                     │ │                            ││
│ │ Style:              │ │ ✓ Prefers morning deep work││
│ │ [Coach ▼]           │ │ ✓ Career pillar is priority││
│ │                     │ │ ✓ 2-hour focus blocks best ││
│ │ Tone:               │ │ ✓ Dislikes meetings < 30min││
│ │ ○ Encouraging       │ │                            ││
│ │ ● Direct            │ │ + Add memory...            ││
│ │ ○ Analytical        │ │                            ││
│ │                     │ │ [Export] [Clear All]       ││
│ └─────────────────────┘ └─────────────────────────────┘│
│                                                         │
│ ┌─────────────────────────────────────────────────────┐│
│ │ Reasoning Preferences                               ││
│ │                                                     ││
│ │ Show confidence scores:        [On ▼]              ││
│ │ Explanation detail:            [Balanced ▼]        ││
│ │ Proactive suggestions:         [Smart ▼]           ││
│ │ Learning from my feedback:     [On ▼]              ││
│ └─────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

### Mobile Layout
```
┌─────────────────────────┐
│ AI Settings        [<]  │
├─────────────────────────┤
│ Personality             │
│ [Coach ▼]               │
│ ○ Encouraging           │
│ ● Direct                │
│                         │
│ AI Memories             │
│ ┌───────────────────┐   │
│ │✓ Morning deep work│   │
│ │✓ Career priority  │   │
│ │✓ 2-hour blocks    │   │
│ │[+ Add]            │   │
│ └───────────────────┘   │
│                         │
│ Preferences             │
│ Confidence: [On ▼]      │
│ Details: [Balanced ▼]   │
│ Learn: [On ▼]           │
└─────────────────────────┘
```

### Features
- **Personality Picker**: Choose AI communication style
- **Memory Management**: See and edit what AI remembers
- **Privacy Controls**: Delete specific memories
- **Preference Sliders**: Fine-tune AI behavior
- **Export Data**: Download all AI knowledge
- **Reset Options**: Start fresh with AI

---

## 7. Visual Life Map

### Purpose
Interactive visualization of entire PAPT hierarchy with AI insights overlay.

### Web Layout
```
┌─────────────────────────────────────────────────────────┐
│                      Your Life Map                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│     Career 🎯                    Health 💪              │
│       (40%)                       (30%)                 │
│         │                           │                   │
│    ┌────┴────┐                 ┌────┴────┐            │
│    │Product  │                 │Fitness  │            │
│    │Leader   │                 │         │            │
│    └────┬────┘                 └────┬────┘            │
│         │                           │                   │
│   ┌─────┴──────┐            ┌──────┴──────┐          │
│   │MVP Launch  │            │Marathon Prep│          │
│   │⚠️ At Risk  │            │✅ On Track │          │
│   └─────┬──────┘            └──────┬──────┘          │
│         │                           │                   │
│   [5 tasks]                   [8 tasks]               │
│   3 blocked                    2 due today             │
│                                                         │
│ AI Insights:                                            │
│ • Career pillar consuming 55% time (target: 40%)       │
│ • Health goals may suffer without rebalancing          │
│                                                         │
│ [Zoom In] [Filter] [Rebalance] [Export]                │
└─────────────────────────────────────────────────────────┘
```

### Mobile Layout (Vertical Tree)
```
┌─────────────────────────┐
│ Life Map          [≡]   │
├─────────────────────────┤
│ Career 🎯 (40%)         │
│ └─ Product Leader       │
│    └─ MVP Launch ⚠️     │
│       5 tasks, 3 blocked│
│                         │
│ Health 💪 (30%)         │
│ └─ Fitness              │
│    └─ Marathon ✅       │
│       8 tasks           │
│                         │
│ [+] Relationships (20%) │
│ [+] Growth (10%)        │
│                         │
│ ⚠️ Time imbalance       │
│ [View Details]          │
└─────────────────────────┘
```

### Features
- **Interactive Nodes**: Tap to expand/collapse
- **Health Indicators**: Visual status of each node
- **Time Flow**: See actual vs planned allocation
- **Drag to Reorganize**: Move projects between areas
- **AI Annotations**: Insights appear on hover/tap
- **Filter Views**: By status, time period, health

---

## 8. Weekly Review Dashboard

### Purpose
AI-guided weekly reflection and planning session.

### Web Layout
```
┌─────────────────────────────────────────────────────────┐
│                 Weekly Review - Week 45                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Your Week at a Glance:                                 │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
│ │ 24/28        │ │ 85%          │ │ +2 hrs       │    │
│ │ Tasks Done   │ │ On Schedule  │ │ Deep Work    │    │
│ └──────────────┘ └──────────────┘ └──────────────┘    │
│                                                         │
│ AI Analysis:                                            │
│ ✅ Strong week for Career pillar (90% completion)      │
│ ⚠️ Health pillar neglected (only 1 workout)           │
│ 💡 Tuesday/Thursday were your most productive days     │
│                                                         │
│ Reflection Prompts:                                     │
│ 1. What was your biggest win? [________________]       │
│ 2. What held you back? [________________]              │
│ 3. Energy levels this week? [Low|Medium|High]          │
│                                                         │
│ Next Week Preview:                                      │
│ • 3 critical deadlines approaching                     │
│ • Suggested focus: Complete MVP documentation          │
│ • Recommended: Block 2 mornings for deep work          │
│                                                         │
│ [Complete Review] [Plan Next Week] [Skip]               │
└─────────────────────────────────────────────────────────┘
```

### Mobile Layout
```
┌─────────────────────────┐
│ Week 45 Review     [X]  │
├─────────────────────────┤
│ ┌───┐ ┌───┐ ┌───┐      │
│ │24 │ │85%│ │+2h│      │
│ │/28│ │ ✓ │ │🧠│      │
│ └───┘ └───┘ └───┘      │
│                         │
│ AI Insights:            │
│ ✅ Career strong (90%)  │
│ ⚠️ Health weak (20%)   │
│                         │
│ Biggest win?            │
│ [_________________]     │
│                         │
│ What held you back?     │
│ [_________________]     │
│                         │
│ Next week: 3 deadlines  │
│ [Plan Week] [Later]     │
└─────────────────────────┘
```

### Features
- **Automated Metrics**: Pre-calculated by AI
- **Pattern Recognition**: Identifies trends
- **Guided Reflection**: Smart prompts based on data
- **Voice Notes**: Record audio reflections
- **Comparison View**: Week-over-week progress
- **Export Journal**: Save reflections externally

---

## 9. Smart Notification Center

### Purpose
AI-curated notifications with intelligent grouping and prioritization.

### Mobile Layout (Primary)
```
┌─────────────────────────┐
│ Notifications      [⚙️] │
├─────────────────────────┤
│ Now (2)                 │
│ ┌───────────────────┐   │
│ │🚨 Deadline Alert  │   │
│ │PRD due in 2 hours │   │
│ │[Start] [Snooze]   │   │
│ └───────────────────┘   │
│                         │
│ Today (5)               │
│ ┌───────────────────┐   │
│ │📊 Daily Summary   │   │
│ │3 tasks to review  │   │
│ │[Expand] [Clear]   │   │
│ └───────────────────┘   │
│                         │
│ This Week (12)          │
│ [View All]              │
└─────────────────────────┘
```

### Features
- **Smart Grouping**: By urgency, not just time
- **AI Summaries**: "5 similar tasks" → one notification
- **Action Buttons**: Take action without opening app
- **Quiet Hours**: AI learns when not to disturb
- **Batch Operations**: Clear/snooze multiple at once
- **Priority Only Mode**: Just critical notifications

---

## 10. Mobile Quick Actions Menu

### Purpose
Fast access to common actions via gesture or 3D touch.

### Mobile Layout
```
┌─────────────────────────┐
│     Quick Actions       │
├─────────────────────────┤
│ ┌───────┐ ┌───────┐    │
│ │  📝   │ │  🎤   │    │
│ │ Task  │ │ Voice │    │
│ └───────┘ └───────┘    │
│                         │
│ ┌───────┐ ┌───────┐    │
│ │  📸   │ │  ⏱️   │    │
│ │ Photo │ │ Timer │    │
│ └───────┘ └───────┘    │
│                         │
│ ┌───────┐ ┌───────┐    │
│ │  🤖   │ │  📊   │    │
│ │What's │ │Today's│    │
│ │ Next? │ │ Stats │    │
│ └───────┘ └───────┘    │
│                         │
│ [Close]                 │
└─────────────────────────┘
```

### Features
- **Gesture Activated**: Long press app icon
- **Customizable Grid**: Reorder based on usage
- **Voice Commands**: Direct to voice input
- **Quick Timer**: Start focus session instantly
- **AI Queries**: Fast access to common questions

---

## Design System Additions

### New Components
1. **AIInsightCard**: Consistent insight display
2. **VoiceInputButton**: Universal voice interaction
3. **ProgressRing**: Visual progress indicators
4. **HierarchyNode**: Tree view components
5. **TimeBlock**: Calendar-style time slots
6. **ConfidenceMeter**: AI confidence display
7. **QuickActionGrid**: Mobile action launcher
8. **FocusTimer**: Distraction-free timer

### New Design Tokens
```scss
// AI-specific colors
$ai-primary: #3B82F6;
$ai-secondary: #8B5CF6;
$ai-success: #10B981;
$ai-warning: #F59E0B;
$ai-danger: #EF4444;
$ai-surface: #1E293B;
$ai-surface-light: #334155;

// Mobile-specific spacing
$mobile-safe-area-top: env(safe-area-inset-top);
$mobile-safe-area-bottom: env(safe-area-inset-bottom);
$mobile-thumb-reach: 64px;
$mobile-gesture-target: 44px;

// Animation presets
$ai-fade-in: 200ms ease-out;
$ai-slide-up: 300ms cubic-bezier(0.34, 1.56, 0.64, 1);
$ai-pulse: 2s ease-in-out infinite;
```

### Responsive Breakpoints
```scss
$mobile-small: 320px;   // iPhone SE
$mobile-medium: 375px;  // iPhone 12/13
$mobile-large: 428px;   // iPhone 14 Pro Max
$tablet: 768px;         // iPad
$desktop: 1024px;       // Desktop
$desktop-large: 1440px; // Large screens
```

---

## Navigation Flow

### Web Navigation
1. **Global Command**: Cmd+K from anywhere
2. **Sidebar**: Persistent navigation
3. **Breadcrumbs**: Hierarchical location
4. **Quick Switch**: Tab through recent screens

### Mobile Navigation
1. **Bottom Tab Bar**: Core sections
2. **Swipe Gestures**: Between related screens
3. **Pull Actions**: Refresh and quick add
4. **Deep Press**: Quick actions menu

---

## Performance Considerations

### Web Optimizations
- Lazy load visualization components
- Virtual scrolling for long lists
- WebSocket for real-time updates
- Service worker for offline support

### Mobile Optimizations
- Aggressive caching of current day data
- Background sync for changes
- Reduced animation in low power mode
- Progressive image loading

---

## Accessibility Features

### Universal
- Voice control for all major actions
- High contrast mode support
- Keyboard navigation complete
- Screen reader optimized

### Mobile Specific
- Haptic feedback for actions
- Large touch targets (minimum 44px)
- One-handed operation mode
- Reduced motion options

---

This specification provides a complete blueprint for implementing the new screens across web and mobile platforms, with a focus on AI integration and user convenience.