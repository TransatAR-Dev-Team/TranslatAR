using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using System.IO;
using System;
using TMPro;

// permissions namespace, can't run on non-Android platforms
#if PLATFORM_ANDROID
using UnityEngine.Android;
#endif


/// <summary>
/// Represents the expected JSON response structure from the backend's /process-audio endpoint.
/// </summary>
[System.Serializable]
public class TranslationPipelineResponse
{
    /// <summary>
    /// The original text transcribed from the audio.
    /// </summary>
    public string original_text;
    /// <summary>
    /// The translated version of <see cref="original_text"/>.
    /// </summary>
    public string translated_text;
}

/// <summary>
/// Handles communication with a backend service for audio processing (e.g., transcription and translation).
/// Manages microphone input, sends audio data, and displays the response.
/// </summary>
public class BackendConnector : MonoBehaviour
{
    /// <summary>
    /// The URL of the backend endpoint responsible for processing audio.
    /// </summary>
    private const string backendUrl = "http://localhost:8000/api/process-audio";

    /// <summary>
    /// Reference to the TextMeshProUGUI component used to display subtitles to the user.
    /// </summary>
    [Header("UI References")]
    public TextMeshProUGUI subtitleText;

    /// <summary>
    /// An AudioClip used for testing purposes, allowing audio processing without live microphone input.
    /// </summary>
    [Header("Translation Settings")]
    public AudioClip testAudioClip;

    /// <summary>
    /// The language code (e.g., "en" for English) of the audio being recorded.
    /// </summary>
    public string sourceLanguage = "en";

    /// <summary>
    /// The language code (e.g., "es" for Spanish) into which the audio should be translated.
    /// </summary>
    public string targetLanguage = "es";

    // microphone handling

    /// <summary>
    /// A flag indicating whether the microphone is currently recording.
    /// </summary>
    private bool isRecording = false;

    /// <summary>
    /// A flag indicating whether microphone permission has been granted by the user.
    /// </summary>
    private bool permissionGranted = false;

    /// <summary>
    /// The AudioClip object that stores the currently recorded audio.
    /// </summary>
    private AudioClip recordedClip;

    /// <summary>
    /// The maximum duration, in seconds, for a single audio recording.
    /// </summary>
    private const int maxRecordingSeconds = 15;

    /// <summary>
    /// The sample rate (samples per second, or Hz) used for microphone recording.
    /// </summary>
    private const int sampleRate = 44100;


    /// <summary>
    /// Called when the script instance is being loaded.
    /// Initializes UI references and requests microphone permissions on Android.
    /// </summary>
    void Start()
    {
        if (subtitleText == null)
        {
            Debug.LogError("SubtitleText component is not assigned in the Inspector.");
            return;
        }

        // request microphone permission on Android
        #if PLATFORM_ANDROID
        if (!Permission.HasUserAuthorizedPermission(Permission.Microphone))
        {
            subtitleText.text = "Requesting microphone permission...";
            Permission.RequestUserPermission(Permission.Microphone);
        }
        else
        {
            permissionGranted = true;
        }
        #else
        // non-Android platforms (like Unity Editor), assume permission is granted.
        permissionGranted = true;
        #endif

        if (permissionGranted)
        {
            subtitleText.text = "Press and hold (B) button to record.";
        }
    }

    /// <summary>
    /// Called once per frame.
    /// Monitors microphone permission status and handles user input for starting and stopping recording.
    /// </summary>
    void Update()
    {
        #if PLATFORM_ANDROID
        if (!permissionGranted && Permission.HasUserAuthorizedPermission(Permission.Microphone))
        {
            permissionGranted = true;
            subtitleText.text = "Permission granted. Press controller trigger/button to record.";
        }
        #endif

        if (!permissionGranted) return;

        // controller button (A) is bound to (B) in simulator
        bool inputIsActive = Input.GetKey(KeyCode.JoystickButton0) || Input.GetKey(KeyCode.B);

        // transition from IDLE to RECORDING
        // start recording if button held down and not already
        if (!isRecording && inputIsActive)
        {
            StartRecording();
        }

        // transition from RECORDING to IDLE
        // stop recording if button not held down and recording
        else if (isRecording && !inputIsActive)
        {
            StopRecordingAndProcess();
        }
    }

    /// <summary>
    /// Initiates audio recording from the default microphone.
    /// Sets the UI text to indicate recording is in progress.
    /// </summary>
    void StartRecording()
    {
        if (isRecording) return;

        isRecording = true;
        subtitleText.text = "Recording...";
        Debug.Log("Recording started...");
        // start recording from the default microphone
        recordedClip = Microphone.Start(null, false, maxRecordingSeconds, sampleRate);
    }

    /// <summary>
    /// Stops the current audio recording and initiates the process of sending the recorded audio to the backend.
    /// Updates the UI to indicate processing.
    /// </summary>
    void StopRecordingAndProcess()
    {
        if (!isRecording) return;

        isRecording = false;
        subtitleText.text = "Processing audio...";
        Debug.Log("Recording stopped. Processing...");
        Microphone.End(null); // stop recording

        if (recordedClip != null)
        {
            // pass recorded clip to the coroutine
            StartCoroutine(ProcessAudioCoroutine(recordedClip));
        }
        else
        {
            subtitleText.text = "Error: Failed to record audio.";
            Debug.LogError("Recorded clip is null.");
        }
    }

    /// <summary>
    /// Coroutine to handle the asynchronous processing of an AudioClip.
    /// Converts the audio to WAV, sends it to the backend via a UnityWebRequest POST request,
    /// and processes the JSON response.
    /// </summary>
    /// <param name="audioClipToProcess">The AudioClip containing the recorded audio data to be sent.</param>
    /// <returns>An IEnumerator for the coroutine execution.</returns>
    IEnumerator ProcessAudioCoroutine(AudioClip audioClipToProcess)
    {
        var form = new System.Collections.Generic.List<IMultipartFormSection>();

        // convert the AudioClip to a WAV byte array
        byte[] audioData = ConvertAudioClipToWav(audioClipToProcess);
        if (audioData == null)
        {
            subtitleText.text = "Error: Failed to convert AudioClip.";
            yield break;
        }

        form.Add(new MultipartFormFileSection("audio_file", audioData, "recording.wav", "audio/wav"));
        form.Add(new MultipartFormDataSection("source_lang", sourceLanguage));
        form.Add(new MultipartFormDataSection("target_lang", targetLanguage));

        // Create and send the POST request
        using (UnityWebRequest webRequest = UnityWebRequest.Post(backendUrl, form))
        {
            yield return webRequest.SendWebRequest();

            switch (webRequest.result)
            {
                // fuck up path
                case UnityWebRequest.Result.ConnectionError:
                case UnityWebRequest.Result.DataProcessingError:
                case UnityWebRequest.Result.ProtocolError:
                    Debug.LogError("Error: " + webRequest.error);
                    // log the response from the server, it might have a useful FastAPI error message
                    Debug.LogError("Response: " + webRequest.downloadHandler.text);
                    subtitleText.text = "Error: Could not connect to backend.";
                    break;

                // success path
                case UnityWebRequest.Result.Success:
                    string jsonResponse = webRequest.downloadHandler.text;
                    Debug.Log("Received from backend: " + jsonResponse);

                    // parse json
                    TranslationPipelineResponse response = JsonUtility.FromJson<TranslationPipelineResponse>(jsonResponse);
                    subtitleText.text = response.translated_text;
                    // after a successful translation, reset the text
                    Invoke(nameof(ResetIdleText), 5.0f); // after 5 seconds
                    break;
            }
        }
    }

    /// <summary>
    /// Resets the subtitle text to the idle recording prompt, but only if not currently recording.
    /// </summary>
    void ResetIdleText()
    {
        if (!isRecording)
        {
            subtitleText.text = "Press and hold Spacebar or (A) button to record.";
        }
    }

    /// <summary>
    /// Converts a Unity <see cref="AudioClip"/> into a standard WAV format byte array.
    /// This is necessary for sending audio data to external services.
    /// </summary>
    /// <param name="clip">The AudioClip to convert.</param>
    /// <returns>
    /// A byte array representing the AudioClip in WAV format, or null if the input clip is null.
    /// </returns>
    public static byte[] ConvertAudioClipToWav(AudioClip clip)
    {
        if (clip == null) return null;

        using (var memoryStream = new MemoryStream())
        {
            using (var writer = new BinaryWriter(memoryStream))
            {
                // --- Write WAV header ---
                writer.Write(System.Text.Encoding.UTF8.GetBytes("RIFF")); // Chunk ID
                writer.Write(0); // Placeholder for file size (will be updated later)
                writer.Write(System.Text.Encoding.UTF8.GetBytes("WAVE")); // Format
                writer.Write(System.Text.Encoding.UTF8.GetBytes("fmt ")); // Subchunk1 ID
                writer.Write(16); // Subchunk1 size (16 for PCM)
                writer.Write((ushort)1); // Audio format (1 for PCM)
                ushort numChannels = (ushort)clip.channels;
                writer.Write(numChannels); // Number of channels
                uint sampleRate = (uint)clip.frequency;
                writer.Write(sampleRate); // Sample rate
                writer.Write(sampleRate * numChannels * 2); // Byte rate (SampleRate * NumChannels * BytesPerSample)
                writer.Write((ushort)(numChannels * 2)); // Block align (NumChannels * BytesPerSample)
                writer.Write((ushort)16); // Bits per sample (16-bit PCM)

                writer.Write(System.Text.Encoding.UTF8.GetBytes("data")); // Subchunk2 ID
                writer.Write(0); // Placeholder for data size (will be updated later)

                // --- Write Audio data ---
                float[] samples = new float[clip.samples * clip.channels];
                clip.GetData(samples, 0); // Get float audio data from the AudioClip.

                for (int i = 0; i < samples.Length; i++)
                {
                    // Convert float samples (range -1 to 1) to 16-bit PCM (short, range -32768 to 32767).
                    short intSample = (short)(samples[i] * short.MaxValue);
                    writer.Write(intSample);
                }

                // --- Go back and fill in the size placeholders in the header ---
                long fileSize = memoryStream.Length;
                writer.Seek(4, SeekOrigin.Begin); // Position to file size offset
                writer.Write((int)(fileSize - 8)); // RIFF chunk size (total file size - 8 bytes for "RIFF" and size itself)
                writer.Seek(40, SeekOrigin.Begin); // Position to data size offset
                writer.Write((int)(fileSize - 44)); // Data chunk size (total file size - header size)
            }
            return memoryStream.ToArray(); // Return the complete WAV byte array.
        }
    }
}
