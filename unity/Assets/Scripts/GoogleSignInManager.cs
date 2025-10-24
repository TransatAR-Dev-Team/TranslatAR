using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Networking;
using TMPro;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Text;

/// <summary>
/// Manages Google Sign-In authentication for Unity applications.
/// Handles OAuth flow, token exchange, and user profile management.
/// </summary>
public class GoogleSignInManager : MonoBehaviour
{
    [Header("Google OAuth Configuration")]
    [SerializeField] private string clientId = "861587845879-v6ih92nnkk9h1isaiv7gafaqaguockq8.apps.googleusercontent.com";
    [SerializeField] private string redirectUri = "http://localhost:8000/auth/google/callback";
    [SerializeField] private string backendUrl = "http://localhost:8000";
    
    [Header("UI References")]
    [SerializeField] private Button signInButton;
    [SerializeField] private Button signOutButton;
    [SerializeField] private TextMeshProUGUI userInfoText;
    [SerializeField] private Image userProfileImage;
    [SerializeField] private GameObject loginPanel;
    [SerializeField] private GameObject userPanel;
    
    [Header("Authentication State")]
    [SerializeField] private bool isAuthenticated = false;
    [SerializeField] private string currentToken = "";
    [SerializeField] private UserProfile currentUser = null;
    
    // Events
    public static event Action<UserProfile> OnUserSignedIn;
    public static event Action OnUserSignedOut;
    
    // Singleton pattern
    public static GoogleSignInManager Instance { get; private set; }
    
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
    
    void Start()
    {
        InitializeUI();
        CheckExistingAuth();
    }
    
    /// <summary>
    /// Initializes UI elements and sets up button listeners
    /// </summary>
    void InitializeUI()
    {
        if (signInButton != null)
            signInButton.onClick.AddListener(StartGoogleSignIn);
            
        if (signOutButton != null)
            signOutButton.onClick.AddListener(SignOut);
            
        UpdateUI();
    }
    
    /// <summary>
    /// Checks if user is already authenticated from previous session
    /// </summary>
    void CheckExistingAuth()
    {
        string savedToken = PlayerPrefs.GetString("GoogleAuthToken", "");
        if (!string.IsNullOrEmpty(savedToken))
        {
            VerifyToken(savedToken);
        }
    }
    
    /// <summary>
    /// Initiates Google OAuth sign-in process
    /// </summary>
    public void StartGoogleSignIn()
    {
        Debug.Log("Starting Google Sign-In...");
        
        // Open Google OAuth URL in system browser
        string authUrl = $"{backendUrl}/auth/google";
        Application.OpenURL(authUrl);
        
        // Start polling for callback
        StartCoroutine(PollForAuthCallback());
    }
    
    /// <summary>
    /// Polls the backend for authentication completion
    /// </summary>
    IEnumerator PollForAuthCallback()
    {
        float pollInterval = 2f;
        float timeout = 60f; // 1 minute timeout
        float elapsed = 0f;
        
        while (elapsed < timeout)
        {
            yield return new WaitForSeconds(pollInterval);
            elapsed += pollInterval;
            
            // Check if we have a pending auth (this would need backend support)
            // For now, we'll simulate the process
            Debug.Log($"Polling for auth completion... ({elapsed}s)");
        }
        
        Debug.Log("Authentication timeout");
    }
    
    /// <summary>
    /// Handles the authentication callback with authorization code
    /// </summary>
    public void HandleAuthCallback(string authCode)
    {
        StartCoroutine(ExchangeCodeForToken(authCode));
    }
    
    /// <summary>
    /// Exchanges authorization code for access token
    /// </summary>
    IEnumerator ExchangeCodeForToken(string authCode)
    {
        string url = $"{backendUrl}/auth/google/callback?code={authCode}";
        
        using (var request = UnityEngine.Networking.UnityWebRequest.Get(url))
        {
            yield return request.SendWebRequest();
            
            if (request.result == UnityEngine.Networking.UnityWebRequest.Result.Success)
            {
                try
                {
                    var response = JsonUtility.FromJson<AuthResponse>(request.downloadHandler.text);
                    ProcessAuthSuccess(response);
                }
                catch (Exception e)
                {
                    Debug.LogError($"Error parsing auth response: {e.Message}");
                }
            }
            else
            {
                Debug.LogError($"Auth request failed: {request.error}");
            }
        }
    }
    
    /// <summary>
    /// Processes successful authentication response
    /// </summary>
    void ProcessAuthSuccess(AuthResponse response)
    {
        currentToken = response.jwt;
        currentUser = response.user;
        isAuthenticated = true;
        
        // Save token for future sessions
        PlayerPrefs.SetString("GoogleAuthToken", currentToken);
        PlayerPrefs.Save();
        
        // Update UI
        UpdateUI();
        
        // Fire event
        OnUserSignedIn?.Invoke(currentUser);
        
        Debug.Log($"User signed in: {currentUser.name} ({currentUser.email})");
    }
    
    /// <summary>
    /// Verifies existing token with backend
    /// </summary>
    void VerifyToken(string token)
    {
        StartCoroutine(VerifyTokenCoroutine(token));
    }
    
    /// <summary>
    /// Coroutine to verify token with backend
    /// </summary>
    IEnumerator VerifyTokenCoroutine(string token)
    {
        string url = $"{backendUrl}/auth/verify?token={token}";
        
        using (var request = UnityEngine.Networking.UnityWebRequest.Get(url))
        {
            yield return request.SendWebRequest();
            
            if (request.result == UnityEngine.Networking.UnityWebRequest.Result.Success)
            {
                try
                {
                    var response = JsonUtility.FromJson<TokenVerifyResponse>(request.downloadHandler.text);
                    if (response.valid)
                    {
                        // Get user info
                        yield return StartCoroutine(GetUserInfo(token));
                    }
                    else
                    {
                        // Token invalid, clear it
                        PlayerPrefs.DeleteKey("GoogleAuthToken");
                        currentToken = "";
                        isAuthenticated = false;
                        UpdateUI();
                    }
                }
                catch (Exception e)
                {
                    Debug.LogError($"Error verifying token: {e.Message}");
                }
            }
        }
    }
    
    /// <summary>
    /// Gets user information from backend
    /// </summary>
    IEnumerator GetUserInfo(string token)
    {
        string url = $"{backendUrl}/auth/me";
        
        using (var request = UnityEngine.Networking.UnityWebRequest.Get(url))
        {
            request.SetRequestHeader("Authorization", $"Bearer {token}");
            yield return request.SendWebRequest();
            
            if (request.result == UnityEngine.Networking.UnityWebRequest.Result.Success)
            {
                try
                {
                    currentUser = JsonUtility.FromJson<UserProfile>(request.downloadHandler.text);
                    currentToken = token;
                    isAuthenticated = true;
                    UpdateUI();
                    OnUserSignedIn?.Invoke(currentUser);
                }
                catch (Exception e)
                {
                    Debug.LogError($"Error getting user info: {e.Message}");
                }
            }
        }
    }
    
    /// <summary>
    /// Signs out the current user
    /// </summary>
    public void SignOut()
    {
        currentToken = "";
        currentUser = null;
        isAuthenticated = false;
        
        // Clear saved token
        PlayerPrefs.DeleteKey("GoogleAuthToken");
        PlayerPrefs.Save();
        
        // Update UI
        UpdateUI();
        
        // Fire event
        OnUserSignedOut?.Invoke();
        
        Debug.Log("User signed out");
    }
    
    /// <summary>
    /// Updates UI based on authentication state
    /// </summary>
    void UpdateUI()
    {
        if (loginPanel != null)
            loginPanel.SetActive(!isAuthenticated);
            
        if (userPanel != null)
            userPanel.SetActive(isAuthenticated);
            
        if (signInButton != null)
            signInButton.gameObject.SetActive(!isAuthenticated);
            
        if (signOutButton != null)
            signOutButton.gameObject.SetActive(isAuthenticated);
            
        if (isAuthenticated && currentUser != null)
        {
            if (userInfoText != null)
            {
                userInfoText.text = $"Welcome, {currentUser.name}!\n{currentUser.email}";
            }
            
            if (userProfileImage != null && !string.IsNullOrEmpty(currentUser.picture))
            {
                StartCoroutine(LoadProfileImage(currentUser.picture));
            }
        }
    }
    
    /// <summary>
    /// Loads user profile image from URL
    /// </summary>
    IEnumerator LoadProfileImage(string imageUrl)
    {
        using (var request = UnityWebRequest.Get(imageUrl))
        {
            request.downloadHandler = new DownloadHandlerTexture();
            yield return request.SendWebRequest();
            
            if (request.result == UnityEngine.Networking.UnityWebRequest.Result.Success)
            {
                var texture = ((DownloadHandlerTexture)request.downloadHandler).texture;
                var sprite = Sprite.Create(texture, new Rect(0, 0, texture.width, texture.height), new Vector2(0.5f, 0.5f));
                userProfileImage.sprite = sprite;
            }
        }
    }
    
    /// <summary>
    /// Gets the current authentication token
    /// </summary>
    public string GetAuthToken()
    {
        return isAuthenticated ? currentToken : "";
    }
    
    /// <summary>
    /// Gets the current user profile
    /// </summary>
    public UserProfile GetCurrentUser()
    {
        return isAuthenticated ? currentUser : null;
    }
    
    /// <summary>
    /// Checks if user is currently authenticated
    /// </summary>
    public bool IsAuthenticated()
    {
        return isAuthenticated;
    }
}

/// <summary>
/// Represents user profile information from Google
/// </summary>
[System.Serializable]
public class UserProfile
{
    public string id;
    public string email;
    public string name;
    public string picture;
}

/// <summary>
/// Represents authentication response from backend
/// </summary>
[System.Serializable]
public class AuthResponse
{
    public string jwt;
    public UserProfile user;
}

/// <summary>
/// Represents token verification response
/// </summary>
[System.Serializable]
public class TokenVerifyResponse
{
    public bool valid;
    public object decoded;
}
