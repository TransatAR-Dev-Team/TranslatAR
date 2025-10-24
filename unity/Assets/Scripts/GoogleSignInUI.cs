using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Networking;
using TMPro;

public class GoogleSignInUI : MonoBehaviour
{
    [Header("UI References")]
    public Button signInButton;
    public Button signOutButton;
    public TextMeshProUGUI statusText;
    public TextMeshProUGUI userInfoText;
    public Image userProfileImage;
    
    [Header("UI Panels")]
    public GameObject loginPanel;
    public GameObject userPanel;
    
    private GoogleSignInManager authManager;
    
    void Start()
    {
        authManager = GoogleSignInManager.Instance;
        if (authManager == null)
        {
            Debug.LogError("GoogleSignInManager not found! Make sure it's in the scene.");
            return;
        }
        
        SetupUI();
        UpdateUI();
    }
    
    void SetupUI()
    {
        if (signInButton != null)
        {
            signInButton.onClick.AddListener(OnSignInButtonClick);
        }
        
        if (signOutButton != null)
        {
            signOutButton.onClick.AddListener(OnSignOutButtonClick);
        }
    }
    
    public void OnSignInButtonClick()
    {
        Debug.Log("Sign-in button clicked");
        if (authManager != null)
        {
            authManager.StartGoogleSignIn();
            UpdateStatusText("Starting Google Sign-In process...");
        }
    }
    
    public void OnSignOutButtonClick()
    {
        Debug.Log("Sign-out button clicked");
        if (authManager != null)
        {
            authManager.Logout();
            UpdateUI();
        }
    }
    
    public void UpdateUI()
    {
        if (authManager == null) return;
        
        bool isAuthenticated = authManager.IsAuthenticated();
        
        // Update panel visibility
        if (loginPanel != null)
        {
            loginPanel.SetActive(!isAuthenticated);
        }
        
        if (userPanel != null)
        {
            userPanel.SetActive(isAuthenticated);
        }
        
        // Update button states
        if (signInButton != null)
        {
            signInButton.gameObject.SetActive(!isAuthenticated);
        }
        
        if (signOutButton != null)
        {
            signOutButton.gameObject.SetActive(isAuthenticated);
        }
        
        // Update user info
        if (isAuthenticated)
        {
            UpdateUserInfo();
            UpdateStatusText("User signed in successfully!");
        }
        else
        {
            UpdateStatusText("User is not signed in");
        }
    }
    
    private void UpdateUserInfo()
    {
        if (userInfoText != null)
        {
            string userInfo = $"Name: {authManager.userName}\nEmail: {authManager.userEmail}";
            userInfoText.text = userInfo;
        }
        
        // Load profile picture if available
        if (!string.IsNullOrEmpty(authManager.userPicture))
        {
            authManager.LoadUserProfilePicture();
        }
    }
    
    private void UpdateStatusText(string message)
    {
        if (statusText != null)
        {
            statusText.text = message;
        }
        Debug.Log($"Status: {message}");
    }
    
    void Update()
    {
        // Update UI periodically to reflect authentication state changes
        if (authManager != null)
        {
            bool isAuthenticated = authManager.IsAuthenticated();
            
            // Check if UI state matches authentication state
            bool loginPanelActive = loginPanel != null && loginPanel.activeInHierarchy;
            bool userPanelActive = userPanel != null && userPanel.activeInHierarchy;
            
            if (isAuthenticated && !userPanelActive)
            {
                UpdateUI();
            }
            else if (!isAuthenticated && !loginPanelActive)
            {
                UpdateUI();
            }
        }
    }
    
    public void LoadProfileImage(string imageUrl)
    {
        if (userProfileImage != null)
        {
            StartCoroutine(LoadImageCoroutine(imageUrl));
        }
    }
    
    private IEnumerator LoadImageCoroutine(string imageUrl)
    {
        using (UnityWebRequest request = UnityWebRequest.Get(imageUrl))
        {
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                Texture2D texture = DownloadHandlerTexture.GetContent(request);
                if (texture != null)
                {
                    Sprite sprite = Sprite.Create(texture, new Rect(0, 0, texture.width, texture.height), new Vector2(0.5f, 0.5f));
                    userProfileImage.sprite = sprite;
                    Debug.Log("Profile image loaded successfully");
                }
            }
            else
            {
                Debug.LogError($"Failed to load profile image: {request.error}");
            }
        }
    }
}
