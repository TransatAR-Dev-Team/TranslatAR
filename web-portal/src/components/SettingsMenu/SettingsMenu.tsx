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

export default function SettingsMenu({
  initialSettings,
  onSave,
  onClose,
  error,
}: SettingsMenuProps) {
  const [settings, setSettings] = useState(initialSettings);

  useEffect(() => {
    setSettings(initialSettings);
  }, [initialSettings]);

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>,
  ) => {
    const { name, value, type } = e.target;
    // Handle number inputs correctly
    const isNumberField = type === "number";
    setSettings((prev) => ({
      ...prev,
      [name]: isNumberField ? parseFloat(value) : value,
    }));
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-slate-800 rounded-lg p-6 w-full max-w-md mx-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold">Settings</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white text-2xl"
          >
            ×
          </button>
        </div>

        {error && (
          <div className="bg-red-900 text-red-200 p-3 rounded-md mb-4">
            {error}
          </div>
        )}

        <div className="space-y-4">
          <div>
            <label
              htmlFor="source_language"
              className="block text-sm font-medium mb-2"
            >
              Source Language
            </label>
            <select
              id="source_language"
              name="source_language"
              value={settings.source_language}
              onChange={handleInputChange}
              className="w-full bg-slate-700 p-2 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="en">English</option>
              <option value="es">Spanish</option>
              <option value="fr">French</option>
            </select>
          </div>

          <div>
            <label
              htmlFor="target_language"
              className="block text-sm font-medium mb-2"
            >
              Target Language
            </label>
            <select
              id="target_language"
              name="target_language"
              value={settings.target_language}
              onChange={handleInputChange}
              className="w-full bg-slate-700 p-2 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="en">English</option>
              <option value="es">Spanish</option>
              <option value="fr">French</option>
            </select>
          </div>

          <div>
            <label
              htmlFor="chunk_duration_seconds"
              className="block text-sm font-medium mb-2"
            >
              Chunk Duration (seconds)
            </label>
            <input
              type="number"
              id="chunk_duration_seconds"
              name="chunk_duration_seconds"
              value={settings.chunk_duration_seconds}
              onChange={handleInputChange}
              className="w-full bg-slate-700 p-2 rounded-md text-white"
            />
          </div>
        </div>

        <div className="flex justify-end space-x-3 mt-6">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-md"
          >
            Cancel
          </button>
          <button
            onClick={() => onSave(settings)}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md"
          >
            Save Settings
          </button>
        </div>
      </div>
    </div>
  );
}
