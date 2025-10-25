using UnityEngine;
using NUnit.Framework;

public class ManualTestRunner : MonoBehaviour
{
    [ContextMenu("Run All Tests")]
    public void RunAllTests()
    {
        Debug.Log("=== Starting Manual Test Runner ===");
        
        // Test 1: Simple assertion
        TestSimpleAssertion();
        
        // Test 2: GoogleSignInManager creation
        TestGoogleSignInManagerCreation();
        
        // Test 3: GoogleSignInConfig creation
        TestGoogleSignInConfigCreation();
        
        Debug.Log("=== All Manual Tests Completed ===");
    }
    
    private void TestSimpleAssertion()
    {
        try
        {
            Assert.IsTrue(true, "Simple assertion should pass");
            Debug.Log("Simple assertion test PASSED");
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Simple assertion test FAILED: {e.Message}");
        }
    }
    
    private void TestGoogleSignInManagerCreation()
    {
        try
        {
            GameObject testObject = new GameObject("TestGoogleSignInManager");
            GoogleSignInManager manager = testObject.AddComponent<GoogleSignInManager>();
            
            Assert.IsNotNull(manager, "GoogleSignInManager should be created");
            Assert.IsFalse(manager.IsAuthenticated(), "Manager should not be authenticated initially");
            
            Debug.Log("GoogleSignInManager creation test PASSED");
            
            Object.DestroyImmediate(testObject);
        }
        catch (System.Exception e)
        {
            Debug.LogError($"GoogleSignInManager creation test FAILED: {e.Message}");
        }
    }
    
    private void TestGoogleSignInConfigCreation()
    {
        try
        {
            GoogleSignInConfig config = ScriptableObject.CreateInstance<GoogleSignInConfig>();
            
            Assert.IsNotNull(config, "GoogleSignInConfig should be created");
            Assert.IsNotEmpty(config.clientId, "Client ID should not be empty");
            Assert.IsNotEmpty(config.redirectUri, "Redirect URI should not be empty");
            
            Debug.Log("GoogleSignInConfig creation test PASSED");
            
            Object.DestroyImmediate(config);
        }
        catch (System.Exception e)
        {
            Debug.LogError($"GoogleSignInConfig creation test FAILED: {e.Message}");
        }
    }
}
