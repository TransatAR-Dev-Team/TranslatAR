using UnityEngine;

// toggles the visibility of the subtitle display (text and background panel)
public class SubtitleToggle : MonoBehaviour
{
    [Header("Subtitle UI Reference")]
    [Tooltip("Subtitle panel GameObject. Auto-finds if not assigned")]
    [SerializeField] private GameObject subtitlePanel;

    private bool isSubtitleVisible = true;

    void Start()
    {
        // try to find subtitle panel if not assigned
        if (subtitlePanel == null)
        {
            FindSubtitlePanel();
        }

        if (subtitlePanel != null)
        {
            isSubtitleVisible = subtitlePanel.activeSelf;
            Debug.Log($"[SubtitleToggle] Subtitle panel found. Initial state: {(isSubtitleVisible ? "Visible" : "Hidden")}");
        }
        else
        {
            Debug.LogWarning("[SubtitleToggle] Subtitle panel not found. Will retry in Update().");
        }
    }

    void Update()
    {
        // retry finding subtitle panel if not found yet
        if (subtitlePanel == null)
        {
            FindSubtitlePanel();
            if (subtitlePanel != null)
            {
                isSubtitleVisible = subtitlePanel.activeSelf;
                Debug.Log($"[SubtitleToggle] Subtitle panel found in Update. Initial state: {(isSubtitleVisible ? "Visible" : "Hidden")}");
            }
        }
    }

    // attempts to find the subtitle panel GameObject through WebSocketManager
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

        // get the parent panel GameObject (contains both text and background)
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

    // toggles the subtitle visibility on/off
    // translation continues normally
    // call this method from a UI button's onClick event
    public void ToggleSubtitle()
    {
        if (subtitlePanel == null)
        {
            Debug.LogWarning("[SubtitleToggle] Cannot toggle: subtitle panel not assigned. Trying to find it...");
            FindSubtitlePanel();
            
            if (subtitlePanel == null)
            {
                Debug.LogError("[SubtitleToggle] Cannot toggle: subtitle panel not found.");
                return;
            }
        }

        isSubtitleVisible = !isSubtitleVisible;
        subtitlePanel.SetActive(isSubtitleVisible);
    }

    // sets the subtitle visibility explicitly
    // true to show subtitles, false to hide them
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
    }

    // gets the current subtitle visibility state
    // returns true if subtitles are visible, false otherwise
    public bool IsSubtitleVisible()
    {
        return isSubtitleVisible;
    }
}
