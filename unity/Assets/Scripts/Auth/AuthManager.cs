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

    public UserProfile CurrentUser { get; private set; }

    private AuthBackendService _apiService;
    private Coroutine _pollingCoroutine;
    private const string JwtPlayerPrefsKey = "AppAuthToken";

    [Header("UI References")]
    [SerializeField] private LoginPanelUI loginPanelUI;

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
            Debug.Log("Found saved auth token. Fetching user profile...");
            // If we have a token, get the user profile to display the welcome message.
            StartCoroutine(_apiService.GetMe(savedToken, OnProfileReceived, OnAuthError));
        }
        else
        {
            CurrentState = AuthState.LoggedOut;
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

        // Update the UI to show the user code and verification URL
        if (loginPanelUI != null)
        {
            loginPanelUI.ShowLoginDetails(response.user_code, response.verification_url);
        }

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
            if (_pollingCoroutine != null)
            {
                StopCoroutine(_pollingCoroutine);
                _pollingCoroutine = null;
            }

            string appToken = response.access_token;

            // Securely save the token and update state
            PlayerPrefs.SetString(JwtPlayerPrefsKey, appToken);
            PlayerPrefs.Save();

            // Fetch user profile to confirm login
            StartCoroutine(_apiService.GetMe(appToken, OnProfileReceived, OnAuthError));
        }
        else
        {
            OnAuthError($"Login failed with status: {response.status}");
        }
    }

    private void OnProfileReceived(UserProfile profile)
    {
        Debug.Log($"[AuthManager] Welcome, {profile.username} ({profile.email})");
        CurrentUser = profile;
        CurrentState = AuthState.LoggedIn;

        // Update the UI with the welcome message
        if (loginPanelUI != null)
        {
            loginPanelUI.ShowWelcomeMessage(profile.username);
        }

        OnLoginSuccess?.Invoke();
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
