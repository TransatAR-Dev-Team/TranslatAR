using System.Collections;
using System.Collections.Generic;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;

public class SimpleEditModeTests
{
    [Test]
    public void SimpleTest_Passes()
    {
        // Basic test that should always pass
        Assert.IsTrue(true);
        Debug.Log("✅ Simple EditMode test passed!");
    }
    
    [Test]
    public void MathTest_Passes()
    {
        // Test basic math
        int result = 2 + 2;
        Assert.AreEqual(4, result);
        Debug.Log("✅ Math test passed!");
    }
    
    [Test]
    public void StringTest_Passes()
    {
        // Test string operations
        string testString = "Unity Test";
        Assert.IsNotEmpty(testString);
        Assert.IsTrue(testString.Contains("Unity"));
        Debug.Log("✅ String test passed!");
    }
}
