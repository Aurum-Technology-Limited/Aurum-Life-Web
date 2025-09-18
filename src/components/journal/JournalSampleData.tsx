import { useEffect } from 'react';
import { useJournalStore } from '../../stores/journalStore';

const sampleEntries = [
  {
    title: 'Reflecting on Marathon Training Progress',
    content: `Completed week 8 of my marathon training program today, and I'm feeling incredibly strong and confident about the pace improvements I've been seeing. The 18-mile long run went better than expected - I maintained a steady 8:30 pace throughout, which is exactly where I want to be for race day.

What I'm learning about myself through this process is that consistency trumps intensity every time. The days when I didn't feel like running but did it anyway are the ones that built the most mental strength. There's something powerful about proving to yourself that you can follow through on commitments, especially when your body and mind are resisting.

The nutrition strategy is finally clicking too. I've been experimenting with different fuel sources during long runs, and the combination of dates and electrolyte drink seems to work best for my system. No more GI issues, which was a huge concern earlier in the training cycle.

Looking ahead to the next phase, I'm excited but also aware that the real test is coming. The 20+ mile runs will push me into uncharted territory. But if these past 8 weeks have taught me anything, it's that I'm more capable than I give myself credit for.`,
    date: new Date('2024-03-09'),
    mood: 'positive' as const,
    energy: 4,
    tags: ['training', 'health', 'progress', 'running', 'marathon'],
    isPrivate: false
  },
  {
    title: 'Career Development Insights',
    content: `The React Native project I've been working on is teaching me so much about mobile development patterns and cross-platform considerations. Today I had a breakthrough moment when I finally understood how to properly manage state across native modules.

It's fascinating how different mobile development feels compared to web development. The constraints actually force you to be more creative and intentional with your solutions. Every animation, every transition needs to be purposeful because performance is so critical.

I'm starting to see how my career path is evolving. Six months ago I was purely focused on web technologies, but now I'm genuinely excited about mobile development. There's something satisfying about building applications that people carry with them everywhere.

The team dynamics on this project have been excellent too. Working with Sarah and Mike has pushed me to communicate more clearly about technical decisions. I've learned that being right isn't enough - you need to be able to explain why your approach is better in terms that everyone can understand.

Next week I'm planning to propose a new architecture for handling offline data synchronization. It's a complex problem, but I think I have an elegant solution that could become a pattern we use across all our mobile apps.`,
    date: new Date('2024-03-08'),
    mood: 'motivated' as const,
    energy: 5,
    tags: ['career', 'learning', 'mobile', 'react-native', 'technology'],
    isPrivate: false
  },
  {
    title: 'Family Dinner Success',
    content: `Had an amazing family dinner last night that reminded me why these moments are so precious. The kids were full of stories about their school projects, and for once everyone was present - no phones, no distractions, just genuine conversation and laughter.

Emma shared her science fair project about renewable energy, and I was blown away by how thoughtful her approach was. She's only 10 but she's already thinking about environmental impact in ways that some adults don't. When she explained her solar panel experiment, her eyes lit up with genuine curiosity and passion.

Jake was quieter as usual, but he opened up about the book he's reading - something about a young wizard (clearly influenced by Harry Potter phase). What struck me wasn't the story itself, but how he was connecting the character's journey to his own struggles with fitting in at school. These moments of vulnerability from him are rare and precious.

Lisa and I managed to actually have an adult conversation while the kids were distracted with dessert. We talked about our plans for the summer, dreams we've been putting on hold, and how we can better support each other's goals. It's easy to get caught up in the daily logistics of family life and forget we're partners in this bigger adventure.

These dinner conversations need to happen more regularly. I'm committing to putting devices away and being fully present for at least one family meal each day.`,
    date: new Date('2024-03-07'),
    mood: 'grateful' as const,
    energy: 4,
    tags: ['family', 'gratitude', 'connection', 'parenting', 'relationships'],
    isPrivate: false
  },
  {
    title: 'Financial Planning Breakthrough',
    content: `Finally organized my investment portfolio and set up automatic rebalancing today. What should have been done years ago is finally complete, and I feel a huge weight lifted off my shoulders.

The analysis was eye-opening. I was way too heavily invested in tech stocks (occupational hazard, I suppose) and had almost no international diversification. The new allocation spreads risk much more effectively: 40% total stock market index, 20% international stocks, 20% bonds, 10% REITs, and 10% in individual stocks for fun.

Setting up the automatic rebalancing was the game-changer. Now I don't have to think about it - the system will automatically sell high-performing assets and buy underperforming ones to maintain the target allocation. It removes emotion from the equation, which is exactly what I need.

I also increased my 401k contribution to the maximum employer match. Can't believe I was leaving free money on the table for so long. The tax benefits are substantial, and compound growth over the next 20 years should make a significant difference in retirement planning.

The next step is building a proper emergency fund. Right now I have about 3 months of expenses saved, but I want to get to 6 months for peace of mind. I've set up an automatic transfer to a high-yield savings account that should get me there in about 8 months.

Financial security isn't just about money - it's about freedom to make choices based on what's important rather than what's financially necessary.`,
    date: new Date('2024-03-06'),
    mood: 'accomplished' as const,
    energy: 3,
    tags: ['finance', 'planning', 'automation', 'investments', 'goals'],
    isPrivate: false
  },
  {
    title: 'Morning Meditation Practice',
    content: `Started my day with 20 minutes of meditation, and the difference in my mental clarity is remarkable. There's something about those quiet moments before the world wakes up that feels almost sacred.

Today's session focused on loving-kindness meditation. Started with sending compassion to myself, then extended it to family, friends, neutral people, difficult people, and finally all beings. It's challenging to genuinely wish well for people who have hurt you, but that's where the real growth happens.

I notice that my mind is less reactive throughout the day when I start with meditation. Small annoyances that would normally trigger stress responses just seem to roll off me. It's like creating a buffer between stimulus and response.

The physical benefits are noticeable too. My breathing is deeper, my shoulders less tense, and I'm sleeping better at night. Seven weeks of consistent practice is starting to rewire some long-held patterns of anxiety and overthinking.

Tomorrow I want to try walking meditation in the garden. There's something appealing about combining mindfulness with gentle movement and connection to nature.`,
    date: new Date('2024-03-05'),
    mood: 'peaceful' as const,
    energy: 3,
    tags: ['meditation', 'mindfulness', 'morning-routine', 'mental-health', 'self-care'],
    isPrivate: false
  },
  {
    title: 'Creative Block Breakthrough',
    content: `After weeks of feeling stuck on the design project, everything clicked today. Sometimes the best ideas come when you stop forcing them and just let your mind wander.

I was walking through the park during lunch break, not thinking about work at all, when the visual metaphor for the client's brand suddenly became clear. They want to represent transformation and growth, and I kept thinking too literally about butterflies and plants. But watching people move through the space - some hurrying, some strolling, some stopping to chat - I realized the real story is about journey and connection.

Rushed back to the studio and sketched for three hours straight. The concept combines elements of pathways, intersections, and organic growth patterns. It's sophisticated enough for their corporate audience but warm enough to feel approachable.

What I love about this solution is how it can work across all their touchpoints - the logo becomes a navigation system for their website, the color palette reflects different stages of growth, and the typography feels both professional and human.

The client presentation is next week, and for the first time in months, I'm excited rather than anxious about showing my work. There's something magical about the moment when you know you've found the right answer.

This reminds me why I became a designer in the first place - the problem-solving, the visual storytelling, the moment when form and function align perfectly.`,
    date: new Date('2024-03-04'),
    mood: 'excited' as const,
    energy: 5,
    tags: ['creativity', 'design', 'breakthrough', 'inspiration', 'work'],
    isPrivate: false
  }
];

export default function JournalSampleData() {
  const { entries, createEntry } = useJournalStore();

  useEffect(() => {
    // Only add sample data if there are no existing entries
    if (entries.length === 0) {
      sampleEntries.forEach(entry => {
        createEntry(entry);
      });
    }
  }, [entries.length, createEntry]);

  return null; // This component doesn't render anything
}