import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import TranslationView from "./TranslationView";
import type { Settings } from "../SettingsMenu/SettingsMenu";
import { useAudioRecorder } from "../../hooks/useAudioRecorder";

// Mock the Hooks
const mockStartRecording = vi.fn();
const mockStopRecording = vi.fn();
const mockSendData = vi.fn();

// Mock WebSocket Hook
vi.mock("../../hooks/useTranslationWebSocket", () => ({
  useTranslationWebSocket: vi.fn(() => ({
    isConnected: true,
    lastMessage: "Hello World",
    sendData: mockSendData,
  })),
}));

// Mock Recorder Hook
vi.mock("../../hooks/useAudioRecorder", () => ({
  useAudioRecorder: vi.fn(() => ({
    isRecording: false,
    startRecording: mockStartRecording,
    stopRecording: mockStopRecording,
    stream: null,
    error: null,
  })),
}));

// Mock Settings
const mockSettings: Settings = {
  source_language: "en",
  target_language: "es",
  chunk_duration_seconds: 1.5,
  target_sample_rate: 48000,
  silence_threshold: 0.01,
  chunk_overlap_seconds: 0.5,
  websocket_url: "",
  subtitles_enabled: true,
  translation_enabled: true,
  subtitle_font_size: 18,
  subtitle_style: "normal",
};

describe("TranslationView Component", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    // Reset the hook to its default state before each test
    vi.mocked(useAudioRecorder).mockImplementation(() => ({
      isRecording: false,
      startRecording: mockStartRecording,
      stopRecording: mockStopRecording,
      stream: null,
      error: null,
    }));
  });

  it("renders connection status and last message", () => {
    render(<TranslationView settings={mockSettings} />);

    expect(screen.getByText("Connected")).toBeInTheDocument();
    expect(screen.getByText("Hello World")).toBeInTheDocument();
  });

  it("calls startRecording when button is clicked", () => {
    render(<TranslationView settings={mockSettings} />);

    const button = screen.getByRole("button", { name: /start recording/i });
    fireEvent.click(button);

    expect(mockStartRecording).toHaveBeenCalledTimes(1);
  });

  it("displays stop button when recording is active", () => {
    // CHANGE: Use vi.mocked(...).mockReturnValue to simulate recording state
    vi.mocked(useAudioRecorder).mockReturnValue({
      isRecording: true,
      startRecording: mockStartRecording,
      stopRecording: mockStopRecording,
      stream: null,
      error: null,
    });

    render(<TranslationView settings={mockSettings} />);

    const button = screen.getByRole("button", { name: /stop recording/i });
    expect(button).toBeInTheDocument();

    fireEvent.click(button);
    expect(mockStopRecording).toHaveBeenCalledTimes(1);
  });

  it("displays error message from recorder hook", () => {
    // CHANGE: Simulate an error state
    vi.mocked(useAudioRecorder).mockReturnValue({
      isRecording: false,
      startRecording: mockStartRecording,
      stopRecording: mockStopRecording,
      stream: null,
      error: "Microphone access denied",
    });

    render(<TranslationView settings={mockSettings} />);
    expect(screen.getByText("Microphone access denied")).toBeInTheDocument();
  });
});
