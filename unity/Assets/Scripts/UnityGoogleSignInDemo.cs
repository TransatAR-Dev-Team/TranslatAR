using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.Collections;

/// <summary>
/// Simple Unity Google Sign-In Demo
/// This script demonstrates how to use the Google Sign-In system
/// </summary>
public class UnityGoogleSignInDemo : MonoBehaviour
{
    [Header("Demo UI")]
    [SerializeField] private Button signInButton;
    [SerializeField] private Button signOutButton;
    [SerializeField] private TextMeshProUGUI statusText;
    [SerializeField] private TextMeshProUGUI userInfoText;
    [SerializeField] private Image userProfileImage;
    
    [Header("Demo Settings")]
    [SerializeField] private bool showDebugLogs = true;
    
    private GoogleSignInManager signInManager;
    
    void Start()
    {
        InitializeDemo();
        SetupUI();
        SubscribeToEvents();
    }
    
    void OnDestroy()
    {
        UnsubscribeFromEvents();
    }
    
    /// <summary>
    /// Initialize the demo
    /// </summary>
    void InitializeDemo()
    {
        // Get the Google Sign-In Manager
        signInManager = GoogleSignInManager.Instance;
        
        if (signInManager == null)
        {
            LogDemo("ERROR: GoogleSignInManager not found! Please add it to your scene.");
            return;
        }
        
        LogDemo("Unity Google Sign-In Demo initialized!");
        LogDemo($"Backend URL: {signInManager.backendUrl}");
        LogDemo($"Client ID: {signInManager.clientId}");
        
        // Check if user is already signed in
        if (signInManager.IsAuthenticated())
        {
            LogDemo("User is already signed in!");
            DisplayUserInfo();
        }
        else
        {
            LogDemo("User is not signed in. Click 'Sign In with Google' to start.");
        }
    }
    
    /// <summary>
    /// Setup UI elements
    /// </summary>
    void SetupUI()
    {
        if (signInButton != null)
        {
            signInButton.onClick.AddListener(OnSignInClicked);
            signInButton.GetComponentInChildren<TextMeshProUGUI>().text = "Sign In with Google";
        }
        
        if (signOutButton != null)
        {
            signOutButton.onClick.AddListener(OnSignOutClicked);
            signOutButton.GetComponentInChildren<TextMeshProUGUI>().text = "Sign Out";
        }
        
        UpdateUI();
    }
    
    /// <summary>
    /// Subscribe to authentication events
    /// </summary>
    void SubscribeToEvents()
    {
        GoogleSignInManager.OnUserSignedIn += OnUserSignedIn;
        GoogleSignInManager.OnUserSignedOut += OnUserSignedOut;
    }
    
    /// <summary>
    /// Unsubscribe from authentication events
    /// </summary>
    void UnsubscribeFromEvents()
    {
        GoogleSignInManager.OnUserSignedIn -= OnUserSignedIn;
        GoogleSignInManager.OnUserSignedOut -= OnUserSignedOut;
    }
    
    /// <summary>
    /// Handle sign-in button click
    /// </summary>
    void OnSignInClicked()
    {
        LogDemo("Starting Google Sign-In process...");
        
        if (signInManager == null)
        {
            LogDemo("ERROR: SignInManager is null!");
            return;
        }
        
        if (signInManager.IsAuthenticated())
        {
            LogDemo("User is already signed in!");
            return;
        }
        
        // Start the Google Sign-In process
        signInManager.StartGoogleSignIn();
        LogDemo("Google Sign-In process started. Check your browser for the OAuth flow.");
    }
    
    /// <summary>
    /// Handle sign-out button click
    /// </summary>
    void OnSignOutClicked()
    {
        LogDemo("Signing out...");
        
        if (signInManager == null)
        {
            LogDemo("ERROR: SignInManager is null!");
            return;
        }
        
        if (!signInManager.IsAuthenticated())
        {
            LogDemo("User is not signed in!");
            return;
        }
        
        signInManager.SignOut();
        LogDemo("Sign-out completed!");
    }
    
    /// <summary>
    /// Handle user signed in event
    /// </summary>
    void OnUserSignedIn(UserProfile user)
    {
        LogDemo($"SUCCESS: User signed in!");
        LogDemo($"Name: {user.name}");
        LogDemo($"Email: {user.email}");
        LogDemo($"ID: {user.id}");
        
        DisplayUserInfo();
        UpdateUI();
    }
    
    /// <summary>
    /// Handle user signed out event
    /// </summary>
    void OnUserSignedOut()
    {
        LogDemo("User signed out successfully!");
        ClearUserInfo();
        UpdateUI();
    }
    
    /// <summary>
    /// Display user information
    /// </summary>
    void DisplayUserInfo()
    {
        if (signInManager == null || !signInManager.IsAuthenticated())
        {
            ClearUserInfo();
            return;
        }
        
        var user = signInManager.GetCurrentUser();
        if (user != null && userInfoText != null)
        {
            userInfoText.text = $"Welcome, {user.name}!\nEmail: {user.email}";
        }
        
        // Load profile image if available
        if (userProfileImage != null && !string.IsNullOrEmpty(user.picture))
        {
            StartCoroutine(LoadProfileImage(user.picture));
        }
    }
    
    /// <summary>
    /// Clear user information
    /// </summary>
    void ClearUserInfo()
    {
        if (userInfoText != null)
        {
            userInfoText.text = "Not signed in";
        }
        
        if (userProfileImage != null)
        {
            userProfileImage.sprite = null;
        }
    }
    
    /// <summary>
    /// Load user profile image
    /// </summary>
    IEnumerator LoadProfileImage(string imageUrl)
    {
        LogDemo($"Loading profile image from: {imageUrl}");
        
        using (var request = UnityEngine.Networking.UnityWebRequest.Get(imageUrl))
        {
            request.downloadHandler = new UnityEngine.Networking.DownloadHandlerTexture();
            yield return request.SendWebRequest();
            
            if (request.result == UnityEngine.Networking.UnityWebRequest.Result.Success)
            {
                var texture = ((UnityEngine.Networking.DownloadHandlerTexture)request.downloadHandler).texture;
                var sprite = Sprite.Create(texture, new Rect(0, 0, texture.width, texture.height), new Vector2(0.5f, 0.5f));
                userProfileImage.sprite = sprite;
                LogDemo("Profile image loaded successfully!");
            }
            else
            {
                LogDemo($"Failed to load profile image: {request.error}");
            }
        }
    }
    
    /// <summary>
    /// Update UI based on authentication state
    /// </summary>
    void UpdateUI()
    {
        bool isAuthenticated = signInManager != null && signInManager.IsAuthenticated();
        
        if (signInButton != null)
            signInButton.gameObject.SetActive(!isAuthenticated);
            
        if (signOutButton != null)
            signOutButton.gameObject.SetActive(isAuthenticated);
    }
    
    /// <summary>
    /// Log demo messages
    /// </summary>
    void LogDemo(string message)
    {
        if (showDebugLogs)
        {
            Debug.Log($"[UnityGoogleSignInDemo] {message}");
        }
        
        if (statusText != null)
        {
            statusText.text = message;
        }
    }
    
    /// <summary>
    /// Test the authentication system
    /// </summary>
    [ContextMenu("Test Authentication")]
    public void TestAuthentication()
    {
        LogDemo("=== TESTING AUTHENTICATION ===");
        
        if (signInManager == null)
        {
            LogDemo("❌ FAIL: GoogleSignInManager not found");
            return;
        }
        
        LogDemo("✅ PASS: GoogleSignInManager found");
        
        bool isAuth = signInManager.IsAuthenticated();
        LogDemo($"Authentication Status: {(isAuth ? "✅ Authenticated" : "❌ Not Authenticated")}");
        
        if (isAuth)
        {
            var user = signInManager.GetCurrentUser();
            if (user != null)
            {
                LogDemo($"✅ PASS: User profile available - {user.name}");
            }
            else
            {
                LogDemo("❌ FAIL: User profile is null");
            }
        }
        
        LogDemo("=== TEST COMPLETE ===");
    }
}


