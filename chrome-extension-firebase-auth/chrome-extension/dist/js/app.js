// Main application entry point
class MeetingAssistantApp {
    constructor() {
        this.initialized = false;
    }

    async init() {
        if (this.initialized) return;

        try {
            // Wait for DOM to be ready
            if (document.readyState === 'loading') {
                await new Promise(resolve => {
                    document.addEventListener('DOMContentLoaded', resolve);
                });
            }

            // Initialize core components
            await this.initializeComponents();
            
            // Set up global error handling
            this.setupErrorHandling();
            
            // Mark as initialized
            this.initialized = true;
            
            console.log('Meeting Assistant App initialized successfully');
            
        } catch (error) {
            console.error('Failed to initialize app:', error);
            this.showError('Failed to initialize application. Please refresh and try again.');
        }
    }

    async initializeComponents() {
        // Get app container
        const appContainer = document.getElementById('app');
        if (!appContainer) {
            throw new Error('App container not found');
        }

        // Initialize auth manager
        await window.authManager.init();

        // Initialize router
        window.router.init(appContainer);

        // Start with appropriate page based on auth state
        if (window.authManager.isSignedIn()) {
            window.router.navigate('meetings');
        } else {
            window.router.navigate('signin');
        }
    }

    setupErrorHandling() {
        // Global error handler
        window.addEventListener('error', (event) => {
            console.error('Global error:', event.error);
            this.showError('An unexpected error occurred.');
        });

        // Unhandled promise rejection handler
        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled promise rejection:', event.reason);
            this.showError('An error occurred while processing your request.');
        });
    }

    showError(message) {
        // Create or update error notification
        let errorNotification = document.getElementById('errorNotification');
        
        if (!errorNotification) {
            errorNotification = document.createElement('div');
            errorNotification.id = 'errorNotification';
            errorNotification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background-color: var(--discord-red);
                color: var(--discord-white);
                padding: 12px 16px;
                border-radius: 4px;
                z-index: 1000;
                max-width: 300px;
                font-size: 14px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            `;
            document.body.appendChild(errorNotification);
        }

        errorNotification.textContent = message;
        errorNotification.style.display = 'block';

        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (errorNotification) {
                errorNotification.style.display = 'none';
            }
        }, 5000);
    }

    showSuccess(message) {
        // Create or update success notification
        let successNotification = document.getElementById('successNotification');
        
        if (!successNotification) {
            successNotification = document.createElement('div');
            successNotification.id = 'successNotification';
            successNotification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background-color: var(--discord-green);
                color: var(--discord-white);
                padding: 12px 16px;
                border-radius: 4px;
                z-index: 1000;
                max-width: 300px;
                font-size: 14px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            `;
            document.body.appendChild(successNotification);
        }

        successNotification.textContent = message;
        successNotification.style.display = 'block';

        // Auto-hide after 3 seconds
        setTimeout(() => {
            if (successNotification) {
                successNotification.style.display = 'none';
            }
        }, 3000);
    }

    // Utility method to check if extension is in development mode
    isDevelopment() {
        return !chrome.runtime.id || chrome.runtime.getManifest().key === undefined;
    }

    // Get extension version
    getVersion() {
        return chrome.runtime.getManifest().version;
    }

    // Log app info
    logAppInfo() {
        console.log('Meeting Assistant Extension');
        console.log('Version:', this.getVersion());
        console.log('Development mode:', this.isDevelopment());
        console.log('Auth state:', window.authManager.isSignedIn() ? 'Signed in' : 'Not signed in');
    }
}

// Global app instance
window.meetingApp = new MeetingAssistantApp();

// Initialize app when script loads
window.meetingApp.init().then(() => {
    window.meetingApp.logAppInfo();
});

// Hot reload support for development
if (window.meetingApp.isDevelopment()) {
    // Listen for extension reload during development
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
        if (message.action === 'reload') {
            window.location.reload();
        }
    });
}