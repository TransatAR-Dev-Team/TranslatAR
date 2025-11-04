using UnityEngine;

/// <summary>
/// A simple script to attach to a UI Button.
/// It provides a public method that can be called by an OnClick() event.
/// </summary>
public class TestButtonHandler : MonoBehaviour
{
    /// <summary>
    /// This public method will be triggered when the button is "selected"
    /// by the Interaction SDK's event wrapper.
    /// </summary>
    public void OnButtonClicked()
    {
        // This message will appear in the Unity Console window when you click the button.
        Debug.Log("BUTTON CLICKED! The interaction system is working correctly.");
    }
}
