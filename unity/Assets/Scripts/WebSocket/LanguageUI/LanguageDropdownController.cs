using System.Collections.Generic;
using TMPro;
using UnityEngine;

public class LanguageDropdownController : MonoBehaviour
{
    [Header("Assign these in the Inspector")]
    [SerializeField] private TMP_Dropdown dropdown;   // LanguageDropdown
    [SerializeField] private TMP_Text statusText;     // the StatusText TMP label

    [Header("Mode")]
    [Tooltip("If ON: selection is treated as the SPOKEN language and output is forced to English (en). If OFF: selection is the translation TARGET language.")]
    [SerializeField] private bool translateToEnglishMode = false;

    private readonly List<string> names = new()
    {
        "English", "Spanish", "French", "German",
        "Japanese", "Korean", "Chinese (Simplified)"
    };

    private readonly List<string> codes = new()
    {
        "en", "es", "fr", "de",
        "ja", "ko", "zh"
    };

    public static string SelectedLabel { get; private set; } = "Spanish";
    public static string SelectedCode  { get; private set; } = "es";

    private const string PrefTarget = "targetLanguageCode";
    private const string PrefMode   = "translateToEnglishMode"; // "0" or "1"

    void Awake()
    {
        if (!dropdown) dropdown = GetComponent<TMP_Dropdown>();

        // Restore mode
        translateToEnglishMode = PlayerPrefs.GetInt(PrefMode, translateToEnglishMode ? 1 : 0) == 1;

        // Populate options if empty
        if (dropdown.options.Count == 0)
        {
            dropdown.ClearOptions();
            dropdown.AddOptions(new List<string>(names));
        }

        // Default to Spanish if present
        int defaultIndex = names.IndexOf("Spanish");
        if (defaultIndex >= 0) dropdown.value = defaultIndex;
        dropdown.RefreshShownValue();

        // Wire events
        dropdown.onValueChanged.AddListener(OnDropdownChanged);

        // Apply current selection to runtime
        OnDropdownChanged(dropdown.value);
    }

    // Call this from a UI Toggle/Checkbox to switch modes at runtime
    public void SetTranslateToEnglishMode(bool enabled)
    {
        translateToEnglishMode = enabled;
        PlayerPrefs.SetInt(PrefMode, enabled ? 1 : 0);
        PlayerPrefs.Save();

        // Re-apply current selection in the new mode
        OnDropdownChanged(dropdown.value);
    }

    private void OnDropdownChanged(int index)
    {
        if (index < 0 || index >= names.Count || index >= codes.Count) return;

        SelectedLabel = names[index];
        SelectedCode  = codes[index];

        if (translateToEnglishMode)
        {
            // SPOKEN language -> English
            if (WebSocketManager.Instance != null)
            {
                WebSocketManager.Instance.sourceLanguage = SelectedCode; // what the speaker is using
                WebSocketManager.Instance.targetLanguage = "en";         // always to English
            }

            SetStatus($"Input language set to <b>{SelectedLabel}</b> ({SelectedCode}) → translating to <b>English</b> (en) …");
        }
        else
        {
            // Classic TARGET language selector
            if (WebSocketManager.Instance != null)
            {
                WebSocketManager.Instance.targetLanguage = SelectedCode;
                // Leave sourceLanguage as previously configured (or set it elsewhere)
            }

            // Remember last chosen target for convenience
            PlayerPrefs.SetString(PrefTarget, SelectedCode);
            PlayerPrefs.Save();

            SetStatus($"Target language set to <b>{SelectedLabel}</b> ({SelectedCode}) – now translating in <b>{SelectedLabel}</b>…");
        }

        // Debug aid: confirm what we’re sending
        if (WebSocketManager.Instance != null)
        {
            Debug.Log($"[LangDropdown] mode={(translateToEnglishMode ? "Source→EN" : "Target")} " +
                      $"source={WebSocketManager.Instance.sourceLanguage} target={WebSocketManager.Instance.targetLanguage}");
        }
    }

    // --- Optional helpers for UI buttons/toggles ---
    public void EnableTranslateToEnglishMode() => SetTranslateToEnglishMode(true);
    public void DisableTranslateToEnglishMode() => SetTranslateToEnglishMode(false);
    public void ToggleTranslateToEnglishMode()  => SetTranslateToEnglishMode(!translateToEnglishMode);

    // --- UI helpers ---
    private void SetStatus(string msg)
    {
        if (statusText) statusText.text = msg;
        Debug.Log($"[LanguageDropdown] {msg}");
    }
}
