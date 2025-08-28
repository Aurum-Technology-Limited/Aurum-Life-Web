# Aurum Life Web Wireframes - Enhanced AI Architecture

## Design System Constants
- **Background**: `#0B0D14` (Main), `#111827` (gray-900), `#1F2937` (gray-800)
- **Primary**: `#F59E0B` (yellow-500), `#D97706` (yellow-600)
- **Text**: `#FFFFFF` (white), `#D1D5DB` (gray-300), `#9CA3AF` (gray-400)
- **Borders**: `#374151` (gray-700), `#1F2937` (gray-800)
- **AI Accent**: `#3B82F6` (blue-500)

---

## 1. AI Command Center (Universal Search)

```
┌────────────────────────────────────────────────────────────────────────────┐
│ Background: #0B0D14                                                        │
│ ┌────────────────────────────────────────────────────────────────────────┐ │
│ │ Border: #374151 (gray-700)                                             │ │
│ │ Background: #1F2937 (gray-800)                                         │ │
│ │ Padding: 16px                                                          │ │
│ │ Border-radius: 12px                                                    │ │
│ │ Box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5)                      │ │
│ │                                                                        │ │
│ │ ┌────────────────────────────────────────────────────────────────┐   │ │
│ │ │ ⌘K  [🔍] [🎤] Ask AI anything or type a command...            │   │ │
│ │ │ Font: 16px                                                      │   │ │
│ │ │ Color: #D1D5DB (gray-300)                                      │   │ │
│ │ │ Background: #111827 (gray-900)                                 │   │ │
│ │ │ Border: 1px solid #374151                                      │   │ │
│ │ │ Height: 48px                                                    │   │ │
│ │ └────────────────────────────────────────────────────────────────┘   │ │
│ │                                                                        │ │
│ │ AI Suggestions (margin-top: 16px)                                      │ │
│ │ ┌────────────────────────────────────────────────────────────────┐   │ │
│ │ │ 💡 Color: #3B82F6 (blue-500)  Font: 14px bold                  │   │ │
│ │ └────────────────────────────────────────────────────────────────┘   │ │
│ │                                                                        │ │
│ │ ┌────────────────────────────────────────────────────────────────┐   │ │
│ │ │ → "Show tasks blocking MVP launch"                             │   │ │
│ │ │ Padding: 12px 16px | Hover: bg-#374151 | Cursor: pointer       │   │ │
│ │ ├────────────────────────────────────────────────────────────────┤   │ │
│ │ │ → "What should I work on after lunch?"                         │   │ │
│ │ │ Color: #D1D5DB | Icon: #F59E0B                                 │   │ │
│ │ ├────────────────────────────────────────────────────────────────┤   │ │
│ │ │ → "Create task: Review PRD with team"                          │   │ │
│ │ ├────────────────────────────────────────────────────────────────┤   │ │
│ │ │ → "Analyze my work-life balance"                               │   │ │
│ │ └────────────────────────────────────────────────────────────────┘   │ │
│ │                                                                        │ │
│ │ Recent Commands (margin-top: 24px)                                     │ │
│ │ ┌────────────────────────────────────────────────────────────────┐   │ │
│ │ │ Color: #9CA3AF (gray-400) | Font: 12px uppercase               │   │ │
│ │ └────────────────────────────────────────────────────────────────┘   │ │
│ │                                                                        │ │
│ │ ┌────────────────────────────────────────────────────────────────┐   │ │
│ │ │ • Generated daily plan (2 hours ago)                           │   │ │
│ │ │ • Found high-priority tasks (Yesterday)                        │   │ │
│ │ └────────────────────────────────────────────────────────────────┘   │ │
│ └────────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. AI Insights Dashboard

```
┌────────────────────────────────────────────────────────────────────────────┐
│ Background: #0B0D14 | Padding: 24px                                        │
│                                                                            │
│ ┌────────────────────────────────────────────────────────────────────────┐ │
│ │ Header Section                                                          │ │
│ │ ┌──────────────────────────────────────┬────────────────────────────┐ │ │
│ │ │ 🧠 AI Intelligence Center            │ [Settings ⚙️] [Help ?]      │ │ │
│ │ │ Font: 24px bold | Color: white       │ Color: #9CA3AF              │ │ │
│ │ │ Icon: 32px | Color: #3B82F6          │                              │ │ │
│ │ └──────────────────────────────────────┴────────────────────────────┘ │ │
│ └────────────────────────────────────────────────────────────────────────┘ │
│                                                                            │
│ Stats Cards (Grid: 3 columns | Gap: 16px | Margin-top: 24px)              │
│ ┌─────────────────────┬─────────────────────┬─────────────────────┐      │
│ │ Background: #1F2937 │ Background: #1F2937 │ Background: #1F2937 │      │
│ │ Border: #374151     │ Border: #374151     │ Border: #374151     │      │
│ │ Padding: 24px       │ Padding: 24px       │ Padding: 24px       │      │
│ │ Border-radius: 12px │ Border-radius: 12px │ Border-radius: 12px │      │
│ │                     │                     │                     │      │
│ │ Confidence          │ Insights            │ Learning            │      │
│ │ 87%                 │ 156                 │ +12% ↑              │      │
│ │ Font: 36px bold     │ Font: 36px bold     │ Font: 36px bold     │      │
│ │ Color: #10B981      │ Color: #3B82F6      │ Color: #F59E0B      │      │
│ │                     │                     │                     │      │
│ │ This Week           │ Generated           │ This Month          │      │
│ │ Font: 14px          │ Font: 14px          │ Font: 14px          │      │
│ │ Color: #9CA3AF      │ Color: #9CA3AF      │ Color: #9CA3AF      │      │
│ └─────────────────────┴─────────────────────┴─────────────────────┘      │
│                                                                            │
│ Filter Tabs (Margin-top: 32px)                                             │
│ ┌────────────────────────────────────────────────────────────────────────┐ │
│ │ [All] [Priority] [Alignment] [Obstacles] [Patterns]                     │ │
│ │ Active: bg-#F59E0B text-black | Inactive: text-#9CA3AF hover:text-white│ │
│ │ Padding: 8px 16px | Border-radius: 8px | Font: 14px medium             │ │
│ └────────────────────────────────────────────────────────────────────────┘ │
│                                                                            │
│ Insights List (Margin-top: 24px | Gap: 16px)                              │
│ ┌────────────────────────────────────────────────────────────────────────┐ │
│ │ Insight Card 1                                                          │ │
│ │ Background: #1F2937 | Border: #374151 | Padding: 20px | Radius: 12px   │ │
│ │ ┌──────────────────────────────────────────────────────────────────┐   │ │
│ │ │ 🎯 High Priority Insight                          87% confident  │   │ │
│ │ │ Icon: 24px | Title: 16px bold white              Color: #10B981 │   │ │
│ │ ├──────────────────────────────────────────────────────────────────┤   │ │
│ │ │ Your "Launch MVP" project is at risk due to 3 blocking tasks    │   │ │
│ │ │ that haven't moved in a week. Consider prioritizing these.      │   │ │
│ │ │ Font: 14px | Color: #D1D5DB | Line-height: 1.5                  │   │ │
│ │ ├──────────────────────────────────────────────────────────────────┤   │ │
│ │ │ [View Details] [Take Action] [👍] [👎] [Dismiss]                │   │ │
│ │ │ Buttons: px-3 py-1.5 | Font: 12px | Border-radius: 6px          │   │ │
│ │ │ Primary: bg-#F59E0B text-black | Secondary: border-#374151      │   │ │
│ │ └──────────────────────────────────────────────────────────────────┘   │ │
│ └────────────────────────────────────────────────────────────────────────┘ │
│                                                                            │
│ ┌────────────────────────────────────────────────────────────────────────┐ │
│ │ Insight Card 2                                                          │ │
│ │ Background: #1F2937 | Border: #374151 | Padding: 20px                  │ │
│ │ ┌──────────────────────────────────────────────────────────────────┐   │ │
│ │ │ 🔄 Pattern Detected                               92% confident  │   │ │
│ │ │ Icon: 24px | Title: 16px bold white              Color: #10B981 │   │ │
│ │ ├──────────────────────────────────────────────────────────────────┤   │ │
│ │ │ You're most productive on Tuesday-Thursday mornings (9-11 AM).  │   │ │
│ │ │ Consider scheduling your deep work during these peak hours.     │   │ │
│ │ ├──────────────────────────────────────────────────────────────────┤   │ │
│ │ │ [Apply to Schedule] [Learn More] [👍] [👎]                      │   │ │
│ │ └──────────────────────────────────────────────────────────────────┘   │ │
│ └────────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Focus Mode

```
┌────────────────────────────────────────────────────────────────────────────┐
│ Background: #0B0D14 | Height: 100vh | Display: flex | Align: center        │
│                                                                            │
│ ┌────────────────────────────────────────────────────────────────────────┐ │
│ │ Container: max-width-2xl | margin: auto | padding: 48px                 │ │
│ │                                                                          │ │
│ │ ┌────────────────────────────────────────────────────────────────────┐ │ │
│ │ │                         FOCUS MODE                                   │ │ │
│ │ │ Font: 14px uppercase | Color: #9CA3AF | Letter-spacing: 0.1em       │ │ │
│ │ │ Text-align: center | Margin-bottom: 32px                            │ │ │
│ │ └────────────────────────────────────────────────────────────────────┘ │ │
│ │                                                                          │ │
│ │ ┌────────────────────────────────────────────────────────────────────┐ │ │
│ │ │               Write Product Requirements Doc                         │ │ │
│ │ │ Font: 32px bold | Color: white | Text-align: center                 │ │ │
│ │ │                                                                      │ │ │
│ │ │                   Project: MVP Launch                                │ │ │
│ │ │ Font: 16px | Color: #9CA3AF | Margin-top: 8px                       │ │ │
│ │ └────────────────────────────────────────────────────────────────────┘ │ │
│ │                                                                          │ │
│ │ ┌────────────────────────────────────────────────────────────────────┐ │ │
│ │ │                        ⏱️ 01:23:45                                   │ │ │
│ │ │ Font: 48px | Font-family: monospace | Color: white                  │ │ │
│ │ │ Text-align: center | Margin: 48px 0                                 │ │ │
│ │ │                                                                      │ │ │
│ │ │ ┌──────────────────────────────────────────────────────────────┐   │ │ │
│ │ │ │ Progress Bar Container | Height: 8px | Bg: #374151            │   │ │ │
│ │ │ │ ████████████████████░░░░░░░░░░░░                             │   │ │ │
│ │ │ │ Fill: bg-gradient-to-r from-#F59E0B to-#D97706 | Width: 65%  │   │ │ │
│ │ │ └──────────────────────────────────────────────────────────────┘   │ │ │
│ │ │                                                                      │ │ │
│ │ │                    Suggested: 2 hours                                │ │ │
│ │ │ Font: 14px | Color: #9CA3AF | Text-align: center                    │ │ │
│ │ └────────────────────────────────────────────────────────────────────┘ │ │
│ │                                                                          │ │
│ │ ┌────────────────────────────────────────────────────────────────────┐ │ │
│ │ │ [⏸️ Pause]        [✓ Complete]        [❌ Exit Focus]               │ │ │
│ │ │ Display: flex | Gap: 16px | Justify: center                         │ │ │
│ │ │ Buttons: px-6 py-3 | Font: 16px medium | Border-radius: 8px        │ │ │
│ │ │ Primary: bg-#F59E0B hover:bg-#D97706 | Secondary: border-#374151   │ │ │
│ │ └────────────────────────────────────────────────────────────────────┘ │ │
│ │                                                                          │ │
│ │ ┌────────────────────────────────────────────────────────────────────┐ │ │
│ │ │ AI Coach Box                                                         │ │ │
│ │ │ Background: #1F2937 | Border: #3B82F6 | Padding: 16px | Radius: 12px│ │ │
│ │ │ Margin-top: 48px                                                     │ │ │
│ │ │                                                                      │ │ │
│ │ │ 🤖 You're in your peak focus hours. Last time this task took       │ │ │
│ │ │    1h 45m. You're on track to finish ahead of schedule!            │ │ │
│ │ │                                                                      │ │ │
│ │ │ Icon: 20px | Color: #3B82F6 | Text: 14px | Color: #D1D5DB          │ │ │
│ │ └────────────────────────────────────────────────────────────────────┘ │ │
│ └────────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Daily Planning Ritual

```
┌────────────────────────────────────────────────────────────────────────────┐
│ Background: #0B0D14 | Padding: 32px                                        │
│                                                                            │
│ ┌────────────────────────────────────────────────────────────────────────┐ │
│ │ Container: max-width-4xl | Background: #111827 | Border: #374151        │ │
│ │ Border-radius: 16px | Padding: 32px                                     │ │
│ │                                                                          │ │
│ │ ┌────────────────────────────────────────────────────────────────────┐ │ │
│ │ │              ☀️ Good Morning! Let's Plan Your Day                    │ │ │
│ │ │ Font: 24px bold | Color: white | Text-align: center                 │ │ │
│ │ │ Icon: 32px | Margin-bottom: 32px                                    │ │ │
│ │ └────────────────────────────────────────────────────────────────────┘ │ │
│ │                                                                          │ │
│ │ Step 1: Energy Check                                                     │ │
│ │ ┌────────────────────────────────────────────────────────────────────┐ │ │
│ │ │ Background: #1F2937 | Border: #374151 | Padding: 24px | Radius: 12px│ │ │
│ │ │                                                                      │ │ │
│ │ │ How's your energy today?                                            │ │ │
│ │ │ Font: 16px medium | Color: white | Margin-bottom: 16px             │ │ │
│ │ │                                                                      │ │ │
│ │ │ ┌────────┬────────┬────────┬────────┐                              │ │ │
│ │ │ │  😴    │  😐    │  😊    │  🚀    │                              │ │ │
│ │ │ │  Low   │ Medium │  High  │  Peak  │                              │ │ │
│ │ │ └────────┴────────┴────────┴────────┘                              │ │ │
│ │ │ Buttons: flex-1 | py-3 | Border: #374151 | Hover: border-#F59E0B   │ │ │
│ │ │ Selected: bg-#F59E0B text-black                                     │ │ │
│ │ └────────────────────────────────────────────────────────────────────┘ │ │
│ │                                                                          │ │
│ │ Step 2: Available Time Blocks                                            │ │
│ │ ┌────────────────────────────────────────────────────────────────────┐ │ │
│ │ │ Background: #1F2937 | Border: #374151 | Padding: 24px              │ │ │
│ │ │                                                                      │ │ │
│ │ │ Available time blocks (AI detected from calendar):                  │ │ │
│ │ │                                                                      │ │ │
│ │ │ ✓ 9:00-10:30  (90 min) - Deep work window                          │ │ │
│ │ │ ✓ 11:00-12:00 (60 min) - Medium focus                              │ │ │
│ │ │ ✓ 2:00-3:30   (90 min) - Post-lunch block                          │ │ │
│ │ │                                                                      │ │ │
│ │ │ Check: #10B981 | Time: font-mono | Duration: #9CA3AF               │ │ │
│ │ └────────────────────────────────────────────────────────────────────┘ │ │
│ │                                                                          │ │
│ │ Step 3: AI Recommended Schedule                                          │ │
│ │ ┌────────────────────────────────────────────────────────────────────┐ │ │
│ │ │ Background: #1F2937 | Border: #3B82F6 | Padding: 0 | Radius: 12px   │ │ │
│ │ │                                                                      │ │ │
│ │ │ ┌─────────┬────────────────────────────────────────────────────┐   │ │ │
│ │ │ │ 9:00 AM │ 🎯 Write PRD (Deep work)                           │   │ │ │
│ │ │ │ #374151 │ Background: #111827 | Padding: 16px                │   │ │ │
│ │ │ │ Width:  │ Task: Font: 16px medium | Color: white            │   │ │ │
│ │ │ │ 80px    │ Reason: Font: 14px | Color: #9CA3AF               │   │ │ │
│ │ │ │         │ ↳ Aligns with MVP launch goal                      │   │ │ │
│ │ │ ├─────────┼────────────────────────────────────────────────────┤   │ │ │
│ │ │ │ 11:00   │ 📧 Process emails & messages                      │   │ │ │
│ │ │ │         │ ↳ Lower energy requirement                         │   │ │ │
│ │ │ ├─────────┼────────────────────────────────────────────────────┤   │ │ │
│ │ │ │ 2:00 PM │ 🤝 Review with team                               │   │ │ │
│ │ │ │         │ ↳ Collaborative energy                             │   │ │ │
│ │ │ └─────────┴────────────────────────────────────────────────────┘   │ │ │
│ │ └────────────────────────────────────────────────────────────────────┘ │ │
│ │                                                                          │ │
│ │ ┌────────────────────────────────────────────────────────────────────┐ │ │
│ │ │ [Adjust Schedule]    [Accept & Start Day]    [Skip Planning]        │ │ │
│ │ │ Display: flex | Gap: 16px | Justify: center | Margin-top: 32px     │ │ │
│ │ │ Primary: bg-gradient from-#F59E0B to-#D97706 | px-8 py-3           │ │ │
│ │ └────────────────────────────────────────────────────────────────────┘ │ │
│ └────────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. AI Memory & Preferences

```
┌────────────────────────────────────────────────────────────────────────────┐
│ Background: #0B0D14 | Padding: 24px                                        │
│                                                                            │
│ ┌────────────────────────────────────────────────────────────────────────┐ │
│ │ Header                                                                   │ │
│ │ ┌──────────────────────────────────────────────────────────────────┐   │ │
│ │ │ 🧠 AI Preferences & Memory                                        │   │ │
│ │ │ Font: 24px bold | Color: white | Icon: #3B82F6                   │   │ │
│ │ └──────────────────────────────────────────────────────────────────┘   │ │
│ └────────────────────────────────────────────────────────────────────────┘ │
│                                                                            │
│ Grid Layout: 2 columns | Gap: 24px | Margin-top: 32px                      │
│ ┌─────────────────────────────────────┬─────────────────────────────────┐ │
│ │ AI Personality                      │ What AI Knows About You         │ │
│ │ Background: #111827                 │ Background: #111827             │ │
│ │ Border: #374151 | Radius: 12px      │ Border: #374151 | Radius: 12px  │ │
│ │ Padding: 24px                       │ Padding: 24px                   │ │
│ │                                     │                                 │ │
│ │ ┌───────────────────────────────┐   │ ┌─────────────────────────────┐ │ │
│ │ │ Style                         │   │ │ Memory List                 │ │ │
│ │ │ Label: 14px bold | #9CA3AF    │   │ │ Max-height: 300px           │ │ │
│ │ │                               │   │ │ Overflow-y: auto            │ │ │
│ │ │ [Coach ▼]                     │   │ │                             │ │ │
│ │ │ Select: w-full | bg-#1F2937   │   │ │ ✓ Prefers morning deep work │ │ │
│ │ │ Border: #374151 | py-2 px-3   │   │ │ ✓ Career pillar priority    │ │ │
│ │ └───────────────────────────────┘   │ │ ✓ 2-hour focus blocks best  │ │ │
│ │                                     │ │ ✓ Dislikes meetings < 30min │ │ │
│ │ Tone (margin-top: 24px)             │ │                             │ │ │
│ │ ┌───────────────────────────────┐   │ │ Each item: py-2 | border-b  │ │ │
│ │ │ ○ Encouraging                 │   │ │ Check: #10B981 | Text: #D1D5│ │ │
│ │ │ ● Direct                      │   │ └─────────────────────────────┘ │ │
│ │ │ ○ Analytical                  │   │                                 │ │
│ │ │                               │   │ ┌─────────────────────────────┐ │ │
│ │ │ Radio: custom | Label: flex   │   │ │ + Add memory...             │ │ │
│ │ │ Gap: 8px | py-2               │   │ │ Button: w-full | py-2       │ │ │
│ │ │ Selected: text-#F59E0B        │   │ │ Border: dashed #374151      │ │ │
│ │ └───────────────────────────────┘   │ │ Hover: border-#F59E0B       │ │ │
│ │                                     │ └─────────────────────────────┘ │ │
│ │ Communication Level                 │                                 │ │
│ │ ┌───────────────────────────────┐   │ ┌─────────────────────────────┐ │ │
│ │ │ Minimal ░░░░█████░░░ Detailed │   │ │ [Export] [Clear All]        │ │ │
│ │ │ Slider: w-full | accent-#F59E0B│   │ │ Buttons: text-sm            │ │ │
│ │ └───────────────────────────────┘   │ └─────────────────────────────┘ │ │
│ └─────────────────────────────────────┴─────────────────────────────────┘ │
│                                                                            │
│ Reasoning Preferences (Full width | Margin-top: 24px)                      │
│ ┌────────────────────────────────────────────────────────────────────────┐ │
│ │ Background: #111827 | Border: #374151 | Padding: 24px | Radius: 12px    │ │
│ │                                                                          │ │
│ │ Grid: 2 columns | Gap: 24px                                              │ │
│ │ ┌──────────────────────────────┬──────────────────────────────┐        │ │
│ │ │ Show confidence scores       │ Explanation detail           │        │ │
│ │ │ [On ▼]                       │ [Balanced ▼]                 │        │ │
│ │ ├──────────────────────────────┼──────────────────────────────┤        │ │
│ │ │ Proactive suggestions        │ Learning from feedback       │        │ │
│ │ │ [Smart ▼]                    │ [On ▼]                       │        │ │
│ │ └──────────────────────────────┴──────────────────────────────┘        │ │
│ │                                                                          │ │
│ │ Each setting: Label (14px #9CA3AF) + Select (same style as above)       │ │
│ └────────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Visual Life Map

```
┌────────────────────────────────────────────────────────────────────────────┐
│ Background: #0B0D14 | Height: calc(100vh - header) | Overflow: hidden      │
│                                                                            │
│ ┌────────────────────────────────────────────────────────────────────────┐ │
│ │ Header Bar                                                               │ │
│ │ Background: #111827 | Border-bottom: #374151 | Padding: 16px            │ │
│ │ ┌──────────────────────────────────┬──────────────────────────────┐   │ │
│ │ │ 🗺️ Your Life Map                 │ [Zoom] [Filter] [Export]     │   │ │
│ │ │ Font: 20px bold | Color: white   │ Buttons: px-3 py-1.5         │   │ │
│ │ └──────────────────────────────────┴──────────────────────────────┘   │ │
│ └────────────────────────────────────────────────────────────────────────┘ │
│                                                                            │
│ Canvas Area (Position: relative | Overflow: auto)                          │
│ ┌────────────────────────────────────────────────────────────────────────┐ │
│ │ SVG Canvas: Width: 100% | Height: 100% | Background: #0B0D14           │ │
│ │                                                                          │ │
│ │     Career 🎯                          Health 💪                        │ │
│ │     ┌──────────────┐                  ┌──────────────┐                 │ │
│ │     │ Rect: #1F2937│                  │ Rect: #1F2937│                 │ │
│ │     │ Border: 2px  │                  │ Border: 2px  │                 │ │
│ │     │ #F59E0B      │                  │ #10B981      │                 │ │
│ │     │ Radius: 12px │                  │ Radius: 12px │                 │ │
│ │     │ Padding: 16px│                  │ Padding: 16px│                 │ │
│ │     │              │                  │              │                 │ │
│ │     │ Career (40%) │                  │ Health (30%) │                 │ │
│ │     └──────┬───────┘                  └──────┬───────┘                 │ │
│ │            │ Line: stroke-#374151             │                         │ │
│ │            │ stroke-width: 2                  │                         │ │
│ │      ┌─────┴─────┐                     ┌─────┴─────┐                   │ │
│ │      │ Product   │                     │ Fitness   │                   │ │
│ │      │ Leader    │                     │           │                   │ │
│ │      └─────┬─────┘                     └─────┬─────┘                   │ │
│ │            │                                  │                         │ │
│ │     ┌──────┴──────┐                  ┌───────┴──────┐                  │ │
│ │     │ MVP Launch  │                  │ Marathon Prep│                  │ │
│ │     │ ⚠️ At Risk  │                  │ ✅ On Track  │                  │ │
│ │     │ Bg: #EF4444 │                  │ Bg: #10B981  │                  │ │
│ │     │ Bg-opacity: │                  │ Bg-opacity:  │                  │ │
│ │     │ 0.1         │                  │ 0.1          │                  │ │
│ │     └──────┬──────┘                  └──────┬───────┘                  │ │
│ │            │                                 │                          │ │
│ │      [5 tasks]                         [8 tasks]                       │ │
│ │      3 blocked                         2 due today                      │ │
│ │      Font: 12px                        Font: 12px                       │ │
│ │      Color: #9CA3AF                    Color: #9CA3AF                   │ │
│ │                                                                          │ │
│ │ Node styling:                                                            │ │
│ │ - Hover: transform scale(1.05) | transition: 200ms                       │ │
│ │ - Click: Shows detail panel                                              │ │
│ │ - Drag: Reorganize structure                                             │ │
│ └────────────────────────────────────────────────────────────────────────┘ │
│                                                                            │
│ AI Insights Panel (Position: fixed | Bottom: 24px | Right: 24px)          │
│ ┌────────────────────────────────────────────────────────────────────────┐ │
│ │ Background: #111827 | Border: #3B82F6 | Padding: 16px | Radius: 12px    │ │
│ │ Max-width: 400px | Box-shadow: 0 10px 15px rgba(0,0,0,0.3)             │ │
│ │                                                                          │ │
│ │ AI Insights:                                                             │ │
│ │ • Career pillar consuming 55% time (target: 40%)                        │ │
│ │ • Health goals may suffer without rebalancing                           │ │
│ │                                                                          │ │
│ │ Font: 14px | Color: #D1D5DB | Line-height: 1.5                          │ │
│ │ Bullet: #3B82F6                                                          │ │
│ └────────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Weekly Review Dashboard

```
┌────────────────────────────────────────────────────────────────────────────┐
│ Background: #0B0D14 | Padding: 32px                                        │
│                                                                            │
│ ┌────────────────────────────────────────────────────────────────────────┐ │
│ │ Header Section                                                           │ │
│ │ ┌──────────────────────────────────────────────────────────────────┐   │ │
│ │ │ 📊 Weekly Review - Week 45                                        │   │ │
│ │ │ Font: 28px bold | Color: white | Icon: 32px                      │   │ │
│ │ │ Margin-bottom: 32px                                               │   │ │
│ │ └──────────────────────────────────────────────────────────────────┘   │ │
│ └────────────────────────────────────────────────────────────────────────┘ │
│                                                                            │
│ Week Stats (Grid: 3 columns | Gap: 24px)                                   │
│ ┌──────────────────────┬──────────────────────┬──────────────────────┐   │
│ │ Background: #111827  │ Background: #111827  │ Background: #111827  │   │
│ │ Border: #374151      │ Border: #374151      │ Border: #374151      │   │
│ │ Padding: 24px        │ Padding: 24px        │ Padding: 24px        │   │
│ │                      │                      │                      │   │
│ │ Tasks Completed      │ On Schedule          │ Deep Work            │   │
│ │ 24/28               │ 85%                  │ +2 hrs               │   │
│ │ Font: 32px bold      │ Font: 32px bold      │ Font: 32px bold      │   │
│ │ Color: #10B981       │ Color: #3B82F6       │ Color: #F59E0B       │   │
│ │                      │                      │                      │   │
│ │ Label: 14px #9CA3AF  │ Label: 14px #9CA3AF  │ Label: 14px #9CA3AF  │   │
│ └──────────────────────┴──────────────────────┴──────────────────────┘   │
│                                                                            │
│ AI Analysis Section (Margin-top: 32px)                                     │
│ ┌────────────────────────────────────────────────────────────────────────┐ │
│ │ Background: #111827 | Border: #3B82F6 | Padding: 24px | Radius: 12px    │ │
│ │                                                                          │ │
│ │ AI Analysis:                                                             │ │
│ │ Font: 16px medium | Color: white | Margin-bottom: 16px                  │ │
│ │                                                                          │ │
│ │ ✅ Strong week for Career pillar (90% completion)                       │ │
│ │ ⚠️ Health pillar neglected (only 1 workout)                            │ │
│ │ 💡 Tuesday/Thursday were your most productive days                      │ │
│ │                                                                          │ │
│ │ Each item: py-2 | Icon: 20px | Text: 14px | Color: #D1D5DB             │ │
│ └────────────────────────────────────────────────────────────────────────┘ │
│                                                                            │
│ Reflection Section (Grid: 2 columns | Gap: 24px | Margin-top: 32px)        │
│ ┌────────────────────────────────────────────────────────────────────────┐ │
│ │ Left Column                          │ Right Column                     │ │
│ │ Background: #111827                  │ Background: #111827              │ │
│ │ Border: #374151 | Padding: 24px      │ Border: #374151 | Padding: 24px  │ │
│ │                                      │                                  │ │
│ │ Reflection Prompts                   │ Next Week Preview                │ │
│ │ Font: 16px medium | Color: white     │ Font: 16px medium | Color: white │ │
│ │                                      │                                  │ │
│ │ 1. What was your biggest win?       │ • 3 critical deadlines           │ │
│ │ ┌──────────────────────────────┐    │ • MVP documentation focus        │ │
│ │ │ Textarea: w-full | h-20      │    │ • Block 2 mornings for deep work │ │
│ │ │ Bg: #1F2937 | Border: #374151│    │                                  │ │
│ │ │ Padding: 12px | Radius: 8px  │    │ Each item: py-2 | bullet: #F59E0B│ │
│ │ └──────────────────────────────┘    │ Text: 14px | Color: #D1D5DB      │ │
│ │                                      │                                  │ │
│ │ 2. What held you back?              │ ┌────────────────────────────┐   │ │
│ │ ┌──────────────────────────────┐    │ │ [Plan Next Week]           │   │ │
│ │ │ Textarea (same style)        │    │ │ Button: w-full | py-3      │   │ │
│ │ └──────────────────────────────┘    │ │ Bg: gradient #F59E0B       │   │ │
│ │                                      │ │ to #D97706                 │   │ │
│ │ 3. Energy levels this week?         │ │ Font: 16px medium          │   │ │
│ │ [Low] [Medium] [High]                │ │ Text: black                │   │ │
│ │ Button group (same as energy check)  │ └────────────────────────────┘   │ │
│ └────────────────────────────────────────────────────────────────────────┘ │
│                                                                            │
│ Action Buttons (Margin-top: 32px | Display: flex | Justify: center)        │
│ ┌────────────────────────────────────────────────────────────────────────┐ │
│ │ [Complete Review]     [Skip]                                            │ │
│ │ Primary button        Secondary button                                  │ │
│ │ px-8 py-3            px-8 py-3                                          │ │
│ └────────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Design System Summary

### Colors
- **Primary**: `#F59E0B` (yellow-500), `#D97706` (yellow-600)
- **AI Accent**: `#3B82F6` (blue-500)
- **Success**: `#10B981` (green-500)
- **Warning**: `#EF4444` (red-500)
- **Background**: `#0B0D14` (main), `#111827` (gray-900), `#1F2937` (gray-800)
- **Borders**: `#374151` (gray-700)
- **Text**: `#FFFFFF` (white), `#D1D5DB` (gray-300), `#9CA3AF` (gray-400)

### Typography
- **Headings**: 28px-32px bold
- **Subheadings**: 20px-24px bold
- **Body**: 14px-16px regular
- **Small**: 12px-14px
- **Monospace**: For time displays

### Spacing
- **Container padding**: 24px-32px
- **Card padding**: 16px-24px
- **Element spacing**: 8px-16px gaps
- **Section margins**: 24px-32px

### Components
- **Cards**: Background #111827/#1F2937, Border #374151, Radius 12px
- **Buttons**: Primary (gradient yellow), Secondary (border only)
- **Inputs**: Background #1F2937, Border #374151, Focus border #F59E0B
- **AI Elements**: Border/accent #3B82F6

This design system maintains consistency with Aurum Life's existing dark theme and yellow accent colors while introducing blue as the AI indicator color.