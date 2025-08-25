// API utilities for backend communication
class ApiManager {
    constructor() {
        this.baseURL = 'http://localhost:8000/api';
        this.ragURL = 'http://127.0.0.1:8000/api';
    }

    // Get authorization headers
    getAuthHeaders() {
        const token = window.authManager?.getToken();
        return {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` })
        };
    }

    // Generic fetch wrapper with error handling
    async fetch(url, options = {}) {
        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    ...this.getAuthHeaders(),
                    ...options.headers
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Fetch meetings from backend
    async fetchMeetings() {
        const url = `${this.baseURL}/meetings`;
        return await this.fetch(url);
    }

    // Load chat history for a meeting
    // async loadChatHistory(meetingId) {
    //     const url = `${this.ragURL}/rag/query/${meetingId}`;
    //     try {
    //         const data = await this.fetch(url);
    //         return (data.chat_history || []).map(msg => ({
    //             role: msg.user_message ? 'user' : 'bot',
    //             message: msg.user_message || msg.ai_response || msg.message,
    //             timestamp: msg.timestamp || Date.now()
    //         }));
    //     } catch (error) {
    //         console.error('Failed to load chat history:', error);
    //         return [];
    //     }
    // }

    async loadChatHistory(meetingId) {
    const url = `${this.ragURL}/rag/history/${meetingId}`;
    try {
        const data = await this.fetch(url);
         // Sort chat_history by timestamp ascending
        const sortedHistory = (data.chat_history || []).sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
        // Map each chat_history item to user and bot messages
        const history = [];
        sortedHistory.forEach(msg => {
            if (msg.user_query) {
                history.push({
                    role: 'user',
                    message: msg.user_query,
                    timestamp: msg.timestamp || Date.now()
                });
            }
            if (msg.response) {
                history.push({
                    role: 'bot',
                    message: msg.response,
                    timestamp: msg.timestamp || Date.now()
                });
            }
        });
        return history;
    } catch (error) {
        console.error('Failed to load chat history:', error);
        return [];
    }
}

    // Send chat message to RAG system
    async sendChatMessage(meetingId, message) {
        const url = `${this.ragURL}/rag/query/${meetingId}`;
        const data = await this.fetch(url, {
            method: 'POST',
            body: JSON.stringify({ query: message })
        });
        
        return data.response?.full_response || data.response || 'No response';
    }

    // Send voice message to bot
    async sendVoiceMessage(meetingId, audioBlob) {
        const url = `${this.baseURL}/bot-voice`;
        const formData = new FormData();
        formData.append('audio', audioBlob);
        formData.append('meeting_id', meetingId);

        const token = window.authManager?.getToken();
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                ...(token && { 'Authorization': `Bearer ${token}` })
            },
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        return data.reply || 'No response from voice';
    }
}

// Export singleton instance
window.apiManager = new ApiManager();