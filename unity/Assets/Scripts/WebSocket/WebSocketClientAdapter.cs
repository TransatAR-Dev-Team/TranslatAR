using System;
using WebSocketSharp;

/// <summary>
/// Adapter that wraps WebSocketSharp.WebSocket to implement IWebSocketClient.
/// </summary>
public class WebSocketClientAdapter : IWebSocketClient
{
    private WebSocket ws;

    public WebSocketClientAdapter(string url)
    {
        ws = new WebSocket(url);
        
        // Bridge WebSocketSharp events to our interface events
        ws.OnOpen += (sender, e) =>
        {
            OnOpen?.Invoke(sender, e);
        };
        
        ws.OnMessage += (sender, e) =>
        {
            OnMessage?.Invoke(sender, new MessageEventArgs
            {
                IsText = e.IsText,
                Data = e.Data,
                RawData = e.RawData
            });
        };
        
        ws.OnError += (sender, e) =>
        {
            OnError?.Invoke(sender, new ErrorEventArgs
            {
                Message = e.Message,
                Exception = e.Exception
            });
        };
        
        ws.OnClose += (sender, e) =>
        {
            OnClose?.Invoke(sender, new CloseEventArgs
            {
                Code = e.Code,
                Reason = e.Reason
            });
        };
    }

    public event EventHandler OnOpen;
    public event EventHandler<MessageEventArgs> OnMessage;
    public event EventHandler<ErrorEventArgs> OnError;
    public event EventHandler<CloseEventArgs> OnClose;

    public WebSocketState ReadyState => ws.ReadyState;
    
    public void Connect()
    {
        ws.Connect();
    }
    
    public void Send(byte[] data)
    {
        ws.Send(data);
    }
    
    public void Close()
    {
        ws.Close();
    }
}