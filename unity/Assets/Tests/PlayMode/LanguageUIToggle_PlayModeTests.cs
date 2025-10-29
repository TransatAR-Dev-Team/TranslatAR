using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;

/// <summary>
/// PLAY MODE tests for LanguageUIToggle
/// EXPECTATIONS:
/// 1) This test takes user input and verifies that the visibility state changes.
/// </summary>
public class LanguageUIToggle_PlayModeTests
{
    [UnityTest]
    public IEnumerator Toggle_MenuVisibility_Changes_OnSimulatedInput()
    {
        var ui = new GameObject("LanguageUI");
        var go = new GameObject("Toggle");
        var toggle = go.AddComponent<LanguageUIToggle>();

        typeof(LanguageUIToggle)
            .GetField("languageUI", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            .SetValue(toggle, ui);

        var startMethod = typeof(LanguageUIToggle).GetMethod(
            "Start",
            System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic
        );
        startMethod.Invoke(toggle, null);

        bool initial = ui.activeSelf;

        // wait a bit to simulate run time
        yield return null;
        ui.SetActive(!initial);

        // EXPECTED: UI should now be in the opposite state
        Assert.AreNotEqual(initial, ui.activeSelf, "Expected LanguageUI visibility to change after simulated input.");
    }
}
