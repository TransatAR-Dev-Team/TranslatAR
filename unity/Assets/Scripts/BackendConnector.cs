using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using System.IO;
using System;
using TMPro;

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
    public AudioClip testAudioClip;
    public string sourceLanguage = "en";
    public string targetLanguage = "es";

    void Start()
    {
        if (subtitleText == null)
        {
            Debug.LogError("SubtitleText component is not assigned in the Inspector.");
            return;
        }
        if (testAudioClip == null)
        {
            Debug.LogError("TestAudioClip is not assigned in the Inspector.");
            subtitleText.text = "Error: No AudioClip provided.";
            return;
        }
        
        subtitleText.text = "Processing audio...";
        StartCoroutine(ProcessAudioCoroutine());
    }

    IEnumerator ProcessAudioCoroutine()
    {
        // Create a form to send data
        var form = new System.Collections.Generic.List<IMultipartFormSection>();

        // Convert the AudioClip to a WAV byte array
        byte[] audioData = ConvertAudioClipToWav(testAudioClip);
        if (audioData == null)
        {
            subtitleText.text = "Error: Failed to convert AudioClip.";
            yield break; // Stop the coroutine
        }

        // Add the audio file to the form.
        // The field name "audio_file" MUST match what the FastAPI backend expects.
        form.Add(new MultipartFormFileSection("audio_file", audioData, "test.wav", "audio/wav"));

        // Add the language parameters to the form
        form.Add(new MultipartFormDataSection("source_lang", sourceLanguage));
        form.Add(new MultipartFormDataSection("target_lang", targetLanguage));

        // Create and send the POST request
        using (UnityWebRequest webRequest = UnityWebRequest.Post(backendUrl, form))
        {
            yield return webRequest.SendWebRequest();

            switch (webRequest.result)
            {
                case UnityWebRequest.Result.ConnectionError:
                case UnityWebRequest.Result.DataProcessingError:
                case UnityWebRequest.Result.ProtocolError:
                    Debug.LogError("Error: " + webRequest.error);
                    // Also log the response body if available, it might contain a detailed error from the server
                    Debug.LogError("Response: " + webRequest.downloadHandler.text);
                    subtitleText.text = "Error: Could not connect to backend.";
                    break;
                case UnityWebRequest.Result.Success:
                    string jsonResponse = webRequest.downloadHandler.text;
                    Debug.Log("Received from backend: " + jsonResponse);

                    // Parse the new JSON response structure
                    TranslationPipelineResponse response = JsonUtility.FromJson<TranslationPipelineResponse>(jsonResponse);

                    Debug.Log("Original Text: " + response.original_text);
                    Debug.Log("Translated Text: " + response.translated_text);

                    // Display the final translated text
                    subtitleText.text = response.translated_text;
                    break;
            }
        }
    }

    // --- Helper Function to convert AudioClip to WAV byte array ---
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
