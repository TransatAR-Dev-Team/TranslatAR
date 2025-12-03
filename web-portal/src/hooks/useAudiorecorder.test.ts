import { renderHook, act } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { useAudioRecorder } from "./useAudioRecorder";

// --- MOCKS ---
// 1. Mock getUserMedia
const mockGetUserMedia = vi.fn();
Object.defineProperty(global.navigator, "mediaDevices", {
  value: {
    getUserMedia: mockGetUserMedia,
  },
  writable: true,
});

// 2. Mock AudioContext and AudioWorkletNode
const mockAudioContextClose = vi.fn();
const mockConnect = vi.fn();
const mockDisconnect = vi.fn();
const mockWorkletPortOnMessage = vi.fn();

class MockAudioWorkletNode {
  port = {
    onmessage: null as any,
    postMessage: vi.fn(),
  };
  connect = mockConnect;
  disconnect = mockDisconnect;
  constructor() {
    // expose this instance so we can simulate events in tests
    (global as any).lastCreatedWorkletNode = this;
  }
}

class MockAudioContext {
  state = "running";
  sampleRate = 44100;
  audioWorklet = {
    addModule: vi.fn().mockResolvedValue(undefined),
  };
  createMediaStreamSource = vi.fn().mockReturnValue({ connect: vi.fn() });
  destination = {};
  close = mockAudioContextClose;
}

(global as any).AudioContext = MockAudioContext;
(global as any).AudioWorkletNode = MockAudioWorkletNode;

describe("useAudioRecorder Hook", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    mockGetUserMedia.mockReset();
    mockAudioContextClose.mockReset();
    mockDisconnect.mockReset();
    (global as any).lastCreatedWorkletNode = undefined;
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("starts recording successfully", async () => {
    // Setup Mock Stream
    const mockTracks = [{ stop: vi.fn() }];
    mockGetUserMedia.mockResolvedValue({
      getTracks: () => mockTracks,
    });

    const { result } = renderHook(() =>
      useAudioRecorder({ onAudioChunk: vi.fn() }),
    );

    // Initial state
    expect(result.current.isRecording).toBe(false);

    // Start
    await act(async () => {
      await result.current.startRecording();
    });

    expect(result.current.isRecording).toBe(true);
    expect(result.current.stream).toBeDefined();
    expect(mockGetUserMedia).toHaveBeenCalled();
  });

  it("handles errors when starting recording", async () => {
    mockGetUserMedia.mockRejectedValue(new Error("Permission denied"));

    const { result } = renderHook(() =>
      useAudioRecorder({ onAudioChunk: vi.fn() }),
    );

    await act(async () => {
      await result.current.startRecording();
    });

    expect(result.current.isRecording).toBe(false);
    expect(result.current.error).toMatch(/denied/i);
  });

  it("processes audio chunks periodically", async () => {
    const onAudioChunkSpy = vi.fn();
    mockGetUserMedia.mockResolvedValue({
      getTracks: () => [{ stop: vi.fn() }],
    });

    const { result } = renderHook(() =>
      useAudioRecorder({ onAudioChunk: onAudioChunkSpy }),
    );

    await act(async () => {
      await result.current.startRecording();
    });

    // Simulate audio data coming from the Worklet
    const workletNode = (global as any).lastCreatedWorkletNode;
    expect(workletNode).toBeDefined();

    // Fill buffer with enough data (needs ~2 seconds of data at 44.1k)
    // 2 seconds * 44100 = 88200 samples
    // Let's create a loud signal (to pass silence check)
    const largeChunk = new Float32Array(88200).fill(0.5);

    act(() => {
      if (workletNode.port.onmessage) {
        workletNode.port.onmessage({ data: largeChunk });
      }
    });

    // Fast-forward time to trigger interval (1.5s)
    act(() => {
      vi.advanceTimersByTime(1600);
    });

    expect(onAudioChunkSpy).toHaveBeenCalled();
    // Verify it passes a Blob
    expect(onAudioChunkSpy.mock.calls[0][0]).toBeInstanceOf(Blob);
  });

  it("stops recording and cleans up", async () => {
    const mockTrackStop = vi.fn();
    mockGetUserMedia.mockResolvedValue({
      getTracks: () => [{ stop: mockTrackStop }],
    });

    const { result } = renderHook(() =>
      useAudioRecorder({ onAudioChunk: vi.fn() }),
    );

    await act(async () => {
      await result.current.startRecording();
    });

    await act(async () => {
      result.current.stopRecording();
    });

    expect(result.current.isRecording).toBe(false);
    expect(mockAudioContextClose).toHaveBeenCalled();
    expect(mockDisconnect).toHaveBeenCalled(); // Worklet disconnected
    expect(mockTrackStop).toHaveBeenCalled(); // Stream tracks stopped
  });
});
