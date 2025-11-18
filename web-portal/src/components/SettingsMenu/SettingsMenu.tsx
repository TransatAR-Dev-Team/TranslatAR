import { useState, useEffect } from "react";

export interface Settings {
  source_language: string;
  target_language: string;
  chunk_duration_seconds: number;
  target_sample_rate: number;
  silence_threshold: number;
  chunk_overlap_seconds: number;
  websocket_url: string;
}

interface SettingsMenuProps {
  initialSettings: Settings;
  onSave: (newSettings: Settings) => void;
  onClose: () => void;
  error: string | null;
}

const LANGUAGES = [
  { code: "en", label: "English" },
  { code: "es", label: "Spanish" },
  { code: "fr", label: "French" },
  { code: "de", label: "German" },
  { code: "it", label: "Italian" },
  { code: "pt", label: "Portuguese" },
  { code: "ru", label: "Russian" },
  { code: "ja", label: "Japanese" },
  { code: "ko", label: "Korean" },
  { code: "zh", label: "Chinese" },
];

export default function SettingsMenu({
  initialSettings,
  onSave,
  onClose,
  error,
}: SettingsMenuProps) {
  const [settings, setSettings] = useState<Settings>(initialSettings);

  useEffect(() => {
    setSettings(initialSettings);
  }, [initialSettings]);

  const handleChange =
    (field: keyof Settings) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
      const { value, type } = e.target;
      const isNumber = type === "number";

      setSettings((prev) => ({
        ...prev,
        [field]: isNumber ? parseFloat(value) : value,
      }));
    };

  const handleSave = () => {
    onSave(settings);
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-slate-800 rounded-lg p-6 w-full max-w-xl mx-4 shadow-xl">
        {/* Header */}
        <div className="flex justify-between items-center mb-4">
          <div>
            <h2 className="text-2xl font-bold">Settings</h2>
            <p className="text-sm text-slate-300">
              Configure default language pair and audio capture options.
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white text-2xl leading-none"
            aria-label="Close settings"
          >
            ×
          </button>
        </div>

        {error && (
          <div className="bg-red-900 text-red-200 p-3 rounded-md mb-4 text-sm">
            {error}
          </div>
        )}

        <div className="space-y-6">
          {/* Language pairing */}
          <section>
            <h3 className="text-lg font-semibold mb-2">Default Language Pair</h3>
            <p className="text-xs text-slate-300 mb-3">
              This pair will be used by default in the Unity app and backend.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label
                  htmlFor="source_language"
                  className="block text-sm font-medium mb-1"
                >
                  Source Language
                </label>
                <select
                  id="source_language"
                  name="source_language"
                  value={settings.source_language}
                  onChange={handleChange("source_language")}
                  className="w-full bg-slate-700 p-2 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {LANGUAGES.map((lang) => (
                    <option key={lang.code} value={lang.code}>
                      {lang.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label
                  htmlFor="target_language"
                  className="block text-sm font-medium mb-1"
                >
                  Target Language
                </label>
                <select
                  id="target_language"
                  name="target_language"
                  value={settings.target_language}
                  onChange={handleChange("target_language")}
                  className="w-full bg-slate-700 p-2 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {LANGUAGES.map((lang) => (
                    <option key={lang.code} value={lang.code}>
                      {lang.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </section>

          {/* Audio / chunking */}
          <section>
            <h3 className="text-lg font-semibold mb-2">Audio Chunking</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label
                  htmlFor="chunk_duration_seconds"
                  className="block text-sm font-medium mb-1"
                >
                  Chunk Duration (seconds)
                </label>
                <input
                  id="chunk_duration_seconds"
                  type="number"
                  value={settings.chunk_duration_seconds}
                  onChange={handleChange("chunk_duration_seconds")}
                  className="w-full bg-slate-700 p-2 rounded-md text-white"
                  min={1}
                  max={30}
                  step={0.5}
                />
              </div>

              <div>
                <label
                  htmlFor="chunk_overlap_seconds"
                  className="block text-sm font-medium mb-1"
                >
                  Chunk Overlap (seconds)
                </label>
                <input
                  id="chunk_overlap_seconds"
                  type="number"
                  value={settings.chunk_overlap_seconds}
                  onChange={handleChange("chunk_overlap_seconds")}
                  className="w-full bg-slate-700 p-2 rounded-md text-white"
                  min={0}
                  max={5}
                  step={0.1}
                />
              </div>

              <div>
                <label
                  htmlFor="target_sample_rate"
                  className="block text-sm font-medium mb-1"
                >
                  Sample Rate (Hz)
                </label>
                <input
                  id="target_sample_rate"
                  type="number"
                  value={settings.target_sample_rate}
                  onChange={handleChange("target_sample_rate")}
                  className="w-full bg-slate-700 p-2 rounded-md text-white"
                  min={8000}
                  max={96000}
                  step={1000}
                />
              </div>

              <div>
                <label
                  htmlFor="silence_threshold"
                  className="block text-sm font-medium mb-1"
                >
                  Silence Threshold
                </label>
                <input
                  id="silence_threshold"
                  type="number"
                  value={settings.silence_threshold}
                  onChange={handleChange("silence_threshold")}
                  className="w-full bg-slate-700 p-2 rounded-md text-white"
                  min={0}
                  max={1}
                  step={0.001}
                />
              </div>
            </div>
          </section>

          {/* Backend */}
          <section>
            <h3 className="text-lg font-semibold mb-2">Backend Connection</h3>
            <div>
              <label
                htmlFor="websocket_url"
                className="block text-sm font-medium mb-1"
              >
                WebSocket URL
              </label>
              <input
                id="websocket_url"
                type="text"
                value={settings.websocket_url}
                onChange={handleChange("websocket_url")}
                className="w-full bg-slate-700 p-2 rounded-md text-white"
                placeholder="ws://localhost:8000/ws"
              />
              <p className="text-xs text-slate-400 mt-1">
                This should match the WebSocket endpoint the Unity client uses.
              </p>
            </div>
          </section>
        </div>

        {/* Footer buttons */}
        <div className="flex justify-end gap-2 mt-6">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-md"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md"
          >
            Save Settings
          </button>
        </div>
      </div>
    </div>
  );
}
