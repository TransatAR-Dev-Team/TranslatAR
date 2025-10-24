using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class GoogleSignInTest : MonoBehaviour
{
    [Header("Test UI")]
    public Button testButton;
    public TextMeshProUGUI testResultText;

    private void Start()
    {
        if (testButton != null)
        {
            testButton.onClick.AddListener(RunTests);
        }
    }

    public void RunTests()
    {
        Debug.Log("Running Google Sign-In Tests...");
        
        if (testResultText != null)
        {
            testResultText.text = "Running tests...";
        }

        // Test 1: Check if GoogleSignInManager exists
        bool managerExists = GoogleSignInManager.Instance != null;
        Debug.Log($"Test 1 - Manager exists: {managerExists}");

        // Test 2: Check authentication status
        bool isAuthenticated = GoogleSignInManager.Instance?.IsAuthenticated() ?? false;
        Debug.Log($"Test 2 - Is authenticated: {isAuthenticated}");

        // Test 3: Check current user
        string currentUser = GoogleSignInManager.Instance?.GetCurrentUser() ?? "No manager";
        Debug.Log($"Test 3 - Current user: {currentUser}");

        // Test 4: Check auth token
        string authToken = GoogleSignInManager.Instance?.GetAuthToken() ?? "No token";
        bool hasToken = !string.IsNullOrEmpty(authToken);
        Debug.Log($"Test 4 - Has token: {hasToken}");

        // Compile results
        string results = $"Test Results:\n" +
                        $"Manager exists: {managerExists}\n" +
                        $"Is authenticated: {isAuthenticated}\n" +
                        $"Current user: {currentUser}\n" +
                        $"Has token: {hasToken}";

        Debug.Log(results);

        if (testResultText != null)
        {
            testResultText.text = results;
        }
    }
}
