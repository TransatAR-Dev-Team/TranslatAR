using NUnit.Framework;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class SettingsUI_EditModeTests
{
    private GameObject root;
    private TextMeshProUGUI tmp;
    private Slider slider;

    [SetUp]
    public void Setup()
    {
        root = new GameObject("TestRoot", typeof(RectTransform));
        var canvas = root.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;

        // TMP child
        var textGO = new GameObject("SubtitleTMP", typeof(RectTransform));
        textGO.transform.SetParent(root.transform);
        tmp = textGO.AddComponent<TextMeshProUGUI>();

        // slider child
        var sliderGO = new GameObject("FontSlider", typeof(RectTransform));
        sliderGO.transform.SetParent(root.transform);
        slider = sliderGO.AddComponent<Slider>();
    }

    [TearDown]
    public void Teardown()
    {
        Object.DestroyImmediate(root);
        PlayerPrefs.DeleteAll();
    }

    // FONT SIZE CONTROLLER TESTS - EDITMODE
    [Test]
    public void FontSizeController_ApplySavedValueCorrectly()
    {
        PlayerPrefs.SetFloat("SubtitleFontSize", 60f);

        var controller = root.AddComponent<FontSizeController>();
        controller.subtitleText = tmp;
        controller.fontSizeSlider = slider;

        controller.minSize = 18f;
        controller.maxSize = 72f;

        controller.Start(); // public now

        Assert.AreEqual(60f, tmp.fontSize);
        Assert.AreEqual(60f, slider.value);
    }

    [Test]
    public void FontSizeController_SliderUpdateChangesFont()
    {
        var controller = root.AddComponent<FontSizeController>();
        controller.subtitleText = tmp;
        controller.fontSizeSlider = slider;

        controller.Start();
        controller.OnFontSizeChanged(42f);

        Assert.AreEqual(42f, tmp.fontSize);
        Assert.AreEqual(42f, PlayerPrefs.GetFloat("SubtitleFontSize"));
    }

    // OPACITY CONTROLLER TESTS - EDITMODE
    [Test]
    public void OpacityController_ApplySavedOpacityCorrectly()
    {
        PlayerPrefs.SetFloat("SubtitleOpacity", 0.55f);

        var controller = root.AddComponent<OpacityController>();
        controller.subtitleText = tmp;
        controller.opacitySlider = slider;

        controller.Start();

        Assert.AreEqual(0.55f, tmp.alpha, 0.001f);
    }

    [Test]
    public void OpacityController_SliderValueUpdatesTextTransparency()
    {
        var controller = root.AddComponent<OpacityController>();
        controller.subtitleText = tmp;
        controller.opacitySlider = slider;

        controller.Start();
        controller.OnOpacityChanged(80f); // 80% opacity

        Assert.AreEqual(0.8f, tmp.alpha, 0.001f);
        Assert.AreEqual(0.8f, PlayerPrefs.GetFloat("SubtitleOpacity"), 0.001f);
    }
}
