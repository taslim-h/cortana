// Authentication management
class AuthManager {
    constructor() {
        this.user = null;
        this.firebaseToken = null;
        this.callbacks = [];
    }

    // Subscribe to auth state changes
    onAuthStateChanged(callback) {
        this.callbacks.push(callback);
    }

    // Notify all subscribers
    notifyAuthStateChanged() {
        this.callbacks.forEach(callback => callback(this.user));
    }

    // Initialize auth state from storage
    async init() {
        try {
            const result = await StorageManager.get(['user']);
            if (result.user) {
                this.user = result.user;
                this.firebaseToken = result.user.stsTokenManager?.accessToken;
                this.notifyAuthStateChanged();
            }
        } catch (error) {
            console.error('Error initializing auth:', error);
        }
    }

    // Sign in user
    async signIn() {
        try {
            const response = await new Promise((resolve) => {
                chrome.runtime.sendMessage({ action: "signIn" }, resolve);
            });

            if (response && response.user) {
                this.user = response.user;
                this.firebaseToken = response.user.stsTokenManager?.accessToken;
                this.notifyAuthStateChanged();
                return { success: true };
            } else {
                return { 
                    success: false, 
                    error: response?.error || 'Sign in failed' 
                };
            }
        } catch (error) {
            return { 
                success: false, 
                error: error.message 
            };
        }
    }

    // Sign out user
    async signOut() {
        try {
            await new Promise((resolve) => {
                chrome.runtime.sendMessage({ action: "signOut" }, resolve);
            });
            
            this.user = null;
            this.firebaseToken = null;
            this.notifyAuthStateChanged();
            return { success: true };
        } catch (error) {
            return { 
                success: false, 
                error: error.message 
            };
        }
    }

    // Get current user
    getCurrentUser() {
        return this.user;
    }

    // Get Firebase token
    getToken() {
        return this.firebaseToken;
    }

    // Check if user is signed in
    isSignedIn() {
        return this.user !== null && this.firebaseToken !== null;
    }

    // Get user display info
    getUserDisplayInfo() {
        if (!this.user) return null;
        
        return {
            email: this.user.email,
            displayName: this.user.displayName || this.user.email?.split('@')[0],
            photoURL: this.user.photoURL
        };
    }
}

// Export singleton instance
window.authManager = new AuthManager();