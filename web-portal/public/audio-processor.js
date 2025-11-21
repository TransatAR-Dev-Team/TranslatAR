// This class runs in a separate thread (the AudioWorkletGlobalScope).
// It cannot access the DOM or window object directly.
class AudioProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this._buffer = new Float32Array(0);
  }

  // This method is called for every block of audio data.
  process(inputs) {
    // We expect a single input with a single channel.
    const input = inputs[0];
    const channel = input[0];

    if (channel) {
      // Append the new audio data to our internal buffer.
      const newBuffer = new Float32Array(this._buffer.length + channel.length);
      newBuffer.set(this._buffer, 0);
      newBuffer.set(channel, this._buffer.length);
      this._buffer = newBuffer;

      // Send the entire current buffer back to the main thread.
      // The main thread will be responsible for chunking and sending it.
      this.port.postMessage(this._buffer);
    }

    // Return true to keep the processor alive.
    return true;
  }
}

// Register the processor with a name that we can reference from the main thread.
registerProcessor("audio-processor", AudioProcessor);
