// frontend/js/utils.js

// API Configuration
const API_URL = 'http://localhost:8000/api';

// Utility Functions
const utils = {
    // Show loading spinner
    showLoading() {
        document.getElementById('loading-spinner').classList.add('active');
    },

    // Hide loading spinner
    hideLoading() {
        document.getElementById('loading-spinner').classList.remove('active');
    },

    // Show error message
    showError(message, elementId = 'auth-error') {
        const errorElement = document.getElementById(elementId);
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.classList.add('active');
            setTimeout(() => {
                errorElement.classList.remove('active');
            }, 5000);
        }
    },

    // Format date and time
    formatDateTime(dateString) {
        const date = new Date(dateString);
        const options = {
            weekday: 'short',
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        return date.toLocaleDateString('en-US', options);
    },

    // Format date for input
    formatDateForInput(dateString) {
        const date = new Date(dateString);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        return `${year}-${month}-${day}T${hours}:${minutes}`;
    },

    // Make API request
    async apiRequest(endpoint, options = {}) {
        const token = localStorage.getItem('firebaseToken');

        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': token ? `Bearer ${token}` : ''
            }
        };

        const config = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers
            }
        };

        try {
            const response = await fetch(`${API_URL}${endpoint}`, config);

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Request failed');
            }

            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    },

    // Validate meeting form
    validateMeetingForm(formData) {
        const errors = [];

        if (!formData.title || formData.title.trim() === '') {
            errors.push('Meeting title is required');
        }

        if (!formData.start_time) {
            errors.push('Start time is required');
        }

        if (!formData.end_time) {
            errors.push('End time is required');
        }

        if (formData.start_time && formData.end_time) {
            const startTime = new Date(formData.start_time);
            const endTime = new Date(formData.end_time);

            if (endTime <= startTime) {
                errors.push('End time must be after start time');
            }
        }

        if (formData.meeting_link && !this.isValidUrl(formData.meeting_link)) {
            errors.push('Invalid meeting link');
        }

        if (formData.drive_folder_link && !this.isValidUrl(formData.drive_folder_link)) {
            errors.push('Invalid Google Drive link');
        }

        return errors;
    },

    // Validate URL
    isValidUrl(string) {
        try {
            new URL(string);
            return true;
        } catch (_) {
            return false;
        }
    },

    // Debounce function
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};