import { useState } from 'react';
import { Label } from '../ui/label';
import { Input } from '../ui/input';
import { Button } from '../ui/button';
import { Palette, Check } from 'lucide-react';

interface ColorPickerProps {
  value: string;
  onChange: (color: string) => void;
  label: string;
  id?: string;
}

const predefinedColors = [
  '#10B981', // green
  '#3B82F6', // blue
  '#EC4899', // pink
  '#F59E0B', // amber
  '#8B5CF6', // violet
  '#06B6D4', // cyan
  '#EF4444', // red
  '#84CC16', // lime
  '#F97316', // orange
  '#6366F1', // indigo
  '#D946EF', // fuchsia
  '#059669', // emerald
  '#0EA5E9', // sky
  '#DC2626', // red-600
  '#7C3AED', // violet-600
  '#0891B2', // cyan-600
  '#65A30D', // lime-600
  '#EA580C', // orange-600
  '#4F46E5', // indigo-600
  '#C026D3', // fuchsia-600
  '#F4D03F', // gold (Aurum brand)
  '#F7DC6F', // light gold
  '#B8860B', // dark goldenrod
  '#FFD700', // gold
];

export default function ColorPicker({ value, onChange, label, id }: ColorPickerProps) {
  const [customColor, setCustomColor] = useState(value);
  const [showCustomInput, setShowCustomInput] = useState(false);

  const handleCustomColorChange = (newColor: string) => {
    setCustomColor(newColor);
    onChange(newColor);
  };

  const handlePredefinedColorSelect = (color: string) => {
    setCustomColor(color);
    onChange(color);
    setShowCustomInput(false);
  };

  return (
    <div className="space-y-3">
      <Label htmlFor={id}>{label}</Label>
      
      {/* Predefined Color Grid */}
      <div className="grid grid-cols-8 lg:grid-cols-12 gap-4">
        {predefinedColors.map(color => (
          <button
            key={color}
            type="button"
            className={`relative w-12 h-12 rounded-lg border-2 transition-all hover:scale-110 ${
              value === color 
                ? 'border-[#F4D03F] ring-2 ring-[rgba(244,208,63,0.3)]' 
                : 'border-[rgba(244,208,63,0.2)] hover:border-[rgba(244,208,63,0.4)]'
            }`}
            style={{ backgroundColor: color }}
            onClick={() => handlePredefinedColorSelect(color)}
            title={color}
          >
            {value === color && (
              <Check className="w-5 h-5 text-white absolute inset-0 m-auto drop-shadow-md" />
            )}
          </button>
        ))}
      </div>

      {/* Custom Color Input Toggle */}
      <div className="flex items-center space-x-2">
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={() => setShowCustomInput(!showCustomInput)}
          className="glassmorphism-panel border-0 text-[#B8BCC8] hover:text-white"
        >
          <Palette className="w-4 h-4 mr-2" />
          Custom Color
        </Button>
        
        {showCustomInput && (
          <div className="flex items-center space-x-2">
            <Input
              type="color"
              value={customColor}
              onChange={(e) => handleCustomColorChange(e.target.value)}
              className="w-12 h-8 p-0 border-0 rounded cursor-pointer"
            />
            <Input
              type="text"
              value={customColor}
              onChange={(e) => handleCustomColorChange(e.target.value)}
              placeholder="#000000"
              pattern="^#[0-9A-Fa-f]{6}$"
              className="w-24 glassmorphism-panel border-0 text-sm"
            />
          </div>
        )}
      </div>

      {/* Selected Color Preview */}
      <div className="flex items-center space-x-3 p-3 glassmorphism-panel rounded-lg">
        <div 
          className="w-6 h-6 rounded-full border border-[rgba(244,208,63,0.3)]"
          style={{ backgroundColor: value }}
        />
        <span className="text-sm text-[#B8BCC8]">Selected: {value}</span>
      </div>
    </div>
  );
}