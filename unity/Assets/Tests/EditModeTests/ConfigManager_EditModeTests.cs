using NUnit.Framework;
using UnityEngine;
using System.Collections.Generic;
using System.Reflection;

/// <summary>
/// Edit mode tests for ConfigManager
/// Tests configuration loading, value retrieval, and error handling
/// NOTE: Singleton tests simplified for edit mode (no DontDestroyOnLoad)
/// </summary>
public class ConfigManager_EditModeTests
{
    private GameObject testGameObject;
    private ConfigManager configManager;

    [SetUp]
    public void SetUp()
    {
        testGameObject = new GameObject("ConfigManagerTest");
        configManager = testGameObject.AddComponent<ConfigManager>();
        
        // Reset singleton
        ResetSingleton();
    }

    [TearDown]
    public void TearDown()
    {
        // Reset singleton
        ResetSingleton();

        // Destroy game object if it exists
        if (testGameObject != null)
        {
            UnityEngine.Object.DestroyImmediate(testGameObject);
            testGameObject = null;
        }
    }

    private void ResetSingleton()
    {
        var instanceProperty = typeof(ConfigManager).GetProperty("Instance", 
            BindingFlags.Static | BindingFlags.Public);
        if (instanceProperty != null)
        {
            instanceProperty.SetValue(null, null);
        }
    }

    [Test]
    public void GetValue_ReturnsDefaultValue_WhenKeyNotFound()
    {
        // Arrange
        var configValues = new Dictionary<string, string>();
        SetPrivateField("_configValues", configValues);

        // Act
        string result = configManager.GetValue("NONEXISTENT_KEY", "default_value");

        // Assert
        Assert.AreEqual("default_value", result, 
            "Should return default value when key not found");
    }

    [Test]
    public void GetValue_ReturnsCorrectValue_WhenKeyExists()
    {
        // Arrange
        var configValues = new Dictionary<string, string>
        {
            { "TEST_KEY", "test_value" }
        };
        SetPrivateField("_configValues", configValues);

        // Act
        string result = configManager.GetValue("TEST_KEY");

        // Assert
        Assert.AreEqual("test_value", result, 
            "Should return correct value when key exists");
    }

    [Test]
    public void GetValue_ReturnsNull_WhenKeyNotFoundAndNoDefault()
    {
        // Arrange
        var configValues = new Dictionary<string, string>();
        SetPrivateField("_configValues", configValues);

        // Act
        string result = configManager.GetValue("NONEXISTENT_KEY");

        // Assert
        Assert.IsNull(result, "Should return null when key not found and no default provided");
    }

    [Test]
    public void GetValue_HandlesCaseSensitiveKeys()
    {
        // Arrange
        var configValues = new Dictionary<string, string>
        {
            { "BACKEND_URL", "http://localhost:8000" },
            { "backend_url", "http://different:9000" }
        };
        SetPrivateField("_configValues", configValues);

        // Act
        string upperResult = configManager.GetValue("BACKEND_URL");
        string lowerResult = configManager.GetValue("backend_url");

        // Assert
        Assert.AreEqual("http://localhost:8000", upperResult, 
            "Should return value for uppercase key");
        Assert.AreEqual("http://different:9000", lowerResult, 
            "Should return value for lowercase key");
        Assert.AreNotEqual(upperResult, lowerResult, 
            "Keys should be case-sensitive");
    }

    [Test]
    public void GetValue_HandlesEmptyStringValue()
    {
        // Arrange
        var configValues = new Dictionary<string, string>
        {
            { "EMPTY_KEY", "" }
        };
        SetPrivateField("_configValues", configValues);

        // Act
        string result = configManager.GetValue("EMPTY_KEY", "default");

        // Assert
        Assert.AreEqual("", result, "Should return empty string value, not default");
    }

    [Test]
    public void GetValue_HandlesSpecialCharacters()
    {
        // Arrange
        var configValues = new Dictionary<string, string>
        {
            { "API_KEY", "abc-123_XYZ.789" },
            { "URL", "https://example.com:8080/path?query=value&other=data" }
        };
        SetPrivateField("_configValues", configValues);

        // Act
        string apiKey = configManager.GetValue("API_KEY");
        string url = configManager.GetValue("URL");

        // Assert
        Assert.AreEqual("abc-123_XYZ.789", apiKey, 
            "Should handle special characters in values");
        Assert.AreEqual("https://example.com:8080/path?query=value&other=data", url, 
            "Should handle URLs with special characters");
    }

    [Test]
    public void GetValue_HandlesMultipleKeys()
    {
        // Arrange
        var configValues = new Dictionary<string, string>
        {
            { "KEY1", "value1" },
            { "KEY2", "value2" },
            { "KEY3", "value3" }
        };
        SetPrivateField("_configValues", configValues);

        // Act & Assert
        Assert.AreEqual("value1", configManager.GetValue("KEY1"));
        Assert.AreEqual("value2", configManager.GetValue("KEY2"));
        Assert.AreEqual("value3", configManager.GetValue("KEY3"));
    }

    [Test]
    public void EnvironmentConfig_ConfigEntry_StoresKeyValue()
    {
        // Arrange
        var entry = new EnvironmentConfig.ConfigEntry
        {
            key = "TEST_KEY",
            value = "test_value"
        };

        // Assert
        Assert.AreEqual("TEST_KEY", entry.key);
        Assert.AreEqual("test_value", entry.value);
    }

    [Test]
    public void GetValue_HandlesNumericalStrings()
    {
        // Arrange
        var configValues = new Dictionary<string, string>
        {
            { "PORT", "8000" },
            { "TIMEOUT", "30.5" }
        };
        SetPrivateField("_configValues", configValues);

        // Act
        string port = configManager.GetValue("PORT");
        string timeout = configManager.GetValue("TIMEOUT");

        // Assert
        Assert.AreEqual("8000", port);
        Assert.AreEqual("30.5", timeout);
    }

    [Test]
    public void GetValue_HandlesBooleanStrings()
    {
        // Arrange
        var configValues = new Dictionary<string, string>
        {
            { "DEBUG_MODE", "true" },
            { "PRODUCTION", "false" }
        };
        SetPrivateField("_configValues", configValues);

        // Act
        string debugMode = configManager.GetValue("DEBUG_MODE");
        string production = configManager.GetValue("PRODUCTION");

        // Assert
        Assert.AreEqual("true", debugMode);
        Assert.AreEqual("false", production);
    }

    [Test]
    public void ConfigManager_InitialStateIsValid()
    {
        // Assert - Just verify the component exists and is accessible
        Assert.IsNotNull(configManager, "ConfigManager should be created");
        
        // Verify we can access the GetValue method
        string result = configManager.GetValue("ANY_KEY", "default");
        Assert.AreEqual("default", result, "GetValue should be callable");
    }

    private void SetPrivateField(string fieldName, object value)
    {
        var field = typeof(ConfigManager).GetField(fieldName, 
            BindingFlags.NonPublic | BindingFlags.Instance);
        if (field != null && configManager != null)
        {
            field.SetValue(configManager, value);
        }
    }
}