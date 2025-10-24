using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Networking;
using TMPro;

/// <summary>
/// Manages the Google Sign-In UI elements and user interactions.
/// Provides a clean interface for authentication status and user profile display.
/// </summary>
public class GoogleSignInUI : MonoBehaviour
{
    [Header("UI Panels")]
    [SerializeField] private GameObject loginPanel;
    [SerializeField] private GameObject userPanel;
    
    [Header("Login Panel Elements")]
    [SerializeField] private Button googleSignInButton;
    [SerializeField] private TextMeshProUGUI loginTitleText;
    [SerializeField] private TextMeshProUGUI loginSubtitleText;
    
    [Header("User Panel Elements")]
    [SerializeField] private Image userProfileImage;
    [SerializeField] private TextMeshProUGUI userNameText;
    [SerializeField] private TextMeshProUGUI userEmailText;
    [SerializeField] private Button signOutButton;
    [SerializeField] private Button settingsButton;
    
    [Header("Status Elements")]
    [SerializeField] private TextMeshProUGUI statusText;
    [SerializeField] private GameObject loadingIndicator;
    
    [Header("Styling")]
    [SerializeField] private Color googleBlue = new Color(0.26f, 0.52f, 0.96f);
    [SerializeField] private Color googleRed = new Color(0.86f, 0.26f, 0.21f);
    [SerializeField] private Color googleGreen = new Color(0.2f, 0.66f, 0.33f);
    [SerializeField] private Color googleYellow = new Color(0.98f, 0.74f, 0.02f);
    
    private GoogleSignInManager signInManager;
    
    void Start()
    {
        InitializeUI();
        SubscribeToEvents();
    }
    
    void OnDestroy()
    {
        UnsubscribeFromEvents();
    }
    
    /// <summary>
    /// Initializes UI elements and sets up button listeners
    /// </summary>
    void InitializeUI()
    {
        signInManager = GoogleSignInManager.Instance;
        
        // Setup button listeners
        if (googleSignInButton != null)
        {
            googleSignInButton.onClick.AddListener(OnSignInClicked);
            SetupGoogleButtonStyle(googleSignInButton);
        }
        
        if (signOutButton != null)
        {
            signOutButton.onClick.AddListener(OnSignOutClicked);
            SetupSignOutButtonStyle(signOutButton);
        }
        
        if (settingsButton != null)
        {
            settingsButton.onClick.AddListener(OnSettingsClicked);
        }
        
        // Initialize text content
        if (loginTitleText != null)
            loginTitleText.text = "Sign in to TranslatAR";
            
        if (loginSubtitleText != null)
            loginSubtitleText.text = "Connect with your Google account to access personalized features";
        
        // Hide loading indicator initially
        if (loadingIndicator != null)
            loadingIndicator.SetActive(false);
            
        // Update UI based on current auth state
        UpdateUI();
    }
    
    /// <summary>
    /// Subscribes to Google Sign-In events
    /// </summary>
    void SubscribeToEvents()
    {
        GoogleSignInManager.OnUserSignedIn += OnUserSignedIn;
        GoogleSignInManager.OnUserSignedOut += OnUserSignedOut;
    }
    
    /// <summary>
    /// Unsubscribes from Google Sign-In events
    /// </summary>
    void UnsubscribeFromEvents()
    {
        GoogleSignInManager.OnUserSignedIn -= OnUserSignedIn;
        GoogleSignInManager.OnUserSignedOut -= OnUserSignedOut;
    }
    
    /// <summary>
    /// Handles sign-in button click
    /// </summary>
    void OnSignInClicked()
    {
        if (signInManager != null)
        {
            ShowStatus("Signing in...", true);
            signInManager.StartGoogleSignIn();
        }
    }
    
    /// <summary>
    /// Handles sign-out button click
    /// </summary>
    void OnSignOutClicked()
    {
        if (signInManager != null)
        {
            signInManager.SignOut();
        }
    }
    
    /// <summary>
    /// Handles settings button click
    /// </summary>
    void OnSettingsClicked()
    {
        // TODO: Implement settings functionality
        Debug.Log("Settings clicked");
    }
    
    /// <summary>
    /// Handles user signed in event
    /// </summary>
    void OnUserSignedIn(UserProfile user)
    {
        UpdateUserProfile(user);
        ShowStatus("Welcome back!", false);
    }
    
    /// <summary>
    /// Handles user signed out event
    /// </summary>
    void OnUserSignedOut()
    {
        UpdateUI();
        ShowStatus("Signed out successfully", false);
    }
    
    /// <summary>
    /// Updates the entire UI based on authentication state
    /// </summary>
    void UpdateUI()
    {
        bool isAuthenticated = signInManager != null && signInManager.IsAuthenticated();
        
        // Show/hide panels
        if (loginPanel != null)
            loginPanel.SetActive(!isAuthenticated);
            
        if (userPanel != null)
            userPanel.SetActive(isAuthenticated);
        
        // Update user profile if authenticated
        if (isAuthenticated && signInManager != null)
        {
            var user = signInManager.GetCurrentUser();
            if (user != null)
            {
                UpdateUserProfile(user);
            }
        }
    }
    
    /// <summary>
    /// Updates user profile display
    /// </summary>
    void UpdateUserProfile(UserProfile user)
    {
        if (userNameText != null)
            userNameText.text = user.name;
            
        if (userEmailText != null)
            userEmailText.text = user.email;
            
        // Load profile image if available
        if (userProfileImage != null && !string.IsNullOrEmpty(user.picture))
        {
            StartCoroutine(LoadProfileImage(user.picture));
        }
    }
    
    /// <summary>
    /// Loads user profile image from URL
    /// </summary>
    System.Collections.IEnumerator LoadProfileImage(string imageUrl)
    {
        using (var request = UnityWebRequest.Get(imageUrl))
        {
            request.downloadHandler = new DownloadHandlerTexture();
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                var texture = ((DownloadHandlerTexture)request.downloadHandler).texture;
                var sprite = Sprite.Create(texture, new Rect(0, 0, texture.width, texture.height), new Vector2(0.5f, 0.5f));
                userProfileImage.sprite = sprite;
            }
        }
    }
    
    /// <summary>
    /// Shows status message to user
    /// </summary>
    void ShowStatus(string message, bool showLoading = false)
    {
        if (statusText != null)
        {
            statusText.text = message;
            statusText.gameObject.SetActive(true);
        }
        
        if (loadingIndicator != null)
            loadingIndicator.SetActive(showLoading);
            
        // Auto-hide status after 3 seconds
        if (!showLoading)
        {
            Invoke(nameof(HideStatus), 3f);
        }
    }
    
    /// <summary>
    /// Hides status message
    /// </summary>
    void HideStatus()
    {
        if (statusText != null)
            statusText.gameObject.SetActive(false);
            
        if (loadingIndicator != null)
            loadingIndicator.SetActive(false);
    }
    
    /// <summary>
    /// Sets up Google button styling
    /// </summary>
    void SetupGoogleButtonStyle(Button button)
    {
        if (button == null) return;
        
        // Set button colors to Google blue
        var colors = button.colors;
        colors.normalColor = googleBlue;
        colors.highlightedColor = new Color(googleBlue.r * 0.9f, googleBlue.g * 0.9f, googleBlue.b * 0.9f);
        colors.pressedColor = new Color(googleBlue.r * 0.8f, googleBlue.g * 0.8f, googleBlue.b * 0.8f);
        button.colors = colors;
        
        // Add Google logo or text
        var buttonText = button.GetComponentInChildren<TextMeshProUGUI>();
        if (buttonText != null)
        {
            buttonText.text = "Sign in with Google";
            buttonText.color = Color.white;
        }
    }
    
    /// <summary>
    /// Sets up sign-out button styling
    /// </summary>
    void SetupSignOutButtonStyle(Button button)
    {
        if (button == null) return;
        
        // Set button colors to Google red
        var colors = button.colors;
        colors.normalColor = googleRed;
        colors.highlightedColor = new Color(googleRed.r * 0.9f, googleRed.g * 0.9f, googleRed.b * 0.9f);
        colors.pressedColor = new Color(googleRed.r * 0.8f, googleRed.g * 0.8f, googleRed.b * 0.8f);
        button.colors = colors;
        
        // Set button text
        var buttonText = button.GetComponentInChildren<TextMeshProUGUI>();
        if (buttonText != null)
        {
            buttonText.text = "Sign Out";
            buttonText.color = Color.white;
        }
    }
}
