using UnityEngine;
using UnityEngine.TestTools;
using NUnit.Framework;
using System.Collections;

namespace TranslatAR.Tests
{
    public class TestRunner : MonoBehaviour
    {
        [UnityTest]
        public IEnumerator RunAllTests()
        {
            Debug.Log("Starting Unity Google Sign-In Tests...");
            
            // Run GoogleSignInManager tests
            yield return RunGoogleSignInManagerTests();
            
            // Run GoogleSignInConfig tests
            yield return RunGoogleSignInConfigTests();
            
            // Run GoogleSignInUI tests
            yield return RunGoogleSignInUITests();
            
            Debug.Log("All Unity Google Sign-In Tests completed!");
        }
        
        private IEnumerator RunGoogleSignInManagerTests()
        {
            Debug.Log("Running GoogleSignInManager tests...");
            
            // Test singleton instance
            var manager = GoogleSignInManager.Instance;
            Assert.IsNotNull(manager, "GoogleSignInManager singleton should exist");
            
            // Test initial state
            Assert.IsFalse(manager.IsAuthenticated(), "Should not be authenticated initially");
            Assert.IsEmpty(manager.GetCurrentUser(), "Current user should be empty initially");
            Assert.IsEmpty(manager.GetAuthToken(), "Auth token should be empty initially");
            
            // Test token setting
            string testToken = "test_jwt_token_123";
            manager.SetAuthToken(testToken);
            Assert.IsTrue(manager.IsAuthenticated(), "Should be authenticated after setting token");
            Assert.AreEqual(testToken, manager.GetAuthToken(), "Auth token should match");
            
            // Test user info setting
            var testUser = new UserInfo
            {
                id = "123",
                email = "test@example.com",
                name = "Test User",
                picture = "https://example.com/picture.jpg"
            };
            manager.SetUserInfo(testUser);
            Assert.AreEqual(testUser.name, manager.userName, "User name should match");
            Assert.AreEqual(testUser.email, manager.userEmail, "User email should match");
            
            // Test logout
            manager.Logout();
            Assert.IsFalse(manager.IsAuthenticated(), "Should not be authenticated after logout");
            
            Debug.Log("GoogleSignInManager tests passed!");
            yield return null;
        }
        
        private IEnumerator RunGoogleSignInConfigTests()
        {
            Debug.Log("Running GoogleSignInConfig tests...");
            
            var config = ScriptableObject.CreateInstance<GoogleSignInConfig>();
            
            // Test default values
            Assert.IsNotEmpty(config.clientId, "Client ID should not be empty");
            Assert.IsNotEmpty(config.redirectUri, "Redirect URI should not be empty");
            Assert.IsNotEmpty(config.backendUrl, "Backend URL should not be empty");
            Assert.IsNotNull(config.scopes, "Scopes should not be null");
            Assert.IsTrue(config.scopes.Length > 0, "Scopes should have at least one item");
            
            // Test URL generation
            string authUrl = config.GetAuthUrl();
            Assert.IsNotEmpty(authUrl, "Auth URL should not be empty");
            Assert.IsTrue(authUrl.Contains(config.clientId), "Auth URL should contain client ID");
            
            string callbackUrl = config.GetCallbackUrl();
            Assert.IsNotEmpty(callbackUrl, "Callback URL should not be empty");
            
            string verifyUrl = config.GetVerifyUrl("test_token");
            Assert.IsNotEmpty(verifyUrl, "Verify URL should not be empty");
            Assert.IsTrue(verifyUrl.Contains("test_token"), "Verify URL should contain token");
            
            // Test validation
            Assert.IsTrue(config.IsValid(), "Config should be valid with default values");
            
            // Test with invalid values
            config.clientId = "";
            Assert.IsFalse(config.IsValid(), "Config should be invalid with empty client ID");
            
            Object.DestroyImmediate(config);
            
            Debug.Log("GoogleSignInConfig tests passed!");
            yield return null;
        }
        
        private IEnumerator RunGoogleSignInUITests()
        {
            Debug.Log("Running GoogleSignInUI tests...");
            
            // Create test UI controller
            var uiObject = new GameObject("TestGoogleSignInUI");
            var uiController = uiObject.AddComponent<GoogleSignInUI>();
            
            // Test that UI controller can be created
            Assert.IsNotNull(uiController, "GoogleSignInUI should be created successfully");
            
            // Test button click methods don't throw errors
            Assert.DoesNotThrow(() => uiController.OnSignInButtonClick(), "Sign-in button click should not throw");
            Assert.DoesNotThrow(() => uiController.OnSignOutButtonClick(), "Sign-out button click should not throw");
            
            // Test UI update doesn't throw errors
            Assert.DoesNotThrow(() => uiController.UpdateUI(), "UpdateUI should not throw");
            
            // Test profile image loading doesn't throw errors
            Assert.DoesNotThrow(() => uiController.LoadProfileImage("https://example.com/test.jpg"), 
                "LoadProfileImage should not throw");
            
            Object.DestroyImmediate(uiObject);
            
            Debug.Log("GoogleSignInUI tests passed!");
            yield return null;
        }
    }
}
