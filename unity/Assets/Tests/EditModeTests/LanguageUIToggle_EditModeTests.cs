using NUnit.Framework;
using UnityEngine;

/// <summary>
/// EDIT MODE tests for LanguageUIToggle
/// EXPECTATIONS:
/// 1) When LanguageUIToggle starts, it reads the initial visibility of the assigned LanguageUI obj
/// 2) The test checks that the LanguageUI remains active by default
/// </summary>

public class LanguageUIToggle_EditModeTests
{
    [Test]
    public void LanguageUIToggle_Start_SetsInitialState()
    {
        var ui = new GameObject("LanguageUI");
        var go = new GameObject("Toggle");
        var toggle = go.AddComponent<LanguageUIToggle>();

        typeof(LanguageUIToggle)
            .GetField("languageUI", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            .SetValue(toggle, ui);

        var startMethod = typeof(LanguageUIToggle).GetMethod("Start", 
            System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
        startMethod.Invoke(toggle, null);

       // EXPECTED: LanguageUI is active
        Assert.IsTrue(ui.activeSelf, "Expected the LanguageUI to start as active.");
    }
}
