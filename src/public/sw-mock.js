/**
 * Mock Service Worker for Development Environments
 * Provides minimal service worker functionality without actual caching
 */

console.log('Mock Service Worker loaded - this is normal in development environments');

// Install event - minimal setup
self.addEventListener('install', (event) => {
  console.log('Mock Service Worker installing...');
  self.skipWaiting();
});

// Activate event - take control immediately
self.addEventListener('activate', (event) => {
  console.log('Mock Service Worker activating...');
  event.waitUntil(self.clients.claim());
});

// Fetch event - pass through all requests
self.addEventListener('fetch', (event) => {
  // Just pass through all requests without caching
  event.respondWith(fetch(event.request));
});

// Message event - handle messages from main thread
self.addEventListener('message', (event) => {
  const { type, data } = event.data;
  
  switch (type) {
    case 'SHOW_NOTIFICATION':
      console.log('Mock notification request:', data.title);
      // In a real environment, this would show the notification
      break;
      
    case 'CACHE_OFFLINE_DATA':
      console.log('Mock cache offline data request');
      break;
      
    case 'CLEAR_CACHE':
      console.log('Mock clear cache request');
      break;
      
    case 'SKIP_WAITING':
      self.skipWaiting();
      break;
  }
});

// Mock sync event
self.addEventListener('sync', (event) => {
  console.log('Mock background sync event:', event.tag);
});

// Mock push event
self.addEventListener('push', (event) => {
  console.log('Mock push event received');
});

console.log('Mock Service Worker setup complete');