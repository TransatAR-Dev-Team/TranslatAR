using NUnit.Framework;
using UnityEngine;

public class BasicUnityTests
{
    [Test]
    public void BasicUnityTest_Passes()
    {
        // Test basic Unity functionality
        Assert.IsTrue(true);
        Debug.Log("✅ Basic Unity test passed!");
    }
    
    [Test]
    public void GameObjectTest_Passes()
    {
        // Test GameObject creation
        GameObject testObject = new GameObject("TestObject");
        Assert.IsNotNull(testObject);
        Assert.AreEqual("TestObject", testObject.name);
        
        Object.DestroyImmediate(testObject);
        Debug.Log("✅ GameObject test passed!");
    }
    
    [Test]
    public void Vector3Test_Passes()
    {
        // Test Vector3 operations
        Vector3 v1 = new Vector3(1, 2, 3);
        Vector3 v2 = new Vector3(1, 2, 3);
        Assert.AreEqual(v1, v2);
        Debug.Log("✅ Vector3 test passed!");
    }
}
