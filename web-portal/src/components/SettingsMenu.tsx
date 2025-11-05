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

interface SettingsModalProps {
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
}: SettingsModalProps) {
  const [settings, setSettings] = useState(initialSettings);

  useEffect(() => {
    setSettings(initialSettings);
  }, [initialSettings]);

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>,
  ) => {
    const { name, value } = e.target;
    setSettings((prev) => ({
      ...prev,
      [name]: e.target.type === "number" ? parseFloat(value) : value,
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
          {/* Form fields */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Source Language
            </label>
            <select
              name="source_language"
              value={settings.source_language}
              onChange={handleInputChange}
              className="w-full bg-slate-700 p-2 rounded-md text-white"
            >
              <option value="en">English</option>
              <option value="es">Spanish</option>
            </select>
          </div>
        </div>

        <div className="flex justify-end space-x-3 mt-6">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-700 rounded-md"
          >
            Cancel
          </button>
          <button
            onClick={() => onSave(settings)}
            className="px-4 py-2 bg-blue-600 rounded-md"
          >
            Save Settings
          </button>
        </div>
      </div>
    </div>
  );
}
