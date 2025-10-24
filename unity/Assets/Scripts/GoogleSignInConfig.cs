using UnityEngine;

[CreateAssetMenu(fileName = "GoogleSignInConfig", menuName = "Google Sign-In/Config")]
public class GoogleSignInConfig : ScriptableObject
{
    [Header("OAuth Configuration")]
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
    
    [Header("Settings")]
    public bool autoSelect = false;
    public bool cancelOnTapOutside = false;
    public string context = "signup";
    public bool itpSupport = true;
    public bool useFedcmForPrompt = true;
    public string uxMode = "popup";
    
    public string GetAuthUrl()
    {
        string scopeString = string.Join(" ", scopes);
        return $"{backendUrl}{authEndpoint}?client_id={clientId}&redirect_uri={redirectUri}&scope={scopeString}&response_type=code&access_type=offline";
    }
    
    public string GetCallbackUrl()
    {
        return $"{backendUrl}{callbackEndpoint}";
    }
    
    public string GetVerifyUrl(string token)
    {
        return $"{backendUrl}{verifyEndpoint}?token={token}";
    }
    
    public bool IsValid()
    {
        return !string.IsNullOrEmpty(clientId) && 
               !string.IsNullOrEmpty(redirectUri) && 
               !string.IsNullOrEmpty(backendUrl);
    }
    
    public void Validate()
    {
        if (string.IsNullOrEmpty(clientId))
        {
            Debug.LogWarning("GoogleSignInConfig: Client ID is not set!");
        }
        
        if (string.IsNullOrEmpty(redirectUri))
        {
            Debug.LogWarning("GoogleSignInConfig: Redirect URI is not set!");
        }
        
        if (string.IsNullOrEmpty(backendUrl))
        {
            Debug.LogWarning("GoogleSignInConfig: Backend URL is not set!");
        }
        
        if (scopes == null || scopes.Length == 0)
        {
            Debug.LogWarning("GoogleSignInConfig: No OAuth scopes defined!");
        }
    }
}
