// // frontend/js/drive-picker.js

// const drivePicker = {
//     pickerApiLoaded: false,
//     oauthToken: null,
//     currentMeetingId: null,
    
//     // Initialize the Google Picker API
//     init() {
//         // Load the Google API
//         const script = document.createElement('script');
//         script.src = 'https://apis.google.com/js/api.js';
//         script.onload = () => this.onApiLoad();
//         document.body.appendChild(script);
//     },

//     // Called when Google API is loaded
//     onApiLoad() {
//         gapi.load('auth', () => {
//             console.log('Google Auth API loaded');
//         });
//         gapi.load('picker', () => {
//             this.pickerApiLoaded = true;
//             console.log('Google Picker API loaded');
//         });
//     },

//     // Select folder for a meeting
//     async selectFolderForMeeting(meetingId) {
//         this.currentMeetingId = meetingId;
        
//         if (!this.pickerApiLoaded) {
//             alert('Google Picker is still loading. Please try again.');
//             return;
//         }

//         // First authenticate via our backend
//         const message = `Select a Google Drive folder for this meeting.\n\n` +
//                        `You can choose from any Google account you have access to.`;
        
//         if (!confirm(message)) return;

//         // Start OAuth flow through our backend
//         await this.authenticateAndShowPicker();
//     },

//     // Authenticate through backend and show picker
//     async authenticateAndShowPicker() {
//         utils.showLoading();
        
//         try {
//             // Get authorization URL from backend
//             const response = await utils.apiRequest('/drive/authorize', {
//                 method: 'POST',
//                 body: JSON.stringify({
//                     redirect_uri: `${window.location.origin}/drive-picker-callback.html`
//                 })
//             });

//             // Store meeting ID for after auth
//             sessionStorage.setItem('picker_meeting_id', this.currentMeetingId);

//             // Open authorization popup
//             const authWindow = window.open(
//                 response.auth_url,
//                 'Google Drive Authorization',
//                 'width=500,height=600,left=200,top=100'
//             );

//             if (!authWindow) {
//                 alert('Popup blocked! Please allow popups for this site.');
//                 utils.hideLoading();
//                 return;
//             }

//             // Listen for authorization completion
//             window.addEventListener('message', async (event) => {
//                 if (event.data.type === 'drive-picker-auth-success') {
//                     authWindow.close();
                    
//                     // Exchange code for token
//                     const tokenResult = await utils.apiRequest('/drive/callback', {
//                         method: 'POST',
//                         body: JSON.stringify({
//                             code: event.data.code,
//                             redirect_uri: `${window.location.origin}/drive-picker-callback.html`
//                         })
//                     });

//                     if (tokenResult.token) {
//                         this.oauthToken = tokenResult.token.access_token;
//                         // Now show the picker
//                         this.showPicker(tokenResult.token);
//                     }
//                 }
//             }, { once: true });

//         } catch (error) {
//             utils.showError('Failed to start authorization');
//             console.error('Authorization error:', error);
//         } finally {
//             utils.hideLoading();
//         }
//     },

//     // Show the Google Picker
//     showPicker(fullTokenData) {
//         if (!this.oauthToken) {
//             console.error('No OAuth token available');
//             return;
//         }

//         // Create picker view for folders only
//         const view = new google.picker.DocsView(google.picker.ViewId.FOLDERS)
//             .setSelectFolderEnabled(true)
//             .setMode(google.picker.DocsViewMode.LIST);

//         // Create picker
//         const picker = new google.picker.PickerBuilder()
//             .addView(view)
//             .setOAuthToken(this.oauthToken)
//             .setDeveloperKey(GOOGLE_API_KEY) // You need to set this in index.html
//             .setCallback((data) => this.pickerCallback(data, fullTokenData))
//             .setTitle('Select a folder for this meeting')
//             .enableFeature(google.picker.Feature.NAV_HIDDEN)
//             .build();

//         picker.setVisible(true);
//     },

//     // Handle picker selection
//     async pickerCallback(data, fullTokenData) {
//         if (data.action === google.picker.Action.PICKED) {
//             const folder = data.docs[0];
//             console.log('Folder selected:', folder);

//             // Folder object contains:
//             // - id: The folder ID
//             // - name: The folder name
//             // - url: The folder URL
            
//             await this.linkFolderToMeeting(folder, fullTokenData);
//         } else if (data.action === google.picker.Action.CANCEL) {
//             console.log('Picker cancelled');
//             sessionStorage.removeItem('picker_meeting_id');
//         }
//     },

//     // Link the selected folder to the meeting
//     async linkFolderToMeeting(folder, tokenData) {
//         const meetingId = this.currentMeetingId || sessionStorage.getItem('picker_meeting_id');
        
//         if (!meetingId) {
//             utils.showError('Meeting ID lost. Please try again.');
//             return;
//         }

//         utils.showLoading();

//         try {
//             // Create the request with folder info
//             const requestData = {
//                 folder_id: folder.id,
//                 folder_name: folder.name,
//                 folder_url: folder.url || `https://drive.google.com/drive/folders/${folder.id}`,
//                 access_token: tokenData
//             };

//             const response = await utils.apiRequest(`/drive/meetings/${meetingId}/link-folder`, {
//                 method: 'POST',
//                 body: JSON.stringify(requestData)
//             });

//             utils.showError(`Folder "${folder.name}" linked successfully!`, 'success-message');
            
//             // Clean up
//             sessionStorage.removeItem('picker_meeting_id');
//             this.currentMeetingId = null;
//             this.oauthToken = null;
            
//             // Reload meetings to show the update
//             await meetingManager.loadMeetings();
            
//         } catch (error) {
//             console.error('Failed to link folder:', error);
//             utils.showError('Failed to link the selected folder');
//         } finally {
//             utils.hideLoading();
//         }
//     },

//     // For the meeting modal - select folder before saving
//     async selectFolderForModal() {
//         if (!this.pickerApiLoaded) {
//             alert('Google Picker is still loading. Please try again.');
//             return;
//         }

//         // Store selected folder temporarily
//         sessionStorage.setItem('modal_folder_selection', 'pending');
        
//         // Start the picker flow
//         await this.authenticateAndShowPicker();
//     },

//     // Modified picker callback for modal usage
//     async modalPickerCallback(data, fullTokenData) {
//         if (data.action === google.picker.Action.PICKED) {
//             const folder = data.docs[0];
            
//             // Store the folder info for when meeting is saved
//             sessionStorage.setItem('selected_folder', JSON.stringify({
//                 id: folder.id,
//                 name: folder.name,
//                 url: folder.url || `https://drive.google.com/drive/folders/${folder.id}`,
//                 token: fullTokenData
//             }));
            
//             // Update UI to show selected folder
//             const folderDisplay = document.getElementById('selected-folder-display');
//             if (folderDisplay) {
//                 folderDisplay.textContent = folder.name;
//                 folderDisplay.style.display = 'block';
//             }
            
//             utils.showError(`Folder "${folder.name}" selected`, 'success-message');
//         }
        
//         sessionStorage.removeItem('modal_folder_selection');
//     }
// };

// // Initialize on load
// document.addEventListener('DOMContentLoaded', () => {
//     drivePicker.init();
// });

// frontend/js/drive-picker.js

const drivePicker = {
    pickerApiLoaded: false,
    oauthToken: null,
    currentMeetingId: null,
    
    // Initialize the Google Picker API
    init() {
        // Load the Google API
        const script = document.createElement('script');
        script.src = 'https://apis.google.com/js/api.js';
        script.onload = () => this.onApiLoad();
        document.body.appendChild(script);
    },

    // Called when Google API is loaded
    onApiLoad() {
        console.log('Google API script loaded');
        
        if (!window.gapi) {
            console.error('Google API (gapi) not available');
            return;
        }

        gapi.load('auth', () => {
            console.log('Google Auth API loaded');
        });
        
        gapi.load('picker', () => {
            this.pickerApiLoaded = true;
            console.log('Google Picker API loaded');
            
            // Check if API key is set
            if (typeof GOOGLE_API_KEY === 'undefined' || GOOGLE_API_KEY === 'YOUR_API_KEY') {
                console.error('GOOGLE_API_KEY not set! Please update it in index.html');
                alert('Google API Key not configured. Please update GOOGLE_API_KEY in index.html');
            }
        });
    },

    // Select folder for a meeting
    async selectFolderForMeeting(meetingId) {
        this.currentMeetingId = meetingId;
        
        if (!this.pickerApiLoaded) {
            alert('Google Picker is still loading. Please try again.');
            return;
        }

        // First authenticate via our backend
        const message = `Select a Google Drive folder for this meeting.\n\n` +
                       `You can choose from any Google account you have access to.`;
        
        if (!confirm(message)) return;

        // Start OAuth flow through our backend
        await this.authenticateAndShowPicker();
    },

    // Authenticate through backend and show picker
    async authenticateAndShowPicker() {
        utils.showLoading();
        
        try {
            // Get authorization URL from backend
            const response = await utils.apiRequest('/drive/authorize', {
                method: 'POST',
                body: JSON.stringify({
                    redirect_uri: `${window.location.origin}/drive-picker-callback.html`
                })
            });

            // Store meeting ID for after auth
            sessionStorage.setItem('picker_meeting_id', this.currentMeetingId);

            // Open authorization popup
            const authWindow = window.open(
                response.auth_url,
                'Google Drive Authorization',
                'width=500,height=600,left=200,top=100'
            );

            if (!authWindow) {
                alert('Popup blocked! Please allow popups for this site.');
                utils.hideLoading();
                return;
            }

            // Set up message listener BEFORE opening the window
            const messageHandler = async (event) => {
                console.log('Received message:', event.data);
                
                if (event.data.type === 'drive-picker-auth-success') {
                    window.removeEventListener('message', messageHandler);
                    authWindow.close();
                    
                    try {
                        // Exchange code for token
                        const tokenResult = await utils.apiRequest('/drive/callback', {
                            method: 'POST',
                            body: JSON.stringify({
                                code: event.data.code,
                                redirect_uri: `${window.location.origin}/drive-picker-callback.html`
                            })
                        });

                        console.log('Token result:', tokenResult);

                        if (tokenResult.token) {
                            this.oauthToken = tokenResult.token.access_token;
                            // Now show the picker
                            setTimeout(() => {
                                this.showPicker(tokenResult.token);
                            }, 500);
                        }
                    } catch (error) {
                        console.error('Token exchange error:', error);
                        utils.showError('Failed to complete authorization');
                    }
                }
            };
            
            window.addEventListener('message', messageHandler);

            // Also check if window is closed without auth
            const checkClosed = setInterval(() => {
                if (authWindow.closed) {
                    clearInterval(checkClosed);
                    utils.hideLoading();
                    window.removeEventListener('message', messageHandler);
                }
            }, 1000);

        } catch (error) {
            utils.showError('Failed to start authorization');
            console.error('Authorization error:', error);
            utils.hideLoading();
        }
    },

    // Show the Google Picker
    showPicker(fullTokenData) {
        console.log('showPicker called with token:', this.oauthToken ? 'Token exists' : 'No token');
        
        if (!this.oauthToken) {
            console.error('No OAuth token available');
            utils.showError('Authorization failed. Please try again.');
            return;
        }

        if (!window.google || !window.google.picker) {
            console.error('Google Picker API not loaded');
            utils.showError('Google Picker is not ready. Please refresh and try again.');
            return;
        }

        try {
            // Hide loading spinner since picker will show
            utils.hideLoading();

            // Create picker view for folders only
            const view = new google.picker.DocsView(google.picker.ViewId.FOLDERS)
                .setSelectFolderEnabled(true)
                .setMode(google.picker.DocsViewMode.LIST);

            // Create picker
            const picker = new google.picker.PickerBuilder()
                .addView(view)
                .setOAuthToken(this.oauthToken)
                .setDeveloperKey(GOOGLE_API_KEY)
                .setCallback((data) => this.pickerCallback(data, fullTokenData))
                .setTitle('Select a folder for this meeting')
                .enableFeature(google.picker.Feature.NAV_HIDDEN)
                .setMaxItems(1)
                .build();

            console.log('Showing picker...');
            picker.setVisible(true);
        } catch (error) {
            console.error('Error showing picker:', error);
            utils.showError('Failed to show folder picker. Please try again.');
        }
    },

    // Handle picker selection
    async pickerCallback(data, fullTokenData) {
        console.log('Picker callback - Action:', data.action, 'Data:', data);
        
        if (data.action === google.picker.Action.PICKED) {
            const folder = data.docs[0];
            console.log('Folder selected:', folder);

            // Folder object contains:
            // - id: The folder ID
            // - name: The folder name
            // - url: The folder URL (might not always be present)
            
            await this.linkFolderToMeeting(folder, fullTokenData);
        } else if (data.action === google.picker.Action.CANCEL) {
            console.log('Picker cancelled');
            sessionStorage.removeItem('picker_meeting_id');
        } else if (data.action === google.picker.Action.LOADED) {
            console.log('Picker loaded successfully');
        }
    },

    // Link the selected folder to the meeting
    async linkFolderToMeeting(folder, tokenData) {
        const meetingId = this.currentMeetingId || sessionStorage.getItem('picker_meeting_id');
        
        if (!meetingId) {
            utils.showError('Meeting ID lost. Please try again.');
            return;
        }

        utils.showLoading();

        try {
            // Create the request with folder info
            const requestData = {
                folder_id: folder.id,
                folder_name: folder.name,
                folder_url: folder.url || `https://drive.google.com/drive/folders/${folder.id}`,
                access_token: tokenData
            };

            const response = await utils.apiRequest(`/drive/meetings/${meetingId}/link-folder`, {
                method: 'POST',
                body: JSON.stringify(requestData)
            });

            utils.showError(`Folder "${folder.name}" linked successfully!`, 'success-message');
            
            // Clean up
            sessionStorage.removeItem('picker_meeting_id');
            this.currentMeetingId = null;
            this.oauthToken = null;
            
            console.log('Folder linked, reloading meetings...');
            // Reload meetings to show the update
            await meetingManager.loadMeetings();
            console.log('Meetings reloaded successfully');
            
            
        } catch (error) {
            console.error('Failed to link folder:', error);
            utils.showError('Failed to link the selected folder');
        } finally {
            utils.hideLoading();
        }
    },

    // For the meeting modal - select folder before saving
    async selectFolderForModal() {
        if (!this.pickerApiLoaded) {
            alert('Google Picker is still loading. Please try again.');
            return;
        }

        // Store selected folder temporarily
        sessionStorage.setItem('modal_folder_selection', 'pending');
        
        // Start the picker flow
        await this.authenticateAndShowPicker();
    },

    // Modified picker callback for modal usage
    async modalPickerCallback(data, fullTokenData) {
        if (data.action === google.picker.Action.PICKED) {
            const folder = data.docs[0];
            
            // Store the folder info for when meeting is saved
            sessionStorage.setItem('selected_folder', JSON.stringify({
                id: folder.id,
                name: folder.name,
                url: folder.url || `https://drive.google.com/drive/folders/${folder.id}`,
                token: fullTokenData
            }));
            
            // Update UI to show selected folder
            const folderDisplay = document.getElementById('selected-folder-display');
            if (folderDisplay) {
                folderDisplay.textContent = folder.name;
                folderDisplay.style.display = 'block';
            }
            
            utils.showError(`Folder "${folder.name}" selected`, 'success-message');
        }
        
        sessionStorage.removeItem('modal_folder_selection');
    }
};

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    drivePicker.init();
});