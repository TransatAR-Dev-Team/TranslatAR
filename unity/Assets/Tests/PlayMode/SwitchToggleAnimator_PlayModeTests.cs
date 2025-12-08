using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
using UnityEngine.UI;
using TMPro;
using System.Reflection;

/// <summary>
/// Play mode tests for SwitchToggleAnimator
/// Tests animation behavior and visual transitions
/// </summary>
public class SwitchToggleAnimator_PlayModeTests
{
    private GameObject root;
    private Toggle toggle;
    private SwitchToggleAnimator animator;
    private RectTransform knob;
    private Image background;
    private TextMeshProUGUI onText;
    private TextMeshProUGUI offText;

    [UnitySetUp]
    public IEnumerator SetUp()
    {
        // Create root with Canvas
        root = new GameObject("ToggleRoot", typeof(RectTransform));
        var canvas = root.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;

        // Add Toggle and SwitchToggleAnimator
        toggle = root.AddComponent<Toggle>();
        animator = root.AddComponent<SwitchToggleAnimator>();

        // Create Background
        var bgObj = new GameObject("Background", typeof(RectTransform));
        bgObj.transform.SetParent(root.transform);
        background = bgObj.AddComponent<Image>();
        background.rectTransform.sizeDelta = new Vector2(100, 50);

        // Create Knob
        var knobObj = new GameObject("Checkmark", typeof(RectTransform));
        knobObj.transform.SetParent(root.transform);
        knob = knobObj.GetComponent<RectTransform>();
        knob.sizeDelta = new Vector2(40, 40);

        // Create Text elements
        var onTextObj = new GameObject("OnText", typeof(RectTransform));
        onTextObj.transform.SetParent(root.transform);
        onText = onTextObj.AddComponent<TextMeshProUGUI>();
        onText.text = "ON";

        var offTextObj = new GameObject("OffText", typeof(RectTransform));
        offTextObj.transform.SetParent(root.transform);
        offText = offTextObj.AddComponent<TextMeshProUGUI>();
        offText.text = "OFF";

        // Assign to animator using reflection
        SetPrivateField("knob", knob);
        SetPrivateField("backgroundImage", background);
        SetPrivateField("onText", onText);
        SetPrivateField("offText", offText);

        yield return null;
    }

    [UnityTearDown]
    public IEnumerator TearDown()
    {
        if (root != null)
        {
            UnityEngine.Object.Destroy(root);
        }
        yield return null;
    }

    [UnityTest]
    public IEnumerator ToggleChange_AnimatesKnobPosition()
    {
        // Arrange - Start() should be called automatically
        yield return null;
        
        Vector2 initialPosition = knob.anchoredPosition;
        toggle.isOn = false;

        // Act - Toggle to on
        toggle.isOn = true;
        toggle.onValueChanged.Invoke(true);

        // Wait for animation
        yield return new WaitForSeconds(0.3f);

        // Assert
        Assert.AreNotEqual(initialPosition, knob.anchoredPosition,
            "Knob position should change after toggle");
    }

    [UnityTest]
    public IEnumerator ToggleChange_ChangesBackgroundColor()
    {
        // Arrange
        yield return null;
        
        toggle.isOn = false;
        toggle.onValueChanged.Invoke(false);
        yield return new WaitForSeconds(0.3f);
        
        Color offColor = background.color;

        // Act - Toggle to on
        toggle.isOn = true;
        toggle.onValueChanged.Invoke(true);
        yield return new WaitForSeconds(0.3f);

        // Assert
        Assert.AreNotEqual(offColor, background.color,
            "Background color should change after toggle");
    }

    [UnityTest]
    public IEnumerator ToggleOn_ShowsOnText_HidesOffText()
    {
        // Arrange
        yield return null;
        
        // Act
        toggle.isOn = true;
        toggle.onValueChanged.Invoke(true);
        yield return new WaitForSeconds(0.3f);

        // Assert
        Assert.IsTrue(onText.gameObject.activeSelf, "ON text should be visible");
        Assert.IsFalse(offText.gameObject.activeSelf, "OFF text should be hidden");
    }

    [UnityTest]
    public IEnumerator ToggleOff_ShowsOffText_HidesOnText()
    {
        // Arrange
        yield return null;
        
        // Act
        toggle.isOn = false;
        toggle.onValueChanged.Invoke(false);
        yield return new WaitForSeconds(0.3f);

        // Assert
        Assert.IsFalse(onText.gameObject.activeSelf, "ON text should be hidden");
        Assert.IsTrue(offText.gameObject.activeSelf, "OFF text should be visible");
    }

    [UnityTest]
    public IEnumerator MultipleToggles_AnimateProperly()
    {
        // Arrange
        yield return null;

        // Act - Toggle multiple times
        toggle.isOn = true;
        toggle.onValueChanged.Invoke(true);
        yield return new WaitForSeconds(0.15f);

        toggle.isOn = false;
        toggle.onValueChanged.Invoke(false);
        yield return new WaitForSeconds(0.15f);

        toggle.isOn = true;
        toggle.onValueChanged.Invoke(true);
        yield return new WaitForSeconds(0.3f);

        // Assert - Should end in ON state
        Assert.IsTrue(onText.gameObject.activeSelf, 
            "Should handle multiple toggles correctly");
    }

    [UnityTest]
    public IEnumerator Animation_SmoothEasing_Applied()
    {
        // Arrange
        yield return null;
        
        toggle.isOn = false;
        toggle.onValueChanged.Invoke(false);
        yield return new WaitForSeconds(0.3f);
        
        Vector2 startPos = knob.anchoredPosition;

        // Act - Toggle and sample position mid-animation
        toggle.isOn = true;
        toggle.onValueChanged.Invoke(true);
        
        yield return new WaitForSeconds(0.1f); // Mid-animation
        Vector2 midPos = knob.anchoredPosition;
        
        yield return new WaitForSeconds(0.2f); // End of animation
        Vector2 endPos = knob.anchoredPosition;

        // Assert - Mid position should be between start and end (easing in effect)
        Assert.AreNotEqual(startPos, midPos, "Should be animating");
        Assert.AreNotEqual(midPos, endPos, "Should continue animating to end");
    }

    [UnityTest]
    public IEnumerator ToggleWithoutAnimation_SetsStateImmediately()
    {
        // Arrange - Set animation duration to 0 or use SetSwitchState directly
        var setSwitchStateMethod = typeof(SwitchToggleAnimator).GetMethod("SetSwitchState",
            BindingFlags.NonPublic | BindingFlags.Instance);
        
        yield return null;

        // Act - Set state without animation
        setSwitchStateMethod.Invoke(animator, new object[] { true });

        // Assert - Should be in ON state immediately
        Assert.IsTrue(onText.gameObject.activeSelf, 
            "State should be set immediately without animation");
        Assert.IsFalse(offText.gameObject.activeSelf, 
            "OFF text should be hidden immediately");
    }

    [UnityTest]
    public IEnumerator Animation_CompletesWithinExpectedTime()
    {
        // Arrange
        yield return null;
        
        toggle.isOn = false;
        toggle.onValueChanged.Invoke(false);
        yield return new WaitForSeconds(0.3f);

        var offPosField = typeof(SwitchToggleAnimator).GetField("offPosition",
            BindingFlags.NonPublic | BindingFlags.Instance);
        var onPosField = typeof(SwitchToggleAnimator).GetField("onPosition",
            BindingFlags.NonPublic | BindingFlags.Instance);
        
        Vector2 offPos = (Vector2)offPosField.GetValue(animator);
        Vector2 onPos = (Vector2)onPosField.GetValue(animator);

        // Act - Toggle on
        toggle.isOn = true;
        toggle.onValueChanged.Invoke(true);
        
        // Wait for animation duration (0.2s) + small buffer
        yield return new WaitForSeconds(0.25f);

        // Assert - Should be at final position
        float distance = Vector2.Distance(knob.anchoredPosition, onPos);
        Assert.Less(distance, 1f, 
            "Animation should complete and knob should be at final position");
    }

    [UnityTest]
    public IEnumerator RapidToggling_HandlesGracefully()
    {
        // Arrange
        yield return null;

        // Act - Toggle rapidly without waiting for animations
        toggle.isOn = true;
        toggle.onValueChanged.Invoke(true);
        yield return new WaitForSeconds(0.05f);

        toggle.isOn = false;
        toggle.onValueChanged.Invoke(false);
        yield return new WaitForSeconds(0.05f);

        toggle.isOn = true;
        toggle.onValueChanged.Invoke(true);
        yield return new WaitForSeconds(0.05f);

        toggle.isOn = false;
        toggle.onValueChanged.Invoke(false);

        // Wait for final animation
        yield return new WaitForSeconds(0.3f);

        // Assert - Should end up in correct final state
        Assert.IsFalse(onText.gameObject.activeSelf, 
            "Should handle rapid toggling and end in correct state");
        Assert.IsTrue(offText.gameObject.activeSelf, 
            "OFF text should be visible after rapid toggling");
    }

    [UnityTest]
    public IEnumerator ColorTransition_AnimatesSmoothly()
    {
        // Arrange
        yield return null;
        
        toggle.isOn = false;
        toggle.onValueChanged.Invoke(false);
        yield return new WaitForSeconds(0.3f);
        
        Color startColor = background.color;

        // Act - Toggle and check color mid-animation
        toggle.isOn = true;
        toggle.onValueChanged.Invoke(true);
        
        yield return new WaitForSeconds(0.1f); // Mid-animation
        Color midColor = background.color;
        
        yield return new WaitForSeconds(0.2f); // End of animation
        Color endColor = background.color;

        // Assert - Colors should be transitioning
        Assert.AreNotEqual(startColor, midColor, 
            "Color should be transitioning mid-animation");
        Assert.AreNotEqual(midColor, endColor, 
            "Color should continue transitioning to end");
    }

    [UnityTest]
    public IEnumerator KnobPosition_MaintainsYAxis()
    {
        // Arrange
        yield return null;
        
        float initialY = knob.anchoredPosition.y;

        // Act - Toggle multiple times
        toggle.isOn = true;
        toggle.onValueChanged.Invoke(true);
        yield return new WaitForSeconds(0.3f);

        toggle.isOn = false;
        toggle.onValueChanged.Invoke(false);
        yield return new WaitForSeconds(0.3f);

        // Assert - Y position should remain constant
        Assert.AreEqual(initialY, knob.anchoredPosition.y, 0.1f,
            "Knob Y position should remain constant during animation");
    }

    [UnityTest]
    public IEnumerator Animation_StartsFromCurrentPosition()
    {
        // Arrange
        yield return null;
        
        // Start in OFF state
        toggle.isOn = false;
        toggle.onValueChanged.Invoke(false);
        yield return new WaitForSeconds(0.3f);

        // Act - Start toggling but interrupt mid-animation
        toggle.isOn = true;
        toggle.onValueChanged.Invoke(true);
        yield return new WaitForSeconds(0.1f); // Partial animation
        
        Vector2 interruptPosition = knob.anchoredPosition;
        
        // Reverse direction mid-animation
        toggle.isOn = false;
        toggle.onValueChanged.Invoke(false);
        yield return new WaitForSeconds(0.05f);
        
        Vector2 reverseStartPosition = knob.anchoredPosition;

        // Assert - Should start from current position, not jump
        float positionDifference = Mathf.Abs(interruptPosition.x - reverseStartPosition.x);
        Assert.Less(positionDifference, 10f,
            "Animation should start from current position when interrupted");
    }

    private void SetPrivateField(string fieldName, object value)
    {
        var field = typeof(SwitchToggleAnimator).GetField(fieldName,
            BindingFlags.NonPublic | BindingFlags.Instance);
        field.SetValue(animator, value);
    }
}
