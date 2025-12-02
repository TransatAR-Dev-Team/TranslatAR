import { useState, useEffect } from "react";

export interface Settings {
  // Backend-related (kept for compatibility, but not shown to user)
  source_language: string;
  target_language: string;
  chunk_duration_seconds: number;
  target_sample_rate: number;
  silence_threshold: number;
  chunk_overlap_seconds: number;
  websocket_url: string;

  // UX-facing
  subtitles_enabled: boolean;
  translation_enabled: boolean;
  subtitle_font_size: number;
  subtitle_style: "normal" | "bold" | "high-contrast";
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

  // Generic updater that preserves untouched fields (backend ones included)
  const updateField =
    <K extends keyof Settings>(field: K) =>
    (value: Settings[K]) => {
      setSettings((prev) => ({
        ...prev,
        [field]: value,
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
              Configure your default language pair and subtitle behavior.
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
          {/* Default Language Pair */}
          <section>
            <h3 className="text-lg font-semibold mb-2">Default Language Pair</h3>
            <p className="text-xs text-slate-300 mb-3">
              This pair is used as your default for real-time translation.
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
                  value={settings.source_language}
                  onChange={(e) =>
                    updateField("source_language")(e.target.value)
                  }
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
                  value={settings.target_language}
                  onChange={(e) =>
                    updateField("target_language")(e.target.value)
                  }
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

          {/* Live Subtitles & Translation */}
          <section>
            <h3 className="text-lg font-semibold mb-2">
              Live Subtitles & Translation
            </h3>
            <div className="space-y-3">
              {/* Toggle: subtitles */}
              <label className="flex items-center justify-between bg-slate-700/60 rounded-md px-3 py-2 cursor-pointer">
                <span className="text-sm">
                  Enable live subtitles in the headset
                </span>
                <input
                  type="checkbox"
                  className="h-4 w-4 accent-blue-500"
                  checked={settings.subtitles_enabled}
                  onChange={(e) =>
                    updateField("subtitles_enabled")(e.target.checked)
                  }
                />
              </label>

              {/* Toggle: translation */}
              <label className="flex items-center justify-between bg-slate-700/60 rounded-md px-3 py-2 cursor-pointer">
                <span className="text-sm">
                  Enable live translation (audio → text)
                </span>
                <input
                  type="checkbox"
                  className="h-4 w-4 accent-blue-500"
                  checked={settings.translation_enabled}
                  onChange={(e) =>
                    updateField("translation_enabled")(e.target.checked)
                  }
                />
              </label>
            </div>
          </section>

          {/* Subtitle appearance */}
          <section>
            <h3 className="text-lg font-semibold mb-2">Subtitle Appearance</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Font size */}
              <div>
                <label
                  htmlFor="subtitle_font_size"
                  className="block text-sm font-medium mb-1"
                >
                  Font Size (px)
                </label>
                <input
                  id="subtitle_font_size"
                  type="number"
                  min={12}
                  max={40}
                  step={1}
                  value={settings.subtitle_font_size}
                  onChange={(e) =>
                    updateField("subtitle_font_size")(
                      Number(e.target.value) || 18,
                    )
                  }
                  className="w-full bg-slate-700 p-2 rounded-md text-white"
                />
                <p className="text-xs text-slate-400 mt-1">
                  Larger sizes are easier to read in AR.
                </p>
              </div>

              {/* Style */}
              <div>
                <label
                  htmlFor="subtitle_style"
                  className="block text-sm font-medium mb-1"
                >
                  Style
                </label>
                <select
                  id="subtitle_style"
                  value={settings.subtitle_style}
                  onChange={(e) =>
                    updateField("subtitle_style")(
                      e.target.value as Settings["subtitle_style"],
                    )
                  }
                  className="w-full bg-slate-700 p-2 rounded-md text-white"
                >
                  <option value="normal">Normal</option>
                  <option value="bold">Bold</option>
                  <option value="high-contrast">High Contrast</option>
                </select>
                <p className="text-xs text-slate-400 mt-1">
                  High contrast is best for bright environments.
                </p>
              </div>
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