/**
 * RAG (Retrieval-Augmented Generation) Categorization Service
 * 
 * Provides intelligent content categorization using embeddings, context analysis,
 * and semantic understanding for automatic pillar/area/project suggestions.
 */

export interface ContentEmbedding {
  id: string;
  content: string;
  embedding: number[];
  category: string;
  subcategory?: string;
  metadata: {
    pillar: string;
    area?: string;
    project?: string;
    keywords: string[];
    entities: string[];
    sentiment: 'positive' | 'neutral' | 'negative';
    urgency: 'low' | 'medium' | 'high';
    complexity: 'simple' | 'moderate' | 'complex';
  };
  confidence: number;
  timestamp: number;
}

export interface CategorizationResult {
  pillar: string;
  area?: string;
  project?: string;
  confidence: number;
  reasoning: string;
  alternatives: Array<{
    pillar: string;
    area?: string;
    confidence: number;
  }>;
  metadata: {
    sentiment: 'positive' | 'neutral' | 'negative';
    urgency: 'low' | 'medium' | 'high';
    complexity: 'simple' | 'moderate' | 'complex';
    keywords: string[];
    entities: string[];
    suggestedTags: string[];
    estimatedDuration?: string;
    priority?: 'low' | 'medium' | 'high';
  };
}

export interface ContextualData {
  recentItems: Array<{
    content: string;
    pillar: string;
    area?: string;
    timestamp: number;
  }>;
  userPreferences: {
    frequentPillars: string[];
    workingHours: { start: string; end: string };
    focusAreas: string[];
  };
  currentContext: {
    timeOfDay: 'morning' | 'afternoon' | 'evening' | 'night';
    dayOfWeek: string;
    currentTasks?: string[];
    currentProjects?: string[];
  };
}

class RAGCategorizationService {
  private embeddings: Map<string, ContentEmbedding> = new Map();
  private categoryPatterns: Map<string, RegExp[]> = new Map();
  private contextHistory: ContentEmbedding[] = [];
  private userLearningData: Map<string, any> = new Map();

  constructor() {
    this.initializePatterns();
    this.loadStoredData();
  }

  /**
   * Initialize category patterns for initial classification
   */
  private initializePatterns(): void {
    this.categoryPatterns.set('Health & Fitness', [
      /\b(workout|exercise|gym|fitness|health|run|walk|yoga|meditation|diet|nutrition|doctor|medical)\b/i,
      /\b(calories|weight|muscle|cardio|strength|training|sports|athletic)\b/i,
      /\b(mental health|therapy|wellness|self-care|sleep|energy)\b/i
    ]);

    this.categoryPatterns.set('Career & Professional', [
      /\b(work|job|career|project|meeting|deadline|presentation|client|business|professional)\b/i,
      /\b(salary|promotion|interview|networking|skills|leadership|management|team)\b/i,
      /\b(development|coding|design|analysis|strategy|planning|goals|kpi)\b/i
    ]);

    this.categoryPatterns.set('Relationships', [
      /\b(family|friend|relationship|partner|spouse|date|social|communication|love)\b/i,
      /\b(conversation|call|visit|dinner|party|celebration|anniversary|wedding)\b/i,
      /\b(conflict|resolution|support|connection|bonding|quality time)\b/i
    ]);

    this.categoryPatterns.set('Personal Development', [
      /\b(learn|study|course|book|skill|growth|development|improvement|goal)\b/i,
      /\b(meditation|reflection|journal|habit|routine|mindset|productivity)\b/i,
      /\b(creativity|art|music|writing|hobby|passion|interest|exploration)\b/i
    ]);

    this.categoryPatterns.set('Finance & Wealth', [
      /\b(money|budget|savings|investment|financial|income|expense|debt|loan)\b/i,
      /\b(portfolio|stocks|crypto|retirement|insurance|tax|planning|wealth)\b/i,
      /\b(purchase|buying|selling|cost|price|value|economic|market)\b/i
    ]);

    this.categoryPatterns.set('Home & Living', [
      /\b(home|house|apartment|cleaning|organizing|maintenance|repair|renovation)\b/i,
      /\b(cooking|recipe|meal|grocery|shopping|garden|plants|decoration)\b/i,
      /\b(utility|rent|mortgage|neighborhood|moving|furniture|appliance)\b/i
    ]);
  }

  /**
   * Load stored embeddings and user data
   */
  private loadStoredData(): void {
    try {
      const storedEmbeddings = localStorage.getItem('aurum-rag-embeddings');
      if (storedEmbeddings) {
        const data = JSON.parse(storedEmbeddings);
        data.forEach((item: ContentEmbedding) => {
          this.embeddings.set(item.id, item);
        });
      }

      const storedLearning = localStorage.getItem('aurum-rag-learning');
      if (storedLearning) {
        const data = JSON.parse(storedLearning);
        Object.entries(data).forEach(([key, value]) => {
          this.userLearningData.set(key, value);
        });
      }
    } catch (error) {
      console.error('Failed to load RAG data:', error);
    }
  }

  /**
   * Save embeddings and learning data
   */
  private saveData(): void {
    try {
      const embeddingArray = Array.from(this.embeddings.values());
      localStorage.setItem('aurum-rag-embeddings', JSON.stringify(embeddingArray));

      const learningObject = Object.fromEntries(this.userLearningData);
      localStorage.setItem('aurum-rag-learning', JSON.stringify(learningObject));
    } catch (error) {
      console.error('Failed to save RAG data:', error);
    }
  }

  /**
   * Generate simple embedding vector (using TF-IDF-like approach)
   */
  private generateEmbedding(text: string): number[] {
    const words = text.toLowerCase().match(/\b\w+\b/g) || [];
    const vocab = ['work', 'health', 'family', 'money', 'learn', 'home', 'project', 'goal', 'task', 'idea'];
    
    return vocab.map(word => {
      const count = words.filter(w => w.includes(word) || word.includes(w)).length;
      return count / words.length;
    });
  }

  /**
   * Calculate cosine similarity between two embeddings
   */
  private cosineSimilarity(a: number[], b: number[]): number {
    const dotProduct = a.reduce((sum, val, i) => sum + val * b[i], 0);
    const magnitudeA = Math.sqrt(a.reduce((sum, val) => sum + val * val, 0));
    const magnitudeB = Math.sqrt(b.reduce((sum, val) => sum + val * val, 0));
    
    if (magnitudeA === 0 || magnitudeB === 0) return 0;
    return dotProduct / (magnitudeA * magnitudeB);
  }

  /**
   * Extract entities and keywords from text
   */
  private extractEntities(text: string): { keywords: string[]; entities: string[] } {
    const words = text.toLowerCase().match(/\b\w+\b/g) || [];
    
    // Simple keyword extraction (remove stop words)
    const stopWords = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'my', 'your', 'his', 'her', 'its', 'our', 'their'];
    const keywords = words.filter(word => 
      word.length > 3 && 
      !stopWords.includes(word) &&
      !/^\d+$/.test(word)
    );

    // Simple entity extraction (capitalize words that might be proper nouns)
    const entities = text.match(/\b[A-Z][a-z]+\b/g) || [];
    
    return { 
      keywords: [...new Set(keywords)].slice(0, 10), 
      entities: [...new Set(entities)].slice(0, 5) 
    };
  }

  /**
   * Analyze sentiment of the text
   */
  private analyzeSentiment(text: string): 'positive' | 'neutral' | 'negative' {
    const positiveWords = ['good', 'great', 'excellent', 'amazing', 'awesome', 'happy', 'excited', 'love', 'perfect', 'wonderful', 'fantastic', 'brilliant', 'success', 'achieve', 'accomplish'];
    const negativeWords = ['bad', 'terrible', 'awful', 'hate', 'sad', 'angry', 'frustrated', 'difficult', 'problem', 'issue', 'fail', 'mistake', 'wrong', 'stress', 'worry'];
    
    const words = text.toLowerCase().match(/\b\w+\b/g) || [];
    const positiveCount = words.filter(word => positiveWords.includes(word)).length;
    const negativeCount = words.filter(word => negativeWords.includes(word)).length;
    
    if (positiveCount > negativeCount) return 'positive';
    if (negativeCount > positiveCount) return 'negative';
    return 'neutral';
  }

  /**
   * Determine urgency level
   */
  private analyzeUrgency(text: string): 'low' | 'medium' | 'high' {
    const highUrgencyWords = ['urgent', 'asap', 'immediately', 'emergency', 'deadline', 'tomorrow', 'today', 'now', 'quick', 'fast'];
    const mediumUrgencyWords = ['soon', 'this week', 'important', 'priority', 'schedule', 'plan'];
    
    const lowerText = text.toLowerCase();
    
    if (highUrgencyWords.some(word => lowerText.includes(word))) return 'high';
    if (mediumUrgencyWords.some(word => lowerText.includes(word))) return 'medium';
    return 'low';
  }

  /**
   * Determine complexity level
   */
  private analyzeComplexity(text: string): 'simple' | 'moderate' | 'complex' {
    const complexWords = ['strategy', 'analysis', 'research', 'development', 'implementation', 'system', 'process', 'methodology'];
    const moderateWords = ['plan', 'organize', 'prepare', 'design', 'review', 'study', 'practice'];
    
    const lowerText = text.toLowerCase();
    const wordCount = text.split(/\s+/).length;
    
    if (wordCount > 50 || complexWords.some(word => lowerText.includes(word))) return 'complex';
    if (wordCount > 20 || moderateWords.some(word => lowerText.includes(word))) return 'moderate';
    return 'simple';
  }

  /**
   * Main categorization function
   */
  async categorizeContent(
    content: string, 
    contentType: 'idea' | 'task' | 'note' | 'goal',
    contextualData?: ContextualData
  ): Promise<CategorizationResult> {
    const embedding = this.generateEmbedding(content);
    const { keywords, entities } = this.extractEntities(content);
    const sentiment = this.analyzeSentiment(content);
    const urgency = this.analyzeUrgency(content);
    const complexity = this.analyzeComplexity(content);

    // Pattern-based initial classification
    let bestMatch = { pillar: 'Personal Development', confidence: 0.4, reasoning: 'Default categorization' };
    
    for (const [pillar, patterns] of this.categoryPatterns) {
      for (const pattern of patterns) {
        const matches = content.match(pattern);
        if (matches && matches.length > 0) {
          const confidence = Math.min(0.9, 0.5 + (matches.length * 0.1));
          if (confidence > bestMatch.confidence) {
            bestMatch = {
              pillar,
              confidence,
              reasoning: `Detected ${matches.length} relevant keyword${matches.length > 1 ? 's' : ''}: ${matches.slice(0, 3).join(', ')}`
            };
          }
        }
      }
    }

    // Enhance with similarity matching if we have embeddings
    const similarItems = this.findSimilarContent(embedding, 5);
    if (similarItems.length > 0) {
      const pillarCounts = similarItems.reduce((acc, item) => {
        acc[item.metadata.pillar] = (acc[item.metadata.pillar] || 0) + item.confidence;
        return acc;
      }, {} as Record<string, number>);
      
      const topSimilarPillar = Object.entries(pillarCounts)
        .sort(([, a], [, b]) => b - a)[0];
      
      if (topSimilarPillar && topSimilarPillar[1] > bestMatch.confidence) {
        bestMatch = {
          pillar: topSimilarPillar[0],
          confidence: Math.min(0.95, topSimilarPillar[1]),
          reasoning: `Similar to ${similarItems.length} previous items in this category`
        };
      }
    }

    // Context-based adjustments
    if (contextualData) {
      const contextBoost = this.applyContextualBoost(bestMatch.pillar, contextualData);
      bestMatch.confidence = Math.min(0.98, bestMatch.confidence + contextBoost);
    }

    // Determine area based on pillar and content
    const area = this.suggestArea(bestMatch.pillar, content, contentType);
    const project = this.suggestProject(bestMatch.pillar, area, content, contextualData);

    // Generate alternatives
    const alternatives = this.generateAlternatives(content, embedding, bestMatch.pillar);

    // Generate suggested tags
    const suggestedTags = this.generateTags(content, keywords, entities, contentType);

    // Estimate duration for tasks
    const estimatedDuration = contentType === 'task' ? this.estimateDuration(content, complexity) : undefined;

    // Determine priority
    const priority = this.determinePriority(urgency, complexity, contentType);

    return {
      pillar: bestMatch.pillar,
      area,
      project,
      confidence: bestMatch.confidence,
      reasoning: bestMatch.reasoning,
      alternatives,
      metadata: {
        sentiment,
        urgency,
        complexity,
        keywords,
        entities,
        suggestedTags,
        estimatedDuration,
        priority
      }
    };
  }

  /**
   * Find similar content based on embeddings
   */
  private findSimilarContent(embedding: number[], limit: number = 5): ContentEmbedding[] {
    const similarities = Array.from(this.embeddings.values())
      .map(item => ({
        ...item,
        similarity: this.cosineSimilarity(embedding, item.embedding)
      }))
      .filter(item => item.similarity > 0.3)
      .sort((a, b) => b.similarity - a.similarity)
      .slice(0, limit);

    return similarities;
  }

  /**
   * Apply contextual boost based on user patterns
   */
  private applyContextualBoost(pillar: string, context: ContextualData): number {
    let boost = 0;

    // Time-based boost
    if (context.currentContext.timeOfDay === 'morning' && pillar === 'Health & Fitness') {
      boost += 0.1;
    }
    if (context.currentContext.timeOfDay === 'afternoon' && pillar === 'Career & Professional') {
      boost += 0.1;
    }

    // Recent activity boost
    const recentPillars = context.recentItems.map(item => item.pillar);
    const recentPillarCount = recentPillars.filter(p => p === pillar).length;
    if (recentPillarCount > 0) {
      boost += Math.min(0.2, recentPillarCount * 0.05);
    }

    // User preference boost
    if (context.userPreferences.frequentPillars.includes(pillar)) {
      boost += 0.15;
    }

    return boost;
  }

  /**
   * Suggest area based on pillar and content
   */
  private suggestArea(pillar: string, content: string, contentType: string): string {
    const areaMapping: Record<string, Record<string, string[]>> = {
      'Health & Fitness': {
        'Physical Health': ['workout', 'exercise', 'gym', 'fitness', 'sport', 'training'],
        'Mental Health': ['meditation', 'therapy', 'stress', 'mental', 'mindfulness'],
        'Nutrition': ['diet', 'food', 'meal', 'nutrition', 'eating', 'cooking']
      },
      'Career & Professional': {
        'Current Projects': ['project', 'work', 'task', 'assignment', 'development'],
        'Skill Development': ['learn', 'skill', 'course', 'training', 'certification'],
        'Networking': ['meeting', 'client', 'networking', 'relationship', 'contact']
      },
      'Relationships': {
        'Family': ['family', 'parent', 'child', 'sibling', 'relative'],
        'Friends': ['friend', 'social', 'party', 'hangout', 'visit'],
        'Romantic': ['partner', 'spouse', 'date', 'relationship', 'romantic']
      },
      'Personal Development': {
        'Learning': ['learn', 'study', 'book', 'course', 'education', 'knowledge'],
        'Habits': ['habit', 'routine', 'practice', 'consistency', 'behavior'],
        'Creativity': ['creative', 'art', 'music', 'writing', 'hobby', 'passion']
      },
      'Finance & Wealth': {
        'Budgeting': ['budget', 'expense', 'spending', 'cost', 'money'],
        'Investments': ['invest', 'stock', 'portfolio', 'crypto', 'savings'],
        'Planning': ['financial', 'retirement', 'planning', 'goal', 'future']
      },
      'Home & Living': {
        'Maintenance': ['repair', 'fix', 'maintenance', 'clean', 'organize'],
        'Improvement': ['renovation', 'upgrade', 'decoration', 'furniture'],
        'Daily Life': ['cooking', 'grocery', 'chores', 'routine', 'household']
      }
    };

    const pillarAreas = areaMapping[pillar];
    if (!pillarAreas) return 'General';

    const lowerContent = content.toLowerCase();
    for (const [area, keywords] of Object.entries(pillarAreas)) {
      if (keywords.some(keyword => lowerContent.includes(keyword))) {
        return area;
      }
    }

    return Object.keys(pillarAreas)[0]; // Return first area as default
  }

  /**
   * Suggest project based on context
   */
  private suggestProject(pillar: string, area: string, content: string, context?: ContextualData): string | undefined {
    if (!context?.currentContext.currentProjects) return undefined;

    const lowerContent = content.toLowerCase();
    const relevantProjects = context.currentContext.currentProjects.filter(project => {
      const lowerProject = project.toLowerCase();
      return lowerContent.includes(lowerProject) || lowerProject.includes(lowerContent.split(' ')[0]);
    });

    return relevantProjects[0];
  }

  /**
   * Generate alternative categorizations
   */
  private generateAlternatives(content: string, embedding: number[], excludePillar: string): Array<{pillar: string; area?: string; confidence: number}> {
    const alternatives: Array<{pillar: string; area?: string; confidence: number}> = [];
    
    for (const [pillar, patterns] of this.categoryPatterns) {
      if (pillar === excludePillar) continue;
      
      for (const pattern of patterns) {
        const matches = content.match(pattern);
        if (matches && matches.length > 0) {
          const confidence = Math.min(0.8, 0.3 + (matches.length * 0.1));
          alternatives.push({
            pillar,
            confidence,
            area: this.suggestArea(pillar, content, 'idea')
          });
        }
      }
    }

    return alternatives
      .sort((a, b) => b.confidence - a.confidence)
      .slice(0, 3);
  }

  /**
   * Generate suggested tags
   */
  private generateTags(content: string, keywords: string[], entities: string[], contentType: string): string[] {
    const tags = new Set<string>();
    
    // Add content type
    tags.add(contentType);
    
    // Add top keywords
    keywords.slice(0, 3).forEach(keyword => tags.add(keyword));
    
    // Add entities
    entities.slice(0, 2).forEach(entity => tags.add(entity));
    
    // Add contextual tags
    const lowerContent = content.toLowerCase();
    if (lowerContent.includes('urgent') || lowerContent.includes('asap')) tags.add('urgent');
    if (lowerContent.includes('meeting') || lowerContent.includes('call')) tags.add('communication');
    if (lowerContent.includes('creative') || lowerContent.includes('idea')) tags.add('creative');
    
    return Array.from(tags).slice(0, 8);
  }

  /**
   * Estimate duration for tasks
   */
  private estimateDuration(content: string, complexity: string): string {
    const wordCount = content.split(/\s+/).length;
    
    if (complexity === 'simple' || wordCount < 10) {
      return '15-30 minutes';
    } else if (complexity === 'moderate' || wordCount < 30) {
      return '1-2 hours';
    } else {
      return 'Half day or more';
    }
  }

  /**
   * Determine priority
   */
  private determinePriority(urgency: string, complexity: string, contentType: string): 'low' | 'medium' | 'high' {
    if (urgency === 'high') return 'high';
    if (urgency === 'medium' && complexity !== 'simple') return 'medium';
    if (contentType === 'goal') return 'medium';
    return 'low';
  }

  /**
   * Learn from user feedback
   */
  learnFromFeedback(content: string, actualCategory: {pillar: string; area?: string; project?: string}, wasCorrect: boolean): void {
    const embedding = this.generateEmbedding(content);
    const { keywords, entities } = this.extractEntities(content);
    
    const contentEmbedding: ContentEmbedding = {
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      content,
      embedding,
      category: actualCategory.pillar,
      subcategory: actualCategory.area,
      metadata: {
        pillar: actualCategory.pillar,
        area: actualCategory.area,
        project: actualCategory.project,
        keywords,
        entities,
        sentiment: this.analyzeSentiment(content),
        urgency: this.analyzeUrgency(content),
        complexity: this.analyzeComplexity(content)
      },
      confidence: wasCorrect ? 0.9 : 0.7,
      timestamp: Date.now()
    };

    this.embeddings.set(contentEmbedding.id, contentEmbedding);
    this.contextHistory.push(contentEmbedding);

    // Keep only recent history (last 1000 items)
    if (this.contextHistory.length > 1000) {
      this.contextHistory = this.contextHistory.slice(-1000);
    }

    this.saveData();
  }

  /**
   * Get user learning statistics
   */
  getLearningStats(): {totalItems: number; accuracy: number; topCategories: string[]} {
    const totalItems = this.embeddings.size;
    const accurateItems = Array.from(this.embeddings.values()).filter(item => item.confidence > 0.8).length;
    const accuracy = totalItems > 0 ? accurateItems / totalItems : 0;
    
    const categoryCount = Array.from(this.embeddings.values()).reduce((acc, item) => {
      acc[item.category] = (acc[item.category] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
    
    const topCategories = Object.entries(categoryCount)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 5)
      .map(([category]) => category);

    return { totalItems, accuracy, topCategories };
  }

  /**
   * Reset learning data (for testing or fresh start)
   */
  resetLearningData(): void {
    this.embeddings.clear();
    this.contextHistory = [];
    this.userLearningData.clear();
    localStorage.removeItem('aurum-rag-embeddings');
    localStorage.removeItem('aurum-rag-learning');
  }
}

export const ragCategorizationService = new RAGCategorizationService();