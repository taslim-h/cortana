// Background service worker for Chrome extension using offscreen document with iframe
// Compatible with your existing Firebase hosting authentication approach

const OFFSCREEN_DOCUMENT_PATH = 'offscreen.html';

// Track if offscreen document is being created
let creatingOffscreenDocument;

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "signIn") {
    handleSignIn().then(user => {
      if (user && !user.error) {
        // Store user data in Chrome storage
        chrome.storage.local.set({ user: user }, () => {
          sendResponse({ user: user });
        });
      } else {
        // Handle authentication error
        sendResponse({ error: user?.error || 'Authentication failed' });
      }
    }).catch(error => {
      console.error("Authentication error:", error);
      sendResponse({ error: error.message });
    });
    return true; // Keep the message channel open for async response
  } else if (request.action === "signOut") {
    handleSignOut().then(() => {
      sendResponse({ success: true });
    }).catch(error => {
      console.error("Sign out error:", error);
      sendResponse({ error: error.message });
    });
    return true;
  }
});

// Handle sign in using offscreen document with iframe
async function handleSignIn() {
  try {
    // Ensure offscreen document is available
    await setupOffscreenDocument();
    
    // Send message to offscreen document to handle auth
    return new Promise((resolve, reject) => {
      chrome.runtime.sendMessage(
        { action: "getAuth", target: "offscreen" },
        (response) => {
          if (chrome.runtime.lastError) {
            reject(chrome.runtime.lastError);
          } else if (response?.error) {
            resolve({ error: response.error });
          } else {
            resolve(response);
          }
        }
      );
    });
  } catch (error) {
    console.error("Error setting up authentication:", error);
    return { error: error.message };
  }
}

// Handle sign out
async function handleSignOut() {
  try {
    // Remove user data from storage
    await new Promise((resolve) => {
      chrome.storage.local.remove("user", resolve);
    });
    
    // Ensure offscreen document is available
    await setupOffscreenDocument();
    
    // Send sign out message to offscreen document
    return new Promise((resolve, reject) => {
      chrome.runtime.sendMessage(
        { action: "signOut", target: "offscreen" },
        (response) => {
          if (chrome.runtime.lastError) {
            // Even if there's an error, consider it successful since we cleared storage
            console.warn("Sign out message error:", chrome.runtime.lastError);
            resolve();
          } else {
            resolve(response);
          }
        }
      );
    });
  } catch (error) {
    console.error("Sign out error:", error);
    throw error;
  }
}

// Set up offscreen document for Firebase auth iframe
async function setupOffscreenDocument() {
  // Check if offscreen document already exists
  if (await hasOffscreenDocument()) {
    return;
  }

  // Create offscreen document if it doesn't exist
  if (creatingOffscreenDocument) {
    await creatingOffscreenDocument;
  } else {
    creatingOffscreenDocument = chrome.offscreen.createDocument({
      url: OFFSCREEN_DOCUMENT_PATH,
      reasons: [chrome.offscreen.Reason.DOM_SCRAPING],
      justification: "Firebase Authentication requires iframe access for secure authentication"
    });
    
    await creatingOffscreenDocument;
    creatingOffscreenDocument = null;
  }
}

// Check if offscreen document exists
async function hasOffscreenDocument() {
  try {
    const clients = await self.clients.matchAll();
    return clients.some(client => client.url.endsWith(OFFSCREEN_DOCUMENT_PATH));
  } catch (error) {
    console.error("Error checking offscreen document:", error);
    return false;
  }
}

// Extension installation handler
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    console.log('Meeting Assistant extension installed');
    // Optionally open welcome page
  } else if (details.reason === 'update') {
    console.log('Meeting Assistant extension updated to version', chrome.runtime.getManifest().version);
    
    // Clean up old offscreen documents on update
    chrome.offscreen.hasDocument().then(hasDoc => {
      if (hasDoc) {
        chrome.offscreen.closeDocument();
      }
    }).catch(() => {
      // Ignore errors
    });
  }
});

// Handle extension startup
chrome.runtime.onStartup.addListener(() => {
  console.log('Meeting Assistant extension started');
});

// Cleanup on suspend
chrome.runtime.onSuspend.addListener(() => {
  console.log('Meeting Assistant extension suspending');
  
  // Close offscreen document to save resources
  chrome.offscreen.hasDocument().then(hasDoc => {
    if (hasDoc) {
      chrome.offscreen.closeDocument();
    }
  }).catch(() => {
    // Ignore errors
  });
});

// Listen for storage changes to sync auth state
chrome.storage.onChanged.addListener((changes, namespace) => {
  if (namespace === 'local' && changes.user) {
    // Auth state changed
    const isSignedIn = changes.user.newValue ? true : false;
    const wasSignedIn = changes.user.oldValue ? true : false;
    
    if (isSignedIn !== wasSignedIn) {
      console.log('Auth state changed:', isSignedIn ? 'signed in' : 'signed out');
      
      // Optionally notify other parts of the extension
      // This could be useful for content scripts or other components
    }
  }
});

// Handle messages from offscreen document (for debugging)
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'authStateChanged') {
    console.log('Auth state update from offscreen:', request.user ? 'signed in' : 'signed out');
    
    // Update stored user data if needed
    if (request.user) {
      chrome.storage.local.set({ user: request.user });
    } else {
      chrome.storage.local.remove('user');
    }
  }
});

// Periodic cleanup of offscreen document (optional)
// This can help prevent memory leaks in long-running sessions
setInterval(() => {
  chrome.offscreen.hasDocument().then(hasDoc => {
    if (hasDoc) {
      // Check if we actually need the offscreen document
      chrome.storage.local.get(['user'], (result) => {
        if (!result.user) {
          // No user signed in, we can close the offscreen document
          chrome.offscreen.closeDocument().catch(() => {
            // Ignore errors
          });
        }
      });
    }
  }).catch(() => {
    // Ignore errors
  });
}, 10 * 60 * 1000); // Every 10 minutes