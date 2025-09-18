import { useEffect } from 'react';
import { useAppStore } from '../stores/basicAppStore';

export function useThemeInitialization() {
  const appearanceSettings = useAppStore(state => state.appearanceSettings);

  useEffect(() => {
    // Apply appearance settings to document
    const root = document.documentElement;
    const body = document.body;
    
    // Always apply dark mode to both root and body
    root.classList.add('dark');
    body.classList.add('dark');
    
    // Set CSS custom properties
    root.style.setProperty('--font-size', `${appearanceSettings.fontSize}px`);
    
    // Apply class-based settings
    const classesToToggle = [
      { condition: !appearanceSettings.glassEffect, className: 'no-glass-effect' },
      { condition: appearanceSettings.reducedMotion, className: 'reduce-motion' },
      { condition: appearanceSettings.highContrast, className: 'high-contrast' },
      { condition: appearanceSettings.compactMode, className: 'compact-mode' },
    ];

    classesToToggle.forEach(({ condition, className }) => {
      if (condition) {
        root.classList.add(className);
      } else {
        root.classList.remove(className);
      }
    });
  }, [appearanceSettings]);

  return { appearanceSettings };
}