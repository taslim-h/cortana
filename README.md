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

