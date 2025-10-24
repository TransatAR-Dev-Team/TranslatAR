using NUnit.Framework;
using UnityEngine;

namespace TranslatAR.Tests
{
    public class GoogleSignInConfigTest
    {
        private GoogleSignInConfig config;

        [SetUp]
        public void Setup()
        {
            config = ScriptableObject.CreateInstance<GoogleSignInConfig>();
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
        public void TestDefaultValues()
        {
            Assert.IsNotEmpty(config.clientId);
            Assert.IsNotEmpty(config.redirectUri);
            Assert.IsNotEmpty(config.backendUrl);
            Assert.IsNotNull(config.scopes);
            Assert.IsTrue(config.scopes.Length > 0);
        }

        [Test]
        public void TestGetAuthUrl()
        {
            config.clientId = "test_client_id";
            config.redirectUri = "http://localhost:8000/auth/google/callback";
            config.backendUrl = "http://localhost:8000";
            config.scopes = new string[] { "openid", "email", "profile" };
            
            string authUrl = config.GetAuthUrl();
            
            Assert.IsNotEmpty(authUrl);
            Assert.IsTrue(authUrl.Contains("test_client_id"));
            Assert.IsTrue(authUrl.Contains("http://localhost:8000/auth/google/callback"));
            Assert.IsTrue(authUrl.Contains("openid"));
            Assert.IsTrue(authUrl.Contains("email"));
            Assert.IsTrue(authUrl.Contains("profile"));
        }

        [Test]
        public void TestGetCallbackUrl()
        {
            config.backendUrl = "http://localhost:8000";
            config.callbackEndpoint = "/auth/google/callback";
            
            string callbackUrl = config.GetCallbackUrl();
            
            Assert.AreEqual("http://localhost:8000/auth/google/callback", callbackUrl);
        }

        [Test]
        public void TestGetVerifyUrl()
        {
            config.backendUrl = "http://localhost:8000";
            config.verifyEndpoint = "/auth/verify";
            
            string token = "test_token";
            string verifyUrl = config.GetVerifyUrl(token);
            
            Assert.AreEqual("http://localhost:8000/auth/verify?token=test_token", verifyUrl);
        }

        [Test]
        public void TestGetOneTapEndpoint()
        {
            config.backendUrl = "http://localhost:8000";
            
            string oneTapEndpoint = config.GetOneTapEndpoint();
            
            Assert.AreEqual("http://localhost:8000/auth/google/one-tap", oneTapEndpoint);
        }

        [Test]
        public void TestGetScopeString()
        {
            config.scopes = new string[] { "openid", "email", "profile" };
            
            string scopeString = config.GetScopeString();
            
            Assert.AreEqual("openid email profile", scopeString);
        }

        [Test]
        public void TestIsValid()
        {
            // Test with valid config
            config.clientId = "test_client_id";
            config.redirectUri = "http://localhost:8000/auth/google/callback";
            config.backendUrl = "http://localhost:8000";
            
            Assert.IsTrue(config.IsValid());
            
            // Test with invalid config
            config.clientId = "";
            Assert.IsFalse(config.IsValid());
            
            config.clientId = "test_client_id";
            config.redirectUri = "";
            Assert.IsFalse(config.IsValid());
            
            config.redirectUri = "http://localhost:8000/auth/google/callback";
            config.backendUrl = "";
            Assert.IsFalse(config.IsValid());
        }

        [Test]
        public void TestGetWebGLInitScript()
        {
            config.clientId = "test_client_id";
            config.autoSelect = false;
            config.cancelOnTapOutside = false;
            config.context = "signup";
            config.itpSupport = true;
            config.useFedcmForPrompt = true;
            config.uxMode = "popup";
            
            string initScript = config.GetWebGLInitScript();
            
            Assert.IsNotEmpty(initScript);
            Assert.IsTrue(initScript.Contains("test_client_id"));
            Assert.IsTrue(initScript.Contains("false")); // autoSelect
            Assert.IsTrue(initScript.Contains("signup")); // context
            Assert.IsTrue(initScript.Contains("popup")); // uxMode
        }

        [Test]
        public void TestGetWebGLPromptScript()
        {
            string promptScript = config.GetWebGLPromptScript();
            
            Assert.IsNotEmpty(promptScript);
            Assert.IsTrue(promptScript.Contains("google.accounts.id.prompt"));
        }

        [Test]
        public void TestValidate()
        {
            // Test with empty client ID
            config.clientId = "";
            config.Validate(); // Should not throw, just log warning
            
            // Test with empty redirect URI
            config.clientId = "test_client_id";
            config.redirectUri = "";
            config.Validate(); // Should not throw, just log warning
            
            // Test with empty backend URL
            config.redirectUri = "http://localhost:8000/auth/google/callback";
            config.backendUrl = "";
            config.Validate(); // Should not throw, just log warning
            
            // Test with empty scopes
            config.backendUrl = "http://localhost:8000";
            config.scopes = new string[0];
            config.Validate(); // Should not throw, just log warning
        }
    }
}
