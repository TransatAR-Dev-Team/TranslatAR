using NUnit.Framework;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

namespace TranslatAR.Tests
{
    public class GoogleSignInUITest
    {
        private GoogleSignInUI uiController;
        private GoogleSignInManager manager;
        private GameObject testObject;
        private Button signInButton;
        private Button signOutButton;
        private TextMeshProUGUI statusText;
        private TextMeshProUGUI userInfoText;
        private Image userProfileImage;
        private GameObject loginPanel;
        private GameObject userPanel;

        [SetUp]
        public void Setup()
        {
            // Create test GameObject
            testObject = new GameObject("TestGoogleSignInUI");
            uiController = testObject.AddComponent<GoogleSignInUI>();
            manager = testObject.AddComponent<GoogleSignInManager>();
            
            // Create UI elements
            var canvasObject = new GameObject("Canvas");
            var canvas = canvasObject.AddComponent<Canvas>();
            
            // Create panels
            loginPanel = new GameObject("LoginPanel");
            loginPanel.transform.SetParent(canvasObject.transform);
            
            userPanel = new GameObject("UserPanel");
            userPanel.transform.SetParent(canvasObject.transform);
            
            // Create buttons
            var signInButtonObject = new GameObject("SignInButton");
            signInButtonObject.transform.SetParent(loginPanel.transform);
            signInButton = signInButtonObject.AddComponent<Button>();
            
            var signOutButtonObject = new GameObject("SignOutButton");
            signOutButtonObject.transform.SetParent(userPanel.transform);
            signOutButton = signOutButtonObject.AddComponent<Button>();
            
            // Create text elements
            var statusTextObject = new GameObject("StatusText");
            statusTextObject.transform.SetParent(canvasObject.transform);
            statusText = statusTextObject.AddComponent<TextMeshProUGUI>();
            
            var userInfoTextObject = new GameObject("UserInfoText");
            userInfoTextObject.transform.SetParent(userPanel.transform);
            userInfoText = userInfoTextObject.AddComponent<TextMeshProUGUI>();
            
            // Create image
            var userProfileImageObject = new GameObject("UserProfileImage");
            userProfileImageObject.transform.SetParent(userPanel.transform);
            userProfileImage = userProfileImageObject.AddComponent<Image>();
            
            // Assign references
            uiController.signInButton = signInButton;
            uiController.signOutButton = signOutButton;
            uiController.statusText = statusText;
            uiController.userInfoText = userInfoText;
            uiController.userProfileImage = userProfileImage;
            uiController.loginPanel = loginPanel;
            uiController.userPanel = userPanel;
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
        public void TestUIInitialization()
        {
            Assert.IsNotNull(uiController.signInButton);
            Assert.IsNotNull(uiController.signOutButton);
            Assert.IsNotNull(uiController.statusText);
            Assert.IsNotNull(uiController.userInfoText);
            Assert.IsNotNull(uiController.userProfileImage);
            Assert.IsNotNull(uiController.loginPanel);
            Assert.IsNotNull(uiController.userPanel);
        }

        [Test]
        public void TestUpdateUIWhenNotAuthenticated()
        {
            // Ensure user is not authenticated
            manager.Logout();
            
            uiController.UpdateUI();
            
            // Login panel should be active, user panel should be inactive
            Assert.IsTrue(loginPanel.activeInHierarchy);
            Assert.IsFalse(userPanel.activeInHierarchy);
            Assert.IsTrue(signInButton.gameObject.activeInHierarchy);
            Assert.IsFalse(signOutButton.gameObject.activeInHierarchy);
        }

        [Test]
        public void TestUpdateUIWhenAuthenticated()
        {
            // Set up authenticated state
            manager.SetAuthToken("test_token");
            manager.SetUserInfo(new UserInfo 
            { 
                name = "Test User", 
                email = "test@example.com",
                picture = "https://example.com/picture.jpg"
            });
            
            uiController.UpdateUI();
            
            // User panel should be active, login panel should be inactive
            Assert.IsFalse(loginPanel.activeInHierarchy);
            Assert.IsTrue(userPanel.activeInHierarchy);
            Assert.IsFalse(signInButton.gameObject.activeInHierarchy);
            Assert.IsTrue(signOutButton.gameObject.activeInHierarchy);
        }

        [Test]
        public void TestOnSignInButtonClick()
        {
            // Test that clicking sign-in button doesn't throw errors
            Assert.DoesNotThrow(() => uiController.OnSignInButtonClick());
        }

        [Test]
        public void TestOnSignOutButtonClick()
        {
            // Set up authenticated state
            manager.SetAuthToken("test_token");
            manager.SetUserInfo(new UserInfo { name = "Test User" });
            
            // Test sign out
            uiController.OnSignOutButtonClick();
            
            // User should be logged out
            Assert.IsFalse(manager.IsAuthenticated());
        }

        [Test]
        public void TestLoadProfileImage()
        {
            string imageUrl = "https://example.com/test-image.jpg";
            
            // Test that loading profile image doesn't throw errors
            Assert.DoesNotThrow(() => uiController.LoadProfileImage(imageUrl));
        }

        [Test]
        public void TestUIUpdateWithNullManager()
        {
            // Test UI update when manager is null
            uiController = new GameObject("TestGoogleSignInUI").AddComponent<GoogleSignInUI>();
            
            // Should not throw errors
            Assert.DoesNotThrow(() => uiController.UpdateUI());
        }

        [Test]
        public void TestUIUpdateWithNullPanels()
        {
            // Test UI update when panels are null
            uiController.loginPanel = null;
            uiController.userPanel = null;
            
            // Should not throw errors
            Assert.DoesNotThrow(() => uiController.UpdateUI());
        }

        [Test]
        public void TestUIUpdateWithNullButtons()
        {
            // Test UI update when buttons are null
            uiController.signInButton = null;
            uiController.signOutButton = null;
            
            // Should not throw errors
            Assert.DoesNotThrow(() => uiController.UpdateUI());
        }
    }
}
