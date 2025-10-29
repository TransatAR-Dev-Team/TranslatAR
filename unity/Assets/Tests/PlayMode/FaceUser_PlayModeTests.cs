using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;

/// <summary>
/// PLAY MODE test for FaceUser
/// EXPECTED:
/// 1) The FaceUser script should rotate the GameObject so that it faces the user.
/// 2) After LateUpdate() runs, the forward vector of the object should be different compared to its initial direction meaning it rotated
/// </summary>

public class FaceUser_PlayModeTests
{
    [UnityTest]
    public IEnumerator FaceUser_RotatesToFaceTarget()
    {
        var user = new GameObject("User").transform;
        user.position = new Vector3(0, 0, 5f); // Move the user in front

        var faceObj = new GameObject("FaceObj");
        faceObj.transform.position = Vector3.zero;

        var faceScript = faceObj.AddComponent<FaceUser>();
        faceScript.target = user;

        Vector3 initialForward = faceObj.transform.forward;

        // wait a bit to simulate runtime behavior
        yield return null;

        var method = typeof(FaceUser).GetMethod("LateUpdate",
            System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
        method.Invoke(faceScript, null);

        // EXPECTED: object rotated towards user
        Assert.AreNotEqual(initialForward, faceObj.transform.forward,
            $"Expected FaceUser to rotate towards the target. Forward remained {faceObj.transform.forward}.");
    }
}
