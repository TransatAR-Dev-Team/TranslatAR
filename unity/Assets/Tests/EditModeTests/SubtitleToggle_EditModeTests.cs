using NUnit.Framework;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

/// <summary>
/// Edit mode tests for SubtitleToggle
/// EXPECTATIONS:
/// 1) Start() loads saved state from PlayerPrefs when available
/// 2) Start() uses current panel state when no saved state exists
/// 3) Start() handles null subtitle panel gracefully
/// 4) SetSubtitleVisible() updates panel visibility and saves to PlayerPrefs
/// 5) IsSubtitleVisible() returns correct state
/// 6) FindSubtitlePanel() locates panel through WebSocketManager
/// </summary>
public class SubtitleToggle_EditModeTests
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

    [Test]
    public void SubtitleToggle_Start_LoadsSavedStateFromPlayerPrefs()
    {
        // set saved state in PlayerPrefs (hidden)
        PlayerPrefs.SetInt(SUBTITLE_VISIBILITY_KEY, 0);
        PlayerPrefs.Save();

        var go = new GameObject("SubtitleToggle");
        var toggle = go.AddComponent<SubtitleToggle>();

        // set subtitle panel
        typeof(SubtitleToggle)
            .GetField("subtitlePanel", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            .SetValue(toggle, subtitlePanelGO);

        // call Start()
        var startMethod = typeof(SubtitleToggle).GetMethod("Start",
            System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
        startMethod.Invoke(toggle, null);

        // Expected: panel should be hidden based on PlayerPrefs
        Assert.IsFalse(subtitlePanelGO.activeSelf, "Expected subtitle panel to be hidden based on PlayerPrefs.");

        bool isVisible = (bool)typeof(SubtitleToggle)
            .GetField("isSubtitleVisible", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            .GetValue(toggle);
        Assert.IsFalse(isVisible, "Expected isSubtitleVisible to be false based on PlayerPrefs.");

        UnityEngine.Object.DestroyImmediate(go);
    }

    [Test]
    public void SubtitleToggle_Start_UsesCurrentPanelStateWhenNoSavedState()
    {
        // no saved state, panel is active
        subtitlePanelGO.SetActive(true);

        var go = new GameObject("SubtitleToggle");
        var toggle = go.AddComponent<SubtitleToggle>();

        // set subtitle panel
        typeof(SubtitleToggle)
            .GetField("subtitlePanel", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            .SetValue(toggle, subtitlePanelGO);

        // call Start()
        var startMethod = typeof(SubtitleToggle).GetMethod("Start",
            System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
        startMethod.Invoke(toggle, null);

        // Expected: should use current panel state (active)
        bool isVisible = (bool)typeof(SubtitleToggle)
            .GetField("isSubtitleVisible", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            .GetValue(toggle);
        Assert.IsTrue(isVisible, "Expected isSubtitleVisible to match current panel state (active).");

        UnityEngine.Object.DestroyImmediate(go);
    }

    [Test]
    public void SubtitleToggle_Start_HandlesNullSubtitlePanel()
    {
        var go = new GameObject("SubtitleToggle");
        var toggle = go.AddComponent<SubtitleToggle>();

        // don't set subtitle panel (leave it null)

        // call Start()
        var startMethod = typeof(SubtitleToggle).GetMethod("Start",
            System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
        startMethod.Invoke(toggle, null);

        // Expected: shouldn't crash, should try to find panel
        GameObject panel = (GameObject)typeof(SubtitleToggle)
            .GetField("subtitlePanel", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            .GetValue(toggle);
        
        // Expected: should find panel through WebSocketManager
        Assert.IsNotNull(panel, "Expected FindSubtitlePanel to locate panel through WebSocketManager.");

        UnityEngine.Object.DestroyImmediate(go);
    }

    [Test]
    public void SubtitleToggle_SetSubtitleVisible_UpdatesPanelAndSavesToPlayerPrefs()
    {
        var go = new GameObject("SubtitleToggle");
        var toggle = go.AddComponent<SubtitleToggle>();

        // set subtitle panel
        typeof(SubtitleToggle)
            .GetField("subtitlePanel", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            .SetValue(toggle, subtitlePanelGO);

        subtitlePanelGO.SetActive(true);

        // hide subtitles
        toggle.SetSubtitleVisible(false);

        // Expected: panel should be hidden
        Assert.IsFalse(subtitlePanelGO.activeSelf, "Expected subtitle panel to be hidden.");

        // Expected: PlayerPrefs should be saved
        int savedValue = PlayerPrefs.GetInt(SUBTITLE_VISIBILITY_KEY, -1);
        Assert.AreEqual(0, savedValue, "Expected PlayerPrefs to save hidden state (0).");

        UnityEngine.Object.DestroyImmediate(go);
    }

    [Test]
    public void SubtitleToggle_IsSubtitleVisible_ReturnsCorrectState()
    {
        var go = new GameObject("SubtitleToggle");
        var toggle = go.AddComponent<SubtitleToggle>();

        // set state to hidden
        typeof(SubtitleToggle)
            .GetField("isSubtitleVisible", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            .SetValue(toggle, false);

        // check the state
        bool result = toggle.IsSubtitleVisible();

        // Expected: should return the current state
        Assert.IsFalse(result, "Expected IsSubtitleVisible to return false.");

        UnityEngine.Object.DestroyImmediate(go);
    }

    [Test]
    public void SubtitleToggle_FindSubtitlePanel_LocatesPanelThroughWebSocketManager()
    {
        var go = new GameObject("SubtitleToggle");
        var toggle = go.AddComponent<SubtitleToggle>();

        // call FindSubtitlePanel
        var findMethod = typeof(SubtitleToggle).GetMethod("FindSubtitlePanel",
            System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
        findMethod.Invoke(toggle, null);

        // Expected: should find the panel through WebSocketManager
        GameObject panel = (GameObject)typeof(SubtitleToggle)
            .GetField("subtitlePanel", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            .GetValue(toggle);
        Assert.IsNotNull(panel, "Expected FindSubtitlePanel to locate panel through WebSocketManager.");
        Assert.AreEqual(subtitlePanelGO, panel, "Expected found panel to match the created panel.");

        UnityEngine.Object.DestroyImmediate(go);
    }

    [Test]
    public void SubtitleToggle_OnToggleValueChanged_UpdatesPanelAndSavesToPlayerPrefs()
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

        // start with panel visible
        subtitlePanelGO.SetActive(true);
        typeof(SubtitleToggle)
            .GetField("isSubtitleVisible", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            .SetValue(toggle, true);

        // simulate toggle change
        var onToggleMethod = typeof(SubtitleToggle).GetMethod("OnToggleValueChanged",
            System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
        onToggleMethod.Invoke(toggle, new object[] { false });

        // Expected: panel should be hidden
        Assert.IsFalse(subtitlePanelGO.activeSelf, "Expected subtitle panel to be hidden after toggle change.");

        // Expected: PlayerPrefs should be saved
        int savedValue = PlayerPrefs.GetInt(SUBTITLE_VISIBILITY_KEY, -1);
        Assert.AreEqual(0, savedValue, "Expected PlayerPrefs to save hidden state.");

        UnityEngine.Object.DestroyImmediate(go);
    }
}

