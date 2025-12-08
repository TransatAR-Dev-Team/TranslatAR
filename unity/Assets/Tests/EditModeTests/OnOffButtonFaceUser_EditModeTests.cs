using NUnit.Framework;
using UnityEngine;

/// <summary>
/// Edit mode tests for OnOffButtonFaceUser
/// Tests UI rotation and camera tracking functionality
/// </summary>
public class OnOffButtonFaceUser_EditModeTests
{
    [Test]
    public void OnOffButtonFaceUser_InitializesWithMainCamera()
    {
        // Arrange
        var go = new GameObject("OnOffButtonFaceUser");
        var script = go.AddComponent<OnOffButtonFaceUser>();
        
        var camObj = new GameObject("MainCamera");
        camObj.AddComponent<Camera>();
        camObj.tag = "MainCamera";

        // Act
        script.Initialize();

        // Assert
        Assert.AreEqual(Camera.main.transform, script.target, 
            "Target should default to Camera.main");
        
        UnityEngine.Object.DestroyImmediate(go);
        UnityEngine.Object.DestroyImmediate(camObj);
    }

    [Test]
    public void OnOffButtonFaceUser_KeepUpright_DefaultsTrue()
    {
        // Arrange
        var go = new GameObject("OnOffButtonFaceUser");
        var script = go.AddComponent<OnOffButtonFaceUser>();

        // Assert
        Assert.IsTrue(script.keepUpright, 
            "keepUpright should default to true for OnOffButton variant");
        
        UnityEngine.Object.DestroyImmediate(go);
    }

    [Test]
    public void OnOffButtonFaceUser_SmoothTurn_DefaultsZero()
    {
        // Arrange
        var go = new GameObject("OnOffButtonFaceUser");
        var script = go.AddComponent<OnOffButtonFaceUser>();

        // Assert
        Assert.AreEqual(0f, script.smoothTurn, 
            "smoothTurn should default to 0 for instant rotation");
        
        UnityEngine.Object.DestroyImmediate(go);
    }

    [Test]
    public void OnOffButtonFaceUser_CanAssignCanvas()
    {
        // Arrange
        var go = new GameObject("OnOffButtonFaceUser");
        var script = go.AddComponent<OnOffButtonFaceUser>();
        
        var canvasObj = new GameObject("Canvas");
        var canvas = canvasObj.AddComponent<Canvas>();

        // Act
        var canvasField = typeof(OnOffButtonFaceUser).GetField("menuCanvas",
            System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
        canvasField.SetValue(script, canvas);
        var retrievedCanvas = (Canvas)canvasField.GetValue(script);

        // Assert
        Assert.AreEqual(canvas, retrievedCanvas, 
            "Should be able to assign and retrieve canvas");
        
        UnityEngine.Object.DestroyImmediate(go);
        UnityEngine.Object.DestroyImmediate(canvasObj);
    }

    [Test]
    public void OnOffButtonFaceUser_TargetCanBeSet()
    {
        // Arrange
        var go = new GameObject("OnOffButtonFaceUser");
        var script = go.AddComponent<OnOffButtonFaceUser>();
        var targetObj = new GameObject("CustomTarget");

        // Act
        script.target = targetObj.transform;

        // Assert
        Assert.AreEqual(targetObj.transform, script.target, 
            "Target should be settable");
        
        UnityEngine.Object.DestroyImmediate(go);
        UnityEngine.Object.DestroyImmediate(targetObj);
    }

    [Test]
    public void OnOffButtonFaceUser_Initialize_DoesNotCrash()
    {
        // Arrange
        var go = new GameObject("OnOffButtonFaceUser");
        var script = go.AddComponent<OnOffButtonFaceUser>();

        // Act & Assert - Should not throw exception
        Assert.DoesNotThrow(() => script.Initialize(),
            "Initialize should not crash");
        
        UnityEngine.Object.DestroyImmediate(go);
    }

    [Test]
    public void OnOffButtonFaceUser_HasPublicFields()
    {
        // Arrange
        var go = new GameObject("OnOffButtonFaceUser");
        var script = go.AddComponent<OnOffButtonFaceUser>();

        // Assert - Verify public fields exist and are accessible
        Assert.IsNotNull(typeof(OnOffButtonFaceUser).GetField("target"), 
            "target field should be public");
        Assert.IsNotNull(typeof(OnOffButtonFaceUser).GetField("keepUpright"), 
            "keepUpright field should be public");
        Assert.IsNotNull(typeof(OnOffButtonFaceUser).GetField("smoothTurn"), 
            "smoothTurn field should be public");
        
        UnityEngine.Object.DestroyImmediate(go);
    }

    [Test]
    public void OnOffButtonFaceUser_HasInitializeMethod()
    {
        // Arrange
        var go = new GameObject("OnOffButtonFaceUser");
        var script = go.AddComponent<OnOffButtonFaceUser>();

        // Assert - Verify Initialize method exists and is public
        var method = typeof(OnOffButtonFaceUser).GetMethod("Initialize");
        Assert.IsNotNull(method, "Initialize method should exist");
        Assert.IsTrue(method.IsPublic, "Initialize method should be public");
        
        UnityEngine.Object.DestroyImmediate(go);
    }
}
