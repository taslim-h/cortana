// Meetings management functionality
class MeetingsManager {
    constructor() {
        this.meetings = [];
        this.selectedMeeting = null;
    }

    // Load meetings from API
    async loadMeetings() {
        try {
            this.meetings = await window.apiManager.fetchMeetings();
            return this.meetings;
        } catch (error) {
            console.error('Error loading meetings:', error);
            throw error;
        }
    }

    // Get meeting by ID
    getMeetingById(meetingId) {
        return this.meetings.find(meeting => meeting._id === meetingId);
    }

    // Format meeting for display
    formatMeeting(meeting) {
        return {
            id: meeting._id,
            title: meeting.title,
            startTime: new Date(meeting.start_time),
            endTime: new Date(meeting.end_time),
            description: meeting.description || 'No description available',
            duration: this.calculateDuration(meeting.start_time, meeting.end_time),
            isUpcoming: new Date(meeting.start_time) > new Date(),
            isPast: new Date(meeting.end_time) < new Date(),
            isOngoing: this.isMeetingOngoing(meeting.start_time, meeting.end_time)
        };
    }

    // Calculate meeting duration
    calculateDuration(startTime, endTime) {
        const start = new Date(startTime);
        const end = new Date(endTime);
        const durationMs = end - start;
        
        const hours = Math.floor(durationMs / (1000 * 60 * 60));
        const minutes = Math.floor((durationMs % (1000 * 60 * 60)) / (1000 * 60));
        
        if (hours > 0) {
            return `${hours}h ${minutes}m`;
        }
        return `${minutes}m`;
    }

    // Check if meeting is currently ongoing
    isMeetingOngoing(startTime, endTime) {
        const now = new Date();
        const start = new Date(startTime);
        const end = new Date(endTime);
        
        return now >= start && now <= end;
    }

    // Get meetings by status
    getMeetingsByStatus() {
        const formatted = this.meetings.map(meeting => this.formatMeeting(meeting));
        
        return {
            upcoming: formatted.filter(meeting => meeting.isUpcoming),
            ongoing: formatted.filter(meeting => meeting.isOngoing),
            past: formatted.filter(meeting => meeting.isPast)
        };
    }

    // Search meetings
    searchMeetings(query) {
        if (!query.trim()) return this.meetings;
        
        const searchTerm = query.toLowerCase();
        return this.meetings.filter(meeting => 
            meeting.title.toLowerCase().includes(searchTerm) ||
            (meeting.description && meeting.description.toLowerCase().includes(searchTerm))
        );
    }

    // Get meeting statistics
    getMeetingStats() {
        const grouped = this.getMeetingsByStatus();
        
        return {
            total: this.meetings.length,
            upcoming: grouped.upcoming.length,
            ongoing: grouped.ongoing.length,
            past: grouped.past.length
        };
    }

    // Render meeting card HTML
    renderMeetingCard(meeting) {
        const formatted = this.formatMeeting(meeting);
        const statusClass = formatted.isOngoing ? 'ongoing' : formatted.isUpcoming ? 'upcoming' : 'past';
        const statusIcon = formatted.isOngoing ? 'bi-record-circle' : formatted.isUpcoming ? 'bi-clock' : 'bi-check-circle';
        
        return `
            <div class="meeting-card ${statusClass}" data-meeting-id="${meeting._id}">
                <div class="meeting-header">
                    <div class="meeting-title">${formatted.title}</div>
                    <div class="meeting-status">
                        <i class="bi ${statusIcon}"></i>
                    </div>
                </div>
                <div class="meeting-time">
                    <i class="bi bi-clock"></i>
                    ${formatted.startTime.toLocaleString()} - ${formatted.endTime.toLocaleString()}
                </div>
                <div class="meeting-duration">
                    <i class="bi bi-hourglass-split"></i>
                    Duration: ${formatted.duration}
                </div>
                <div class="meeting-description">${formatted.description}</div>
                <div class="meeting-actions">
                    <button class="btn-discord-secondary btn-sm chat-btn" data-meeting-id="${meeting._id}">
                        <i class="bi bi-chat"></i> Chat
                    </button>
                </div>
            </div>
        `;
    }

    // Render meetings list with grouping
    renderMeetingsList(container) {
        if (!container) return;

        const grouped = this.getMeetingsByStatus();
        let html = '';

        // Ongoing meetings
        if (grouped.ongoing.length > 0) {
            html += '<div class="meetings-section">';
            html += '<h3 class="section-title"><i class="bi bi-record-circle text-danger"></i> Ongoing Meetings</h3>';
            html += grouped.ongoing.map(meeting => this.renderMeetingCard(meeting)).join('');
            html += '</div>';
        }

        // Upcoming meetings
        if (grouped.upcoming.length > 0) {
            html += '<div class="meetings-section">';
            html += '<h3 class="section-title"><i class="bi bi-clock text-warning"></i> Upcoming Meetings</h3>';
            html += grouped.upcoming.map(meeting => this.renderMeetingCard(meeting)).join('');
            html += '</div>';
        }

        // Past meetings (limited to last 10)
        if (grouped.past.length > 0) {
            const recentPast = grouped.past.slice(0, 10);
            html += '<div class="meetings-section">';
            html += '<h3 class="section-title"><i class="bi bi-check-circle text-success"></i> Recent Past Meetings</h3>';
            html += recentPast.map(meeting => this.renderMeetingCard(meeting)).join('');
            html += '</div>';
        }

        if (html === '') {
            html = '<div class="no-meetings"><i class="bi bi-calendar-x"></i><p>No meetings found</p></div>';
        }

        container.innerHTML = html;

        // Bind chat button events
        container.querySelectorAll('.chat-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const meetingId = btn.dataset.meetingId;
                this.openChat(meetingId);
            });
        });
    }

    // Open chat for specific meeting
    openChat(meetingId) {
        this.selectedMeeting = meetingId;
        if (window.router) {
            window.router.navigate('chat');
            // Set the meeting selection after navigation
            setTimeout(() => {
                const meetingSelect = document.getElementById('meetingSelect');
                if (meetingSelect) {
                    meetingSelect.value = meetingId;
                    meetingSelect.dispatchEvent(new Event('change'));
                }
            }, 100);
        }
    }
}

// Export singleton instance
window.meetingsManager = new MeetingsManager();