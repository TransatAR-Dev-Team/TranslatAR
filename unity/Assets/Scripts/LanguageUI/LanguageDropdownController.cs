using System.Collections.Generic;
using TMPro;
using UnityEngine;

public class LanguageDropdownController : MonoBehaviour
{
    [Header("Assign these in the Inspector")]
    [SerializeField] private TMP_Dropdown dropdown;   // LanguageDropdown
    [SerializeField] private TMP_Text statusText;     // the StatusText TMP label

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

    void Awake()
    {
        if (!dropdown) dropdown = GetComponent<TMP_Dropdown>();

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
        OnDropdownChanged(dropdown.value);
    }

    private void OnDropdownChanged(int index)
    {
        if (index < 0 || index >= names.Count || index >= codes.Count) return;

        SelectedLabel = names[index];
        SelectedCode  = codes[index];
        SetStatus($"Language changed to <b>{SelectedLabel}</b> ({SelectedCode}) — now translating in <b>{SelectedLabel}</b>…");
    }

    // --- Logs ---

    public void ShowLanguageChanged()
    {
        SetStatus($"Language changed to <b>{SelectedLabel}</b> ({SelectedCode})");
    }

    public void ShowTranslating()
    {
        AppendStatus($"  Now translating in <b>{SelectedLabel}</b>…");
    }

    public void ShowIdle()
    {
        SetStatus($"Ready. Target language: <b>{SelectedLabel}</b>");
    }

    // --- UI helpers ---

    private void SetStatus(string msg)
    {
        if (statusText) statusText.text = msg;
        Debug.Log($"[LanguageDropdown] {msg}");
    }

    private void AppendStatus(string msg)
    {
        if (statusText)
        {
            if (string.IsNullOrEmpty(statusText.text)) statusText.text = msg;
            else statusText.text += msg;
        }
        Debug.Log($"[LanguageDropdown] {msg}");
    }
}
