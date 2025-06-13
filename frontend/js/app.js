// frontend/js/app.js

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    // Initialize managers
    authManager.init();
    meetingManager.init();
    calendarManager.init();
    driveManager.init();

    // Set up global error handler
    window.addEventListener('unhandledrejection', event => {
        console.error('Unhandled promise rejection:', event.reason);
        utils.hideLoading();
    });

    // Handle OAuth callbacks if this is a callback page
    handleOAuthCallbacks();
});

// Handle OAuth callbacks for Google services
function handleOAuthCallbacks() {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const state = urlParams.get('state');

    if (code) {
        // This is an OAuth callback
        if (window.location.pathname.includes('calendar-callback')) {
            // Send message to opener window
            if (window.opener) {
                window.opener.postMessage({
                    type: 'calendar-auth-success',
                    code: code
                }, window.location.origin);

                // Show success message
                document.body.innerHTML = `
                    <div style="display: flex; align-items: center; justify-content: center; height: 100vh; font-family: Arial, sans-serif;">
                        <div style="text-align: center;">
                            <h2>Authorization Successful!</h2>
                            <p>You can close this window.</p>
                        </div>
                    </div>
                `;
            }
        } else if (window.location.pathname.includes('drive-callback')) {
            // Send message to opener window
            if (window.opener) {
                window.opener.postMessage({
                    type: 'drive-auth-success',
                    code: code
                }, window.location.origin);

                // Show success message
                document.body.innerHTML = `
                    <div style="display: flex; align-items: center; justify-content: center; height: 100vh; font-family: Arial, sans-serif;">
                        <div style="text-align: center;">
                            <h2>Authorization Successful!</h2>
                            <p>You can close this window.</p>
                        </div>
                    </div>
                `;
            }
        }
    }
}

// Add CSS for components not in the main CSS file
const style = document.createElement('style');
style.textContent = `
    .empty-state {
        text-align: center;
        padding: 40px 20px;
        color: var(--text-secondary);
    }
    
    .empty-state p {
        margin-bottom: 8px;
    }
    
    .error-state {
        text-align: center;
        padding: 40px 20px;
        color: var(--danger-color);
    }
    
    .success-message {
        color: var(--success-color);
        font-size: 14px;
        margin-top: 16px;
        text-align: center;
        display: block;
    }
    
    .meeting-description {
        color: var(--text-secondary);
        font-size: 14px;
        margin-top: 8px;
    }
    
    .event-location {
        color: var(--text-secondary);
        font-size: 12px;
        margin-top: 4px;
    }
    
    .folder-contents {
        padding: 20px;
        max-height: 400px;
        overflow-y: auto;
    }
    
    .file-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px;
        border-radius: 4px;
        transition: background 0.3s;
    }
    
    .file-item:hover {
        background: var(--background);
    }
    
    .file-icon {
        color: var(--text-secondary);
        font-size: 24px;
    }
    
    .file-info {
        flex: 1;
        min-width: 0;
    }
    
    .file-name {
        display: block;
        color: var(--primary-color);
        text-decoration: none;
        font-weight: 500;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .file-name:hover {
        text-decoration: underline;
    }
    
    .file-meta {
        display: block;
        color: var(--text-secondary);
        font-size: 12px;
        margin-top: 4px;
    }
`;
document.head.appendChild(style);