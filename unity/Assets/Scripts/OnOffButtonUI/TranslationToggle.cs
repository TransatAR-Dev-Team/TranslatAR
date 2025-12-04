using UnityEngine;
using UnityEngine.UI;

// toggles translation processing on/off
// when translation is off, new translation responses are ignored but subtitles still show
public class TranslationToggle : MonoBehaviour
{
    private bool isTranslationEnabled = true;
    private Toggle uiToggle;
    private bool isUpdatingToggle = false; // prevent recursive updates
    
    // key for saving translation enabled state
    private const string TRANSLATION_ENABLED_KEY = "TranslationEnabled";

    void Start()
    {
        // try to find the toggle component
        uiToggle = GetComponent<Toggle>();
        
        // connect to toggle if it exists
        if (uiToggle != null)
        {
            uiToggle.onValueChanged.AddListener(OnToggleValueChanged);
        }

        // get initial translation state (load saved state first, then sync with WebSocketManager)
        if (PlayerPrefs.HasKey(TRANSLATION_ENABLED_KEY))
        {
            isTranslationEnabled = PlayerPrefs.GetInt(TRANSLATION_ENABLED_KEY) == 1;
        }
        
        // apply saved state to WebSocketManager if it exists
        if (WebSocketManager.Instance != null)
        {
            // if we loaded a saved state, apply it to WebSocketManager
            if (PlayerPrefs.HasKey(TRANSLATION_ENABLED_KEY))
            {
                WebSocketManager.Instance.SetTranslationEnabled(isTranslationEnabled);
            }
            else
            {
                // otherwise use WebSocketManager's current state
                isTranslationEnabled = WebSocketManager.Instance.isTranslationEnabled;
            }
            UpdateToggleVisualState();
        }
        else
        {
            Debug.LogWarning("[TranslationToggle] WebSocketManager.Instance is null. Will retry in Update().");
        }
    }

    void Update()
    {
        // keep trying to find WebSocketManager if it's not ready yet
        if (WebSocketManager.Instance == null)
        {
            return;
        }

        // sync state if it changed from somewhere else
        if (WebSocketManager.Instance.isTranslationEnabled != isTranslationEnabled)
        {
            isTranslationEnabled = WebSocketManager.Instance.isTranslationEnabled;
            UpdateToggleVisualState();
        }
    }

    void OnDestroy()
    {
        // clean up to prevent memory leaks
        if (uiToggle != null)
        {
            uiToggle.onValueChanged.RemoveListener(OnToggleValueChanged);
        }
    }

    // called when the toggle value changes
    private void OnToggleValueChanged(bool isOn)
    {
        if (isUpdatingToggle) return; // prevent recursive updates

        if (WebSocketManager.Instance == null)
        {
            Debug.LogWarning("[TranslationToggle] Cannot toggle: WebSocketManager.Instance is null. Waiting for it to initialize...");
            // revert the toggle back to previous state
            isUpdatingToggle = true;
            if (uiToggle != null)
            {
                uiToggle.isOn = isTranslationEnabled;
            }
            isUpdatingToggle = false;
            return;
        }

        isTranslationEnabled = isOn;
        WebSocketManager.Instance.SetTranslationEnabled(isTranslationEnabled);
        
        // save the state so it persists when app restarts
        PlayerPrefs.SetInt(TRANSLATION_ENABLED_KEY, isTranslationEnabled ? 1 : 0);
        PlayerPrefs.Save();
    }

    // updates the toggle visual to match the actual state
    private void UpdateToggleVisualState()
    {
        if (uiToggle != null && !isUpdatingToggle)
        {
            isUpdatingToggle = true;
            uiToggle.isOn = isTranslationEnabled;
            isUpdatingToggle = false;
        }
    }

    // sets the translation state
    // pass true to enable, false to disable
    public void SetTranslationEnabled(bool enabled)
    {
        if (WebSocketManager.Instance == null)
        {
            Debug.LogWarning("[TranslationToggle] Cannot set translation state: WebSocketManager.Instance is null.");
            return;
        }

        isTranslationEnabled = enabled;
        WebSocketManager.Instance.SetTranslationEnabled(isTranslationEnabled);
        UpdateToggleVisualState();
        
        // save the state so it persists when app restarts
        PlayerPrefs.SetInt(TRANSLATION_ENABLED_KEY, isTranslationEnabled ? 1 : 0);
        PlayerPrefs.Save();
    }

    // gets the current translation state
    // returns true if enabled, false if disabled
    public bool IsTranslationEnabled()
    {
        if (WebSocketManager.Instance != null)
        {
            isTranslationEnabled = WebSocketManager.Instance.isTranslationEnabled;
        }
        return isTranslationEnabled;
    }
}


