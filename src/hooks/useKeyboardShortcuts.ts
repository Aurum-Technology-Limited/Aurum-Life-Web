import { useEffect } from 'react';
import { SectionType } from '../types/app';

interface KeyboardShortcut {
  key: string;
  ctrlKey?: boolean;
  altKey?: boolean;
  shiftKey?: boolean;
  action: () => void;
  description: string;
}

interface UseKeyboardShortcutsProps {
  onSectionChange: (section: SectionType) => void;
  onNotificationsOpen: () => void;
}

export function useKeyboardShortcuts({
  onSectionChange,
  onNotificationsOpen,
}: UseKeyboardShortcutsProps) {
  useEffect(() => {

    const shortcuts: KeyboardShortcut[] = [
      // Navigation shortcuts
      {
        key: '1',
        altKey: true,
        action: () => onSectionChange('dashboard'),
        description: 'Go to Dashboard',
      },
      {
        key: '2',
        altKey: true,
        action: () => onSectionChange('today'),
        description: 'Go to Today',
      },
      {
        key: '3',
        altKey: true,
        action: () => onSectionChange('pillars'),
        description: 'Go to Pillars',
      },
      {
        key: '4',
        altKey: true,
        action: () => onSectionChange('areas'),
        description: 'Go to Areas',
      },
      {
        key: '5',
        altKey: true,
        action: () => onSectionChange('projects'),
        description: 'Go to Projects',
      },
      {
        key: '6',
        altKey: true,
        action: () => onSectionChange('tasks'),
        description: 'Go to Tasks',
      },
      {
        key: '7',
        altKey: true,
        action: () => onSectionChange('journal'),
        description: 'Go to Journal',
      },
      // Utility shortcuts
      {
        key: 'n',
        ctrlKey: true,
        action: onNotificationsOpen,
        description: 'Open Notifications',
      },
      {
        key: '/',
        ctrlKey: true,
        action: () => {
          // Focus search input
          const searchInput = document.querySelector('input[placeholder*="Search"]') as HTMLInputElement;
          if (searchInput) {
            searchInput.focus();
          }
        },
        description: 'Focus Search',
      },
    ];

    const handleKeyDown = (event: KeyboardEvent) => {
      // Don't trigger shortcuts when typing in input fields
      if (
        event.target instanceof HTMLInputElement ||
        event.target instanceof HTMLTextAreaElement ||
        (event.target as HTMLElement)?.contentEditable === 'true'
      ) {
        return;
      }

      const matchingShortcut = shortcuts.find(
        (shortcut) =>
          shortcut.key.toLowerCase() === event.key.toLowerCase() &&
          !!shortcut.ctrlKey === (event.ctrlKey || event.metaKey) &&
          !!shortcut.altKey === event.altKey &&
          !!shortcut.shiftKey === event.shiftKey
      );

      if (matchingShortcut) {
        event.preventDefault();
        matchingShortcut.action();
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [onSectionChange, onNotificationsOpen]);

  // Return shortcuts for help modal or documentation
  return {
    shortcuts: [
      { combo: 'Alt + 1-7', description: 'Navigate to sections' },
      { combo: 'Ctrl + N', description: 'Open notifications' },
      { combo: 'Ctrl + /', description: 'Focus search' },
    ],
  };
}