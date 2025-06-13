// frontend/js/meetings.js

let currentMeetingId = null;
let meetings = [];

const meetingManager = {
    // Initialize meeting management
    init() {
        // Bind events
        document.getElementById('add-meeting-btn').addEventListener('click', () => {
            this.openMeetingModal();
        });

        document.getElementById('meeting-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveMeeting();
        });
    },

    // Load all meetings
    async loadMeetings() {
        utils.showLoading();

        try {
            const response = await utils.apiRequest('/meetings');
            meetings = response;
            this.displayMeetings();
        } catch (error) {
            utils.showError('Failed to load meetings');
            console.error('Load meetings error:', error);
        } finally {
            utils.hideLoading();
        }
    },

    // Display meetings
    displayMeetings() {
        const meetingsList = document.getElementById('meetings-list');

        if (meetings.length === 0) {
            meetingsList.innerHTML = `
                <div class="empty-state">
                    <p>No meetings scheduled yet</p>
                    <p>Click the + button to add your first meeting</p>
                </div>
            `;
            return;
        }

        meetingsList.innerHTML = meetings.map(meeting => `
            <div class="meeting-card" data-meeting-id="${meeting._id}">
                <div class="meeting-header">
                    <div>
                        <h3 class="meeting-title">${meeting.title}</h3>
                        <p class="meeting-time">
                            ${utils.formatDateTime(meeting.start_time)} - 
                            ${new Date(meeting.end_time).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
                        </p>
                        ${meeting.description ? `<p class="meeting-description">${meeting.description}</p>` : ''}
                    </div>
                    <div class="meeting-actions">
                        <button class="icon-btn" onclick="meetingManager.editMeeting('${meeting._id}')">
                            <span class="material-icons">edit</span>
                        </button>
                        <button class="icon-btn" onclick="meetingManager.deleteMeeting('${meeting._id}')">
                            <span class="material-icons">delete</span>
                        </button>
                    </div>
                </div>
                <div class="meeting-links">
                    ${meeting.meeting_link ? `
                        <a href="${meeting.meeting_link}" target="_blank" class="meeting-link">
                            <span class="material-icons">videocam</span>
                            Join Meeting
                        </a>
                    ` : ''}
                    ${meeting.drive_folder_link ? `
                        <a href="#" onclick="driveManager.viewFolder('${meeting._id}'); return false;" class="meeting-link">
                            <span class="material-icons">folder</span>
                            View Folder
                        </a>
                    ` : ''}
                </div>
            </div>
        `).join('');
    },

    // Open meeting modal
    openMeetingModal(meetingId = null) {
        currentMeetingId = meetingId;
        const modal = document.getElementById('meeting-modal');
        const form = document.getElementById('meeting-form');

        if (meetingId) {
            // Edit mode
            document.getElementById('modal-title').textContent = 'Edit Meeting';
            const meeting = meetings.find(m => m._id === meetingId);

            if (meeting) {
                document.getElementById('meeting-title').value = meeting.title;
                document.getElementById('start-time').value = utils.formatDateForInput(meeting.start_time);
                document.getElementById('end-time').value = utils.formatDateForInput(meeting.end_time);
                document.getElementById('meeting-link').value = meeting.meeting_link || '';
                document.getElementById('drive-folder').value = meeting.drive_folder_link || '';
                document.getElementById('description').value = meeting.description || '';
            }
        } else {
            // Add mode
            document.getElementById('modal-title').textContent = 'Add Meeting';
            form.reset();

            // Set default times
            const now = new Date();
            const startTime = new Date(now.getTime() + 60 * 60 * 1000); // 1 hour from now
            const endTime = new Date(startTime.getTime() + 60 * 60 * 1000); // 2 hours from now

            document.getElementById('start-time').value = utils.formatDateForInput(startTime);
            document.getElementById('end-time').value = utils.formatDateForInput(endTime);
        }

        modal.classList.add('active');
    },

    // Save meeting (create or update)
    async saveMeeting() {
        const formData = {
            title: document.getElementById('meeting-title').value,
            start_time: document.getElementById('start-time').value,
            end_time: document.getElementById('end-time').value,
            meeting_link: document.getElementById('meeting-link').value || null,
            drive_folder_link: document.getElementById('drive-folder').value || null,
            description: document.getElementById('description').value || null
        };

        console.log('Saving meeting with data:', formData);

        // Validate form
        const errors = utils.validateMeetingForm(formData);
        if (errors.length > 0) {
            utils.showError(errors[0]);
            return;
        }

        utils.showLoading();

        try {
            let response;

            if (currentMeetingId) {
                // Update existing meeting
                response = await utils.apiRequest(`/meetings/${currentMeetingId}`, {
                    method: 'PUT',
                    body: JSON.stringify(formData)
                });
            } else {
                // Create new meeting
                response = await utils.apiRequest('/meetings', {
                    method: 'POST',
                    body: JSON.stringify(formData)
                });
            }

            console.log('Meeting saved:', response);

            closeMeetingModal(); // Call the global function, not this.closeMeetingModal
            await this.loadMeetings();

            // If Google Drive link was provided, prompt for authorization
            if (formData.drive_folder_link) {
                // For new meetings OR if the link changed
                const isNewMeeting = !currentMeetingId;
                const linkChanged = currentMeetingId &&
                    meetings.find(m => m._id === currentMeetingId)?.drive_folder_link !== formData.drive_folder_link;

                if (isNewMeeting || linkChanged) {
                    console.log('Drive link detected, prompting for authorization...');
                    // Give a moment for the UI to update
                    setTimeout(() => {
                        driveManager.promptDriveAuth(response._id, formData.drive_folder_link);
                    }, 500);
                }
            }
        } catch (error) {
            console.error('Save meeting error:', error);
            if (error.message.includes('conflict')) {
                // Handle collision
                try {
                    const errorData = JSON.parse(error.message);
                    this.showCollisionWarning(errorData.detail);
                } catch {
                    this.showCollisionWarning({
                        message: 'Meeting time conflicts with existing meeting',
                        conflicting_meeting: null
                    });
                }
            } else {
                utils.showError('Failed to save meeting');
            }
        } finally {
            utils.hideLoading();
        }
    },

    // Edit meeting
    editMeeting(meetingId) {
        this.openMeetingModal(meetingId);
    },

    // Delete meeting
    async deleteMeeting(meetingId) {
        if (!confirm('Are you sure you want to delete this meeting?')) {
            return;
        }

        utils.showLoading();

        try {
            await utils.apiRequest(`/meetings/${meetingId}`, {
                method: 'DELETE'
            });

            await this.loadMeetings();
        } catch (error) {
            utils.showError('Failed to delete meeting');
        } finally {
            utils.hideLoading();
        }
    },

    // Show collision warning
    showCollisionWarning(details) {
        const modal = document.getElementById('collision-modal');
        const message = document.getElementById('collision-message');

        let messageText = details.message || 'Meeting time conflicts with existing meeting';

        if (details.conflicting_meeting) {
            const meeting = details.conflicting_meeting;
            messageText += `\n\nConflicting meeting: "${meeting.title}"`;
            messageText += `\nTime: ${utils.formatDateTime(meeting.start_time)} - ${utils.formatDateTime(meeting.end_time)}`;
        }

        message.textContent = messageText;
        modal.classList.add('active');
    }
};

// Modal functions (global for onclick handlers)
function closeMeetingModal() {
    document.getElementById('meeting-modal').classList.remove('active');
    currentMeetingId = null;
}

function closeCollisionModal() {
    document.getElementById('collision-modal').classList.remove('active');
}