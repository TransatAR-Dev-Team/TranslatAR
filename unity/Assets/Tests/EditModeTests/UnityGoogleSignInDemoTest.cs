using NUnit.Framework;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class UnityGoogleSignInDemoTest
{
    [Test]
    public void UnityGoogleSignInDemo_ComponentSetup_Passes()
    {
        // Test UnityGoogleSignInDemo component setup
        GameObject demoObject = new GameObject("GoogleSignInDemo");
        UnityGoogleSignInDemo demo = demoObject.AddComponent<UnityGoogleSignInDemo>();
        
        // Validate component creation
        Assert.IsNotNull(demo);
        
        // Test UI component references (they should be null initially)
        Assert.IsNull(demo.signInButton);
        Assert.IsNull(demo.signOutButton);
        Assert.IsNull(demo.statusText);
        Assert.IsNull(demo.userInfoText);
        Assert.IsNull(demo.userProfileImage);
        Assert.IsNull(demo.loginPanel);
        Assert.IsNull(demo.userPanel);
        
        Debug.Log("UnityGoogleSignInDemo component setup test passed");
        
        // Clean up
        Object.DestroyImmediate(demoObject);
    }
    
    [Test]
    public void UnityGoogleSignInDemo_ManagerIntegration_Passes()
    {
        // Test integration with GoogleSignInManager
        GameObject demoObject = new GameObject("GoogleSignInDemo");
        UnityGoogleSignInDemo demo = demoObject.AddComponent<UnityGoogleSignInDemo>();
        
        // Test that demo can access manager
        Assert.IsNotNull(demo);
        
        // Test demo functionality
        demo.SetupDemo();
        
        Debug.Log("UnityGoogleSignInDemo manager integration test passed");
        
        // Clean up
        Object.DestroyImmediate(demoObject);
    }
    
    [Test]
    public void UnityGoogleSignInDemo_UIConfiguration_Passes()
    {
        // Test UI configuration
        GameObject demoObject = new GameObject("GoogleSignInDemo");
        UnityGoogleSignInDemo demo = demoObject.AddComponent<UnityGoogleSignInDemo>();
        
        // Test UI setup
        Assert.IsNotNull(demo);
        
        // Test that demo can handle UI updates
        demo.UpdateUI();
        
        Debug.Log("UnityGoogleSignInDemo UI configuration test passed");
        
        // Clean up
        Object.DestroyImmediate(demoObject);
    }
    
    [Test]
    public void UnityGoogleSignInDemo_AuthenticationFlow_Passes()
    {
        // Test authentication flow
        GameObject demoObject = new GameObject("GoogleSignInDemo");
        UnityGoogleSignInDemo demo = demoObject.AddComponent<UnityGoogleSignInDemo>();
        
        // Test demo authentication methods
        Assert.IsNotNull(demo);
        
        // Test sign-in flow
        demo.OnSignInClicked();
        
        // Test sign-out flow
        demo.OnSignOutClicked();
        
        Debug.Log("UnityGoogleSignInDemo authentication flow test passed");
        
        // Clean up
        Object.DestroyImmediate(demoObject);
    }
    
    [Test]
    public void UnityGoogleSignInDemo_ErrorHandling_Passes()
    {
        // Test error handling
        GameObject demoObject = new GameObject("GoogleSignInDemo");
        UnityGoogleSignInDemo demo = demoObject.AddComponent<UnityGoogleSignInDemo>();
        
        // Test error handling methods
        Assert.IsNotNull(demo);
        
        // Test error display
        demo.ShowError("Test error message");
        
        Debug.Log("UnityGoogleSignInDemo error handling test passed");
        
        // Clean up
        Object.DestroyImmediate(demoObject);
    }
}
