/**
 * Aurum Life PWA Service Worker
 * Handles offline caching, background sync, and push notifications
 */

const CACHE_NAME = 'aurum-life-v1';
const OFFLINE_DATA_CACHE = 'aurum-offline-data-v1';
const STATIC_CACHE = 'aurum-static-v1';

// Files to cache for offline use
const STATIC_FILES = [
  '/',
  '/App.tsx',
  '/styles/globals.css',
  '/icons/icon-192x192.png',
  '/icons/icon-512x512.png',
  '/icons/badge-72x72.png',
  '/manifest.json'
];

// Install event - cache static files
self.addEventListener('install', (event) => {
  console.log('Service Worker installing...');
  
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('Caching static files...');
        return cache.addAll(STATIC_FILES);
      })
      .then(() => {
        console.log('Static files cached successfully');
        // Skip waiting to activate immediately
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('Failed to cache static files:', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('Service Worker activating...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== CACHE_NAME && 
                cacheName !== OFFLINE_DATA_CACHE && 
                cacheName !== STATIC_CACHE) {
              console.log('Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        // Take control of all clients immediately
        return self.clients.claim();
      })
  );
});

// Fetch event - serve from cache when offline
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // Skip external requests
  if (url.origin !== location.origin) {
    return;
  }

  // Handle API requests
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(handleApiRequest(request));
    return;
  }

  // Handle static file requests
  event.respondWith(
    caches.match(request)
      .then((cachedResponse) => {
        if (cachedResponse) {
          return cachedResponse;
        }

        // If not in cache, fetch from network
        return fetch(request)
          .then((response) => {
            // Don't cache non-successful responses
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            // Clone the response
            const responseToCache = response.clone();

            // Add to cache
            caches.open(CACHE_NAME)
              .then((cache) => {
                cache.put(request, responseToCache);
              });

            return response;
          })
          .catch(() => {
            // Return offline page for navigation requests
            if (request.mode === 'navigate') {
              return caches.match('/');
            }
            
            // Return a basic offline response for other requests
            return new Response('Offline', { 
              status: 200, 
              statusText: 'Offline' 
            });
          });
      })
  );
});

// Handle API requests with offline fallback
async function handleApiRequest(request) {
  try {
    // Try network first
    const response = await fetch(request);
    
    // Cache successful responses
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    
    return response;
  } catch (error) {
    console.log('Network request failed, trying cache...');
    
    // Fallback to cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }

    // If no cache, return offline data
    return handleOfflineApiRequest(request);
  }
}

// Handle API requests when offline
async function handleOfflineApiRequest(request) {
  const url = new URL(request.url);
  
  try {
    // Try to get offline data from cache
    const offlineDataCache = await caches.open(OFFLINE_DATA_CACHE);
    const offlineDataResponse = await offlineDataCache.match('/offline-data');
    
    if (offlineDataResponse) {
      const offlineData = await offlineDataResponse.json();
      
      // Route to appropriate offline data
      if (url.pathname.includes('/pillars')) {
        return new Response(JSON.stringify(offlineData.pillars || []), {
          headers: { 'Content-Type': 'application/json' }
        });
      } else if (url.pathname.includes('/areas')) {
        return new Response(JSON.stringify(offlineData.areas || []), {
          headers: { 'Content-Type': 'application/json' }
        });
      } else if (url.pathname.includes('/projects')) {
        return new Response(JSON.stringify(offlineData.projects || []), {
          headers: { 'Content-Type': 'application/json' }
        });
      } else if (url.pathname.includes('/tasks')) {
        return new Response(JSON.stringify(offlineData.tasks || []), {
          headers: { 'Content-Type': 'application/json' }
        });
      } else if (url.pathname.includes('/journal')) {
        return new Response(JSON.stringify(offlineData.journalEntries || []), {
          headers: { 'Content-Type': 'application/json' }
        });
      }
    }
  } catch (error) {
    console.error('Error handling offline API request:', error);
  }
  
  // Default offline response
  return new Response(JSON.stringify({ 
    error: 'Offline - data not available',
    offline: true 
  }), {
    status: 503,
    statusText: 'Service Unavailable',
    headers: { 'Content-Type': 'application/json' }
  });
}

// Background sync event
self.addEventListener('sync', (event) => {
  console.log('Background sync event:', event.tag);
  
  if (event.tag === 'aurum-data-sync') {
    event.waitUntil(performBackgroundSync());
  }
});

// Perform background sync
async function performBackgroundSync() {
  try {
    console.log('Performing background sync...');
    
    // Get queued actions from IndexedDB or localStorage
    const queuedActions = await getQueuedActions();
    
    for (const action of queuedActions) {
      try {
        await processQueuedAction(action);
        await removeQueuedAction(action.id);
      } catch (error) {
        console.error('Failed to process queued action:', error);
      }
    }
    
    // Notify main thread
    const clients = await self.clients.matchAll();
    clients.forEach(client => {
      client.postMessage({
        type: 'BACKGROUND_SYNC',
        data: { success: true, processedCount: queuedActions.length }
      });
    });
    
  } catch (error) {
    console.error('Background sync failed:', error);
  }
}

// Get queued actions (simplified - would use IndexedDB in production)
async function getQueuedActions() {
  // This would typically read from IndexedDB
  // For now, return empty array
  return [];
}

// Process a queued action
async function processQueuedAction(action) {
  // Send the action to the server
  const response = await fetch('/api/sync', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(action)
  });
  
  if (!response.ok) {
    throw new Error(`Sync failed: ${response.status}`);
  }
}

// Remove queued action
async function removeQueuedAction(actionId) {
  // Remove from IndexedDB
  console.log('Removing queued action:', actionId);
}

// Push notification event
self.addEventListener('push', (event) => {
  console.log('Push event received:', event);
  
  let notificationData = {
    title: 'Aurum Life',
    body: 'You have a new notification',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/badge-72x72.png',
    tag: 'aurum-notification',
    requireInteraction: false
  };
  
  if (event.data) {
    try {
      notificationData = { ...notificationData, ...event.data.json() };
    } catch (error) {
      console.error('Error parsing push data:', error);
    }
  }
  
  event.waitUntil(
    self.registration.showNotification(notificationData.title, {
      body: notificationData.body,
      icon: notificationData.icon,
      badge: notificationData.badge,
      tag: notificationData.tag,
      requireInteraction: notificationData.requireInteraction,
      data: notificationData.data || {},
      actions: [
        {
          action: 'open',
          title: 'Open App'
        },
        {
          action: 'dismiss',
          title: 'Dismiss'
        }
      ]
    })
  );
});

// Notification click event
self.addEventListener('notificationclick', (event) => {
  console.log('Notification clicked:', event);
  
  event.notification.close();
  
  if (event.action === 'open' || !event.action) {
    // Open the app
    event.waitUntil(
      self.clients.matchAll({ type: 'window', includeUncontrolled: true })
        .then((clients) => {
          // Check if app is already open
          for (const client of clients) {
            if (client.url.includes(location.origin) && 'focus' in client) {
              return client.focus();
            }
          }
          
          // Open new window
          if (self.clients.openWindow) {
            return self.clients.openWindow('/');
          }
        })
    );
  }
  
  // Handle notification data
  if (event.notification.data) {
    // Send data to main thread
    self.clients.matchAll().then(clients => {
      clients.forEach(client => {
        client.postMessage({
          type: 'NOTIFICATION_CLICKED',
          data: event.notification.data
        });
      });
    });
  }
});

// Message event - handle messages from main thread
self.addEventListener('message', (event) => {
  const { type, data } = event.data;
  
  switch (type) {
    case 'SHOW_NOTIFICATION':
      self.registration.showNotification(data.title, data.options);
      break;
      
    case 'CACHE_OFFLINE_DATA':
      cacheOfflineData(data);
      break;
      
    case 'CLEAR_CACHE':
      clearAllCaches();
      break;
      
    case 'SKIP_WAITING':
      self.skipWaiting();
      break;
  }
});

// Cache offline data
async function cacheOfflineData(data) {
  try {
    const cache = await caches.open(OFFLINE_DATA_CACHE);
    await cache.put('/offline-data', new Response(JSON.stringify(data)));
    console.log('Offline data cached successfully');
  } catch (error) {
    console.error('Failed to cache offline data:', error);
  }
}

// Clear all caches
async function clearAllCaches() {
  try {
    const cacheNames = await caches.keys();
    await Promise.all(cacheNames.map(name => caches.delete(name)));
    console.log('All caches cleared');
  } catch (error) {
    console.error('Failed to clear caches:', error);
  }
}

// Periodic background sync (if supported)
self.addEventListener('periodicsync', (event) => {
  if (event.tag === 'aurum-periodic-sync') {
    event.waitUntil(performPeriodicSync());
  }
});

async function performPeriodicSync() {
  console.log('Performing periodic sync...');
  
  try {
    // Sync critical data
    await performBackgroundSync();
    
    // Update offline cache with fresh data
    const response = await fetch('/api/sync/offline-data');
    if (response.ok) {
      const freshData = await response.json();
      await cacheOfflineData(freshData);
    }
    
  } catch (error) {
    console.error('Periodic sync failed:', error);
  }
}

console.log('Aurum Life Service Worker loaded successfully');