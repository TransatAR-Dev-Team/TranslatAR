using System;
using WebSocketSharp;

/// <summary>
/// Interface for WebSocket client operations, enabling testability and decoupling.
/// </summary>
public interface IWebSocketClient
{
    event EventHandler OnOpen;
    event EventHandler<MessageEventArgs> OnMessage;
    event EventHandler<ErrorEventArgs> OnError;
    event EventHandler<CloseEventArgs> OnClose;
    
    WebSocketState ReadyState { get; }
    void Connect();
    void Send(byte[] data);
    void Close();
}

/// <summary>
/// Custom message event arguments independent of WebSocketSharp.
/// </summary>
public class MessageEventArgs : EventArgs
{
    public bool IsText { get; set; }
    public string Data { get; set; }
    public byte[] RawData { get; set; }
}

/// <summary>
/// Custom error event arguments independent of WebSocketSharp.
/// </summary>
public class ErrorEventArgs : EventArgs
{
    public string Message { get; set; }
    public Exception Exception { get; set; }
}

/// <summary>
/// Custom close event arguments independent of WebSocketSharp.
/// </summary>
public class CloseEventArgs : EventArgs
{
    public ushort Code { get; set; }
    public string Reason { get; set; }
}