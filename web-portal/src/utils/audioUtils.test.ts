import { describe, it, expect } from "vitest";
import { createWavBlob } from "./audioUtils";

describe("audioUtils", () => {
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
});
