using UnityEngine;
using System;
using System.Text;
using System.Collections.Generic;
using WebSocketSharp;
using TMPro;

/// <summary>
/// Represents the expected JSON response structure from the backend's /process-audio endpoint.
/// </summary>
[System.Serializable]
public class TranscriptionResponse
{
    public string original_text;
    public string translated_text;
    public string conversation_id;
}

public class WebSocketManager : MonoBehaviour
{
    [Header("WebSocket Settings")]
    /// <summary>
    /// The URL of the websocket endpoint responsible for processing audio.
    /// </summary>
    public string websocketUrl = "ws://localhost:8000/ws";

    /// <summary>
    /// The language code (e.g., "en" for English) of the audio being recorded.
    /// </summary>
    public string sourceLanguage = "en";

    /// <summary>
    /// The language code (e.g., "es" for Spanish) into which the audio should be translated.
    /// </summary>
    public string targetLanguage = "es";

    [Header("UI References")]
    /// <summary>
    /// Reference to the TextMeshProUGUI component used to display subtitles to the user.
    /// </summary>
    public TextMeshProUGUI subtitleText;

    /// <summary>
    /// The WebSocket connection instance used to communicate with the backend server.
    /// </summary>
    private IWebSocketClient ws;

    /// <summary>
    /// A flag indicating whether the websocket endpoint is connected.
    /// </summary>
    private bool isConnected = false;

    // Queue for main thread execution
    private Queue<Action> mainThreadActions = new Queue<Action>();
    private object queueLock = new object();

    // Factory for creating WebSocket clients (allows injection for testing)
    private Func<string, IWebSocketClient> webSocketFactory;

    // Singleton pattern
    public static WebSocketManager Instance { get; private set; }

    /// <summary>
    /// Initializes the singleton instance and prevents duplicate instances across scenes.
    /// </summary>
    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            Initialize(); // Use default factory for production
        }
        else
        {
            Destroy(gameObject);
        }
    }

    /// <summary>
    /// Initializes the WebSocket factory. Can be called with a custom factory for testing.
    /// </summary>
    /// <param name="factory">Optional factory function for creating IWebSocketClient instances.</param>
    public void Initialize(Func<string, IWebSocketClient> factory = null)
    {
        webSocketFactory = factory ?? ((url) => new WebSocketClientAdapter(url));
    }

    /// <summary>
    /// Initiates the WebSocket connection when the component starts.
    /// </summary>
    void Start()
    {
        ConnectWebSocket();
    }

    /// <summary>
    /// Processes queued actions from WebSocket callbacks on the main thread each frame.
    /// </summary>
    void Update()
    {
        // Process queued actions on main thread
        lock (queueLock)
        {
            while (mainThreadActions.Count > 0)
            {
                mainThreadActions.Dequeue()?.Invoke();
            }
        }
    }

    /// <summary>
    /// Establishes the WebSocket connection and configures event handlers for open, message, error, and close events.
    /// </summary>
    public void ConnectWebSocket()
    {
        try
        {
            Debug.Log("Attempting to connect to WebSocket at: " + websocketUrl);
            ws = webSocketFactory(websocketUrl);

            ws.OnOpen += (sender, e) =>
            {
                Debug.Log("WebSocket connected!");
                isConnected = true;

                // Queue UI update for main thread
                lock (queueLock)
                {
                    mainThreadActions.Enqueue(() =>
                        UpdateSubtitle("Connected. Press and hold (B) button to record."));
                }
            };

            ws.OnMessage += (sender, e) =>
            {
                if (e.IsText)
                {
                    string message = e.Data;
                    Debug.Log("Received: " + message);

                    // Queue for main thread
                    lock (queueLock)
                    {
                        mainThreadActions.Enqueue(() => HandleTranscriptionResponse(message));
                    }
                }
            };

            ws.OnError += (sender, e) =>
            {
                Debug.LogError("WebSocket Error: " + e.Message);

                // Queue UI update for main thread
                lock (queueLock)
                {
                    mainThreadActions.Enqueue(() => UpdateSubtitle("Connection error."));
                }
            };

            ws.OnClose += (sender, e) =>
            {
                Debug.Log("WebSocket closed!");
                isConnected = false;

                // Queue UI update for main thread
                lock (queueLock)
                {
                    mainThreadActions.Enqueue(() => UpdateSubtitle("Disconnected."));
                }
            };

            ws.Connect();
        }
        catch (System.Exception e)
        {
            Debug.LogError($"[WebSocketManager] FATAL: Failed to initiate WebSocket connection: {e.Message}");
            isConnected = false;
            UpdateSubtitle("Failed to connect to server.");
        }
    }

    /// <summary>
    /// Sends an audio chunk to the backend with language and format metadata.
    /// The data is packaged as: [4-byte length][JSON metadata][raw audio bytes].
    /// </summary>
    /// <param name="audioData">The raw audio data bytes to transmit.</param>
    public void SendAudioChunk(byte[] audioData)
    {
        if (!isConnected || ws == null || ws.ReadyState != WebSocketState.Open)
        {
            Debug.LogWarning("WebSocket not connected. Cannot send audio.");
            return;
        }

        try
        {
            string jwtToken = AuthManager.Instance?.CurrentJwt;
            byte[] packagedData = PackageAudioData(audioData, jwtToken);
            ws.Send(packagedData);
            Debug.Log($"Sent audio chunk: {audioData.Length} bytes (authenticated: {!string.IsNullOrEmpty(jwtToken)})");
        }
        catch (Exception e)
        {
            Debug.LogError("Error sending audio: " + e.Message);
        }
    }

    /// <summary>
    /// Packages audio data with metadata for transmission.
    /// Returns: [4-byte length][JSON metadata][raw audio bytes]
    /// </summary>
    /// <param name="audioData">The raw audio data bytes.</param>
    /// <returns>The fully packaged byte array ready for transmission.</returns>
    public byte[] PackageAudioData(byte[] audioData, string jwtToken = null)
    {
        // Create metadata JSON
        string metadata = JsonUtility.ToJson(new MetadataPayload
        {
            source_lang = sourceLanguage,
            target_lang = targetLanguage,
            sample_rate = AudioSettings.outputSampleRate,
            channels = 1,
            jwt_token = jwtToken
        });

        byte[] metadataBytes = Encoding.UTF8.GetBytes(metadata);
        byte[] metadataLength = BitConverter.GetBytes(metadataBytes.Length);

        // Combine: [4 bytes length][metadata][audio]
        byte[] fullMessage = new byte[4 + metadataBytes.Length + audioData.Length];
        Buffer.BlockCopy(metadataLength, 0, fullMessage, 0, 4);
        Buffer.BlockCopy(metadataBytes, 0, fullMessage, 4, metadataBytes.Length);
        Buffer.BlockCopy(audioData, 0, fullMessage, 4 + metadataBytes.Length, audioData.Length);

        return fullMessage;
    }

    /// <summary>
    /// Parses the JSON transcription response from the backend and updates the subtitle display.
    /// Prioritizes translated text over original text if both are present.
    /// Also adds the translation to the conversation list UI.
    /// </summary>
    /// <param name="json">The JSON string containing transcription results.</param>
    public void HandleTranscriptionResponse(string json)
    {
        try
        {
            TranscriptionResponse response = JsonUtility.FromJson<TranscriptionResponse>(json);

            if (!string.IsNullOrEmpty(response.translated_text))
            {
                // Update subtitle
                UpdateSubtitle(response.translated_text);

                // Add translation to conversation list
                if (ConversationListUI.Instance != null)
                {
                    ConversationListUI.Instance.AddTranslation(
                        response.original_text,
                        response.translated_text,
                        response.conversation_id
                    );
                }
            }
            else if (!string.IsNullOrEmpty(response.original_text))
            {
                UpdateSubtitle(response.original_text);

                // Add to list even if only original text is available
                if (ConversationListUI.Instance != null)
                {
                    ConversationListUI.Instance.AddTranslation(
                        response.original_text,
                        "",
                        response.conversation_id
                    );
                }
            }
        }
        catch (Exception e)
        {
            Debug.LogError("Error parsing transcription: " + e.Message);
        }
    }

    /// <summary>
    /// Updates the subtitle UI text component with the provided text.
    /// </summary>
    /// <param name="text">The text to display in the subtitle area.</param>
    public void UpdateSubtitle(string text)
    {
        if (subtitleText != null)
        {
            subtitleText.text = text;
        }
    }

    /// <summary>
    /// Closes the WebSocket connection gracefully when the application quits.
    /// </summary>
    void OnApplicationQuit()
    {
        if (ws != null && ws.ReadyState == WebSocketState.Open)
        {
            ws.Close();
        }
    }

    public bool IsConnected => isConnected;
}

[System.Serializable]
public class MetadataPayload
{
    public string source_lang;
    public string target_lang;
    public int sample_rate;
    public int channels;
    public string jwt_token;
}
