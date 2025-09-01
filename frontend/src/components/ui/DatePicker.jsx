import React, { useState, useRef, useEffect } from 'react';
import { Calendar, ChevronDown } from 'lucide-react';
import { DayPicker } from 'react-day-picker';
import 'react-day-picker/dist/style.css';

const DatePicker = ({ 
  value, 
  onChange, 
  placeholder = "Select date", 
  className = "",
  disabled = false,
  minDate = null,
  maxDate = null 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const dropdownRef = useRef(null);
  const inputRef = useRef(null);

  // Format date for display (DD/MM/YYYY)
  const formatDate = (date) => {
    if (!date) return '';
    const d = new Date(date);
    const day = d.getDate().toString().padStart(2, '0');
    const month = (d.getMonth() + 1).toString().padStart(2, '0');
    const year = d.getFullYear();
    return `${day}/${month}/${year}`;
  };

  // Parse input value (DD/MM/YYYY)
  const parseDate = (dateString) => {
    const parts = dateString.split('/');
    if (parts.length !== 3) return null;
    
    const day = parseInt(parts[0], 10);
    const month = parseInt(parts[1], 10);
    const year = parseInt(parts[2], 10);
    
    if (isNaN(day) || isNaN(month) || isNaN(year)) return null;
    if (day < 1 || day > 31 || month < 1 || month > 12 || year < 1900 || year > 2100) return null;
    
    return new Date(year, month - 1, day);
  };

  // Update input value when value prop changes
  useEffect(() => {
    setInputValue(formatDate(value));
  }, [value]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleInputChange = (e) => {
    const newValue = e.target.value;
    setInputValue(newValue);
    
    // Try to parse the date as user types
    const parsedDate = parseDate(newValue);
    if (parsedDate && !isNaN(parsedDate.getTime())) {
      onChange(parsedDate);
    }
  };

  const handleInputBlur = () => {
    // Format the input value on blur
    const parsedDate = parseDate(inputValue);
    if (parsedDate && !isNaN(parsedDate.getTime())) {
      setInputValue(formatDate(parsedDate));
      onChange(parsedDate);
    } else if (inputValue && !parsedDate) {
      // Invalid format, clear the input
      setInputValue('');
      onChange(null);
    }
  };

  const handleCalendarSelect = (selectedDate) => {
    if (selectedDate) {
      onChange(selectedDate);
      setInputValue(formatDate(selectedDate));
      setIsOpen(false);
    }
  };

  const handleInputKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleInputBlur();
    } else if (e.key === 'Escape') {
      setIsOpen(false);
      inputRef.current?.blur();
    }
  };

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          onBlur={handleInputBlur}
          onKeyDown={handleInputKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 pr-20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
        />
        
        {/* Calendar Icon */}
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          disabled={disabled}
          className="absolute right-2 top-1/2 transform -translate-y-1/2 p-1 text-gray-400 hover:text-white transition-colors"
        >
          <Calendar className="h-5 w-5" />
        </button>
        
        {/* Format helper */}
        <div className="absolute right-8 top-1/2 transform -translate-y-1/2 text-xs text-gray-500 pointer-events-none">
          DD/MM/YYYY
        </div>
      </div>

      {/* Calendar Dropdown */}
      {isOpen && (
        <div className="absolute top-full left-0 mt-2 bg-gray-900 border border-gray-600 rounded-lg shadow-xl z-50 p-4">
          <DayPicker
            mode="single"
            selected={value}
            onSelect={handleCalendarSelect}
            disabled={[
              ...(minDate ? [{ before: minDate }] : []),
              ...(maxDate ? [{ after: maxDate }] : [])
            ]}
            classNames={{
              months: "text-white",
              month: "text-white", 
              caption: "text-white font-semibold mb-2",
              head_row: "border-b border-gray-700",
              head_cell: "text-gray-300 font-medium p-2 text-center",
              row: "border-0",
              cell: "text-center p-1",
              button: "w-8 h-8 rounded text-sm hover:bg-purple-600 focus:bg-purple-600 text-white transition-colors",
              button_reset: "p-0 m-0 border-0 bg-transparent",
              day: "w-8 h-8 flex items-center justify-center",
              day_today: "bg-purple-600 text-white rounded font-semibold",
              day_selected: "bg-purple-700 text-white rounded font-semibold",
              day_disabled: "text-gray-600 cursor-not-allowed",
              day_outside: "text-gray-600",
              day_range_middle: "bg-purple-500/30",
              nav: "flex items-center justify-between mb-2",
              nav_button: "w-8 h-8 rounded hover:bg-gray-700 flex items-center justify-center text-white",
              nav_button_previous: "order-1",
              nav_button_next: "order-3",
              caption_label: "order-2 flex-1 text-center"
            }}
          />
          
          <div className="mt-2 pt-2 border-t border-gray-700 text-center">
            <button
              type="button"
              onClick={() => setIsOpen(false)}
              className="px-4 py-2 text-sm bg-gray-700 hover:bg-gray-600 rounded transition-colors text-white"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default DatePicker;