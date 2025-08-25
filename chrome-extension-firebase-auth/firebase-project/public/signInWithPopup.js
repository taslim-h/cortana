import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import { getAuth, GoogleAuthProvider, signInWithPopup } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";

const firebaseConfig = {
  apiKey: "AIzaSyBLuMniPPU0W2vRDf0bFWNl1PmpLzoYcao",
  authDomain: "cortana-4cc9a.firebaseapp.com",
  projectId: "cortana-4cc9a",
  storageBucket: "cortana-4cc9a.appspot.com",
  messagingSenderId: "822500793872",
  appId: "1:822500793872:web:04e9634c3083b94becf495",
  measurementId: "G-P88XB84E17"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth();
const PROVIDER = new GoogleAuthProvider();
const PARENT_FRAME = document.location.ancestorOrigins[0];

function sendResponse(result) {
  window.parent.postMessage(JSON.stringify(result), PARENT_FRAME);
}

window.addEventListener("message", function ({ data }) {
  if (data.initAuth) {
    signInWithPopup(auth, PROVIDER)
      .then(async (result) => {
        const user = result.user;
        console.log("User from signInWithPopup:", user); // Debug
        // const idToken = await user.getIdToken();
        localStorage.setItem('firebaseToken',  user.stsTokenManager.accessToken); // Store the ID token in local storage
        console.log("User object:",  user.stsTokenManager.accessToken);
        sendResponse({
          user: {
            email: user.email,
            uid: user.uid,
            displayName: user.displayName,
            photoURL: user.photoURL,
            idToken: user.stsTokenManager.accessToken, // Use the access token directly
          },
        });
      })
      .catch((error) => {
        sendResponse({ error: error.message });
      });
  }
});
