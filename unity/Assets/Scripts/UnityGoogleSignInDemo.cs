using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class UnityGoogleSignInDemo : MonoBehaviour
{
    [Header("UI References")]
    public Button signInButton;
    public Button signOutButton;
    public TextMeshProUGUI statusText;
    public TextMeshProUGUI userInfoText;
    public Image userProfileImage;

    private GoogleSignInManager signInManager;

    private void Start()
    {
        signInManager = GoogleSignInManager.Instance;
        
        // Set up button listeners
        if (signInButton != null)
            signInButton.onClick.AddListener(OnSignInButtonClick);
        
        if (signOutButton != null)
            signOutButton.onClick.AddListener(OnSignOutButtonClick);

        // Subscribe to WebGL events
        GoogleSignInWebGL.OnAuthCodeReceived += OnAuthCodeReceived;
        GoogleSignInWebGL.OnAuthError += OnAuthError;

        UpdateUI();
    }

    private void OnDestroy()
    {
        // Unsubscribe from events
        GoogleSignInWebGL.OnAuthCodeReceived -= OnAuthCodeReceived;
        GoogleSignInWebGL.OnAuthError -= OnAuthError;
    }

    private void Update()
    {
        UpdateUI();
    }

    private void UpdateUI()
    {
        if (signInManager == null) return;

        bool isAuthenticated = signInManager.IsAuthenticated();

        // Update button visibility
        if (signInButton != null)
            signInButton.gameObject.SetActive(!isAuthenticated);
        
        if (signOutButton != null)
            signOutButton.gameObject.SetActive(isAuthenticated);

        // Update status text
        if (statusText != null)
        {
            if (isAuthenticated)
            {
                statusText.text = "User signed in successfully!";
                statusText.color = Color.green;
            }
            else
            {
                statusText.text = "User is not signed in";
                statusText.color = Color.white;
            }
        }

        // Update user info
        if (userInfoText != null)
        {
            if (isAuthenticated)
            {
                userInfoText.text = $"Name: {signInManager.userName}\nEmail: {signInManager.userEmail}";
            }
            else
            {
                userInfoText.text = "Not signed in";
            }
        }

        // Update profile image
        if (userProfileImage != null)
        {
            if (isAuthenticated && signInManager.userProfilePicture != null)
            {
                userProfileImage.sprite = Sprite.Create(
                    signInManager.userProfilePicture,
                    new Rect(0, 0, signInManager.userProfilePicture.width, signInManager.userProfilePicture.height),
                    new Vector2(0.5f, 0.5f)
                );
                userProfileImage.gameObject.SetActive(true);
            }
            else
            {
                userProfileImage.gameObject.SetActive(false);
            }
        }
    }

    public void OnSignInButtonClick()
    {
        Debug.Log("Sign In button clicked");
        if (signInManager != null)
        {
            signInManager.StartGoogleSignIn();
        }
    }

    public void OnSignOutButtonClick()
    {
        Debug.Log("Sign Out button clicked");
        if (signInManager != null)
        {
            signInManager.Logout();
        }
    }

    private void OnAuthCodeReceived(string authCode)
    {
        Debug.Log($"Demo received auth code: {authCode}");
        if (signInManager != null)
        {
            signInManager.HandleAuthCode(authCode);
        }
    }

    private void OnAuthError(string error)
    {
        Debug.LogError($"Demo received auth error: {error}");
        if (statusText != null)
        {
            statusText.text = $"Authentication error: {error}";
            statusText.color = Color.red;
        }
    }
}
