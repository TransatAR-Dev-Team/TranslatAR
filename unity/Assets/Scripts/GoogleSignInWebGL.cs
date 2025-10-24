using System;
using System.Collections.Generic;
using UnityEngine;

public class GoogleSignInWebGL : MonoBehaviour
{
    public static event Action<string> OnAuthCodeReceived;
    public static event Action<string> OnAuthError;

    public static void OpenGoogleAuthPopup()
    {
        string clientId = "YOUR_GOOGLE_CLIENT_ID";
        string redirectUri = "http://localhost:8000/auth/google/callback";
        
        string authUrl = $"https://accounts.google.com/o/oauth2/v2/auth?" +
            $"client_id={clientId}&" +
            $"redirect_uri={redirectUri}&" +
            $"response_type=code&" +
            $"scope=openid email profile&" +
            $"access_type=offline&" +
            $"prompt=consent";

        #if UNITY_WEBGL && !UNITY_EDITOR
            OpenPopup(authUrl);
        #else
            Application.OpenURL(authUrl);
        #endif
    }

    #if UNITY_WEBGL && !UNITY_EDITOR
    [System.Runtime.InteropServices.DllImport("__Internal")]
    private static extern void OpenPopup(string url);

    [System.Runtime.InteropServices.DllImport("__Internal")]
    private static extern void ClosePopup();

    public static void OnURLParametersReceived(string parameters)
    {
        Debug.Log($"Received URL parameters: {parameters}");
        
        try
        {
            var paramDict = ParseJsonToDictionary(parameters);
            
            if (paramDict.ContainsKey("code"))
            {
                string authCode = paramDict["code"];
                Debug.Log($"Auth code received: {authCode}");
                OnAuthCodeReceived?.Invoke(authCode);
            }
            else if (paramDict.ContainsKey("error"))
            {
                string error = paramDict["error"];
                Debug.LogError($"OAuth error: {error}");
                OnAuthError?.Invoke(error);
            }
        }
        catch (Exception e)
        {
            Debug.LogError($"Error parsing URL parameters: {e.Message}");
            OnAuthError?.Invoke(e.Message);
        }
    }

    private static Dictionary<string, string> ParseJsonToDictionary(string json)
    {
        var result = new Dictionary<string, string>();
        
        // Remove curly braces
        json = json.Trim().TrimStart('{').TrimEnd('}');
        
        // Split by commas
        string[] pairs = json.Split(',');
        
        foreach (string pair in pairs)
        {
            string[] keyValue = pair.Split(':');
            if (keyValue.Length == 2)
            {
                string key = keyValue[0].Trim().Trim('"');
                string value = keyValue[1].Trim().Trim('"');
                result[key] = value;
            }
        }
        
        return result;
    }
    #endif
}
