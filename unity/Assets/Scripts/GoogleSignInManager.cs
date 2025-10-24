using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;
using System.Text;

public class GoogleSignInManager : MonoBehaviour
{
    public static GoogleSignInManager Instance { get; private set; }
    
    [Header("OAuth Configuration")]
    public string clientId = "YOUR_GOOGLE_CLIENT_ID";
    public string redirectUri = "http://localhost:8000/auth/google/callback";
    public string backendUrl = "http://localhost:8000";
    
    [Header("User Data")]
    public string userName = "";
    public string userEmail = "";
    public string userPicture = "";
    public string authToken = "";
    
    private bool isAuthenticated = false;
    
    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    public void StartGoogleSignIn()
    {
        Debug.Log("Starting Google Sign-In process...");
        
        #if UNITY_WEBGL && !UNITY_EDITOR
            StartWebGLSignIn();
        #else
            StartEditorSignIn();
        #endif
    }
    
    private void StartWebGLSignIn()
    {
        Debug.Log("WebGL Google Sign-In");
        // WebGL implementation would go here
        // For now, we'll use the same approach as editor
        StartEditorSignIn();
    }
    
    private void StartEditorSignIn()
    {
        Debug.Log("Editor Google Sign-In");
        string authUrl = $"{backendUrl}/auth/google";
        
        // Open browser for OAuth
        Application.OpenURL(authUrl);
        
        // Start polling for callback
        StartCoroutine(PollForCallback());
    }
    
    private IEnumerator PollForCallback()
    {
        Debug.Log("Polling for OAuth callback...");
        
        while (!isAuthenticated)
        {
            yield return new WaitForSeconds(1f);
            
            // Check if we have a token in the URL (WebGL) or need to poll backend
            #if UNITY_WEBGL && !UNITY_EDITOR
                CheckWebGLToken();
            #else
                // For editor, we'd need to implement a way to get the token
                // This is a simplified version
                Debug.Log("Waiting for authentication...");
            #endif
        }
    }
    
    private void CheckWebGLToken()
    {
        // WebGL specific token checking
        Debug.Log("Checking WebGL token...");
    }
    
    public void HandleAuthCode(string authCode)
    {
        Debug.Log($"Handling auth code: {authCode}");
        StartCoroutine(ExchangeCodeForToken(authCode));
    }
    
    private IEnumerator ExchangeCodeForToken(string authCode)
    {
        string url = $"{backendUrl}/auth/google/callback?code={authCode}";
        
        using (UnityWebRequest request = UnityWebRequest.Get(url))
        {
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                try
                {
                    var response = JsonUtility.FromJson<AuthResponse>(request.downloadHandler.text);
                    SetAuthToken(response.jwt);
                    SetUserInfo(response.user);
                    Debug.Log("Authentication successful!");
                }
                catch (Exception e)
                {
                    Debug.LogError($"Failed to parse auth response: {e.Message}");
                }
            }
            else
            {
                Debug.LogError($"Auth request failed: {request.error}");
            }
        }
    }
    
    public void SetAuthToken(string token)
    {
        authToken = token;
        isAuthenticated = true;
        Debug.Log("Auth token set successfully");
    }
    
    public void SetUserInfo(UserInfo user)
    {
        userName = user.name;
        userEmail = user.email;
        userPicture = user.picture;
        Debug.Log($"User info set: {userName} ({userEmail})");
    }
    
    public bool IsAuthenticated()
    {
        return isAuthenticated && !string.IsNullOrEmpty(authToken);
    }
    
    public string GetCurrentUser()
    {
        return userName;
    }
    
    public string GetAuthToken()
    {
        return authToken;
    }
    
    public void Logout()
    {
        userName = "";
        userEmail = "";
        userPicture = "";
        authToken = "";
        isAuthenticated = false;
        Debug.Log("User logged out");
    }
    
    public void LoadUserProfilePicture()
    {
        if (!string.IsNullOrEmpty(userPicture))
        {
            StartCoroutine(LoadProfileImage(userPicture));
        }
    }
    
    private IEnumerator LoadProfileImage(string imageUrl)
    {
        using (UnityWebRequest request = UnityWebRequest.Get(imageUrl))
        {
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                Texture2D texture = DownloadHandlerTexture.GetContent(request);
                // You can use this texture for UI elements
                Debug.Log("Profile picture loaded successfully");
            }
            else
            {
                Debug.LogError($"Failed to load profile picture: {request.error}");
            }
        }
    }
}

[System.Serializable]
public class AuthResponse
{
    public string jwt;
    public UserInfo user;
}

[System.Serializable]
public class UserInfo
{
    public string id;
    public string email;
    public string name;
    public string picture;
}
