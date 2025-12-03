using UnityEngine;

// Manages the visibility of the settings menu.
// The menu can be shown/hidden via public methods, typically called by a settings button.

public class SettingsMenuUI : MonoBehaviour
{
    [Header("Settings Menu Reference")]
    [Tooltip("The GameObject containing the settings menu Canvas/UI elements")]
    [SerializeField] private GameObject settingsMenu;

    [Header("Initial State")]
    [Tooltip("Whether the settings menu should be visible when the scene starts")]
    [SerializeField] private bool startVisible = false;

    private bool isVisible;

    void Start()
    {
        if (settingsMenu == null)
        {
            Debug.LogWarning("[SettingsMenuUI] Settings menu GameObject not assigned.");
            return;
        }

        // Set initial visibility state
        isVisible = startVisible;
        settingsMenu.SetActive(isVisible);
    }

   
    //Toggles the visibility of the settings menu.
    
    public void ToggleMenu()
    {
        if (settingsMenu == null) return;

        isVisible = !isVisible;
        settingsMenu.SetActive(isVisible);
        Debug.Log(isVisible ? "[SettingsMenuUI] Settings menu opened" : "[SettingsMenuUI] Settings menu closed");
    }

   
    //Shows the settings menu.
   
    public void ShowMenu()
    {
        if (settingsMenu == null) return;

        isVisible = true;
        settingsMenu.SetActive(true);
        Debug.Log("[SettingsMenuUI] Settings menu opened");
    }

   
    // Hides  settings menu.
    
    public void HideMenu()
    {
        if (settingsMenu == null) return;

        isVisible = false;
        settingsMenu.SetActive(false);
        Debug.Log("[SettingsMenuUI] Settings menu closed");
    }

   
    // Returns whether the settings menu is currently visible.
  
    public bool IsMenuVisible => isVisible;
}


