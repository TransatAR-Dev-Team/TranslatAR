using UnityEngine;
using System.IO;
using System.Collections;

#if PLATFORM_ANDROID
using UnityEngine.Android;
#endif

public class AudioRecordingManager : MonoBehaviour
{
    [Header("Recording Settings")]
    public float chunkDurationSeconds = 1.5f; // Send chunks every 1.5 seconds
    public int targetSampleRate = 44100; // CD quality for better transcription
    public float silenceThreshold = 0.01f; // Minimum volume to consider as speech (adjust if needed)

    private bool isRecording = false;
    private bool permissionGranted = false;
    private AudioClip recordingClip;
    private int lastSamplePosition = 0;
    private float chunkTimer = 0f;

    private const int maxRecordingLength = 10; // 10 second circular buffer

    void Start()
    {
#if PLATFORM_ANDROID
        if (!Permission.HasUserAuthorizedPermission(Permission.Microphone))
        {
            Permission.RequestUserPermission(Permission.Microphone);
        }
        else
        {
            permissionGranted = true;
        }
#else
        permissionGranted = true;
#endif
    }

    void Update()
    {
#if PLATFORM_ANDROID
        if (!permissionGranted && Permission.HasUserAuthorizedPermission(Permission.Microphone))
        {
            permissionGranted = true;
        }
#endif

        if (!permissionGranted) return;

        // Button input
        bool inputIsActive = Input.GetKey(KeyCode.JoystickButton0) || Input.GetKey(KeyCode.B);

        // Start recording
        if (!isRecording && inputIsActive)
        {
            StartRecording();
        }
        // Stop recording
        else if (isRecording && !inputIsActive)
        {
            StopRecording();
        }

        // While recording, capture and send chunks periodically
        if (isRecording)
        {
            chunkTimer += Time.deltaTime;
            if (chunkTimer >= chunkDurationSeconds)
            {
                CaptureAndSendChunk();
                chunkTimer = 0f;
            }
        }
    }

    void StartRecording()
    {
        if (isRecording) return;
        if (WebSocketManager.Instance == null || !WebSocketManager.Instance.IsConnected)
        {
            Debug.LogWarning("WebSocket not connected. Cannot start recording.");
            return;
        }

        isRecording = true;
        lastSamplePosition = 0;
        chunkTimer = 0f;

        Debug.Log("Recording started...");

        // Start fresh - end any previous recording
        if (Microphone.IsRecording(null))
        {
            Microphone.End(null);
        }

        // Start continuous recording into circular buffer
        recordingClip = Microphone.Start(null, true, maxRecordingLength, targetSampleRate);

        // Wait for microphone to start
        StartCoroutine(WaitForMicrophoneStart());
    }

    IEnumerator WaitForMicrophoneStart()
    {
        // Wait until microphone starts recording
        while (Microphone.GetPosition(null) <= 0)
        {
            yield return null;
        }
        Debug.Log("Microphone active, sending chunks...");
    }

    void StopRecording()
    {
        if (!isRecording) return;

        isRecording = false;
        Debug.Log("Recording stopped.");

        // Send any remaining audio if it has speech
        CaptureAndSendChunk();

        // Clean up
        Microphone.End(null);
        recordingClip = null;
        lastSamplePosition = 0;
        chunkTimer = 0f; // Reset timer
    }

    void CaptureAndSendChunk()
    {
        if (recordingClip == null) return;

        int currentPosition = Microphone.GetPosition(null);

        // Handle wraparound in circular buffer
        if (currentPosition < lastSamplePosition)
        {
            currentPosition += recordingClip.samples;
        }

        int samplesAvailable = currentPosition - lastSamplePosition;

        // Skip if not enough data
        if (samplesAvailable < targetSampleRate * 0.5f) // at least 0.5 seconds
        {
            return;
        }

        // Extract audio chunk
        float[] samples = new float[samplesAvailable * recordingClip.channels];
        recordingClip.GetData(samples, lastSamplePosition % recordingClip.samples);

        // Check if chunk contains actual speech (not just silence)
        if (!HasSufficientVolume(samples))
        {
            Debug.Log("Skipping silent chunk");
            lastSamplePosition = currentPosition % recordingClip.samples;
            return;
        }

        // Convert to 16-bit PCM WAV
        byte[] wavData = ConvertSamplesToWav(samples, targetSampleRate, recordingClip.channels);

        // Send via WebSocket
        if (WebSocketManager.Instance != null)
        {
            WebSocketManager.Instance.SendAudioChunk(wavData);
        }

        // Update position
        lastSamplePosition = currentPosition % recordingClip.samples;
    }

    bool HasSufficientVolume(float[] samples)
    {
        // Calculate RMS (Root Mean Square) volume
        float sum = 0f;
        for (int i = 0; i < samples.Length; i++)
        {
            sum += samples[i] * samples[i];
        }
        float rms = Mathf.Sqrt(sum / samples.Length);

        Debug.Log($"Audio RMS: {rms:F4} (threshold: {silenceThreshold:F4})");

        return rms > silenceThreshold;
    }

    public static byte[] ConvertSamplesToWav(float[] samples, int sampleRate, int channels)
    {
        using (var memoryStream = new MemoryStream())
        {
            using (var writer = new BinaryWriter(memoryStream))
            {
                // WAV header
                writer.Write(System.Text.Encoding.UTF8.GetBytes("RIFF"));
                writer.Write(0); // Placeholder for file size
                writer.Write(System.Text.Encoding.UTF8.GetBytes("WAVE"));
                writer.Write(System.Text.Encoding.UTF8.GetBytes("fmt "));
                writer.Write(16); // PCM chunk size
                writer.Write((ushort)1); // Audio format (PCM)
                writer.Write((ushort)channels);
                writer.Write(sampleRate);
                writer.Write(sampleRate * channels * 2); // Byte rate
                writer.Write((ushort)(channels * 2)); // Block align
                writer.Write((ushort)16); // Bits per sample

                writer.Write(System.Text.Encoding.UTF8.GetBytes("data"));
                writer.Write(0); // Placeholder for data size

                // Write audio data
                foreach (float sample in samples)
                {
                    short intSample = (short)(Mathf.Clamp(sample, -1f, 1f) * short.MaxValue);
                    writer.Write(intSample);
                }

                // Fill in size placeholders
                long fileSize = memoryStream.Length;
                writer.Seek(4, SeekOrigin.Begin);
                writer.Write((int)(fileSize - 8));
                writer.Seek(40, SeekOrigin.Begin);
                writer.Write((int)(fileSize - 44));
            }
            return memoryStream.ToArray();
        }
    }

    void OnApplicationQuit()
    {
        if (isRecording)
        {
            Microphone.End(null);
        }
    }
}