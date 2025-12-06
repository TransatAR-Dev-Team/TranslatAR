import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import fs from "fs";
import path from "path";

// 1. Setup the Mock Environment for AudioWorklet
const mockPostMessage = vi.fn();

class MockAudioWorkletProcessor {
  port: { postMessage: any };
  constructor() {
    this.port = { postMessage: mockPostMessage };
  }
}

const mockRegisterProcessor = vi.fn();

describe("AudioProcessor (Worklet)", () => {
  let ProcessorClass: any;

  beforeEach(() => {
    vi.clearAllMocks();

    // 2. Inject Globals
    // @ts-ignore
    global.AudioWorkletProcessor = MockAudioWorkletProcessor;
    // @ts-ignore
    global.registerProcessor = mockRegisterProcessor;

    // 3. Load the code manually
    const filePath = path.resolve(process.cwd(), "public/audio-processor.js");
    const fileContent = fs.readFileSync(filePath, "utf-8");

    // Execute the file content in the current scope
    // eslint-disable-next-line no-eval
    eval(fileContent);

    // 4. Retrieve the registered class
    ProcessorClass = mockRegisterProcessor.mock.calls[0][1];
  });

  afterEach(() => {
    // Clean up globals
    // @ts-ignore
    delete global.AudioWorkletProcessor;
    // @ts-ignore
    delete global.registerProcessor;
  });

  it("should forward incoming data chunks to the main thread", () => {
    const processor = new ProcessorClass();
    const inputData = new Float32Array([0.1, 0.2, 0.3]);
    const inputs = [[inputData]];

    processor.process(inputs);

    expect(mockPostMessage).toHaveBeenCalledWith(expect.any(Float32Array));
    const sentData = mockPostMessage.mock.calls[0][0];
    expect(sentData).toHaveLength(3);
    expect(sentData[0]).toBeCloseTo(0.1);
  });

  it("should stream multiple chunks sequentially", () => {
    const processor = new ProcessorClass();

    // First call
    processor.process([[new Float32Array([1, 1])]]);

    // Second call
    processor.process([[new Float32Array([2, 2])]]);

    // Should have called postMessage twice
    expect(mockPostMessage).toHaveBeenCalledTimes(2);

    // First message
    const firstCallData = mockPostMessage.mock.calls[0][0];
    expect(firstCallData).toHaveLength(2);
    expect(firstCallData[0]).toBe(1);

    // Second message
    const secondCallData = mockPostMessage.mock.calls[1][0];
    expect(secondCallData).toHaveLength(2);
    expect(secondCallData[0]).toBe(2);
  });

  it("should handle empty input gracefully", () => {
    const processor = new ProcessorClass();
    const inputs = [[]]; // No channels

    const result = processor.process(inputs);

    // Should return true to keep processor alive
    expect(result).toBe(true);
    // Should not post message for empty input
    expect(mockPostMessage).not.toHaveBeenCalled();
  });
});
