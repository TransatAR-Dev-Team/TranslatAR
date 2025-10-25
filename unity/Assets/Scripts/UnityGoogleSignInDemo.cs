using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class UnityGoogleSignInDemo : MonoBehaviour
{
    [Header("UI References")]
    public Button signInButton;
    public Button signOutButton;
    public TextMeshProUGUI statusText;
    public TextMeshProUGUI userInfoText;
    public Image userProfileImage;
    
    [Header("UI Panels")]
    public GameObject loginPanel;
    public GameObject userPanel;
    
    private GoogleSignInManager authManager;
    private GoogleSignInUI uiController;
    
    void Start()
    {
        // Get references
        authManager = GoogleSignInManager.Instance;
        uiController = GetComponent<GoogleSignInUI>();
        
        if (authManager == null)
        {
            Debug.LogError("GoogleSignInManager not found! Make sure it's in the scene.");
            return;
        }
        
        if (uiController == null)
        {
            Debug.LogError("GoogleSignInUI component not found!");
            return;
        }
        
        // Setup demo
        SetupDemo();
    }
    
    void SetupDemo()
    {
        Debug.Log("Setting up Unity Google Sign-In Demo");
        
        // Validate configuration
        if (authManager.config == null || authManager.config.clientId == "YOUR_GOOGLE_CLIENT_ID")
        {
            Debug.LogWarning("Please configure your Google Client ID in the GoogleSignInConfig!");
        }
        
        // Setup UI
        if (uiController != null)
        {
            uiController.signInButton = signInButton;
            uiController.signOutButton = signOutButton;
            uiController.statusText = statusText;
            uiController.userInfoText = userInfoText;
            uiController.userProfileImage = userProfileImage;
            uiController.loginPanel = loginPanel;
            uiController.userPanel = userPanel;
        }
        
        Debug.Log("Demo setup complete!");
    }
    
    void Update()
    {
        // Update demo status
        if (authManager != null)
        {
            bool isAuthenticated = authManager.IsAuthenticated();
            
            if (isAuthenticated)
            {
                Debug.Log($"Demo: User authenticated - {authManager.userName} ({authManager.userEmail})");
            }
        }
    }
    
    public void TestAuthentication()
    {
        if (authManager == null)
        {
            Debug.LogError("Auth manager not available for testing");
            return;
        }
        
        Debug.Log("Testing authentication...");
        Debug.Log($"Is Authenticated: {authManager.IsAuthenticated()}");
        Debug.Log($"Current User: {authManager.GetCurrentUser()}");
        Debug.Log($"Auth Token: {(string.IsNullOrEmpty(authManager.GetAuthToken()) ? "None" : "Present")}");
    }
    
    public void TestSignIn()
    {
        Debug.Log("Testing sign-in process...");
        
        if (authManager != null)
        {
            authManager.StartGoogleSignIn();
        }
        else
        {
            Debug.LogError("Auth manager not available");
        }
    }
    
    public void TestSignOut()
    {
        Debug.Log("Testing sign-out process...");
        
        if (authManager != null)
        {
            authManager.Logout();
        }
        else
        {
            Debug.LogError("Auth manager not available");
        }
    }
    
    public void TestUserInfo()
    {
        if (authManager == null)
        {
            Debug.LogError("Auth manager not available");
            return;
        }
        
        Debug.Log("=== User Information ===");
        Debug.Log($"Name: {authManager.userName}");
        Debug.Log($"Email: {authManager.userEmail}");
        Debug.Log($"Picture URL: {authManager.userPicture}");
        Debug.Log($"Authenticated: {authManager.IsAuthenticated()}");
        Debug.Log("=======================");
    }
    
    public void TestProfilePicture()
    {
        if (authManager == null)
        {
            Debug.LogError("Auth manager not available");
            return;
        }
        
        if (string.IsNullOrEmpty(authManager.userPicture))
        {
            Debug.LogWarning("No profile picture URL available");
            return;
        }
        
        Debug.Log($"Loading profile picture from: {authManager.userPicture}");
        authManager.LoadUserProfilePicture();
    }
    
    void OnGUI()
    {
        if (authManager == null) return;
        
        GUILayout.BeginArea(new Rect(10, 10, 300, 200));
        GUILayout.Label("Unity Google Sign-In Demo", GUI.skin.box);
        
        if (GUILayout.Button("Test Authentication"))
        {
            TestAuthentication();
        }
        
        if (GUILayout.Button("Test Sign In"))
        {
            TestSignIn();
        }
        
        if (GUILayout.Button("Test Sign Out"))
        {
            TestSignOut();
        }
        
        if (GUILayout.Button("Show User Info"))
        {
            TestUserInfo();
        }
        
        if (GUILayout.Button("Load Profile Picture"))
        {
            TestProfilePicture();
        }
        
        GUILayout.Space(10);
        GUILayout.Label($"Status: {(authManager.IsAuthenticated() ? "Signed In" : "Not Signed In")}");
        
        if (authManager.IsAuthenticated())
        {
            GUILayout.Label($"User: {authManager.userName}");
        }
        
        GUILayout.EndArea();
    }
}
