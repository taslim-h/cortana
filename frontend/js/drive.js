// frontend/js/drive.js

const driveManager = {
    // Initialize drive management
    init() {
        console.log('Drive manager initialized');
    },

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
                if (confirm('Google Drive access has expired or is missing. Would you like to re-link the folder?')) {
                    // Use picker to re-link
                    drivePicker.selectFolderForMeeting(meetingId);
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
                    <h3>Google Drive Folder: ${data.folder_name || 'Contents'}</h3>
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
        if (!mimeType) return 'insert_drive_file';
        
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
    }
};