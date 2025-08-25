// document.addEventListener("DOMContentLoaded", function () {
//   const signInBtn = document.getElementById("signInButton");
//   const signOutBtn = document.getElementById("signOutButton");
//   const userInfo = document.getElementById("userInfo");
//   const meetingsList = document.getElementById("meetingsList");

//   function updateUI(user) {
//     console.log("User object from storage:", user); // Add this line
//     if (user) {
//       userInfo.textContent = `Signed in as: ${user.email} ${user.displayName}`;
//       signInBtn.style.display = "none";
//       signOutBtn.style.display = "block";
//       fetchMeetings(user.stsTokenManager.accessToken);
//     }
//     else { 
//       userInfo.textContent = "Not signed in";
//       signInBtn.style.display = "block";
//       signOutBtn.style.display = "none";
//       meetingsList.innerHTML = "";
//     }
//   }

//   async function fetchMeetings(idToken) {
//     try {
//         console.log("Using ID Token:", idToken);
//         meetingsList.innerHTML = "<p>Loading meetings...</p>";
//       const response = await fetch("http://localhost:8000/api/meetings", {
//         headers: {
//           Authorization: `Bearer ${idToken}`,
//         },
//       });

//       if (!response.ok) {
//         meetingsList.innerHTML = `<p>Error fetching meetings: ${response.status}</p>`;
//         return;
//       }

//       const meetings = await response.json();

//       meetingsList.innerHTML = meetings
//         .map((m) => `<li>${m.title}</li>`)
//         .join("");
//     } catch (err) {
//       meetingsList.innerHTML = `<p>Error: ${err.message}</p>`;
//     }
//   }

//   chrome.storage.local.get(["user"], function (result) {
//     updateUI(result.user);
//   });

//   signInBtn.addEventListener("click", function () {
//     chrome.runtime.sendMessage({ action: "signIn" }, function (response) {
//       if (response && response.user) {
//         updateUI(response.user);
//       } else {
//         userInfo.textContent = "Sign in failed: " + response?.error;
//       }
//     });
//   });

//   signOutBtn.addEventListener("click", function () {
//     chrome.runtime.sendMessage({ action: "signOut" }, function () {
//       updateUI(null);
//     });
//   });
// });
// // This code is for a Chrome extension popup that allows users to sign in with Google and view their meetings.






document.addEventListener("DOMContentLoaded", function () {
  const signInBtn = document.getElementById("signInButton");
  const signOutBtn = document.getElementById("signOutButton");
  const userInfo = document.getElementById("userInfo");
  const meetingsList = document.getElementById("meetingsList");

  let currentMeetingId = null;
  let chatHistory = {};
  let firebaseToken = null;

  const chatBox = document.getElementById("chatBox");
  const chatInput = document.getElementById("chatInput");
  const sendBtn = document.getElementById("sendBtn");
  const voiceBtn = document.getElementById("voiceBtn");
  const meetingSelector = document.getElementById("meetingSelector");

  // ===================== UI NAVIGATION ===================== //
  const sections = document.querySelectorAll(".content-section");
  const navButtons = document.querySelectorAll(".sidebar button");

  navButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      navButtons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      sections.forEach((sec) => (sec.style.display = "none"));

      const targetId =
        btn.id === "navMeetings"
          ? "meetingsSection"
          : btn.id === "navBotChat"
          ? "botChatSection"
          : null;

      if (targetId) {
        const section = document.getElementById(targetId);
        if (section) section.style.display = "block";
      }
    });
  });

  // ===================== AUTH & MEETINGS ===================== //

  function updateUI(user) {
    if (user) {
      userInfo.textContent = `Signed in as: ${user.email} ${user.displayName}`;
      signInBtn.style.display = "none";
      signOutBtn.style.display = "block";

      firebaseToken = user.stsTokenManager.accessToken;
      fetchMeetings();
    } else {
      userInfo.textContent = "Not signed in";
      signInBtn.style.display = "block";
      signOutBtn.style.display = "none";
      meetingsList.innerHTML = "";
    }
  }

  chrome.storage.local.get(["user"], function (result) {
    updateUI(result.user);
  });

  signInBtn.addEventListener("click", function () {
    chrome.runtime.sendMessage({ action: "signIn" }, function (response) {
      if (response && response.user) {
        updateUI(response.user);
      } else {
        userInfo.textContent = "Sign in failed: " + response?.error;
      }
    });
  });

  signOutBtn.addEventListener("click", function () {
    chrome.runtime.sendMessage({ action: "signOut" }, function () {
      updateUI(null);
    });
  });

  async function fetchMeetings() {
    try {
      meetingsList.innerHTML = "<p>Loading meetings...</p>";
      const response = await fetch("http://localhost:8000/api/meetings", {
        headers: {
          Authorization: `Bearer ${firebaseToken}`,
        },
      });

      if (!response.ok) {
        meetingsList.innerHTML = `<p>Error fetching meetings: ${response.status}</p>`;
        return;
      }

      const meetings = await response.json();

      meetingsList.innerHTML = meetings
        .map((m) => {
          const start = new Date(m.start_time).toLocaleString();
          const end = new Date(m.end_time).toLocaleString();
          const description = m.description || "No description";

          return `
            <li class="meeting-card">
              <strong>${m.title}</strong><br>
              🕒 <em>${start}</em> to <em>${end}</em><br>
              📄 ${description}
            </li>`;
        })
        .join("");

      populateMeetingSelector(meetings);
    } catch (err) {
      meetingsList.innerHTML = `<p>Error: ${err.message}</p>`;
    }
  }

  // ===================== MEETING SELECTOR ===================== //

  function populateMeetingSelector(meetings) {
    const select = document.createElement("select");
    select.className = "form-select mb-2";

    meetings.forEach((meeting) => {
      const option = document.createElement("option");
      option.value = meeting._id;
      option.textContent = meeting.title;
      select.appendChild(option);
    });

    select.addEventListener("change", async (e) => {
      currentMeetingId = e.target.value;
      // await loadChatHistory(); 
      chatBox.innerHTML = "";
    });

    meetingSelector.innerHTML = "<label>Select a meeting:</label>";
    meetingSelector.appendChild(select);

    currentMeetingId = meetings[0]?._id;
    loadChatHistory();
  }

  // ===================== CHAT ===================== //

  function renderChat() {
    chatBox.innerHTML = "";
    const history = chatHistory[currentMeetingId] || [];

    history.forEach(({ role, message }) => {
      const msgDiv = document.createElement("div");
      msgDiv.className =
        role === "user" ? "text-end text-primary" : "text-start text-dark";
      msgDiv.innerText = message;
      chatBox.appendChild(msgDiv);
    });

    chatBox.scrollTop = chatBox.scrollHeight;
  }

  function addMessage(role, message) {
    if (!chatHistory[currentMeetingId]) {
      chatHistory[currentMeetingId] = [];
    }
    chatHistory[currentMeetingId].push({ role, message });
    renderChat();
  }

  async function loadChatHistory() {
    if (!currentMeetingId || !firebaseToken) return;
    try {
      const res = await fetch(
        `http://127.0.0.1:8000/api/rag/query/${currentMeetingId}`,
        {
          headers: {
            Authorization: `Bearer ${firebaseToken}`,
          },
        }
      );
      const data = await res.json();
      chatHistory[currentMeetingId] = (data.chat_history || []).map((msg) => ({
      role: msg.user_message ? "user" : "bot",
      message: msg.user_message || msg.ai_response || msg.message,
    }));


      renderChat();
    } catch (err) {
      console.error("Failed to load chat history:", err);
    }
  }

  // ===================== SEND BUTTON ===================== //

  sendBtn.addEventListener("click", async () => {
    const message = chatInput.value.trim();
    if (!message || !currentMeetingId || !firebaseToken) return;

    addMessage("user", message);
    chatInput.value = "";

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/rag/query/${currentMeetingId}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            // Authorization: `Bearer ${firebaseToken}`,
          },
          body: JSON.stringify({ query: message }),
        }
      );

      const data = await response.json();
      addMessage("bot", data.response?.full_response  || "No response");
    } catch (err) {
      addMessage("bot", "Error talking to bot.");
    }
  });

  // ENTER KEY TO SEND
  chatInput.addEventListener("keypress", function (e) {
    if (e.key === "Enter") sendBtn.click();
  });

  // ===================== VOICE BUTTON ===================== //

  voiceBtn.addEventListener("click", async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mediaRecorder = new MediaRecorder(stream);
    const chunks = [];

    mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
    mediaRecorder.onstop = async () => {
      const blob = new Blob(chunks, { type: "audio/webm" });
      const formData = new FormData();
      formData.append("audio", blob);
      formData.append("meeting_id", currentMeetingId);

      try {
        const response = await fetch("http://localhost:8000/api/bot-voice", {
          method: "POST",
          headers: {
            Authorization: `Bearer ${firebaseToken}`,
          },
          body: formData,
        });

        const data = await response.json();
        addMessage("user", "[Voice Input]");
        addMessage("bot", data.reply || "No response from voice");
      } catch (err) {
        addMessage("bot", "Voice processing failed.");
      }
    };

    mediaRecorder.start();
    setTimeout(() => mediaRecorder.stop(), 5000);
  });
});
