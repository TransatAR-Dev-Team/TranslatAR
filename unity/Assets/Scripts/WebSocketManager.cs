using UnityEngine;
using WebSocketSharp;

public class WebSocketManager : MonoBehaviour
{
    private WebSocket ws;

    void Start()
    {
        ws = new WebSocket("ws://localhost:8000/ws");

        ws.OnOpen += (sender, e) =>
        {
            Debug.Log("Connected!");

            ws.Send("Hello from Unity!");
        };

        ws.OnMessage += (sender, e) =>
        {
            Debug.Log($"Received: {e.Data}");
        };

        ws.OnError += (sender, e) =>
        {
            Debug.LogError($"Error: {e.Message}");
        };

        ws.Connect();
    }
}