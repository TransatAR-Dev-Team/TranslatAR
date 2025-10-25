using UnityEngine;
using UnityEngine.UI;
using NUnit.Framework;
using UnityEngine.TestTools;
using System.Collections;

public class TestRunnerButton : MonoBehaviour
{
    [Header("UI References")]
    public Button runTestsButton;
    public Text testResultsText;
    
    void Start()
    {
        if (runTestsButton != null)
        {
            runTestsButton.onClick.AddListener(RunAllTests);
        }
    }
    
    public void RunAllTests()
    {
        Debug.Log("Starting Unity Google Sign-In Tests...");
        StartCoroutine(RunTestsCoroutine());
    }
    
    private IEnumerator RunTestsCoroutine()
    {
        // Test 1: GoogleSignInManager
        yield return TestGoogleSignInManager();
        
        // Test 2: GoogleSignInConfig
        yield return TestGoogleSignInConfig();
        
        // Test 3: GoogleSignInUI
        yield return TestGoogleSignInUI();
        
        Debug.Log("All Unity Google Sign-In Tests completed!");
        
        if (testResultsText != null)
        {
            testResultsText.text = "All tests completed! Check Console for details.";
        }
    }
    
    private IEnumerator TestGoogleSignInManager()
    {
        Debug.Log("Testing GoogleSignInManager...");
        
        // Create test GameObject
        GameObject testObject = new GameObject("TestGoogleSignInManager");
        GoogleSignInManager manager = testObject.AddComponent<GoogleSignInManager>();
        
        // Test singleton
        Assert.IsNotNull(GoogleSignInManager.Instance);
        
        // Test initial state
        Assert.IsFalse(manager.IsAuthenticated());
        Assert.IsEmpty(manager.GetCurrentUser());
        
        // Test token setting
        string testToken = "test_jwt_token_123";
        manager.SetAuthToken(testToken);
        Assert.IsTrue(manager.IsAuthenticated());
        Assert.AreEqual(testToken, manager.GetAuthToken());
        
        // Test user info
        UserInfo testUser = new UserInfo
        {
            id = "123",
            email = "test@example.com",
            name = "Test User",
            picture = "https://example.com/picture.jpg"
        };
        manager.SetUserInfo(testUser);
        Assert.AreEqual(testUser.name, manager.userName);
        
        // Test logout
        manager.Logout();
        Assert.IsFalse(manager.IsAuthenticated());
        
        Object.DestroyImmediate(testObject);
        Debug.Log("GoogleSignInManager tests passed!");
        yield return null;
    }
    
    private IEnumerator TestGoogleSignInConfig()
    {
        Debug.Log("Testing GoogleSignInConfig...");
        
        GoogleSignInConfig config = ScriptableObject.CreateInstance<GoogleSignInConfig>();
        
        // Test default values
        Assert.IsNotEmpty(config.clientId);
        Assert.IsNotEmpty(config.redirectUri);
        Assert.IsNotEmpty(config.backendUrl);
        
        // Test URL generation
        string authUrl = config.GetAuthUrl();
        Assert.IsNotEmpty(authUrl);
        Assert.IsTrue(authUrl.Contains(config.clientId));
        
        // Test validation
        Assert.IsTrue(config.IsValid());
        
        Object.DestroyImmediate(config);
        Debug.Log("GoogleSignInConfig tests passed!");
        yield return null;
    }
    
    private IEnumerator TestGoogleSignInUI()
    {
        Debug.Log("Testing GoogleSignInUI...");
        
        GameObject uiObject = new GameObject("TestGoogleSignInUI");
        GoogleSignInUI uiController = uiObject.AddComponent<GoogleSignInUI>();
        
        // Test that UI controller can be created
        Assert.IsNotNull(uiController);
        
        // Test button click methods don't throw errors
        Assert.DoesNotThrow(() => uiController.OnSignInButtonClick());
        Assert.DoesNotThrow(() => uiController.OnSignOutButtonClick());
        
        // Test UI update doesn't throw errors
        Assert.DoesNotThrow(() => uiController.UpdateUI());
        
        Object.DestroyImmediate(uiObject);
        Debug.Log("GoogleSignInUI tests passed!");
        yield return null;
    }
}
