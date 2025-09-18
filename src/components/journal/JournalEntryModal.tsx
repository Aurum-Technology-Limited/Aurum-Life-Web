import React, { useState, useEffect } from 'react';
import { X, Save, Calendar, Tag, Heart, Battery, Lock, Unlock, Trash2, Copy } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '../ui/dialog';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Slider } from '../ui/slider';
import { Switch } from '../ui/switch';
import { Label } from '../ui/label';
import { useJournalStore, JournalEntry } from '../../stores/journalStore';
import { useEnhancedFeaturesStore } from '../../stores/enhancedFeaturesStore';
import VoiceToText from './VoiceToText';
import LimitedInput from '../forms/LimitedInput';
import CharacterLimitIndicator from '../shared/CharacterLimitIndicator';

const moodOptions = [
  { value: 'excited', label: 'Excited', emoji: '🤩', color: 'text-orange-400' },
  { value: 'positive', label: 'Positive', emoji: '😊', color: 'text-green-400' },
  { value: 'neutral', label: 'Neutral', emoji: '😐', color: 'text-gray-400' },
  { value: 'thoughtful', label: 'Thoughtful', emoji: '🤔', color: 'text-purple-400' },
  { value: 'challenging', label: 'Challenging', emoji: '😤', color: 'text-red-400' },
  { value: 'grateful', label: 'Grateful', emoji: '🙏', color: 'text-pink-400' },
  { value: 'motivated', label: 'Motivated', emoji: '💪', color: 'text-blue-400' },
  { value: 'accomplished', label: 'Accomplished', emoji: '🎯', color: 'text-yellow-400' },
  { value: 'peaceful', label: 'Peaceful', emoji: '☮️', color: 'text-teal-400' },
  { value: 'energized', label: 'Energized', emoji: '⚡', color: 'text-emerald-400' }
];

const energyLabels = ['Low', 'Mild', 'Moderate', 'High', 'Peak'];

// Character limits for journal entries
const MAX_TITLE_LENGTH = 100;
const MAX_CONTENT_LENGTH = 50000; // Generous limit for long-form writing
const MAX_TAG_LENGTH = 30;
const MAX_TAGS = 20;

export default function JournalEntryModal() {
  const {
    currentEntry,
    isEntryModalOpen,
    isEditMode,
    closeEntryModal,
    createEntry,
    updateEntry,
    deleteEntry,
    duplicateEntry
  } = useJournalStore();

  const { pillars } = useEnhancedFeaturesStore();

  const [formData, setFormData] = useState<Partial<JournalEntry>>({});
  const [newTag, setNewTag] = useState('');
  const [wordCount, setWordCount] = useState(0);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (currentEntry) {
      setFormData(currentEntry);
      setWordCount(currentEntry.wordCount || 0);
    } else {
      setFormData({});
      setWordCount(0);
    }
  }, [currentEntry]);

  useEffect(() => {
    if (formData.content) {
      const count = formData.content.trim().split(/\s+/).filter(word => word.length > 0).length;
      setWordCount(count);
    }
  }, [formData.content]);

  const truncateText = (text: string, maxLength: number) => {
    return text.length > maxLength ? text.substring(0, maxLength) : text;
  };

  const handleInputChange = (field: keyof JournalEntry, value: any) => {
    // Apply character limits
    if (field === 'title' && typeof value === 'string') {
      value = truncateText(value, MAX_TITLE_LENGTH);
    } else if (field === 'content' && typeof value === 'string') {
      value = truncateText(value, MAX_CONTENT_LENGTH);
    }

    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleAddTag = () => {
    const trimmedTag = newTag.trim();
    const truncatedTag = truncateText(trimmedTag, MAX_TAG_LENGTH);
    
    if (truncatedTag && 
        !formData.tags?.includes(truncatedTag) && 
        (formData.tags?.length || 0) < MAX_TAGS) {
      const updatedTags = [...(formData.tags || []), truncatedTag];
      handleInputChange('tags', updatedTags);
      setNewTag('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    const updatedTags = formData.tags?.filter(tag => tag !== tagToRemove) || [];
    handleInputChange('tags', updatedTags);
  };

  const handleSave = async () => {
    if (!formData.title?.trim() || !formData.content?.trim()) {
      return;
    }

    setIsSaving(true);
    
    try {
      const entryData = {
        ...formData,
        title: formData.title.trim(),
        content: formData.content.trim(),
        tags: formData.tags || [],
        wordCount: wordCount,
        date: formData.date || new Date(),
        mood: formData.mood || 'neutral',
        energy: formData.energy || 3,
        isPrivate: formData.isPrivate || false
      } as JournalEntry;

      if (isEditMode && currentEntry) {
        updateEntry(currentEntry.id, entryData);
      } else {
        createEntry(entryData);
      }

      closeEntryModal();
    } catch (error) {
      console.error('Error saving journal entry:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = () => {
    if (currentEntry && window.confirm('Are you sure you want to delete this journal entry?')) {
      deleteEntry(currentEntry.id);
      closeEntryModal();
    }
  };

  const handleDuplicate = () => {
    if (currentEntry) {
      duplicateEntry(currentEntry.id);
      closeEntryModal();
    }
  };

  const selectedMood = moodOptions.find(mood => mood.value === formData.mood);

  return (
    <Dialog open={isEntryModalOpen} onOpenChange={closeEntryModal}>
      <DialogContent className="glassmorphism-card border-0 bg-card text-card-foreground max-w-4xl max-h-[90vh] p-0">
        <DialogHeader className="px-6 py-4 border-b border-border">
          <div className="flex items-center justify-between">
            <DialogTitle className="text-xl">
              {isEditMode ? 'Edit Journal Entry' : 'New Journal Entry'}
            </DialogTitle>
            <div className="flex items-center space-x-2">
              {isEditMode && currentEntry && (
                <>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleDuplicate}
                    className="text-muted-foreground hover:text-foreground"
                  >
                    <Copy className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleDelete}
                    className="text-destructive hover:text-destructive/80"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </>
              )}
              <Button variant="ghost" size="sm" onClick={closeEntryModal}>
                <X className="w-4 h-4" />
              </Button>
            </div>
          </div>
          <DialogDescription className="text-muted-foreground text-sm">
            {isEditMode 
              ? 'Edit your journal entry with mood tracking, voice-to-text, and pillar association'
              : 'Create a new journal entry with mood tracking, voice-to-text, and pillar association'
            }
          </DialogDescription>
        </DialogHeader>

        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Title and Date */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="md:col-span-2">
              <LimitedInput
                label="Title"
                value={formData.title || ''}
                onValueChange={(value) => handleInputChange('title', value)}
                placeholder="Give your entry a title..."
                maxLength={MAX_TITLE_LENGTH}
                showProgress={true}
                showIcon={true}
                helperText="Create a meaningful title for your journal entry"
              />
            </div>
            <div>
              <Label htmlFor="date">Date</Label>
              <Input
                id="date"
                type="date"
                value={formData.date ? new Date(formData.date).toISOString().split('T')[0] : ''}
                onChange={(e) => handleInputChange('date', new Date(e.target.value))}
                className="glassmorphism-card border-0 bg-input"
              />
            </div>
          </div>

          {/* Mood and Energy */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <Label>Mood</Label>
              <Select 
                value={formData.mood || 'neutral'} 
                onValueChange={(value) => handleInputChange('mood', value)}
              >
                <SelectTrigger className="glassmorphism-card border-0 bg-input">
                  <SelectValue>
                    {selectedMood && (
                      <div className="flex items-center space-x-2">
                        <span>{selectedMood.emoji}</span>
                        <span>{selectedMood.label}</span>
                      </div>
                    )}
                  </SelectValue>
                </SelectTrigger>
                <SelectContent className="glassmorphism-card border-0 bg-card">
                  {moodOptions.map((mood) => (
                    <SelectItem key={mood.value} value={mood.value}>
                      <div className="flex items-center space-x-2">
                        <span>{mood.emoji}</span>
                        <span className={mood.color}>{mood.label}</span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label>Energy Level</Label>
              <div className="space-y-3">
                <Slider
                  value={[formData.energy || 3]}
                  onValueChange={(value) => handleInputChange('energy', value[0])}
                  max={5}
                  min={1}
                  step={1}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-muted-foreground">
                  {energyLabels.map((label, index) => (
                    <span key={index} className={formData.energy === index + 1 ? 'text-primary' : ''}>
                      {label}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Content */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <Label htmlFor="content">
                Content ({(formData.content || '').length}/{MAX_CONTENT_LENGTH})
              </Label>
              <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                <div className="flex items-center space-x-1">
                  <span>{wordCount}</span>
                  <span>words</span>
                </div>
                <div className="flex items-center space-x-2">
                  {formData.isPrivate ? <Lock className="w-4 h-4" /> : <Unlock className="w-4 h-4" />}
                  <Switch
                    checked={formData.isPrivate || false}
                    onCheckedChange={(checked) => handleInputChange('isPrivate', checked)}
                  />
                  <span>Private</span>
                </div>
              </div>
            </div>
            <VoiceToText
              onTextChange={(text) => handleInputChange('content', text)}
              initialText={formData.content || ''}
              placeholder="Write your journal entry here or use voice recording..."
              disabled={isSaving}
            />
          </div>

          {/* Tags */}
          <div>
            <Label>Tags ({(formData.tags?.length || 0)}/{MAX_TAGS})</Label>
            <div className="space-y-3">
              <div className="flex flex-wrap gap-2">
                {formData.tags?.map((tag, index) => (
                  <Badge
                    key={index}
                    variant="secondary"
                    className="glassmorphism-card bg-primary/10 text-primary border-primary/20"
                  >
                    {tag}
                    <button
                      onClick={() => handleRemoveTag(tag)}
                      className="ml-2 text-primary/70 hover:text-primary"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </Badge>
                ))}
              </div>
              <div className="flex space-x-2">
                <LimitedInput
                  value={newTag}
                  onValueChange={(value) => setNewTag(value)}
                  placeholder="Add a tag..."
                  maxLength={MAX_TAG_LENGTH}
                  showProgress={false}
                  showIcon={false}
                  onKeyPress={(e) => e.key === 'Enter' && handleAddTag()}
                  disabled={(formData.tags?.length || 0) >= MAX_TAGS}
                  className="flex-1 glassmorphism-card border-0 bg-input"
                />
                <Button 
                  onClick={handleAddTag} 
                  variant="outline" 
                  size="sm"
                  disabled={!newTag.trim() || (formData.tags?.length || 0) >= MAX_TAGS}
                  className="glassmorphism-card border-0"
                >
                  <Tag className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>

          {/* Pillar Association */}
          {pillars.length > 0 && (
            <div>
              <Label>Associated Pillar (Optional)</Label>
              <Select 
                value={formData.pillarId || 'none'} 
                onValueChange={(value) => handleInputChange('pillarId', value === 'none' ? undefined : value)}
              >
                <SelectTrigger className="glassmorphism-card border-0 bg-input">
                  <SelectValue placeholder="Select a pillar to associate with this entry..." />
                </SelectTrigger>
                <SelectContent className="glassmorphism-card border-0 bg-card">
                  <SelectItem value="none">No pillar association</SelectItem>
                  {pillars.map((pillar) => (
                    <SelectItem key={pillar.id} value={pillar.id}>
                      <div className="flex items-center space-x-2">
                        <div 
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: pillar.color }}
                        />
                        <span>{pillar.name}</span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-border flex justify-between items-center">
          <div className="text-sm text-muted-foreground">
            {formData.createdAt && (
              <span>
                Created: {new Date(formData.createdAt).toLocaleString()}
              </span>
            )}
            {formData.updatedAt && formData.createdAt && formData.updatedAt !== formData.createdAt && (
              <span className="ml-4">
                Updated: {new Date(formData.updatedAt).toLocaleString()}
              </span>
            )}
          </div>
          <div className="flex space-x-3">
            <Button variant="outline" onClick={closeEntryModal}>
              Cancel
            </Button>
            <Button 
              onClick={handleSave} 
              disabled={!formData.title?.trim() || !formData.content?.trim() || isSaving}
              className="bg-primary text-primary-foreground hover:bg-primary/90"
            >
              <Save className="w-4 h-4 mr-2" />
              {isSaving ? 'Saving...' : (isEditMode ? 'Update Entry' : 'Save Entry')}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}