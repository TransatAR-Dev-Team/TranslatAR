using UnityEngine;
using TMPro;
using UnityEngine.UI;

public class FontSizeController : MonoBehaviour
{
    [Header("UI References")]
    public TextMeshProUGUI subtitleText;    
    public Slider fontSizeSlider;           
    public TextMeshProUGUI fontSizeValueText;

    private const string FONT_SIZE_KEY = "SubtitleFontSize";

    [Header("Font Size Settings")]
    public float minSize = 18f;
    public float maxSize = 72f;

    void Start()
    {
        /* temp hardcoded font value for testing (remove after controllers work)
           works in 2d editor
        float hardcodedTestSize = 50f;
        float savedSize = hardcodedTestSize;
        */

        float savedSize = PlayerPrefs.GetFloat(FONT_SIZE_KEY, 48f);
        savedSize = Mathf.Clamp(savedSize, minSize, maxSize);

        // apply font to subtitle text
        if (subtitleText != null)
        {
            subtitleText.fontSize = savedSize;
            Debug.Log($"[TEST] Hardcoded subtitle font size applied: {savedSize}"); // debug log to make sure hardcoded value works 
        }

        // slider setup (for when controllers work)
        if (fontSizeSlider != null)
        {
            fontSizeSlider.minValue = minSize;
            fontSizeSlider.maxValue = maxSize;
            fontSizeSlider.value = savedSize;
            fontSizeSlider.onValueChanged.AddListener(OnFontSizeChanged);
        }

        // update label
        if (fontSizeValueText != null)
        {
            fontSizeValueText.text = $"{Mathf.RoundToInt(savedSize)}pt";
        }

        // save
        PlayerPrefs.SetFloat(FONT_SIZE_KEY, savedSize);
    }

    // slider reaction (for when controllers work)
    public void OnFontSizeChanged(float value)
    {
        if (subtitleText != null)
            subtitleText.fontSize = value;

        if (fontSizeValueText != null)
            fontSizeValueText.text = $"{Mathf.RoundToInt(value)}pt";

        PlayerPrefs.SetFloat(FONT_SIZE_KEY, value);
    }
}
