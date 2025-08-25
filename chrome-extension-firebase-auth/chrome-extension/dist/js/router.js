// // Simple router for managing different pages/views
// class Router {
//     constructor() {
//         this.currentPage = null;
//         this.appContainer = null;
//         this.pages = {
//             'signin': this.renderSignInPage.bind(this),
//             'meetings': this.renderMeetingsPage.bind(this),
//             'chat': this.renderChatPage.bind(this)
//         };
//         this.speechEnabled = false;
//     }

//     init(container) {
//         this.appContainer = container;
        
//         // Listen for auth state changes
//         window.authManager.onAuthStateChanged((user) => {
//             if (user) {
//                 this.navigate('meetings');
//             } else {
//                 this.navigate('signin');
//             }
//         });
//     }

//     navigate(page) {
//         if (this.pages[page]) {
//             this.currentPage = page;
//             this.render();
//         }
//     }

//     render() {
//         if (this.appContainer && this.pages[this.currentPage]) {
//             this.appContainer.innerHTML = this.pages[this.currentPage]();
//             this.bindEvents();
//         }
//     }

//     renderSignInPage() {
//         return `
//             <div class="sign-in-container">
//                 <div class="sign-in-icon">
//                     <i class="bi bi-person-circle"></i>
//                 </div>
//                 <h1 class="sign-in-title">Welcome to Meeting Assistant</h1>
//                 <p class="sign-in-subtitle">Sign in to access your meetings and chat with the AI assistant</p>
//                 <button id="signInBtn" class="btn-discord">
//                     <i class="bi bi-google"></i> Sign In with Google
//                 </button>
//                 <div id="authMessage" class="mt-3"></div>
//             </div>
//         `;
//     }

//     renderMeetingsPage() {
//         const userInfo = window.authManager.getUserDisplayInfo();
//         return `
//             <div class="app-header">
//                 <h1 class="app-title">Meeting Assistant</h1>
//                 <div class="d-flex align-items-center gap-2">
//                     <p class="user-info mb-0">Welcome, ${userInfo?.displayName || userInfo?.email}</p>
//                     <button id="signOutBtn" class="btn-discord-danger btn-icon">
//                         <i class="bi bi-box-arrow-right"></i>
//                     </button>
//                 </div>
//             </div>
            
//             <div class="nav-container">
//                 <div class="nav-tabs">
//                     <button class="nav-tab active" data-page="meetings">
//                         <i class="bi bi-calendar-event"></i>
//                         Meetings
//                     </button>
//                     <button class="nav-tab" data-page="chat">
//                         <i class="bi bi-robot"></i>
//                         Chat
//                     </button>
//                 </div>
//             </div>
            
//             <div class="main-content">
//                 <div id="loadingIndicator" class="loading">
//                     <div class="loading-spinner"></div>
//                     Loading meetings...
//                 </div>
//                 <div id="meetingsContainer" class="d-none"></div>
//                 <div id="errorContainer" class="d-none"></div>
//             </div>
//         `;
//     }

//    renderChatPage() {
//     const userInfo = window.authManager.getUserDisplayInfo();
//     return `
//         <div class="app-header">
//             <h1 class="app-title">Meeting Assistant</h1>
//             <div class="d-flex align-items-center gap-2">
//                 <p class="user-info mb-0">Welcome, ${userInfo?.displayName || userInfo?.email}</p>
//                 <button id="signOutBtn" class="btn-discord-danger btn-icon">
//                     <i class="bi bi-box-arrow-right"></i>
//                 </button>
//             </div>
//         </div>
        
//         <div class="nav-container">
//             <div class="nav-tabs">
//                 <button class="nav-tab" data-page="meetings">
//                     <i class="bi bi-calendar-event"></i>
//                     Meetings
//                 </button>
//                 <button class="nav-tab active" data-page="chat">
//                     <i class="bi bi-robot"></i>
//                     Chat
//                 </button>
//             </div>
//         </div>
        
//         <div class="main-content">
//             <div class="chat-container">
//                 <div class="meeting-selector">
//                     <select id="meetingSelect" class="form-select">
//                         <option value="">Select a meeting...</option>
//                     </select>
//                     <div class="speech-toggle">
//                         <input type="checkbox" id="speechToggle" class="toggle-checkbox">
//                         <label for="speechToggle" class="toggle-label">
//                             <span class="toggle-handle"></span>
//                             <span class="toggle-text">Speech Reply</span>
//                         </label>
//                     </div>
//                 </div>
                
//                 <div id="chatBox" class="chat-box">
//                     <div class="text-center" style="color: var(--discord-gray); padding: 20px;">
//                         Select a meeting to start chatting
//                     </div>
//                 </div>
                
//                 <div class="chat-input-container">
//                     <input 
//                         id="chatInput" 
//                         type="text" 
//                         class="chat-input" 
//                         placeholder="Ask something about the meeting..."
//                         disabled
//                     >
//                     <button id="sendBtn" class="btn-discord btn-icon" disabled>
//                         <i class="bi bi-send"></i>
//                     </button>
//                     <button id="voiceBtn" class="btn-discord-secondary btn-icon" disabled>
//                         <i class="bi bi-mic"></i>
//                     </button>
//                 </div>
//             </div>
//         </div>
//     `;
// }
//     bindEvents() {
//         // Sign in button
//         const signInBtn = document.getElementById('signInBtn');
//         if (signInBtn) {
//             signInBtn.addEventListener('click', this.handleSignIn.bind(this));
//         }

//         // Sign out button
//         const signOutBtn = document.getElementById('signOutBtn');
//         if (signOutBtn) {
//             signOutBtn.addEventListener('click', this.handleSignOut.bind(this));
//         }

//         // Navigation tabs
//         const navTabs = document.querySelectorAll('.nav-tab');
//         navTabs.forEach(tab => {
//             tab.addEventListener('click', () => {
//                 const page = tab.dataset.page;
//                 this.navigate(page);
//             });
//         });

//         // Page-specific event binding
//         if (this.currentPage === 'meetings') {
//             this.bindMeetingsEvents();
//         } else if (this.currentPage === 'chat') {
//             this.bindChatEvents();
//         }
//     }

//     async handleSignIn() {
//         const signInBtn = document.getElementById('signInBtn');
//         const authMessage = document.getElementById('authMessage');
        
//         if (signInBtn) {
//             signInBtn.disabled = true;
//             signInBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Signing in...';
//         }

//         const result = await window.authManager.signIn();
        
//         if (!result.success) {
//             if (authMessage) {
//                 authMessage.innerHTML = `<div class="error-message">${result.error}</div>`;
//             }
//             if (signInBtn) {
//                 signInBtn.disabled = false;
//                 signInBtn.innerHTML = '<i class="bi bi-google"></i> Sign In with Google';
//             }
//         }
//     }

//     async handleSignOut() {
//         await window.authManager.signOut();
//     }

//     bindMeetingsEvents() {
//         this.loadMeetings();
//     }

//     bindChatEvents() {
//         this.loadMeetingsForChat();
//         this.bindChatInputEvents();
//     }

//     async loadMeetings() {
//         const loadingIndicator = document.getElementById('loadingIndicator');
//         const meetingsContainer = document.getElementById('meetingsContainer');
//         const errorContainer = document.getElementById('errorContainer');

//         try {
//             const meetings = await window.apiManager.fetchMeetings();
            
//             if (loadingIndicator) loadingIndicator.classList.add('d-none');
            
//             if (meetings && meetings.length > 0) {
//                 meetingsContainer.innerHTML = meetings.map(meeting => this.renderMeetingCard(meeting)).join('');
//                 meetingsContainer.classList.remove('d-none');
//             } else {
//                 meetingsContainer.innerHTML = '<div class="text-center" style="color: var(--discord-gray); padding: 40px;">No meetings found</div>';
//                 meetingsContainer.classList.remove('d-none');
//             }
//         } catch (error) {
//             if (loadingIndicator) loadingIndicator.classList.add('d-none');
//             if (errorContainer) {
//                 errorContainer.innerHTML = `<div class="error-message">Error loading meetings: ${error.message}</div>`;
//                 errorContainer.classList.remove('d-none');
//             }
//         }
//     }

//     renderMeetingCard(meeting) {
//         const startTime = new Date(meeting.start_time).toLocaleString();
//         const endTime = new Date(meeting.end_time).toLocaleString();
//         const description = meeting.description || 'No description available';

//         return `
//             <div class="meeting-card" data-meeting-id="${meeting._id}">
//                 <div class="meeting-title">${meeting.title}</div>
//                 <div class="meeting-time">
//                     <i class="bi bi-clock"></i>
//                     ${startTime} - ${endTime}
//                 </div>
//                 <div class="meeting-description">${description}</div>
//             </div>
//         `;
//     }

//     async loadMeetingsForChat() {
//         try {
//             const meetings = await window.apiManager.fetchMeetings();
//             const meetingSelect = document.getElementById('meetingSelect');
            
//             if (meetingSelect && meetings) {
//                 meetingSelect.innerHTML = '<option value="">Select a meeting...</option>' +
//                     meetings.map(meeting => 
//                         `<option value="${meeting._id}">${meeting.title}</option>`
//                     ).join('');
                
//                 meetingSelect.addEventListener('change', this.handleMeetingSelection.bind(this));
//             }
//         } catch (error) {
//             console.error('Error loading meetings for chat:', error);
//         }
//     }

//     async handleMeetingSelection(event) {
//         const meetingId = event.target.value;
//         const chatInput = document.getElementById('chatInput');
//         const sendBtn = document.getElementById('sendBtn');
//         const voiceBtn = document.getElementById('voiceBtn');
//         const chatBox = document.getElementById('chatBox');

//         if (meetingId) {
//             // Enable chat controls
//             chatInput.disabled = false;
//             sendBtn.disabled = false;
//             voiceBtn.disabled = false;
//             chatInput.placeholder = 'Ask something about the meeting...';

//             // Load chat history
//             try {
//                 chatBox.innerHTML = '<div class="loading"><div class="loading-spinner"></div>Loading chat history...</div>';
                
//                 const history = await window.apiManager.loadChatHistory(meetingId);
                
//                 if (history.length > 0) {
//                     this.renderChatHistory(history);
//                 } else {
//                     chatBox.innerHTML = '<div class="text-center" style="color: var(--discord-gray); padding: 20px;">No previous conversations. Start by asking a question!</div>';
//                 }
                
//                 window.currentMeetingId = meetingId;
//             } catch (error) {
//                 chatBox.innerHTML = `<div class="error-message">Error loading chat history: ${error.message}</div>`;
//             }
//         } else {
//             // Disable chat controls
//             chatInput.disabled = true;
//             sendBtn.disabled = true;
//             voiceBtn.disabled = true;
//             chatInput.placeholder = 'Select a meeting first...';
//             chatBox.innerHTML = '<div class="text-center" style="color: var(--discord-gray); padding: 20px;">Select a meeting to start chatting</div>';
//             window.currentMeetingId = null;
//         }
//     }

//     bindChatInputEvents() {
//         const chatInput = document.getElementById('chatInput');
//         const sendBtn = document.getElementById('sendBtn');
//         const voiceBtn = document.getElementById('voiceBtn');

//         if (sendBtn) {
//             sendBtn.addEventListener('click', this.handleSendMessage.bind(this));
//         }

//         if (chatInput) {
//             chatInput.addEventListener('keypress', (e) => {
//                 if (e.key === 'Enter' && !e.shiftKey) {
//                     e.preventDefault();
//                     this.handleSendMessage();
//                 }
//             });
//         }

//         if (voiceBtn) {
//             voiceBtn.addEventListener('click', this.handleVoiceMessage.bind(this));
//         }
//     }

//     async handleSendMessage() {
//         const chatInput = document.getElementById('chatInput');
//         const message = chatInput.value.trim();
        
//         if (!message || !window.currentMeetingId) return;

//         // Clear input
//         chatInput.value = '';

//         // Add user message to chat
//         this.addMessageToChat('user', message);

//         try {
//             // Send message to API
//             const response = await window.apiManager.sendChatMessage(window.currentMeetingId, message);
            
//             // Add bot response to chat
//             this.addMessageToChat('bot', response);
            
//             // Store in local storage for persistence
//             await window.StorageManager.addChatMessage(window.currentMeetingId, 'user', message);
//             await window.StorageManager.addChatMessage(window.currentMeetingId, 'bot', response);
            
//         } catch (error) {
//             this.addMessageToChat('bot', 'Sorry, I encountered an error while processing your message.');
//             console.error('Error sending message:', error);
//         }
//     }

//     // async handleVoiceMessage() {
//     //     const voiceBtn = document.getElementById('voiceBtn');
        
//     //     if (!window.currentMeetingId) return;

//     //     try {
//     //         const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
//     //         const mediaRecorder = new MediaRecorder(stream);
//     //         const chunks = [];

//     //         // Update UI
//     //         voiceBtn.innerHTML = '<i class="bi bi-stop-circle"></i>';
//     //         voiceBtn.classList.add('recording');

//     //         mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
            
//     //         mediaRecorder.onstop = async () => {
//     //             // Reset UI
//     //             voiceBtn.innerHTML = '<i class="bi bi-mic"></i>';
//     //             voiceBtn.classList.remove('recording');
                
//     //             const blob = new Blob(chunks, { type: 'audio/webm' });
                
//     //             try {
//     //                 this.addMessageToChat('user', '[Voice Message]');
//     //                 const response = await window.apiManager.sendVoiceMessage(window.currentMeetingId, blob);
//     //                 this.addMessageToChat('bot', response);
//     //             } catch (error) {
//     //                 this.addMessageToChat('bot', 'Sorry, I had trouble processing your voice message.');
//     //                 console.error('Error processing voice:', error);
//     //             }
                
//     //             // Stop all tracks
//     //             stream.getTracks().forEach(track => track.stop());
//     //         };

//     //         mediaRecorder.start();
            
//     //         // Stop recording after 5 seconds
//     //         setTimeout(() => {
//     //             if (mediaRecorder.state === 'recording') {
//     //                 mediaRecorder.stop();
//     //             }
//     //         }, 5000);
            
//     //     } catch (error) {
//     //         console.error('Error accessing microphone:', error);
//     //         this.addMessageToChat('bot', 'Sorry, I could not access your microphone.');
//     //     }
//     // }


//     // ...existing code...

// // async handleVoiceMessage() {
// //     const voiceBtn = document.getElementById('voiceBtn');
// //     const chatInput = document.getElementById('chatInput');
// //     if (!window.currentMeetingId) return;

// //     // If already recording, do nothing
// //     if (voiceBtn.classList.contains('recording')) return;

// //     // Show stop (cross) button
// //     voiceBtn.innerHTML = '<i class="bi bi-x-circle"></i>';
// //     voiceBtn.classList.add('recording');

// //     // Setup SpeechRecognition
// //     const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
// //     if (!SpeechRecognition) {
// //         this.addMessageToChat('bot', 'Speech recognition is not supported in this browser.');
// //         voiceBtn.innerHTML = '<i class="bi bi-mic"></i>';
// //         voiceBtn.classList.remove('recording');
// //         return;
// //     }

// //     const recognition = new SpeechRecognition();
// //     recognition.lang = 'en-US';
// //     recognition.interimResults = false;
// //     recognition.maxAlternatives = 1;

// //     recognition.onresult = (event) => {
// //         const transcript = event.results[0][0].transcript;
// //         chatInput.value = transcript;
// //         // Optionally, send the message automatically
// //         this.handleSendMessage();
// //     };

// //     recognition.onerror = (event) => {
// //         this.addMessageToChat('bot', 'Sorry, I could not recognize your speech.');
// //         voiceBtn.innerHTML = '<i class="bi bi-mic"></i>';
// //         voiceBtn.classList.remove('recording');
// //     };

// //     recognition.onend = () => {
// //         voiceBtn.innerHTML = '<i class="bi bi-mic"></i>';
// //         voiceBtn.classList.remove('recording');
// //     };

// //     recognition.start();

// //     // Stop recording when cross button is clicked
// //     const stopHandler = () => {
// //         recognition.stop();
// //         voiceBtn.innerHTML = '<i class="bi bi-mic"></i>';
// //         voiceBtn.classList.remove('recording');
// //         voiceBtn.removeEventListener('click', stopHandler);
// //         voiceBtn.addEventListener('click', this.handleVoiceMessage.bind(this));
// //     };

// //     voiceBtn.removeEventListener('click', this.handleVoiceMessage.bind(this));
// //     voiceBtn.addEventListener('click', stopHandler);
// // }

// // ...existing code...

// async handleVoiceMessage() {
//     const voiceBtn = document.getElementById('voiceBtn');
//     const chatInput = document.getElementById('chatInput');
    
//     if (!window.currentMeetingId) {
//         this.addMessageToChat('bot', 'Please select a meeting first');
//         return;
//     }

//     // Check if already recording
//     if (voiceBtn.classList.contains('recording')) {
//         return;
//     }

//     // Check browser support
//     const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
//     if (!SpeechRecognition) {
//         this.addMessageToChat('bot', 'Your browser doesn\'t support speech recognition');
//         return;
//     }

//     // Update UI
//     voiceBtn.innerHTML = '<i class="bi bi-x-circle"></i>';
//     voiceBtn.classList.add('recording');
//     voiceBtn.title = 'Stop recording';

//     const recognition = new SpeechRecognition();
//     recognition.lang = 'en-US';
//     recognition.interimResults = true;  // Enable interim results
//     recognition.continuous = true;      // Keep listening until stopped
//     recognition.maxAlternatives = 1;

//     // Timeout variables
//     let speechTimeout;
//     const SPEECH_TIMEOUT_MS = 3000; // 3 seconds of silence before stopping

//     // Create a one-time click handler to stop recording
//     const stopRecording = () => {
//         clearTimeout(speechTimeout);
//         recognition.stop();
//         voiceBtn.innerHTML = '<i class="bi bi-mic"></i>';
//         voiceBtn.classList.remove('recording');
//         voiceBtn.title = 'Start voice input';
//         voiceBtn.removeEventListener('click', stopRecording);
//         voiceBtn.addEventListener('click', this.handleVoiceMessage.bind(this));
//     };

//     recognition.onresult = (event) => {
//         // Clear any existing timeout
//         clearTimeout(speechTimeout);
        
//         // Get the most recent result
//         const results = event.results;
//         const last = results[results.length - 1];
        
//         // If the result is final, process it
//         if (last.isFinal) {
//             const transcript = last[0].transcript;
//             chatInput.value = transcript;
//             stopRecording();
//             this.handleSendMessage();
//         } else {
//             // Set a timeout if speech pauses
//             speechTimeout = setTimeout(() => {
//                 if (voiceBtn.classList.contains('recording')) {
//                     const interimTranscript = Array.from(results)
//                         .map(result => result[0].transcript)
//                         .join('');
//                     if (interimTranscript.trim().length > 0) {
//                         chatInput.value = interimTranscript;
//                         this.handleSendMessage();
//                     }
//                     stopRecording();
//                 }
//             }, SPEECH_TIMEOUT_MS);
//         }
//     };

//     recognition.onerror = (event) => {
//         console.error('Speech recognition error', event.error);
//         this.addMessageToChat('bot', `Error: ${event.error}`);
//         stopRecording();
//     };

//     recognition.onend = () => {
//         if (voiceBtn.classList.contains('recording')) {
//             stopRecording();
//         }
//     };

//     // Request microphone permission
//     try {
//         await navigator.mediaDevices.getUserMedia({ audio: true });
//         recognition.start();
//         voiceBtn.removeEventListener('click', this.handleVoiceMessage.bind(this));
//         voiceBtn.addEventListener('click', stopRecording);
//     } catch (error) {
//         console.error('Microphone access denied', error);
//         this.addMessageToChat('bot', 'Microphone access was denied');
//         stopRecording();
//     }
// }
//     addMessageToChat(role, message) {
//         const chatBox = document.getElementById('chatBox');
//         if (!chatBox) return;

//         const messageDiv = document.createElement('div');
//         messageDiv.className = `chat-message ${role}`;
//         messageDiv.textContent = message;

//         chatBox.appendChild(messageDiv);
//         chatBox.scrollTop = chatBox.scrollHeight;
//     }

//     renderChatHistory(history) {
//         const chatBox = document.getElementById('chatBox');
//         if (!chatBox) return;

//         chatBox.innerHTML = '';
//         history.forEach(({ role, message }) => {
//             this.addMessageToChat(role, message);
//         });
//     }
// }

// // Export singleton instance
// window.router = new Router();

// Simple router for managing different pages/views
class Router {
    constructor() {
        this.currentPage = null;
        this.appContainer = null;
        this.pages = {
            'signin': this.renderSignInPage.bind(this),
            'meetings': this.renderMeetingsPage.bind(this),
            'chat': this.renderChatPage.bind(this)
        };
        this.speechEnabled = false;
    }

    init(container) {
        this.appContainer = container;
        
        // Initialize speech synthesis voices when they become available
        if ('speechSynthesis' in window) {
            window.speechSynthesis.onvoiceschanged = () => {
                // Voices are now loaded
            };
            
            // Some browsers need this to load voices
            if (window.speechSynthesis.getVoices().length === 0) {
                window.speechSynthesis.getVoices();
            }
        }
        
        // Listen for auth state changes
        window.authManager.onAuthStateChanged((user) => {
            if (user) {
                this.navigate('meetings');
            } else {
                this.navigate('signin');
            }
        });
    }

    navigate(page) {
        if (this.pages[page]) {
            this.currentPage = page;
            this.render();
        }
    }

    render() {
        if (this.appContainer && this.pages[this.currentPage]) {
            this.appContainer.innerHTML = this.pages[this.currentPage]();
            this.bindEvents();
        }
    }

    renderSignInPage() {
        return `
            <div class="sign-in-container">
                <div class="sign-in-icon">
                    <i class="bi bi-person-circle"></i>
                </div>
                <h1 class="sign-in-title">Welcome to Meeting Assistant</h1>
                <p class="sign-in-subtitle">Sign in to access your meetings and chat with the AI assistant</p>
                <button id="signInBtn" class="btn-discord">
                    <i class="bi bi-google"></i> Sign In with Google
                </button>
                <div id="authMessage" class="mt-3"></div>
            </div>
        `;
    }

    renderMeetingsPage() {
        const userInfo = window.authManager.getUserDisplayInfo();
        return `
            <div class="app-header">
                <h1 class="app-title">Meeting Assistant</h1>
                <div class="d-flex align-items-center gap-2">
                    <p class="user-info mb-0">Welcome, ${userInfo?.displayName || userInfo?.email}</p>
                    <button id="signOutBtn" class="btn-discord-danger btn-icon">
                        <i class="bi bi-box-arrow-right"></i>
                    </button>
                </div>
            </div>
            
            <div class="nav-container">
                <div class="nav-tabs">
                    <button class="nav-tab active" data-page="meetings">
                        <i class="bi bi-calendar-event"></i>
                        Meetings
                    </button>
                    <button class="nav-tab" data-page="chat">
                        <i class="bi bi-robot"></i>
                        Chat
                    </button>
                </div>
            </div>
            
            <div class="main-content">
                <div id="loadingIndicator" class="loading">
                    <div class="loading-spinner"></div>
                    Loading meetings...
                </div>
                <div id="meetingsContainer" class="d-none"></div>
                <div id="errorContainer" class="d-none"></div>
            </div>
        `;
    }

    renderChatPage() {
        const userInfo = window.authManager.getUserDisplayInfo();
        return `
            <div class="app-header">
                <h1 class="app-title">Meeting Assistant</h1>
                <div class="d-flex align-items-center gap-2">
                    <p class="user-info mb-0">Welcome, ${userInfo?.displayName || userInfo?.email}</p>
                    <button id="signOutBtn" class="btn-discord-danger btn-icon">
                        <i class="bi bi-box-arrow-right"></i>
                    </button>
                </div>
            </div>
            
            <div class="nav-container">
                <div class="nav-tabs">
                    <button class="nav-tab" data-page="meetings">
                        <i class="bi bi-calendar-event"></i>
                        Meetings
                    </button>
                    <button class="nav-tab active" data-page="chat">
                        <i class="bi bi-robot"></i>
                        Chat
                    </button>
                </div>
            </div>
            
            <div class="main-content">
                <div class="chat-container">
                    <div class="meeting-selector">
                        <select id="meetingSelect" class="form-select">
                            <option value="">Select a meeting...</option>
                        </select>
                        <div class="speech-toggle">
                            <input type="checkbox" id="speechToggle" class="toggle-checkbox">
                            <label for="speechToggle" class="toggle-label">
                                <span class="toggle-handle"></span>
                                <span class="toggle-text">Speech Reply</span>
                            </label>
                        </div>
                    </div>
                    
                    <div id="chatBox" class="chat-box">
                        <div class="text-center" style="color: var(--discord-gray); padding: 20px;">
                            Select a meeting to start chatting
                        </div>
                    </div>
                    
                    <div class="chat-input-container">
                        <input 
                            id="chatInput" 
                            type="text" 
                            class="chat-input" 
                            placeholder="Ask something about the meeting..."
                            disabled
                        >
                        <button id="sendBtn" class="btn-discord btn-icon" disabled>
                            <i class="bi bi-send"></i>
                        </button>
                        <button id="voiceBtn" class="btn-discord-secondary btn-icon" disabled>
                            <i class="bi bi-mic"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    bindEvents() {
        // Sign in button
        const signInBtn = document.getElementById('signInBtn');
        if (signInBtn) {
            signInBtn.addEventListener('click', this.handleSignIn.bind(this));
        }

        // Sign out button
        const signOutBtn = document.getElementById('signOutBtn');
        if (signOutBtn) {
            signOutBtn.addEventListener('click', this.handleSignOut.bind(this));
        }

        // Navigation tabs
        const navTabs = document.querySelectorAll('.nav-tab');
        navTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const page = tab.dataset.page;
                this.navigate(page);
            });
        });

        // Page-specific event binding
        if (this.currentPage === 'meetings') {
            this.bindMeetingsEvents();
        } else if (this.currentPage === 'chat') {
            this.bindChatEvents();
        }
    }

    async handleSignIn() {
        const signInBtn = document.getElementById('signInBtn');
        const authMessage = document.getElementById('authMessage');
        
        if (signInBtn) {
            signInBtn.disabled = true;
            signInBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Signing in...';
        }

        const result = await window.authManager.signIn();
        
        if (!result.success) {
            if (authMessage) {
                authMessage.innerHTML = `<div class="error-message">${result.error}</div>`;
            }
            if (signInBtn) {
                signInBtn.disabled = false;
                signInBtn.innerHTML = '<i class="bi bi-google"></i> Sign In with Google';
            }
        }
    }

    async handleSignOut() {
        await window.authManager.signOut();
    }

    bindMeetingsEvents() {
        this.loadMeetings();
    }

// In the bindChatEvents method, replace the StorageManager code with this:
bindChatEvents() {
    this.loadMeetingsForChat();
    this.bindChatInputEvents();
    
    // Bind speech toggle event
    const speechToggle = document.getElementById('speechToggle');
    if (speechToggle) {
        speechToggle.addEventListener('change', (e) => {
            this.speechEnabled = e.target.checked;
            
            // Store preference in storage
            try {
                if (window.StorageManager && typeof window.StorageManager.setItem === 'function') {
                    window.StorageManager.setItem('speechEnabled', this.speechEnabled);
                } else {
                    // Fallback to localStorage
                    localStorage.setItem('speechEnabled', this.speechEnabled);
                }
            } catch (error) {
                console.error('Error saving speech preference:', error);
            }
        });
        
        // Load saved preference
        try {
            let enabled = false;
            if (window.StorageManager && typeof window.StorageManager.getItem === 'function') {
                enabled =  window.StorageManager.getItem('speechEnabled');
            } else {
                // Fallback to localStorage
                enabled = localStorage.getItem('speechEnabled');
            }
            
            if (enabled !== null) {
                this.speechEnabled = enabled === 'true' || enabled === true;
                speechToggle.checked = this.speechEnabled;
            }
        } catch (error) {
            console.error('Error loading speech preference:', error);
        }
    }
}

    async loadMeetings() {
        const loadingIndicator = document.getElementById('loadingIndicator');
        const meetingsContainer = document.getElementById('meetingsContainer');
        const errorContainer = document.getElementById('errorContainer');

        try {
            const meetings = await window.apiManager.fetchMeetings();
            
            if (loadingIndicator) loadingIndicator.classList.add('d-none');
            
            if (meetings && meetings.length > 0) {
                meetingsContainer.innerHTML = meetings.map(meeting => this.renderMeetingCard(meeting)).join('');
                meetingsContainer.classList.remove('d-none');
            } else {
                meetingsContainer.innerHTML = '<div class="text-center" style="color: var(--discord-gray); padding: 40px;">No meetings found</div>';
                meetingsContainer.classList.remove('d-none');
            }
        } catch (error) {
            if (loadingIndicator) loadingIndicator.classList.add('d-none');
            if (errorContainer) {
                errorContainer.innerHTML = `<div class="error-message">Error loading meetings: ${error.message}</div>`;
                errorContainer.classList.remove('d-none');
            }
        }
    }

    renderMeetingCard(meeting) {
        const startTime = new Date(meeting.start_time).toLocaleString();
        const endTime = new Date(meeting.end_time).toLocaleString();
        const description = meeting.description || 'No description available';

        return `
            <div class="meeting-card" data-meeting-id="${meeting._id}">
                <div class="meeting-title">${meeting.title}</div>
                <div class="meeting-time">
                    <i class="bi bi-clock"></i>
                    ${startTime} - ${endTime}
                </div>
                <div class="meeting-description">${description}</div>
            </div>
        `;
    }

    async loadMeetingsForChat() {
        try {
            const meetings = await window.apiManager.fetchMeetings();
            const meetingSelect = document.getElementById('meetingSelect');
            
            if (meetingSelect && meetings) {
                meetingSelect.innerHTML = '<option value="">Select a meeting...</option>' +
                    meetings.map(meeting => 
                        `<option value="${meeting._id}">${meeting.title}</option>`
                    ).join('');
                
                meetingSelect.addEventListener('change', this.handleMeetingSelection.bind(this));
            }
        } catch (error) {
            console.error('Error loading meetings for chat:', error);
        }
    }

    async handleMeetingSelection(event) {
        const meetingId = event.target.value;
        const chatInput = document.getElementById('chatInput');
        const sendBtn = document.getElementById('sendBtn');
        const voiceBtn = document.getElementById('voiceBtn');
        const chatBox = document.getElementById('chatBox');

        if (meetingId) {
            // Enable chat controls
            chatInput.disabled = false;
            sendBtn.disabled = false;
            voiceBtn.disabled = false;
            chatInput.placeholder = 'Ask something about the meeting...';

            // Load chat history
            try {
                chatBox.innerHTML = '<div class="loading"><div class="loading-spinner"></div>Loading chat history...</div>';
                
                const history = await window.apiManager.loadChatHistory(meetingId);
                
                if (history.length > 0) {
                    this.renderChatHistory(history);
                } else {
                    chatBox.innerHTML = '<div class="text-center" style="color: var(--discord-gray); padding: 20px;">No previous conversations. Start by asking a question!</div>';
                }
                
                window.currentMeetingId = meetingId;
            } catch (error) {
                chatBox.innerHTML = `<div class="error-message">Error loading chat history: ${error.message}</div>`;
            }
        } else {
            // Disable chat controls
            chatInput.disabled = true;
            sendBtn.disabled = true;
            voiceBtn.disabled = true;
            chatInput.placeholder = 'Select a meeting first...';
            chatBox.innerHTML = '<div class="text-center" style="color: var(--discord-gray); padding: 20px;">Select a meeting to start chatting</div>';
            window.currentMeetingId = null;
        }
    }

    bindChatInputEvents() {
        const chatInput = document.getElementById('chatInput');
        const sendBtn = document.getElementById('sendBtn');
        const voiceBtn = document.getElementById('voiceBtn');

        if (sendBtn) {
            sendBtn.addEventListener('click', this.handleSendMessage.bind(this));
        }

        if (chatInput) {
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.handleSendMessage();
                }
            });
        }

        if (voiceBtn) {
            voiceBtn.addEventListener('click', this.handleVoiceMessage.bind(this));
        }
    }

    speak(text) {
        if (!this.speechEnabled) return;
        
        if ('speechSynthesis' in window) {
            // Cancel any ongoing speech
            window.speechSynthesis.cancel();
            
            const utterance = new SpeechSynthesisUtterance(text);
            
            // Set some reasonable defaults
            utterance.rate = 1;
            utterance.pitch = 1;
            utterance.volume = 1;
            
            // Try to get a nice voice
            const voices = window.speechSynthesis.getVoices();
            const preferredVoices = voices.filter(v => 
                v.lang.includes('en') && 
                (v.name.includes('Google') || v.name.includes('Natural'))
            );
            
            if (preferredVoices.length > 0) {
                utterance.voice = preferredVoices[0];
            }
            
            window.speechSynthesis.speak(utterance);
        }
    }

    async handleSendMessage() {
    const chatInput = document.getElementById('chatInput');
    const message = chatInput.value.trim();
    
    if (!message || !window.currentMeetingId) return;

    // Clear input
    chatInput.value = '';

    // Add user message to chat
    this.addMessageToChat('user', message);

    try {
        // Send message to API
        const response = await window.apiManager.sendChatMessage(window.currentMeetingId, message);
        
        // Add bot response to chat
        this.addMessageToChat('bot', response);
        
        // Speak the response if enabled
        this.speak(response);

        // Store in storage for persistence
        try {
            if (window.StorageManager && typeof window.StorageManager.addChatMessage === 'function') {
                await window.StorageManager.addChatMessage(window.currentMeetingId, 'user', message);
                await window.StorageManager.addChatMessage(window.currentMeetingId, 'bot', response);
            } else {
                // Fallback implementation or skip storage
                console.warn('StorageManager not available, chat history not persisted');
            }
        } catch (storageError) {
            console.error('Error storing chat message:', storageError);
        }

    } catch (error) {
        const errorMsg = 'Sorry, I encountered an error while processing your message.';
        this.addMessageToChat('bot', errorMsg);
        this.speak(errorMsg);
        console.error('Error sending message:', error);
    }
}



    async handleVoiceMessage() {
        const voiceBtn = document.getElementById('voiceBtn');
        const chatInput = document.getElementById('chatInput');
        
        if (!window.currentMeetingId) {
            this.addMessageToChat('bot', 'Please select a meeting first');
            return;
        }

        // Check if already recording
        if (voiceBtn.classList.contains('recording')) {
            return;
        }

        // Check browser support
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            this.addMessageToChat('bot', 'Your browser doesn\'t support speech recognition');
            return;
        }

        // Update UI
        voiceBtn.innerHTML = '<i class="bi bi-x-circle"></i>';
        voiceBtn.classList.add('recording');
        voiceBtn.title = 'Stop recording';

        const recognition = new SpeechRecognition();
        recognition.lang = 'en-US';
        recognition.interimResults = true;  // Enable interim results
        recognition.continuous = true;      // Keep listening until stopped
        recognition.maxAlternatives = 1;

        // Timeout variables
        let speechTimeout;
        const SPEECH_TIMEOUT_MS = 3000; // 3 seconds of silence before stopping

        // Create a one-time click handler to stop recording
        const stopRecording = () => {
            clearTimeout(speechTimeout);
            recognition.stop();
            voiceBtn.innerHTML = '<i class="bi bi-mic"></i>';
            voiceBtn.classList.remove('recording');
            voiceBtn.title = 'Start voice input';
            voiceBtn.removeEventListener('click', stopRecording);
            voiceBtn.addEventListener('click', this.handleVoiceMessage.bind(this));
        };

        recognition.onresult = (event) => {
            // Clear any existing timeout
            clearTimeout(speechTimeout);
            
            // Get the most recent result
            const results = event.results;
            const last = results[results.length - 1];
            
            // If the result is final, process it
            if (last.isFinal) {
                const transcript = last[0].transcript;
                chatInput.value = transcript;
                stopRecording();
                this.handleSendMessage();
            } else {
                // Set a timeout if speech pauses
                speechTimeout = setTimeout(() => {
                    if (voiceBtn.classList.contains('recording')) {
                        const interimTranscript = Array.from(results)
                            .map(result => result[0].transcript)
                            .join('');
                        if (interimTranscript.trim().length > 0) {
                            chatInput.value = interimTranscript;
                            this.handleSendMessage();
                        }
                        stopRecording();
                    }
                }, SPEECH_TIMEOUT_MS);
            }
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error', event.error);
            this.addMessageToChat('bot', `Error: ${event.error}`);
            stopRecording();
        };

        recognition.onend = () => {
            if (voiceBtn.classList.contains('recording')) {
                stopRecording();
            }
        };

        // Request microphone permission
        try {
            await navigator.mediaDevices.getUserMedia({ audio: true });
            recognition.start();
            voiceBtn.removeEventListener('click', this.handleVoiceMessage.bind(this));
            voiceBtn.addEventListener('click', stopRecording);
        } catch (error) {
            console.error('Microphone access denied', error);
            this.addMessageToChat('bot', 'Microphone access was denied');
            stopRecording();
        }
    }

    addMessageToChat(role, message) {
        const chatBox = document.getElementById('chatBox');
        if (!chatBox) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${role}`;
        
        if (role === 'bot') {
            messageDiv.innerHTML = `
                <div class="message-content">${message}</div>
                <button class="speak-btn" title="Read aloud">
                    <i class="bi bi-volume-up"></i>
                </button>
            `;
            
            // Add click handler for the speak button
            const speakBtn = messageDiv.querySelector('.speak-btn');
            speakBtn.addEventListener('click', () => {
                this.speak(message);
            });
        } else {
            messageDiv.textContent = message;
        }

        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    renderChatHistory(history) {
        const chatBox = document.getElementById('chatBox');
        if (!chatBox) return;

        chatBox.innerHTML = '';
        history.forEach(({ role, message }) => {
            this.addMessageToChat(role, message);
        });
    }
}

// Export singleton instance
window.router = new Router();