using UnityEngine;
using System.Collections.Generic;
using System.Linq;

public class ConfigManager : MonoBehaviour
{
    public static ConfigManager Instance { get; private set; }

    private Dictionary<string, string> _configValues = new Dictionary<string, string>();

    void Awake()
    {
        // Standard singleton pattern.
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            LoadConfig();
        }
        else
        {
            Destroy(gameObject);
        }
    }

    private void LoadConfig()
    {
        // 'Resources.Load' looks for assets in any 'Resources' folder.
        // The asset name is used without the file extension.
        var configAsset = Resources.Load<EnvironmentConfig>("EnvironmentConfig");

        if (configAsset == null)
        {
            Debug.LogError("FATAL: EnvironmentConfig.asset not found in a Resources folder. Please run 'TranslatAR > Update Environment Config' in the editor.");
            return;
        }

        // Convert the list to a dictionary for fast lookups.
        _configValues = configAsset.entries.ToDictionary(entry => entry.key, entry => entry.value);
        Debug.Log($"Configuration loaded with {_configValues.Count} entries.");
    }

    /// <summary>
    /// Gets a configuration value by key.
    /// </summary>
    /// <param name="key">The key from the .env file (e.g., "BACKEND_URL").</param>
    /// <param name="defaultValue">An optional value to return if the key is not found.</param>
    /// <returns>The configuration value string, or the default value.</returns>
    public string GetValue(string key, string defaultValue = null)
    {
        if (_configValues.TryGetValue(key, out var value))
        {
            return value;
        }

        Debug.LogWarning($"Config key '{key}' not found. Returning default value.");
        return defaultValue;
    }
}
