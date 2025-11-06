using UnityEngine;
using UnityEditor;
using System.IO;
using System.Collections.Generic;

public class EnvConfigUpdater
{
    // Defines the path to the .env file relative to the Assets folder.
    private const string EnvFilePath = "../../.env";

    // Defines where the ScriptableObject asset is located.
    private const string ConfigAssetPath = "Assets/Resources/EnvironmentConfig.asset";

    // This adds the menu item to the Unity Editor.
    [MenuItem("TranslatAR/Update Environment Config from .env")]
    public static void UpdateConfig()
    {
        Debug.Log("Starting configuration update from .env file...");
        string rootPath = Path.GetFullPath(Path.Combine(Application.dataPath, EnvFilePath));

        if (!File.Exists(rootPath))
        {
            Debug.LogError($".env file not found at path: {rootPath}. Please create it at the project root.");
            return;
        }

        // Load the ScriptableObject asset.
        var config = AssetDatabase.LoadAssetAtPath<EnvironmentConfig>(ConfigAssetPath);
        if (config == null)
        {
            Debug.LogError($"EnvironmentConfig asset not found at '{ConfigAssetPath}'. Please create one via: Assets > Create > TranslatAR > Environment Config, and place it in the 'Assets/Resources' folder.");
            return;
        }

        // Parse the .env file.
        var envValues = ParseEnvFile(rootPath);

        // Update the ScriptableObject.
        config.entries.Clear();
        foreach (var pair in envValues)
        {
            config.entries.Add(new EnvironmentConfig.ConfigEntry { key = pair.Key, value = pair.Value });
        }

        // IMPORTANT: Mark the asset as dirty to ensure changes are saved.
        EditorUtility.SetDirty(config);
        AssetDatabase.SaveAssets();

        Debug.Log($"Successfully updated EnvironmentConfig with {envValues.Count} values from .env file.");
    }

    private static Dictionary<string, string> ParseEnvFile(string path)
    {
        var dictionary = new Dictionary<string, string>();
        foreach (var line in File.ReadAllLines(path))
        {
            var trimmedLine = line.Trim();
            // Skip comments and empty lines.
            if (trimmedLine.StartsWith("#") || string.IsNullOrEmpty(trimmedLine))
                continue;

            var parts = trimmedLine.Split(new[] { '=' }, 2);
            if (parts.Length == 2)
            {
                var key = parts[0].Trim();
                var value = parts[1].Trim();
                dictionary[key] = value;
            }
        }
        return dictionary;
    }
}
