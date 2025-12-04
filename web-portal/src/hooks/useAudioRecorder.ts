import { useState, useRef, useCallback, useEffect } from "react";
import { createWavBlob } from "../utils/audioUtils";

const CHUNK_DURATION_SECONDS = 1.5;
const CHUNK_OVERLAP_SECONDS = 0.5;
const SILENCE_THRESHOLD = 0.01;

interface UseAudioRecorderProps {
  onAudioChunk: (blob: Blob) => void;
  sampleRate?: number;
}

export function useAudioRecorder({ onAudioChunk }: UseAudioRecorderProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Refs for audio processing internals
  const audioContextRef = useRef<AudioContext | null>(null);
  const audioWorkletNodeRef = useRef<AudioWorkletNode | null>(null);
  const audioBufferRef = useRef<Float32Array>(new Float32Array(0));
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const processChunk = useCallback(() => {
    if (audioBufferRef.current.length === 0) return;

    const ctx = audioContextRef.current;
    if (!ctx) return;

    const currentSampleRate = ctx.sampleRate;
    const samplesToProcess = Math.floor(
      (CHUNK_DURATION_SECONDS + CHUNK_OVERLAP_SECONDS) * currentSampleRate,
    );

    if (audioBufferRef.current.length < samplesToProcess) return;

    // 1. Slice the chunk
    const audioChunk = audioBufferRef.current.slice(0, samplesToProcess);

    // 2. Remove processed data (leaving overlap)
    const samplesToDiscard = Math.floor(
      CHUNK_DURATION_SECONDS * currentSampleRate,
    );
    audioBufferRef.current = audioBufferRef.current.slice(samplesToDiscard);

    // 3. Silence Detection (RMS)
    const rms = Math.sqrt(
      audioChunk.reduce((sum, val) => sum + val * val, 0) / audioChunk.length,
    );

    if (rms < SILENCE_THRESHOLD) {
      return; // Skip silence
    }

    // 4. Create Blob and notify parent
    const wavBlob = createWavBlob(audioChunk, currentSampleRate);
    onAudioChunk(wavBlob);
  }, [onAudioChunk]);

  const startRecording = useCallback(async () => {
    if (isRecording) return;
    setError(null);

    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: true,
        video: true, // We ask for video here so we can pass it to the UI
      });

      setStream(mediaStream); // Expose stream to UI for the <video> tag

      const context = new AudioContext();
      audioContextRef.current = context;

      await context.audioWorklet.addModule("/audio-processor.js");

      const workletNode = new AudioWorkletNode(context, "audio-processor");
      audioWorkletNodeRef.current = workletNode;

      workletNode.port.onmessage = (event) => {
        const newChunk = event.data;
        const currentBuffer = audioBufferRef.current;
        const newBuffer = new Float32Array(
          currentBuffer.length + newChunk.length,
        );
        newBuffer.set(currentBuffer);
        newBuffer.set(newChunk, currentBuffer.length);
        audioBufferRef.current = newBuffer;
      };

      const source = context.createMediaStreamSource(mediaStream);
      source.connect(workletNode);
      workletNode.connect(context.destination);

      intervalRef.current = setInterval(
        processChunk,
        CHUNK_DURATION_SECONDS * 1000,
      );

      setIsRecording(true);
    } catch (err) {
      console.error("Error starting audio recorder:", err);
      setError("Microphone access denied or not supported.");
      setIsRecording(false);
    }
  }, [isRecording, processChunk]);

  const stopRecording = useCallback(() => {
    setIsRecording(false);

    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    // Process any remaining data immediately
    processChunk();

    // Cleanup Audio Nodes
    if (audioWorkletNodeRef.current) {
      audioWorkletNodeRef.current.disconnect();
      audioWorkletNodeRef.current = null;
    }

    if (audioContextRef.current && audioContextRef.current.state !== "closed") {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    // Cleanup Stream
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      setStream(null);
    }

    // Reset Buffer
    audioBufferRef.current = new Float32Array(0);
  }, [stream, processChunk]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (isRecording) stopRecording();
    };
  }, []);

  return {
    isRecording,
    stream,
    error,
    startRecording,
    stopRecording,
  };
}
