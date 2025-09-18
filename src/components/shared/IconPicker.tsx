import { useState } from 'react';
import { Label } from '../ui/label';
import { Input } from '../ui/input';
import { ScrollArea } from '../ui/scroll-area';
import { Search } from 'lucide-react';
import * as LucideIcons from 'lucide-react';

interface IconPickerProps {
  value: string;
  onChange: (iconName: string) => void;
  label: string;
  id?: string;
}

// Comprehensive list of commonly used icons for all hierarchy levels
const allIcons = [
  // Core hierarchy icons
  'Target', 'Heart', 'Briefcase', 'Users', 'DollarSign', 'GraduationCap', 'Home', 'Activity',
  'Focus', 'Eye', 'Crosshair', 'Scope', 'Bullseye', 'CircleDot', 'MapPin', 'Navigation',
  'FolderKanban', 'Folder', 'Package', 'Box', 'Clipboard', 'FileText', 'Layers', 'Grid3x3',
  'CheckSquare', 'Square', 'Circle', 'CheckCircle', 'ListTodo', 'ClipboardList', 'FileCheck',
  
  // General purpose icons
  'Star', 'Flag', 'Bell', 'Lightning', 'Sun', 'Moon', 'Cloud', 'Umbrella', 'Coffee', 'Music',
  'Camera', 'Image', 'Video', 'Headphones', 'Phone', 'Mail', 'MessageCircle', 'Settings',
  'Tool', 'Wrench', 'Hammer', 'Paintbrush', 'Palette', 'Scissors', 'Ruler', 'Brain', 'Globe',
  'Shield', 'Zap', 'Crown', 'Compass', 'Mountain', 'Trophy', 'Rocket', 'Flame', 'Diamond',
  'Route', 'Signpost', 'Bookmark', 'Pin', 'Map', 'Radar', 'Telescope', 'ScanEye', 'Binoculars',
  'Layout', 'Kanban', 'Workflow', 'GitBranch', 'Puzzle', 'Blocks', 'Component', 'Archive',
  'Inbox', 'Package2', 'PackageOpen', 'CheckCheck', 'SquareCheck', 'CircleCheck', 'Check',
  'Plus', 'Minus', 'Play', 'Pause', 'Clock', 'Timer', 'Calendar', 'AlarmClock', 'Hourglass'
].filter((icon, index, array) => array.indexOf(icon) === index); // Remove duplicates

export default function IconPicker({ value, onChange, label, id }: IconPickerProps) {
  const [searchQuery, setSearchQuery] = useState('');

  const getIconsToShow = () => {
    let iconsToShow = allIcons;

    if (searchQuery) {
      iconsToShow = iconsToShow.filter(iconName =>
        iconName.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    return iconsToShow;
  };

  const renderIcon = (iconName: string) => {
    const IconComponent = (LucideIcons as any)[iconName];
    if (!IconComponent) return null;
    return <IconComponent className="w-5 h-5" />;
  };

  const getSelectedIcon = () => {
    if (!value) return null;
    const IconComponent = (LucideIcons as any)[value];
    if (!IconComponent) return null;
    return <IconComponent className="w-5 h-5" />;
  };

  return (
    <div className="space-y-3">
      <Label htmlFor={id}>{label}</Label>
      
      {/* Search Only */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-[#B8BCC8]" />
        <Input
          type="text"
          placeholder="Search icons..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10 glassmorphism-panel border-0"
        />
      </div>

      {/* Icon Grid */}
      <ScrollArea className="h-64 glassmorphism-panel rounded-lg p-4">
        <div className="grid grid-cols-8 lg:grid-cols-12 gap-4">
          {getIconsToShow().map(iconName => (
            <button
              key={iconName}
              type="button"
              className={`flex items-center justify-center w-14 h-14 rounded-lg border-2 transition-all hover:scale-105 ${
                value === iconName 
                  ? 'border-[#F4D03F] bg-[rgba(244,208,63,0.1)] text-[#F4D03F]' 
                  : 'border-[rgba(244,208,63,0.2)] hover:border-[rgba(244,208,63,0.4)] text-[#B8BCC8] hover:text-white'
              }`}
              onClick={() => onChange(iconName)}
              title={iconName}
            >
              {renderIcon(iconName)}
            </button>
          ))}
        </div>
        
        {getIconsToShow().length === 0 && (
          <div className="text-center py-8 text-[#B8BCC8]">
            No icons found matching "{searchQuery}"
          </div>
        )}
      </ScrollArea>

      {/* Selected Icon Preview */}
      <div className="flex items-center space-x-3 p-3 glassmorphism-panel rounded-lg">
        <div className="flex items-center justify-center w-8 h-8 rounded-lg border border-[rgba(244,208,63,0.3)] text-[#F4D03F]">
          {getSelectedIcon() || <div className="w-5 h-5 border border-dashed border-[#B8BCC8] rounded" />}
        </div>
        <span className="text-sm text-[#B8BCC8]">
          Selected: {value || 'None'}
        </span>
      </div>
    </div>
  );
}