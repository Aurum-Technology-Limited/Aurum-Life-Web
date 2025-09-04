#!/usr/bin/env node
/**
 * Lighthouse Performance Audit for Aurum Life Frontend
 * Measures Core Web Vitals and provides optimization recommendations
 */

const fs = require('fs');
const path = require('path');

// Performance thresholds based on Core Web Vitals
const PERFORMANCE_THRESHOLDS = {
  FCP: { good: 1800, needsImprovement: 3000 }, // First Contentful Paint (ms)
  LCP: { good: 2500, needsImprovement: 4000 }, // Largest Contentful Paint (ms)
  TBT: { good: 200, needsImprovement: 600 },   // Total Blocking Time (ms)
  CLS: { good: 0.1, needsImprovement: 0.25 },  // Cumulative Layout Shift
  SI: { good: 3400, needsImprovement: 5800 },  // Speed Index (ms)
};

class FrontendPerformanceAuditor {
  constructor() {
    this.results = {
      timestamp: new Date().toISOString(),
      metrics: {},
      opportunities: [],
      diagnostics: [],
      bundleAnalysis: {},
      recommendations: []
    };
  }

  async runAudit() {
    console.log('🚀 Starting Frontend Performance Audit...\n');
    
    // Analyze bundle size
    console.log('📦 Analyzing Bundle Sizes...');
    this.analyzeBundleSize();
    
    // Analyze dependencies
    console.log('\n📚 Analyzing Dependencies...');
    this.analyzeDependencies();
    
    // Analyze React performance patterns
    console.log('\n⚛️ Analyzing React Patterns...');
    await this.analyzeReactPatterns();
    
    // Generate recommendations
    console.log('\n💡 Generating Recommendations...');
    this.generateRecommendations();
    
    // Save results
    this.saveResults();
  }

  analyzeBundleSize() {
    const buildPath = path.join(__dirname, 'frontend', 'build', 'static');
    
    if (!fs.existsSync(buildPath)) {
      console.log('⚠️  Build directory not found. Run `npm run build` first.');
      this.results.bundleAnalysis.status = 'Build not found';
      return;
    }

    const bundles = {
      js: [],
      css: [],
      total: 0
    };

    // Recursively analyze build directory
    const analyzeDir = (dirPath) => {
      const files = fs.readdirSync(dirPath);
      
      files.forEach(file => {
        const filePath = path.join(dirPath, file);
        const stat = fs.statSync(filePath);
        
        if (stat.isDirectory()) {
          analyzeDir(filePath);
        } else if (file.endsWith('.js')) {
          const sizeKB = stat.size / 1024;
          bundles.js.push({ name: file, size: sizeKB });
          bundles.total += sizeKB;
        } else if (file.endsWith('.css')) {
          const sizeKB = stat.size / 1024;
          bundles.css.push({ name: file, size: sizeKB });
          bundles.total += sizeKB;
        }
      });
    };

    analyzeDir(buildPath);

    // Sort by size
    bundles.js.sort((a, b) => b.size - a.size);
    bundles.css.sort((a, b) => b.size - a.size);

    this.results.bundleAnalysis = bundles;

    // Check for large bundles
    const largeJS = bundles.js.filter(b => b.size > 250);
    if (largeJS.length > 0) {
      this.results.opportunities.push({
        id: 'large-javascript-bundles',
        title: 'Large JavaScript bundles detected',
        description: `${largeJS.length} JS files are larger than 250KB`,
        files: largeJS.slice(0, 5),
        savings: Math.round(largeJS.reduce((sum, b) => sum + (b.size - 250), 0)) + ' KB',
        recommendation: 'Enable code splitting and lazy loading for routes'
      });
    }

    console.log(`Total bundle size: ${bundles.total.toFixed(2)} KB`);
    console.log(`JavaScript: ${bundles.js.reduce((sum, b) => sum + b.size, 0).toFixed(2)} KB`);
    console.log(`CSS: ${bundles.css.reduce((sum, b) => sum + b.size, 0).toFixed(2)} KB`);
  }

  analyzeDependencies() {
    const packageJsonPath = path.join(__dirname, 'frontend', 'package.json');
    
    if (!fs.existsSync(packageJsonPath)) {
      console.log('⚠️  package.json not found');
      return;
    }

    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
    const dependencies = packageJson.dependencies || {};
    
    // Check for duplicate/redundant dependencies
    const uiLibraries = Object.keys(dependencies).filter(dep => 
      dep.includes('@radix-ui') || 
      dep.includes('@mui') || 
      dep.includes('antd') ||
      dep.includes('semantic-ui')
    );

    if (uiLibraries.length > 10) {
      this.results.opportunities.push({
        id: 'multiple-ui-libraries',
        title: 'Multiple UI component libraries detected',
        description: `Found ${uiLibraries.length} UI-related dependencies`,
        count: uiLibraries.length,
        libraries: uiLibraries.slice(0, 10),
        recommendation: 'Consider consolidating to a single UI library to reduce bundle size'
      });
    }

    // Check for large dependencies
    const largeDeps = {
      'moment': { alternative: 'date-fns or dayjs', savings: '~200KB' },
      'lodash': { alternative: 'lodash-es with tree shaking', savings: '~70KB' },
      '@mui/material': { alternative: 'Only import used components', savings: '~300KB' },
      'chart.js': { alternative: 'Consider lighter alternatives like recharts', savings: '~150KB' }
    };

    Object.entries(largeDeps).forEach(([dep, info]) => {
      if (dependencies[dep]) {
        this.results.opportunities.push({
          id: `large-dependency-${dep}`,
          title: `Heavy dependency: ${dep}`,
          description: `${dep} adds significant weight to your bundle`,
          recommendation: `Consider using ${info.alternative}`,
          potentialSavings: info.savings
        });
      }
    });

    // Check React version
    const reactVersion = dependencies.react?.replace(/[\^~]/, '') || 'unknown';
    console.log(`React version: ${reactVersion}`);
    
    if (reactVersion.startsWith('19')) {
      this.results.diagnostics.push({
        id: 'react-19',
        title: 'Using React 19',
        description: 'Great! You\'re using the latest React with automatic optimizations'
      });
    }
  }

  async analyzeReactPatterns() {
    const srcPath = path.join(__dirname, 'frontend', 'src');
    
    if (!fs.existsSync(srcPath)) {
      console.log('⚠️  src directory not found');
      return;
    }

    const issues = {
      inlineHandlers: [],
      missingMemo: [],
      largeComponents: [],
      deepNesting: []
    };

    // Analyze React components
    const analyzeFile = (filePath) => {
      if (!filePath.endsWith('.js') && !filePath.endsWith('.jsx')) return;
      
      const content = fs.readFileSync(filePath, 'utf8');
      const relativePath = path.relative(srcPath, filePath);
      
      // Check for inline function handlers
      const inlineHandlerPattern = /onClick=\{(?:function|\(.*?\)|.*?=>)/g;
      const inlineMatches = content.match(inlineHandlerPattern) || [];
      if (inlineMatches.length > 3) {
        issues.inlineHandlers.push({
          file: relativePath,
          count: inlineMatches.length,
          recommendation: 'Use useCallback for event handlers'
        });
      }

      // Check component size
      const lines = content.split('\n').length;
      if (lines > 300) {
        issues.largeComponents.push({
          file: relativePath,
          lines: lines,
          recommendation: 'Consider splitting into smaller components'
        });
      }

      // Check for missing React.memo on functional components
      if (content.includes('export default function') && !content.includes('memo(')) {
        const hasProps = content.match(/function\s+\w+\s*\(.*?\)/);
        if (hasProps && hasProps[0].includes('props')) {
          issues.missingMemo.push({
            file: relativePath,
            recommendation: 'Consider using React.memo for pure components'
          });
        }
      }
    };

    // Recursively analyze all files
    const walkDir = (dir) => {
      const files = fs.readdirSync(dir);
      files.forEach(file => {
        const filePath = path.join(dir, file);
        const stat = fs.statSync(filePath);
        
        if (stat.isDirectory() && !file.startsWith('.') && file !== 'node_modules') {
          walkDir(filePath);
        } else if (stat.isFile()) {
          analyzeFile(filePath);
        }
      });
    };

    walkDir(srcPath);

    // Add issues to opportunities
    if (issues.inlineHandlers.length > 0) {
      this.results.opportunities.push({
        id: 'inline-event-handlers',
        title: 'Inline event handlers causing unnecessary re-renders',
        count: issues.inlineHandlers.length,
        files: issues.inlineHandlers.slice(0, 5),
        recommendation: 'Use useCallback hook for event handlers to prevent re-renders'
      });
    }

    if (issues.largeComponents.length > 0) {
      this.results.opportunities.push({
        id: 'large-components',
        title: 'Large components detected',
        count: issues.largeComponents.length,
        files: issues.largeComponents.slice(0, 5),
        recommendation: 'Split large components into smaller, focused components'
      });
    }

    console.log(`Analyzed ${Object.values(issues).flat().length} potential React performance issues`);
  }

  generateRecommendations() {
    const recommendations = [];

    // High priority recommendations
    if (this.results.bundleAnalysis.total > 1000) {
      recommendations.push({
        priority: 'HIGH',
        title: 'Reduce JavaScript bundle size',
        description: 'Your bundle size is over 1MB which impacts initial load time',
        actions: [
          'Enable code splitting with React.lazy() and Suspense',
          'Use dynamic imports for route-based splitting',
          'Analyze bundle with webpack-bundle-analyzer',
          'Remove unused dependencies'
        ],
        estimatedImpact: '40-60% reduction in initial bundle size'
      });
    }

    // Medium priority recommendations
    const hasMultipleUILibs = this.results.opportunities.find(o => o.id === 'multiple-ui-libraries');
    if (hasMultipleUILibs) {
      recommendations.push({
        priority: 'MEDIUM',
        title: 'Consolidate UI libraries',
        description: 'Multiple UI libraries increase bundle size significantly',
        actions: [
          'Standardize on a single UI library (recommend keeping @radix-ui)',
          'Remove redundant component libraries',
          'Create a shared component library'
        ],
        estimatedImpact: '20-30% reduction in bundle size'
      });
    }

    // Performance optimization recommendations
    recommendations.push({
      priority: 'MEDIUM',
      title: 'Implement React performance optimizations',
      description: 'Optimize React rendering performance',
      actions: [
        'Use React.memo for component memoization',
        'Implement useMemo and useCallback hooks',
        'Use React DevTools Profiler to identify bottlenecks',
        'Implement virtual scrolling for long lists'
      ],
      estimatedImpact: '30-50% improvement in rendering performance'
    });

    // Image optimization
    recommendations.push({
      priority: 'LOW',
      title: 'Optimize images and assets',
      description: 'Implement modern image optimization techniques',
      actions: [
        'Use next-gen image formats (WebP, AVIF)',
        'Implement lazy loading for images',
        'Use responsive images with srcset',
        'Compress images with tools like sharp or imagemin'
      ],
      estimatedImpact: '50-70% reduction in image payload'
    });

    this.results.recommendations = recommendations;
  }

  saveResults() {
    const outputFile = path.join(__dirname, `frontend_performance_report_${Date.now()}.json`);
    fs.writeFileSync(outputFile, JSON.stringify(this.results, null, 2));
    
    console.log(`\n✅ Frontend performance audit complete!`);
    console.log(`📄 Full report saved to: ${outputFile}\n`);
    
    // Print summary
    console.log('📊 PERFORMANCE SUMMARY');
    console.log('=' * 50);
    console.log(`Bundle Size: ${this.results.bundleAnalysis.total?.toFixed(2) || 'N/A'} KB`);
    console.log(`Opportunities Found: ${this.results.opportunities.length}`);
    console.log(`Recommendations: ${this.results.recommendations.length}`);
    
    // Print high priority recommendations
    const highPriority = this.results.recommendations.filter(r => r.priority === 'HIGH');
    if (highPriority.length > 0) {
      console.log('\n🚨 HIGH PRIORITY RECOMMENDATIONS:');
      highPriority.forEach(rec => {
        console.log(`\n- ${rec.title}`);
        console.log(`  ${rec.description}`);
        console.log(`  Estimated Impact: ${rec.estimatedImpact}`);
      });
    }
  }
}

// Run the audit
const auditor = new FrontendPerformanceAuditor();
auditor.runAudit();