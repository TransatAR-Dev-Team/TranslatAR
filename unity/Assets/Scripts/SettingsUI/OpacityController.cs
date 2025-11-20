using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class OpacityController : MonoBehaviour
{
    [Header("UI References")]
    public TextMeshProUGUI subtitleText;       
    public Slider opacitySlider;               
    public TextMeshProUGUI opacityValueText;  

    private const string OPACITY_KEY = "SubtitleOpacity";

    void Start()
    {
        // default is 100%
        float savedOpacity = PlayerPrefs.GetFloat(OPACITY_KEY, 1f);
        savedOpacity = Mathf.Clamp(savedOpacity, 0.01f, 1f);

        // apply to subtitle text only (and not other TMPs)
        ApplyOpacity(savedOpacity);

        // convert opacity (0.0–1.0) to slider range (1–100)
        float sliderValue = Mathf.Round(savedOpacity * 100f);

        // setup slider
        if (opacitySlider != null)
        {
            opacitySlider.minValue = 1f;
            opacitySlider.maxValue = 100f;
            opacitySlider.wholeNumbers = true;
            opacitySlider.value = sliderValue;

            opacitySlider.onValueChanged.AddListener(OnOpacityChanged);
        }

        // update label
        if (opacityValueText != null)
            opacityValueText.text = $"{Mathf.RoundToInt(sliderValue)}%";
    }

    // slider setup
    public void OnOpacityChanged(float sliderValue)
    {
        
        float opacity = sliderValue / 100f;
        ApplyOpacity(opacity);

        if (opacityValueText != null)
            opacityValueText.text = $"{Mathf.RoundToInt(sliderValue)}%";

        // save
        PlayerPrefs.SetFloat(OPACITY_KEY, opacity);
    }

    // slider reaction
    private void ApplyOpacity(float opacity)
    {
        if (subtitleText != null)
        {
            subtitleText.alpha = opacity;   // changes only this TMP instance
        }
    }
}
