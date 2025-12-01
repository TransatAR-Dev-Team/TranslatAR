import { useState, useRef, useCallback, useEffect } from "react";
import { useTranslationWebSocket } from "../../hooks/useTranslationWebSocket";
import { createWavBlob } from "../../utils/audioUtils";
import type { Settings } from "../SettingsMenu/SettingsMenu";

const CHUNK_DURATION_SECONDS = 1.5;
const CHUNK_OVERLAP_SECONDS = 0.5;
const SILENCE_THRESHOLD = 0.01;

async function packageAudioData(
  audioBlob: Blob,
  settings: Settings,
): Promise<Blob> {
  const token = localStorage.getItem("translatar_jwt");
  const metadata = {
    source_lang: settings.source_language,
    target_lang: settings.target_language,
    jwt_token: token || null,
    sample_rate: settings.target_sample_rate,
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

interface TranslationViewProps {
  settings: Settings;
}

export default function TranslationView({ settings }: TranslationViewProps) {
  const { isConnected, lastMessage, sendData } = useTranslationWebSocket();
  const [isRecording, setIsRecording] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);

  // Refs for audio processing
  const audioContextRef = useRef<AudioContext | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const audioWorkletNodeRef = useRef<AudioWorkletNode | null>(null);
  const audioBufferRef = useRef<Float32Array>(new Float32Array(0));
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const processAndSendChunk = useCallback(() => {
    if (audioBufferRef.current.length === 0) return;

    const sampleRate = audioContextRef.current?.sampleRate || 44100;
    const samplesToProcess = Math.floor(
      (CHUNK_DURATION_SECONDS + CHUNK_OVERLAP_SECONDS) * sampleRate,
    );

    if (audioBufferRef.current.length < samplesToProcess) return;

    const audioChunk = audioBufferRef.current.slice(0, samplesToProcess);
    const samplesToDiscard = Math.floor(CHUNK_DURATION_SECONDS * sampleRate);
    audioBufferRef.current = audioBufferRef.current.slice(samplesToDiscard);
    const rms = Math.sqrt(
      audioChunk.reduce((sum, val) => sum + val * val, 0) / audioChunk.length,
    );
    if (rms < SILENCE_THRESHOLD) {
      console.log(`Chunk RMS (${rms.toFixed(4)}) below threshold. Skipping.`);
      return;
    }

    // Create WAV and send, passing the settings object
    const wavBlob = createWavBlob(audioChunk, sampleRate);
    packageAudioData(wavBlob, settings).then((packagedBlob) => {
      sendData(packagedBlob);
      console.log(
        `Sent audio chunk with target lang: ${settings.target_language}`,
      );
    });
  }, [sendData, settings]);

  const startRecording = async () => {
    if (!isConnected || isRecording) return;

    console.log("Attempting to start recording...");

    setIsRecording(true);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true,
        video: true,
      });
      mediaStreamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }

      const context = new AudioContext();
      audioContextRef.current = context;

      // 1. Load the worklet module from the public directory
      await context.audioWorklet.addModule("/audio-processor.js");

      // 2. Create an AudioWorkletNode instead of a ScriptProcessorNode
      const workletNode = new AudioWorkletNode(context, "audio-processor");
      audioWorkletNodeRef.current = workletNode;

      // 3. Listen for messages (raw audio data) from the worklet
      workletNode.port.onmessage = (event) => {
        const newChunk = event.data; // Float32Array
        const currentBuffer = audioBufferRef.current;

        // Create a new buffer large enough for both
        const newBuffer = new Float32Array(
          currentBuffer.length + newChunk.length,
        );

        // Copy old data
        newBuffer.set(currentBuffer);
        // Append new data
        newBuffer.set(newChunk, currentBuffer.length);

        // Update ref
        audioBufferRef.current = newBuffer;
      };

      const source = context.createMediaStreamSource(stream);
      source.connect(workletNode);
      workletNode.connect(context.destination);

      intervalRef.current = setInterval(
        processAndSendChunk,
        CHUNK_DURATION_SECONDS * 1000,
      );

      console.log("Recording started successfully.");
    } catch (err) {
      console.error(
        "Error accessing media devices or setting up AudioWorklet:",
        err,
      );
      alert("Microphone, webcam access denied, or browser not supported.");
      setIsRecording(false);
    }
  };

  const stopRecording = useCallback(() => {
    console.log("Attempting to stop recording...");
    setIsRecording(false);
  }, []);

  const handleToggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  useEffect(() => {
    // This return function is the cleanup handler.
    return () => {
      console.log("Running component unmount cleanup...");
      if (intervalRef.current) clearInterval(intervalRef.current);

      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      }

      if (audioWorkletNodeRef.current) {
        audioWorkletNodeRef.current.disconnect();
      }

      if (
        audioContextRef.current &&
        audioContextRef.current.state !== "closed"
      ) {
        audioContextRef.current.close();
      }
      // Reset all refs
      intervalRef.current = null;
      mediaStreamRef.current = null;
      audioWorkletNodeRef.current = null;
      audioContextRef.current = null;
    };
  }, []);

  // This separate effect handles the logic when the recording state is toggled off.
  useEffect(() => {
    if (!isRecording) {
      console.log("isRecording is false, running cleanup logic...");
      if (intervalRef.current) clearInterval(intervalRef.current);

      intervalRef.current = null;
      processAndSendChunk();
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach((track) => track.stop());
        mediaStreamRef.current = null;
      }

      if (audioWorkletNodeRef.current) {
        audioWorkletNodeRef.current.disconnect();
        audioWorkletNodeRef.current = null;
      }

      if (
        audioContextRef.current &&
        audioContextRef.current.state !== "closed"
      ) {
        audioContextRef.current.close();
        audioContextRef.current = null;
      }

      if (videoRef.current) {
        videoRef.current.srcObject = null;
      }
    }
  }, [isRecording, processAndSendChunk]);

  const buttonText = isRecording ? "Stop Recording" : "Start Recording";

  return (
    <div className="bg-slate-800 rounded-lg p-6 shadow-lg text-center">
      <h2 className="text-2xl font-semibold mb-2">Live Translation</h2>
      <p className="text-slate-400 text-sm mb-4">
        Connection Status:{" "}
        <span className={isConnected ? "text-green-400" : "text-red-400"}>
          {isConnected ? "Connected" : "Disconnected"}
        </span>
      </p>
      <div className="relative bg-slate-900 rounded-md my-4 min-h-[300px] flex items-center justify-center overflow-hidden">
        <video
          ref={videoRef}
          autoPlay
          muted
          playsInline
          className={`absolute top-0 left-0 w-full h-full object-cover transition-opacity duration-300 ${
            isRecording ? "opacity-100" : "opacity-0"
          }`}
          style={{ transform: "scaleX(-1)" }}
        ></video>
        <div className="absolute bottom-0 left-0 right-0 p-4 bg-black/50">
          <p className="text-2xl text-slate-200 text-center drop-shadow-lg">
            {lastMessage || "..."}
          </p>
        </div>
      </div>
      <button
        onClick={handleToggleRecording}
        className={`w-full px-4 py-3 rounded-md transition-colors text-white font-bold text-lg select-none ${
          isRecording
            ? "bg-red-600 hover:bg-red-700"
            : "bg-blue-600 hover:bg-blue-700 disabled:bg-gray-500"
        }`}
        disabled={!isConnected}
      >
        {buttonText}
      </button>
    </div>
  );
}
