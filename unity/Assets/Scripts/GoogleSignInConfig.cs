using UnityEngine;

[CreateAssetMenu(fileName = "GoogleSignInConfig", menuName = "Google Sign-In/Config")]
public class GoogleSignInConfig : ScriptableObject
{
    [Header("Google OAuth Configuration")]
    public string clientId = "YOUR_GOOGLE_CLIENT_ID";
    public string clientSecret = "YOUR_GOOGLE_CLIENT_SECRET";
    public string redirectUri = "http://localhost:8000/auth/google/callback";

    [Header("Backend Configuration")]
    public string backendUrl = "http://localhost:8000";
    public string authEndpoint = "/auth/google";
    public string callbackEndpoint = "/auth/google/callback";
    public string verifyEndpoint = "/auth/verify";

    [Header("OAuth Scopes")]
    public string[] scopes = { "openid", "email", "profile" };

    [Header("Debug Settings")]
    public bool enableDebugLogs = true;
    public bool useTestEnvironment = false;
}
