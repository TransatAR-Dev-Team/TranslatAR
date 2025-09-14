using UnityEngine;
using UnityEngine.Networking;
using System.Collections;

// A simple class to demonstrate connecting to backend
[System.Serializable]
public class BackendMessage
{
    public string message;
}

public class BackendConnector : MonoBehaviour
{
    private const string backendUrl = "http://localhost:8000/api/db-hello";

    void Start()
    {
        StartCoroutine(GetDataFromBackend());
    }

    IEnumerator GetDataFromBackend()
    {
        using (UnityWebRequest webRequest = UnityWebRequest.Get(backendUrl))
        {
            yield return webRequest.SendWebRequest();

            switch (webRequest.result)
            {
                case UnityWebRequest.Result.ConnectionError:
                case UnityWebRequest.Result.DataProcessingError:
                case UnityWebRequest.Result.ProtocolError:
                    Debug.LogError("Error: " + webRequest.error);
                    break;
                case UnityWebRequest.Result.Success:
                    string jsonResponse = webRequest.downloadHandler.text;
                    Debug.Log("Received from backend: " + jsonResponse);

                    BackendMessage message = JsonUtility.FromJson<BackendMessage>(jsonResponse);

                    Debug.Log("Message from backend: " + message.message);
                    break;
            }
        }
    }
}