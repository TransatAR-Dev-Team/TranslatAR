import React, { useState, useRef, useCallback } from "react";
import { useTranslationWebSocket } from "../../hooks/useTranslationWebSocket";
import { createWavBlob } from "../../utils/audioUtils";

const CHUNK_DURATION_SECONDS = 1.5;
const SILENCE_THRESHOLD = 0.01;

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
  };
  const metadataJson = JSON.stringify(metadata);
  const metadataBytes = new TextEncoder().encode(metadataJson);
  const metadataLength = new ArrayBuffer(4);
  new DataView(metadataLength).setUint32(0, metadataBytes.length, true); // true for little-endian

  return new Blob([
    metadataLength,
    metadataBytes,
    await audioBlob.arrayBuffer(),
  ]);
}

export default function LiveTranslationView() {
  const { isConnected, lastMessage, sendData } = useTranslationWebSocket();
  const [isRecording, setIsRecording] = useState(false);
  const [statusText, setStatusText] = useState("Press and hold to record");

  // Refs to hold audio processing objects
  const audioContextRef = useRef<AudioContext | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const scriptProcessorRef = useRef<ScriptProcessorNode | null>(null);
  const audioBufferRef = useRef<Float32Array[]>([]);

  const processAudio = useCallback((event: AudioProcessingEvent) => {
    const inputData = event.inputBuffer.getChannelData(0);
    audioBufferRef.current.push(new Float32Array(inputData));
  }, []);

  const startRecording = async () => {
    if (!isConnected) {
      alert("WebSocket is not connected. Please wait or refresh.");
      return;
    }
    try {
      setStatusText("Recording...");
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;

      const context = new AudioContext();
      audioContextRef.current = context;

      const source = context.createMediaStreamSource(stream);
      const processor = context.createScriptProcessor(4096, 1, 1); // bufferSize, inputChannels, outputChannels
      scriptProcessorRef.current = processor;

      processor.onaudioprocess = processAudio;
      source.connect(processor);
      processor.connect(context.destination);

      setIsRecording(true);
    } catch (err) {
      console.error("Error accessing microphone:", err);
      setStatusText("Microphone access denied.");
    }
  };

  const stopRecording = useCallback(() => {
    setStatusText("Processing...");
    setIsRecording(false);

    // Stop microphone and audio processing
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop());
    }
    if (scriptProcessorRef.current) {
      scriptProcessorRef.current.disconnect();
      scriptProcessorRef.current = null;
    }
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    // Process the final collected audio buffer
    if (audioBufferRef.current.length > 0) {
      const completeBuffer = new Float32Array(
        audioBufferRef.current.reduce((acc, val) => acc + val.length, 0),
      );
      let offset = 0;
      for (const buffer of audioBufferRef.current) {
        completeBuffer.set(buffer, offset);
        offset += buffer.length;
      }

      // Silence detection
      const rms = Math.sqrt(
        completeBuffer.reduce((sum, val) => sum + val * val, 0) /
          completeBuffer.length,
      );
      if (rms < SILENCE_THRESHOLD) {
        setStatusText("Silence detected. Not sending.");
        console.log(`RMS (${rms.toFixed(4)}) is below threshold.`);
        audioBufferRef.current = []; // Clear buffer
        return;
      }

      // Create WAV and send
      const wavBlob = createWavBlob(completeBuffer, 44100); // Assuming 44.1kHz sample rate
      packageAudioData(wavBlob, "en", "es").then((packagedBlob) => {
        sendData(packagedBlob);
      });
    }

    audioBufferRef.current = []; // Clear buffer
    setStatusText("Press and hold to record");
  }, [sendData]);

  // Use mouse down/up events to mirror the "hold" functionality
  const handleMouseDown = () => {
    if (!isRecording) startRecording();
  };

  const handleMouseUp = () => {
    if (isRecording) stopRecording();
  };

  return (
    <div className="bg-slate-800 rounded-lg p-6 shadow-lg text-center">
      <h2 className="text-2xl font-semibold mb-2">Live Translation</h2>
      <p className="text-slate-400 text-sm mb-4">
        Connection Status:{" "}
        <span className={isConnected ? "text-green-400" : "text-red-400"}>
          {isConnected ? "Connected" : "Disconnected"}
        </span>
      </p>

      {/* Main Display for Subtitles/Status */}
      <div className="bg-slate-900 rounded-md my-4 p-6 min-h-[100px] flex items-center justify-center">
        <p className="text-2xl text-slate-200">{lastMessage || "..."}</p>
      </div>

      {/* Record Button */}
      <button
        onMouseDown={handleMouseDown}
        onMouseUp={handleMouseUp}
        onTouchStart={handleMouseDown} // For mobile
        onTouchEnd={handleMouseUp} // For mobile
        className={`w-full px-4 py-3 rounded-md transition-colors text-white font-bold text-lg ${
          isRecording
            ? "bg-red-600 hover:bg-red-700"
            : "bg-blue-600 hover:bg-blue-700"
        }`}
      >
        {statusText}
      </button>
    </div>
  );
}
