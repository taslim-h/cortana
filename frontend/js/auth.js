// frontend/js/auth.js

// Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyBLuMniPPU0W2vRDf0bFWNl1PmpLzoYcao",
    authDomain: "cortana-4cc9a.firebaseapp.com",
    projectId: "cortana-4cc9a",
    storageBucket: "cortana-4cc9a.firebasestorage.app",
    messagingSenderId: "822500793872",
    appId: "1:822500793872:web:04e9634c3083b94becf495",
    measurementId: "G-P88XB84E17"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();

// Auth state management
let currentUser = null;

// Auth functions
const authManager = {
    // Initialize auth state listener
    init() {
        auth.onAuthStateChanged(async (user) => {
            if (user) {
                currentUser = user;
                const token = await user.getIdToken();
                localStorage.setItem('firebaseToken', token);

                // Verify token with backend
                try {
                    await utils.apiRequest('/auth/verify', {
                        method: 'POST',
                        body: JSON.stringify({ token })
                    });

                    this.showApp();
                    meetingManager.loadMeetings();
                    calendarManager.checkIntegration();
                } catch (error) {
                    console.error('Token verification failed:', error);
                    this.signOut();
                }
            } else {
                currentUser = null;
                localStorage.removeItem('firebaseToken');
                this.showAuth();
            }
        });

        // Set up auth persistence
        auth.setPersistence(firebase.auth.Auth.Persistence.LOCAL);

        // Bind auth events
        this.bindAuthEvents();
    },

    // Bind authentication events
    bindAuthEvents() {
        // Login button
        document.getElementById('login-btn').addEventListener('click', () => {
            this.signInWithEmail();
        });

        // Signup button
        document.getElementById('signup-btn').addEventListener('click', () => {
            this.signUpWithEmail();
        });

        // Google sign-in button
        document.getElementById('google-signin-btn').addEventListener('click', () => {
            this.signInWithGoogle();
        });

        // Logout button
        document.getElementById('logout-btn').addEventListener('click', () => {
            this.signOut();
        });

        // Enter key on password field
        document.getElementById('password-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.signInWithEmail();
            }
        });
    },

    // Sign in with email and password
    async signInWithEmail() {
        const email = document.getElementById('email-input').value;
        const password = document.getElementById('password-input').value;

        if (!email || !password) {
            utils.showError('Please enter email and password');
            return;
        }

        utils.showLoading();

        try {
            await auth.signInWithEmailAndPassword(email, password);
        } catch (error) {
            utils.showError(this.getErrorMessage(error));
        } finally {
            utils.hideLoading();
        }
    },

    // Sign up with email and password
    async signUpWithEmail() {
        const email = document.getElementById('email-input').value;
        const password = document.getElementById('password-input').value;

        if (!email || !password) {
            utils.showError('Please enter email and password');
            return;
        }

        if (password.length < 6) {
            utils.showError('Password must be at least 6 characters');
            return;
        }

        utils.showLoading();

        try {
            await auth.createUserWithEmailAndPassword(email, password);
        } catch (error) {
            utils.showError(this.getErrorMessage(error));
        } finally {
            utils.hideLoading();
        }
    },

    // Sign in with Google
    async signInWithGoogle() {
        const provider = new firebase.auth.GoogleAuthProvider();
        provider.addScope('email');
        provider.addScope('profile');

        utils.showLoading();

        try {
            await auth.signInWithPopup(provider);
        } catch (error) {
            utils.showError(this.getErrorMessage(error));
        } finally {
            utils.hideLoading();
        }
    },

    // Sign out
    async signOut() {
        utils.showLoading();

        try {
            await auth.signOut();
            localStorage.clear();
        } catch (error) {
            console.error('Sign out error:', error);
        } finally {
            utils.hideLoading();
        }
    },

    // Show app interface
    showApp() {
        document.getElementById('auth-container').style.display = 'none';
        document.getElementById('app-container').style.display = 'flex';
        document.getElementById('user-email').textContent = currentUser.email;
    },

    // Show auth interface
    showAuth() {
        document.getElementById('auth-container').style.display = 'flex';
        document.getElementById('app-container').style.display = 'none';
        document.getElementById('email-input').value = '';
        document.getElementById('password-input').value = '';
    },

    // Get user-friendly error message
    getErrorMessage(error) {
        switch (error.code) {
            case 'auth/email-already-in-use':
                return 'Email is already registered';
            case 'auth/invalid-email':
                return 'Invalid email address';
            case 'auth/operation-not-allowed':
                return 'Operation not allowed';
            case 'auth/weak-password':
                return 'Password is too weak';
            case 'auth/user-disabled':
                return 'User account is disabled';
            case 'auth/user-not-found':
                return 'User not found';
            case 'auth/wrong-password':
                return 'Incorrect password';
            case 'auth/popup-closed-by-user':
                return 'Sign-in popup was closed';
            default:
                return error.message || 'An error occurred';
        }
    },

    // Get current user
    getCurrentUser() {
        return currentUser;
    }
};