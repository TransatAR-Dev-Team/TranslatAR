using UnityEngine;
using TMPro;

public class LoginPanelUI : MonoBehaviour
{
    [Header("UI References")]
    [SerializeField] private GameObject panelObject;
    [SerializeField] private TextMeshProUGUI userCodeText;
    [SerializeField] private TextMeshProUGUI instructionsText;
    [SerializeField] private GameObject loginButton; // Assign your LoginButton in the inspector
    [SerializeField] private GameObject loadingSpinner; // Optional: if you add a spinner later

    void Start()
    {
        // Hide the panel initially
        // panelObject.SetActive(false);

        // Subscribe to AuthManager events
        if (AuthManager.Instance != null)
        {
            // We need to modify AuthManager slightly to expose the start event,
            // or just poll state in Update, but events are cleaner.
            // For now, let's just rely on the public methods we'll call from AuthManager.
        }
    }

    public void ShowLoginDetails(string userCode, string url)
    {
        panelObject.SetActive(true);
        userCodeText.text = userCode;
        instructionsText.text = $"Go to <color=#4da6ff>{url}</color>\nand enter the code above.";

        // Hide the login button while showing the code
        if(loginButton != null) loginButton.SetActive(false);
    }

    public void ShowWelcomeMessage(string username)
    {
        panelObject.SetActive(true); // Ensure panel is visible
        userCodeText.text = $"Welcome, {username}!";
        instructionsText.text = "You are successfully logged in.";

        if(loginButton != null) loginButton.SetActive(false);
    }

    public void HidePanel()
    {
        panelObject.SetActive(false);
    }
}
