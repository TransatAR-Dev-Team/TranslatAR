using UnityEngine;

// toggles translation processing on/off
// when translation is off, new translation responses are ignored but subtitle display remains visible
public class TranslationToggle : MonoBehaviour
{
    private bool isTranslationEnabled = true;

    void Start()
    {
        // initialize translation state from WebSocketManager
        if (WebSocketManager.Instance != null)
        {
            isTranslationEnabled = WebSocketManager.Instance.isTranslationEnabled;
            Debug.Log($"[TranslationToggle] Translation state initialized. Initial state: {(isTranslationEnabled ? "Enabled" : "Disabled")}");
        }
        else
        {
            Debug.LogWarning("[TranslationToggle] WebSocketManager.Instance is null. Will retry in Update().");
        }
    }

    void Update()
    {
        // retry finding WebSocketManager if not found yet
        if (WebSocketManager.Instance == null)
        {
            return;
        }

        // sync state if it changed externally
        if (WebSocketManager.Instance.isTranslationEnabled != isTranslationEnabled)
        {
            isTranslationEnabled = WebSocketManager.Instance.isTranslationEnabled;
        }
    }

    // toggles translation processing on/off
    // when translation is off, new translation responses are ignored but subtitle display remains visible
    // call this method from a UI button's onClick event
    public void ToggleTranslation()
    {
        if (WebSocketManager.Instance == null)
        {
            Debug.LogWarning("[TranslationToggle] Cannot toggle: WebSocketManager.Instance is null. Waiting for it to initialize...");
            return;
        }

        isTranslationEnabled = !isTranslationEnabled;
        WebSocketManager.Instance.SetTranslationEnabled(isTranslationEnabled);
    }

    // sets the translation state explicitly
    // true to enable translation, false to disable it
    public void SetTranslationEnabled(bool enabled)
    {
        if (WebSocketManager.Instance == null)
        {
            Debug.LogWarning("[TranslationToggle] Cannot set translation state: WebSocketManager.Instance is null.");
            return;
        }

        isTranslationEnabled = enabled;
        WebSocketManager.Instance.SetTranslationEnabled(isTranslationEnabled);
    }

    // gets the current translation state
    // returns true if translation is enabled, false otherwise
    public bool IsTranslationEnabled()
    {
        if (WebSocketManager.Instance != null)
        {
            isTranslationEnabled = WebSocketManager.Instance.isTranslationEnabled;
        }
        return isTranslationEnabled;
    }
}

