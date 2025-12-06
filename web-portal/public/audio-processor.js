// This class runs in a separate thread (the AudioWorkletGlobalScope).
// It cannot access the DOM or window object directly.
class AudioProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
  }

  // This method is called for every block of audio data.
  process(inputs) {
    // We expect a single input with a single channel.
    const input = inputs[0];
    const channel = input[0];

    if (channel && channel.length > 0) {
      // Send the audio chunk directly to the main thread.
      // The main thread is responsible for buffering and processing.
      this.port.postMessage(channel);
    }

    // Return true to keep the processor alive.
    return true;
  }
}

// Register the processor with a name that we can reference from the main thread.
registerProcessor("audio-processor", AudioProcessor);
