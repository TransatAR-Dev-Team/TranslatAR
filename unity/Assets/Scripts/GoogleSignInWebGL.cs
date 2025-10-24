using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System.Text;

/// <summary>
/// Handles Google Sign-In for Unity WebGL builds.
/// Uses Unity's WebGL JavaScript interop to open OAuth in the same window.
/// </summary>
public class GoogleSignInWebGL : MonoBehaviour
{
    [Header("WebGL Configuration")]
    [SerializeField] private GoogleSignInConfig config;
    [SerializeField] private GoogleSignInManager signInManager;
    
    [Header("WebGL Settings")]
    [SerializeField] private bool usePopupWindow = true;
    [SerializeField] private int popupWidth = 500;
    [SerializeField] private int popupHeight = 600;
    
    private const string JSLIB_OPEN_URL = "openURL";
    private const string JSLIB_GET_URL_PARAMS = "getURLParameters";
    
    void Start()
    {
        if (signInManager == null)
            signInManager = GoogleSignInManager.Instance;
            
        if (config == null)
            config = Resources.Load<GoogleSignInConfig>("GoogleSignInConfig");
    }
    
    /// <summary>
    /// Opens Google OAuth URL in WebGL environment
    /// </summary>
    public void OpenGoogleSignIn()
    {
        if (config == null)
        {
            Debug.LogError("Google Sign-In Config not found!");
            return;
        }
        
        string authUrl = config.GetOAuthUrl();
        config.LogDebug($"Opening OAuth URL: {authUrl}");
        
        if (usePopupWindow)
        {
            OpenURLInPopup(authUrl);
        }
        else
        {
            OpenURLInSameWindow(authUrl);
        }
    }
    
    /// <summary>
    /// Opens URL in a popup window (WebGL)
    /// </summary>
    void OpenURLInPopup(string url)
    {
        #if UNITY_WEBGL && !UNITY_EDITOR
        string jsCode = $@"
            var popup = window.open('{url}', 'google-signin', 
                'width={popupWidth},height={popupHeight},scrollbars=yes,resizable=yes');
            
            if (popup) {{
                var checkClosed = setInterval(function() {{
                    if (popup.closed) {{
                        clearInterval(checkClosed);
                        SendMessage('{gameObject.name}', 'OnPopupClosed', '');
                    }}
                }}, 1000);
            }} else {{
                SendMessage('{gameObject.name}', 'OnPopupBlocked', '');
            }}
        ";
        
        Application.ExternalEval(jsCode);
        #else
        // Fallback for editor or non-WebGL builds
        Application.OpenURL(url);
        #endif
    }
    
    /// <summary>
    /// Opens URL in the same window (WebGL)
    /// </summary>
    void OpenURLInSameWindow(string url)
    {
        #if UNITY_WEBGL && !UNITY_EDITOR
        Application.ExternalEval($"window.location.href = '{url}';");
        #else
        Application.OpenURL(url);
        #endif
    }
    
    /// <summary>
    /// Called when popup window is closed
    /// </summary>
    public void OnPopupClosed(string message)
    {
        config?.LogDebug("OAuth popup closed");
        // Check if authentication was successful
        StartCoroutine(CheckForAuthResult());
    }
    
    /// <summary>
    /// Called when popup is blocked by browser
    /// </summary>
    public void OnPopupBlocked(string message)
    {
        config?.LogDebug("OAuth popup blocked by browser");
        // Fallback: redirect in same window
        if (config != null)
        {
            OpenURLInSameWindow(config.GetOAuthUrl());
        }
    }
    
    /// <summary>
    /// Checks for authentication result in URL parameters
    /// </summary>
    IEnumerator CheckForAuthResult()
    {
        yield return new WaitForSeconds(1f); // Wait for URL to update
        
        #if UNITY_WEBGL && !UNITY_EDITOR
        string jsCode = @"
            var urlParams = new URLSearchParams(window.location.search);
            var code = urlParams.get('code');
            var error = urlParams.get('error');
            
            if (code) {
                SendMessage('" + gameObject.name + @"', 'OnAuthCodeReceived', code);
            } else if (error) {
                SendMessage('" + gameObject.name + @"', 'OnAuthError', error);
            } else {
                SendMessage('" + gameObject.name + @"', 'OnNoAuthResult', '');
            }
        ";
        
        Application.ExternalEval(jsCode);
        #endif
    }
    
    /// <summary>
    /// Called when authorization code is received
    /// </summary>
    public void OnAuthCodeReceived(string code)
    {
        config?.LogDebug($"Received auth code: {code}");
        
        if (signInManager != null)
        {
            signInManager.HandleAuthCallback(code);
        }
    }
    
    /// <summary>
    /// Called when authentication error occurs
    /// </summary>
    public void OnAuthError(string error)
    {
        config?.LogDebug($"Authentication error: {error}");
        Debug.LogError($"Google Sign-In Error: {error}");
    }
    
    /// <summary>
    /// Called when no authentication result is found
    /// </summary>
    public void OnNoAuthResult(string message)
    {
        config?.LogDebug("No authentication result found");
    }
    
    /// <summary>
    /// Gets URL parameters from current page (WebGL only)
    /// </summary>
    public Dictionary<string, string> GetURLParameters()
    {
        var parameters = new Dictionary<string, string>();
        
        #if UNITY_WEBGL && !UNITY_EDITOR
        string jsCode = @"
            var urlParams = new URLSearchParams(window.location.search);
            var params = {};
            for (var pair of urlParams.entries()) {
                params[pair[0]] = pair[1];
            }
            SendMessage('" + gameObject.name + @"', 'OnURLParametersReceived', JSON.stringify(params));
        ";
        
        Application.ExternalEval(jsCode);
        #endif
        
        return parameters;
    }
    
    /// <summary>
    /// Called when URL parameters are received from JavaScript
    /// </summary>
    public void OnURLParametersReceived(string jsonParams)
    {
        try
        {
            // Parse JSON manually since JsonUtility doesn't support Dictionary
            var parameters = ParseJsonToDictionary(jsonParams);
            
            if (parameters.ContainsKey("code"))
            {
                OnAuthCodeReceived(parameters["code"]);
            }
            else if (parameters.ContainsKey("error"))
            {
                OnAuthError(parameters["error"]);
            }
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Error parsing URL parameters: {e.Message}");
        }
    }
    
    /// <summary>
    /// Parses JSON string to Dictionary (simple implementation)
    /// </summary>
    Dictionary<string, string> ParseJsonToDictionary(string json)
    {
        var result = new Dictionary<string, string>();
        
        // Simple JSON parsing for URL parameters
        json = json.Trim('{', '}');
        var pairs = json.Split(',');
        
        foreach (var pair in pairs)
        {
            var keyValue = pair.Split(':');
            if (keyValue.Length == 2)
            {
                var key = keyValue[0].Trim().Trim('"');
                var value = keyValue[1].Trim().Trim('"');
                result[key] = value;
            }
        }
        
        return result;
    }
    
    /// <summary>
    /// Clears URL parameters after processing
    /// </summary>
    public void ClearURLParameters()
    {
        #if UNITY_WEBGL && !UNITY_EDITOR
        Application.ExternalEval("window.history.replaceState({}, document.title, window.location.pathname);");
        #endif
    }
}
