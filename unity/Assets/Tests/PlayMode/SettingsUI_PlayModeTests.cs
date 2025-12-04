using System.Collections;
using NUnit.Framework;
using TMPro;
using UnityEngine;
using UnityEngine.TestTools;
using UnityEngine.UI;

public class SettingsUI_PlayModeTests
{
    private GameObject root;
    private TextMeshProUGUI tmp;
    private Slider slider;

    [UnitySetUp]
    public IEnumerator Setup()
    {
        root = new GameObject("RuntimeRoot", typeof(RectTransform));
        var canvas = root.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;

        // text object
        var textGO = new GameObject("SubtitleTMP", typeof(RectTransform));
        textGO.transform.SetParent(root.transform);
        tmp = textGO.AddComponent<TextMeshProUGUI>();

        // slider object
        var sliderGO = new GameObject("UISlider", typeof(RectTransform));
        sliderGO.transform.SetParent(root.transform);
        slider = sliderGO.AddComponent<Slider>();

        // wait a frame so Unity fully initializes UI
        yield return null;
    }

    [UnityTearDown]
    public IEnumerator Teardown()
    {
        Object.Destroy(root);
        PlayerPrefs.DeleteAll();
        yield return null;
    }

    //  FONT SIZE CONTROLLER - PLAY MODE TEST

    [UnityTest]
    public IEnumerator FontSizeController_StartUsesSavedFontSize()
    {
        // Arrange: save value first
        PlayerPrefs.SetFloat("SubtitleFontSize", 33f);

        var controller = root.AddComponent<FontSizeController>();
        controller.subtitleText = tmp;
        controller.fontSizeSlider = slider;

        // wait a sec so Start() runs automatically
        yield return null;

        Assert.AreEqual(33f, tmp.fontSize);
        Assert.AreEqual(33f, slider.value);
    }

    [UnityTest]
    public IEnumerator FontSizeController_SliderChangeUpdatesFontAndPrefs()
    {
        var controller = root.AddComponent<FontSizeController>();
        controller.subtitleText = tmp;
        controller.fontSizeSlider = slider;

        yield return null;

        slider.value = 50f;
        slider.onValueChanged.Invoke(slider.value);

        Assert.AreEqual(50f, tmp.fontSize);
        Assert.AreEqual(50f, PlayerPrefs.GetFloat("SubtitleFontSize"));
    }

    // OPACITY CONTROLLER - PLAY MODE TEST

    [UnityTest]
    public IEnumerator OpacityController_StartUsesSavedOpacity()
    {
        PlayerPrefs.SetFloat("SubtitleOpacity", 0.25f);

        var controller = root.AddComponent<OpacityController>();
        controller.subtitleText = tmp;
        controller.opacitySlider = slider;

        yield return null;  

        Assert.AreEqual(0.25f, tmp.alpha, 0.001f);
        Assert.AreEqual(25f, slider.value, 0.001f); 
    }

    [UnityTest]
    public IEnumerator OpacityController_SliderChangeUpdatesAlphaAndPrefs()
    {
        var controller = root.AddComponent<OpacityController>();
        controller.subtitleText = tmp;
        controller.opacitySlider = slider;

        yield return null;   // Start()

        slider.value = 80f;
        slider.onValueChanged.Invoke(slider.value);

        Assert.AreEqual(0.8f, tmp.alpha, 0.001f);
        Assert.AreEqual(0.8f, PlayerPrefs.GetFloat("SubtitleOpacity"), 0.001f);
    }
}
