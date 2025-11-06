using UnityEngine;
using System.Collections.Generic;

// This allows us to create instances of this object from the Unity Editor's menu.
[CreateAssetMenu(fileName = "EnvironmentConfig", menuName = "TranslatAR/Environment Config", order = 1)]
public class EnvironmentConfig : ScriptableObject
{
    // A simple serializable class to hold our key-value pairs.
    [System.Serializable]
    public class ConfigEntry
    {
        public string key;
        public string value;
    }

    // Unity will serialize this list and save it as part of the asset file.
    public List<ConfigEntry> entries = new List<ConfigEntry>();
}
