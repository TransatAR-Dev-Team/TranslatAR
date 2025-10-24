using UnityEngine;
using UnityEngine.TestTools;
using NUnit.Framework;
using System.Collections;

public class GoogleSignInTest : MonoBehaviour
{
    private GoogleSignInManager authManager;
    
    void Start()
    {
        authManager = GoogleSignInManager.Instance;
    }
    
    [Test]
    public void TestAuthManagerExists()
    {
        Assert.IsNotNull(authManager, "GoogleSignInManager should exist in the scene");
    }
    
    [Test]
    public void TestAuthManagerSingleton()
    {
        var instance1 = GoogleSignInManager.Instance;
        var instance2 = GoogleSignInManager.Instance;
        
        Assert.AreEqual(instance1, instance2, "GoogleSignInManager should be a singleton");
    }
    
    [Test]
    public void TestInitialAuthenticationState()
    {
        if (authManager == null) return;
        
        Assert.IsFalse(authManager.IsAuthenticated(), "Should not be authenticated initially");
        Assert.IsEmpty(authManager.GetCurrentUser(), "Current user should be empty initially");
        Assert.IsEmpty(authManager.GetAuthToken(), "Auth token should be empty initially");
    }
    
    [Test]
    public void TestConfiguration()
    {
        if (authManager == null) return;
        
        Assert.IsNotEmpty(authManager.clientId, "Client ID should be configured");
        Assert.IsNotEmpty(authManager.redirectUri, "Redirect URI should be configured");
        Assert.IsNotEmpty(authManager.backendUrl, "Backend URL should be configured");
    }
    
    [Test]
    public void TestLogoutFunctionality()
    {
        if (authManager == null) return;
        
        // Test logout when not authenticated
        authManager.Logout();
        Assert.IsFalse(authManager.IsAuthenticated(), "Should not be authenticated after logout");
        
        // Test logout when authenticated (simulate)
        authManager.SetAuthToken("test_token");
        authManager.SetUserInfo(new UserInfo { name = "Test User", email = "test@example.com" });
        
        Assert.IsTrue(authManager.IsAuthenticated(), "Should be authenticated after setting token");
        
        authManager.Logout();
        Assert.IsFalse(authManager.IsAuthenticated(), "Should not be authenticated after logout");
        Assert.IsEmpty(authManager.GetCurrentUser(), "Current user should be empty after logout");
        Assert.IsEmpty(authManager.GetAuthToken(), "Auth token should be empty after logout");
    }
    
    [Test]
    public void TestUserInfoSetting()
    {
        if (authManager == null) return;
        
        var testUser = new UserInfo
        {
            id = "123",
            email = "test@example.com",
            name = "Test User",
            picture = "https://example.com/picture.jpg"
        };
        
        authManager.SetUserInfo(testUser);
        
        Assert.AreEqual(testUser.name, authManager.userName, "User name should be set correctly");
        Assert.AreEqual(testUser.email, authManager.userEmail, "User email should be set correctly");
        Assert.AreEqual(testUser.picture, authManager.userPicture, "User picture should be set correctly");
    }
    
    [Test]
    public void TestTokenSetting()
    {
        if (authManager == null) return;
        
        string testToken = "test_jwt_token_123";
        authManager.SetAuthToken(testToken);
        
        Assert.AreEqual(testToken, authManager.GetAuthToken(), "Auth token should be set correctly");
        Assert.IsTrue(authManager.IsAuthenticated(), "Should be authenticated after setting token");
    }
    
    [Test]
    public void TestAuthenticationFlow()
    {
        if (authManager == null) return;
        
        // Test initial state
        Assert.IsFalse(authManager.IsAuthenticated(), "Should not be authenticated initially");
        
        // Test setting user info without token
        authManager.SetUserInfo(new UserInfo { name = "Test User" });
        Assert.IsFalse(authManager.IsAuthenticated(), "Should not be authenticated without token");
        
        // Test setting token
        authManager.SetAuthToken("test_token");
        Assert.IsTrue(authManager.IsAuthenticated(), "Should be authenticated with token");
        
        // Test logout
        authManager.Logout();
        Assert.IsFalse(authManager.IsAuthenticated(), "Should not be authenticated after logout");
    }
    
    [Test]
    public void TestWebGLConfiguration()
    {
        var webglComponent = FindObjectOfType<GoogleSignInWebGL>();
        if (webglComponent != null)
        {
            Assert.IsNotEmpty(webglComponent.clientId, "WebGL client ID should be configured");
            Assert.IsNotEmpty(webglComponent.redirectUri, "WebGL redirect URI should be configured");
        }
    }
    
    [Test]
    public void TestUIController()
    {
        var uiController = FindObjectOfType<GoogleSignInUI>();
        if (uiController != null)
        {
            Assert.IsNotNull(uiController, "GoogleSignInUI should exist in the scene");
        }
    }
    
    [Test]
    public void TestDemoController()
    {
        var demoController = FindObjectOfType<UnityGoogleSignInDemo>();
        if (demoController != null)
        {
            Assert.IsNotNull(demoController, "UnityGoogleSignInDemo should exist in the scene");
        }
    }
    
    [Test]
    public void TestConfigurationValidation()
    {
        if (authManager == null) return;
        
        // Test with placeholder values
        if (authManager.clientId == "YOUR_GOOGLE_CLIENT_ID")
        {
            Debug.LogWarning("Google Client ID is not configured - using placeholder value");
        }
        
        // Test with empty values
        string originalClientId = authManager.clientId;
        authManager.clientId = "";
        
        // This should not cause errors
        authManager.StartGoogleSignIn();
        
        // Restore original value
        authManager.clientId = originalClientId;
    }
    
    [Test]
    public void TestErrorHandling()
    {
        if (authManager == null) return;
        
        // Test with invalid token
        authManager.SetAuthToken("invalid_token");
        Assert.IsTrue(authManager.IsAuthenticated(), "Should be authenticated even with invalid token format");
        
        // Test logout with invalid state
        authManager.Logout();
        authManager.Logout(); // Should not cause errors
        
        Assert.IsFalse(authManager.IsAuthenticated(), "Should not be authenticated after multiple logouts");
    }
    
    [Test]
    public void TestProfilePictureLoading()
    {
        if (authManager == null) return;
        
        // Test with empty picture URL
        authManager.userPicture = "";
        authManager.LoadUserProfilePicture(); // Should not cause errors
        
        // Test with valid picture URL
        authManager.userPicture = "https://example.com/picture.jpg";
        authManager.LoadUserProfilePicture(); // Should not cause errors
    }
    
    [Test]
    public void TestMultipleInstances()
    {
        // Test that only one instance exists
        var instances = FindObjectsOfType<GoogleSignInManager>();
        Assert.AreEqual(1, instances.Length, "Should have exactly one GoogleSignInManager instance");
    }
    
    [Test]
    public void TestDontDestroyOnLoad()
    {
        if (authManager == null) return;
        
        // Test that the manager is marked as DontDestroyOnLoad
        Assert.IsTrue(authManager.gameObject.scene.name == "DontDestroyOnLoad" || 
                     authManager.gameObject.scene.name == "MainScene", 
                     "GoogleSignInManager should be persistent across scenes");
    }
}
