using System;
using WebSocketSharp;

/// <summary>
/// Mock implementation of IWebSocketClient for testing purposes.
/// Allows programmatic control of connection state and events.
/// </summary>
public class MockWebSocketClient : IWebSocketClient
{
    public event EventHandler OnOpen;
    public event EventHandler<MessageEventArgs> OnMessage;
    public event EventHandler<ErrorEventArgs> OnError;
    public event EventHandler<CloseEventArgs> OnClose;

    public WebSocketState ReadyState { get; private set; } = WebSocketState.Connecting;
    
    // Track sent data for verification
    public byte[] LastSentData { get; private set; }
    public int SendCallCount { get; private set; }
    
    // Track method calls
    public bool ConnectCalled { get; private set; }
    public bool CloseCalled { get; private set; }
    
    // Configuration
    public bool ShouldFailOnConnect { get; set; }
    public bool ShouldFailOnSend { get; set; }

    public void Connect()
    {
        ConnectCalled = true;
        
        if (ShouldFailOnConnect)
        {
            ReadyState = WebSocketState.Closed;
            TriggerError("Simulated connection failure");
        }
        else
        {
            ReadyState = WebSocketState.Open;
            TriggerOpen();
        }
    }

    public void Send(byte[] data)
    {
        SendCallCount++;
        LastSentData = data;
        
        if (ShouldFailOnSend)
        {
            throw new Exception("Simulated send failure");
        }
    }

    public void Close()
    {
        CloseCalled = true;
        ReadyState = WebSocketState.Closed;
        TriggerClose();
    }

    // Helper methods to trigger events programmatically for testing
    public void TriggerOpen()
    {
        ReadyState = WebSocketState.Open;
        OnOpen?.Invoke(this, EventArgs.Empty);
    }

    public void TriggerMessage(string textData)
    {
        OnMessage?.Invoke(this, new MessageEventArgs
        {
            IsText = true,
            Data = textData
        });
    }

    public void TriggerError(string errorMessage)
    {
        OnError?.Invoke(this, new ErrorEventArgs
        {
            Message = errorMessage
        });
    }

    public void TriggerClose()
    {
        ReadyState = WebSocketState.Closed;
        OnClose?.Invoke(this, new CloseEventArgs());
    }

    public void Reset()
    {
        LastSentData = null;
        SendCallCount = 0;
        ConnectCalled = false;
        CloseCalled = false;
        ReadyState = WebSocketState.Connecting;
    }
}