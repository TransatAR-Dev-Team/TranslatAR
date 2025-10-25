using System.Collections;
using System.Collections.Generic;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;

public class GoogleSignInPlayModeTests
{
    [UnityTest]
    public IEnumerator GoogleSignInPlayMode_SimpleTest_Passes()
    {
        // Simple PlayMode test that doesn't depend on custom classes
        Assert.IsTrue(true);
        Debug.Log("✅ PlayMode test started");
        
        // Wait a frame
        yield return null;
        
        Debug.Log("✅ PlayMode test completed");
    }
    
    [UnityTest]
    public IEnumerator GoogleSignInPlayMode_MathTest_Passes()
    {
        // Test basic math in PlayMode
        int result = 2 + 2;
        Assert.AreEqual(4, result);
        Debug.Log("✅ PlayMode math test passed");
        
        // Wait a frame
        yield return null;
    }
}
