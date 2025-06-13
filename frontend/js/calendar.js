// // frontend/js/calendar.js

// const calendarManager = {
//     // Initialize calendar management
//     init() {
//         document.getElementById('connect-calendar-btn').addEventListener('click', () => {
//             this.connectCalendar();
//         });
//     },

//     // Check if calendar is integrated
//     async checkIntegration() {
//         try {
//             const user = await utils.apiRequest('/auth/me');

//             if (user.calendar_integrated) {
//                 this.showCalendarEvents();
//                 await this.loadCalendarEvents();
//             } else {
//                 this.showConnectButton();
//             }
//         } catch (error) {
//             console.error('Failed to check calendar integration:', error);
//             this.showConnectButton();
//         }
//     },

//     // Connect Google Calendar
//     async connectCalendar() {
//         utils.showLoading();

//         try {
//             // Get authorization URL
//             const response = await utils.apiRequest('/calendar/authorize', {
//                 method: 'POST',
//                 body: JSON.stringify({
//                     redirect_uri: `${window.location.origin}/calendar-callback.html`
//                 })
//             });

//             // Open authorization in popup
//             const authWindow = window.open(
//                 response.auth_url,
//                 'Google Calendar Authorization',
//                 'width=500,height=600'
//             );

//             // Listen for authorization completion
//             const checkAuth = setInterval(async () => {
//                 if (authWindow.closed) {
//                     clearInterval(checkAuth);
//                     utils.hideLoading();

//                     // Check if integration was successful
//                     await this.checkIntegration();
//                 }
//             }, 1000);

//             const messageHandler = async (event) => {
//                 if (event.data.type === 'calendar-auth-success') {
//                     authWindow.close();
//                     clearInterval(checkAuth);
//                     window.removeEventListener('message', messageHandler);

//                     // Complete the authorization
//                     await this.completeAuthorization(event.data.code);
//                 }
//             };

//             window.addEventListener('message', messageHandler);
//         } catch (error) {
//             utils.showError('Failed to connect Google Calendar');
//             console.error('Calendar connection error:', error);
//         } finally {
//             utils.hideLoading();
//         }
//     },

//     // Complete calendar authorization
//     async completeAuthorization(code) {
//         try {
//             await utils.apiRequest('/calendar/callback', {
//                 method: 'POST',
//                 body: JSON.stringify({
//                     code: code,
//                     redirect_uri: `${window.location.origin}/calendar-callback.html`
//                 })
//             });

//             // Refresh integration status
//             await this.checkIntegration();
//         } catch (error) {
//             utils.showError('Failed to complete calendar authorization');
//             console.error('Authorization error:', error);
//         }
//     },

//     // Load calendar events
//     async loadCalendarEvents() {
//         try {
//             const response = await utils.apiRequest('/calendar/events?days=7');
//             this.displayCalendarEvents(response.events);
//         } catch (error) {
//             console.error('Failed to load calendar events:', error);
//             this.showError('Failed to load calendar events');
//         }
//     },

//     // Display calendar events
//     displayCalendarEvents(events) {
//         const eventsContainer = document.getElementById('calendar-events');

//         if (events.length === 0) {
//             eventsContainer.innerHTML = `
//                 <div class="empty-state">
//                     <p>No upcoming events</p>
//                 </div>
//             `;
//             return;
//         }

//         eventsContainer.innerHTML = events.map(event => {
//             const startTime = new Date(event.start);
//             const endTime = new Date(event.end);
//             const isAllDay = event.all_day;

//             return `
//                 <div class="calendar-event">
//                     <div class="event-title">${event.title}</div>
//                     <div class="event-time">
//                         ${isAllDay ?
//                     startTime.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' }) :
//                     `${utils.formatDateTime(event.start)} - ${endTime.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}`
//                 }
//                     </div>
//                     ${event.location ? `<div class="event-location">${event.location}</div>` : ''}
//                 </div>
//             `;
//         }).join('');
//     },

//     // Show calendar events view
//     showCalendarEvents() {
//         document.getElementById('calendar-connect').style.display = 'none';
//         document.getElementById('calendar-events').style.display = 'block';
//     },

//     // Show connect button
//     showConnectButton() {
//         document.getElementById('calendar-connect').style.display = 'block';
//         document.getElementById('calendar-events').style.display = 'none';
//     },

//     // Show error in calendar section
//     showError(message) {
//         const eventsContainer = document.getElementById('calendar-events');
//         eventsContainer.innerHTML = `
//             <div class="error-state">
//                 <p>${message}</p>
//                 <button class="btn secondary" onclick="calendarManager.loadCalendarEvents()">Retry</button>
//             </div>
//         `;
//     }
// };

const calendarManager = {
    currentView: 'events',

    init() {
        document.getElementById('connect-calendar-btn').addEventListener('click', () => {
            this.connectCalendar();
        });
        document.getElementById('show-events-btn').addEventListener('click', () => {
            this.showCalendarEvents();
        });
        document.getElementById('show-tasks-btn').addEventListener('click', () => {
            this.showCalendarTasks();
        });
        document.getElementById('refresh-calendar-btn').addEventListener('click', () => {
            this.refreshCurrentView();
        });
        document.getElementById('disconnect-calendar-btn').addEventListener('click', () => {
            this.disconnectCalendar();
        });
    },

    async checkIntegration() {
        try {
            const user = await utils.apiRequest('/auth/me');
            if (user.calendar_integrated) {
                document.getElementById('calendar-controls').style.display = 'flex';
                this.showCalendarEvents();
            } else {
                this.showConnectButton();
                document.getElementById('calendar-controls').style.display = 'none';
            }
        } catch (error) {
            this.showConnectButton();
            document.getElementById('calendar-controls').style.display = 'none';
        }
    },

    async connectCalendar() {
        utils.showLoading();
        try {
            const response = await utils.apiRequest('/calendar/authorize', {
                method: 'POST',
                body: JSON.stringify({
                    redirect_uri: `${window.location.origin}/calendar-callback.html`
                })
            });
            const authWindow = window.open(
                response.auth_url,
                'Google Calendar Authorization',
                'width=500,height=600'
            );
            const checkAuth = setInterval(async () => {
                if (authWindow.closed) {
                    clearInterval(checkAuth);
                    utils.hideLoading();
                    await this.checkIntegration();
                }
            }, 1000);
            const messageHandler = async (event) => {
                if (event.data.type === 'calendar-auth-success') {
                    authWindow.close();
                    clearInterval(checkAuth);
                    window.removeEventListener('message', messageHandler);
                    await this.completeAuthorization(event.data.code);
                }
            };
            window.addEventListener('message', messageHandler);
        } catch (error) {
            utils.showError('Failed to connect Google Calendar');
        } finally {
            utils.hideLoading();
        }
    },

    async completeAuthorization(code) {
        try {
            await utils.apiRequest('/calendar/callback', {
                method: 'POST',
                body: JSON.stringify({
                    code: code,
                    redirect_uri: `${window.location.origin}/calendar-callback.html`
                })
            });
            await this.checkIntegration();
        } catch (error) {
            utils.showError('Failed to complete calendar authorization');
        }
    },

    async loadCalendarEvents() {
        try {
            const response = await utils.apiRequest('/calendar/events?days=7');
            this.displayCalendarEvents(response.events);
        } catch (error) {
            this.showError('Failed to load calendar events');
        }
    },

    displayCalendarEvents(events) {
        const eventsContainer = document.getElementById('calendar-events');
        if (!events || events.length === 0) {
            eventsContainer.innerHTML = `<div class="empty-state"><p>No upcoming events</p></div>`;
            return;
        }
        eventsContainer.innerHTML = events.map(event => {
            const startTime = new Date(event.start);
            const endTime = new Date(event.end);
            const isAllDay = event.all_day;
            return `
                <div class="calendar-event">
                    <div class="event-title">${event.title}</div>
                    <div class="event-time">
                        ${isAllDay ?
                    startTime.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' }) :
                    `${utils.formatDateTime(event.start)} - ${endTime.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}`
                }
                    </div>
                    ${event.location ? `<div class="event-location">${event.location}</div>` : ''}
                </div>
            `;
        }).join('');
    },

    async loadCalendarTasks() {
        try {
            const response = await utils.apiRequest('/calendar/tasks');
            this.displayCalendarTasks(response.tasks);
        } catch (error) {
            this.showTasksError('Failed to load tasks');
        }
    },

    displayCalendarTasks(tasks) {
        const tasksContainer = document.getElementById('calendar-tasks');
        if (!tasks || tasks.length === 0) {
            tasksContainer.innerHTML = `<div class="empty-state"><p>No tasks found</p></div>`;
            return;
        }
        tasksContainer.innerHTML = tasks.map(task => `
            <div class="calendar-event">
                <div class="event-title">${task.title}</div>
                <div class="event-time">
                    ${task.due ? `Due: ${utils.formatDateTime(task.due)}` : ''}
                    ${task.completed ? `<span style="color:green;">Completed</span>` : ''}
                </div>
                ${task.notes ? `<div class="event-location">${task.notes}</div>` : ''}
                <div class="event-time">Tasklist: ${task.tasklist || ''}</div>
            </div>
        `).join('');
    },

    showTasksError(message) {
        const tasksContainer = document.getElementById('calendar-tasks');
        tasksContainer.innerHTML = `
            <div class="error-state">
                <p>${message}</p>
                <button class="btn secondary" onclick="calendarManager.loadCalendarTasks()">Retry</button>
            </div>
        `;
    },

    showCalendarEvents() {
        this.currentView = 'events';
        document.getElementById('calendar-connect').style.display = 'none';
        document.getElementById('calendar-events').style.display = 'block';
        document.getElementById('calendar-tasks').style.display = 'none';
        this.loadCalendarEvents();
    },

    showCalendarTasks() {
        this.currentView = 'tasks';
        document.getElementById('calendar-connect').style.display = 'none';
        document.getElementById('calendar-events').style.display = 'none';
        document.getElementById('calendar-tasks').style.display = 'block';
        this.loadCalendarTasks();
    },

    refreshCurrentView() {
        if (this.currentView === 'events') {
            this.loadCalendarEvents();
        } else {
            this.loadCalendarTasks();
        }
    },

    async disconnectCalendar() {
        try {
            await utils.apiRequest('/calendar/disconnect', { method: 'DELETE' });
            utils.showError('Calendar disconnected', 'success-message');
            this.showConnectButton();
            document.getElementById('calendar-controls').style.display = 'none';
        } catch (error) {
            utils.showError('Failed to disconnect calendar');
        }
    },

    showConnectButton() {
        document.getElementById('calendar-connect').style.display = 'block';
        document.getElementById('calendar-events').style.display = 'none';
        document.getElementById('calendar-tasks').style.display = 'none';
    },

    showError(message) {
        const eventsContainer = document.getElementById('calendar-events');
        eventsContainer.innerHTML = `
            <div class="error-state">
                <p>${message}</p>
                <button class="btn secondary" onclick="calendarManager.loadCalendarEvents()">Retry</button>
            </div>
        `;
    }
};

window.addEventListener('DOMContentLoaded', () => {
    calendarManager.init();
    calendarManager.checkIntegration();
});