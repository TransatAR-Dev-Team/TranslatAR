using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.UI;

public class GoogleSignInManager : MonoBehaviour
{
    [Header("OAuth Configuration")]
    public string clientId = "YOUR_GOOGLE_CLIENT_ID";
    public string redirectUri = "http://localhost:8000/auth/google/callback";
    public string backendUrl = "http://localhost:8000";

    [Header("User Data")]
    public string authToken;
    public string userEmail;
    public string userName;
    public string userPictureUrl;
    public Texture2D userProfilePicture;

    public static GoogleSignInManager Instance { get; private set; }

    private void Awake()
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
        
        // For WebGL builds, use JavaScript interop
        #if UNITY_WEBGL && !UNITY_EDITOR
            GoogleSignInWebGL.OpenGoogleAuthPopup();
        #else
            // For editor and other platforms, open browser
            string authUrl = $"https://accounts.google.com/o/oauth2/v2/auth?" +
                $"client_id={clientId}&" +
                $"redirect_uri={redirectUri}&" +
                $"response_type=code&" +
                $"scope=openid email profile&" +
                $"access_type=offline&" +
                $"prompt=consent";
            
            Application.OpenURL(authUrl);
        #endif
    }

    public void HandleAuthCode(string authCode)
    {
        Debug.Log($"Received auth code: {authCode}");
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
                Debug.Log("Token exchange successful");
                // The backend will redirect to frontend with token
                // We need to extract token from the response
                string response = request.downloadHandler.text;
                Debug.Log($"Response: {response}");
            }
            else
            {
                Debug.LogError($"Token exchange failed: {request.error}");
            }
        }
    }

    public void SetAuthToken(string token)
    {
        authToken = token;
        Debug.Log($"Auth token set: {token}");
        StartCoroutine(VerifyTokenAndGetUserInfo());
    }

    private IEnumerator VerifyTokenAndGetUserInfo()
    {
        string url = $"{backendUrl}/auth/verify?token={authToken}";
        
        using (UnityWebRequest request = UnityWebRequest.Get(url))
        {
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                string response = request.downloadHandler.text;
                Debug.Log($"Token verification response: {response}");
                
                // Parse JSON response to get user info
                var userData = JsonUtility.FromJson<UserData>(response);
                if (userData.valid)
                {
                    userEmail = userData.user.email;
                    userName = userData.user.name;
                    userPictureUrl = userData.user.picture;
                    
                    Debug.Log($"User signed in: {userName} ({userEmail})");
                    
                    // Load profile picture
                    if (!string.IsNullOrEmpty(userPictureUrl))
                    {
                        StartCoroutine(LoadProfileImage(userPictureUrl));
                    }
                }
            }
            else
            {
                Debug.LogError($"Token verification failed: {request.error}");
            }
        }
    }

    private IEnumerator LoadProfileImage(string imageUrl)
    {
        using (UnityWebRequest request = UnityWebRequest.Get(imageUrl))
        {
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                userProfilePicture = DownloadHandlerTexture.GetContent(request);
                Debug.Log("Profile picture loaded successfully");
            }
            else
            {
                Debug.LogError($"Failed to load profile picture: {request.error}");
            }
        }
    }

    public void Logout()
    {
        authToken = null;
        userEmail = null;
        userName = null;
        userPictureUrl = null;
        userProfilePicture = null;
        
        Debug.Log("User logged out");
    }

    public bool IsAuthenticated()
    {
        return !string.IsNullOrEmpty(authToken);
    }

    public string GetCurrentUser()
    {
        return userName ?? "Not signed in";
    }

    public string GetAuthToken()
    {
        return authToken;
    }

    [System.Serializable]
    public class UserData
    {
        public bool valid;
        public UserInfo user;
    }

    [System.Serializable]
    public class UserInfo
    {
        public string user_id;
        public string email;
        public string name;
        public string picture;
    }
}
