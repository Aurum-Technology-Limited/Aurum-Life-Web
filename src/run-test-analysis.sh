#!/bin/bash

# Aurum Life Test Suite Analysis Script
echo "🧪 AURUM LIFE - COMPREHENSIVE TEST SUITE ANALYSIS"
echo "=================================================="
echo ""

echo "📋 Test Files Structure:"
echo "========================"
find . -name "*.test.*" -type f | head -20
echo ""

echo "🔍 Test Configuration:"
echo "====================="
if [ -f "jest.config.js" ]; then
    echo "✅ Jest configuration found"
else
    echo "❌ Jest configuration missing"
fi

if [ -f "babel.config.js" ]; then
    echo "✅ Babel configuration found"
else
    echo "❌ Babel configuration missing"
fi

echo ""
echo "📊 Running Test Analysis..."
node test-summary-generator.js

echo ""
echo "🏁 Analysis Complete!"
echo "Check test-coverage-analysis.json for detailed report"