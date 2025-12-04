using UnityEngine;
using UnityEngine.UI;

// toggles subtitle visibility on/off
public class SubtitleToggle : MonoBehaviour
{
    [Header("Subtitle UI Reference")]
    [Tooltip("Subtitle panel GameObject. Auto-finds if not assigned")]
    [SerializeField] private GameObject subtitlePanel;

    private bool isSubtitleVisible = true;
    private Toggle uiToggle;
    private bool isUpdatingToggle = false; // prevent recursive updates
    
    // key for saving subtitle visibility state
    private const string SUBTITLE_VISIBILITY_KEY = "SubtitleVisibility";

    void Start()
    {
        // try to find the toggle component
        uiToggle = GetComponent<Toggle>();
        
        // connect to toggle if it exists
        if (uiToggle != null)
        {
            uiToggle.onValueChanged.AddListener(OnToggleValueChanged);
        }

        // try to find subtitle panel if not assigned
        if (subtitlePanel == null)
        {
            FindSubtitlePanel();
        }

        if (subtitlePanel != null)
        {
            // load saved state if it exists, otherwise use current panel state
            if (PlayerPrefs.HasKey(SUBTITLE_VISIBILITY_KEY))
            {
                isSubtitleVisible = PlayerPrefs.GetInt(SUBTITLE_VISIBILITY_KEY) == 1;
            }
            else
            {
                isSubtitleVisible = subtitlePanel.activeSelf;
            }
            
            // apply the state (saved or current)
            subtitlePanel.SetActive(isSubtitleVisible);
            UpdateToggleVisualState();
            Debug.Log($"[SubtitleToggle] Subtitle panel found. Initial state: {(isSubtitleVisible ? "Visible" : "Hidden")}");
        }
        else
        {
            Debug.LogWarning("[SubtitleToggle] Subtitle panel not found. Will retry in Update().");
        }
    }

    void Update()
    {
        // keep trying to find subtitle panel if not found yet
        if (subtitlePanel == null)
        {
            FindSubtitlePanel();
            if (subtitlePanel != null)
            {
                isSubtitleVisible = subtitlePanel.activeSelf;
                UpdateToggleVisualState();
                Debug.Log($"[SubtitleToggle] Subtitle panel found in Update. Initial state: {(isSubtitleVisible ? "Visible" : "Hidden")}");
            }
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

        if (subtitlePanel == null)
        {
            Debug.LogWarning("[SubtitleToggle] Cannot toggle: subtitle panel not assigned. Trying to find it...");
            FindSubtitlePanel();
            
            if (subtitlePanel == null)
            {
                Debug.LogError("[SubtitleToggle] Cannot toggle: subtitle panel not found.");
                // revert the toggle back to previous state
                isUpdatingToggle = true;
                if (uiToggle != null)
                {
                    uiToggle.isOn = isSubtitleVisible;
                }
                isUpdatingToggle = false;
                return;
            }
        }

        isSubtitleVisible = isOn;
        subtitlePanel.SetActive(isSubtitleVisible);
        
        // save the state so it persists when app restarts
        PlayerPrefs.SetInt(SUBTITLE_VISIBILITY_KEY, isSubtitleVisible ? 1 : 0);
        PlayerPrefs.Save();
    }

    // updates the toggle visual to match the actual state
    private void UpdateToggleVisualState()
    {
        if (uiToggle != null && !isUpdatingToggle)
        {
            isUpdatingToggle = true;
            uiToggle.isOn = isSubtitleVisible;
            isUpdatingToggle = false;
        }
    }

    // tries to find the subtitle panel through WebSocketManager
    private void FindSubtitlePanel()
    {
        if (WebSocketManager.Instance == null)
        {
            Debug.LogWarning("[SubtitleToggle] WebSocketManager.Instance is null. Waiting for it to initialize...");
            return;
        }

        if (WebSocketManager.Instance.subtitleText == null)
        {
            Debug.LogWarning("[SubtitleToggle] WebSocketManager.Instance.subtitleText is null. Waiting for it to be assigned...");
            return;
        }

        // get the parent panel (contains both text and background)
        subtitlePanel = WebSocketManager.Instance.subtitleText.transform.parent?.gameObject;
        
        if (subtitlePanel == null)
        {
            // use the text GameObject itself if no parent found
            subtitlePanel = WebSocketManager.Instance.subtitleText.gameObject;
            Debug.Log("[SubtitleToggle] Using subtitle text GameObject directly (no parent panel found).");
        }
        else
        {
            Debug.Log($"[SubtitleToggle] Found subtitle panel: {subtitlePanel.name}");
        }
    }

    // sets subtitle visibility
    // pass true to show, false to hide
    public void SetSubtitleVisible(bool visible)
    {
        if (subtitlePanel == null)
        {
            FindSubtitlePanel();
            if (subtitlePanel == null)
            {
                Debug.LogError("[SubtitleToggle] Cannot set visibility: subtitle panel not found.");
                return;
            }
        }

        isSubtitleVisible = visible;
        subtitlePanel.SetActive(isSubtitleVisible);
        UpdateToggleVisualState();
        
        // save the state so it persists when app restarts
        PlayerPrefs.SetInt(SUBTITLE_VISIBILITY_KEY, isSubtitleVisible ? 1 : 0);
        PlayerPrefs.Save();
    }

    // gets the current subtitle visibility
    // returns true if visible, false if hidden
    public bool IsSubtitleVisible()
    {
        return isSubtitleVisible;
    }
}
