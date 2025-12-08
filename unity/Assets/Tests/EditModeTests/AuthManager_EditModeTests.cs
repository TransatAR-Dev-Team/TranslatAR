using NUnit.Framework;
using UnityEngine;
using System.Collections;
using System.Reflection;

/// <summary>
/// Edit mode tests for AuthManager
/// Tests authentication flow, state management, and token handling
/// NOTE: Singleton pattern tests are simplified for edit mode (no DontDestroyOnLoad)
/// </summary>
public class AuthManager_EditModeTests
{
    private GameObject testGameObject;
    private AuthManager authManager;
    private const string TestJwtToken = "test.jwt.token";
    private const string JwtPlayerPrefsKey = "AppAuthToken";

    [SetUp]
    public void SetUp()
    {
        // Clean up PlayerPrefs before each test
        PlayerPrefs.DeleteKey(JwtPlayerPrefsKey);
        PlayerPrefs.Save();

        testGameObject = new GameObject("AuthManagerTest");
        authManager = testGameObject.AddComponent<AuthManager>();
        
        // Add required AuthBackendService component
        testGameObject.AddComponent<AuthBackendService>();
        
        // Reset singleton for clean state
        ResetSingleton();
    }

    [TearDown]
    public void TearDown()
    {
        // Clean up PlayerPrefs
        PlayerPrefs.DeleteKey(JwtPlayerPrefsKey);
        PlayerPrefs.Save();

        // Reset singleton
        ResetSingleton();

        if (testGameObject != null)
        {
            UnityEngine.Object.DestroyImmediate(testGameObject);
        }
    }

    private void ResetSingleton()
    {
        var instanceField = typeof(AuthManager).GetProperty("Instance", 
            BindingFlags.Static | BindingFlags.Public);
        if (instanceField != null)
        {
            instanceField.SetValue(null, null);
        }
    }

    [Test]
    public void AuthManager_InitializesWithCorrectDefaults()
    {
        // Assert - Check initial values without calling Awake (DontDestroyOnLoad issue)
        Assert.IsNull(authManager.CurrentUser, "CurrentUser should be null initially");
        Assert.IsNull(authManager.CurrentJwt, "CurrentJwt should be null initially");
    }

    [Test]
    public void AuthManager_Logout_ClearsTokenAndState()
    {
        // Arrange - Set up logged in state directly
        PlayerPrefs.SetString(JwtPlayerPrefsKey, TestJwtToken);
        var jwtField = GetPrivateField(typeof(AuthManager), "_currentJwt");
        jwtField.SetValue(authManager, TestJwtToken);
        
        var stateProperty = typeof(AuthManager).GetProperty("CurrentState");
        stateProperty.SetValue(authManager, AuthManager.AuthState.LoggedIn);

        // Act
        authManager.Logout();

        // Assert
        Assert.IsFalse(PlayerPrefs.HasKey(JwtPlayerPrefsKey), "JWT should be removed from PlayerPrefs");
        Assert.AreEqual(AuthManager.AuthState.LoggedOut, authManager.CurrentState, 
            "State should be LoggedOut");
    }

    [Test]
    public void AuthManager_StartLoginFlow_OnlyWorksWhenLoggedOut()
    {
        // Arrange - Set state to LoggedIn
        var stateProperty = typeof(AuthManager).GetProperty("CurrentState");
        stateProperty.SetValue(authManager, AuthManager.AuthState.LoggedIn);

        // Act
        authManager.StartLoginFlow();

        // Assert - State should remain LoggedIn (flow shouldn't start)
        Assert.AreEqual(AuthManager.AuthState.LoggedIn, authManager.CurrentState, 
            "StartLoginFlow should not work when already logged in");
    }

    [Test]
    public void OnDeviceCodeReceived_UpdatesStateToAwaitingLogin()
    {
        // Arrange
        var response = new DeviceStartResponse
        {
            user_code = "TEST123",
            verification_url = "https://example.com/verify",
            device_code = "device123",
            interval = 5,
            expires_in = 600
        };
        
        var method = GetPrivateMethod(typeof(AuthManager), "OnDeviceCodeReceived");
        var stateProperty = typeof(AuthManager).GetProperty("CurrentState");

        // Act
        method.Invoke(authManager, new object[] { response });

        // Assert
        Assert.AreEqual(AuthManager.AuthState.AwaitingDeviceLogin, authManager.CurrentState, 
            "State should be AwaitingDeviceLogin after receiving device code");
    }

    [Test]
    public void OnProfileReceived_UpdatesUserAndState()
    {
        // Arrange
        var profile = new UserProfile
        {
            _id = "user123",
            googleId = "google123",
            email = "test@example.com",
            username = "testuser"
        };
        
        var method = GetPrivateMethod(typeof(AuthManager), "OnProfileReceived");

        // Act
        method.Invoke(authManager, new object[] { profile });

        // Assert
        Assert.AreEqual(AuthManager.AuthState.LoggedIn, authManager.CurrentState, 
            "State should be LoggedIn after receiving profile");
        Assert.AreEqual(profile, authManager.CurrentUser, 
            "CurrentUser should be set to received profile");
        Assert.AreEqual("testuser", authManager.CurrentUser.username, 
            "Username should match");
    }

    [Test]
    public void OnAuthError_ResetsStateToLoggedOut()
    {
        // Arrange
        var stateProperty = typeof(AuthManager).GetProperty("CurrentState");
        stateProperty.SetValue(authManager, AuthManager.AuthState.AwaitingDeviceLogin);
        
        var method = GetPrivateMethod(typeof(AuthManager), "OnAuthError");

        // Act - Expect error log
        UnityEngine.TestTools.LogAssert.Expect(LogType.Error, 
            new System.Text.RegularExpressions.Regex(".*An error occurred.*"));
        method.Invoke(authManager, new object[] { "Test error message" });

        // Assert
        Assert.AreEqual(AuthManager.AuthState.LoggedOut, authManager.CurrentState, 
            "State should reset to LoggedOut on error");
    }

    [Test]
    public void OnPollResponse_HandlesAuthorizationPending()
    {
        // Arrange
        var response = new DevicePollResponse
        {
            status = "authorization_pending"
        };
        
        var stateProperty = typeof(AuthManager).GetProperty("CurrentState");
        stateProperty.SetValue(authManager, AuthManager.AuthState.AwaitingDeviceLogin);
        
        var method = GetPrivateMethod(typeof(AuthManager), "OnPollResponse");

        // Act
        method.Invoke(authManager, new object[] { response });

        // Assert
        Assert.AreEqual(AuthManager.AuthState.AwaitingDeviceLogin, authManager.CurrentState, 
            "State should remain AwaitingDeviceLogin while authorization is pending");
    }

    [Test]
    public void DeviceStartResponse_SerializesCorrectly()
    {
        // Arrange
        string json = @"{
            ""user_code"": ""ABC123"",
            ""verification_url"": ""https://example.com"",
            ""device_code"": ""device456"",
            ""interval"": 5,
            ""expires_in"": 600
        }";

        // Act
        var response = JsonUtility.FromJson<DeviceStartResponse>(json);

        // Assert
        Assert.AreEqual("ABC123", response.user_code);
        Assert.AreEqual("https://example.com", response.verification_url);
        Assert.AreEqual("device456", response.device_code);
        Assert.AreEqual(5, response.interval);
        Assert.AreEqual(600, response.expires_in);
    }

    [Test]
    public void DevicePollResponse_SerializesCorrectly()
    {
        // Arrange
        string json = @"{
            ""status"": ""completed"",
            ""access_token"": ""token123"",
            ""token_type"": ""Bearer""
        }";

        // Act
        var response = JsonUtility.FromJson<DevicePollResponse>(json);

        // Assert
        Assert.AreEqual("completed", response.status);
        Assert.AreEqual("token123", response.access_token);
        Assert.AreEqual("Bearer", response.token_type);
    }

    [Test]
    public void UserProfile_SerializesCorrectly()
    {
        // Arrange
        string json = @"{
            ""_id"": ""user789"",
            ""googleId"": ""google789"",
            ""email"": ""user@example.com"",
            ""username"": ""username123""
        }";

        // Act
        var profile = JsonUtility.FromJson<UserProfile>(json);

        // Assert
        Assert.AreEqual("user789", profile._id);
        Assert.AreEqual("google789", profile.googleId);
        Assert.AreEqual("user@example.com", profile.email);
        Assert.AreEqual("username123", profile.username);
    }

    [Test]
    public void AuthManager_CurrentJwt_ReturnsCorrectValue()
    {
        // Arrange
        var jwtField = GetPrivateField(typeof(AuthManager), "_currentJwt");
        jwtField.SetValue(authManager, TestJwtToken);

        // Act
        string jwt = authManager.CurrentJwt;

        // Assert
        Assert.AreEqual(TestJwtToken, jwt, "CurrentJwt should return the stored JWT");
    }

    private MethodInfo GetPrivateMethod(System.Type type, string methodName)
    {
        return type.GetMethod(methodName, 
            BindingFlags.NonPublic | BindingFlags.Instance);
    }

    private FieldInfo GetPrivateField(System.Type type, string fieldName)
    {
        return type.GetField(fieldName, 
            BindingFlags.NonPublic | BindingFlags.Instance);
    }
}