using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
using UnityEngine.UI;
using TMPro;

/// <summary>
/// Play mode tests for SubtitleToggle
/// EXPECTATIONS:
/// 1) Toggle UI changes update panel visibility
/// 2) State persists to PlayerPrefs after toggle
/// 3) Panel visibility toggles correctly
/// 4) Multiple toggles work correctly
/// </summary>
public class SubtitleToggle_PlayModeTests
{
    private GameObject webSocketManagerGO;
    private WebSocketManager mockWebSocketManager;
    private GameObject subtitlePanelGO;
    private TextMeshProUGUI subtitleText;
    private const string SUBTITLE_VISIBILITY_KEY = "SubtitleVisibility";

    [SetUp]
    public void SetUp()
    {
        // clean up PlayerPrefs before each test
        PlayerPrefs.DeleteKey(SUBTITLE_VISIBILITY_KEY);
        PlayerPrefs.Save();

        // create subtitle panel structure
        subtitlePanelGO = new GameObject("SubtitlePanel");
        var textGO = new GameObject("SubtitleText");
        textGO.transform.SetParent(subtitlePanelGO.transform);
        subtitleText = textGO.AddComponent<TextMeshProUGUI>();

        // create a mock WebSocketManager for testing
        webSocketManagerGO = new GameObject("WebSocketManager");
        mockWebSocketManager = webSocketManagerGO.AddComponent<WebSocketManager>();
        mockWebSocketManager.subtitleText = subtitleText;

        // set the singleton instance so our tests can use it
        var instanceProperty = typeof(WebSocketManager).GetProperty("Instance",
            System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.Public);
        instanceProperty.SetValue(null, mockWebSocketManager);
    }

    [TearDown]
    public void TearDown()
    {
        // clean up PlayerPrefs
        PlayerPrefs.DeleteKey(SUBTITLE_VISIBILITY_KEY);
        PlayerPrefs.Save();

        // reset the singleton
        var instanceProperty = typeof(WebSocketManager).GetProperty("Instance",
            System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.Public);
        instanceProperty.SetValue(null, null);

        // clean up GameObjects
        if (subtitlePanelGO != null)
        {
            UnityEngine.Object.DestroyImmediate(subtitlePanelGO);
        }
        if (webSocketManagerGO != null)
        {
            UnityEngine.Object.DestroyImmediate(webSocketManagerGO);
        }
    }

    [UnityTest]
    public IEnumerator Toggle_UIChange_UpdatesPanelVisibility()
    {
        var go = new GameObject("SubtitleToggle");
        var toggle = go.AddComponent<SubtitleToggle>();
        var uiToggle = go.AddComponent<Toggle>();

        // set up the toggle component and panel
        typeof(SubtitleToggle)
            .GetField("uiToggle", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            .SetValue(toggle, uiToggle);
        typeof(SubtitleToggle)
            .GetField("subtitlePanel", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            .SetValue(toggle, subtitlePanelGO);

        subtitlePanelGO.SetActive(true);

        // initialize
        var startMethod = typeof(SubtitleToggle).GetMethod("Start",
            System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
        startMethod.Invoke(toggle, null);

        yield return null; // wait a frame

        // simulate UI toggle change
        uiToggle.isOn = false;
        uiToggle.onValueChanged.Invoke(false);

        yield return null; // wait a frame

        // Expected: panel should be hidden
        Assert.IsFalse(subtitlePanelGO.activeSelf, "Expected subtitle panel to be hidden after UI toggle.");

        UnityEngine.Object.DestroyImmediate(go);
    }

    [UnityTest]
    public IEnumerator Toggle_StatePersistsToPlayerPrefs()
    {
        var go = new GameObject("SubtitleToggle");
        var toggle = go.AddComponent<SubtitleToggle>();

        typeof(SubtitleToggle)
            .GetField("subtitlePanel", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            .SetValue(toggle, subtitlePanelGO);

        subtitlePanelGO.SetActive(true);

        var startMethod = typeof(SubtitleToggle).GetMethod("Start",
            System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
        startMethod.Invoke(toggle, null);

        yield return null;

        // hide subtitles
        toggle.SetSubtitleVisible(false);

        yield return null;

        // Expected: PlayerPrefs should be saved
        int savedValue = PlayerPrefs.GetInt(SUBTITLE_VISIBILITY_KEY, -1);
        Assert.AreEqual(0, savedValue, "Expected PlayerPrefs to persist hidden state.");

        UnityEngine.Object.DestroyImmediate(go);
    }

    [UnityTest]
    public IEnumerator Toggle_PanelVisibility_TogglesCorrectly()
    {
        var go = new GameObject("SubtitleToggle");
        var toggle = go.AddComponent<SubtitleToggle>();

        typeof(SubtitleToggle)
            .GetField("subtitlePanel", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            .SetValue(toggle, subtitlePanelGO);

        subtitlePanelGO.SetActive(true);

        var startMethod = typeof(SubtitleToggle).GetMethod("Start",
            System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
        startMethod.Invoke(toggle, null);

        yield return null;

        // toggle visibility
        toggle.SetSubtitleVisible(false);
        yield return null;
        Assert.IsFalse(subtitlePanelGO.activeSelf, "Expected panel to be hidden.");

        toggle.SetSubtitleVisible(true);
        yield return null;
        Assert.IsTrue(subtitlePanelGO.activeSelf, "Expected panel to be visible.");

        UnityEngine.Object.DestroyImmediate(go);
    }

    [UnityTest]
    public IEnumerator Toggle_MultipleToggles_WorkCorrectly()
    {
        var go = new GameObject("SubtitleToggle");
        var toggle = go.AddComponent<SubtitleToggle>();
        var uiToggle = go.AddComponent<Toggle>();

        typeof(SubtitleToggle)
            .GetField("uiToggle", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            .SetValue(toggle, uiToggle);
        typeof(SubtitleToggle)
            .GetField("subtitlePanel", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            .SetValue(toggle, subtitlePanelGO);

        subtitlePanelGO.SetActive(true);

        var startMethod = typeof(SubtitleToggle).GetMethod("Start",
            System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
        startMethod.Invoke(toggle, null);

        yield return null;

        // toggle multiple times
        toggle.SetSubtitleVisible(false);
        yield return null;
        toggle.SetSubtitleVisible(true);
        yield return null;
        toggle.SetSubtitleVisible(false);
        yield return null;

        // Expected: final state should be correct
        bool isVisible = toggle.IsSubtitleVisible();
        Assert.IsFalse(isVisible, "Expected final state to be hidden after multiple toggles.");

        // Expected: panel should reflect final state
        Assert.IsFalse(subtitlePanelGO.activeSelf, "Expected panel to reflect final hidden state.");

        UnityEngine.Object.DestroyImmediate(go);
    }

    [UnityTest]
    public IEnumerator Toggle_FindSubtitlePanel_WorksInUpdate()
    {
        // don't set panel initially
        var go = new GameObject("SubtitleToggle");
        var toggle = go.AddComponent<SubtitleToggle>();

        var startMethod = typeof(SubtitleToggle).GetMethod("Start",
            System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
        startMethod.Invoke(toggle, null);

        yield return null;

        // simulate Update() being called (should find panel)
        var updateMethod = typeof(SubtitleToggle).GetMethod("Update",
            System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
        updateMethod.Invoke(toggle, null);

        yield return null;

        // Expected: panel should be found through WebSocketManager
        GameObject panel = (GameObject)typeof(SubtitleToggle)
            .GetField("subtitlePanel", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            .GetValue(toggle);
        Assert.IsNotNull(panel, "Expected FindSubtitlePanel to locate panel in Update().");

        UnityEngine.Object.DestroyImmediate(go);
    }
}

