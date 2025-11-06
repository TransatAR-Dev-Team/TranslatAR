// unity/Assets/Scripts/Auth/AuthBackendService.cs
using UnityEngine;
using UnityEngine.Networking;
using System;
using System.Collections;
using System.Text;

// --- Data Structures for JSON Deserialization ---
[System.Serializable]
public class DeviceStartResponse
{
    public string user_code;
    public string verification_url;
    public string device_code;
    public int interval;
    public int expires_in;
}

[System.Serializable]
public class DevicePollRequest
{
    public string device_code;
}

[System.Serializable]
public class DevicePollResponse
{
    public string status; // "authorization_pending", "completed", "error"
    public string access_token;
    public string token_type;
}

public class AuthBackendService : MonoBehaviour
{
    private string _backendUrl;

    void Start()
    {
        // Load the backend URL from our central config manager
        _backendUrl = ConfigManager.Instance.GetValue("BACKEND_URL", "http://localhost:8000");
    }

    /// <summary>
    /// Coroutine to call the /api/auth/device/start endpoint.
    /// </summary>
    public IEnumerator StartDeviceLogin(Action<DeviceStartResponse> onSuccess, Action<string> onError)
    {
        string url = $"{_backendUrl}/api/auth/device/start";
        using (UnityWebRequest request = UnityWebRequest.PostWwwForm(url, ""))
        {
            request.SetRequestHeader("Content-Type", "application/json");

            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                try
                {
                    DeviceStartResponse response = JsonUtility.FromJson<DeviceStartResponse>(request.downloadHandler.text);
                    onSuccess?.Invoke(response);
                }
                catch (Exception e)
                {
                    onError?.Invoke($"Failed to parse server response: {e.Message}");
                }
            }
            else
            {
                onError?.Invoke($"Failed to start device login. Server responded with: {request.error} - {request.downloadHandler.text}");
            }
        }
    }

    /// <summary>
    /// Coroutine to poll the /api/auth/device/poll endpoint.
    /// </summary>
    public IEnumerator PollForToken(string deviceCode, Action<DevicePollResponse> onSuccess, Action<string> onError)
    {
        string url = $"{_backendUrl}/api/auth/device/poll";
        var requestBody = new DevicePollRequest { device_code = deviceCode };
        string jsonBody = JsonUtility.ToJson(requestBody);
        byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonBody);

        using (UnityWebRequest request = UnityWebRequest.PostWwwForm(url, "POST"))
        {
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");

            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                try
                {
                    DevicePollResponse response = JsonUtility.FromJson<DevicePollResponse>(request.downloadHandler.text);
                    onSuccess?.Invoke(response);
                }
                catch (Exception e)
                {
                    onError?.Invoke($"Failed to parse poll response: {e.Message}");
                }
            }
            else
            {
                onError?.Invoke($"Polling failed. Server responded with: {request.error} - {request.downloadHandler.text}");
            }
        }
    }
}
