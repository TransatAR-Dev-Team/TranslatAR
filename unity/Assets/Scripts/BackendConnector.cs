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


// match the JSON response from the /process-audio endpoint
[System.Serializable]
public class TranslationPipelineResponse
{
    public string original_text;
    public string translated_text;
}

public class BackendConnector : MonoBehaviour
{
    private const string backendUrl = "http://localhost:8000/api/process-audio";

    [Header("UI References")]
    public TextMeshProUGUI subtitleText;

    [Header("Translation Settings")]
    public AudioClip testAudioClip; // keep for easy testing
    public string sourceLanguage = "en";
    public string targetLanguage = "es";

    // microphone handling
    private bool isRecording = false;
    private bool permissionGranted = false;
    private AudioClip recordedClip;
    private const int maxRecordingSeconds = 15;
    private const int sampleRate = 44100;

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

    void StartRecording()
    {
        if (isRecording) return;

        isRecording = true;
        subtitleText.text = "Recording...";
        Debug.Log("Recording started...");
        // start recording from the default microphone
        recordedClip = Microphone.Start(null, false, maxRecordingSeconds, sampleRate);
    }

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

    IEnumerator ProcessAudioCoroutine(AudioClip audioClipToProcess)
    {
        var form = new System.Collections.Generic.List<IMultipartFormSection>();

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
                    // --- CORRECTION ---
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

    // helper method to reset the UI text
    void ResetIdleText()
    {
        if (!isRecording)
        {
            subtitleText.text = "Press and hold Spacebar or (A) button to record.";
        }
    }

    public static byte[] ConvertAudioClipToWav(AudioClip clip)
    {
        if (clip == null) return null;

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
                writer.Write((ushort)1); // Audio format (1 for PCM)
                ushort numChannels = (ushort)clip.channels;
                writer.Write(numChannels);
                uint sampleRate = (uint)clip.frequency;
                writer.Write(sampleRate);
                writer.Write(sampleRate * numChannels * 2); // Byte rate
                writer.Write((ushort)(numChannels * 2)); // Block align
                writer.Write((ushort)16); // Bits per sample

                writer.Write(System.Text.Encoding.UTF8.GetBytes("data"));
                writer.Write(0); // Placeholder for data size

                // Audio data
                float[] samples = new float[clip.samples * clip.channels];
                clip.GetData(samples, 0);

                for (int i = 0; i < samples.Length; i++)
                {
                    // Convert float to 16-bit PCM
                    short intSample = (short)(samples[i] * short.MaxValue);
                    writer.Write(intSample);
                }

                // Go back and fill in the size placeholders
                long fileSize = memoryStream.Length;
                writer.Seek(4, SeekOrigin.Begin);
                writer.Write((int)(fileSize - 8));
                writer.Seek(40, SeekOrigin.Begin);
                writer.Write((int)(fileSize - 44));
            }
            return memoryStream.ToArray();
        }
    }
}
