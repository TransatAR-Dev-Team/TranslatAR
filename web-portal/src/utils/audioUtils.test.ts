import { describe, it, expect, vi, beforeEach, beforeAll } from "vitest";
import { createWavBlob, packageAudioData } from "./audioUtils";
import type { Settings } from "../components/SettingsMenu/SettingsMenu";

const mockSettings: Settings = {
  source_language: "en",
  target_language: "es",
  chunk_duration_seconds: 1.5,
  target_sample_rate: 48000,
  silence_threshold: 0.01,
  chunk_overlap_seconds: 0.5,
  websocket_url: "ws://localhost:8000/ws",
  subtitles_enabled: true,
  translation_enabled: true,
  subtitle_font_size: 18,
  subtitle_style: "normal",
};

describe("audioUtils", () => {
  // Polyfill Blob.prototype.arrayBuffer for JSDOM environment
  beforeAll(() => {
    if (!Blob.prototype.arrayBuffer) {
      Blob.prototype.arrayBuffer = function () {
        return new Promise((resolve, reject) => {
          const reader = new FileReader();
          reader.onload = () => resolve(reader.result as ArrayBuffer);
          reader.onerror = () => reject(reader.error);
          reader.readAsArrayBuffer(this);
        });
      };
    }
  });

  it("createWavBlob should produce a valid WAV blob with the correct size and type", async () => {
    // Arrange: Create a short, simple audio buffer
    const sampleRate = 16000;
    const durationSeconds = 0.5;
    const numSamples = sampleRate * durationSeconds;
    const samples = new Float32Array(numSamples);

    // Fill with a simple sine wave to have non-zero data
    for (let i = 0; i < numSamples; i++) {
      samples[i] = Math.sin((i / sampleRate) * 440 * 2 * Math.PI);
    }

    // Act: Create the WAV blob
    const blob = createWavBlob(samples, sampleRate);

    // Assert: Check the fundamental properties of the blob
    expect(blob).toBeInstanceOf(Blob);
    expect(blob.type).toBe("audio/wav");

    // The size should be the 44-byte WAV header plus 2 bytes for each 16-bit sample
    const expectedSize = 44 + numSamples * 2;
    expect(blob.size).toBe(expectedSize);
  });

  it("createWavBlob should handle an empty Float32Array", () => {
    // Arrange
    const samples = new Float32Array(0);
    const sampleRate = 44100;

    // Act
    const blob = createWavBlob(samples, sampleRate);

    // Assert
    expect(blob.type).toBe("audio/wav");
    expect(blob.size).toBe(44); // Should only contain the header
  });

  describe("packageAudioData", () => {
    beforeEach(() => {
      // Clear localStorage before each test
      localStorage.clear();
      vi.clearAllMocks();
    });

    it("packages audio blob with metadata correctly", async () => {
      // 1. Arrange
      const audioContent = new Uint8Array([1, 2, 3, 4]);
      const audioBlob = new Blob([audioContent], { type: "audio/wav" });
      localStorage.setItem("translatar_jwt", "fake-token-123");

      // 2. Act
      const resultBlob = await packageAudioData(audioBlob, mockSettings);

      // 3. Assert
      // Convert result back to ArrayBuffer to inspect bytes
      const buffer = await resultBlob.arrayBuffer();
      const view = new DataView(buffer);

      // A. Check the first 4 bytes (Metadata Length)
      const metadataLen = view.getUint32(0, true); // Little endian
      expect(metadataLen).toBeGreaterThan(0);

      // B. Decode the Metadata JSON
      // Metadata starts at byte 4 and has length `metadataLen`
      const metadataBytes = buffer.slice(4, 4 + metadataLen);
      const decoder = new TextDecoder();
      const metadataJson = decoder.decode(metadataBytes);
      const metadata = JSON.parse(metadataJson);

      expect(metadata).toEqual({
        source_lang: "en",
        target_lang: "es",
        jwt_token: "fake-token-123",
        sample_rate: 48000,
        channels: 1,
      });

      // C. Check the Audio Data
      // Audio data starts after the metadata
      const audioStart = 4 + metadataLen;
      const actualAudioBytes = new Uint8Array(buffer.slice(audioStart));

      // Should match our original input [1, 2, 3, 4]
      expect(actualAudioBytes).toEqual(audioContent);
    });

    it("handles missing JWT token gracefully", async () => {
      const audioBlob = new Blob(["test"], { type: "audio/wav" });

      // Ensure no token exists
      localStorage.removeItem("translatar_jwt");

      const resultBlob = await packageAudioData(audioBlob, mockSettings);

      const buffer = await resultBlob.arrayBuffer();
      const view = new DataView(buffer);
      const metadataLen = view.getUint32(0, true);

      const metadataBytes = buffer.slice(4, 4 + metadataLen);
      const metadata = JSON.parse(new TextDecoder().decode(metadataBytes));

      expect(metadata.jwt_token).toBeNull();
    });
  });
});
