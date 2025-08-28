# Aurum Life Mobile Wireframes - Enhanced AI Architecture

## Design System Constants (Mobile)
- **Background**: `#0B0D14` (Main), `#111827` (gray-900), `#1F2937` (gray-800)
- **Primary**: `#F59E0B` (yellow-500), `#D97706` (yellow-600)
- **Text**: `#FFFFFF` (white), `#D1D5DB` (gray-300), `#9CA3AF` (gray-400)
- **AI Accent**: `#3B82F6` (blue-500)
- **Safe Areas**: Top/Bottom device safe areas respected
- **Touch Targets**: Minimum 44px height

---

## 1. AI Command Center (Mobile)

```
┌─────────────────────────────────────┐
│ Status Bar (System)                 │
├─────────────────────────────────────┤
│ Background: #0B0D14                 │
│ Safe-area-top: env()                │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ Modal Overlay                   │ │
│ │ Background: rgba(0,0,0,0.7)     │ │
│ │                                 │ │
│ │ ┌─────────────────────────────┐ │ │
│ │ │ Bottom Sheet                 │ │ │
│ │ │ Bg: #111827                  │ │ │
│ │ │ Border-top-radius: 24px      │ │ │
│ │ │ Padding: 20px                │ │ │
│ │ │                              │ │ │
│ │ │ ┌───────────────────────┐   │ │ │
│ │ │ │ Handle Bar            │   │ │ │
│ │ │ │ Width: 48px           │   │ │ │
│ │ │ │ Height: 4px           │   │ │ │
│ │ │ │ Bg: #374151           │   │ │ │
│ │ │ │ Margin: 0 auto 16px   │   │ │ │
│ │ │ └───────────────────────┘   │ │ │
│ │ │                              │ │ │
│ │ │ Search Bar                   │ │ │
│ │ │ ┌───────────────────────┐   │ │ │
│ │ │ │ 🎤  Ask AI...    📷  │   │ │ │
│ │ │ │ Height: 48px         │   │ │ │
│ │ │ │ Bg: #1F2937          │   │ │ │
│ │ │ │ Border: #374151       │   │ │ │
│ │ │ │ Border-radius: 12px   │   │ │ │
│ │ │ │ Padding: 0 16px       │   │ │ │
│ │ │ │ Font: 16px            │   │ │ │
│ │ │ └───────────────────────┘   │ │ │
│ │ │                              │ │ │
│ │ │ Quick Actions (Grid: 2x2)    │ │ │
│ │ │ Margin-top: 20px             │ │ │
│ │ │ Gap: 12px                    │ │ │
│ │ │                              │ │ │
│ │ │ ┌─────────┐ ┌─────────┐     │ │ │
│ │ │ │ Add     │ │ Find    │     │ │ │
│ │ │ │ Task    │ │ Task    │     │ │ │
│ │ │ │ Height: │ │ Height: │     │ │ │
│ │ │ │ 80px    │ │ 80px    │     │ │ │
│ │ │ └─────────┘ └─────────┘     │ │ │
│ │ │ ┌─────────┐ ┌─────────┐     │ │ │
│ │ │ │ Plan    │ │ What's  │     │ │ │
│ │ │ │ Day     │ │ Next    │     │ │ │
│ │ │ └─────────┘ └─────────┘     │ │ │
│ │ │                              │ │ │
│ │ │ Button Style:                │ │ │
│ │ │ - Bg: #1F2937                │ │ │
│ │ │ - Border: #374151            │ │ │
│ │ │ - Border-radius: 12px        │ │ │
│ │ │ - Icon: 24px, #F59E0B        │ │ │
│ │ │ - Text: 12px, #D1D5DB        │ │ │
│ │ │                              │ │ │
│ │ │ Recent Commands              │ │ │
│ │ │ ┌───────────────────────┐   │ │ │
│ │ │ │ Label: uppercase 12px │   │ │ │
│ │ │ │ Color: #9CA3AF        │   │ │ │
│ │ │ │ Margin-top: 24px      │   │ │ │
│ │ │ └───────────────────────┘   │ │ │
│ │ │                              │ │ │
│ │ │ • "Add grocery task"         │ │ │
│ │ │ • "Show today's plan"        │ │ │
│ │ │                              │ │ │
│ │ │ Each: py-3 | border-b        │ │ │
│ │ │ Color: #D1D5DB | Font: 14px  │ │ │
│ │ └─────────────────────────────┘ │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

---

## 2. AI Insights Dashboard (Mobile)

```
┌─────────────────────────────────────┐
│ Status Bar                          │
├─────────────────────────────────────┤
│ Header                              │
│ ┌─────────────────────────────────┐ │
│ │ Bg: #111827 | Height: 56px      │ │
│ │ Padding: 0 16px                  │ │
│ │ Border-bottom: #374151           │ │
│ │                                 │ │
│ │ AI Insights            [⚙️]     │ │
│ │ Font: 18px bold                 │ │
│ │ Color: white                    │ │
│ └─────────────────────────────────┘ │
│                                     │
│ Scrollable Content                  │
│ Background: #0B0D14                 │
│ Padding: 16px                       │
│                                     │
│ Stats Row (Horizontal scroll)       │
│ ┌─────────────────────────────────┐ │
│ │ Display: flex | Gap: 12px        │ │
│ │ Overflow-x: auto                 │ │
│ │ Padding-bottom: 12px             │ │
│ │                                 │ │
│ │ ┌─────────┐ ┌─────────┐ ┌─────┐│ │
│ │ │ 87%     │ │ 156     │ │ +12%││ │
│ │ │ Confid. │ │ Insights│ │ Learn││ │
│ │ │ Min-w:  │ │ Min-w:  │ │      ││ │
│ │ │ 100px   │ │ 100px   │ │      ││ │
│ │ └─────────┘ └─────────┘ └─────┘│ │
│ │                                 │ │
│ │ Card Style:                     │ │
│ │ - Bg: #1F2937                   │ │
│ │ - Border: #374151               │ │
│ │ - Padding: 16px                 │ │
│ │ - Border-radius: 12px           │ │
│ │ - Value: 24px bold              │ │
│ │ - Label: 11px #9CA3AF           │ │
│ └─────────────────────────────────┘ │
│                                     │
│ Filter Pills (Horizontal scroll)    │
│ ┌─────────────────────────────────┐ │
│ │ Display: flex | Gap: 8px         │ │
│ │ Overflow-x: auto                 │ │
│ │ Margin: 16px 0                   │ │
│ │                                 │ │
│ │ [All] [Priority] [Alignment] [..]│ │
│ │                                 │ │
│ │ Pill Style:                     │ │
│ │ - Padding: 6px 12px             │ │
│ │ - Font: 14px                    │ │
│ │ - Border-radius: 20px           │ │
│ │ - Active: bg-#F59E0B text-black │ │
│ │ - Inactive: border-#374151      │ │
│ └─────────────────────────────────┘ │
│                                     │
│ Insight Cards (Vertical list)       │
│ ┌─────────────────────────────────┐ │
│ │ Card 1                          │ │
│ │ Bg: #1F2937 | Border: #374151   │ │
│ │ Padding: 16px | Radius: 12px    │ │
│ │ Margin-bottom: 12px             │ │
│ │                                 │ │
│ │ ┌───────────────────────────┐   │ │
│ │ │ 🎯 Project Risk      87%  │   │ │
│ │ │ Icon: 20px                │   │ │
│ │ │ Title: 14px bold          │   │ │
│ │ │ Confidence: 12px #10B981  │   │ │
│ │ ├───────────────────────────┤   │ │
│ │ │ MVP is blocked by 3 tasks │   │ │
│ │ │ Font: 13px | Color: #D1D5 │   │ │
│ │ │ Line-height: 1.4          │   │ │
│ │ ├───────────────────────────┤   │ │
│ │ │ [→ View] [✓ Act] 👍 👎   │   │ │
│ │ │ Buttons: py-1 px-3        │   │ │
│ │ │ Font: 12px                │   │ │
│ │ │ Display: flex | Gap: 8px  │   │ │
│ │ └───────────────────────────┘   │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ Card 2 (Same structure)         │ │
│ │ 🔄 Pattern Found                │ │
│ │ Tue-Thu mornings are peak       │ │
│ │ [Apply] [More] 👍 👎            │ │
│ └─────────────────────────────────┘ │
│                                     │
│ Bottom safe area padding            │
└─────────────────────────────────────┘
```

---

## 3. Quick Capture (Mobile)

```
┌─────────────────────────────────────┐
│ Status Bar                          │
├─────────────────────────────────────┤
│ Header                              │
│ ┌─────────────────────────────────┐ │
│ │ Bg: #111827 | Height: 56px      │ │
│ │                                 │ │
│ │ [Cancel]  Quick Add    [Save]   │ │
│ │ Buttons: text-#F59E0B            │ │
│ │ Title: 16px bold white          │ │
│ └─────────────────────────────────┘ │
│                                     │
│ Content (Padding: 20px)             │
│ Background: #0B0D14                 │
│                                     │
│ Voice Input Section                 │
│ ┌─────────────────────────────────┐ │
│ │ ┌─────────────────────────────┐ │ │
│ │ │       🎤                     │ │ │
│ │ │   Hold to speak...           │ │ │
│ │ │                              │ │ │
│ │ │ Button: Height 120px         │ │ │
│ │ │ Bg: #1F2937                  │ │ │
│ │ │ Border: 2px dashed #374151   │ │ │
│ │ │ Border-radius: 16px          │ │ │
│ │ │ Icon: 40px #F59E0B           │ │ │
│ │ │ Text: 14px #9CA3AF           │ │ │
│ │ │                              │ │ │
│ │ │ Active state:                │ │ │
│ │ │ - Border: solid #F59E0B      │ │ │
│ │ │ - Bg: #F59E0B/10             │ │ │
│ │ │ - Animation: pulse           │ │ │
│ │ └─────────────────────────────┘ │ │
│ └─────────────────────────────────┘ │
│                                     │
│ OR type (Margin: 20px 0)            │
│ ┌─────────────────────────────────┐ │
│ │ Text: center | Color: #9CA3AF   │ │
│ └─────────────────────────────────┘ │
│                                     │
│ Text Input                          │
│ ┌─────────────────────────────────┐ │
│ │ [What needs to be done?...]     │ │
│ │ Input: Height 48px              │ │
│ │ Bg: #1F2937 | Border: #374151   │ │
│ │ Padding: 0 16px                 │ │
│ │ Font: 16px | Color: white       │ │
│ │ Placeholder: #9CA3AF            │ │
│ └─────────────────────────────────┘ │
│                                     │
│ Capture Type (Margin-top: 24px)     │
│ ┌─────────────────────────────────┐ │
│ │ Capture as:                     │ │
│ │ Label: 14px #9CA3AF | mb-12px   │ │
│ │                                 │ │
│ │ ┌───────┐ ┌───────┐ ┌───────┐ │ │
│ │ │ Task  │ │ Idea  │ │ Note  │ │ │
│ │ │ ✓     │ │       │ │       │ │ │
│ │ └───────┘ └───────┘ └───────┘ │ │
│ │                                 │ │
│ │ Button Style:                   │ │
│ │ - Height: 44px | Flex: 1        │ │
│ │ - Border: 1px #374151           │ │
│ │ - Selected: bg-#F59E0B/20       │ │
│ │ - Selected: border-#F59E0B      │ │
│ └─────────────────────────────────┘ │
│                                     │
│ AI Suggestions                      │
│ ┌─────────────────────────────────┐ │
│ │ Bg: #1F2937/50 | Padding: 16px  │ │
│ │ Border: 1px #3B82F6             │ │
│ │ Border-radius: 12px             │ │
│ │                                 │ │
│ │ 🤖 AI Suggests:                 │ │
│ │ Icon: 16px | Label: 12px bold   │ │
│ │                                 │ │
│ │ Project: [Current Project ▼]    │ │
│ │ Priority: [Medium ▼]            │ │
│ │ Due: [Tomorrow ▼]               │ │
│ │                                 │ │
│ │ Select Style:                   │ │
│ │ - Height: 36px | Width: 100%    │ │
│ │ - Bg: #111827 | Border: #374151 │ │
│ │ - Margin-top: 8px               │ │
│ └─────────────────────────────────┘ │
│                                     │
│ Add Photo Button                    │
│ ┌─────────────────────────────────┐ │
│ │ [📷 Add Photo]                  │ │
│ │ Button: Width 100% | Height 44px│ │
│ │ Border: 1px dashed #374151      │ │
│ │ Margin-top: 20px                │ │
│ └─────────────────────────────────┘ │
│                                     │
│ Action Buttons (Fixed bottom)       │
│ ┌─────────────────────────────────┐ │
│ │ Padding: 20px | Bg: #111827     │ │
│ │ Border-top: #374151             │ │
│ │                                 │ │
│ │ [Save & Add Another]            │ │
│ │ [Save & Close]                  │ │
│ │                                 │ │
│ │ Buttons: Width 100% | Height 48 │ │
│ │ Primary: bg-gradient #F59E0B    │ │
│ │ Secondary: border only          │ │
│ │ Margin-top: 12px                │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

---

## 4. Focus Mode (Mobile)

```
┌─────────────────────────────────────┐
│ Background: #0B0D14                 │
│ Height: 100vh                       │
│                                     │
│ Close Button (Top-right)            │
│ ┌─────────────────────────────────┐ │
│ │ [✕]                             │ │
│ │ Position: absolute              │ │
│ │ Top: safe-area + 16px           │ │
│ │ Right: 16px                     │ │
│ │ Size: 44x44px                   │ │
│ │ Color: #9CA3AF                  │ │
│ └─────────────────────────────────┘ │
│                                     │
│ Timer Section (Center)              │
│ ┌─────────────────────────────────┐ │
│ │ Display: flex                   │ │
│ │ Flex-direction: column          │ │
│ │ Align-items: center             │ │
│ │ Justify-content: center         │ │
│ │ Height: 100%                    │ │
│ │ Padding: 32px                   │ │
│ │                                 │ │
│ │ ┌─────────────────────────────┐ │ │
│ │ │     ⏱️ 01:23:45             │ │ │
│ │ │ Font: 48px | Font-weight: 200│ │ │
│ │ │ Font-family: SF Mono         │ │ │
│ │ │ Color: white                 │ │ │
│ │ │ Text-align: center           │ │ │
│ │ └─────────────────────────────┘ │ │
│ │                                 │ │
│ │ Progress Ring                   │ │
│ │ ┌─────────────────────────────┐ │ │
│ │ │ SVG: 200x200px               │ │ │
│ │ │ Margin: 32px 0               │ │ │
│ │ │                              │ │ │
│ │ │   ┌─────────────────┐        │ │ │
│ │ │   │                 │        │ │ │
│ │ │   │  ████████████   │        │ │ │
│ │ │   │  ░░░░░░░░░░░░   │        │ │ │
│ │ │   │                 │        │ │ │
│ │ │   └─────────────────┘        │ │ │
│ │ │                              │ │ │
│ │ │ Track: stroke-#374151        │ │ │
│ │ │ Fill: stroke-#F59E0B         │ │ │
│ │ │ Stroke-width: 8px            │ │ │
│ │ └─────────────────────────────┘ │ │
│ │                                 │ │
│ │ Task Info                      │ │
│ │ ┌─────────────────────────────┐ │ │
│ │ │ Write Product                │ │ │
│ │ │ Requirements Doc             │ │ │
│ │ │                              │ │ │
│ │ │ Font: 20px bold             │ │ │
│ │ │ Color: white                │ │ │
│ │ │ Text-align: center          │ │ │
│ │ │ Line-height: 1.3            │ │ │
│ │ │                              │ │ │
│ │ │ MVP Launch                   │ │ │
│ │ │ Font: 14px | Color: #9CA3AF │ │ │
│ │ │ Margin-top: 8px             │ │ │
│ │ └─────────────────────────────┘ │ │
│ └─────────────────────────────────┘ │
│                                     │
│ AI Coach Message                    │
│ ┌─────────────────────────────────┐ │
│ │ Position: absolute              │ │
│ │ Bottom: safe-area + 120px       │ │
│ │ Left: 20px | Right: 20px        │ │
│ │                                 │ │
│ │ Bg: #1F2937 | Border: #3B82F6  │ │
│ │ Padding: 16px | Radius: 12px   │ │
│ │                                 │ │
│ │ 🤖 On track! Last time         │ │
│ │    this took 1h 45m             │ │
│ │                                 │ │
│ │ Icon: 16px | Text: 13px        │ │
│ │ Color: #D1D5DB                  │ │
│ └─────────────────────────────────┘ │
│                                     │
│ Control Buttons (Fixed bottom)      │
│ ┌─────────────────────────────────┐ │
│ │ Position: fixed                 │ │
│ │ Bottom: safe-area + 20px        │ │
│ │ Left: 20px | Right: 20px        │ │
│ │                                 │ │
│ │ ┌───────┐ ┌───────┐ ┌───────┐ │ │
│ │ │  ⏸️   │ │  ✓    │ │  ❌   │ │ │
│ │ │ Pause │ │ Done  │ │ Exit  │ │ │
│ │ └───────┘ └───────┘ └───────┘ │ │
│ │                                 │ │
│ │ Button Style:                   │ │
│ │ - Height: 56px | Flex: 1        │ │
│ │ - Bg: #1F2937 | Border: #374151 │ │
│ │ - Icon: 24px | Text: 12px       │ │
│ │ - Display: flex-col | Gap: 4px  │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

---

## 5. Daily Planning Ritual (Mobile)

```
┌─────────────────────────────────────┐
│ Status Bar                          │
├─────────────────────────────────────┤
│ Header                              │
│ ┌─────────────────────────────────┐ │
│ │ ☀️ Good Morning!                │ │
│ │ Font: 20px bold | Color: white  │ │
│ │ Icon: 24px                      │ │
│ │ Padding: 20px                   │ │
│ │ Text-align: center              │ │
│ │ Bg: #111827                     │ │
│ └─────────────────────────────────┘ │
│                                     │
│ Scrollable Content                  │
│ Background: #0B0D14                 │
│ Padding: 20px                       │
│                                     │
│ Energy Check                        │
│ ┌─────────────────────────────────┐ │
│ │ Energy today?                   │ │
│ │ Label: 16px bold white | mb-16  │ │
│ │                                 │ │
│ │ ┌─────────┐ ┌─────────┐        │ │
│ │ │   😴    │ │   😐    │        │ │
│ │ │   Low   │ │  Medium │        │ │
│ │ └─────────┘ └─────────┘        │ │
│ │ ┌─────────┐ ┌─────────┐        │ │
│ │ │   😊    │ │   🚀    │        │ │
│ │ │  High   │ │  Peak   │        │ │
│ │ └─────────┘ └─────────┘        │ │
│ │                                 │ │
│ │ Grid: 2x2 | Gap: 12px           │ │
│ │ Button Style:                   │ │
│ │ - Height: 80px                  │ │
│ │ - Bg: #1F2937                   │ │
│ │ - Border: 1px #374151           │ │
│ │ - Border-radius: 12px           │ │
│ │ - Selected: border-#F59E0B      │ │
│ │ - Selected: bg-#F59E0B/20       │ │
│ │ - Icon: 32px | Text: 13px       │ │
│ └─────────────────────────────────┘ │
│                                     │
│ Your Schedule (Margin-top: 32px)    │
│ ┌─────────────────────────────────┐ │
│ │ Your optimal schedule:          │ │
│ │ Label: 16px bold white | mb-16  │ │
│ │                                 │ │
│ │ ┌─────────────────────────────┐ │ │
│ │ │ Time Block 1                 │ │ │
│ │ │ Bg: #1F2937 | Border: #374151│ │ │
│ │ │ Padding: 16px | Radius: 12px │ │ │
│ │ │ Margin-bottom: 12px          │ │ │
│ │ │                              │ │ │
│ │ │ 9:00 AM - Write PRD 🎯      │ │ │
│ │ │ Time: font-mono 14px bold    │ │ │
│ │ │ Task: 16px white             │ │ │
│ │ │ Icon: 20px                   │ │ │
│ │ │                              │ │ │
│ │ │ ↳ Deep work window           │ │ │
│ │ │ Reason: 13px #9CA3AF         │ │ │
│ │ │ Margin-left: 20px            │ │ │
│ │ └─────────────────────────────┘ │ │
│ │                                 │ │
│ │ ┌─────────────────────────────┐ │ │
│ │ │ 11:00 AM - Emails 📧        │ │ │
│ │ │ ↳ Low energy task           │ │ │
│ │ └─────────────────────────────┘ │ │
│ │                                 │ │
│ │ ┌─────────────────────────────┐ │ │
│ │ │ 2:00 PM - Team Review 🤝    │ │ │
│ │ │ ↳ Collaboration time        │ │ │
│ │ └─────────────────────────────┘ │ │
│ └─────────────────────────────────┘ │
│                                     │
│ Action Buttons (Fixed bottom)       │
│ ┌─────────────────────────────────┐ │
│ │ Bg: #111827 | Padding: 20px     │ │
│ │ Border-top: #374151             │ │
│ │                                 │ │
│ │ [Adjust]                        │ │
│ │ Button: Width 100% | Height 48  │ │
│ │ Border: 1px #374151             │ │
│ │ Margin-bottom: 12px             │ │
│ │                                 │ │
│ │ [Start Day]                     │ │
│ │ Button: Width 100% | Height 48  │ │
│ │ Bg: gradient #F59E0B to #D97706 │ │
│ │ Font: 16px bold | Color: black  │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

---

## 6. AI Memory & Preferences (Mobile)

```
┌─────────────────────────────────────┐
│ Status Bar                          │
├─────────────────────────────────────┤
│ Header                              │
│ ┌─────────────────────────────────┐ │
│ │ [<] AI Settings                 │ │
│ │ Back: 44x44px touch target      │ │
│ │ Title: 18px bold white          │ │
│ └─────────────────────────────────┘ │
│                                     │
│ Scrollable Content                  │
│ Background: #0B0D14                 │
│                                     │
│ Personality Section                 │
│ ┌─────────────────────────────────┐ │
│ │ Section: Padding 20px           │ │
│ │                                 │ │
│ │ Personality                     │ │
│ │ Label: 14px bold #9CA3AF        │ │
│ │ Margin-bottom: 12px             │ │
│ │                                 │ │
│ │ [Coach ▼]                       │ │
│ │ Select: Width 100% | Height 48  │ │
│ │ Bg: #1F2937 | Border: #374151   │ │
│ │ Padding: 0 16px                 │ │
│ │ Border-radius: 8px              │ │
│ │                                 │ │
│ │ ○ Encouraging                   │ │
│ │ ● Direct                        │ │
│ │ ○ Analytical                    │ │
│ │                                 │ │
│ │ Radio list: Margin-top: 16px    │ │
│ │ Each item: py-12px              │ │
│ │ Radio: 20px | Label: 16px       │ │
│ │ Selected: text-#F59E0B          │ │
│ └─────────────────────────────────┘ │
│                                     │
│ Divider: Height 1px | Bg: #374151   │
│                                     │
│ AI Memories Section                 │
│ ┌─────────────────────────────────┐ │
│ │ Section: Padding 20px           │ │
│ │                                 │ │
│ │ AI Memories                     │ │
│ │ Label: 14px bold #9CA3AF | mb-12│ │
│ │                                 │ │
│ │ ┌─────────────────────────────┐ │ │
│ │ │ Memory List                  │ │ │
│ │ │ Bg: #1F2937 | Border: #374151│ │ │
│ │ │ Border-radius: 12px          │ │ │
│ │ │ Padding: 12px                │ │ │
│ │ │                              │ │ │
│ │ │ ✓ Morning deep work          │ │ │
│ │ │ ✓ Career priority            │ │ │
│ │ │ ✓ 2-hour blocks              │ │ │
│ │ │                              │ │ │
│ │ │ Each: py-8px | Font: 14px    │ │ │
│ │ │ Check: 16px #10B981          │ │ │
│ │ │ Text: #D1D5DB                │ │ │
│ │ │                              │ │ │
│ │ │ [+ Add]                      │ │ │
│ │ │ Button: py-8px | Width 100%  │ │ │
│ │ │ Border-top: 1px #374151      │ │ │
│ │ │ Text: #F59E0B                │ │ │
│ │ └─────────────────────────────┘ │ │
│ └─────────────────────────────────┘ │
│                                     │
│ Preferences Section                 │
│ ┌─────────────────────────────────┐ │
│ │ Section: Padding 20px           │ │
│ │                                 │ │
│ │ Preferences                     │ │
│ │ Label: 14px bold #9CA3AF | mb-16│ │
│ │                                 │ │
│ │ Confidence: [On ▼]              │ │
│ │ Row: Label + Select             │ │
│ │ Label: 16px white               │ │
│ │ Select: same style as above     │ │
│ │                                 │ │
│ │ Details: [Balanced ▼]           │ │
│ │ Margin-top: 16px                │ │
│ │                                 │ │
│ │ Learning: [On ▼]                │ │
│ │ Margin-top: 16px                │ │
│ └─────────────────────────────────┘ │
│                                     │
│ Bottom padding for safe area        │
└─────────────────────────────────────┘
```

---

## 7. Visual Life Map (Mobile)

```
┌─────────────────────────────────────┐
│ Status Bar                          │
├─────────────────────────────────────┤
│ Header                              │
│ ┌─────────────────────────────────┐ │
│ │ Life Map                  [≡]   │ │
│ │ Title: 18px bold white          │ │
│ │ Menu: 44x44px touch target      │ │
│ └─────────────────────────────────┘ │
│                                     │
│ Tree View (Vertical)                │
│ Background: #0B0D14                 │
│ Padding: 16px                       │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ Pillar 1                        │ │
│ │ ┌─────────────────────────────┐ │ │
│ │ │ Career 🎯 (40%)              │ │ │
│ │ │                              │ │ │
│ │ │ Container:                   │ │ │
│ │ │ - Bg: #1F2937                │ │ │
│ │ │ - Border: 2px #F59E0B        │ │ │
│ │ │ - Border-radius: 12px        │ │ │
│ │ │ - Padding: 16px              │ │ │
│ │ │ - Margin-bottom: 8px         │ │ │
│ │ │                              │ │ │
│ │ │ Title: 16px bold white       │ │ │
│ │ │ Icon: 20px                   │ │ │
│ │ │ Percentage: 14px #9CA3AF     │ │ │
│ │ └─────────────────────────────┘ │ │
│ │                                 │ │
│ │ └─ Product Leader               │ │
│ │    Area: Indent 16px            │ │
│ │    Font: 14px | Color: #D1D5DB  │ │
│ │    Padding: 12px 16px           │ │
│ │    Border-left: 2px #374151     │ │
│ │                                 │ │
│ │    └─ MVP Launch ⚠️             │ │
│ │       Project: Indent 32px      │ │
│ │       Bg: #EF4444/10            │ │
│ │       Border: 1px #EF4444       │ │
│ │       Padding: 12px             │ │
│ │       Border-radius: 8px        │ │
│ │       Margin: 8px 0             │ │
│ │                                 │ │
│ │       5 tasks, 3 blocked        │ │
│ │       Font: 12px #9CA3AF        │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ Pillar 2                        │ │
│ │ ┌─────────────────────────────┐ │ │
│ │ │ Health 💪 (30%)              │ │ │
│ │ │ Border: 2px #10B981          │ │ │
│ │ └─────────────────────────────┘ │ │
│ │                                 │ │
│ │ └─ Fitness                      │ │
│ │    └─ Marathon ✅               │ │
│ │       8 tasks                   │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ [+] Relationships (20%)         │ │
│ │ [+] Growth (10%)                │ │
│ │                                 │ │
│ │ Collapsed items:                │ │
│ │ - Display: flex                 │ │
│ │ - Align-items: center           │ │
│ │ - Padding: 16px                 │ │
│ │ - Bg: #1F2937                   │ │
│ │ - Border: 1px #374151           │ │
│ │ - Margin-bottom: 8px            │ │
│ └─────────────────────────────────┘ │
│                                     │
│ AI Warning (Fixed bottom)           │
│ ┌─────────────────────────────────┐ │
│ │ Position: fixed                 │ │
│ │ Bottom: safe-area + 20px        │ │
│ │ Left: 16px | Right: 16px        │ │
│ │                                 │ │
│ │ ⚠️ Time imbalance detected      │ │
│ │ [View Details]                  │ │
│ │                                 │ │
│ │ Container:                      │ │
│ │ - Bg: #1F2937                   │ │
│ │ - Border: 1px #F59E0B           │ │
│ │ - Padding: 12px                 │ │
│ │ - Border-radius: 8px            │ │
│ │ - Box-shadow: 0 4px 12px rgba() │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

---

## 8. Weekly Review (Mobile)

```
┌─────────────────────────────────────┐
│ Status Bar                          │
├─────────────────────────────────────┤
│ Header                              │
│ ┌─────────────────────────────────┐ │
│ │ Week 45 Review            [X]   │ │
│ │ Title: 18px bold white          │ │
│ │ Close: 44x44px                  │ │
│ └─────────────────────────────────┘ │
│                                     │
│ Scrollable Content                  │
│ Background: #0B0D14                 │
│ Padding: 16px                       │
│                                     │
│ Stats Row (Horizontal scroll)       │
│ ┌─────────────────────────────────┐ │
│ │ Display: flex | Gap: 12px        │ │
│ │ Overflow-x: auto | pb-12px       │ │
│ │                                 │ │
│ │ ┌───────┐ ┌───────┐ ┌───────┐ │ │
│ │ │  24   │ │  85%  │ │  +2h  │ │ │
│ │ │  /28  │ │   ✓   │ │  🧠   │ │ │
│ │ └───────┘ └───────┘ └───────┘ │ │
│ │                                 │ │
│ │ Card Style:                     │ │
│ │ - Min-width: 100px              │ │
│ │ - Height: 80px                  │ │
│ │ - Bg: #1F2937                   │ │
│ │ - Border: 1px #374151           │ │
│ │ - Border-radius: 12px           │ │
│ │ - Padding: 12px                 │ │
│ │ - Value: 24px bold              │ │
│ │ - Label: 11px #9CA3AF           │ │
│ └─────────────────────────────────┘ │
│                                     │
│ AI Insights (Margin-top: 20px)      │
│ ┌─────────────────────────────────┐ │
│ │ AI Insights:                    │ │
│ │ Label: 14px bold #9CA3AF | mb-12│ │
│ │                                 │ │
│ │ ✅ Career strong (90%)          │ │
│ │ ⚠️ Health weak (20%)           │ │
│ │                                 │ │
│ │ Each insight:                   │ │
│ │ - Padding: 12px                 │ │
│ │ - Bg: #1F2937                   │ │
│ │ - Border-radius: 8px            │ │
│ │ - Margin-bottom: 8px            │ │
│ │ - Icon: 16px                    │ │
│ │ - Text: 14px #D1D5DB            │ │
│ └─────────────────────────────────┘ │
│                                     │
│ Reflection Inputs (mt-24px)         │
│ ┌─────────────────────────────────┐ │
│ │ Biggest win?                    │ │
│ │ Label: 14px bold white | mb-8   │ │
│ │                                 │ │
│ │ [_________________________]     │ │
│ │ Textarea: Width 100%            │ │
│ │ Height: 80px                    │ │
│ │ Bg: #1F2937 | Border: #374151   │ │
│ │ Padding: 12px                   │ │
│ │ Border-radius: 8px              │ │
│ │ Font: 16px | Color: white       │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ What held you back?             │ │
│ │ [_________________________]     │ │
│ │ (Same textarea style)           │ │
│ └─────────────────────────────────┘ │
│                                     │
│ Next Week Preview (mt-24px)         │
│ ┌─────────────────────────────────┐ │
│ │ Next week: 3 critical deadlines │ │
│ │                                 │ │
│ │ Container:                      │ │
│ │ - Bg: #1F2937                   │ │
│ │ - Border: 1px #3B82F6           │ │
│ │ - Padding: 16px                 │ │
│ │ - Border-radius: 12px           │ │
│ │ - Font: 14px #D1D5DB            │ │
│ └─────────────────────────────────┘ │
│                                     │
│ Action Buttons (Fixed bottom)       │
│ ┌─────────────────────────────────┐ │
│ │ [Plan Week]                     │ │
│ │ Button: Width 100% | Height 48  │ │
│ │ Bg: gradient #F59E0B            │ │
│ │ Margin-bottom: 12px             │ │
│ │                                 │ │
│ │ [Later]                         │ │
│ │ Button: Width 100% | Height 48  │ │
│ │ Border: 1px #374151             │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

---

## 9. Smart Notifications (Mobile)

```
┌─────────────────────────────────────┐
│ Status Bar                          │
├─────────────────────────────────────┤
│ Header                              │
│ ┌─────────────────────────────────┐ │
│ │ Notifications             [⚙️]  │ │
│ │ Title: 18px bold white          │ │
│ │ Settings: 44x44px               │ │
│ └─────────────────────────────────┘ │
│                                     │
│ Notification Groups                 │
│ Background: #0B0D14                 │
│ Padding: 16px                       │
│                                     │
│ Now Section                         │
│ ┌─────────────────────────────────┐ │
│ │ Now (2)                         │ │
│ │ Section: 12px bold #9CA3AF      │ │
│ │ Count: #F59E0B                  │ │
│ │ Margin-bottom: 12px             │ │
│ │                                 │ │
│ │ ┌─────────────────────────────┐ │ │
│ │ │ Notification Card            │ │ │
│ │ │ Bg: #1F2937                  │ │ │
│ │ │ Border: 1px #EF4444          │ │ │
│ │ │ Border-radius: 12px          │ │ │
│ │ │ Padding: 16px                │ │ │
│ │ │ Margin-bottom: 12px          │ │ │
│ │ │                              │ │ │
│ │ │ 🚨 Deadline Alert            │ │ │
│ │ │ Icon: 20px | Title: 14px bold│ │ │
│ │ │                              │ │ │
│ │ │ PRD due in 2 hours           │ │ │
│ │ │ Text: 14px #D1D5DB           │ │ │
│ │ │ Margin-top: 4px              │ │ │
│ │ │                              │ │ │
│ │ │ [Start] [Snooze]             │ │ │
│ │ │ Buttons: py-6px px-12px      │ │ │
│ │ │ Font: 12px                   │ │ │
│ │ │ Margin-top: 12px             │ │ │
│ │ │ Gap: 8px                     │ │ │
│ │ └─────────────────────────────┘ │ │
│ └─────────────────────────────────┘ │
│                                     │
│ Today Section                       │
│ ┌─────────────────────────────────┐ │
│ │ Today (5)                       │ │
│ │                                 │ │
│ │ ┌─────────────────────────────┐ │ │
│ │ │ 📊 Daily Summary             │ │ │
│ │ │ 3 tasks to review            │ │ │
│ │ │                              │ │ │
│ │ │ Border: 1px #374151          │ │ │
│ │ │ (Less urgent styling)        │ │ │
│ │ │                              │ │ │
│ │ │ [Expand] [Clear]             │ │ │
│ │ └─────────────────────────────┘ │ │
│ └─────────────────────────────────┘ │
│                                     │
│ This Week Section                   │
│ ┌─────────────────────────────────┐ │
│ │ This Week (12)                  │ │
│ │                                 │ │
│ │ [View All]                      │ │
│ │ Button: Width 100% | Height 44  │ │
│ │ Border: 1px dashed #374151      │ │
│ │ Text: #9CA3AF                   │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

---

## 10. Quick Actions Menu (Mobile)

```
┌─────────────────────────────────────┐
│ Modal Overlay                       │
│ Background: rgba(0,0,0,0.7)         │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ Quick Actions Container         │ │
│ │ Position: center                │ │
│ │ Max-width: 320px                │ │
│ │ Width: calc(100% - 40px)        │ │
│ │ Bg: #111827                     │ │
│ │ Border-radius: 20px             │ │
│ │ Padding: 24px                   │ │
│ │ Box-shadow: 0 10px 40px rgba()  │ │
│ │                                 │ │
│ │ Quick Actions                   │ │
│ │ Title: 16px bold white          │ │
│ │ Text-align: center              │ │
│ │ Margin-bottom: 20px             │ │
│ │                                 │ │
│ │ Action Grid (3x2)               │ │
│ │ ┌───────┐ ┌───────┐ ┌───────┐ │ │
│ │ │  📝   │ │  🎤   │ │  📸   │ │ │
│ │ │ Task  │ │ Voice │ │ Photo │ │ │
│ │ └───────┘ └───────┘ └───────┘ │ │
│ │ ┌───────┐ ┌───────┐ ┌───────┐ │ │
│ │ │  ⏱️   │ │  🤖   │ │  📊   │ │ │
│ │ │ Timer │ │What's │ │Today's│ │ │
│ │ │       │ │ Next? │ │ Stats │ │ │
│ │ └───────┘ └───────┘ └───────┘ │ │
│ │                                 │ │
│ │ Grid: 3 columns | Gap: 12px     │ │
│ │ Button Style:                   │ │
│ │ - Size: 88x88px                 │ │
│ │ - Bg: #1F2937                   │ │
│ │ - Border: 1px #374151           │ │
│ │ - Border-radius: 16px           │ │
│ │ - Display: flex                 │ │
│ │ - Flex-direction: column        │ │
│ │ - Align-items: center           │ │
│ │ - Justify-content: center       │ │
│ │ - Gap: 4px                      │ │
│ │ - Icon: 28px                    │ │
│ │ - Label: 11px #D1D5DB           │ │
│ │                                 │ │
│ │ Hover/Active state:             │ │
│ │ - Transform: scale(0.95)        │ │
│ │ - Bg: #374151                   │ │
│ │ - Border: #F59E0B               │ │
│ │                                 │ │
│ │ [Close]                         │ │
│ │ Button: Width 100% | Height 44  │ │
│ │ Margin-top: 20px                │ │
│ │ Border: 1px #374151             │ │
│ │ Text: #9CA3AF                   │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

---

## Mobile Design System Summary

### Touch Targets
- Minimum height: 44px
- Preferred height: 48-56px for primary actions
- Spacing between targets: 8-12px minimum

### Safe Areas
- Top: `env(safe-area-inset-top)`
- Bottom: `env(safe-area-inset-bottom)`
- Additional padding: 20px from screen edges

### Typography (Mobile)
- Headers: 18-20px bold
- Body: 14-16px regular
- Small text: 11-12px
- Buttons: 14-16px medium

### Mobile-Specific Components
- Bottom sheets with drag handle
- Horizontal scrolling for stats/filters
- Fixed bottom action buttons
- Full-screen modals
- Swipe gestures support

### Animations
- Sheet slide-up: 300ms ease-out
- Button press: scale(0.95)
- Page transitions: horizontal slide
- Loading states: pulse animation

This mobile design maintains consistency with Aurum Life's design system while optimizing for touch interaction and mobile viewport constraints.