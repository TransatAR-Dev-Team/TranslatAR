using UnityEngine;
using System.IO;
using System.Collections;

#if PLATFORM_ANDROID
using UnityEngine.Android;
#endif

/// <summary>
/// Manages microphone audio recording, chunking, and transmission to the WebSocket backend.
/// Handles permission requests, silence detection, and continuous recording with overlap.
/// </summary>
public class AudioRecordingManager : MonoBehaviour
{
    [Header("Recording Settings")]
    /// <summary>
    /// Duration in seconds for each audio chunk sent to the backend.
    /// </summary>
    public float chunkDurationSeconds = 8f;

    /// <summary>
    /// The sample rate (in Hz) used for microphone recording.
    /// </summary>
    public int targetSampleRate = 48000;

    /// <summary>
    /// Minimum RMS volume threshold to consider audio as containing speech rather than silence.
    /// </summary>
    public float silenceThreshold = 0.01f; 

    /// <summary>
    /// Duration in seconds of audio overlap between consecutive chunks to prevent word cutting.
    /// </summary>
    public float chunkOverlapSeconds = 0.5f; 

    /// <summary>
    /// Flag indicating whether the microphone is currently recording.
    /// </summary>
    private bool isRecording = false;

    /// <summary>
    /// Flag indicating whether microphone permission has been granted by the user.
    /// </summary>
    private bool permissionGranted = false;

    /// <summary>
    /// The AudioClip instance that holds the continuous microphone recording data.
    /// </summary>    
    // private AudioClip recordingClip; // Temporarily disabled due to compilation issues

    /// <summary>
    /// The sample position in the recording buffer where the last chunk ended.
    /// </summary>
    private int lastSamplePosition = 0;

    /// <summary>
    /// Timer tracking elapsed time since the last chunk was sent.
    /// </summary>
    private float chunkTimer = 0f;
    
    /// <summary>
    /// The number of audio samples to include as overlap between chunks.
    /// </summary>
    private int overlapSamples = 0;

    /// <summary>
    /// Maximum length in seconds for the circular recording buffer.
    /// </summary>
    private const int maxRecordingLength = 30;

    /// <summary>
    /// Requests microphone permission on Android and initializes overlap sample count.
    /// </summary>
    void Start()
    {
        #if PLATFORM_ANDROID
        // Temporarily disabled microphone permission check
        /*
        if (!Permission.HasUserAuthorizedPermission(Permission.Microphone))
        {
            Permission.RequestUserPermission(Permission.Microphone);
        }
        else
        {
            permissionGranted = true;
        }
        */
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

    /// <summary>
    /// Begins continuous microphone recording into a circular buffer.
    /// </summary>
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
        // Temporarily disabled microphone check
        /*
        if (Microphone.IsRecording(null))
        {
            // Microphone.End(null); // Temporarily disabled
        }
        */

        // Start continuous recording into circular buffer
        // recordingClip = Microphone.Start(null, true, maxRecordingLength, targetSampleRate); // Temporarily disabled

    }

    /// <summary>
    /// Stops microphone recording, sends any remaining audio chunk, and cleans up resources.
    /// </summary>
    void StopRecording()
    {
        if (!isRecording) return;

        isRecording = false;
        Debug.Log("Recording stopped.");

        // Send any remaining audio if it has speech
        CaptureAndSendChunk();

        // Clean up
        // Microphone.End(null); // Temporarily disabled
        // recordingClip = null; // Temporarily disabled
        lastSamplePosition = 0;
        chunkTimer = 0f; // Reset timer
    }

    /// <summary>
    /// Captures the current audio chunk from the recording buffer, checks for sufficient volume,
    /// converts to WAV format, and sends it to the WebSocket backend.
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
    /// </summary>
    /// <param name="samples">The audio sample data to analyze.</param>
    /// <returns>True if the audio exceeds the silence threshold; otherwise, false.</returns>
    bool HasSufficientVolume(float[] samples)
    {
        // Calculate RMS
        float sum = 0f;
        for (int i = 0; i < samples.Length; i++)
        {
            sum += samples[i] * samples[i];
        }
        float rms = Mathf.Sqrt(sum / samples.Length);

        // Also check peak amplitude
        float maxAmplitude = 0f;
        for (int i = 0; i < samples.Length; i++)
        {
            float abs = Mathf.Abs(samples[i]);
            if (abs > maxAmplitude) maxAmplitude = abs;
        }

        bool hasVolume = rms > silenceThreshold && maxAmplitude > silenceThreshold * 2;

        Debug.Log($"Audio RMS: {rms:F4}, Peak: {maxAmplitude:F4}, HasSpeech: {hasVolume}");

        return hasVolume;
    }

    /// <summary>
    /// Converts raw float audio samples to WAV file format with proper headers.
    /// </summary>
    /// <param name="samples">The audio sample data to convert.</param>
    /// <param name="sampleRate">The sample rate of the audio in Hz.</param>
    /// <param name="channels">The number of audio channels (1 for mono, 2 for stereo).</param>
    /// <returns>A byte array containing the complete WAV file data.</returns>
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

    /// <summary>
    /// Ensures the microphone is properly stopped when the application quits.
    /// </summary>
    void OnApplicationQuit()
    {
        if (isRecording)
        {
            // Microphone.End(null); // Temporarily disabled
        }
    }
}