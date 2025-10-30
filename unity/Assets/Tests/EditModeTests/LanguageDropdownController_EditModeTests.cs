using NUnit.Framework;
using UnityEngine;
using TMPro;

/// <summary>
/// EDIT MODE tests for LanguageDropdownController.
/// Expectations: 
/// 1) When the LanguageDropdownController is awakened, it should populate the TMP_Dropdown with language options.
/// 2) It should also set the default selected language to "Spanish
/// </summary>

public class LanguageDropdownController_EditModeTests
{
    [Test]
    public void Dropdown_Populates_OnAwake()
    {
        var go = new GameObject("LanguageDropdown");
        var dropdown = go.AddComponent<TMP_Dropdown>();
        var status = new GameObject("StatusText").AddComponent<TextMeshProUGUI>();
        var controller = go.AddComponent<LanguageDropdownController>();
        typeof(LanguageDropdownController)
            .GetField("statusText", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            .SetValue(controller, status);

        var awakeMethod = typeof(LanguageDropdownController).GetMethod(
            "Awake",
            System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic
        );
        awakeMethod.Invoke(controller, null);

        // EXPECTED: Dropdown should have language fields and default to Spanish
        Assert.IsTrue(dropdown.options.Count > 0, "Expected dropdown to be populated with options.");
        Assert.AreEqual("Spanish", LanguageDropdownController.SelectedLabel, "Expected default language to be Spanish.");
    }
}
