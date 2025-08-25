// Storage utilities for Chrome extension
class StorageManager {
    // Get items from chrome.storage.local
    static async get(keys) {
        return new Promise((resolve, reject) => {
            chrome.storage.local.get(keys, (result) => {
                if (chrome.runtime.lastError) {
                    reject(chrome.runtime.lastError);
                } else {
                    resolve(result);
                }
            });
        });
    }

    // Set items in chrome.storage.local
    static async set(items) {
        return new Promise((resolve, reject) => {
            chrome.storage.local.set(items, () => {
                if (chrome.runtime.lastError) {
                    reject(chrome.runtime.lastError);
                } else {
                    resolve();
                }
            });
        });
    }

    // Remove items from chrome.storage.local
    static async remove(keys) {
        return new Promise((resolve, reject) => {
            chrome.storage.local.remove(keys, () => {
                if (chrome.runtime.lastError) {
                    reject(chrome.runtime.lastError);
                } else {
                    resolve();
                }
            });
        });
    }

    // Clear all items from chrome.storage.local
    static async clear() {
        return new Promise((resolve, reject) => {
            chrome.storage.local.clear(() => {
                if (chrome.runtime.lastError) {
                    reject(chrome.runtime.lastError);
                } else {
                    resolve();
                }
            });
        });
    }

    // Get chat history for a meeting
    static async getChatHistory(meetingId) {
        const result = await this.get([`chat_${meetingId}`]);
        return result[`chat_${meetingId}`] || [];
    }

    // Set chat history for a meeting
    static async setChatHistory(meetingId, history) {
        await this.set({ [`chat_${meetingId}`]: history });
    }

    // Add message to chat history
    static async addChatMessage(meetingId, role, message) {
        const history = await this.getChatHistory(meetingId);
        history.push({ role, message, timestamp: Date.now() });
        await this.setChatHistory(meetingId, history);
        return history;
    }

    // Clear chat history for a meeting
    static async clearChatHistory(meetingId) {
        await this.remove([`chat_${meetingId}`]);
    }
}

// Export to global scope
window.StorageManager = StorageManager;