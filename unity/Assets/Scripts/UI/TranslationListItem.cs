using UnityEngine;
using TMPro;

/// <summary>
/// Individual translation item UI component.
/// Displays original text, translated text, and timestamp.
/// </summary>
public class TranslationListItem : MonoBehaviour
{
    [Header("UI References")]
    /// <summary>
    /// UI element displaying the original text
    /// </summary>
    public TextMeshProUGUI originalTextUI;

    /// <summary>
    /// UI element displaying the translated text
    /// </summary>
    public TextMeshProUGUI translatedTextUI;

    /// <summary>
    /// UI element displaying the timestamp (optional)
    /// </summary>
    public TextMeshProUGUI timestampUI;

    [Header("Styling")]
    /// <summary>
    /// Original text color
    /// </summary>
    public Color originalTextColor = new Color(0.7f, 0.7f, 0.7f, 1f);

    /// <summary>
    /// Translated text color
    /// </summary>
    public Color translatedTextColor = Color.white;

    /// <summary>
    /// Currently displayed data
    /// </summary>
    private TranslationData currentData;

    /// <summary>
    /// Set translation data and update UI
    /// </summary>
    /// <param name="data">Translation data to display</param>
    public void SetData(TranslationData data)
    {
        currentData = data;

        if (originalTextUI != null)
        {
            originalTextUI.text = data.OriginalText ?? "";
            originalTextUI.color = originalTextColor;
        }

        if (translatedTextUI != null)
        {
            translatedTextUI.text = data.TranslatedText ?? "";
            translatedTextUI.color = translatedTextColor;
        }

        if (timestampUI != null)
        {
            timestampUI.text = data.Timestamp.ToString("HH:mm:ss");
        }
    }

    /// <summary>
    /// Get currently displayed data
    /// </summary>
    public TranslationData GetData()
    {
        return currentData;
    }

    /// <summary>
    /// Update only the original text
    /// </summary>
    public void UpdateOriginalText(string text)
    {
        if (originalTextUI != null)
        {
            originalTextUI.text = text;
        }
        if (currentData != null)
        {
            currentData.OriginalText = text;
        }
    }

    /// <summary>
    /// Update only the translated text
    /// </summary>
    public void UpdateTranslatedText(string text)
    {
        if (translatedTextUI != null)
        {
            translatedTextUI.text = text;
        }
        if (currentData != null)
        {
            currentData.TranslatedText = text;
        }
    }
}
