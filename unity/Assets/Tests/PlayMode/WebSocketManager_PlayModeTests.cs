using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
using TMPro;

/// <summary>
/// Play mode tests for WebSocketManager
/// Tests real-time WebSocket connection, message handling, and UI updates
/// </summary>
public class WebSocketManager_PlayModeTests
{
    private GameObject testGameObject;
    private WebSocketManager manager;
    private MockWebSocketClient mockWebSocket;
    private GameObject subtitleGameObject;
    private TextMeshProUGUI subtitleText;

    [SetUp]
    public void SetUp()
    {
        testGameObject = new GameObject("WebSocketManagerTest");
        manager = testGameObject.AddComponent<WebSocketManager>();
        
        // Create subtitle UI
        subtitleGameObject = new GameObject("SubtitleText");
        subtitleText = subtitleGameObject.AddComponent<TextMeshProUGUI>();
        manager.subtitleText = subtitleText;
        
        // Set up mock WebSocket
        mockWebSocket = new MockWebSocketClient();
        manager.Initialize((url) => mockWebSocket);
        manager.sourceLanguage = "en";
        manager.targetLanguage = "es";
        
        // Reset singleton
        var instanceProperty = typeof(WebSocketManager).GetProperty("Instance",
            System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.Public);
        instanceProperty.SetValue(null, manager);
    }

    [TearDown]
    public void TearDown()
    {
        // Reset singleton
        var instanceProperty = typeof(WebSocketManager).GetProperty("Instance",
            System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.Public);
        instanceProperty.SetValue(null, null);

        if (subtitleGameObject != null)
        {
            UnityEngine.Object.DestroyImmediate(subtitleGameObject);
        }
        if (testGameObject != null)
        {
            UnityEngine.Object.DestroyImmediate(testGameObject);
        }
    }

    [UnityTest]
    public IEnumerator ConnectWebSocket_UpdatesSubtitleOnOpen()
    {
        // Act
        manager.ConnectWebSocket();
        mockWebSocket.TriggerOpen();
        
        // Wait for Update() to process queued actions
        yield return null;
        yield return null;

        // Assert
        Assert.IsTrue(manager.IsConnected, "Manager should report connected");
        Assert.IsTrue(subtitleText.text.Contains("Connected"), 
            "Subtitle should show connection message");
    }

    [UnityTest]
    public IEnumerator HandleTranscriptionResponse_UpdatesSubtitle()
    {
        // Arrange
        string json = @"{""original_text"":""Hello"",""translated_text"":""Hola""}";
        
        // Act
        manager.HandleTranscriptionResponse(json);
        yield return null;

        // Assert
        Assert.AreEqual("Hola", subtitleText.text, 
            "Subtitle should show translated text");
    }

    [UnityTest]
    public IEnumerator HandleTranscriptionResponse_UsesOriginalWhenNoTranslation()
    {
        // Arrange
        string json = @"{""original_text"":""Hello""}";
        
        // Act
        manager.HandleTranscriptionResponse(json);
        yield return null;

        // Assert
        Assert.AreEqual("Hello", subtitleText.text, 
            "Subtitle should show original text when no translation");
    }

    [UnityTest]
    public IEnumerator SendAudioChunk_SendsWhenConnected()
    {
        // Arrange
        manager.ConnectWebSocket();
        mockWebSocket.TriggerOpen();
        yield return null;
        
        byte[] audioData = new byte[] { 1, 2, 3, 4, 5 };

        // Act
        manager.SendAudioChunk(audioData, "conv123");
        yield return null;

        // Assert
        Assert.AreEqual(1, mockWebSocket.SendCallCount, "Should send audio chunk");
        Assert.IsNotNull(mockWebSocket.LastSentData, "Should have sent data");
    }

    [UnityTest]
    public IEnumerator SetTranslationEnabled_False_IgnoresNewResponses()
    {
        // Arrange
        manager.SetTranslationEnabled(false);
        string json = @"{""original_text"":""Hello"",""translated_text"":""Hola""}";
        subtitleText.text = "Previous text";
        
        // Act
        manager.HandleTranscriptionResponse(json);
        yield return null;

        // Assert
        Assert.AreEqual("Previous text", subtitleText.text, 
            "Subtitle should not update when translation disabled");
    }

    [UnityTest]
    public IEnumerator SetTranslationEnabled_True_ProcessesResponses()
    {
        // Arrange
        manager.SetTranslationEnabled(true);
        string json = @"{""original_text"":""Hello"",""translated_text"":""Hola""}";
        
        // Act
        manager.HandleTranscriptionResponse(json);
        yield return null;

        // Assert
        Assert.AreEqual("Hola", subtitleText.text, 
            "Subtitle should update when translation enabled");
    }

    [UnityTest]
    public IEnumerator MessageReceived_ProcessesOnMainThread()
    {
        // Arrange
        manager.ConnectWebSocket();
        mockWebSocket.TriggerOpen();
        yield return null;
        yield return null;
        
        string json = @"{""original_text"":""Test"",""translated_text"":""Prueba""}";

        // Act - Simulate receiving message
        mockWebSocket.TriggerMessage(json);
        
        // Wait for Update() to process queued action
        yield return null;
        yield return null;

        // Assert
        Assert.AreEqual("Prueba", subtitleText.text, 
            "Message should be processed on main thread");
    }

    [UnityTest]
    public IEnumerator PackageAudioData_IncludesConversationId()
    {
        // Arrange
        byte[] audioData = new byte[] { 1, 2, 3 };
        string conversationId = "test_conversation_123";
        
        // Act
        byte[] result = manager.PackageAudioData(audioData, null, conversationId);
        
        yield return null;

        // Assert
        Assert.Greater(result.Length, audioData.Length, 
            "Packaged data should include metadata");
        
        // Extract metadata
        int metadataLength = System.BitConverter.ToInt32(result, 0);
        byte[] metadataBytes = new byte[metadataLength];
        System.Buffer.BlockCopy(result, 4, metadataBytes, 0, metadataLength);
        string metadata = System.Text.Encoding.UTF8.GetString(metadataBytes);
        
        Assert.IsTrue(metadata.Contains("test_conversation_123"), 
            "Metadata should contain conversation ID");
    }

    [UnityTest]
    public IEnumerator PackageAudioData_IncludesJwtToken()
    {
        // Arrange
        byte[] audioData = new byte[] { 1, 2, 3 };
        string jwtToken = "test.jwt.token";
        
        // Act
        byte[] result = manager.PackageAudioData(audioData, jwtToken);
        
        yield return null;

        // Assert
        int metadataLength = System.BitConverter.ToInt32(result, 0);
        byte[] metadataBytes = new byte[metadataLength];
        System.Buffer.BlockCopy(result, 4, metadataBytes, 0, metadataLength);
        string metadata = System.Text.Encoding.UTF8.GetString(metadataBytes);
        
        Assert.IsTrue(metadata.Contains("test.jwt.token"), 
            "Metadata should contain JWT token");
    }

    [UnityTest]
    public IEnumerator UpdateSubtitle_UpdatesTextComponent()
    {
        // Act
        manager.UpdateSubtitle("Test subtitle");
        yield return null;

        // Assert
        Assert.AreEqual("Test subtitle", subtitleText.text, 
            "Subtitle text should be updated");
    }

    [UnityTest]
    public IEnumerator HandleTranscriptionResponse_LogsDetectedLanguage()
    {
        // Arrange
        string json = @"{
            ""original_text"":""Hello"",
            ""translated_text"":""Hola"",
            ""detected_language"":""en"",
            ""language_probability"":0.95
        }";
        
        // Act
        manager.HandleTranscriptionResponse(json);
        yield return null;

        // Assert - Check that it processes without error
        Assert.AreEqual("Hola", subtitleText.text);
    }
}
