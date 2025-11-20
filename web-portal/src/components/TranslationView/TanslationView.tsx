import React, { useState, useRef, useCallback, useEffect } from "react";
import { useTranslationWebSocket } from "../../hooks/useTranslationWebSocket";
import { createWavBlob } from "../../utils/audioUtils";

// Mirroring the Unity settings for consistency
const CHUNK_DURATION_SECONDS = 1.5;
const CHUNK_OVERLAP_SECONDS = 0.5;
const SILENCE_THRESHOLD = 0.01;

// Helper to package data
async function packageAudioData(
  audioBlob: Blob,
  sourceLang: string,
  targetLang: string,
): Promise<Blob> {
  const token = localStorage.getItem("translatar_jwt");
  const metadata = {
    source_lang: sourceLang,
    target_lang: targetLang,
    jwt_token: token || null,
    sample_rate: 44100,
    channels: 1,
  };
  const metadataJson = JSON.stringify(metadata);
  const metadataBytes = new TextEncoder().encode(metadataJson);
  const metadataLength = new ArrayBuffer(4);
  new DataView(metadataLength).setUint32(0, metadataBytes.length, true);

  return new Blob([
    metadataLength,
    metadataBytes,
    await audioBlob.arrayBuffer(),
  ]);
}

export default function LiveTranslationView() {
  const { isConnected, lastMessage, sendData } = useTranslationWebSocket();
  const [isRecording, setIsRecording] = useState(false);

  // Refs for audio processing
  const audioContextRef = useRef<AudioContext | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const scriptProcessorRef = useRef<ScriptProcessorNode | null>(null);

  // --- Refs for continuous processing ---
  const audioBufferRef = useRef<Float32Array>(new Float32Array(0));
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // --- The core chunking logic ---
  const processAndSendChunk = useCallback(() => {
    if (audioBufferRef.current.length === 0) return;

    // We process a fixed chunk size + overlap
    const sampleRate = audioContextRef.current?.sampleRate || 44100;
    const samplesToProcess = Math.floor(
      (CHUNK_DURATION_SECONDS + CHUNK_OVERLAP_SECONDS) * sampleRate,
    );

    if (audioBufferRef.current.length < samplesToProcess) return; // Not enough audio yet

    const audioChunk = audioBufferRef.current.slice(0, samplesToProcess);

    // --- Slice the buffer to maintain the overlap for the next chunk ---
    const samplesToKeep = Math.floor(CHUNK_OVERLAP_SECONDS * sampleRate);
    const samplesToDiscard = Math.floor(CHUNK_DURATION_SECONDS * sampleRate);
    audioBufferRef.current = audioBufferRef.current.slice(samplesToDiscard);

    // Silence detection on the chunk
    const rms = Math.sqrt(
      audioChunk.reduce((sum, val) => sum + val * val, 0) / audioChunk.length,
    );
    if (rms < SILENCE_THRESHOLD) {
      console.log(`Chunk RMS (${rms.toFixed(4)}) below threshold. Skipping.`);
      return;
    }

    // Create WAV and send
    const wavBlob = createWavBlob(audioChunk, sampleRate);
    packageAudioData(wavBlob, "en", "es").then((packagedBlob) => {
      sendData(packagedBlob);
      console.log(`Sent audio chunk of ${packagedBlob.size} bytes.`);
    });
  }, [sendData]);

  const startRecording = async () => {
    if (!isConnected || isRecording) return;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;

      const context = new AudioContext();
      audioContextRef.current = context;
      audioBufferRef.current = new Float32Array(0); // Reset buffer

      const source = context.createMediaStreamSource(stream);
      const processor = context.createScriptProcessor(4096, 1, 1);
      scriptProcessorRef.current = processor;

      processor.onaudioprocess = (event: AudioProcessingEvent) => {
        const inputData = event.inputBuffer.getChannelData(0);
        // Append new audio data to our main buffer
        const newBuffer = new Float32Array(
          audioBufferRef.current.length + inputData.length,
        );
        newBuffer.set(audioBufferRef.current, 0);
        newBuffer.set(inputData, audioBufferRef.current.length);
        audioBufferRef.current = newBuffer;
      };

      source.connect(processor);
      processor.connect(context.destination);

      setIsRecording(true);

      // --- Set up the interval to send chunks periodically ---
      if (intervalRef.current) clearInterval(intervalRef.current);
      intervalRef.current = setInterval(
        processAndSendChunk,
        CHUNK_DURATION_SECONDS * 1000,
      );
    } catch (err) {
      console.error("Error accessing microphone:", err);
      alert("Microphone access denied.");
    }
  };

  const stopRecording = useCallback(() => {
    setIsRecording(false);
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    // Send any remaining audio
    processAndSendChunk();

    // Clean up audio resources
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop());
    }
    if (scriptProcessorRef.current) scriptProcessorRef.current.disconnect();
    if (audioContextRef.current) audioContextRef.current.close();
  }, [processAndSendChunk]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (isRecording) stopRecording();
    };
  }, [isRecording, stopRecording]);

  const statusText = isRecording ? "Recording..." : "Press and Hold to Record";

  return (
    <div className="bg-slate-800 rounded-lg p-6 shadow-lg text-center">
      <h2 className="text-2xl font-semibold mb-2">Live Translation</h2>
      <p className="text-slate-400 text-sm mb-4">
        Connection Status:{" "}
        <span className={isConnected ? "text-green-400" : "text-red-400"}>
          {isConnected ? "Connected" : "Disconnected"}
        </span>
      </p>

      <div className="bg-slate-900 rounded-md my-4 p-6 min-h-[100px] flex items-center justify-center">
        <p className="text-2xl text-slate-200">{lastMessage || "..."}</p>
      </div>

      <button
        onMouseDown={startRecording}
        onMouseUp={stopRecording}
        onMouseLeave={isRecording ? stopRecording : undefined} // Stop if mouse leaves button
        onTouchStart={startRecording}
        onTouchEnd={stopRecording}
        className={`w-full px-4 py-3 rounded-md transition-colors text-white font-bold text-lg select-none ${
          isRecording
            ? "bg-red-600 hover:bg-red-700"
            : "bg-blue-600 hover:bg-blue-700 disabled:bg-gray-500"
        }`}
        disabled={!isConnected}
      >
        {statusText}
      </button>
    </div>
  );
}
