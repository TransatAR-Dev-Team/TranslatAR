// unity/Assets/Scripts/Auth/AuthManager.cs
using UnityEngine;
using System.Collections;
using System;

public class AuthManager : MonoBehaviour
{
    public static AuthManager Instance { get; private set; }

    // Events that other parts of the app can subscribe to
    public static event Action OnLoginSuccess;
    public static event Action OnLogout;

    public enum AuthState { LoggedOut, AwaitingDeviceLogin, LoggedIn }
    public AuthState CurrentState { get; private set; } = AuthState.LoggedOut;

    private AuthBackendService _apiService;
    private Coroutine _pollingCoroutine;
    private const string JwtPlayerPrefsKey = "AppAuthToken";

    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            _apiService = GetComponent<AuthBackendService>();
        }
        else
        {
            Destroy(gameObject);
        }
    }

    void Start()
    {
        // Check if we have a saved token from a previous session
        string savedToken = PlayerPrefs.GetString(JwtPlayerPrefsKey, null);
        if (!string.IsNullOrEmpty(savedToken))
        {
            Debug.Log("Found saved auth token. User is logged in.");
            CurrentState = AuthState.LoggedIn;
            // In a real app, you would verify this token with the backend here.
        }
    }

    /// <summary>
    /// Public method to initiate the entire login flow.
    /// </summary>
    public void StartLoginFlow()
    {
        if (CurrentState != AuthState.LoggedOut) return;

        Debug.Log("[AuthManager] Starting device login flow...");
        StartCoroutine(_apiService.StartDeviceLogin(OnDeviceCodeReceived, OnAuthError));
    }

    private void OnDeviceCodeReceived(DeviceStartResponse response)
    {
        Debug.Log($"[AuthManager] Received User Code: {response.user_code}");
        CurrentState = AuthState.AwaitingDeviceLogin;

        // TODO: Trigger UI to show the user code and URL
        Debug.LogWarning($"ACTION REQUIRED: Go to {response.verification_url} and enter code: {response.user_code}");

        // Start polling the backend
        _pollingCoroutine = StartCoroutine(PollLoop(response.device_code, response.interval));
    }

    private IEnumerator PollLoop(string deviceCode, int interval)
    {
        while (CurrentState == AuthState.AwaitingDeviceLogin)
        {
            yield return new WaitForSeconds(interval);
            Debug.Log("[AuthManager] Polling for token...");
            StartCoroutine(_apiService.PollForToken(deviceCode, OnPollResponse, OnAuthError));
        }
    }

    private void OnPollResponse(DevicePollResponse response)
    {
        if (response.status == "authorization_pending")
        {
            Debug.Log("[AuthManager] ...Authorization is still pending.");
            return;
        }

        if (response.status == "completed" && !string.IsNullOrEmpty(response.access_token))
        {
            Debug.Log("[AuthManager] Login complete! Received application JWT.");
            StopCoroutine(_pollingCoroutine);
            _pollingCoroutine = null;

            // Securely save the token and update state
            PlayerPrefs.SetString(JwtPlayerPrefsKey, response.access_token);
            PlayerPrefs.Save();
            CurrentState = AuthState.LoggedIn;

            // TODO: Hide the login UI
            Debug.LogWarning("TODO: Hide the login panel now.");

            // Fire the global login success event
            OnLoginSuccess?.Invoke();
        }
        else
        {
            // Handle other errors like "expired_token"
            OnAuthError($"Login failed with status: {response.status}");
        }
    }

    public void Logout()
    {
        PlayerPrefs.DeleteKey(JwtPlayerPrefsKey);
        PlayerPrefs.Save();
        CurrentState = AuthState.LoggedOut;
        Debug.Log("[AuthManager] User has been logged out.");
        OnLogout?.Invoke();
    }

    private void OnAuthError(string errorMessage)
    {
        Debug.LogError($"[AuthManager] An error occurred: {errorMessage}");
        if (_pollingCoroutine != null)
        {
            StopCoroutine(_pollingCoroutine);
            _pollingCoroutine = null;
        }
        CurrentState = AuthState.LoggedOut;
        // TODO: Update UI to show the error
    }
}
