import React, { useState } from 'react';
import { X, Plus, Trash2, Save } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '../ui/dialog';
import { Button } from '../ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Label } from '../ui/label';
import { Badge } from '../ui/badge';
import { useJournalStore, JournalTemplate } from '../../stores/journalStore';
import LimitedInput from '../forms/LimitedInput';
import LimitedTextarea from '../forms/LimitedTextarea';

interface CustomTemplateModalProps {
  isOpen: boolean;
  onClose: () => void;
  onTemplateCreated: (template: JournalTemplate) => void;
}

// Character limits for template creation
const MAX_TEMPLATE_NAME_LENGTH = 25;
const MAX_TEMPLATE_DESCRIPTION_LENGTH = 80;
const MAX_PROMPT_LENGTH = 120;
const MAX_PROMPTS = 10;
const MIN_PROMPTS = 1;

const templateIcons = [
  '📝', '🙏', '🎯', '🎨', '🧩', '💡', '🌟', '📚', '🏆', '🌱',
  '💭', '🔥', '⚡', '🌈', '🎪', '🎭', '🎪', '🎨', '🎯', '🏅'
];

const categoryOptions = [
  { value: 'daily', label: 'Daily', description: 'Regular daily practices' },
  { value: 'gratitude', label: 'Gratitude', description: 'Appreciation and thankfulness' },
  { value: 'reflection', label: 'Reflection', description: 'Deep thinking and introspection' },
  { value: 'goal-setting', label: 'Goal Setting', description: 'Planning and tracking progress' },
  { value: 'problem-solving', label: 'Problem Solving', description: 'Working through challenges' },
  { value: 'creative', label: 'Creative', description: 'Creative expression and exploration' },
  { value: 'custom', label: 'Custom', description: 'Your unique template category' }
];

export default function CustomTemplateModal({ isOpen, onClose, onTemplateCreated }: CustomTemplateModalProps) {
  const { createTemplate } = useJournalStore();

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category: 'custom' as JournalTemplate['category'],
    icon: '📝',
    prompts: ['']
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const truncateText = (text: string, maxLength: number) => {
    return text.length > maxLength ? text.substring(0, maxLength) : text;
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Template name is required';
    } else if (formData.name.length > MAX_TEMPLATE_NAME_LENGTH) {
      newErrors.name = `Name must be ${MAX_TEMPLATE_NAME_LENGTH} characters or less`;
    }

    if (!formData.description.trim()) {
      newErrors.description = 'Description is required';
    } else if (formData.description.length > MAX_TEMPLATE_DESCRIPTION_LENGTH) {
      newErrors.description = `Description must be ${MAX_TEMPLATE_DESCRIPTION_LENGTH} characters or less`;
    }

    const validPrompts = formData.prompts.filter(prompt => prompt.trim());
    if (validPrompts.length < MIN_PROMPTS) {
      newErrors.prompts = `At least ${MIN_PROMPTS} prompt is required`;
    }

    // Check each prompt length
    formData.prompts.forEach((prompt, index) => {
      if (prompt.trim() && prompt.length > MAX_PROMPT_LENGTH) {
        newErrors[`prompt-${index}`] = `Prompt must be ${MAX_PROMPT_LENGTH} characters or less`;
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleInputChange = (field: keyof typeof formData, value: any) => {
    if (field === 'name') {
      value = truncateText(value, MAX_TEMPLATE_NAME_LENGTH);
    } else if (field === 'description') {
      value = truncateText(value, MAX_TEMPLATE_DESCRIPTION_LENGTH);
    }

    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear related errors
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const handlePromptChange = (index: number, value: string) => {
    const truncatedValue = truncateText(value, MAX_PROMPT_LENGTH);
    const newPrompts = [...formData.prompts];
    newPrompts[index] = truncatedValue;
    setFormData(prev => ({ ...prev, prompts: newPrompts }));
    
    // Clear related errors
    if (errors[`prompt-${index}`]) {
      setErrors(prev => ({ ...prev, [`prompt-${index}`]: '' }));
    }
    if (errors.prompts) {
      setErrors(prev => ({ ...prev, prompts: '' }));
    }
  };

  const addPrompt = () => {
    if (formData.prompts.length < MAX_PROMPTS) {
      setFormData(prev => ({ 
        ...prev, 
        prompts: [...prev.prompts, ''] 
      }));
    }
  };

  const removePrompt = (index: number) => {
    if (formData.prompts.length > 1) {
      const newPrompts = formData.prompts.filter((_, i) => i !== index);
      setFormData(prev => ({ ...prev, prompts: newPrompts }));
    }
  };

  const handleSubmit = () => {
    if (!validateForm()) {
      return;
    }

    const validPrompts = formData.prompts.filter(prompt => prompt.trim());
    
    const newTemplate: Omit<JournalTemplate, 'id'> = {
      name: formData.name.trim(),
      description: formData.description.trim(),
      category: formData.category,
      icon: formData.icon,
      prompts: validPrompts
    };

    createTemplate(newTemplate);
    
    // Create the full template with ID for callback
    const fullTemplate: JournalTemplate = {
      ...newTemplate,
      id: crypto.randomUUID()
    };
    
    onTemplateCreated(fullTemplate);
    handleClose();
  };

  const handleClose = () => {
    setFormData({
      name: '',
      description: '',
      category: 'custom',
      icon: '📝',
      prompts: ['']
    });
    setErrors({});
    onClose();
  };

  const selectedCategory = categoryOptions.find(cat => cat.value === formData.category);
  const validPromptCount = formData.prompts.filter(prompt => prompt.trim()).length;

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent 
        className="glassmorphism-card border-0 bg-card text-card-foreground max-w-2xl max-h-[90vh] p-0 overflow-hidden"
        aria-describedby="custom-template-description"
      >
        <DialogHeader className="px-6 py-4 border-b border-border">
          <div className="flex items-center justify-between">
            <DialogTitle className="text-xl">Create Custom Template</DialogTitle>
            <Button variant="ghost" size="sm" onClick={handleClose}>
              <X className="w-4 h-4" />
            </Button>
          </div>
          <DialogDescription id="custom-template-description">
            Design your own journal prompts and save them as a reusable template
          </DialogDescription>
        </DialogHeader>

        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Template Name */}
          <div>
            <LimitedInput
              label="Template Name"
              value={formData.name}
              onValueChange={(value) => handleInputChange('name', value)}
              placeholder="Enter template name..."
              maxLength={MAX_TEMPLATE_NAME_LENGTH}
              className={errors.name ? 'border-destructive' : ''}
              showProgress={true}
              showIcon={true}
              helperText="Choose a memorable, descriptive name for your template"
            />
            {errors.name && (
              <p className="text-destructive text-sm mt-1">{errors.name}</p>
            )}
          </div>

          {/* Template Description */}
          <div>
            <LimitedTextarea
              label="Description"
              value={formData.description}
              onValueChange={(value) => handleInputChange('description', value)}
              placeholder="Describe what this template is for..."
              maxLength={MAX_TEMPLATE_DESCRIPTION_LENGTH}
              className={`min-h-20 ${errors.description ? 'border-destructive' : ''}`}
              showProgress={true}
              showIcon={true}
              helperText="Explain the purpose and context for this journal template"
            />
            {errors.description && (
              <p className="text-destructive text-sm mt-1">{errors.description}</p>
            )}
          </div>

          {/* Category and Icon */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Category</Label>
              <Select 
                value={formData.category} 
                onValueChange={(value) => handleInputChange('category', value)}
              >
                <SelectTrigger className="glassmorphism-card border-0 bg-input">
                  <SelectValue>
                    {selectedCategory && (
                      <div className="flex items-center space-x-2">
                        <span>{selectedCategory.label}</span>
                      </div>
                    )}
                  </SelectValue>
                </SelectTrigger>
                <SelectContent className="glassmorphism-card border-0 bg-card">
                  {categoryOptions.map((category) => (
                    <SelectItem key={category.value} value={category.value}>
                      <div>
                        <div className="font-medium">{category.label}</div>
                        <div className="text-xs text-muted-foreground">{category.description}</div>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Icon</Label>
              <Select 
                value={formData.icon} 
                onValueChange={(value) => handleInputChange('icon', value)}
              >
                <SelectTrigger className="glassmorphism-card border-0 bg-input">
                  <SelectValue>
                    <div className="flex items-center space-x-2">
                      <span className="text-lg">{formData.icon}</span>
                      <span>Choose Icon</span>
                    </div>
                  </SelectValue>
                </SelectTrigger>
                <SelectContent className="glassmorphism-card border-0 bg-card">
                  <div className="grid grid-cols-5 gap-2 p-2">
                    {templateIcons.map((icon) => (
                      <SelectItem key={icon} value={icon} className="cursor-pointer">
                        <span className="text-lg">{icon}</span>
                      </SelectItem>
                    ))}
                  </div>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Prompts */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <Label>
                Journal Prompts ({validPromptCount}/{MIN_PROMPTS} minimum, {MAX_PROMPTS} maximum)
              </Label>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={addPrompt}
                disabled={formData.prompts.length >= MAX_PROMPTS}
                className="glassmorphism-card border-0"
              >
                <Plus className="w-4 h-4 mr-1" />
                Add Prompt
              </Button>
            </div>
            
            {errors.prompts && (
              <p className="text-destructive text-sm">{errors.prompts}</p>
            )}

            <div className="space-y-3">
              {formData.prompts.map((prompt, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Prompt {index + 1}</span>
                    {formData.prompts.length > 1 && (
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => removePrompt(index)}
                        className="text-destructive hover:text-destructive/80"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    )}
                  </div>
                  <LimitedInput
                    value={prompt}
                    onValueChange={(value) => handlePromptChange(index, value)}
                    placeholder={`Enter prompt ${index + 1}...`}
                    maxLength={MAX_PROMPT_LENGTH}
                    className={errors[`prompt-${index}`] ? 'border-destructive' : ''}
                    showProgress={true}
                    showIcon={true}
                    helperText="Write a clear, thought-provoking question or statement"
                  />
                  {errors[`prompt-${index}`] && (
                    <p className="text-destructive text-sm mt-1">{errors[`prompt-${index}`]}</p>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Preview */}
          <div className="space-y-2">
            <Label>Preview</Label>
            <div className="glassmorphism-panel p-4 space-y-3">
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-2">
                  <span className="text-xl">{formData.icon}</span>
                  <div>
                    <h4 className="font-medium">{formData.name || 'Template Name'}</h4>
                    <Badge variant="outline" className="text-xs mt-1">
                      {selectedCategory?.label}
                    </Badge>
                  </div>
                </div>
              </div>
              <p className="text-sm text-muted-foreground">
                {formData.description || 'Template description will appear here...'}
              </p>
              <div className="text-xs text-muted-foreground">
                {validPromptCount} prompts
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-border flex justify-between items-center">
          <div className="text-sm text-muted-foreground">
            💡 Character limits ensure clean, readable templates. Use clear, actionable prompts.
          </div>
          <div className="flex space-x-3">
            <Button variant="outline" onClick={handleClose}>
              Cancel
            </Button>
            <Button 
              onClick={handleSubmit}
              className="bg-primary text-primary-foreground hover:bg-primary/90"
              disabled={!formData.name.trim() || !formData.description.trim() || validPromptCount < MIN_PROMPTS}
            >
              <Save className="w-4 h-4 mr-2" />
              Create Template
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}