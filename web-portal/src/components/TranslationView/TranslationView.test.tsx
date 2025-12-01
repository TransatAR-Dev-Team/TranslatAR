import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import TranslationView from "./TranslationView";
import type { Settings } from "../SettingsMenu/SettingsMenu";
// 1. Import hooks directly so we can use vi.mocked() on them
import { useAudioRecorder } from "../../hooks/useAudioRecorder";

// 2. Mock the Hooks
// We define the spies globally so we can check if they were called
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
// IMPORTANT: We use vi.fn() here so that we can use .mockReturnValue() in the tests
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
    // Simulate recording state
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
    // Simulate an error state
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

  it("applies font size from settings", () => {
    const customSettings = { ...mockSettings, subtitle_font_size: 32 };
    render(<TranslationView settings={customSettings} />);

    const message = screen.getByText("Hello World");
    expect(message).toHaveStyle({ fontSize: "32px" });
  });

  it("hides subtitles when disabled", () => {
    const customSettings = { ...mockSettings, subtitles_enabled: false };
    render(<TranslationView settings={customSettings} />);

    const message = screen.queryByText("Hello World");
    expect(message).not.toBeInTheDocument();
  });

  it("applies high contrast styling", () => {
    const customSettings: Settings = {
      ...mockSettings,
      subtitle_style: "high-contrast",
    };
    render(<TranslationView settings={customSettings} />);

    const message = screen.getByText("Hello World");
    // Check for yellow text (Tailwind class)
    expect(message).toHaveClass("text-yellow-300");
    // High contrast should also force bold
    expect(message).toHaveClass("font-bold");
  });
});
