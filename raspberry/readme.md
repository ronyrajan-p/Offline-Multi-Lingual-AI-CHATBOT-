# Offline Raspberry Pi Multilingual AI Chatbot

This project is a fully offline multilingual AI chatbot for Raspberry Pi. It is designed to run without internet access by using a local AI model, offline translation, and local storage.

## Purpose

This chatbot is for environments where internet access is unavailable, unreliable, expensive, or not allowed. It focuses on offline operation, privacy, local AI inference, local translation, and Raspberry Pi performance optimization.

## Architecture

```text
Touchscreen / Monitor
        |
        v
Local Chat UI
        |
        v
FastAPI Backend
        |
 +------+----------------+
 |      |                |
LLM  Offline Translator SQLite
 |      |
 +------+----------------+
        |
        v
    Response
```

## Recommended Folder Structure

```text
raspberry/
|
+-- frontend/
|   +-- src/
|   +-- public/
|   +-- package.json
|
+-- backend/
|   +-- main.py
|   +-- routes/
|   +-- services/
|   +-- models/
|
+-- models/
|   +-- local-llm-files/
|
+-- translations/
|   +-- argos-packages/
|
+-- database/
|   +-- chatbot.sqlite
|   +-- schema.sql
|
+-- readme.md
```

The Raspberry Pi application should use the shared `core/` package for common chatbot behavior. Raspberry-specific files should only handle local AI, offline translation, local database storage, hardware constraints, and deployment on Raspberry Pi OS.

## Core Dependency

The Raspberry Pi application should connect to the core modules:

```text
core/
|
+-- chatbot.py
+-- language_detector.py
+-- prompt_builder.py
+-- response_formatter.py
+-- conversation_manager.py
+-- config.py
+-- utils.py
```

The `core/` package should not directly depend on `llama.cpp`, Argos Translate, Raspberry Pi OS, local model files, or SQLite implementation details. Those details belong in `raspberry/`.

## Features

- Runs without internet.
- Local AI model.
- Offline English, Tamil, and Hindi translation.
- Local SQLite database.
- Optimized for Raspberry Pi performance.
- No external API dependencies.
- Local-first privacy.
- Touchscreen or monitor-based usage.

## Technologies

- FastAPI
- React served locally
- `llama.cpp`
- Argos Translate
- SQLite
- Raspberry Pi OS

## Implementation Steps

1. Prepare the Raspberry Pi
   - Install Raspberry Pi OS.
   - Install Python 3.
   - Install required build tools.
   - Set up the project directory on the Raspberry Pi.

2. Create the backend
   - Set up a FastAPI application in `raspberry/backend/`.
   - Reuse the shared `core/` package.
   - Add local chat endpoints.
   - Keep the backend independent from internet services.

3. Add local AI support
   - Install and configure `llama.cpp`.
   - Download or prepare a small model that can run on Raspberry Pi hardware.
   - Prefer quantized models for better performance.
   - Create a local AI service wrapper in `raspberry/backend/`.
   - Send prompts from `core/prompt_builder.py` to the local model.

4. Add offline translation
   - Install Argos Translate.
   - Add English, Tamil, and Hindi translation packages.
   - Create an offline translation service in `raspberry/backend/`.
   - Store translation assets in `raspberry/translations/`.

5. Add local database support
   - Use SQLite for chat history.
   - Store sessions, messages, timestamps, and selected language locally.
   - Keep the database inside `raspberry/database/`.

6. Serve the local UI
   - Build the React frontend as static files.
   - Serve the UI locally through FastAPI or a lightweight local server.
   - Support touchscreen or monitor-based usage.

7. Optimize for Raspberry Pi
   - Use small or quantized local models.
   - Limit maximum response length.
   - Stream responses if possible.
   - Reduce background tasks.
   - Keep the UI lightweight.
   - Monitor CPU, memory, and temperature during testing.

8. Test offline behavior
   - Disconnect internet and confirm the application still works.
   - Test English, Tamil, and Hindi conversations.
   - Test local model response time.
   - Test startup after reboot.
   - Test database persistence.
   - Test touchscreen or monitor usage.

## User Flow

```text
User
   |
   v
Local React UI
   |
   v
FastAPI
   |
   +-- Argos Translate
   +-- llama.cpp
         |
         v
     Response
```

## Development Roadmap

1. Build the shared `core/` package.
2. Create the local FastAPI backend.
3. Reuse or adapt the React frontend.
4. Add `llama.cpp` integration.
5. Add Argos Translate integration.
6. Add local SQLite storage.
7. Optimize for Raspberry Pi performance.
8. Test with internet disconnected.

## Implementation Principles

- Keep reusable chatbot logic in `core/`.
- Keep offline AI and translation code inside `raspberry/`.
- Avoid external API dependencies.
- Use service wrappers for local AI and translation.
- Make the Raspberry Pi edition fully local and privacy-friendly.
- Prioritize reliability and performance over large model size.
