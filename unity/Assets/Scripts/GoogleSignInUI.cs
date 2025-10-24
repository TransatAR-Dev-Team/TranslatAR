using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class GoogleSignInUI : MonoBehaviour
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
        UpdateUI();
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
        if (signInManager != null)
        {
            signInManager.StartGoogleSignIn();
        }
    }

    public void OnSignOutButtonClick()
    {
        if (signInManager != null)
        {
            signInManager.Logout();
        }
    }
}
