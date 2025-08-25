const FIREBASE_HOSTING_URL = "https://cortana-4cc9a.web.app",
    iframe = document.createElement("iframe");
iframe.src = FIREBASE_HOSTING_URL, document.body.appendChild(iframe), chrome.runtime.onMessage.addListener((e, t, r) => {
    if ("getAuth" === e.action && "offscreen" === e.target) return window.addEventListener("message", function e({
        data: t
    }) {
        try {
            const n = JSON.parse(t);
            window.removeEventListener("message", e), r(n.user)
        } catch (e) {
            console.error("Error parsing iframe message:", e)
        }
    }), iframe.contentWindow.postMessage({
        initAuth: !0
    }, FIREBASE_HOSTING_URL), !0
});


        // // Your Firebase hosting URL
        // const FIREBASE_HOSTING_URL = "https://cortana-4cc9a.web.app";
        
        // // Create iframe for Firebase auth
        // const iframe = document.createElement("iframe");
        // iframe.src = FIREBASE_HOSTING_URL;
        // iframe.style.display = "none"; // Hidden iframe
        // iframe.style.width = "0";
        // iframe.style.height = "0";
        // document.body.appendChild(iframe);

        // // Listen for messages from background script
        // chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
        //     if (request.action === "getAuth" && request.target === "offscreen") {
        //         handleAuthRequest(sendResponse);
        //         return true; // Keep message channel open for async response
        //     } else if (request.action === "signOut" && request.target === "offscreen") {
        //         handleSignOut(sendResponse);
        //         return true;
        //     }
        // });

        // // Handle authentication request
        // function handleAuthRequest(sendResponse) {
        //     // Set up message listener for iframe response
        //     const messageHandler = function(event) {
        //         // Verify origin for security
        //         if (event.origin !== FIREBASE_HOSTING_URL) {
        //             console.warn("Received message from unauthorized origin:", event.origin);
        //             return;
        //         }

        //         try {
        //             const data = typeof event.data === 'string' ? JSON.parse(event.data) : event.data;
                    
        //             if (data.user) {
        //                 // Clean up listener
        //                 window.removeEventListener("message", messageHandler);
                        
        //                 // Send user data back to background script
        //                 sendResponse(data.user);
        //             } else if (data.error) {
        //                 // Handle authentication error
        //                 window.removeEventListener("message", messageHandler);
        //                 sendResponse({ error: data.error });
        //             }
        //         } catch (error) {
        //             console.error("Error parsing iframe message:", error);
        //             window.removeEventListener("message", messageHandler);
        //             sendResponse({ error: "Failed to parse authentication response" });
        //         }
        //     };

        //     // Add message listener
        //     window.addEventListener("message", messageHandler);

        //     // Send authentication request to iframe
        //     try {
        //         iframe.contentWindow.postMessage({ 
        //             action: "initAuth",
        //             initAuth: true 
        //         }, FIREBASE_HOSTING_URL);
        //     } catch (error) {
        //         console.error("Error sending message to iframe:", error);
        //         window.removeEventListener("message", messageHandler);
        //         sendResponse({ error: "Failed to communicate with authentication service" });
        //     }

        //     // Set timeout for authentication (30 seconds)
        //     setTimeout(() => {
        //         window.removeEventListener("message", messageHandler);
        //         sendResponse({ error: "Authentication timeout" });
        //     }, 30000);
        // }

        // // Handle sign out request
        // function handleSignOut(sendResponse) {
        //     const messageHandler = function(event) {
        //         if (event.origin !== FIREBASE_HOSTING_URL) {
        //             return;
        //         }

        //         try {
        //             const data = typeof event.data === 'string' ? JSON.parse(event.data) : event.data;
                    
        //             if (data.signedOut || data.success) {
        //                 window.removeEventListener("message", messageHandler);
        //                 sendResponse({ success: true });
        //             }
        //         } catch (error) {
        //             console.error("Error during sign out:", error);
        //             window.removeEventListener("message", messageHandler);
        //             sendResponse({ error: "Sign out failed" });
        //         }
        //     };

        //     window.addEventListener("message", messageHandler);

        //     try {
        //         iframe.contentWindow.postMessage({ 
        //             action: "signOut"
        //         }, FIREBASE_HOSTING_URL);
        //     } catch (error) {
        //         console.error("Error sending sign out message:", error);
        //         window.removeEventListener("message", messageHandler);
        //         sendResponse({ error: "Failed to sign out" });
        //     }

        //     // Timeout for sign out
        //     setTimeout(() => {
        //         window.removeEventListener("message", messageHandler);
        //         sendResponse({ success: true }); // Assume success even if no response
        //     }, 5000);
        // }

        // // Handle iframe load
        // iframe.onload = function() {
        //     console.log("Firebase auth iframe loaded successfully");
            
        //     // Optional: Send a ping to verify communication
        //     try {
        //         iframe.contentWindow.postMessage({ 
        //             action: "ping" 
        //         }, FIREBASE_HOSTING_URL);
        //     } catch (error) {
        //         console.error("Error pinging iframe:", error);
        //     }
        // };

        // iframe.onerror = function() {
        //     console.error("Failed to load Firebase auth iframe");
        // };

        // // Listen for general messages from iframe (for debugging/status)
        // window.addEventListener("message", function(event) {
        //     if (event.origin !== FIREBASE_HOSTING_URL) {
        //         return;
        //     }

        //     try {
        //         const data = typeof event.data === 'string' ? JSON.parse(event.data) : event.data;
                
        //         // Handle status messages
        //         if (data.status) {
        //             console.log("Firebase auth status:", data.status);
        //         } else if (data.pong) {
        //             console.log("Firebase auth iframe is responsive");
        //         }
        //     } catch (error) {
        //         // Ignore parsing errors for non-JSON messages
        //     }
        // });

        // // Log that offscreen document is ready
        // console.log("Firebase Auth offscreen document ready");
        // console.log("Firebase hosting URL:", FIREBASE_HOSTING_URL);
    