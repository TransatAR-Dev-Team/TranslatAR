import { renderHook, act } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { useTranslationWebSocket } from "./useTranslationWebSocket";

// We need to capture the WebSocket instance created inside the hook
// so we can trigger events on it (onopen, onmessage, etc.)
let mockWebSocketInstance: any = null;

class MockWebSocket {
  url: string;
  readyState: number;
  send: ReturnType<typeof vi.fn>;
  close: ReturnType<typeof vi.fn>;

  // Callback placeholders that the hook will assign to
  onopen: (() => void) | null = null;
  onmessage: ((event: any) => void) | null = null;
  onerror: ((error: any) => void) | null = null;
  onclose: (() => void) | null = null;

  static OPEN = 1;
  static CONNECTING = 0;
  static CLOSING = 2;
  static CLOSED = 3;

  constructor(url: string) {
    this.url = url;
    this.readyState = MockWebSocket.CONNECTING;
    this.send = vi.fn();
    this.close = vi.fn();
    mockWebSocketInstance = this;
  }
}

describe("useTranslationWebSocket Hook", () => {
  const originalWebSocket = global.WebSocket;

  beforeEach(() => {
    // 1. Reset the captured instance
    mockWebSocketInstance = null;

    // 2. Mock the global WebSocket object
    global.WebSocket = MockWebSocket as any;

    // 3. Mock window.location because the hook uses it to build the URL
    Object.defineProperty(window, "location", {
      value: { host: "localhost:3000" },
      writable: true,
    });
  });

  afterEach(() => {
    // Restore the original WebSocket implementation
    global.WebSocket = originalWebSocket;
    vi.clearAllMocks();
  });

  it("should initialize with default state", () => {
    const { result } = renderHook(() => useTranslationWebSocket());

    expect(result.current.isConnected).toBe(false);
    expect(result.current.lastMessage).toBe(null);
  });

  it("should connect and update state on 'open' event", () => {
    const { result } = renderHook(() => useTranslationWebSocket());

    expect(mockWebSocketInstance).toBeDefined();

    // Simulate WebSocket opening
    act(() => {
      mockWebSocketInstance.readyState = MockWebSocket.OPEN;
      if (mockWebSocketInstance.onopen) {
        mockWebSocketInstance.onopen();
      }
    });

    expect(result.current.isConnected).toBe(true);
    expect(result.current.lastMessage).toBe("Connected.");
  });

  it("should update lastMessage when receiving a translated_text message", () => {
    const { result } = renderHook(() => useTranslationWebSocket());

    // Connect first
    act(() => {
      if (mockWebSocketInstance.onopen) mockWebSocketInstance.onopen();
    });

    // Simulate receiving a message
    const mockEvent = {
      data: JSON.stringify({ translated_text: "Hola Mundo" }),
    };

    act(() => {
      if (mockWebSocketInstance.onmessage) {
        mockWebSocketInstance.onmessage(mockEvent);
      }
    });

    expect(result.current.lastMessage).toBe("Hola Mundo");
  });

  it("should handle connection errors", () => {
    const { result } = renderHook(() => useTranslationWebSocket());

    // Suppress console.error for this test since the hook logs the error
    const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});

    act(() => {
      if (mockWebSocketInstance.onerror) {
        mockWebSocketInstance.onerror(new Error("Network failure"));
      }
    });

    expect(result.current.lastMessage).toBe("Connection Error.");

    consoleSpy.mockRestore();
  });

  it("should handle disconnection", () => {
    const { result } = renderHook(() => useTranslationWebSocket());

    // Connect first
    act(() => {
      if (mockWebSocketInstance.onopen) mockWebSocketInstance.onopen();
    });
    expect(result.current.isConnected).toBe(true);

    // Disconnect
    act(() => {
      if (mockWebSocketInstance.onclose) {
        mockWebSocketInstance.onclose();
      }
    });

    expect(result.current.isConnected).toBe(false);
    expect(result.current.lastMessage).toBe("Disconnected.");
  });

  it("should send data when connected", () => {
    const { result } = renderHook(() => useTranslationWebSocket());

    // Connect manually
    act(() => {
      mockWebSocketInstance.readyState = MockWebSocket.OPEN;
      if (mockWebSocketInstance.onopen) mockWebSocketInstance.onopen();
    });

    const testBlob = new Blob(["test audio"], { type: "audio/wav" });

    act(() => {
      result.current.sendData(testBlob);
    });

    expect(mockWebSocketInstance.send).toHaveBeenCalledWith(testBlob);
  });

  it("should NOT send data if WebSocket is not open", () => {
    const { result } = renderHook(() => useTranslationWebSocket());
    const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});

    // Ensure socket is not OPEN (it defaults to CONNECTING in our mock)
    mockWebSocketInstance.readyState = MockWebSocket.CONNECTING;

    const testBlob = new Blob(["test"], { type: "text/plain" });

    act(() => {
      result.current.sendData(testBlob);
    });

    expect(mockWebSocketInstance.send).not.toHaveBeenCalled();
    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringContaining("WebSocket is not connected"),
    );

    consoleSpy.mockRestore();
  });

  it("should close the WebSocket when unmounted", () => {
    const { unmount } = renderHook(() => useTranslationWebSocket());

    // Capture the close method before unmounting makes the instance inaccessible
    const closeSpy = mockWebSocketInstance.close;

    unmount();

    expect(closeSpy).toHaveBeenCalled();
  });
});
