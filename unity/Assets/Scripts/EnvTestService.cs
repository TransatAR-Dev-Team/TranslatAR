using UnityEngine;
using System.Collections;

/// <summary>
/// A simple service to test that the ConfigManager is successfully loading
/// values from the root .env file at runtime.
/// </summary>
public class EnvTestService : MonoBehaviour
{
    // The key we want to fetch from the .env file.
    private const string KeyToTest = "GOOGLE_CLIENT_ID_UNITY";

    IEnumerator Start()
    {
        // Wait until the end of the frame to ensure the ConfigManager singleton has initialized in Awake().
        yield return new WaitForEndOfFrame();

        Debug.Log($"[EnvTestService] Attempting to fetch key: '{KeyToTest}'...");

        if (ConfigManager.Instance == null)
        {
            Debug.LogError("[EnvTestService] FATAL: ConfigManager.Instance is null. Make sure it's attached to a GameObject in the scene.");
            yield break;
        }

        // Fetch the value from the ConfigManager.
        string value = ConfigManager.Instance.GetValue(KeyToTest);

        if (!string.IsNullOrEmpty(value))
        {
            // For security, we'll only print part of the key in a real app,
            // but for this test, printing the whole thing is fine.
            Debug.Log($"[EnvTestService] SUCCESS! Found value: '{value}'");
        }
        else
        {
            Debug.LogError($"[EnvTestService] FAILED. The value for '{KeyToTest}' was not found. " +
                           "Ensure the key exists in your root .env file and you have run 'TranslatAR > Update Environment Config'.");
        }
    }
}
