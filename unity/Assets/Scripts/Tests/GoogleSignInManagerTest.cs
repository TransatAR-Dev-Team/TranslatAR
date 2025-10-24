using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
using System.Collections;

namespace TranslatAR.Tests
{
    public class GoogleSignInManagerTest
    {
        private GoogleSignInManager manager;
        private GameObject testObject;

        [SetUp]
        public void Setup()
        {
            // Create test GameObject
            testObject = new GameObject("TestGoogleSignInManager");
            manager = testObject.AddComponent<GoogleSignInManager>();
            
            // Create test config
            var config = ScriptableObject.CreateInstance<GoogleSignInConfig>();
            config.clientId = "test_client_id";
            config.redirectUri = "http://localhost:8000/auth/google/callback";
            config.backendUrl = "http://localhost:8000";
            manager.config = config;
        }

        [TearDown]
        public void TearDown()
        {
            if (testObject != null)
            {
                Object.DestroyImmediate(testObject);
            }
        }

        [Test]
        public void TestSingletonInstance()
        {
            Assert.IsNotNull(GoogleSignInManager.Instance);
            Assert.AreEqual(manager, GoogleSignInManager.Instance);
        }

        [Test]
        public void TestInitialAuthenticationState()
        {
            Assert.IsFalse(manager.IsAuthenticated());
            Assert.IsEmpty(manager.GetCurrentUser());
            Assert.IsEmpty(manager.GetAuthToken());
        }

        [Test]
        public void TestSetAuthToken()
        {
            string testToken = "test_jwt_token_123";
            manager.SetAuthToken(testToken);
            
            Assert.IsTrue(manager.IsAuthenticated());
            Assert.AreEqual(testToken, manager.GetAuthToken());
        }

        [Test]
        public void TestSetUserInfo()
        {
            var testUser = new UserInfo
            {
                id = "123",
                email = "test@example.com",
                name = "Test User",
                picture = "https://example.com/picture.jpg"
            };
            
            manager.SetUserInfo(testUser);
            
            Assert.AreEqual(testUser.name, manager.userName);
            Assert.AreEqual(testUser.email, manager.userEmail);
            Assert.AreEqual(testUser.picture, manager.userPicture);
        }

        [Test]
        public void TestLogout()
        {
            // Set up authenticated state
            manager.SetAuthToken("test_token");
            manager.SetUserInfo(new UserInfo { name = "Test User", email = "test@example.com" });
            
            Assert.IsTrue(manager.IsAuthenticated());
            
            // Test logout
            manager.Logout();
            
            Assert.IsFalse(manager.IsAuthenticated());
            Assert.IsEmpty(manager.GetCurrentUser());
            Assert.IsEmpty(manager.GetAuthToken());
            Assert.IsEmpty(manager.userName);
            Assert.IsEmpty(manager.userEmail);
        }

        [Test]
        public void TestAuthenticationFlow()
        {
            // Test initial state
            Assert.IsFalse(manager.IsAuthenticated());
            
            // Test setting user info without token
            manager.SetUserInfo(new UserInfo { name = "Test User" });
            Assert.IsFalse(manager.IsAuthenticated());
            
            // Test setting token
            manager.SetAuthToken("test_token");
            Assert.IsTrue(manager.IsAuthenticated());
            
            // Test logout
            manager.Logout();
            Assert.IsFalse(manager.IsAuthenticated());
        }

        [Test]
        public void TestConfigValidation()
        {
            Assert.IsNotNull(manager.config);
            Assert.IsNotEmpty(manager.config.clientId);
            Assert.IsNotEmpty(manager.config.redirectUri);
            Assert.IsNotEmpty(manager.config.backendUrl);
        }

        [Test]
        public void TestConfigWithoutAssignment()
        {
            manager.config = null;
            
            // Should not throw errors when config is null
            Assert.DoesNotThrow(() => manager.StartGoogleSignIn());
        }
    }
}
