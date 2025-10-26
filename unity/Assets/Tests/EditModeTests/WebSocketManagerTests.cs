using NUnit.Framework;
using UnityEngine;
using System;
using System.Text;

/// <summary>
/// Edit Mode tests for WebSocketManager core functionality.
/// </summary>
public class WebSocketManagerTests
{
    private GameObject testGameObject;
    private WebSocketManager manager;
    private MockWebSocketClient mockWebSocket;

    [SetUp]
    public void SetUp()
    {
        testGameObject = new GameObject("WebSocketManagerTest");
        manager = testGameObject.AddComponent<WebSocketManager>();
        mockWebSocket = new MockWebSocketClient();
        manager.Initialize((url) => mockWebSocket);
        manager.sourceLanguage = "en";
        manager.targetLanguage = "es";
    }

    [TearDown]
    public void TearDown()
    {
        if (testGameObject != null)
        {
            UnityEngine.Object.DestroyImmediate(testGameObject);
        }
    }

    [Test]
    public void HandleTranscriptionResponse_PrioritizesTranslatedText()
    {
        // Arrange
        string json = @"{""original_text"":""Hello"",""translated_text"":""Hola""}";
        var subtitleGO = new GameObject("Subtitle");
        var subtitleText = subtitleGO.AddComponent<TMPro.TextMeshProUGUI>();
        manager.subtitleText = subtitleText;

        // Act
        manager.HandleTranscriptionResponse(json);

        // Assert
        Assert.AreEqual("Hola", subtitleText.text);
        UnityEngine.Object.DestroyImmediate(subtitleGO);
    }

    [Test]
    public void PackageAudioData_HasCorrectStructure()
    {
        // Arrange
        byte[] audioData = new byte[] { 1, 2, 3, 4, 5 };
        
        // Act
        byte[] result = manager.PackageAudioData(audioData);

        // Assert - Verify: [4-byte length][metadata][audio]
        int metadataLength = BitConverter.ToInt32(result, 0);
        int expectedLength = 4 + metadataLength + audioData.Length;
        Assert.AreEqual(expectedLength, result.Length);
        
        // Verify metadata contains required fields
        byte[] metadataBytes = new byte[metadataLength];
        Buffer.BlockCopy(result, 4, metadataBytes, 0, metadataLength);
        string metadata = Encoding.UTF8.GetString(metadataBytes);
        Assert.IsTrue(metadata.Contains("source_lang"));
        Assert.IsTrue(metadata.Contains("target_lang"));
    }

    [Test]
    public void SendAudioChunk_WhenConnected_SendsPackagedData()
    {
        // Arrange
        manager.ConnectWebSocket();
        mockWebSocket.TriggerOpen();
        byte[] audioData = new byte[] { 1, 2, 3 };

        // Act
        manager.SendAudioChunk(audioData);

        // Assert
        Assert.AreEqual(1, mockWebSocket.SendCallCount);
        Assert.IsNotNull(mockWebSocket.LastSentData);
        Assert.Greater(mockWebSocket.LastSentData.Length, audioData.Length);
    }

    [Test]
    public void ConnectWebSocket_CallsConnect()
    {
        // Act
        manager.ConnectWebSocket();

        // Assert
        Assert.IsTrue(mockWebSocket.ConnectCalled);
    }
}