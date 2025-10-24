using UnityEngine;
using UnityEngine.TestTools;
using NUnit.Framework;
using System.Collections;

public class GoogleSignInConfigTest
{
    private GoogleSignInConfig config;
    
    [SetUp]
    public void Setup()
    {
        // Create a test config
        config = ScriptableObject.CreateInstance<GoogleSignInConfig>();
        config.clientId = "test_client_id";
        config.clientSecret = "test_client_secret";
        config.redirectUri = "http://localhost:8000/auth/google/callback";
        config.backendUrl = "http://localhost:8000";
        config.authEndpoint = "/auth/google";
        config.callbackEndpoint = "/auth/google/callback";
        config.verifyEndpoint = "/auth/verify";
        config.scopes = new string[] { "openid", "email", "profile" };
        config.autoSelect = false;
        config.cancelOnTapOutside = false;
        config.context = "signup";
        config.itpSupport = true;
        config.useFedcmForPrompt = true;
        config.uxMode = "popup";
    }
    
    [TearDown]
    public void TearDown()
    {
        if (config != null)
        {
            Object.DestroyImmediate(config);
        }
    }
    
    [Test]
    public void TestGetAuthUrl()
    {
        string authUrl = config.GetAuthUrl();
        
        Assert.IsTrue(authUrl.Contains("http://localhost:8000/auth/google"));
        Assert.IsTrue(authUrl.Contains("client_id=test_client_id"));
        Assert.IsTrue(authUrl.Contains("redirect_uri=http://localhost:8000/auth/google/callback"));
        Assert.IsTrue(authUrl.Contains("scope=openid email profile"));
        Assert.IsTrue(authUrl.Contains("response_type=code"));
        Assert.IsTrue(authUrl.Contains("access_type=offline"));
    }
    
    [Test]
    public void TestGetCallbackUrl()
    {
        string callbackUrl = config.GetCallbackUrl();
        Assert.AreEqual("http://localhost:8000/auth/google/callback", callbackUrl);
    }
    
    [Test]
    public void TestGetVerifyUrl()
    {
        string token = "test_token_123";
        string verifyUrl = config.GetVerifyUrl(token);
        Assert.AreEqual("http://localhost:8000/auth/verify?token=test_token_123", verifyUrl);
    }
    
    [Test]
    public void TestGetOneTapEndpoint()
    {
        string oneTapUrl = config.GetOneTapEndpoint();
        Assert.AreEqual("http://localhost:8000/auth/google/one-tap", oneTapUrl);
    }
    
    [Test]
    public void TestGetScopeString()
    {
        string scopeString = config.GetScopeString();
        Assert.AreEqual("openid email profile", scopeString);
    }
    
    [Test]
    public void TestGetWebGLInitScript()
    {
        string initScript = config.GetWebGLInitScript();
        
        Assert.IsTrue(initScript.Contains("window.google.accounts.id.initialize"));
        Assert.IsTrue(initScript.Contains("client_id: 'test_client_id'"));
        Assert.IsTrue(initScript.Contains("auto_select: false"));
        Assert.IsTrue(initScript.Contains("cancel_on_tap_outside: false"));
        Assert.IsTrue(initScript.Contains("context: 'signup'"));
        Assert.IsTrue(initScript.Contains("itp_support: true"));
        Assert.IsTrue(initScript.Contains("use_fedcm_for_prompt: true"));
        Assert.IsTrue(initScript.Contains("ux_mode: 'popup'"));
    }
    
    [Test]
    public void TestGetWebGLPromptScript()
    {
        string promptScript = config.GetWebGLPromptScript();
        
        Assert.IsTrue(promptScript.Contains("window.google.accounts.id.prompt"));
        Assert.IsTrue(promptScript.Contains("One-tap notification"));
        Assert.IsTrue(promptScript.Contains("isNotDisplayed"));
        Assert.IsTrue(promptScript.Contains("isSkippedMoment"));
    }
    
    [Test]
    public void TestIsValid_WithValidConfig()
    {
        Assert.IsTrue(config.IsValid());
    }
    
    [Test]
    public void TestIsValid_WithEmptyClientId()
    {
        config.clientId = "";
        Assert.IsFalse(config.IsValid());
    }
    
    [Test]
    public void TestIsValid_WithEmptyRedirectUri()
    {
        config.redirectUri = "";
        Assert.IsFalse(config.IsValid());
    }
    
    [Test]
    public void TestIsValid_WithEmptyBackendUrl()
    {
        config.backendUrl = "";
        Assert.IsFalse(config.IsValid());
    }
    
    [Test]
    public void TestValidate_WithValidConfig()
    {
        // Should not throw any exceptions
        config.Validate();
    }
    
    [Test]
    public void TestValidate_WithEmptyClientId()
    {
        config.clientId = "";
        
        // Should log warning but not throw exception
        config.Validate();
    }
    
    [Test]
    public void TestValidate_WithEmptyScopes()
    {
        config.scopes = new string[0];
        
        // Should log warning but not throw exception
        config.Validate();
    }
    
    [Test]
    public void TestConfigFields()
    {
        Assert.AreEqual("test_client_id", config.clientId);
        Assert.AreEqual("test_client_secret", config.clientSecret);
        Assert.AreEqual("http://localhost:8000/auth/google/callback", config.redirectUri);
        Assert.AreEqual("http://localhost:8000", config.backendUrl);
        Assert.AreEqual("/auth/google", config.authEndpoint);
        Assert.AreEqual("/auth/google/callback", config.callbackEndpoint);
        Assert.AreEqual("/auth/verify", config.verifyEndpoint);
        Assert.AreEqual(3, config.scopes.Length);
        Assert.AreEqual("openid", config.scopes[0]);
        Assert.AreEqual("email", config.scopes[1]);
        Assert.AreEqual("profile", config.scopes[2]);
        Assert.IsFalse(config.autoSelect);
        Assert.IsFalse(config.cancelOnTapOutside);
        Assert.AreEqual("signup", config.context);
        Assert.IsTrue(config.itpSupport);
        Assert.IsTrue(config.useFedcmForPrompt);
        Assert.AreEqual("popup", config.uxMode);
    }
    
    [Test]
    public void TestConfigSerialization()
    {
        // Test that config can be serialized/deserialized
        string json = JsonUtility.ToJson(config);
        Assert.IsNotNull(json);
        Assert.IsTrue(json.Length > 0);
    }
}
