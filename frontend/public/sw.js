// FarmyGo Service Worker - v1.0.0
const CACHE_NAME = 'farmygo-v1.0.0';
const API_CACHE_NAME = 'farmygo-api-v1.0.0';
const OFFLINE_URL = '/offline.html';

// Assets to cache for offline functionality
const STATIC_ASSETS = [
  '/',
  '/offline.html',
  '/manifest.json',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/icons/icon-192x192.png',
  '/icons/icon-512x512.png'
];

// API endpoints that should be cached
const API_CACHE_PATTERNS = [
  /\/api\/auth\/me/,
  /\/api\/security\/status/,
  /\/api\/companies/,
  /\/api\/couriers/,
  /\/api\/customers/,
  /\/api\/orders/
];

// Install event - cache static resources
self.addEventListener('install', (event) => {
  console.log('🔧 FarmyGo Service Worker installing...');
  
  event.waitUntil(
    (async () => {
      try {
        const cache = await caches.open(CACHE_NAME);
        console.log('📦 Caching static assets...');
        await cache.addAll(STATIC_ASSETS);
        console.log('✅ Static assets cached successfully');
        
        // Skip waiting to activate immediately
        await self.skipWaiting();
      } catch (error) {
        console.error('❌ Service Worker install failed:', error);
      }
    })()
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('🚀 FarmyGo Service Worker activating...');
  
  event.waitUntil(
    (async () => {
      try {
        // Take control of all clients immediately
        await self.clients.claim();
        
        // Clean up old caches
        const cacheNames = await caches.keys();
        const oldCaches = cacheNames.filter(name => 
          name !== CACHE_NAME && name !== API_CACHE_NAME
        );
        
        if (oldCaches.length > 0) {
          console.log('🗑️ Cleaning up old caches:', oldCaches);
          await Promise.all(
            oldCaches.map(cacheName => caches.delete(cacheName))
          );
        }
        
        console.log('✅ Service Worker activated successfully');
      } catch (error) {
        console.error('❌ Service Worker activation failed:', error);
      }
    })()
  );
});

// Fetch event - implement caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests and chrome-extension URLs
  if (request.method !== 'GET' || url.protocol === 'chrome-extension:') {
    return;
  }
  
  // Handle API requests
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(handleApiRequest(request));
    return;
  }
  
  // Handle navigation requests
  if (request.mode === 'navigate') {
    event.respondWith(handleNavigationRequest(request));
    return;
  }
  
  // Handle static assets
  event.respondWith(handleStaticRequest(request));
});

// API Request Handler - Network First with Cache Fallback
async function handleApiRequest(request) {
  const url = new URL(request.url);
  const shouldCache = API_CACHE_PATTERNS.some(pattern => pattern.test(url.pathname));
  
  try {
    // Always try network first for fresh data
    const networkResponse = await fetch(request.clone());
    
    // Cache successful responses for offline use
    if (shouldCache && networkResponse.ok) {
      const cache = await caches.open(API_CACHE_NAME);
      await cache.put(request.clone(), networkResponse.clone());
      console.log('💾 Cached API response:', url.pathname);
    }
    
    return networkResponse;
  } catch (error) {
    console.log('🌐 Network failed, trying cache for:', url.pathname);
    
    // Try to serve from cache when network fails
    if (shouldCache) {
      const cache = await caches.open(API_CACHE_NAME);
      const cachedResponse = await cache.match(request);
      
      if (cachedResponse) {
        console.log('📱 Serving from cache:', url.pathname);
        return cachedResponse;
      }
    }
    
    // Return offline response for API calls
    return new Response(
      JSON.stringify({ 
        error: 'Offline', 
        message: 'Dati non disponibili offline. Connettiti a internet per accedere.' 
      }),
      { 
        status: 503,
        statusText: 'Service Unavailable',
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Navigation Request Handler - Cache First for Shell
async function handleNavigationRequest(request) {
  try {
    // Try network first
    const networkResponse = await fetch(request);
    return networkResponse;
  } catch (error) {
    console.log('🌐 Navigation request failed, serving from cache');
    
    // Serve cached app shell or offline page
    const cache = await caches.open(CACHE_NAME);
    const cachedResponse = await cache.match('/') || await cache.match(OFFLINE_URL);
    
    return cachedResponse || new Response('Offline', { status: 503 });
  }
}

// Static Request Handler - Cache First
async function handleStaticRequest(request) {
  const cache = await caches.open(CACHE_NAME);
  const cachedResponse = await cache.match(request);
  
  if (cachedResponse) {
    // Serve from cache immediately
    return cachedResponse;
  }
  
  try {
    // Try network and cache the response
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      await cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('❌ Failed to fetch static asset:', request.url);
    return new Response('Asset not available offline', { status: 503 });
  }
}

// Background sync for offline actions
self.addEventListener('sync', (event) => {
  console.log('🔄 Background sync triggered:', event.tag);
  
  if (event.tag === 'order-sync') {
    event.waitUntil(syncOrders());
  } else if (event.tag === 'delivery-update-sync') {
    event.waitUntil(syncDeliveryUpdates());
  }
});

async function syncOrders() {
  try {
    console.log('📦 Syncing offline orders...');
    // Implementation for syncing offline created orders
    // This would sync data stored in IndexedDB when back online
  } catch (error) {
    console.error('❌ Order sync failed:', error);
  }
}

async function syncDeliveryUpdates() {
  try {
    console.log('🚚 Syncing delivery updates...');
    // Implementation for syncing offline delivery status updates
  } catch (error) {
    console.error('❌ Delivery sync failed:', error);
  }
}

// Push notification handler
self.addEventListener('push', (event) => {
  console.log('🔔 Push notification received');
  
  const options = {
    title: 'FarmyGo',
    body: 'Nuovo ordine di consegna ricevuto!',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/badge-72x72.png',
    tag: 'farmygo-notification',
    requireInteraction: true,
    actions: [
      {
        action: 'view',
        title: 'Visualizza Ordine',
        icon: '/icons/action-view.png'
      },
      {
        action: 'dismiss',
        title: 'Ignora',
        icon: '/icons/action-dismiss.png'
      }
    ],
    data: {
      url: '/orders',
      timestamp: Date.now()
    }
  };
  
  if (event.data) {
    try {
      const payload = event.data.json();
      options.title = payload.title || options.title;
      options.body = payload.body || options.body;
      options.data = { ...options.data, ...payload.data };
    } catch (error) {
      console.error('❌ Error parsing push payload:', error);
    }
  }
  
  event.waitUntil(
    self.registration.showNotification(options.title, options)
  );
});

// Notification click handler
self.addEventListener('notificationclick', (event) => {
  console.log('🔔 Notification clicked:', event.action);
  
  event.notification.close();
  
  if (event.action === 'view') {
    // Open the app to the orders page
    event.waitUntil(
      clients.openWindow(event.notification.data.url || '/orders')
    );
  } else if (event.action === 'dismiss') {
    // Just close the notification
    return;
  } else {
    // Default action - open the app
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

// Message handler for communication with main thread
self.addEventListener('message', (event) => {
  console.log('💬 Message received in SW:', event.data);
  
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  } else if (event.data && event.data.type === 'CACHE_URLS') {
    // Cache additional URLs requested by the app
    event.waitUntil(
      (async () => {
        const cache = await caches.open(CACHE_NAME);
        await cache.addAll(event.data.urls);
        console.log('✅ Additional URLs cached');
      })()
    );
  }
});

console.log('🎯 FarmyGo Service Worker loaded successfully!');