using NUnit.Framework;
using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// Edit mode tests for TranslationToggle
/// EXPECTATIONS:
/// 1) Start() loads saved state from PlayerPrefs when available
/// 2) Start() syncs with WebSocketManager when it exists
/// 3) Start() handles null WebSocketManager gracefully
/// 4) SetTranslationEnabled() updates state and saves to PlayerPrefs
/// 5) IsTranslationEnabled() returns correct state
/// </summary>
public class TranslationToggle_EditModeTests
{
    private GameObject webSocketManagerGO;
    private WebSocketManager mockWebSocketManager;
    private const string TRANSLATION_ENABLED_KEY = "TranslationEnabled";

    [SetUp]
    public void SetUp()
    {
        // clean up PlayerPrefs before each test
        PlayerPrefs.DeleteKey(TRANSLATION_ENABLED_KEY);
        PlayerPrefs.Save();

        // create a mock WebSocketManager for testing
        webSocketManagerGO = new GameObject("WebSocketManager");
        mockWebSocketManager = webSocketManagerGO.AddComponent<WebSocketManager>();
        // set the singleton instance so our tests can use it
        var instanceProperty = typeof(WebSocketManager).GetProperty("Instance",
            System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.Public);
        instanceProperty.SetValue(null, mockWebSocketManager);
    }

    [TearDown]
    public void TearDown()
    {
        // clean up PlayerPrefs
        PlayerPrefs.DeleteKey(TRANSLATION_ENABLED_KEY);
        PlayerPrefs.Save();

        // reset the singleton
        var instanceProperty = typeof(WebSocketManager).GetProperty("Instance",
            System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.Public);
        instanceProperty.SetValue(null, null);

        // clean up GameObjects
        if (webSocketManagerGO != null)
        {
            UnityEngine.Object.DestroyImmediate(webSocketManagerGO);
        }
    }

    [Test]
    public void TranslationToggle_Start_LoadsSavedStateFromPlayerPrefs()
    {
        // set saved state in PlayerPrefs (disabled)
        PlayerPrefs.SetInt(TRANSLATION_ENABLED_KEY, 0);
        PlayerPrefs.Save();

        var go = new GameObject("TranslationToggle");
        var toggle = go.AddComponent<TranslationToggle>();

        // call Start()
        var startMethod = typeof(TranslationToggle).GetMethod("Start",
            System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
        startMethod.Invoke(toggle, null);

        // Expected: should load the saved state from PlayerPrefs
        bool isEnabled = (bool)typeof(TranslationToggle)
            .GetField("isTranslationEnabled", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            .GetValue(toggle);
        Assert.IsFalse(isEnabled, "Expected translation to be disabled based on PlayerPrefs.");

        UnityEngine.Object.DestroyImmediate(go);
    }

    [Test]
    public void TranslationToggle_Start_SyncsWithWebSocketManager()
    {
        // set WebSocketManager state to disabled
        mockWebSocketManager.SetTranslationEnabled(false);

        var go = new GameObject("TranslationToggle");
        var toggle = go.AddComponent<TranslationToggle>();

        // call Start() - no saved PlayerPrefs, so it should use WebSocketManager state
        var startMethod = typeof(TranslationToggle).GetMethod("Start",
            System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
        startMethod.Invoke(toggle, null);

        // Expected: should sync with WebSocketManager state
        bool isEnabled = (bool)typeof(TranslationToggle)
            .GetField("isTranslationEnabled", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            .GetValue(toggle);
        Assert.IsFalse(isEnabled, "Expected translation state to sync with WebSocketManager.");

        UnityEngine.Object.DestroyImmediate(go);
    }

    [Test]
    public void TranslationToggle_Start_HandlesNullWebSocketManager()
    {
        // clear WebSocketManager instance (simulate it not being ready)
        var instanceProperty = typeof(WebSocketManager).GetProperty("Instance",
            System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.Public);
        instanceProperty.SetValue(null, null);

        var go = new GameObject("TranslationToggle");
        var toggle = go.AddComponent<TranslationToggle>();

        // call Start()
        var startMethod = typeof(TranslationToggle).GetMethod("Start",
            System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
        startMethod.Invoke(toggle, null);

        // Expected: shouldn't crash, default state should be enabled
        bool isEnabled = (bool)typeof(TranslationToggle)
            .GetField("isTranslationEnabled", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            .GetValue(toggle);
        Assert.IsTrue(isEnabled, "Expected default translation state to be enabled when WebSocketManager is null.");

        UnityEngine.Object.DestroyImmediate(go);
    }

    [Test]
    public void TranslationToggle_SetTranslationEnabled_UpdatesStateAndSavesToPlayerPrefs()
    {
        var go = new GameObject("TranslationToggle");
        var toggle = go.AddComponent<TranslationToggle>();

        // disable translation
        toggle.SetTranslationEnabled(false);

        // Expected: should update state and save to PlayerPrefs
        bool isEnabled = (bool)typeof(TranslationToggle)
            .GetField("isTranslationEnabled", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            .GetValue(toggle);
        Assert.IsFalse(isEnabled, "Expected translation state to be disabled.");

        int savedValue = PlayerPrefs.GetInt(TRANSLATION_ENABLED_KEY, -1);
        Assert.AreEqual(0, savedValue, "Expected PlayerPrefs to save disabled state (0).");

        UnityEngine.Object.DestroyImmediate(go);
    }

    [Test]
    public void TranslationToggle_IsTranslationEnabled_ReturnsCorrectState()
    {
        var go = new GameObject("TranslationToggle");
        var toggle = go.AddComponent<TranslationToggle>();

        // set WebSocketManager state first (IsTranslationEnabled syncs with it)
        mockWebSocketManager.SetTranslationEnabled(false);

        // check the state
        bool result = toggle.IsTranslationEnabled();

        // Expected: should return the synced state from WebSocketManager
        Assert.IsFalse(result, "Expected IsTranslationEnabled to return false (synced from WebSocketManager).");

        UnityEngine.Object.DestroyImmediate(go);
    }

    [Test]
    public void TranslationToggle_OnToggleValueChanged_UpdatesWebSocketManager()
    {
        var go = new GameObject("TranslationToggle");
        var toggle = go.AddComponent<TranslationToggle>();
        var uiToggle = go.AddComponent<Toggle>();

        // set up the toggle component
        typeof(TranslationToggle)
            .GetField("uiToggle", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            .SetValue(toggle, uiToggle);

        // start with translation enabled
        typeof(TranslationToggle)
            .GetField("isTranslationEnabled", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            .SetValue(toggle, true);

        // simulate toggle change
        var onToggleMethod = typeof(TranslationToggle).GetMethod("OnToggleValueChanged",
            System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
        onToggleMethod.Invoke(toggle, new object[] { false });

        // Expected: WebSocketManager should be updated
        Assert.IsFalse(mockWebSocketManager.isTranslationEnabled, "Expected WebSocketManager translation state to be disabled.");

        // Expected: PlayerPrefs should be saved
        int savedValue = PlayerPrefs.GetInt(TRANSLATION_ENABLED_KEY, -1);
        Assert.AreEqual(0, savedValue, "Expected PlayerPrefs to save disabled state.");

        UnityEngine.Object.DestroyImmediate(go);
    }
}

