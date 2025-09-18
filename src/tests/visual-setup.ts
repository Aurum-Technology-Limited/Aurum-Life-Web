/**
 * Visual Testing Setup
 * Configuration for jest-image-snapshot and visual regression tests
 */

import { configureToMatchImageSnapshot } from 'jest-image-snapshot';

// Configure image snapshot matching
const toMatchImageSnapshot = configureToMatchImageSnapshot({
  // Store snapshots in a dedicated directory
  customSnapshotsDir: `${process.cwd()}/tests/__image_snapshots__`,
  
  // Use a more descriptive naming convention
  customSnapshotIdentifier: ({ counter, currentTestName, testPath }) => {
    const testFile = testPath.split('/').pop()?.replace('.test.tsx', '') || 'unknown';
    return `${testFile}-${currentTestName.replace(/\s+/g, '-').toLowerCase()}-${counter}`;
  },
  
  // Allow some difference for cross-platform compatibility
  failureThreshold: 0.02,
  failureThresholdType: 'percent',
  
  // Generate diff images for debugging
  storeReceivedOnFailure: true,
  
  // Update snapshots in CI when SNAPSHOT_UPDATE is set
  updateSnapshot: process.env.SNAPSHOT_UPDATE === 'true',
  
  // Blur for consistent testing
  blur: 1,
  
  // Comparison options
  comparisonMethod: 'pixelmatch',
  
  // Generate diff images
  diffMode: true,
  diffDirection: 'horizontal',
});

// Extend Jest expect with image snapshot matcher
expect.extend({ toMatchImageSnapshot });

// Global setup for visual tests
beforeAll(() => {
  // Set deterministic random seed for consistent pseudo-random values
  Math.random = jest.fn(() => 0.5);
  
  // Mock requestAnimationFrame for consistent timing
  global.requestAnimationFrame = jest.fn(cb => setTimeout(cb, 16));
  global.cancelAnimationFrame = jest.fn();
  
  // Mock performance API for consistent timing
  Object.defineProperty(performance, 'now', {
    writable: true,
    value: jest.fn(() => 1000),
  });
});

// Clean up after visual tests
afterAll(() => {
  jest.restoreAllMocks();
});

// Set up consistent viewport for visual tests
Object.defineProperty(HTMLElement.prototype, 'offsetHeight', {
  configurable: true,
  value: 100,
});

Object.defineProperty(HTMLElement.prototype, 'offsetWidth', {
  configurable: true,
  value: 100,
});

// Mock getBoundingClientRect for consistent layout
Element.prototype.getBoundingClientRect = jest.fn(() => ({
  width: 120,
  height: 120,
  top: 0,
  left: 0,
  bottom: 120,
  right: 120,
  x: 0,
  y: 0,
  toJSON: jest.fn(),
}));

// Mock scrollTo for testing
Element.prototype.scrollTo = jest.fn();
window.scrollTo = jest.fn();

// Console setup for cleaner visual test output
const originalError = console.error;
beforeAll(() => {
  console.error = (...args) => {
    if (
      typeof args[0] === 'string' &&
      args[0].includes('Warning: ReactDOM.render is no longer supported')
    ) {
      return;
    }
    originalError.call(console, ...args);
  };
});

afterAll(() => {
  console.error = originalError;
});