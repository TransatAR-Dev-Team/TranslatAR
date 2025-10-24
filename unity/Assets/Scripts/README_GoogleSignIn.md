# Unity Google Sign-In Implementation

This implementation provides Google OAuth authentication for Unity applications, specifically designed for the TranslatAR project.

## Features

- ✅ **Google OAuth Integration** - Full OAuth 2.0 flow with Google
- ✅ **Cross-Platform Support** - Works on Windows, Mac, WebGL, and mobile
- ✅ **Token Management** - Secure JWT token handling and storage
- ✅ **User Profile Display** - Shows user name, email, and profile picture
- ✅ **WebGL Support** - Special handling for Unity WebGL builds
- ✅ **Persistent Sessions** - Remembers login across app restarts
- ✅ **Event System** - C# events for authentication state changes

## Setup Instructions

### 1. Google Cloud Console Configuration

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API
4. Create OAuth 2.0 credentials:
   - **Application Type**: Web application
   - **Authorized JavaScript origins**: `http://localhost` (for development)
   - **Authorized redirect URIs**: `http://localhost:8000/auth/google/callback`

### 2. Unity Project Setup

1. **Add Scripts to Unity**:
   - Copy all `.cs` files to `Assets/Scripts/` folder
   - Unity will automatically compile the scripts

2. **Create Configuration Asset**:
   - Right-click in Project window
   - Create → TranslatAR → Google Sign-In Config
   - Configure with your Google OAuth credentials

3. **Setup Scene**:
   - Create UI Canvas with Google Sign-In elements
   - Add `GoogleSignInManager` component to a GameObject
   - Add `GoogleSignInUI` component to handle UI interactions
   - For WebGL builds, add `GoogleSignInWebGL` component

### 3. UI Setup

Create the following UI elements:

#### Login Panel
- **Google Sign-In Button** - Triggers authentication
- **Title Text** - "Sign in to TranslatAR"
- **Subtitle Text** - Description text

#### User Panel
- **User Profile Image** - Shows Google profile picture
- **User Name Text** - Displays user's name
- **User Email Text** - Shows user's email
- **Sign Out Button** - Logs out user
- **Settings Button** - Additional options

#### Status Elements
- **Status Text** - Shows authentication status
- **Loading Indicator** - Spinner during authentication

### 4. Backend Integration

The Unity client communicates with your TranslatAR backend:

- **OAuth URL**: `http://localhost:8000/auth/google`
- **Callback URL**: `http://localhost:8000/auth/google/callback`
- **Token Verification**: `http://localhost:8000/auth/verify`
- **User Info**: `http://localhost:8000/auth/me`

## Usage

### Basic Authentication

```csharp
// Get the sign-in manager
GoogleSignInManager signInManager = GoogleSignInManager.Instance;

// Check if user is authenticated
if (signInManager.IsAuthenticated())
{
    string token = signInManager.GetAuthToken();
    UserProfile user = signInManager.GetCurrentUser();
    Debug.Log($"Welcome, {user.name}!");
}
else
{
    // Start sign-in process
    signInManager.StartGoogleSignIn();
}
```

### Event Handling

```csharp
// Subscribe to authentication events
GoogleSignInManager.OnUserSignedIn += OnUserSignedIn;
GoogleSignInManager.OnUserSignedOut += OnUserSignedOut;

void OnUserSignedIn(UserProfile user)
{
    Debug.Log($"User signed in: {user.name} ({user.email})");
    // Update UI, load user data, etc.
}

void OnUserSignedOut()
{
    Debug.Log("User signed out");
    // Clear UI, reset state, etc.
}
```

### WebGL Specific

For WebGL builds, use the WebGL helper:

```csharp
GoogleSignInWebGL webGLHelper = GetComponent<GoogleSignInWebGL>();
webGLHelper.OpenGoogleSignIn();
```

## Configuration

### GoogleSignInConfig ScriptableObject

Create a configuration asset with these settings:

- **Client ID**: Your Google OAuth client ID
- **Redirect URI**: Must match Google Cloud Console settings
- **Backend URL**: Your TranslatAR backend URL
- **Token Settings**: Expiration time and storage preferences
- **UI Colors**: Google brand colors for buttons
- **Debug Settings**: Enable logging and request logging

### Environment Variables

Make sure your backend has the correct environment variables:

```env
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
JWT_SECRET=your_jwt_secret_here
```

## Platform-Specific Notes

### Windows/Mac Standalone
- Uses `Application.OpenURL()` to open system browser
- Handles OAuth callback through polling mechanism

### WebGL
- Uses JavaScript interop to open OAuth in popup or same window
- Handles URL parameters for OAuth callback
- Requires special WebGL helper component

### Mobile (Android/iOS)
- Can use native Google Sign-In SDK (requires additional setup)
- Current implementation uses web-based OAuth flow

## Troubleshooting

### Common Issues

1. **"Client ID not found"**
   - Ensure GoogleSignInConfig is properly configured
   - Check that Client ID matches Google Cloud Console

2. **"Backend connection failed"**
   - Verify backend is running on correct port
   - Check network connectivity
   - Ensure CORS is properly configured

3. **"Token verification failed"**
   - Check JWT secret configuration
   - Verify token hasn't expired
   - Ensure backend token verification endpoint works

4. **WebGL popup blocked**
   - Browser may block popups
   - Implementation falls back to same-window redirect
   - Consider user education about popup permissions

### Debug Logging

Enable debug logging in GoogleSignInConfig:
- Set `Enable Debug Logging` to true
- Set `Log Auth Requests` to true for detailed request logging

## Security Considerations

- **Token Storage**: Tokens are stored in PlayerPrefs (not secure for production)
- **HTTPS**: Use HTTPS in production for secure communication
- **Token Expiration**: Tokens expire after 24 hours by default
- **Backend Validation**: All tokens are verified with backend before use

## Integration with TranslatAR

This Google Sign-In implementation integrates with your existing TranslatAR backend:

1. **Authentication**: Users sign in with Google accounts
2. **Token Exchange**: Unity receives JWT tokens from backend
3. **API Calls**: All backend API calls include authentication headers
4. **User Data**: User profiles are stored and managed by backend
5. **Session Management**: Tokens persist across Unity sessions

The implementation provides a seamless authentication experience for your TranslatAR Unity application!


