import React, { useState } from 'react';
import { BookOpen, Heart, Target, Palette, Brain, Plus } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { useJournalStore, JournalTemplate } from '../../stores/journalStore';
import CustomTemplateModal from './CustomTemplateModal';

const categoryIcons = {
  daily: BookOpen,
  gratitude: Heart,
  reflection: Brain,
  'goal-setting': Target,
  'problem-solving': Brain,
  creative: Palette,
  custom: Plus
};

const categoryColors = {
  daily: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
  gratitude: 'bg-pink-500/10 text-pink-400 border-pink-500/30',
  reflection: 'bg-purple-500/10 text-purple-400 border-purple-500/30',
  'goal-setting': 'bg-green-500/10 text-green-400 border-green-500/30',
  'problem-solving': 'bg-orange-500/10 text-orange-400 border-orange-500/30',
  creative: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30',
  custom: 'bg-gray-500/10 text-gray-400 border-gray-500/30'
};

interface TemplateSelectorProps {
  onSelectTemplate: (template: JournalTemplate) => void;
  onCreateBlank: () => void;
}

export default function TemplateSelector({ onSelectTemplate, onCreateBlank }: TemplateSelectorProps) {
  const { templates } = useJournalStore();
  const [isCustomTemplateModalOpen, setIsCustomTemplateModalOpen] = useState(false);

  // Character limits for text content
  const MAX_TITLE_LENGTH = 25;
  const MAX_DESCRIPTION_LENGTH = 80;
  const MAX_PROMPT_PREVIEW_LENGTH = 60;

  const truncateText = (text: string, maxLength: number) => {
    return text.length > maxLength ? text.substring(0, maxLength).trim() + '...' : text;
  };

  const groupedTemplates = templates.reduce((acc, template) => {
    if (!acc[template.category]) {
      acc[template.category] = [];
    }
    acc[template.category].push(template);
    return acc;
  }, {} as Record<string, JournalTemplate[]>);

  return (
    <div className="space-y-6 p-6 max-h-[80vh] overflow-y-auto">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-foreground mb-2">Choose Your Starting Point</h2>
        <p className="text-muted-foreground">
          Select a template to guide your reflection, or start with a blank entry
        </p>
      </div>

      {/* Quick Actions */}
      <div className="flex justify-center space-x-3">
        <Button 
          onClick={onCreateBlank}
          className="bg-primary text-primary-foreground hover:bg-primary/90"
        >
          <BookOpen className="w-4 h-4 mr-2" />
          Blank Entry
        </Button>
      </div>

      {/* Template Categories */}
      <div className="space-y-8 pb-4">
        {Object.entries(groupedTemplates).map(([category, categoryTemplates]) => {
          const IconComponent = categoryIcons[category as keyof typeof categoryIcons] || BookOpen;
          const colorClass = categoryColors[category as keyof typeof categoryColors] || categoryColors.custom;
          
          return (
            <div key={category}>
              <div className="flex items-center space-x-2 mb-4">
                <IconComponent className="w-5 h-5 text-primary" />
                <h3 className="text-lg font-semibold text-foreground capitalize">
                  {category.replace('-', ' ')}
                </h3>
                <Badge variant="secondary" className={colorClass}>
                  {categoryTemplates.length}
                </Badge>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {categoryTemplates.map((template) => (
                  <Card 
                    key={template.id}
                    className="glassmorphism-card border-0 cursor-pointer hover:scale-105 transition-transform h-full"
                    onClick={() => onSelectTemplate(template)}
                  >
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex items-center space-x-2 min-w-0 flex-1">
                          <span className="text-2xl flex-shrink-0">{template.icon}</span>
                          <CardTitle className="text-base" title={template.name}>
                            {truncateText(template.name, MAX_TITLE_LENGTH)}
                          </CardTitle>
                        </div>
                        <Badge variant="outline" className={`${colorClass} text-xs flex-shrink-0`}>
                          {template.category}
                        </Badge>
                      </div>
                      <CardDescription className="text-sm leading-relaxed" title={template.description}>
                        {truncateText(template.description, MAX_DESCRIPTION_LENGTH)}
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="pt-0">
                      <div className="space-y-3">
                        <div className="text-xs text-muted-foreground font-medium">
                          {template.prompts.length} prompts
                        </div>
                        <div className="text-xs text-muted-foreground leading-relaxed" title={template.prompts[0]}>
                          {truncateText(template.prompts[0], MAX_PROMPT_PREVIEW_LENGTH)}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {/* Custom Template Creation */}
      <Card className="glassmorphism-card border-0 border-dashed border-border/50 cursor-pointer hover:border-primary/30 transition-colors">
        <CardContent className="p-8 text-center">
          <Plus className="w-12 h-12 mx-auto mb-4 text-primary/50" />
          <h3 className="text-lg font-medium text-foreground mb-2">Create Custom Template</h3>
          <p className="text-sm text-muted-foreground mb-4">
            Design your own journal prompts and save them as templates for future use
          </p>
          <Button 
            variant="outline" 
            className="border-border hover:bg-accent"
            onClick={() => setIsCustomTemplateModalOpen(true)}
          >
            <Plus className="w-4 h-4 mr-2" />
            Create Template
          </Button>
        </CardContent>
      </Card>

      {/* Custom Template Modal */}
      <CustomTemplateModal 
        isOpen={isCustomTemplateModalOpen}
        onClose={() => setIsCustomTemplateModalOpen(false)}
        onTemplateCreated={(template) => {
          // Auto-select the newly created template for immediate use
          onSelectTemplate(template);
        }}
      />
    </div>
  );
}