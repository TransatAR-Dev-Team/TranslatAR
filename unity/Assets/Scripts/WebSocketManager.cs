using UnityEngine;
using System;
using System.Text;
using System.Collections.Generic;
using WebSocketSharp;
using TMPro;

[System.Serializable]
public class TranscriptionResponse
{
    public string original_text;
    public string translated_text;
}

public class WebSocketManager : MonoBehaviour
{
    [Header("WebSocket Settings")]
    public string websocketUrl = "ws://localhost:8000/ws";
    public string sourceLanguage = "en";
    public string targetLanguage = "es";

    [Header("UI References")]
    public TextMeshProUGUI subtitleText;

    private WebSocket ws;
    private bool isConnected = false;

    // Queue for main thread execution
    private Queue<Action> mainThreadActions = new Queue<Action>();
    private object queueLock = new object();

    // Singleton pattern
    public static WebSocketManager Instance { get; private set; }

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

    void Start()
    {
        ConnectWebSocket();
    }

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

    void UpdateSubtitle(string text)
    {
        if (subtitleText != null)
        {
            subtitleText.text = text;
        }
    }

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