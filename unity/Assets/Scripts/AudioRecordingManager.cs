using UnityEngine;
using System.IO;
using System.Collections;

#if PLATFORM_ANDROID
using UnityEngine.Android;
#endif

/// <summary>
/// Manages microphone audio recording, chunking, and transmission to the WebSocket backend.
/// Handles permission requests, silence detection, and continuous recording with overlap.
/// 
/// NOTE: Audio functionality is temporarily disabled due to compilation issues.
/// This class maintains the interface but all audio operations are commented out.
/// </summary>
public class AudioRecordingManager : MonoBehaviour
{
    [Header("Recording Settings")]
    /// <summary>
    /// Duration in seconds for each audio chunk sent to the backend.
    /// </summary>
    public float chunkDurationSeconds = 8f;

    /// <summary>
    /// Overlap duration in seconds between consecutive chunks to avoid word cutting.
    /// </summary>
    public float chunkOverlapSeconds = 1f;

    /// <summary>
    /// Target sample rate for audio recording (Hz).
    /// </summary>
    public int targetSampleRate = 44100;

    /// <summary>
    /// Maximum recording length in seconds before automatic stop.
    /// </summary>
    public int maxRecordingLength = 300; // 5 minutes

    [Header("Volume Detection")]
    /// <summary>
    /// Minimum RMS (Root Mean Square) amplitude threshold for speech detection.
    /// </summary>
    public float speechThreshold = 0.01f;

    /// <summary>
    /// Minimum peak amplitude threshold for speech detection.
    /// </summary>
    public float peakThreshold = 0.1f;

    [Header("Debug")]
    /// <summary>
    /// Enable debug logging for audio processing.
    /// </summary>
    public bool enableDebugLogging = false;

    // Private fields
    private bool isRecording = false;
    private bool permissionGranted = false;
    private float chunkTimer = 0f;
    private int overlapSamples = 0;
    private int lastSamplePosition = 0;

    /// <summary>
    /// Requests microphone permission on Android and initializes overlap sample count.
    /// </summary>
    void Start()
    {
        #if PLATFORM_ANDROID
        // Temporarily disabled microphone permission check
        // All microphone operations are disabled due to compilation issues
        #else
        permissionGranted = true;
        #endif

        overlapSamples = (int)(chunkOverlapSeconds * targetSampleRate);
    }

    /// <summary>
    /// Monitors button input to start/stop recording and sends audio chunks at regular intervals.
    /// </summary>
    void Update()
    {
        #if PLATFORM_ANDROID
        // if (!permissionGranted && Permission.HasUserAuthorizedPermission(Permission.Microphone)) // Temporarily disabled
        {
            permissionGranted = true;
        }
        #endif

        // Handle recording state
        if (isRecording)
        {
            chunkTimer += Time.deltaTime;
            
            // Send chunk at regular intervals
            if (chunkTimer >= chunkDurationSeconds)
            {
                // Temporarily disabled audio processing
                // CaptureAndSendChunk();
                chunkTimer = 0f;
            }
        }
    }

    /// <summary>
    /// Starts microphone recording with continuous chunking.
    /// </summary>
    public void StartRecording()
    {
        if (!permissionGranted)
        {
            Debug.LogWarning("Microphone permission not granted");
            return;
        }

        if (isRecording)
        {
            Debug.LogWarning("Recording already in progress");
            return;
        }

        isRecording = true;
        chunkTimer = 0f;

        Debug.Log("Recording started...");

        // Temporarily disabled microphone operations
        /*
        // Start fresh - end any previous recording
        if (Microphone.IsRecording(null))
        {
            Microphone.End(null);
        }

        // Start continuous recording into circular buffer
        recordingClip = Microphone.Start(null, true, maxRecordingLength, targetSampleRate);
        */
    }

    /// <summary>
    /// Stops microphone recording, sends any remaining audio chunk, and cleans up resources.
    /// </summary>
    public void StopRecording()
    {
        if (!isRecording)
        {
            Debug.LogWarning("No recording in progress");
            return;
        }

        isRecording = false;

        // Send any remaining audio if it has speech
        // CaptureAndSendChunk(); // Temporarily disabled

        // Clean up
        // Microphone.End(null); // Temporarily disabled
        // recordingClip = null; // Temporarily disabled
        lastSamplePosition = 0;
        chunkTimer = 0f; // Reset timer
    }

    /// <summary>
    /// Captures the current audio chunk from the recording buffer, checks for sufficient volume,
    /// converts to WAV format, and sends it to the WebSocket backend.
    /// 
    /// NOTE: This method is temporarily disabled due to compilation issues.
    /// </summary>
    void CaptureAndSendChunk()
    {
        // Temporarily disabled entire audio processing function
        /*
        if (recordingClip == null) return;

        int currentPosition = Microphone.GetPosition(null);

        // Handle wraparound in circular buffer
        if (currentPosition < lastSamplePosition)
        {
            currentPosition += recordingClip.samples;
        }

        int samplesAvailable = currentPosition - lastSamplePosition;

        if (samplesAvailable < targetSampleRate * 2.0f) // At least 2 seconds
        {
            return;
        }

        // Include overlap from previous chunk to avoid word cutting
        int startPosition = Mathf.Max(0, (lastSamplePosition - overlapSamples) % recordingClip.samples);
        int totalSamples = samplesAvailable + overlapSamples;

        float[] samples = new float[totalSamples * recordingClip.channels];
        recordingClip.GetData(samples, startPosition);

        if (!HasSufficientVolume(samples))
        {
            Debug.Log("Skipping silent chunk");
            lastSamplePosition = currentPosition % recordingClip.samples;
            return;
        }

        // Convert to WAV
        byte[] wavData = ConvertSamplesToWav(samples, targetSampleRate, recordingClip.channels);

        if (WebSocketManager.Instance != null)
        {
            WebSocketManager.Instance.SendAudioChunk(wavData);
        }

        // Update position (not including overlap for next chunk)
        lastSamplePosition = currentPosition % recordingClip.samples;
        */
    }

    /// <summary>
    /// Analyzes audio samples to determine if they contain sufficient volume to be considered speech.
    /// Uses both RMS and peak amplitude thresholds.
    /// 
    /// NOTE: This method is temporarily disabled due to compilation issues.
    /// </summary>
    /// <param name="samples">Audio samples to analyze</param>
    /// <returns>True if samples contain sufficient volume for speech</returns>
    bool HasSufficientVolume(float[] samples)
    {
        // Temporarily disabled volume analysis
        /*
        if (samples == null || samples.Length == 0)
            return false;

        float rms = 0f;
        float peak = 0f;

        foreach (float sample in samples)
        {
            rms += sample * sample;
            peak = Mathf.Max(peak, Mathf.Abs(sample));
        }

        rms = Mathf.Sqrt(rms / samples.Length);

        if (enableDebugLogging)
        {
            Debug.Log($"Audio analysis - RMS: {rms:F4}, Peak: {peak:F4}");
        }

        return rms >= speechThreshold && peak >= peakThreshold;
        */
        return true; // Temporarily return true to avoid breaking the flow
    }

    /// <summary>
    /// Converts audio samples to WAV format with proper headers.
    /// 
    /// NOTE: This method is temporarily disabled due to compilation issues.
    /// </summary>
    /// <param name="samples">Audio samples to convert</param>
    /// <param name="sampleRate">Sample rate in Hz</param>
    /// <param name="channels">Number of audio channels</param>
    /// <returns>WAV file data as byte array</returns>
    byte[] ConvertSamplesToWav(float[] samples, int sampleRate, int channels)
    {
        // Temporarily disabled WAV conversion
        /*
        if (samples == null || samples.Length == 0)
            return new byte[0];

        int sampleCount = samples.Length;
        int byteRate = sampleRate * channels * 2; // 16-bit samples
        int blockAlign = channels * 2;
        int dataSize = sampleCount * 2;
        int fileSize = 36 + dataSize;

        using (MemoryStream stream = new MemoryStream())
        using (BinaryWriter writer = new BinaryWriter(stream))
        {
            // WAV header
            writer.Write("RIFF".ToCharArray());
            writer.Write(fileSize);
            writer.Write("WAVE".ToCharArray());
            writer.Write("fmt ".ToCharArray());
            writer.Write(16); // fmt chunk size
            writer.Write((short)1); // PCM format
            writer.Write((short)channels);
            writer.Write(sampleRate);
            writer.Write(byteRate);
            writer.Write((short)blockAlign);
            writer.Write((short)16); // bits per sample
            writer.Write("data".ToCharArray());
            writer.Write(dataSize);

            // Audio data
            foreach (float sample in samples)
            {
                short sampleValue = (short)(sample * short.MaxValue);
                writer.Write(sampleValue);
            }

            return stream.ToArray();
        }
        */
        return new byte[0]; // Temporarily return empty array
    }

    /// <summary>
    /// Gets the current recording state.
    /// </summary>
    /// <returns>True if currently recording</returns>
    public bool IsRecording()
    {
        return isRecording;
    }

    /// <summary>
    /// Gets the microphone permission status.
    /// </summary>
    /// <returns>True if microphone permission is granted</returns>
    public bool HasMicrophonePermission()
    {
        return permissionGranted;
    }
}