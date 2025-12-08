using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;

/// <summary>
/// Play mode tests for OnOffButtonFaceUser
/// Tests runtime rotation behavior
/// </summary>
public class OnOffButtonFaceUser_PlayModeTests
{
    [UnityTest]
    public IEnumerator OnOffButtonFaceUser_RotatesToFaceTarget()
    {
        // Arrange
        var user = new GameObject("User").transform;
        user.position = new Vector3(0, 0, 5f);

        var faceObj = new GameObject("OnOffButtonFaceObj");
        faceObj.transform.position = Vector3.zero;

        var faceScript = faceObj.AddComponent<OnOffButtonFaceUser>();
        faceScript.target = user;
        faceScript.keepUpright = true;

        Vector3 initialForward = faceObj.transform.forward;

        // Act - Wait for LateUpdate to execute
        yield return null;
        yield return null;

        var method = typeof(OnOffButtonFaceUser).GetMethod("LateUpdate",
            System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
        method.Invoke(faceScript, null);

        // Assert
        Assert.AreNotEqual(initialForward, faceObj.transform.forward,
            "Object should rotate towards target");
        
        UnityEngine.Object.DestroyImmediate(faceObj);
        UnityEngine.Object.DestroyImmediate(user.gameObject);
    }

    [UnityTest]
    public IEnumerator OnOffButtonFaceUser_KeepUpright_ConstrainsYRotation()
    {
        // Arrange
        var user = new GameObject("User").transform;
        user.position = new Vector3(3, 2, 5f); // Elevated position

        var faceObj = new GameObject("OnOffButtonFaceObj");
        faceObj.transform.position = Vector3.zero;

        var faceScript = faceObj.AddComponent<OnOffButtonFaceUser>();
        faceScript.target = user;
        faceScript.keepUpright = true;

        // Act
        yield return null;
        var method = typeof(OnOffButtonFaceUser).GetMethod("LateUpdate",
            System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
        method.Invoke(faceScript, null);

        // Assert - When keepUpright is true, rotation should only happen around Y axis
        float angleX = faceObj.transform.eulerAngles.x;
        float angleZ = faceObj.transform.eulerAngles.z;
        
        // X and Z angles should be close to 0 or 360 (no pitch/roll)
        bool isUpright = (Mathf.Abs(angleX) < 1f || Mathf.Abs(angleX - 360f) < 1f) &&
                        (Mathf.Abs(angleZ) < 1f || Mathf.Abs(angleZ - 360f) < 1f);
        
        Assert.IsTrue(isUpright, 
            "Object should remain upright (no pitch/roll) when keepUpright is true");
        
        UnityEngine.Object.DestroyImmediate(faceObj);
        UnityEngine.Object.DestroyImmediate(user.gameObject);
    }

    [UnityTest]
    public IEnumerator OnOffButtonFaceUser_CanvasRotates_WithParent()
    {
        // Arrange
        var user = new GameObject("User").transform;
        user.position = new Vector3(0, 0, 5f);

        var faceObj = new GameObject("OnOffButtonFaceObj");
        faceObj.transform.position = Vector3.zero;

        var canvasObj = new GameObject("Canvas");
        canvasObj.transform.position = new Vector3(1, 0, 0);
        var canvas = canvasObj.AddComponent<Canvas>();

        var faceScript = faceObj.AddComponent<OnOffButtonFaceUser>();
        faceScript.target = user;
        
        var canvasField = typeof(OnOffButtonFaceUser).GetField("menuCanvas",
            System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
        canvasField.SetValue(faceScript, canvas);

        Vector3 initialCanvasForward = canvas.transform.forward;

        // Act
        yield return null;
        var method = typeof(OnOffButtonFaceUser).GetMethod("LateUpdate",
            System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
        method.Invoke(faceScript, null);

        // Assert
        Assert.AreNotEqual(initialCanvasForward, canvas.transform.forward,
            "Canvas should also rotate to face target");
        
        UnityEngine.Object.DestroyImmediate(faceObj);
        UnityEngine.Object.DestroyImmediate(canvasObj);
        UnityEngine.Object.DestroyImmediate(user.gameObject);
    }

    [UnityTest]
    public IEnumerator OnOffButtonFaceUser_NoTarget_DoesNotCrash()
    {
        // Arrange
        var faceObj = new GameObject("OnOffButtonFaceObj");
        var faceScript = faceObj.AddComponent<OnOffButtonFaceUser>();
        faceScript.target = null;

        // Act & Assert - Should not throw exception
        yield return null;
        
        var method = typeof(OnOffButtonFaceUser).GetMethod("LateUpdate",
            System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
        Assert.DoesNotThrow(() => method.Invoke(faceScript, null),
            "Should handle null target gracefully");
        
        UnityEngine.Object.DestroyImmediate(faceObj);
    }

    [UnityTest]
    public IEnumerator OnOffButtonFaceUser_KeepUprightFalse_AllowsFullRotation()
    {
        // Arrange
        var user = new GameObject("User").transform;
        user.position = new Vector3(3, 5, 5f); // High elevated position

        var faceObj = new GameObject("OnOffButtonFaceObj");
        faceObj.transform.position = Vector3.zero;

        var faceScript = faceObj.AddComponent<OnOffButtonFaceUser>();
        faceScript.target = user;
        faceScript.keepUpright = false; // Allow full rotation

        Vector3 initialEuler = faceObj.transform.eulerAngles;

        // Act
        yield return null;
        var method = typeof(OnOffButtonFaceUser).GetMethod("LateUpdate",
            System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
        method.Invoke(faceScript, null);

        // Assert - Should have some X rotation when facing elevated target
        float angleX = faceObj.transform.eulerAngles.x;
        
        // Should have tilted (X rotation changed from initial)
        Assert.AreNotEqual(initialEuler.x, angleX,
            "Object should tilt to face elevated target when keepUpright is false");
        
        UnityEngine.Object.DestroyImmediate(faceObj);
        UnityEngine.Object.DestroyImmediate(user.gameObject);
    }

    [UnityTest]
    public IEnumerator OnOffButtonFaceUser_SmoothTurn_AnimatesRotation()
    {
        // Arrange
        var user = new GameObject("User").transform;
        user.position = new Vector3(0, 0, 5f);

        var faceObj = new GameObject("OnOffButtonFaceObj");
        faceObj.transform.position = Vector3.zero;
        faceObj.transform.rotation = Quaternion.Euler(0, 180, 0); // Face away

        var faceScript = faceObj.AddComponent<OnOffButtonFaceUser>();
        faceScript.target = user;
        faceScript.smoothTurn = 90f; // 90 degrees per second

        Vector3 initialForward = faceObj.transform.forward;

        // Act - Call LateUpdate a few times over simulated time
        yield return null;
        
        var method = typeof(OnOffButtonFaceUser).GetMethod("LateUpdate",
            System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
        
        // First update - should start rotating but not complete
        method.Invoke(faceScript, null);
        Vector3 midRotationForward = faceObj.transform.forward;
        
        // Should have started rotating
        Assert.AreNotEqual(initialForward, midRotationForward,
            "Object should start rotating with smooth turn");
        
        UnityEngine.Object.DestroyImmediate(faceObj);
        UnityEngine.Object.DestroyImmediate(user.gameObject);
    }

    [UnityTest]
    public IEnumerator OnOffButtonFaceUser_Initialize_FindsMainCamera()
    {
        // Arrange
        var mainCamObj = new GameObject("MainCamera");
        var cam = mainCamObj.AddComponent<Camera>();
        mainCamObj.tag = "MainCamera";

        var faceObj = new GameObject("OnOffButtonFaceObj");
        var faceScript = faceObj.AddComponent<OnOffButtonFaceUser>();
        faceScript.target = null; // Don't set target initially

        // Act
        faceScript.Initialize();
        yield return null;

        // Assert
        Assert.IsNotNull(faceScript.target, 
            "Initialize should find and set main camera as target");
        Assert.AreEqual(Camera.main.transform, faceScript.target,
            "Target should be set to main camera transform");
        
        UnityEngine.Object.DestroyImmediate(faceObj);
        UnityEngine.Object.DestroyImmediate(mainCamObj);
    }
}
