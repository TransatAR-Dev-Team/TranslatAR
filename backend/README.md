# Backend - TranslatAR

This directory contains the backend API gateway for the TranslatAR project. It's a Python application built with FastAPI that orchestrates communication between the frontend, the speech-to-text service, the translation service, and the database. It is containerized with Docker.

## Tech Stack

- [Python](https://www.python.org/): **Version 3.11.**
- [FastAPI](https://fastapi.tiangolo.com/): A modern, high-performance Python web framework for building APIs.
- [MongoDB](https://www.mongodb.com/): A NoSQL database used here to store translation history and user data, accessed via the `motor` async driver.
- [Docker](https://www.docker.com/): A containerization tool, allowing the service to run in an isolated and consistent environment.
- [PyJWT](https://pyjwt.readthedocs.io/): JSON Web Token implementation for user authentication.

## Features

- **Google OAuth 2.0 Authentication**: Secure user login via Google accounts
- **JWT Token Management**: Session management using JSON Web Tokens
- **User Profile Management**: Store and retrieve user preferences and settings
- **Translation History**: Track and store all translation requests
- **WebSocket Support**: Real-time communication for live translation
- **API Gateway**: Orchestrates calls to STT, Translation, and Summarization services

## Environment Variables

The backend requires the following environment variables. Create a `.env` file in the project root:

```env
# Database Configuration
DATABASE_URL=mongodb://mongodb:27017

# Service URLs
STT_URL=http://stt:9000
TRANSLATION_URL=http://translation:9001
SUMMARIZATION_URL=http://summarization:9002

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback

# JWT Configuration
JWT_SECRET=your_jwt_secret_key_here
```

### Setting Up Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API
4. Go to "Credentials" and create OAuth 2.0 Client ID
5. Add authorized redirect URIs:
   - `http://localhost:8000/auth/google/callback` (for local development)
   - Add your production URL when deploying
6. Copy the Client ID and Client Secret to your `.env` file

## API Endpoints

### Authentication Endpoints

- `GET /auth/google` - Get Google OAuth login URL
- `GET /auth/google/callback` - Handle OAuth callback and return JWT
- `GET /auth/verify?token=<jwt>` - Verify JWT token validity
- `GET /auth/me` - Get current user information (requires Authorization header)

### Translation Endpoints

- `POST /api/process-audio` - Process audio file and return translation
- `GET /api/history` - Get translation history
- `POST /api/summarize` - Summarize text
- `GET /api/settings` - Get user settings
- `POST /api/settings` - Update user settings
- `GET /api/health` - Health check endpoint

### Static Files

- `GET /static/login.html` - Google login page

## Getting Started

See the `README.md` in the root of the project for instructions on building and running the entire project.

For details on managing Python dependencies and setting up a local testing environment, please see the [Python Services - Development Guide](../docs/developer_guide.python_services.md).
