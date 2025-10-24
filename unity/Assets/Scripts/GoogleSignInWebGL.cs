using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class GoogleSignInWebGL : MonoBehaviour
{
    [Header("WebGL Configuration")]
    public string clientId = "YOUR_GOOGLE_CLIENT_ID";
    public string redirectUri = "http://localhost:8000/auth/google/callback";
    
    private GoogleSignInManager authManager;
    
    void Start()
    {
        authManager = GoogleSignInManager.Instance;
        if (authManager == null)
        {
            Debug.LogError("GoogleSignInManager not found!");
            return;
        }
        
        #if UNITY_WEBGL && !UNITY_EDITOR
            InitializeWebGL();
        #endif
    }
    
    #if UNITY_WEBGL && !UNITY_EDITOR
    private void InitializeWebGL()
    {
        Debug.Log("Initializing WebGL Google Sign-In");
        
        // Initialize Google Sign-In for WebGL
        InitializeGoogleSignIn();
    }
    
    private void InitializeGoogleSignIn()
    {
        try
        {
            // Initialize Google Sign-In JavaScript
            string initScript = $@"
                window.google.accounts.id.initialize({{
                    client_id: '{clientId}',
                    callback: handleCredentialResponse,
                    auto_select: false,
                    cancel_on_tap_outside: false,
                    context: 'signup',
                    itp_support: true,
                    use_fedcm_for_prompt: true,
                    ux_mode: 'popup',
                    login_uri: window.location.origin
                }});
            ";
            
            Application.ExternalEval(initScript);
            
            Debug.Log("Google Sign-In initialized for WebGL");
        }
        catch (Exception e)
        {
            Debug.LogError($"Failed to initialize Google Sign-In: {e.Message}");
        }
    }
    
    public void StartWebGLSignIn()
    {
        try
        {
            string promptScript = @"
                window.google.accounts.id.prompt((notification) => {
                    console.log('One-tap notification:', notification);
                    if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
                        console.log('One-tap not displayed');
                    }
                });
            ";
            
            Application.ExternalEval(promptScript);
            
            Debug.Log("WebGL Google Sign-In prompt initiated");
        }
        catch (Exception e)
        {
            Debug.LogError($"Failed to start WebGL sign-in: {e.Message}");
        }
    }
    
    public void HandleWebGLCallback(string url)
    {
        Debug.Log($"WebGL callback received: {url}");
        
        try
        {
            // Parse URL parameters
            var parameters = ParseUrlParameters(url);
            
            if (parameters.ContainsKey("code"))
            {
                string authCode = parameters["code"];
                Debug.Log($"Auth code received: {authCode}");
                
                if (authManager != null)
                {
                    authManager.HandleAuthCode(authCode);
                }
            }
            else if (parameters.ContainsKey("error"))
            {
                string error = parameters["error"];
                Debug.LogError($"OAuth error: {error}");
            }
        }
        catch (Exception e)
        {
            Debug.LogError($"Failed to handle WebGL callback: {e.Message}");
        }
    }
    
    private Dictionary<string, string> ParseUrlParameters(string url)
    {
        var parameters = new Dictionary<string, string>();
        
        try
        {
            var uri = new Uri(url);
            var query = uri.Query;
            
            if (query.StartsWith("?"))
            {
                query = query.Substring(1);
            }
            
            var pairs = query.Split('&');
            foreach (var pair in pairs)
            {
                if (string.IsNullOrEmpty(pair)) continue;
                
                var keyValue = pair.Split('=');
                if (keyValue.Length == 2)
                {
                    string key = Uri.UnescapeDataString(keyValue[0]);
                    string value = Uri.UnescapeDataString(keyValue[1]);
                    parameters[key] = value;
                }
            }
        }
        catch (Exception e)
        {
            Debug.LogError($"Failed to parse URL parameters: {e.Message}");
        }
        
        return parameters;
    }
    
    private Dictionary<string, string> ParseJsonToDictionary(string json)
    {
        var dictionary = new Dictionary<string, string>();
        
        try
        {
            // Simple JSON parsing for key-value pairs
            json = json.Trim();
            if (json.StartsWith("{") && json.EndsWith("}"))
            {
                json = json.Substring(1, json.Length - 2);
                
                var pairs = json.Split(',');
                foreach (var pair in pairs)
                {
                    if (string.IsNullOrEmpty(pair)) continue;
                    
                    var keyValue = pair.Split(':');
                    if (keyValue.Length == 2)
                    {
                        string key = keyValue[0].Trim().Trim('"');
                        string value = keyValue[1].Trim().Trim('"');
                        dictionary[key] = value;
                    }
                }
            }
        }
        catch (Exception e)
        {
            Debug.LogError($"Failed to parse JSON: {e.Message}");
        }
        
        return dictionary;
    }
    #endif
    
    public void OnWebGLAuthSuccess(string token)
    {
        Debug.Log($"WebGL auth success: {token}");
        
        if (authManager != null)
        {
            authManager.SetAuthToken(token);
        }
    }
    
    public void OnWebGLAuthError(string error)
    {
        Debug.LogError($"WebGL auth error: {error}");
    }
}
