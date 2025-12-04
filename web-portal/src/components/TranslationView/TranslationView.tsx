import { useRef, useEffect, useState } from "react"; // Added useState
import { useTranslationWebSocket } from "../../hooks/useTranslationWebSocket";
import { useAudioRecorder } from "../../hooks/useAudioRecorder";
import { packageAudioData } from "../../utils/audioUtils";
import type { Settings } from "../SettingsMenu/SettingsMenu";

interface TranslationViewProps {
  settings: Settings;
}

export default function TranslationView({ settings }: TranslationViewProps) {
  const { isConnected, lastMessage, sendData } = useTranslationWebSocket();
  const videoRef = useRef<HTMLVideoElement>(null);

  // --- Generate a stable Conversation ID for this session ---
  const [conversationId] = useState(() => crypto.randomUUID());

  const handleAudioChunk = async (wavBlob: Blob) => {
    if (!isConnected) return;

    const packagedBlob = await packageAudioData(
      wavBlob,
      settings,
      conversationId,
    );

    sendData(packagedBlob);
    console.log(
      `Sent chunk (${settings.source_language}->${settings.target_language}) ID: ${conversationId}`,
    );
  };

  const { isRecording, startRecording, stopRecording, stream, error } =
    useAudioRecorder({
      onAudioChunk: handleAudioChunk,
    });

  // 3. UI Logic: Attach stream to video element when it becomes available
  useEffect(() => {
    if (videoRef.current && stream) {
      videoRef.current.srcObject = stream;
    } else if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
  }, [stream]);

  // 4. Interaction Handler
  const handleToggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const buttonText = isRecording ? "Stop Recording" : "Start Recording";

  // 5. Dynamic Styles Calculation
  const isHighContrast = settings.subtitle_style === "high-contrast";
  const isBold = settings.subtitle_style === "bold" || isHighContrast;

  const containerClasses = `absolute bottom-0 left-0 right-0 p-4 transition-colors duration-300 ${
    isHighContrast ? "bg-black" : "bg-black/50"
  }`;

  const textClasses = `text-center drop-shadow-lg transition-all duration-300 ${
    isHighContrast ? "text-yellow-300" : "text-slate-200"
  } ${isBold ? "font-bold" : "font-normal"}`;

  return (
    <div className="bg-slate-800 rounded-lg p-6 shadow-lg text-center">
      <h2 className="text-2xl font-semibold mb-2">Live Translation</h2>

      <p className="text-slate-400 text-sm mb-4">
        Connection Status:{" "}
        <span className={isConnected ? "text-green-400" : "text-red-400"}>
          {isConnected ? "Connected" : "Disconnected"}
        </span>
      </p>

      {error && <p className="text-red-500 mb-4 font-bold">{error}</p>}

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

        {/* Subtitles Overlay */}
        {settings.subtitles_enabled && (
          <div className={containerClasses}>
            <p
              className={textClasses}
              style={{
                fontSize: `${settings.subtitle_font_size}px`,
                lineHeight: 1.4,
              }}
            >
              {lastMessage || "..."}
            </p>
          </div>
        )}
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
