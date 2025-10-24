using UnityEngine;
using UnityEngine.UI;
using TMPro;

/// <summary>
/// Test script to validate Google Sign-In implementation in Unity.
/// This script can be attached to a GameObject to test authentication functionality.
/// </summary>
public class GoogleSignInTest : MonoBehaviour
{
    [Header("Test UI Elements")]
    [SerializeField] private Button testSignInButton;
    [SerializeField] private Button testSignOutButton;
    [SerializeField] private Button testVerifyTokenButton;
    [SerializeField] private TextMeshProUGUI testStatusText;
    [SerializeField] private TextMeshProUGUI testUserInfoText;
    
    [Header("Test Configuration")]
    [SerializeField] private bool enableAutoTest = false;
    [SerializeField] private float autoTestInterval = 5f;
    
    private GoogleSignInManager signInManager;
    private float testTimer = 0f;
    
    void Start()
    {
        InitializeTest();
        SetupUI();
        SubscribeToEvents();
    }
    
    void Update()
    {
        if (enableAutoTest)
        {
            testTimer += Time.deltaTime;
            if (testTimer >= autoTestInterval)
            {
                RunAutomatedTest();
                testTimer = 0f;
            }
        }
    }
    
    void OnDestroy()
    {
        UnsubscribeFromEvents();
    }
    
    /// <summary>
    /// Initializes the test environment
    /// </summary>
    void InitializeTest()
    {
        signInManager = GoogleSignInManager.Instance;
        
        if (signInManager == null)
        {
            LogTest("ERROR: GoogleSignInManager not found! Make sure it's in the scene.");
            return;
        }
        
        LogTest("Google Sign-In Test initialized successfully");
        LogTest($"Backend URL: {signInManager.backendUrl}");
        LogTest($"Client ID: {signInManager.clientId}");
    }
    
    /// <summary>
    /// Sets up test UI elements
    /// </summary>
    void SetupUI()
    {
        if (testSignInButton != null)
            testSignInButton.onClick.AddListener(TestSignIn);
            
        if (testSignOutButton != null)
            testSignOutButton.onClick.AddListener(TestSignOut);
            
        if (testVerifyTokenButton != null)
            testVerifyTokenButton.onClick.AddListener(TestVerifyToken);
    }
    
    /// <summary>
    /// Subscribes to authentication events
    /// </summary>
    void SubscribeToEvents()
    {
        GoogleSignInManager.OnUserSignedIn += OnUserSignedIn;
        GoogleSignInManager.OnUserSignedOut += OnUserSignedOut;
    }
    
    /// <summary>
    /// Unsubscribes from authentication events
    /// </summary>
    void UnsubscribeFromEvents()
    {
        GoogleSignInManager.OnUserSignedIn -= OnUserSignedIn;
        GoogleSignInManager.OnUserSignedOut -= OnUserSignedOut;
    }
    
    /// <summary>
    /// Tests Google Sign-In functionality
    /// </summary>
    public void TestSignIn()
    {
        LogTest("Testing Google Sign-In...");
        
        if (signInManager == null)
        {
            LogTest("ERROR: SignInManager is null!");
            return;
        }
        
        if (signInManager.IsAuthenticated())
        {
            LogTest("User is already authenticated");
            DisplayUserInfo();
        }
        else
        {
            LogTest("Starting Google Sign-In process...");
            signInManager.StartGoogleSignIn();
        }
    }
    
    /// <summary>
    /// Tests sign-out functionality
    /// </summary>
    public void TestSignOut()
    {
        LogTest("Testing Sign-Out...");
        
        if (signInManager == null)
        {
            LogTest("ERROR: SignInManager is null!");
            return;
        }
        
        if (signInManager.IsAuthenticated())
        {
            signInManager.SignOut();
            LogTest("Sign-out completed");
        }
        else
        {
            LogTest("User is not authenticated");
        }
    }
    
    /// <summary>
    /// Tests token verification
    /// </summary>
    public void TestVerifyToken()
    {
        LogTest("Testing Token Verification...");
        
        if (signInManager == null)
        {
            LogTest("ERROR: SignInManager is null!");
            return;
        }
        
        if (signInManager.IsAuthenticated())
        {
            string token = signInManager.GetAuthToken();
            LogTest($"Token: {token.Substring(0, Mathf.Min(20, token.Length))}...");
            LogTest("Token verification test completed");
        }
        else
        {
            LogTest("No token to verify - user not authenticated");
        }
    }
    
    /// <summary>
    /// Runs automated test sequence
    /// </summary>
    void RunAutomatedTest()
    {
        LogTest("=== AUTOMATED TEST ===");
        
        // Test 1: Check authentication status
        bool isAuth = signInManager != null && signInManager.IsAuthenticated();
        LogTest($"Authentication Status: {isAuth}");
        
        // Test 2: Check token availability
        if (isAuth)
        {
            string token = signInManager.GetAuthToken();
            LogTest($"Token Available: {!string.IsNullOrEmpty(token)}");
            
            // Test 3: Check user info
            var user = signInManager.GetCurrentUser();
            if (user != null)
            {
                LogTest($"User Info: {user.name} ({user.email})");
            }
        }
        
        LogTest("=== END AUTOMATED TEST ===");
    }
    
    /// <summary>
    /// Handles user signed in event
    /// </summary>
    void OnUserSignedIn(UserProfile user)
    {
        LogTest($"SUCCESS: User signed in - {user.name} ({user.email})");
        DisplayUserInfo();
    }
    
    /// <summary>
    /// Handles user signed out event
    /// </summary>
    void OnUserSignedOut()
    {
        LogTest("SUCCESS: User signed out");
        ClearUserInfo();
    }
    
    /// <summary>
    /// Displays current user information
    /// </summary>
    void DisplayUserInfo()
    {
        if (signInManager == null || !signInManager.IsAuthenticated())
        {
            ClearUserInfo();
            return;
        }
        
        var user = signInManager.GetCurrentUser();
        if (user != null && testUserInfoText != null)
        {
            testUserInfoText.text = $"Name: {user.name}\nEmail: {user.email}\nID: {user.id}";
        }
    }
    
    /// <summary>
    /// Clears user information display
    /// </summary>
    void ClearUserInfo()
    {
        if (testUserInfoText != null)
        {
            testUserInfoText.text = "Not authenticated";
        }
    }
    
    /// <summary>
    /// Logs test messages
    /// </summary>
    void LogTest(string message)
    {
        Debug.Log($"[GoogleSignInTest] {message}");
        
        if (testStatusText != null)
        {
            testStatusText.text = message;
        }
    }
    
    /// <summary>
    /// Validates the implementation
    /// </summary>
    [ContextMenu("Validate Implementation")]
    public void ValidateImplementation()
    {
        LogTest("=== VALIDATION START ===");
        
        // Check 1: GoogleSignInManager exists
        if (signInManager == null)
        {
            LogTest("❌ FAIL: GoogleSignInManager not found");
            return;
        }
        LogTest("✅ PASS: GoogleSignInManager found");
        
        // Check 2: Configuration is valid
        if (string.IsNullOrEmpty(signInManager.clientId))
        {
            LogTest("❌ FAIL: Client ID not configured");
        }
        else
        {
            LogTest("✅ PASS: Client ID configured");
        }
        
        if (string.IsNullOrEmpty(signInManager.backendUrl))
        {
            LogTest("❌ FAIL: Backend URL not configured");
        }
        else
        {
            LogTest("✅ PASS: Backend URL configured");
        }
        
        // Check 3: Authentication state
        bool isAuth = signInManager.IsAuthenticated();
        LogTest($"Authentication State: {(isAuth ? "Authenticated" : "Not Authenticated")}");
        
        if (isAuth)
        {
            var user = signInManager.GetCurrentUser();
            if (user != null)
            {
                LogTest($"✅ PASS: User profile available - {user.name}");
            }
            else
            {
                LogTest("❌ FAIL: User profile is null");
            }
        }
        
        LogTest("=== VALIDATION COMPLETE ===");
    }
}


