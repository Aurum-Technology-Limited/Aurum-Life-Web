import React, { useState, useRef, useEffect } from 'react';
import { Calendar, ChevronDown } from 'lucide-react';

const DatePicker = ({ 
  value, 
  onChange, 
  placeholder = "Select date", 
  className = "",
  disabled = false 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth());
  const [showYearDropdown, setShowYearDropdown] = useState(false);
  const dropdownRef = useRef(null);
  const inputRef = useRef(null);

  // Generate year options (1900 to current year)
  const currentYear = new Date().getFullYear();
  const yearOptions = Array.from(
    { length: currentYear - 1900 + 1 }, 
    (_, i) => 1900 + i
  ).reverse();

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

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
    if (day < 1 || day > 31 || month < 1 || month > 12 || year < 1900 || year > currentYear) return null;
    
    return new Date(year, month - 1, day);
  };

  // Update input value when value prop changes
  useEffect(() => {
    setInputValue(formatDate(value));
    if (value) {
      setSelectedYear(value.getFullYear());
      setSelectedMonth(value.getMonth());
    }
  }, [value]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
        setShowYearDropdown(false);
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
      setSelectedYear(parsedDate.getFullYear());
      setSelectedMonth(parsedDate.getMonth());
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

  const handleDayClick = (day) => {
    const selectedDate = new Date(selectedYear, selectedMonth, day);
    onChange(selectedDate);
    setInputValue(formatDate(selectedDate));
    setIsOpen(false);
  };

  const handleYearSelect = (year) => {
    setSelectedYear(year);
    setShowYearDropdown(false);
  };

  const handleMonthSelect = (month) => {
    setSelectedMonth(month);
  };

  // Generate calendar days
  const generateCalendarDays = () => {
    const firstDay = new Date(selectedYear, selectedMonth, 1);
    const lastDay = new Date(selectedYear, selectedMonth + 1, 0);
    const firstDayOfWeek = firstDay.getDay();
    const daysInMonth = lastDay.getDate();
    
    const days = [];
    
    // Add empty cells for days before month starts
    for (let i = 0; i < firstDayOfWeek; i++) {
      days.push(null);
    }
    
    // Add days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      days.push(day);
    }
    
    return days;
  };

  const calendarDays = generateCalendarDays();

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          onBlur={handleInputBlur}
          placeholder={placeholder}
          disabled={disabled}
          className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 pr-24 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
        />
        
        {/* Format helper */}
        <div className="absolute right-10 top-1/2 transform -translate-y-1/2 text-xs text-gray-500 pointer-events-none">
          📅
        </div>
        
        {/* Calendar Icon */}
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          disabled={disabled}
          className="absolute right-2 top-1/2 transform -translate-y-1/2 p-1.5 text-gray-400 hover:text-white transition-colors bg-gray-700 hover:bg-gray-600 rounded border border-gray-600"
        >
          <Calendar className="h-4 w-4" />
        </button>
      </div>

      {/* Calendar Dropdown */}
      {isOpen && (
        <div className="absolute top-full left-0 mt-2 bg-gray-900 border border-gray-600 rounded-lg shadow-xl z-50 p-4 min-w-[320px]">
          {/* Calendar Header with Year/Month Selection */}
          <div className="flex items-center justify-between mb-4 pb-2 border-b border-gray-700">
            <button
              type="button"
              onClick={() => setSelectedMonth(selectedMonth === 0 ? 11 : selectedMonth - 1)}
              className="p-1 hover:bg-gray-700 rounded text-white"
            >
              <ChevronDown className="h-4 w-4 rotate-90" />
            </button>
            
            <div className="flex items-center gap-2">
              {/* Month Selector */}
              <select
                value={selectedMonth}
                onChange={(e) => handleMonthSelect(parseInt(e.target.value))}
                className="bg-gray-700 border border-gray-600 rounded px-2 py-1 text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                {monthNames.map((month, index) => (
                  <option key={month} value={index}>
                    {month}
                  </option>
                ))}
              </select>
              
              {/* Year Selector */}
              <div className="relative">
                <button
                  type="button"
                  onClick={() => setShowYearDropdown(!showYearDropdown)}
                  className="flex items-center gap-1 px-2 py-1 bg-gray-700 hover:bg-gray-600 rounded text-white transition-colors text-sm"
                >
                  <span>{selectedYear}</span>
                  <ChevronDown className="h-3 w-3" />
                </button>
                
                {/* Year Dropdown */}
                {showYearDropdown && (
                  <div className="absolute top-full left-0 mt-1 bg-gray-800 border border-gray-600 rounded-lg shadow-lg z-20 max-h-48 overflow-y-auto w-20">
                    {yearOptions.map((year) => (
                      <button
                        key={year}
                        type="button"
                        onClick={() => handleYearSelect(year)}
                        className={`w-full px-3 py-2 text-left hover:bg-gray-700 text-white transition-colors text-sm ${
                          year === selectedYear ? 'bg-purple-600' : ''
                        }`}
                      >
                        {year}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
            
            <button
              type="button"
              onClick={() => setSelectedMonth(selectedMonth === 11 ? 0 : selectedMonth + 1)}
              className="p-1 hover:bg-gray-700 rounded text-white"
            >
              <ChevronDown className="h-4 w-4 -rotate-90" />
            </button>
          </div>

          {/* Calendar Grid */}
          <div className="grid grid-cols-7 gap-1 mb-4">
            {/* Day headers */}
            {['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'].map((day) => (
              <div key={day} className="text-center text-gray-300 font-medium p-2 text-xs">
                {day}
              </div>
            ))}
            
            {/* Calendar days */}
            {calendarDays.map((day, index) => (
              <div key={index} className="text-center p-1">
                {day ? (
                  <button
                    type="button"
                    onClick={() => handleDayClick(day)}
                    className={`w-8 h-8 rounded text-sm transition-colors ${
                      value && 
                      value.getDate() === day && 
                      value.getMonth() === selectedMonth && 
                      value.getFullYear() === selectedYear
                        ? 'bg-purple-700 text-white font-semibold'
                        : 'text-white hover:bg-purple-600'
                    }`}
                  >
                    {day}
                  </button>
                ) : (
                  <div className="w-8 h-8"></div>
                )}
              </div>
            ))}
          </div>
          
          <div className="text-center">
            <button
              type="button"
              onClick={() => {
                setIsOpen(false);
                setShowYearDropdown(false);
              }}
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