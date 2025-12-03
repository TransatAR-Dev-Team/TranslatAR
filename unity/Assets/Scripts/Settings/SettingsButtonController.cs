using UnityEngine;
using UnityEngine.UI;


//Handles the settings button click to toggle the settings menu.

public class SettingsButtonController : MonoBehaviour
{
    [Header("Settings Menu Manager")]
    [Tooltip("Reference to the SettingsMenuUI component that manages the settings menu visibility")]
    [SerializeField] private SettingsMenuUI settingsMenuUI;

    [Header("Button Reference (Optional)")]
    [Tooltip("The button component. If not assigned, will try to find it on this GameObject")]
    [SerializeField] private Button settingsButton;

    void Start()
    {
        // Try to find SettingsMenuUI if not assigned
        if (settingsMenuUI == null)
        {
            settingsMenuUI = FindObjectOfType<SettingsMenuUI>();
            if (settingsMenuUI == null)
            {
                Debug.LogWarning("[SettingsButtonController] SettingsMenuUI not found. Please assign it in the Inspector.");
            }
        }

        // Try to find Button component if not assigned
        if (settingsButton == null)
        {
            settingsButton = GetComponent<Button>();
        }

        // Wire up the button click event
        if (settingsButton != null)
        {
            settingsButton.onClick.AddListener(OnSettingsButtonClicked);
        }
        else
        {
            Debug.LogWarning("[SettingsButtonController] No Button component found. Please attach this script to a Button GameObject.");
        }
    }

   
    // Called when the settings button is clicked.
  
    
    public void OnSettingsButtonClicked()
    {
        if (settingsMenuUI != null)
        {
            settingsMenuUI.ToggleMenu();
        }
        else
        {
            Debug.LogWarning("[SettingsButtonController] Cannot toggle menu: SettingsMenuUI not assigned.");
        }
    }

    void OnDestroy()
    {
        // Clean up event listener
        if (settingsButton != null)
        {
            settingsButton.onClick.RemoveListener(OnSettingsButtonClicked);
        }
    }
}


