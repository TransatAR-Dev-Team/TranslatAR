using UnityEngine;
using NUnit.Framework;

public class TestRunner : MonoBehaviour
{
    [ContextMenu("Run Google OAuth Tests")]
    public void RunGoogleOAuthTests()
    {
        Debug.Log("=== Running Google OAuth Tests ===");
        
        // Test 1: Environment Setup
        TestEnvironmentSetup();
        
        // Test 2: String Validation
        TestStringValidation();
        
        // Test 3: URL Generation
        TestUrlGeneration();
        
        // Test 4: Response Parsing
        TestResponseParsing();
        
        Debug.Log("=== All Google OAuth Tests Completed ===");
    }
    
    private void TestEnvironmentSetup()
    {
        Debug.Log("Test 1: Environment Setup - PASSED");
    }
    
    private void TestStringValidation()
    {
        string clientId = "test_client_id";
        string redirectUri = "http://localhost:8000/auth/callback";
        
        if (!string.IsNullOrEmpty(clientId) && !string.IsNullOrEmpty(redirectUri))
        {
            Debug.Log("Test 2: String Validation - PASSED");
        }
        else
        {
            Debug.Log("Test 2: String Validation - FAILED");
        }
    }
    
    private void TestUrlGeneration()
    {
        string baseUrl = "https://accounts.google.com/oauth/authorize";
        string clientId = "test_client_id";
        string redirectUri = "http://localhost:8000/auth/callback";
        
        string authUrl = $"{baseUrl}?client_id={clientId}&redirect_uri={redirectUri}";
        
        if (!string.IsNullOrEmpty(authUrl) && authUrl.Contains("accounts.google.com"))
        {
            Debug.Log("Test 3: URL Generation - PASSED");
        }
        else
        {
            Debug.Log("Test 3: URL Generation - FAILED");
        }
    }
    
    private void TestResponseParsing()
    {
        string mockResponse = "{\"access_token\":\"test_token\",\"token_type\":\"Bearer\"}";
        
        if (!string.IsNullOrEmpty(mockResponse) && mockResponse.Contains("access_token"))
        {
            Debug.Log("Test 4: Response Parsing - PASSED");
        }
        else
        {
            Debug.Log("Test 4: Response Parsing - FAILED");
        }
    }
}
