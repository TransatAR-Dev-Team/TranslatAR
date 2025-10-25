# Google OAuth Setup Guide

This project requires Google OAuth credentials to work properly. Follow these steps to set up Google OAuth:

## 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note the project ID

## 2. Enable Google+ API

1. In the Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google+ API" and enable it
3. Also enable "Google OAuth2 API"

## 3. Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Web application" as the application type
4. Set the following:
   - **Name**: TranslatAR OAuth Client
   - **Authorized JavaScript origins**: 
     - `http://localhost:5173`
     - `http://localhost:8000`
   - **Authorized redirect URIs**:
     - `http://localhost:8000/auth/google/callback`

## 4. Configure Environment Variables

1. Copy the `oauth-config.env` file:
   ```bash
   cp oauth-config.env .env
   ```

2. Edit the `.env` file and replace the placeholder values:
   ```
   GOOGLE_CLIENT_ID=your_actual_client_id_from_google_console
   GOOGLE_CLIENT_SECRET=your_actual_client_secret_from_google_console
   GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
   JWT_SECRET=your_strong_random_jwt_secret_here
   ```

## 5. Restart Services

After configuring the environment variables, restart the services:

```bash
make down
make up
```

## 6. Test the Setup

1. Open your browser and go to `http://localhost:5173`
2. Click the Google Sign-In button
3. You should be redirected to Google's OAuth consent screen
4. After authorization, you should be redirected back to the application

## Troubleshooting

- **"Google OAuth not configured"**: Make sure all environment variables are set correctly
- **"Invalid redirect URI"**: Check that the redirect URI in Google Console matches exactly
- **"Invalid client"**: Verify that the client ID and secret are correct
- **CORS errors**: Ensure the authorized JavaScript origins include `http://localhost:5173`

## Security Notes

- Never commit the `.env` file to version control
- Use a strong, random JWT secret
- In production, use HTTPS and update the redirect URIs accordingly
- Consider using environment-specific OAuth applications for development vs production
