using UnityEngine;
using TMPro;

public class LoginPanelUI : MonoBehaviour
{
    [Header("UI References")]
    [SerializeField] private GameObject panelObject;
    [SerializeField] private TextMeshProUGUI userCodeText;
    [SerializeField] private TextMeshProUGUI instructionsText;
    [SerializeField] private GameObject loginButton;
    [SerializeField] private GameObject logoutButton;
    [SerializeField] private GameObject loadingSpinner; // Optional: if you add a spinner later

    void Start()
    {
        // Subscribe to AuthManager events to automatically update the UI
        AuthManager.OnLoginSuccess += HandleLoginSuccess;
        AuthManager.OnLogout += ShowLoggedOutState;

        // Set the initial state of the UI based on the AuthManager's state when we start
        // This handles the case where the user is already logged in from a previous session.
        if (AuthManager.Instance != null)
        {
            if (AuthManager.Instance.CurrentState == AuthManager.AuthState.LoggedIn)
            {
                HandleLoginSuccess();
            }
            else
            {
                ShowLoggedOutState();
            }
        }
        else
        {
            // Fallback if AuthManager isn't ready for some reason
            ShowLoggedOutState();
        }
    }

    private void OnDestroy()
    {
        // Unsubscribe to prevent memory leaks
        AuthManager.OnLoginSuccess -= HandleLoginSuccess;
        AuthManager.OnLogout -= ShowLoggedOutState;
    }

    /// <summary>
    /// Configures the UI for a logged-out user. Shows the login button.
    /// </summary>
    public void ShowLoggedOutState()
    {
        panelObject.SetActive(true); // Keep the panel visible
        instructionsText.text = "Please log in to continue.";
        userCodeText.text = ""; // Clear the code/welcome message

        loginButton.SetActive(true);
        logoutButton.SetActive(false);
    }

    /// <summary>
    /// Called after a successful login to show the welcome message and logout button.
    /// </summary>
    private void HandleLoginSuccess()
    {
        if (AuthManager.Instance?.CurrentUser != null)
        {
            ShowWelcomeMessage(AuthManager.Instance.CurrentUser.username);
        }
    }

    public void ShowLoginDetails(string userCode, string url)
    {
        panelObject.SetActive(true);
        userCodeText.text = userCode;
        instructionsText.text = $"Go to <color=#4da6ff>{url}</color>\nand enter the code above.";

        loginButton.SetActive(false);
        logoutButton.SetActive(false);
    }

    public void ShowWelcomeMessage(string username)
    {
        panelObject.SetActive(true);
        userCodeText.text = $"Welcome, {username}!";
        instructionsText.text = "You are successfully logged in.";

        loginButton.SetActive(false);
        logoutButton.SetActive(true);
    }

    public void HidePanel()
    {
        panelObject.SetActive(false);
    }
}
