using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
using TMPro;

/// <summary>
/// PLAY MODE tests for LanguageDropdownController
/// EXPECTATIONS: 
/// 1) The TMP_Dropdown should trigger the OnValueChanged event
//                          AND
/// 2) Changing the dropdown value should update the selected language
/// </summary>

public class LanguageDropdownController_PlayModeTests
{
    [UnityTest]
    public IEnumerator Dropdown_Changes_SelectedLanguage()
    {
        var go = new GameObject("LanguageDropdown");
        var dropdown = go.AddComponent<TMP_Dropdown>();
        var status = new GameObject("StatusText").AddComponent<TextMeshProUGUI>();

        var controller = go.AddComponent<LanguageDropdownController>();
        typeof(LanguageDropdownController)
            .GetField("dropdown", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            .SetValue(controller, dropdown);
        typeof(LanguageDropdownController)
            .GetField("statusText", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            .SetValue(controller, status);

        var awakeMethod = typeof(LanguageDropdownController).GetMethod(
            "Awake",
            System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic
        );
        awakeMethod.Invoke(controller, null);

        dropdown.value = 0;
        dropdown.onValueChanged.Invoke(0);

        yield return null; // wait a bit to simulate run time

        // EXPECTED: SelectedLabel should update to another language
        Assert.AreEqual("English", LanguageDropdownController.SelectedLabel, "Expected selected label to update after dropdown change.");
    }
}
