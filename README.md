# Cortana - AI-Powered Meeting Assistant

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.8+-brightgreen.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)

**An intelligent meeting assistant with real-time transcription, RAG-powered insights, and seamless Google Workspace integration**

[Features](#-features) • [Architecture](#-architecture) • [Installation](#-installation) • [Usage](#-usage) • [API Documentation](#-api-documentation) • [Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Technology Stack](#-technology-stack)
- [Installation](#-installation)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
  - [Meet Bot Setup](#meet-bot-setup)
  - [Chrome Extension Setup](#chrome-extension-setup)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [System Components](#-system-components)
- [RAG Pipeline](#-rag-pipeline)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

**Cortana** is an advanced AI-powered meeting assistant designed to revolutionize how teams manage, document, and extract insights from meetings. By combining real-time transcription, semantic search, and intelligent document processing, Cortana provides contextual answers and comprehensive meeting summaries through a Retrieval-Augmented Generation (RAG) system.

### Key Highlights

- **Real-time Meeting Transcription**: Automated bot joins Google Meet sessions and captures live transcripts with speaker identification
- **RAG-Powered Q&A**: Query meeting content and related documents using natural language
- **Google Workspace Integration**: Seamless connectivity with Google Drive, Calendar, and Meet
- **Multi-user Support**: Enterprise-ready authentication with Firebase and Google Sign-In
- **Chrome Extension**: Convenient access to meeting insights directly from your browser
- **Vector Search**: Powered by Pinecone for lightning-fast semantic search capabilities

---

## ✨ Features

### = User Management
- **Multi-user Support**: Secure user registration and authentication
- **Authentication Options**:
  - Email/Password authentication via Firebase
  - Google Sign-In (OAuth 2.0)
- **Authorization**: JWT-based secure API access with HTTP header validation

### 📅 Meeting Scheduling & Management
- **Flexible Scheduling**:
  - Set meeting date, time, and duration
  - Add Google Meet links (immediately or later)
  - Connect Google Drive folders for context-aware documents
- **Google Calendar Integration**:
  - Automatic synchronization with Google Calendar
  - Fetch upcoming events and tasks
  - Collision detection for overlapping meetings
- **Google Picker API**:
  - Link Google Drive folders seamlessly
  - Support for multiple Google accounts

### > Intelligent Meeting Bot
- **Automated Meeting Participation**:
  - Python-based bot with Selenium and Undetected Chrome
  - Joins as guest (requires host approval)
  - Automatic caption (CC) activation
- **Real-time Transcription**:
  - Live caption capture with speaker labels
  - Continuous processing with ~58-second RAG availability delay
  - Optimized chunking for minimal latency (8-50 words per chunk)
  - Automatic vectorization and Pinecone upload

### 📁 Document Processing & RAG
- **Multi-format Support**: `.txt`, `.docx`, `.py`, `.md`, images, videos, PDFs
- **Google Drive Integration**:
  - Automatic file fetching from linked folders
  - Document conversion and text extraction
  - Image and video content processing
- **Vector Database**:
  - OpenAI embeddings (text-embedding-ada-002)
  - Pinecone cloud-based vector storage
  - Rich metadata: `meeting_id`, `user_id`, `timestamp`, `speaker_count`
- **Contextual Retrieval**:
  - Semantic search across meeting transcripts
  - Document-based context enhancement
  - Multi-source information synthesis

### 🧩 Chrome Extension
- **Meeting Dashboard**: View all user meetings in one place
- **RAG Chat Interface**:
  - Query meeting metadata
  - Search linked Drive content
  - Access real-time transcriptions
- **Voice Interaction**: Hands-free chatbot queries for accessibility
- **Seamless Authentication**: Uses web app credentials

### = API Layer
- **FastAPI Framework**: High-performance, async Python API
- **RESTful Endpoints**: Standardized HTTP methods
- **Security**:
  - Authorization via HTTP headers
  - Firebase Admin SDK integration
  - JWT token validation
- **CORS Support**: Configurable cross-origin access

---

## <→ Architecture

### System Architecture Overview

```

                         CLIENT LAYER                            
│
  Web Application (Frontend)        Chrome Extension           
  - HTML/CSS/JavaScript              - Firebase Auth            
  - Firebase Authentication          - Meeting Dashboard        
  - Google APIs Integration          - Voice Chat Interface     
│└│
                                                   
               │
                                 HTTPS/REST API
→
                        API LAYER (FastAPI)                      
│
  • Authentication Routes        • Meeting Management            
  • Google Drive Integration     • Google Calendar Sync          
  • RAG Query Endpoints          • Document Processing           
│││
                                             
                                             
→ → →
   MongoDB            Pinecone       Google APIs            
   (Database)         (Vectors)      - Drive API            
                                     - Calendar API         
  • User profiles     • Embeddings   - Meet (via bot)       
  • Meetings          • Metadata   
  • Metadata          • Semantic  
     search    
                      
                              →
                               Vectorization
                              
└
                  BACKGROUND SERVICES                            
│
  Meet Bot (Python/Selenium)         Document Processor         
  - Scheduled meeting joins          - Drive file fetching      
  - Real-time caption capture        - Multi-format conversion  
  - Speaker identification           - Text extraction          
  - Continuous transcription         - Image/Video processing   
  - Auto-vectorization               - Chunking & embedding     

```

### Data Flow

#### 1. Meeting Creation & Document Indexing
```
User → Web App → FastAPI → MongoDB (metadata)
                      →
                 Google Drive API → Fetch Documents
                      →
              Document Processor → Extract & Chunk
                      →
                 OpenAI API → Create Embeddings
                      →
                 Pinecone → Store Vectors
```

#### 2. Real-time Meeting Transcription
```
Scheduler → Check MongoDB → Meeting Due
                →
        Launch Meet Bot (Selenium)
                →
        Join Google Meet as Guest
                →
        Enable Captions → Capture Stream
                →
        Process Captions (8-50 word chunks)
                →
        OpenAI Embedding → Pinecone Upload
                →
        Available for RAG (~58s delay)
```

#### 3. RAG Query Flow
```
User Query → Chrome Extension/Web App
                →
            FastAPI RAG Endpoint
                →
        Query Embedding (OpenAI)
                →
        Semantic Search (Pinecone)
                →
        Retrieve Relevant Chunks
                →
        LLM Generation (Context + Query)
                →
        Response → User
```

---

## =→ Technology Stack

### Backend
- **Framework**: FastAPI 0.104.1
- **Database**: MongoDB (Motor 3.3.2│ PyMongo 4.6.0)
- **Authentication**: Firebase Admin SDK 6.2.0
- **Google APIs**:
  - google-api-python-client 2.110.0
  - google-auth 2.25.0
  - google-auth-oauthlib 1.2.0
- **Security**:
  - python-jose[cryptography] 3.3.0
  - passlib[bcrypt] 1.7.4
- **Server**: Uvicorn 0.24.0
- **Environment**: python-dotenv 1.0.0, pydantic 2.5.0

### Meet Bot
- **Browser Automation**: Selenium, undetected-chromedriver
- **Vector Database**: Pinecone (cloud)
- **Embeddings**: OpenAI API (text-embedding-ada-002)
- **Scheduling**: Python multiprocessing
- **Utilities**: dateutil, pytz, psutil

### Frontend
- **Core**: HTML5, CSS3, JavaScript (ES6+)
- **Authentication**: Firebase JavaScript SDK 10.13.1
- **APIs**: Google Picker API, Google Calendar API

### Chrome Extension
- **Build Tool**: Webpack 5.94.0
- **Dependencies**: Firebase 10.13.1
- **Bundling**: copy-webpack-plugin, html-webpack-plugin

### Infrastructure
- **Vector Search**: Pinecone (cloud-hosted)
- **Database**: MongoDB (local or Atlas)
- **File Storage**: Google Drive API
- **AI/ML**: OpenAI API

---

## 📦 Installation

### Prerequisites

Before installing Cortana, ensure you have the following:

- **Python** 3.8 or higher
- **Node.js** 14 or higher (for Chrome extension build)
- **MongoDB** (local installation or MongoDB Atlas account)
- **Google Cloud Platform** project with enabled APIs:
  - Google Drive API
  - Google Calendar API
- **Firebase** project
- **Pinecone** account with an index created
- **OpenAI** API key

### Backend Setup

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd cortana
```

#### 2. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

#### 3. Configure Environment Variables

Create a `.env` file in the `backend` directory:

```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=meeting_assistant

# Firebase Configuration
FIREBASE_SERVICE_ACCOUNT_JSON_BASE64=<base64-encoded-service-account-json>

# Google OAuth2 Configuration
GOOGLE_CLIENT_ID=<your-google-client-id>.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=<your-google-client-secret>
GOOGLE_REDIRECT_URI=http://localhost:3000/drive-callback.html

# JWT Configuration
SECRET_KEY=<your-secret-key-change-in-production>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Pinecone Configuration
PINECONE_API_KEY=<your-pinecone-api-key>
PINECONE_INDEX_NAME=<your-pinecone-index-name>

# OpenAI Configuration
OPENAI_API_KEY=<your-openai-api-key>
EMBEDDING_MODEL=text-embedding-ada-002
```

#### 4. Firebase Setup

1. Visit [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or select existing
3. Enable Authentication:
   - Navigate to **Authentication > Sign-in method**
   - Enable **Email/Password** provider
   - Enable **Google** provider
4. Generate Service Account Key:
   - Go to **Project Settings > Service Accounts**
   - Click **Generate new private key**
   - Download the JSON file
   - Encode to Base64: `cat service-account.json | base64` (Linux/Mac) or `certutil -encode service-account.json base64.txt` (Windows)
   - Copy the Base64 string to `FIREBASE_SERVICE_ACCOUNT_JSON_BASE64` in `.env`

#### 5. Google Cloud Platform Setup

1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable required APIs:
   - **Google Drive API**
   - **Google Calendar API**
   - **Google Picker API**
4. Create OAuth 2.0 Credentials:
   - Navigate to **APIs & Services > Credentials**
   - Click **Create Credentials > OAuth client ID**
   - Select **Web application**
   - Add authorized redirect URIs:
     - `http://localhost:8000/api/auth/google/callback`
     - `http://localhost:3000/drive-callback.html`
     - `http://localhost:3000/calendar-callback.html`
   - Copy **Client ID** and **Client Secret** to `.env`

#### 6. Pinecone Setup

1. Visit [Pinecone Console](https://app.pinecone.io/)
2. Create a new project
3. Create an index:
   - **Dimensions**: 1536 (for OpenAI text-embedding-ada-002)
   - **Metric**: Cosine
   - **Pod Type**: Starter (free tier) or Standard
4. Copy **API Key** and **Index Name** to `.env`

#### 7. OpenAI API Setup

1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create an API key
3. Copy the key to `OPENAI_API_KEY` in `.env`

#### 8. Run the Backend Server

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

Access API documentation at `http://localhost:8000/docs` (Swagger UI)

---

### Frontend Setup

#### 1. Configure Firebase

Edit `frontend/js/auth.js` and update the Firebase configuration:

```javascript
const firebaseConfig = {
    apiKey: "your-api-key",
    authDomain: "your-project.firebaseapp.com",
    projectId: "your-project-id",
    storageBucket: "your-project.appspot.com",
    messagingSenderId: "your-sender-id",
    appId: "your-app-id"
};
```

Find these values in **Firebase Console > Project Settings > General > Your apps > Web app**

#### 2. Update API Configuration

Edit `frontend/js/utils.js` and ensure the API URL is correct:

```javascript
const API_URL = 'http://localhost:8000';
```

#### 3. Serve the Frontend

**Option 1: Using Python**
```bash
cd frontend
python -m http.server 3000
```

**Option 2: Using Node.js http-server**
```bash
npm install -g http-server
cd frontend
http-server -p 3000
```

**Option 3: Using VS Code Live Server**
- Install the "Live Server• extension
- Right-click on `frontend/index.html`
- Select "Open with Live Server"

The frontend will be available at `http://localhost:3000`

---

### Meet Bot Setup

#### 1. Install Additional Dependencies

```bash
cd meet_bot
pip install selenium undetected-chromedriver pinecone-client openai python-dotenv pymongo dateutil pytz psutil
```

#### 2. Configure Environment Variables

Create a `.env` file in the `meet_bot` directory (or use the same `.env` from backend):

```env
PINECONE_API_KEY=<your-pinecone-api-key>
PINECONE_INDEX_NAME=<your-pinecone-index-name>
OPENAI_API_KEY=<your-openai-api-key>
EMBEDDING_MODEL=text-embedding-ada-002
```

#### 3. Install Chrome/Chromium

Ensure Google Chrome or Chromium is installed on your system. The bot uses undetected-chromedriver which will automatically download the appropriate ChromeDriver version.

#### 4. Run the Meet Bot Scheduler

```bash
cd meet_bot
python bot_transcription.py
```

The bot will:
- Check MongoDB every 60 seconds for upcoming meetings
- Automatically join meetings at scheduled times
- Capture and process real-time transcriptions
- Upload vectorized chunks to Pinecone

---

### Chrome Extension Setup

#### 1. Install Dependencies

```bash
cd chrome-extension-firebase-auth/chrome-extension
npm install
```

#### 2. Configure Firebase

Edit `chrome-extension-firebase-auth/chrome-extension/src/popup/popup.js` (or equivalent config file) and update Firebase configuration:

```javascript
const firebaseConfig = {
    apiKey: "your-api-key",
    authDomain: "your-project.firebaseapp.com",
    projectId: "your-project-id",
    storageBucket: "your-project.appspot.com",
    messagingSenderId: "your-sender-id",
    appId: "your-app-id"
};
```

#### 3. Build the Extension

```bash
npm run release
```

This will create a `dist` folder and a `dist.zip` file.

#### 4. Load in Chrome

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable **Developer mode** (toggle in top-right corner)
3. Click **Load unpacked**
4. Select the `dist` folder from the extension directory
5. The extension will now appear in your Chrome toolbar

#### 5. Login

- Click the extension icon
- Login with your web app credentials
- Access your meetings and chat with the RAG system

---

## → Configuration

### MongoDB Configuration

**Local MongoDB**:
```bash
# Start MongoDB
mongod --dbpath /path/to/data/directory
```

**MongoDB Atlas** (Cloud):
1. Create a free cluster at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Set up database user and network access
3. Get connection string and update `MONGODB_URL` in `.env`:
```env
MONGODB_URL=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/<database>?retryWrites=true&w=majority
```

### Timezone Configuration

The meet bot uses Asia/Dhaka timezone by default. To change:

Edit `meet_bot/bot_transcription.py`:
```python
LOCAL_TZ = pytz.timezone('Your/Timezone')  # e.g.│ 'America/New_York'
```

### RAG System Configuration

**Chunking Parameters** (in `meet_bot/bot_transcription.py`):
```python
self.min_chunk_words = 8    # Minimum words before upload
self.max_chunk_words = 50   # Maximum words per chunk
self.max_chunk_seconds = 8  # Force upload interval (seconds)
```

**Embedding Model**:
- Default: `text-embedding-ada-002` (1536 dimensions)
- Alternative: `text-embedding-3-small` (512 dimensions) - requires Pinecone index update

---

## 🚀 Usage

### 1. Register/Login

1. Open `http://localhost:3000` in your browser
2. Click **Sign Up** to create a new account or **Sign In** with email/Google
3. After authentication│ you'll be redirected to the dashboard

### 2. Create a Meeting

1. Click the **+ New Meeting** button
2. Fill in the meeting details:
   - **Title**: Meeting name
   - **Start Time**: When the meeting begins
   - **End Time**: When the meeting ends
   - **Meeting Link**: Google Meet URL (optional, can be added later)
   - **Google Drive Folder**: Link to a Google Drive folder for context documents
   - **Description**: Additional notes
3. Click **Create Meeting**

### 3. Connect Google Calendar

1. Click **Connect Calendar** in the sidebar
2. Authorize access to your Google Calendar
3. Your upcoming events will be displayed automatically

### 4. Link Google Drive Folder

1. When creating/editing a meeting, click **Select Drive Folder**
2. The Google Picker will open
3. Select the folder containing relevant documents
4. Files will be automatically processed and vectorized

### 5. Bot Joins Meeting

**Automated Process**:
- The meet bot scheduler checks for upcoming meetings every 60 seconds
- When a meeting is due, the bot automatically:
  - Joins the Google Meet session as a guest
  - Waits for host approval
  - Enables captions
  - Starts capturing and processing transcriptions

**Manual Monitoring**:
```bash
# Watch the bot logs
cd meet_bot
python bot_transcription.py
```

### 6. Query with RAG (Chrome Extension)

1. Click the **Cortana** extension icon in Chrome
2. Login with your credentials
3. View your meetings list
4. Select a meeting to query
5. Ask questions like:
   - "What were the main action items discussed?"
   - "Who mentioned the budget constraints?"
   - "Summarize the Q3 strategy discussion"
6. Use the microphone icon for voice queries

### 7. Query with RAG (Web App)

The web app can be extended to include a chat interface. Currently│ RAG is primarily accessed via the Chrome extension.

---

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword",
  "display_name": "John Doe"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "uid": "user-id",
    "email": "user@example.com",
    "display_name": "John Doe"
  }
}
```

### Meeting Endpoints

#### Create Meeting
```http
POST /api/meetings
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Team Standup",
  "start_time": "2025-10-12T10:00:00",
  "end_time": "2025-10-12T10:30:00",
  "meeting_link": "https://meet.google.com/abc-defg-hij",
  "drive_folder_id": "1a2b3c4d5e6f",
  "description": "Daily team sync"
}
```

#### Get User Meetings
```http
GET /api/meetings
Authorization: Bearer <token>
```

#### Update Meeting
```http
PUT /api/meetings/{meeting_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Updated Title",
  "meeting_link": "https://meet.google.com/new-link"
}
```

#### Delete Meeting
```http
DELETE /api/meetings/{meeting_id}
Authorization: Bearer <token>
```

### Google Drive Endpoints

#### Connect Drive
```http
GET /api/drive/auth
Authorization: Bearer <token>
```

#### Get Folder Contents
```http
GET /api/drive/folder/{folder_id}
Authorization: Bearer <token>
```

#### Process Drive Files
```http
POST /api/drive/process
Authorization: Bearer <token>
Content-Type: application/json

{
  "folder_id": "1a2b3c4d5e6f",
  "meeting_id": "meeting-id-123"
}
```

### Google Calendar Endpoints

#### Connect Calendar
```http
GET /api/calendar/auth
Authorization: Bearer <token>
```

#### Get Upcoming Events
```http
GET /api/calendar/events
Authorization: Bearer <token>
```

### RAG Endpoints

#### Query RAG System
```http
POST /api/rag/query
Authorization: Bearer <token>
Content-Type: application/json

{
  "query": "What were the action items from the meeting?",
  "meeting_id": "meeting-id-123",
  "top_k": 5
}
```

**Response**:
```json
{
  "query": "What were the action items from the meeting?",
  "answer": "The main action items discussed were...",
  "sources": [
    {
      "chunk_id": "meeting-123_chunk_0001",
      "text": "Action item 1: Complete the proposal by Friday...",
      "score": 0.92,
      "metadata": {
        "speaker_count": 2,
        "timestamp": "2025-10-12T10:15:00Z"
      }
    }
  ]
}
```

### Interactive API Documentation

Visit `http://localhost:8000/docs` for Swagger UI with interactive API testing.

---

## 🧩 System Components

### 1. Backend (FastAPI)

**Location**: `backend/app/`

**Structure**:
```
backend/app/
 config.py              # Configuration management
 main.py                # Application entry point
 factory.py             # Application factory
 models/
    user.py            # User data models
    meeting.py         # Meeting data models
 routes/
    auth.py            # Authentication routes
    meetings.py        # Meeting management routes
    google_drive.py    # Google Drive integration
    google_calendar.py # Google Calendar integration
    rag.py             # RAG query endpoints
 services/
    firebase_auth.py   # Firebase authentication
    mongodb.py         # Database operations
    meeting_service.py # Meeting business logic
    google_services.py # Google API integration
    document_processor.py # Document processing
    image_processor.py # Image content extraction
    GoogleVideoProcessor.py # Video processing
    indexing_service.py # Vector indexing
    rag_service.py     # RAG query logic
    chat_service.py    # Chat interface
 utils/
     validators.py      # Input validation
```

**Key Features**:
- Async/await support for high performance
- Dependency injection for services
- JWT-based authentication middleware
- CORS configuration for cross-origin requests
- Comprehensive error handling

### 2. Meet Bot

**Location**: `meet_bot/bot_transcription.py`

**Key Classes**:
- **`GoogleMeetBot`**: Handles meeting joining and management
- **`CaptionProcessor`**: Processes and chunks transcriptions
- **`CaptionCapture`**: Captures real-time captions from Google Meet
- **`DatabaseManager`**: MongoDB operations for meeting scheduling

**Features**:
- Selenium-based browser automation
- Undetected ChromeDriver to avoid bot detection
- Real-time caption processing with duplicate detection
- Optimized chunking for minimal RAG latency
- Automatic vectorization and Pinecone upload
- Multi-threaded caption capture
- Graceful cleanup and error handling

**Processing Pipeline**:
```
Caption Detected → Deduplicate → Accumulate →
Check Thresholds → Create Chunk → Generate Embedding →
Upload to Pinecone (with metadata)
```

### 3. Frontend (Web Application)

**Location**: `frontend/`

**Structure**:
```
frontend/
 index.html             # Main application page
 drive-callback.html    # Google Drive OAuth callback
 calendar-callback.html # Google Calendar OAuth callback
 css/
    styles.css         # Application styles
 js/
     auth.js            # Firebase authentication
     app.js             # Main application logic
     meetings.js        # Meeting management
     calendar.js        # Calendar integration
     drive.js           # Drive integration
     drive-picker.js    # Google Picker implementation
     utils.js           # Utility functions
```

**Features**:
- Firebase authentication UI
- Meeting CRUD operations
- Google Calendar event display
- Google Drive folder picker
- Real-time meeting updates
- Responsive design

### 4. Chrome Extension

**Location**: `chrome-extension-firebase-auth/chrome-extension/`

**Structure**:
```
chrome-extension/
 manifest.json          # Extension manifest
 webpack.config.js      # Build configuration
 package.json           # Dependencies
 src/
     background/        # Background scripts
        background.js  # Service worker
     popup/             # Extension popup
         popup.html     # Popup UI
         popup.js       # Popup logic
         popup.css      # Popup styles
```

**Features**:
- Firebase authentication
- Meeting list view
- RAG chat interface
- Voice input support
- Real-time query responses

---

## 🔍 RAG Pipeline

### Document Processing Pipeline

```
Google Drive Folder
        →
Fetch Files (Drive API)
        →
File Type Detection
        →
└
                                   
Text Files         Images/Videos    PDFs
    →                   →             →
Extract Text     OCR/Vision API  PDF Parser
    →                   →             →
│
        →
    Clean & Normalize
        →
    Chunk (500-1000 chars)
        →
    Generate Embeddings (OpenAI)
        →
    Store in Pinecone (with metadata)
```

### Real-time Transcription Pipeline

```
Google Meet Session
        →
Caption Stream (Selenium)
        →
Speaker Identification
        →
Duplicate Detection
        →
Accumulate Text (8-50 words)
        →
Semantic Boundary Detection
        →
Create Conversation Chunk
        →
Generate Embedding (OpenAI)
        →
Upload to Pinecone
        →
Available for RAG (~58s from speech)
```

### Query Pipeline

```
User Query
    →
Generate Query Embedding (OpenAI)
    →
Semantic Search (Pinecone)
    →
Retrieve Top K Chunks (k=5)
    →
Filter by meeting_id/user_id
    →
Construct Context Window
    →
LLM Generation (GPT-4/GPT-3.5)
    →
Return Answer + Sources
```

### Metadata Schema

**Pinecone Vector Metadata**:
```json
{
  "meeting_id": "507f1f77bcf86cd79943901",
  "user_id": "user-abc-123",
  "text": "Excerpt of the conversation or document content...",
  "chunk_id": "meeting-123_chunk_0042",
  "chunk_number": 42,
  "timestamp": "2025-10-12T10:15:30.123Z",
  "chunk_start": "2025-10-12T10:15:00Z",
  "chunk_end": "2025-10-12T10:15:30Z",
  "speaker_count": 2,
  "word_count": 35,
  "processing_mode": "rapid_real_time",
  "source_type": "transcript|document|image|video"
}
```

---

## =→ Troubleshooting

### Common Issues

#### 1. Firebase Authentication Errors

**Symptom**: "Firebase configuration error• or authentication fails

**Solutions**:
- Verify Firebase configuration in `frontend/js/auth.js` and extension config
- Ensure Email/Password and Google providers are enabled in Firebase Console
- Check that domain is authorized: **Firebase Console > Authentication > Settings > Authorized domains**
- Confirm service account JSON is correctly Base64-encoded in backend `.env`

#### 2. MongoDB Connection Errors

**Symptom**: "Failed to connect to MongoDB"

**Solutions**:
- **Local MongoDB**: Ensure MongoDB service is running (`mongod`)
- **MongoDB Atlas**:
  - Check connection string in `.env`
  - Verify IP whitelist in **MongoDB Atlas > Network Access**
  - Confirm database user credentials
- Test connection: `mongosh "mongodb://localhost:27017"` or `mongosh "<atlas-connection-string>"`

#### 3. Google API Errors

**Symptom**: "API not enabled• or "Invalid credentials"

**Solutions**:
- Verify APIs are enabled: **Google Cloud Console > APIs & Services > Library**
  - Google Drive API
  - Google Calendar API
  - Google Picker API
- Check OAuth 2.0 credentials and redirect URIs in **Google Cloud Console > Credentials**
- Ensure scopes are correctly set in API requests
- Verify client ID and secret in `.env`

#### 4. Pinecone Connection Errors

**Symptom**: "Index not found• or "Failed to connect to Pinecone"

**Solutions**:
- Verify API key in `.env`: `PINECONE_API_KEY`
- Confirm index name matches: `PINECONE_INDEX_NAME`
- Check index dimensions match embedding model (1536 for text-embedding-ada-002)
- Test connection:
  ```python
  from pinecone import Pinecone
  pc = Pinecone(api_key="your-key")
  pc.list_indexes()
  ```

#### 5. Meet Bot Not Joining Meetings

**Symptom**: Bot doesn't join scheduled meetings

**Solutions**:
- Ensure `bot_transcription.py` is running: `python meet_bot/bot_transcription.py`
- Check MongoDB has meetings with `meeting_link` set
- Verify meeting times are correct (check timezone settings)
- Ensure Chrome/Chromium is installed
- Check logs for error messages
- Manually test: Add a meeting with `start_time` in the next 2 minutes

#### 6. Captions Not Captured

**Symptom**: Bot joins but no transcriptions appear in Pinecone

**Solutions**:
- **Host must enable captions** in Google Meet
- **Host must admit the bot** from the waiting room
- Check bot logs for "Caption container not found• errors
- Verify caption selectors haven't changed (Google Meet UI updates)
- Test manually by joining a Meet with captions enabled

#### 7. CORS Errors

**Symptom**: "CORS policy blocked• in browser console

**Solutions**:
- Backend CORS is configured for all origins in development (`allow_origins=["*"]`)
- For production, update `app/main.py` or `app/factory.py`:
  ```python
  app.add_middleware(
      CORSMiddleware│
      allow_origins=["https://yourdomain.com"]│  # Specify allowed domains
      allow_credentials=True│
      allow_methods=["*"]│
      allow_headers=["*"]│
  )
  ```

#### 8. Chrome Extension Not Loading

**Symptom**: Extension fails to load or shows errors

**Solutions**:
- Rebuild extension: `cd chrome-extension && npm run release`
- Check for build errors in terminal
- Verify `dist` folder is created
- In Chrome: `chrome://extensions/` → **Reload** extension
- Check browser console for errors
- Ensure Firebase config is correct in extension files

#### 9. OpenAI API Errors

**Symptom**: "Rate limit exceeded• or "Invalid API key"

**Solutions**:
- Verify `OPENAI_API_KEY` in `.env`
- Check API usage limits at [OpenAI Dashboard](https://platform.openai.com/usage)
- Ensure billing is enabled for your OpenAI account
- For rate limits, implement backoff/retry logic or upgrade plan

#### 10. RAG Queries Return No Results

**Symptom**: "No relevant information found"

**Solutions**:
- Verify documents are uploaded to Pinecone:
  ```python
  index.describe_index_stats()  # Check total_vector_count
  ```
- Check `meeting_id` and `user_id` filters in query
- Ensure embeddings were created successfully (check logs)
- Try querying without filters for testing
- Verify Pinecone index metric is "cosine"

---

### Debugging Tips

#### 1. Enable Detailed Logging

**Backend**:
Edit `backend/app/main.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Meet Bot**:
Already enabled in `meet_bot/bot_transcription.py`:
```python
logging.basicConfig(level=logging.INFO│ format='%(asctime)s - %(levelname)s - %(message)s')
```

#### 2. Monitor API Requests

Use browser **Network tab** (F12) to inspect:
- Request/response payloads
- HTTP status codes
- Authorization headers

#### 3. Database Inspection

**MongoDB Compass** (GUI):
- Download: [MongoDB Compass](https://www.mongodb.com/try/download/compass)
- Connect to your database
- Inspect `meetings`, `users` collections

**Mongo Shell**:
```bash
mongosh "mongodb://localhost:27017/meeting_assistant"
db.meetings.find().pretty()
db.users.find().pretty()
```

#### 4. Pinecone Vector Inspection

```python
from pinecone import Pinecone

pc = Pinecone(api_key="your-key")
index = pc.Index("your-index-name")

# Check index stats
stats = index.describe_index_stats()
print(f"Total vectors: {stats['total_vector_count']}")

# Query vectors
results = index.query(
    vector=[0.0]*1536│  # Dummy vector
    top_k=10│
    include_metadata=True
)
print(results)
```

#### 5. Test Individual Components

**Test OpenAI Embeddings**:
```python
from openai import OpenAI
client = OpenAI(api_key="your-key")

response = client.embeddings.create(
    model="text-embedding-ada-002"│
    input="Test text"
)
print(f"Embedding dimensions: {len(response.data[0].embedding)}")
```

**Test Firebase Auth**:
```python
import firebase_admin
from firebase_admin import credentials│ auth

cred = credentials.Certificate("path/to/serviceAccountKey.json")
firebase_admin.initialize_app(cred)

user = auth.get_user_by_email("test@example.com")
print(f"User: {user.uid}")
```

---

## > Contributing

We welcome contributions to Cortana! Here's how you can help:

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**:
   - Follow existing code style
   - Add comments for complex logic
   - Update documentation if needed
4. **Test your changes**:
   - Ensure all existing functionality works
   - Add unit tests for new features
5. **Commit your changes**:
   ```bash
   git commit -m "feat: add new feature description"
   ```
   Use conventional commit messages:
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `refactor:` Code refactoring
   - `test:` Test additions/modifications
6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Create a Pull Request**:
   - Provide a clear description of changes
   - Reference any related issues
   - Ensure CI checks pass

### Code Style

- **Python**: Follow PEP 8 guidelines
- **JavaScript**: Use ES6+ syntax, consistent indentation (2 spaces)
- **Naming**: Descriptive variable/function names
- **Comments**: Explain "why• not "what"

### Testing

```bash
# Backend tests (if implemented)
cd backend
pytest

# Frontend tests (if implemented)
cd frontend
npm test
```

### Reporting Issues

Use GitHub Issues to report bugs or request features:
- **Bug Report**: Describe the issue, steps to reproduce, expected vs actual behavior
- **Feature Request**: Describe the feature, use case, and potential implementation

---

## 📄 License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2025 Cortana Team

Permission is hereby granted│ free of charge│ to any person obtaining a copy
of this software and associated documentation files (the "Software")│ to deal
in the Software without restriction│ including without limitation the rights
to use│ copy│ modify│ merge│ publish│ distribute│ sublicense│ and/or sell
copies of the Software│ and to permit persons to whom the Software is
furnished to do so│ subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS"│ WITHOUT WARRANTY OF ANY KIND│ EXPRESS OR
IMPLIED│ INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY│
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM│ DAMAGES OR OTHER
LIABILITY│ WHETHER IN AN ACTION OF CONTRACT│ TORT OR OTHERWISE│ ARISING FROM│
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 Acknowledgments

- **FastAPI**: For the excellent async web framework
- **Firebase**: For authentication and infrastructure
- **Pinecone**: For vector database capabilities
- **OpenAI**: For embeddings and language models
- **Google**: For Workspace API integrations
- **Selenium**: For browser automation
- **MongoDB**: For flexible document storage

---

## 📧 Contact & Support

For questions│ support│ or feedback:

- **GitHub Issues**: [Create an issue](https://github.com/your-repo/cortana/issues)
- **Email**: support@cortana-ai.com (replace with actual email)
- **Documentation**: [Full Documentation](https://docs.cortana-ai.com) (if available)

---

## =→ Roadmap

### Planned Features

- [ ] **Multi-language Support**: Support for non-English transcriptions
- [ ] **Advanced Analytics**: Meeting sentiment analysis, participation metrics
- [ ] **Slack Integration**: Notifications and bot commands via Slack
- [ ] **Microsoft Teams Support**: Extend bot to Teams meetings
- [ ] **Automated Summaries**: AI-generated meeting summaries sent via email
- [ ] **Action Item Tracking**: Extract and assign action items with deadlines
- [ ] **Mobile App**: React Native or Flutter app for iOS/Android
- [ ] **Offline Mode**: Local RAG for sensitive meetings
- [ ] **Custom LLM Support**: Integration with local/open-source LLMs
- [ ] **Video Highlights**: Automatic extraction of key meeting moments
- [ ] **Speaker Diarization**: Enhanced speaker identification with voice fingerprinting
- [ ] **Collaborative Editing**: Real-time collaborative meeting notes

---

<div align="center">

**Built with d by the Cortana Team**

⭐ Star this repository if you find it useful!

[Report Bug](https://github.com/your-repo/cortana/issues) • [Request Feature](https://github.com/your-repo/cortana/issues)

</div>
