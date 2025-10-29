using NUnit.Framework;
using UnityEngine;

/// <summary>
/// EDIT MODE tests for FaceUser.
/// Expectations:
/// 1) If no target is assigned, Initialize() should default target to Camera.main.
/// 2) keepUpright defaults to false.
/// 3) keepUpright can be changed and persists.
/// </summary>

public class FaceUser_EditModeTests
{
    [Test]
    public void FaceUser_UsesMainCamera_WhenNoTargetAssigned()
    {
        var go = new GameObject("FaceUser");
        var script = go.AddComponent<FaceUser>();

        var camObj = new GameObject("MainCamera");
        camObj.AddComponent<Camera>();
        camObj.tag = "MainCamera";

        script.Initialize();

        // EXPECT: Camera.main to be set as default
        Assert.AreEqual(Camera.main.transform, script.target,
            "Expected FaceUser.target to default to Camera.main when not set.");
    }

    [Test]
    public void FaceUser_KeepUpright_DefaultsFalse()
    {
        var go = new GameObject("FaceUser");
        var script = go.AddComponent<FaceUser>();

        // EXPECT: keepUpRight to be initalized as false
        Assert.IsFalse(script.keepUpright, "Expected keepUpright default to be false.");
    }

    [Test]
    public void FaceUser_KeepUpright_CanBeSetTrue()
    {
        var go = new GameObject("FaceUser");
        var script = go.AddComponent<FaceUser>();
        script.keepUpright = true;

        // EXPECT: keepUpRight to stay as true
        Assert.IsTrue(script.keepUpright, "Expected keepUpright to persist after being set to true.");
    }
}
