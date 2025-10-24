using UnityEngine;

/// <summary>
/// Configuration settings for Google Sign-In in Unity.
/// Contains OAuth credentials and backend API endpoints.
/// </summary>
[CreateAssetMenu(fileName = "GoogleSignInConfig", menuName = "TranslatAR/Google Sign-In Config")]
public class GoogleSignInConfig : ScriptableObject
{
    [Header("Google OAuth Settings")]
    [Tooltip("Google OAuth Client ID from Google Cloud Console")]
    public string clientId = "861587845879-v6ih92nnkk9h1isaiv7gafaqaguockq8.apps.googleusercontent.com";
    
    [Tooltip("OAuth redirect URI (must match Google Cloud Console settings)")]
    public string redirectUri = "http://localhost:8000/auth/google/callback";
    
    [Header("Backend API Settings")]
    [Tooltip("Base URL of the TranslatAR backend API")]
    public string backendUrl = "http://localhost:8000";
    
    [Tooltip("API endpoint for Google OAuth")]
    public string authEndpoint = "/auth/google";
    
    [Tooltip("API endpoint for OAuth callback")]
    public string callbackEndpoint = "/auth/google/callback";
    
    [Tooltip("API endpoint for token verification")]
    public string verifyEndpoint = "/auth/verify";
    
    [Tooltip("API endpoint for user information")]
    public string userEndpoint = "/auth/me";
    
    [Header("Authentication Settings")]
    [Tooltip("Token expiration time in seconds (24 hours)")]
    public int tokenExpirationSeconds = 86400;
    
    [Tooltip("Whether to save authentication token locally")]
    public bool saveTokenLocally = true;
    
    [Tooltip("Key for storing token in PlayerPrefs")]
    public string tokenPrefsKey = "GoogleAuthToken";
    
    [Header("UI Settings")]
    [Tooltip("Google brand colors")]
    public Color googleBlue = new Color(0.26f, 0.52f, 0.96f);
    public Color googleRed = new Color(0.86f, 0.26f, 0.21f);
    public Color googleGreen = new Color(0.2f, 0.66f, 0.33f);
    public Color googleYellow = new Color(0.98f, 0.74f, 0.02f);
    
    [Tooltip("Status message display duration")]
    public float statusMessageDuration = 3f;
    
    [Header("Debug Settings")]
    [Tooltip("Enable debug logging")]
    public bool enableDebugLogging = true;
    
    [Tooltip("Log authentication requests and responses")]
    public bool logAuthRequests = false;
    
    /// <summary>
    /// Gets the full OAuth URL for Google sign-in
    /// </summary>
    public string GetOAuthUrl()
    {
        return $"{backendUrl}{authEndpoint}";
    }
    
    /// <summary>
    /// Gets the full callback URL for OAuth
    /// </summary>
    public string GetCallbackUrl()
    {
        return $"{backendUrl}{callbackEndpoint}";
    }
    
    /// <summary>
    /// Gets the full verification URL
    /// </summary>
    public string GetVerifyUrl()
    {
        return $"{backendUrl}{verifyEndpoint}";
    }
    
    /// <summary>
    /// Gets the full user info URL
    /// </summary>
    public string GetUserInfoUrl()
    {
        return $"{backendUrl}{userEndpoint}";
    }
    
    /// <summary>
    /// Validates the configuration
    /// </summary>
    public bool IsValid()
    {
        if (string.IsNullOrEmpty(clientId))
        {
            Debug.LogError("Google Sign-In Config: Client ID is required");
            return false;
        }
        
        if (string.IsNullOrEmpty(backendUrl))
        {
            Debug.LogError("Google Sign-In Config: Backend URL is required");
            return false;
        }
        
        if (string.IsNullOrEmpty(redirectUri))
        {
            Debug.LogError("Google Sign-In Config: Redirect URI is required");
            return false;
        }
        
        return true;
    }
    
    /// <summary>
    /// Logs debug information if enabled
    /// </summary>
    public void LogDebug(string message)
    {
        if (enableDebugLogging)
        {
            Debug.Log($"[GoogleSignIn] {message}");
        }
    }
    
    /// <summary>
    /// Logs authentication requests if enabled
    /// </summary>
    public void LogAuthRequest(string endpoint, string method = "GET")
    {
        if (logAuthRequests)
        {
            Debug.Log($"[GoogleSignIn] {method} {endpoint}");
        }
    }
}


