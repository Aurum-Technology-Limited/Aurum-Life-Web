import React from 'react';
import { ArrowRight, ArrowDown } from 'lucide-react';

const HierarchyIntroduction = ({ onContinue }) => {
  return (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-4xl font-bold text-white mb-4">
          Understanding Aurum Life's System
        </h2>
        <p className="text-gray-400 text-xl max-w-3xl mx-auto leading-relaxed">
          Before we set up your personal system, let's understand the foundational hierarchy that makes Aurum Life so effective.
        </p>
      </div>

      {/* Hierarchy Visualization */}
      <div className="max-w-4xl mx-auto">
        <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-2xl p-8 border border-gray-700">
          <h3 className="text-2xl font-bold text-white mb-8 text-center">The Aurum Life Hierarchy</h3>
          
          <div className="space-y-6">
            {/* Pillars */}
            <div className="flex items-center space-x-6">
              <div className="w-20 h-20 bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl flex items-center justify-center flex-shrink-0">
                <span className="text-3xl">🏛️</span>
              </div>
              <div className="flex-1">
                <h4 className="text-2xl font-bold text-blue-400 mb-2">Pillars</h4>
                <p className="text-gray-300 text-lg leading-relaxed">
                  <strong>Your life-long goals and the ultimate 'Why' behind your work.</strong>
                  <br />
                  These are the fundamental areas of your life that matter most to you - like Health, Career, Relationships, or Personal Growth.
                </p>
              </div>
            </div>

            {/* Arrow Down */}
            <div className="flex justify-center">
              <ArrowDown className="w-8 h-8 text-gray-500" />
            </div>

            {/* Areas */}
            <div className="flex items-center space-x-6">
              <div className="w-20 h-20 bg-gradient-to-r from-green-500 to-green-600 rounded-xl flex items-center justify-center flex-shrink-0">
                <span className="text-3xl">🎯</span>
              </div>
              <div className="flex-1">
                <h4 className="text-2xl font-bold text-green-400 mb-2">Areas</h4>
                <p className="text-gray-300 text-lg leading-relaxed">
                  <strong>The means and systems by which you will achieve your goals (The 'How').</strong>
                  <br />
                  These are the ongoing responsibilities and systems within each pillar - like Fitness, Learning, or Networking.
                </p>
              </div>
            </div>

            {/* Arrow Down */}
            <div className="flex justify-center">
              <ArrowDown className="w-8 h-8 text-gray-500" />
            </div>

            {/* Projects */}
            <div className="flex items-center space-x-6">
              <div className="w-20 h-20 bg-gradient-to-r from-yellow-500 to-yellow-600 rounded-xl flex items-center justify-center flex-shrink-0">
                <span className="text-3xl">📁</span>
              </div>
              <div className="flex-1">
                <h4 className="text-2xl font-bold text-yellow-400 mb-2">Projects</h4>
                <p className="text-gray-300 text-lg leading-relaxed">
                  <strong>The defined, realistic objectives with timeframes to achieve your goals (The 'What').</strong>
                  <br />
                  These are specific, outcome-based initiatives with clear endpoints - like "Complete Marathon Training" or "Launch Side Business".
                </p>
              </div>
            </div>

            {/* Arrow Down */}
            <div className="flex justify-center">
              <ArrowDown className="w-8 h-8 text-gray-500" />
            </div>

            {/* Tasks */}
            <div className="flex items-center space-x-6">
              <div className="w-20 h-20 bg-gradient-to-r from-purple-500 to-purple-600 rounded-xl flex items-center justify-center flex-shrink-0">
                <span className="text-3xl">✅</span>
              </div>
              <div className="flex-1">
                <h4 className="text-2xl font-bold text-purple-400 mb-2">Tasks</h4>
                <p className="text-gray-300 text-lg leading-relaxed">
                  <strong>The individual, actionable steps to complete your projects.</strong>
                  <br />
                  These are the specific actions you can do right now - like "Research running shoes" or "Write business plan outline".
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Example Flow */}
      <div className="max-w-4xl mx-auto">
        <div className="bg-gradient-to-br from-yellow-900/20 to-orange-900/20 rounded-2xl p-8 border border-yellow-800/30">
          <h3 className="text-2xl font-bold text-white mb-6 text-center">Example: How It All Connects</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-center">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-500/20 rounded-xl flex items-center justify-center mx-auto mb-3">
                <span className="text-2xl">🏛️</span>
              </div>
              <h4 className="text-white font-semibold mb-2">Pillar</h4>
              <p className="text-gray-300 text-sm">"Health & Fitness"</p>
            </div>
            
            <div className="hidden md:flex justify-center">
              <ArrowRight className="w-6 h-6 text-gray-500" />
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-green-500/20 rounded-xl flex items-center justify-center mx-auto mb-3">
                <span className="text-2xl">🎯</span>
              </div>
              <h4 className="text-white font-semibold mb-2">Area</h4>
              <p className="text-gray-300 text-sm">"Cardiovascular Training"</p>
            </div>
            
            <div className="hidden md:flex justify-center">
              <ArrowRight className="w-6 h-6 text-gray-500" />
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-yellow-500/20 rounded-xl flex items-center justify-center mx-auto mb-3">
                <span className="text-2xl">📁</span>
              </div>
              <h4 className="text-white font-semibold mb-2">Project</h4>
              <p className="text-gray-300 text-sm">"Run 5K in Under 25 Minutes"</p>
            </div>
          </div>
          
          <div className="mt-6 pt-6 border-t border-yellow-800/30">
            <h5 className="text-white font-semibold mb-3 text-center">Sample Tasks:</h5>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div className="bg-purple-500/10 rounded-lg p-3 text-center">
                <span className="text-purple-400">✅ Buy running shoes</span>
              </div>
              <div className="bg-purple-500/10 rounded-lg p-3 text-center">
                <span className="text-purple-400">✅ Plan weekly schedule</span>
              </div>
              <div className="bg-purple-500/10 rounded-lg p-3 text-center">
                <span className="text-purple-400">✅ Complete first run</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Key Benefits */}
      <div className="max-w-4xl mx-auto">
        <div className="bg-gradient-to-br from-gray-800/30 to-gray-900/30 rounded-2xl p-8 border border-gray-700">
          <h3 className="text-2xl font-bold text-white mb-6 text-center">Why This Hierarchy Works</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center mx-auto mb-3">
                <span className="text-blue-400 text-xl">🎯</span>
              </div>
              <h4 className="text-white font-semibold mb-2">Clarity</h4>
              <p className="text-gray-400 text-sm">Every action connects to your bigger purpose</p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center mx-auto mb-3">
                <span className="text-green-400 text-xl">⚡</span>
              </div>
              <h4 className="text-white font-semibold mb-2">Focus</h4>
              <p className="text-gray-400 text-sm">Clear priorities prevent overwhelm</p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-yellow-500/20 rounded-lg flex items-center justify-center mx-auto mb-3">
                <span className="text-yellow-400 text-xl">📈</span>
              </div>
              <h4 className="text-white font-semibold mb-2">Progress</h4>
              <p className="text-gray-400 text-sm">Track meaningful advancement toward your goals</p>
            </div>
          </div>
        </div>
      </div>

      {/* Continue Button */}
      <div className="text-center">
        <button
          onClick={onContinue}
          className="flex items-center space-x-3 px-8 py-4 bg-gradient-to-r from-yellow-500 to-yellow-600 hover:from-yellow-600 hover:to-yellow-700 text-black font-bold text-lg rounded-lg transition-all duration-200 mx-auto shadow-lg"
        >
          <span>I Understand - Let's Build My System</span>
          <ArrowRight className="w-6 h-6" />
        </button>
      </div>
    </div>
  );
};

export default HierarchyIntroduction;