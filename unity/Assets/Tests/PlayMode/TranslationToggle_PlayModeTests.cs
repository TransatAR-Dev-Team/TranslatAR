using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
using UnityEngine.UI;

/// <summary>
/// Play mode tests for TranslationToggle
/// EXPECTATIONS:
/// 1) Toggle UI changes update WebSocketManager state
/// 2) State persists to PlayerPrefs after toggle
/// 3) State syncs when WebSocketManager changes externally
/// 4) Multiple toggles work correctly
/// </summary>
public class TranslationToggle_PlayModeTests
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

    [UnityTest]
    public IEnumerator Toggle_UIChange_UpdatesWebSocketManager()
    {
        var go = new GameObject("TranslationToggle");
        var toggle = go.AddComponent<TranslationToggle>();
        var uiToggle = go.AddComponent<Toggle>();

        // set up the toggle component
        typeof(TranslationToggle)
            .GetField("uiToggle", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            .SetValue(toggle, uiToggle);

        // initialize
        var startMethod = typeof(TranslationToggle).GetMethod("Start",
            System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
        startMethod.Invoke(toggle, null);

        yield return null; // wait a frame

        // simulate UI toggle change
        uiToggle.isOn = false;
        uiToggle.onValueChanged.Invoke(false);

        yield return null; // wait a frame

        // Expected: WebSocketManager should be updated
        Assert.IsFalse(mockWebSocketManager.isTranslationEnabled, "Expected WebSocketManager translation state to be disabled after UI toggle.");

        UnityEngine.Object.DestroyImmediate(go);
    }

    [UnityTest]
    public IEnumerator Toggle_StatePersistsToPlayerPrefs()
    {
        var go = new GameObject("TranslationToggle");
        var toggle = go.AddComponent<TranslationToggle>();
        var uiToggle = go.AddComponent<Toggle>();

        typeof(TranslationToggle)
            .GetField("uiToggle", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            .SetValue(toggle, uiToggle);

        var startMethod = typeof(TranslationToggle).GetMethod("Start",
            System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
        startMethod.Invoke(toggle, null);

        yield return null;

        // toggle off
        toggle.SetTranslationEnabled(false);

        yield return null;

        // Expected: PlayerPrefs should be saved
        int savedValue = PlayerPrefs.GetInt(TRANSLATION_ENABLED_KEY, -1);
        Assert.AreEqual(0, savedValue, "Expected PlayerPrefs to persist disabled state.");

        UnityEngine.Object.DestroyImmediate(go);
    }

    [UnityTest]
    public IEnumerator Toggle_SyncsWhenWebSocketManagerChangesExternally()
    {
        var go = new GameObject("TranslationToggle");
        var toggle = go.AddComponent<TranslationToggle>();
        var uiToggle = go.AddComponent<Toggle>();

        typeof(TranslationToggle)
            .GetField("uiToggle", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            .SetValue(toggle, uiToggle);

        var startMethod = typeof(TranslationToggle).GetMethod("Start",
            System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
        startMethod.Invoke(toggle, null);

        yield return null;

        // change WebSocketManager state externally
        mockWebSocketManager.SetTranslationEnabled(false);

        // simulate Update() being called
        var updateMethod = typeof(TranslationToggle).GetMethod("Update",
            System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
        updateMethod.Invoke(toggle, null);

        yield return null;

        // Expected: toggle should sync with WebSocketManager
        bool isEnabled = (bool)typeof(TranslationToggle)
            .GetField("isTranslationEnabled", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            .GetValue(toggle);
        Assert.IsFalse(isEnabled, "Expected toggle state to sync with WebSocketManager.");

        // Expected: UI toggle should update
        Assert.IsFalse(uiToggle.isOn, "Expected UI toggle to reflect synced state.");

        UnityEngine.Object.DestroyImmediate(go);
    }

    [UnityTest]
    public IEnumerator Toggle_MultipleToggles_WorkCorrectly()
    {
        var go = new GameObject("TranslationToggle");
        var toggle = go.AddComponent<TranslationToggle>();
        var uiToggle = go.AddComponent<Toggle>();

        typeof(TranslationToggle)
            .GetField("uiToggle", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            .SetValue(toggle, uiToggle);

        var startMethod = typeof(TranslationToggle).GetMethod("Start",
            System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
        startMethod.Invoke(toggle, null);

        yield return null;

        // toggle multiple times
        toggle.SetTranslationEnabled(false);
        yield return null;
        toggle.SetTranslationEnabled(true);
        yield return null;
        toggle.SetTranslationEnabled(false);
        yield return null;

        // Expected: final state should be correct
        bool isEnabled = toggle.IsTranslationEnabled();
        Assert.IsFalse(isEnabled, "Expected final state to be disabled after multiple toggles.");

        // Expected: WebSocketManager should reflect final state
        Assert.IsFalse(mockWebSocketManager.isTranslationEnabled, "Expected WebSocketManager to reflect final state.");

        UnityEngine.Object.DestroyImmediate(go);
    }
}

