import React, { useState } from 'react';
import SemanticSearch, { useSemanticSearch } from './SemanticSearch';
import { SearchIcon } from '@heroicons/react/outline';

const SemanticSearchTest = () => {
  const { isOpen, open: openSemanticSearch, close: closeSemanticSearch } = useSemanticSearch();
  const [testResults, setTestResults] = useState([]);

  const handleTestButtonClick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    console.log('🔍 Test: Semantic search button clicked');
    openSemanticSearch();
  };

  const handleKeyboardTest = () => {
    console.log('🔍 Test: Simulating keyboard shortcut (Ctrl+Shift+F)');
    // Simulate the keyboard event
    const event = new KeyboardEvent('keydown', {
      key: 'f',
      ctrlKey: true,
      shiftKey: true,
      bubbles: true
    });
    document.dispatchEvent(event);
  };

  const handleResultSelect = (result) => {
    console.log('🔍 Test: Result selected:', result);
    setTestResults(prev => [...prev, result]);
  };

  return (
    <div className="min-h-screen bg-[#0B0D14] p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-white mb-8">Semantic Search Test</h1>
        
        <div className="space-y-6">
          {/* Button Test */}
          <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
            <h2 className="text-xl font-semibold text-white mb-4">Button Click Test</h2>
            <button
              onClick={handleTestButtonClick}
              className="flex items-center px-4 py-3 text-sm font-medium rounded-lg bg-purple-600 hover:bg-purple-700 text-white transition-colors"
            >
              <SearchIcon className="h-5 w-5 mr-3" />
              Open Semantic Search (Button)
            </button>
            <p className="text-gray-400 text-sm mt-2">
              Click this button to test the semantic search modal opening via button click.
            </p>
          </div>

          {/* Keyboard Test */}
          <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
            <h2 className="text-xl font-semibold text-white mb-4">Keyboard Shortcut Test</h2>
            <button
              onClick={handleKeyboardTest}
              className="flex items-center px-4 py-3 text-sm font-medium rounded-lg bg-blue-600 hover:bg-blue-700 text-white transition-colors"
            >
              ⌨️ Simulate Ctrl+Shift+F
            </button>
            <p className="text-gray-400 text-sm mt-2">
              Click this button to simulate the keyboard shortcut, or press Ctrl+Shift+F directly.
            </p>
          </div>

          {/* Status Display */}
          <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
            <h2 className="text-xl font-semibold text-white mb-4">Status</h2>
            <div className="space-y-2">
              <p className="text-gray-300">
                Search Modal Status: 
                <span className={`ml-2 px-2 py-1 rounded text-sm font-medium ${
                  isOpen ? 'bg-green-600 text-white' : 'bg-red-600 text-white'
                }`}>
                  {isOpen ? 'OPEN' : 'CLOSED'}
                </span>
              </p>
              <p className="text-gray-300">
                Test Results: {testResults.length} selections made
              </p>
            </div>
          </div>

          {/* Console Instructions */}
          <div className="bg-yellow-900/20 border border-yellow-600/30 p-6 rounded-lg">
            <h2 className="text-xl font-semibold text-yellow-400 mb-4">Debug Instructions</h2>
            <div className="text-yellow-300 text-sm space-y-2">
              <p>• Open browser console to see debug messages</p>
              <p>• Test both button click and keyboard shortcut (Ctrl+Shift+F)</p>
              <p>• Watch the status indicator above</p>
              <p>• Both methods should open the search modal</p>
            </div>
          </div>
        </div>
      </div>

      {/* Semantic Search Modal - Global */}
      <SemanticSearch 
        isOpen={isOpen} 
        onClose={closeSemanticSearch} 
        onResultSelect={handleResultSelect} 
      />
    </div>
  );
};

export default SemanticSearchTest;