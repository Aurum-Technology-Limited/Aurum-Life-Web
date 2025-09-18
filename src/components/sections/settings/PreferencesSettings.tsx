import { useState, useEffect } from 'react';
import { Palette, Contrast, Zap } from 'lucide-react';
import { Button } from '../../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../ui/card';
import { Label } from '../../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../ui/select';
import { Separator } from '../../ui/separator';
import { RadioGroup, RadioGroupItem } from '../../ui/radio-group';
import { Switch } from '../../ui/switch';
import { Slider } from '../../ui/slider';
import { Badge } from '../../ui/badge';
import { motion } from 'motion/react';
import { useAppStore } from '../../../stores/basicAppStore';

export default function PreferencesSettings() {
  // Get appearance settings from store (dark mode only)
  const appearanceSettings = useAppStore(state => state.appearanceSettings);
  const updateAppearanceSettings = useAppStore(state => state.updateAppearanceSettings);
  const resetAppearanceSettings = useAppStore(state => state.resetAppearanceSettings);

  const [preferences, setPreferences] = useState({
    language: 'en',
    timezone: 'auto',
    dateFormat: 'MM/DD/YYYY',
    startOfWeek: 'monday',
    animations: 'normal'
  });

  // Theme functions removed - application is dark mode only

  // Apply custom CSS properties and other preferences
  useEffect(() => {
    const root = document.documentElement;
    root.style.setProperty('--font-size', `${appearanceSettings.fontSize}px`);
    
    // Apply glass effect toggle
    if (!appearanceSettings.glassEffect) {
      root.classList.add('no-glass-effect');
    } else {
      root.classList.remove('no-glass-effect');
    }

    // Apply reduced motion
    if (appearanceSettings.reducedMotion) {
      root.classList.add('reduce-motion');
    } else {
      root.classList.remove('reduce-motion');
    }

    // Apply high contrast
    if (appearanceSettings.highContrast) {
      root.classList.add('high-contrast');
    } else {
      root.classList.remove('high-contrast');
    }

    // Apply compact mode
    if (appearanceSettings.compactMode) {
      root.classList.add('compact-mode');
    } else {
      root.classList.remove('compact-mode');
    }
  }, [appearanceSettings]);



  // Theme options removed - application is dark mode only

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
      className="space-y-6"
    >
      {/* Theme Settings */}
      <Card className="glassmorphism-card border-0">
        <CardHeader>
          <CardTitle className="text-white flex items-center space-x-2">
            <Palette className="w-5 h-5 text-[#F4D03F]" />
            <span>Theme & Appearance</span>
          </CardTitle>
          <CardDescription className="text-[#B8BCC8]">
            Experience Aurum Life's signature dark gold theme and adjust display preferences
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Advanced Appearance Options */}
          <div className="space-y-4">
            <Label className="text-white text-base font-medium">Advanced Options</Label>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-[#B8BCC8] font-medium">Glass Effect</Label>
                  <p className="text-xs text-[#6B7280] mt-1">Enable glassmorphism styling</p>
                </div>
                <Switch
                  checked={appearanceSettings.glassEffect}
                  onCheckedChange={(checked) => 
                    updateAppearanceSettings({ glassEffect: checked })
                  }
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-[#B8BCC8] font-medium">Reduced Motion</Label>
                  <p className="text-xs text-[#6B7280] mt-1">Minimize animations</p>
                </div>
                <Switch
                  checked={appearanceSettings.reducedMotion}
                  onCheckedChange={(checked) => 
                    updateAppearanceSettings({ reducedMotion: checked })
                  }
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-[#B8BCC8] font-medium">High Contrast</Label>
                  <p className="text-xs text-[#6B7280] mt-1">Improve accessibility</p>
                </div>
                <Switch
                  checked={appearanceSettings.highContrast}
                  onCheckedChange={(checked) => 
                    updateAppearanceSettings({ highContrast: checked })
                  }
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-[#B8BCC8] font-medium">Compact Mode</Label>
                  <p className="text-xs text-[#6B7280] mt-1">Reduce spacing</p>
                </div>
                <Switch
                  checked={appearanceSettings.compactMode}
                  onCheckedChange={(checked) => 
                    updateAppearanceSettings({ compactMode: checked })
                  }
                />
              </div>
            </div>

            <div>
              <Label className="text-[#B8BCC8] font-medium">Font Size</Label>
              <p className="text-xs text-[#6B7280] mt-1 mb-3">Adjust text size throughout the app</p>
              <div className="flex items-center space-x-4">
                <span className="text-sm text-[#B8BCC8]">Small</span>
                <Slider
                  value={[appearanceSettings.fontSize]}
                  onValueChange={(value) => 
                    updateAppearanceSettings({ fontSize: value[0] })
                  }
                  max={20}
                  min={12}
                  step={1}
                  className="flex-1"
                />
                <span className="text-sm text-[#B8BCC8]">Large</span>
                <Badge variant="outline" className="border-[#F4D03F] text-[#F4D03F] min-w-[3rem]">
                  {appearanceSettings.fontSize}px
                </Badge>
              </div>
            </div>
          </div>

          <div className="flex justify-end">
            <Button 
              variant="outline" 
              className="border-[rgba(244,208,63,0.2)] text-[#F4D03F]"
              onClick={() => {
                resetAppearanceSettings();
              }}
            >
              <Zap className="w-4 h-4 mr-2" />
              Reset to Defaults
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Language & Region */}
      <Card className="glassmorphism-card border-0">
        <CardHeader>
          <CardTitle className="text-white">Language & Region</CardTitle>
          <CardDescription className="text-[#B8BCC8]">
            Set your language, timezone, and regional preferences
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <Label className="text-white font-medium">Language</Label>
              <Select value={preferences.language} onValueChange={(value) => setPreferences(prev => ({ ...prev, language: value }))}>
                <SelectTrigger className="mt-2 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                  <SelectItem value="en">🇺🇸 English</SelectItem>
                  <SelectItem value="es">🇪🇸 Español</SelectItem>
                  <SelectItem value="fr">🇫🇷 Français</SelectItem>
                  <SelectItem value="de">🇩🇪 Deutsch</SelectItem>
                  <SelectItem value="zh">🇨🇳 中文</SelectItem>
                  <SelectItem value="ja">🇯🇵 日本語</SelectItem>
                  <SelectItem value="pt">🇵🇹 Português</SelectItem>
                  <SelectItem value="ru">🇷🇺 Русский</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label className="text-white font-medium">Time Zone</Label>
              <Select value={preferences.timezone} onValueChange={(value) => setPreferences(prev => ({ ...prev, timezone: value }))}>
                <SelectTrigger className="mt-2 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                  <SelectItem value="auto">Auto-detect</SelectItem>
                  <SelectItem value="pst">Pacific Time (PST)</SelectItem>
                  <SelectItem value="est">Eastern Time (EST)</SelectItem>
                  <SelectItem value="cst">Central Time (CST)</SelectItem>
                  <SelectItem value="mst">Mountain Time (MST)</SelectItem>
                  <SelectItem value="utc">UTC</SelectItem>
                  <SelectItem value="gmt">GMT</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <Separator className="bg-[rgba(244,208,63,0.1)]" />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <Label className="text-white font-medium">Date Format</Label>
              <RadioGroup 
                value={preferences.dateFormat} 
                onValueChange={(value) => setPreferences(prev => ({ ...prev, dateFormat: value }))}
                className="mt-3"
              >
                <div className="space-y-2">
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="MM/DD/YYYY" id="us-date" />
                    <Label htmlFor="us-date" className="text-[#B8BCC8]">MM/DD/YYYY (US)</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="DD/MM/YYYY" id="eu-date" />
                    <Label htmlFor="eu-date" className="text-[#B8BCC8]">DD/MM/YYYY (EU)</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="YYYY-MM-DD" id="iso-date" />
                    <Label htmlFor="iso-date" className="text-[#B8BCC8]">YYYY-MM-DD (ISO)</Label>
                  </div>
                </div>
              </RadioGroup>
            </div>
            
            <div>
              <Label className="text-white font-medium">Start of Week</Label>
              <Select value={preferences.startOfWeek} onValueChange={(value) => setPreferences(prev => ({ ...prev, startOfWeek: value }))}>
                <SelectTrigger className="mt-2 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                  <SelectItem value="sunday">Sunday</SelectItem>
                  <SelectItem value="monday">Monday</SelectItem>
                  <SelectItem value="saturday">Saturday</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Display Settings */}
      <Card className="glassmorphism-card border-0">
        <CardHeader>
          <CardTitle className="text-white">Display Settings</CardTitle>
          <CardDescription className="text-[#B8BCC8]">
            Adjust content display and interface density
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <Label className="text-white font-medium">Dashboard Density</Label>
              <Select defaultValue="comfortable">
                <SelectTrigger className="mt-2 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                  <SelectItem value="compact">Compact</SelectItem>
                  <SelectItem value="comfortable">Comfortable</SelectItem>
                  <SelectItem value="spacious">Spacious</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label className="text-white font-medium">Animation Level</Label>
              <Select defaultValue="normal">
                <SelectTrigger className="mt-2 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                  <SelectItem value="none">No animations</SelectItem>
                  <SelectItem value="reduced">Reduced</SelectItem>
                  <SelectItem value="normal">Normal</SelectItem>
                  <SelectItem value="enhanced">Enhanced</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Save Actions */}
      <div className="flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-4">
        <Button 
          className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F] flex-1 sm:flex-none"
          onClick={() => {
            // Settings are auto-saved to localStorage via Zustand persist
            // Show feedback that settings are saved
            const event = new CustomEvent('show-toast', {
              detail: {
                title: 'Settings Saved',
                description: 'Your display preferences have been saved successfully.',
                type: 'success'
              }
            });
            window.dispatchEvent(event);
          }}
        >
          <Palette className="w-4 h-4 mr-2" />
          Save Settings
        </Button>
        <Button 
          variant="outline" 
          className="border-[rgba(244,208,63,0.2)] text-[#F4D03F] flex-1 sm:flex-none"
          onClick={() => {
            resetAppearanceSettings();
            setPreferences({
              language: 'en',
              timezone: 'auto',
              dateFormat: 'MM/DD/YYYY',
              startOfWeek: 'monday',
              animations: 'normal'
            });
            // Theme is always dark - no need to change
            
            const event = new CustomEvent('show-toast', {
              detail: {
                title: 'Settings Reset',
                description: 'All display settings have been reset to default values.',
                type: 'info'
              }
            });
            window.dispatchEvent(event);
          }}
        >
          <Zap className="w-4 h-4 mr-2" />
          Reset to Defaults
        </Button>
      </div>
    </motion.div>
  );
}