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
    private WebSocket ws;
    /// <summary>
    /// A flag indicating whether the websocket endpoint is connected.
    /// </summary>
    private bool isConnected = false;

    // Queue for main thread execution
    private Queue<Action> mainThreadActions = new Queue<Action>();
    private object queueLock = new object();

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
        }
        else
        {
            Destroy(gameObject);
        }
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
    void ConnectWebSocket()
    {
        try
        {
            ws = new WebSocket(websocketUrl);

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
        catch (Exception e)
        {
            Debug.LogError("Failed to connect WebSocket: " + e.Message);
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
            // Create metadata JSON
            string metadata = JsonUtility.ToJson(new MetadataPayload
            {
                source_lang = sourceLanguage,
                target_lang = targetLanguage,
                sample_rate = 44100,
                channels = 1
            });

            byte[] metadataBytes = Encoding.UTF8.GetBytes(metadata);
            byte[] metadataLength = BitConverter.GetBytes(metadataBytes.Length);

            // Combine: [4 bytes length][metadata][audio]
            byte[] fullMessage = new byte[4 + metadataBytes.Length + audioData.Length];
            Buffer.BlockCopy(metadataLength, 0, fullMessage, 0, 4);
            Buffer.BlockCopy(metadataBytes, 0, fullMessage, 4, metadataBytes.Length);
            Buffer.BlockCopy(audioData, 0, fullMessage, 4 + metadataBytes.Length, audioData.Length);

            ws.Send(fullMessage);
            Debug.Log($"Sent audio chunk: {audioData.Length} bytes");
        }
        catch (Exception e)
        {
            Debug.LogError("Error sending audio: " + e.Message);
        }
    }

    /// <summary>
    /// Parses the JSON transcription response from the backend and updates the subtitle display.
    /// Prioritizes translated text over original text if both are present.
    /// </summary>
    /// <param name="json">The JSON string containing transcription results.</param>
    void HandleTranscriptionResponse(string json)
    {
        try
        {
            TranscriptionResponse response = JsonUtility.FromJson<TranscriptionResponse>(json);

            if (!string.IsNullOrEmpty(response.translated_text))
            {
                UpdateSubtitle(response.translated_text);
            }
            else if (!string.IsNullOrEmpty(response.original_text))
            {
                UpdateSubtitle(response.original_text);
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
    void UpdateSubtitle(string text)
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
}