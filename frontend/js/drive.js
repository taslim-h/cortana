// frontend/js/drive.js

const driveManager = {
    currentMeetingId: null,
    pendingFolderUrl: null,

    // Initialize drive management
    init() {
        console.log('Drive manager initialized');
        // Initialize any drive-specific event handlers
    },

    // Prompt for Google Drive authorization
    promptDriveAuth(meetingId, folderUrl) {
        console.log('promptDriveAuth called:', { meetingId, folderUrl });

        this.currentMeetingId = meetingId;
        this.pendingFolderUrl = folderUrl;

        const message = `To access this Google Drive folder, you need to authorize access.\n\n` +
            `You can use ANY Google account that has access to this folder.\n\n` +
            `Click OK to select a Google account and grant permissions.`;

        if (confirm(message)) {
            this.authorizeDrive();
        }
    },

    // Authorize Google Drive access
    async authorizeDrive() {
        console.log('authorizeDrive called');
        utils.showLoading();

        try {
            // Get authorization URL
            const response = await utils.apiRequest('/drive/authorize', {
                method: 'POST',
                body: JSON.stringify({
                    redirect_uri: `${window.location.origin}/drive-callback.html`
                })
            });

            console.log('Authorization URL received:', response.auth_url);

            // Open authorization in popup
            const authWindow = window.open(
                response.auth_url,
                'Google Drive Authorization',
                'width=500,height=600'
            );

            if (!authWindow) {
                alert('Popup blocked! Please allow popups for this site and try again.');
                utils.hideLoading();

                // Show manual authorization button
                this.showManualAuthButton();
                return;
            }

            // Listen for authorization completion
            const checkAuth = setInterval(async () => {
                if (authWindow.closed) {
                    clearInterval(checkAuth);
                    utils.hideLoading();
                }
            }, 1000);

            // Listen for message from popup
            const messageHandler = async (event) => {
                console.log('Message received:', event.data);
                if (event.data.type === 'drive-auth-success') {
                    authWindow.close();
                    clearInterval(checkAuth);
                    window.removeEventListener('message', messageHandler);

                    // Complete the authorization and link folder
                    await this.completeDriveAuth(event.data.code);
                }
            };

            window.addEventListener('message', messageHandler);
        } catch (error) {
            utils.showError('Failed to authorize Google Drive');
            console.error('Drive authorization error:', error);
        } finally {
            utils.hideLoading();
        }
    },

    // Complete drive authorization and link folder
    async completeDriveAuth(code) {
        try {
            // Get access token
            const tokenResponse = await utils.apiRequest('/drive/callback', {
                method: 'POST',
                body: JSON.stringify({
                    code: code,
                    redirect_uri: `${window.location.origin}/drive-callback.html`
                })
            });

            // Link folder to meeting
            if (this.currentMeetingId && this.pendingFolderUrl) {
                await this.linkFolderToMeeting(
                    this.currentMeetingId,
                    this.pendingFolderUrl,
                    tokenResponse.token
                );
            }
        } catch (error) {
            utils.showError('Failed to complete Drive authorization');
            console.error('Drive auth completion error:', error);
        }
    },

    // Link Google Drive folder to meeting
    async linkFolderToMeeting(meetingId, folderUrl, accessToken) {
        utils.showLoading();

        try {
            const response = await utils.apiRequest(`/drive/meetings/${meetingId}/link-folder`, {
                method: 'POST',
                body: JSON.stringify({
                    folder_url: folderUrl,
                    access_token: accessToken
                })
            });

            utils.showError(`Folder "${response.folder_name}" linked successfully`, 'success-message');

            // Reload meetings to show updated links
            await meetingManager.loadMeetings();
        } catch (error) {
            utils.showError('Failed to link Google Drive folder');
            console.error('Link folder error:', error);
        } finally {
            utils.hideLoading();
            this.currentMeetingId = null;
            this.pendingFolderUrl = null;
        }
    },

    // // View folder contents
    // async viewFolder(meetingId) {
    //     utils.showLoading();

    //     try {
    //         const response = await utils.apiRequest(`/drive/meetings/${meetingId}/folder-contents`, {
    //             method: 'GET'
    //         });

    //         this.showFolderContents(response);


    //     } catch (error) {
    //         console.error('View folder error:', error);

    //         if (error.message.includes('No Google Drive folder linked')) {
    //             utils.showError('No Google Drive folder linked to this meeting');
    //         } else if (error.message.includes('authorization has expired') || error.message.includes('401')) {
    //             // Authorization expired, prompt to re-authorize
    //             const meeting = meetings.find(m => m._id === meetingId);
    //             if (meeting && meeting.drive_folder_link) {
    //                 if (confirm('Google Drive authorization has expired. Would you like to re-authorize?')) {
    //                     this.promptDriveAuth(meetingId, meeting.drive_folder_link);
    //                 }
    //             }
    //         } else {
    //             utils.showError('Failed to load folder contents. Please try again.');
    //         }
    //     } finally {
    //         utils.hideLoading();
    //     }
    // },



    // View folder contents
    async viewFolder(meetingId) {
        utils.showLoading();

        try {
            const response = await utils.apiRequest(`/drive/meetings/${meetingId}/folder-contents`, {
                method: 'GET'
            });

            this.showFolderContents(response);

        } catch (error) {
            console.error('View folder error:', error);

            // Check for missing or expired authorization
            const msg = (error.message || '').toLowerCase();
            if (
                msg.includes('no google drive folder linked') ||
                msg.includes('drive access not authorized') ||
                msg.includes('authorization has expired') ||
                msg.includes('401')
            ) {
                const meeting = meetings.find(m => m._id === meetingId);
                if (meeting && meeting.drive_folder_link) {
                    if (confirm('Google Drive access for this meeting is missing or expired. Would you like to re-link the folder?')) {
                        this.promptDriveAuth(meetingId, meeting.drive_folder_link);
                    }
                } else {
                    utils.showError('No Google Drive folder linked to this meeting');
                }
            } else {
                utils.showError('Failed to load folder contents. Please try again.');
            }
        } finally {
            utils.hideLoading();
        }
    },



    // Show folder contents in a modal
    showFolderContents(data) {
        const modal = document.createElement('div');
        modal.className = 'modal active';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Google Drive Folder Contents</h3>
                    <button class="close-btn" onclick="this.closest('.modal').remove()">
                        <span class="material-icons">close</span>
                    </button>
                </div>
                <div class="folder-contents">
                    ${data.files.length === 0 ?
                '<p class="empty-state">This folder is empty</p>' :
                data.files.map(file => `
                            <div class="file-item">
                                <span class="material-icons file-icon">
                                    ${this.getFileIcon(file.mimeType)}
                                </span>
                                <div class="file-info">
                                    <a href="${file.webViewLink}" target="_blank" class="file-name">
                                        ${file.name}
                                    </a>
                                    <span class="file-meta">
                                        ${this.formatFileSize(file.size)} • 
                                        ${new Date(file.modifiedTime).toLocaleDateString()}
                                    </span>
                                </div>
                            </div>
                        `).join('')
            }
                </div>
            </div>
        `;

        document.body.appendChild(modal);
    },

    // Get appropriate icon for file type
    getFileIcon(mimeType) {
        if (mimeType.includes('folder')) return 'folder';
        if (mimeType.includes('document')) return 'description';
        if (mimeType.includes('spreadsheet')) return 'table_chart';
        if (mimeType.includes('presentation')) return 'slideshow';
        if (mimeType.includes('pdf')) return 'picture_as_pdf';
        if (mimeType.includes('image')) return 'image';
        if (mimeType.includes('video')) return 'videocam';
        if (mimeType.includes('audio')) return 'audiotrack';
        return 'insert_drive_file';
    },

    // Format file size
    formatFileSize(bytes) {
        if (!bytes) return '0 Bytes';

        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));

        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    // Show manual authorization button when popup is blocked
    showManualAuthButton() {
        const existingButton = document.getElementById('manual-drive-auth-btn');
        if (existingButton) existingButton.remove();

        const button = document.createElement('button');
        button.id = 'manual-drive-auth-btn';
        button.innerHTML = `
            <span class="material-icons">folder</span>
            Click here to authorize Google Drive access
        `;
        button.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
            padding: 12px 24px;
            background: #1a73e8;
            color: white;
            border: none;
            border-radius: 24px;
            cursor: pointer;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 16px;
            font-weight: 500;
            transition: all 0.3s;
        `;

        button.onmouseover = () => {
            button.style.transform = 'translateY(-2px)';
            button.style.boxShadow = '0 6px 12px rgba(0,0,0,0.15)';
        };

        button.onmouseout = () => {
            button.style.transform = 'translateY(0)';
            button.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
        };

        button.onclick = () => {
            button.remove();
            this.authorizeDrive();
        };

        document.body.appendChild(button);

        // Pulse animation to draw attention
        button.animate([
            { transform: 'scale(1)' },
            { transform: 'scale(1.05)' },
            { transform: 'scale(1)' }
        ], {
            duration: 1000,
            iterations: 3
        });
    }
};