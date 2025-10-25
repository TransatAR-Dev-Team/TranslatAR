using NUnit.Framework;
using UnityEngine;

public class SimpleTest
{
    [Test]
    public void SimpleTest_Passes()
    {
        // This is a very simple test that should always pass
        Assert.IsTrue(true);
        Debug.Log("Simple test passed!");
    }
    
    [Test]
    public void SimpleTest_Addition_Passes()
    {
        // Test basic math
        int result = 2 + 2;
        Assert.AreEqual(4, result);
        Debug.Log("Addition test passed!");
    }
}
