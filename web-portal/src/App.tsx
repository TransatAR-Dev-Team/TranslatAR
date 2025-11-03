import { useEffect, useState, useCallback, useMemo } from "react";
import { GoogleOAuthProvider } from "@react-oauth/google";
import type { GoogleIdTokenPayload } from "./models/GoogleIdTokenPayload";
import type { User } from "./models/User";
import { loginWithGoogleApi } from "./api/auth";
import GoogleLoginButton from "./components/GoogleLoginButton/GoogleLoginButton";

interface HistoryItem {
  _id: string;
  original_text: string;
  translated_text: string;
  source_lang: string;
  target_lang: string;
  timestamp: string;
}

interface Settings {
  source_language: string;
  target_language: string;
  chunk_duration_seconds: number;
  target_sample_rate: number;
  silence_threshold: number;
  chunk_overlap_seconds: number;
  websocket_url: string;
}

const LOCAL_STORAGE_USER_ID_KEY = "user_id";
const QUICK_PAIR_KEY = "quickPair";

const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
if (!googleClientId) {
  console.error("Error. VITE_GOOGLE_CLIENT_ID env variable not set.");
}

const LANGUAGES = [
  { code: "en", name: "English" },
  { code: "es", name: "Spanish" },
  { code: "fr", name: "French" },
  { code: "de", name: "German" },
  { code: "it", name: "Italian" },
  { code: "pt", name: "Portuguese" },
  { code: "ru", name: "Russian" },
  { code: "ja", name: "Japanese" },
  { code: "ko", name: "Korean" },
  { code: "zh", name: "Chinese" },
];

const codeToName = (code: string) =>
  LANGUAGES.find(l => l.code === code)?.name ?? code.toUpperCase();

function App() {
  // --- data/state ---
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [appUser, setAppUser] = useState<User | null>(null);

  const [textToSummarize, setTextToSummarize] = useState<string>("");
  const [summary, setSummary] = useState<string>("");
  const [summaryLength, setSummaryLength] = useState<string>("medium");
  const [isSummarizing, setIsSummarizing] = useState<boolean>(false);
  const [summaryError, setSummaryError] = useState<string | null>(null);

  const [settings, setSettings] = useState<Settings>({
    source_language: "en",
    target_language: "es",
    chunk_duration_seconds: 8.0,
    target_sample_rate: 48000,
    silence_threshold: 0.01,
    chunk_overlap_seconds: 0.5,
    websocket_url: "ws://localhost:8000/ws",
  });
  const [, setIsSettingsLoading] = useState(true);
  const [settingsError, setSettingsError] = useState<string | null>(null);
  const [showSettings, setShowSettings] = useState(false);

  // Connection/health
  const [connected, setConnected] = useState<boolean>(false);
  const [pingMsg, setPingMsg] = useState<string>("");

  // --- on mount ---
  useEffect(() => {
    loadHistory();
    loadSettings();

    // Restore last chosen quick pair (optional)
    const savedPair = localStorage.getItem(QUICK_PAIR_KEY);
    if (savedPair) {
      const [src, tgt] = savedPair.split("→");
      if (src && tgt) {
        setSettings((s) => ({
          ...s,
          source_language: src.toLowerCase(),
          target_language: tgt.toLowerCase(),
        }));
      }
    }

    // Initial health check + periodic ping (pseudo-live status)
    void silentPing();
    const id = setInterval(() => void silentPing(), 15000);
    return () => clearInterval(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // --- API calls ---
  const loadHistory = async () => {
    setIsLoading(true);
    try {
      const response = await fetch("/api/history");
      if (!response.ok) throw new Error("Network response was not ok");
      const data = await response.json();
      setHistory(data.history || []);
      setError(null);
    } catch (err) {
      console.error("Error fetching history:", err);
      setError("Failed to load translation history.");
    } finally {
      setIsLoading(false);
    }
  };

  const loadSettings = async () => {
    setIsSettingsLoading(true);
    try {
      const response = await fetch("/api/settings");
      if (!response.ok) throw new Error("Network response was not ok");
      const data = await response.json();
      if (data?.settings) setSettings(data.settings);
      setSettingsError(null);
    } catch (err) {
      console.error("Error fetching settings:", err);
      setSettingsError("Failed to load settings.");
    } finally {
      setIsSettingsLoading(false);
    }
  };

  const saveSettings = async (newSettings: Settings) => {
    try {
      const response = await fetch("/api/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newSettings),
      });
      if (!response.ok) throw new Error("Failed to save settings");
      const data = await response.json();
      setSettings(data.settings);
      setShowSettings(false);
      setSettingsError(null);
    } catch (err) {
      console.error("Error saving settings:", err);
      setSettingsError("Failed to save settings.");
    }
  };

  const handleSummarize = async () => {
    if (!textToSummarize.trim()) {
      setSummaryError("Please enter some text to summarize.");
      return;
    }
    setIsSummarizing(true);
    setSummaryError(null);
    setSummary("");
    try {
      const response = await fetch("/api/summarize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: textToSummarize, length: summaryLength }),
      });
      if (!response.ok) throw new Error(`Server status: ${response.status}`);
      const data = await response.json();
      setSummary(data.summary || "");
    } catch (err) {
      console.error("Error summarizing text:", err);
      setSummaryError("Failed to generate summary. Please try again.");
    } finally {
      setIsSummarizing(false);
    }
  };

  // Health check (manual)
  const handlePing = async () => {
    setPingMsg("Pinging…");
    try {
      const r = await fetch("/api/health");
      if (!r.ok) throw new Error("health failed");
      const data = await r.text();
      setConnected(true);
      setPingMsg(data || "OK");
    } catch (e) {
      console.error(e);
      setConnected(false);
      setPingMsg("Unreachable");
    } finally {
      setTimeout(() => setPingMsg(""), 2000);
    }
  };

  // Health check (silent/periodic)
  const silentPing = async () => {
    try {
      const r = await fetch("/api/health");
      setConnected(r.ok);
    } catch {
      setConnected(false);
    }
  };

  // --- Quick Pair helpers ---
  const quickPairs = ["EN→ES", "ES→EN", "EN→FR", "FR→EN", "EN→ZH", "ZH→EN"];
  const applyQuickPair = (pair: string) => {
    const [src, tgt] = pair.split("→");
    const next = {
      ...settings,
      source_language: src.toLowerCase(),
      target_language: tgt.toLowerCase(),
    };
    setSettings(next);
    localStorage.setItem(QUICK_PAIR_KEY, pair);
  };

  // --- Simple stats from history ---
  const stats = useMemo(() => {
    if (!history || history.length === 0) {
      return {
        total: 0,
        uniqueSrc: 0,
        uniqueTgt: 0,
        topPair: "—",
        lastActivity: "—",
      };
    }
  
    const srcSet = new Set<string>();
    const tgtSet = new Set<string>();
    const pairCounts = new Map<string, number>();
    let last = 0;
  
    for (const h of history) {
      srcSet.add(h.source_lang);
      tgtSet.add(h.target_lang);
  
      const pairKey = `${h.source_lang}->${h.target_lang}`;
      pairCounts.set(pairKey, (pairCounts.get(pairKey) ?? 0) + 1);
  
      const t = new Date(h.timestamp).getTime();
      if (t > last) last = t;
    }
  
    // find most-used pair
    let bestPair = "—";
    let bestCount = -1;
    for (const [pair, count] of pairCounts.entries()) {
      if (count > bestCount) {
        bestCount = count;
        bestPair = pair;
      }
    }
  
    // humanize the pair codes to names
    const [srcCode, tgtCode] = bestPair.includes("->") ? bestPair.split("->") : ["", ""];
    const prettyPair =
      srcCode && tgtCode ? `${codeToName(srcCode)} → ${codeToName(tgtCode)}` : "—";
  
    const lastDate = last > 0 ? new Date(last).toLocaleString() : "—";
  
    return {
      total: history.length,
      uniqueSrc: srcSet.size,
      uniqueTgt: tgtSet.size,
      topPair: prettyPair,
      lastActivity: lastDate,
    };
  }, [history]);
  

  // --- Auth handlers ---
  const handleLogout = useCallback(() => {
    setAppUser(null);
    localStorage.removeItem(LOCAL_STORAGE_USER_ID_KEY);
  }, []);

  const handleLoginError = useCallback(() => {
    setAppUser(null);
  }, []);

  const handleLoginSuccess = useCallback(
    async (decodedToken: GoogleIdTokenPayload) => {
      const googleId = decodedToken.sub;
      const email = decodedToken.email;
      if (!googleId || !email) {
        alert("Missing required user information!");
        return;
      }
      try {
        const fetchedUser = await loginWithGoogleApi({ googleId, email });
        if (!fetchedUser?._id) throw new Error("Invalid user data after login.");
        localStorage.setItem(LOCAL_STORAGE_USER_ID_KEY, fetchedUser._id);
        setAppUser(fetchedUser);
      } catch (err) {
        console.error("Login failed:", err);
        handleLoginError();
      }
    },
    [handleLoginError]
  );

  // --- UI ---
  return (
    <GoogleOAuthProvider clientId={googleClientId || ""}>
      <main className="bg-slate-900 min-h-screen text-white flex flex-col items-center font-sans p-4">
        <div className="w-full max-w-5xl">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3 mb-6">
            <h1 className="text-3xl font-bold">TranslatAR Web Portal</h1>
            <div className="flex items-center gap-3">
              {appUser ? (
                <>
                  <span className="text-slate-300">Welcome, {appUser.email}</span>
                  <button
                    onClick={handleLogout}
                    className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md transition-colors"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <GoogleLoginButton
                  onLoginSuccess={handleLoginSuccess}
                  onLoginError={handleLoginError}
                />
              )}
              <button
                onClick={() => setShowSettings(true)}
                className="bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded-md transition-colors"
              >
                Settings
              </button>
            </div>
          </div>

          {/* Top row: Quick Pair + Connection/Stats */}
          <div className="grid gap-6 md:grid-cols-2 mb-6">
            {/* Quick Pair */}
            <section className="bg-slate-800 rounded-lg p-5 shadow">
              <h2 className="text-xl font-semibold mb-2">Quick Pair</h2>
              <p className="text-slate-300 mb-3">
                Current pair:{" "}
                <b>
                  {settings.source_language.toUpperCase()} →{" "}
                  {settings.target_language.toUpperCase()}
                </b>
              </p>
              <div className="flex flex-wrap gap-2">
                {quickPairs.map((p) => (
                  <button
                    key={p}
                    className="px-3 py-1.5 rounded-full border border-slate-600 bg-slate-700/60 hover:bg-slate-700"
                    onClick={() => applyQuickPair(p)}
                    title="Prefill capture settings"
                  >
                    {p}
                  </button>
                ))}
              </div>
              <button
                className="mt-4 text-blue-300 underline"
                onClick={() => setShowSettings(true)}
              >
                Change languages
              </button>
            </section>

            {/* Connection + Stats */}
            <section className="bg-slate-800 rounded-lg p-5 shadow">
              <h2 className="text-xl font-semibold mb-3">Connection & Stats</h2>
              <div className="flex items-center gap-2 mb-2">
                <span
                  className={`inline-block w-2.5 h-2.5 rounded-full ${
                    connected ? "bg-green-500" : "bg-red-500"
                  }`}
                />
                <span>{connected ? "Backend reachable" : "Backend unreachable"}</span>
              </div>
              <div className="text-sm text-slate-300 mb-3">
                <div>WS URL: {settings.websocket_url || "not configured"}</div>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
                <StatTile label="Total translations" value={String(stats.total)} />
                <StatTile label="Unique source languages" value={String(stats.uniqueSrc)} />
                <StatTile label="Unique target languages" value={String(stats.uniqueTgt)} />
                <StatTile label="Most-used pair" value={stats.topPair} />
                <StatTile label="Last activity" value={stats.lastActivity} />
              </div>
              <div className="flex gap-2 items-center">
                <button
                  className="bg-slate-700 hover:bg-slate-600 px-3 py-2 rounded-md"
                  onClick={handlePing}
                >
                  Ping
                </button>
                {pingMsg && <span className="text-slate-300 text-sm">{pingMsg}</span>}
              </div>
            </section>
          </div>

          {/* Summarize panel */}
          <section className="bg-slate-800 rounded-lg p-6 shadow mb-6">
            <h2 className="text-2xl font-semibold mb-4">Summarize Text</h2>
            <textarea
              className="w-full bg-slate-700 p-3 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={6}
              value={textToSummarize}
              onChange={(e) => setTextToSummarize(e.target.value)}
              placeholder="Paste or type text here to summarize..."
            />
            <div className="flex items-center mt-4 gap-3">
              <label htmlFor="summary-length" className="font-semibold">
                Summary Length:
              </label>
              <select
                id="summary-length"
                value={summaryLength}
                onChange={(e) => setSummaryLength(e.target.value)}
                className="bg-slate-700 p-2 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="short">Short</option>
                <option value="medium">Medium</option>
                <option value="long">Long</option>
              </select>
              <button
                onClick={handleSummarize}
                disabled={isSummarizing}
                className="ml-auto bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:cursor-not-allowed text-white font-bold py-2 px-4 rounded-md"
              >
                {isSummarizing ? "Summarizing..." : "Summarize"}
              </button>
            </div>
            {summaryError && <p className="text-red-400 mt-3">{summaryError}</p>}
            {summary && (
              <div className="mt-4 bg-slate-700 p-4 rounded-md">
                <h3 className="font-semibold mb-2">Summary:</h3>
                <p>{summary}</p>
              </div>
            )}
          </section>

          {/* History panel */}
          <section className="bg-slate-800 rounded-lg p-6 shadow">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-2xl font-semibold">Translation History</h2>
              <button
                onClick={loadHistory}
                className="bg-slate-700 hover:bg-slate-600 px-3 py-2 rounded-md"
              >
                Reload
              </button>
            </div>
            {isLoading && <p>Loading history...</p>}
            {error && <p className="text-red-400">{error}</p>}
            {!isLoading && !error && (
              <div className="text-left space-y-4 max-h-96 overflow-y-auto">
                {history.length === 0 ? (
                  <p className="text-gray-400">No translations found in the database.</p>
                ) : (
                  history.map((item) => (
                    <div key={item._id} className="border-b border-slate-700 pb-2">
                      <p className="text-gray-400">
                        {item.original_text}{" "}
                        <span className="text-xs">({item.source_lang})</span>
                      </p>
                      <p className="text-lg">
                        {item.translated_text}{" "}
                        <span className="text-xs">({item.target_lang})</span>
                      </p>
                      <p className="text-xs text-slate-400">
                        {new Date(item.timestamp).toLocaleString()}
                      </p>
                    </div>
                  ))
                )}
              </div>
            )}
          </section>
        </div>

        {/* Settings Modal */}
        {showSettings && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-slate-800 rounded-lg p-6 w-full max-w-md">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-bold">Settings</h2>
                <button
                  onClick={() => setShowSettings(false)}
                  className="text-gray-400 hover:text-white text-2xl"
                  aria-label="Close Settings"
                >
                  ×
                </button>
              </div>

              {settingsError && (
                <div className="bg-red-900 text-red-200 p-3 rounded-md mb-4">
                  {settingsError}
                </div>
              )}

              <div className="space-y-4">
              {/* Source Language */}
              <div>
                <label className="block text-sm font-medium mb-2">Source Language</label>
                <select
                  value={settings.source_language}
                  onChange={(e) =>
                    setSettings({ ...settings, source_language: e.target.value })
                  }
                  className="w-full bg-slate-700 p-2 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {LANGUAGES.map((lang) => (
                    <option key={lang.code} value={lang.code}>
                      {lang.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Target Language */}
              <div>
                <label className="block text-sm font-medium mb-2">Target Language</label>
                <select
                  value={settings.target_language}
                  onChange={(e) =>
                    setSettings({ ...settings, target_language: e.target.value })
                  }
                  className="w-full bg-slate-700 p-2 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {LANGUAGES.map((lang) => (
                    <option key={lang.code} value={lang.code}>
                      {lang.name}
                    </option>
                  ))}
                </select>
              </div>


                {/* Numbers */}
                <NumberField
                  label="Chunk Duration (s)"
                  value={settings.chunk_duration_seconds}
                  step={0.5}
                  min={1}
                  max={30}
                  onChange={(v) => setSettings({ ...settings, chunk_duration_seconds: v })}
                />
                <NumberField
                  label="Sample Rate (Hz)"
                  value={settings.target_sample_rate}
                  step={1000}
                  min={8000}
                  max={96000}
                  onChange={(v) => setSettings({ ...settings, target_sample_rate: v })}
                />
                <NumberField
                  label="Silence Threshold"
                  value={settings.silence_threshold}
                  step={0.001}
                  min={0.001}
                  max={1.0}
                  onChange={(v) => setSettings({ ...settings, silence_threshold: v })}
                />
                <NumberField
                  label="Chunk Overlap (s)"
                  value={settings.chunk_overlap_seconds}
                  step={0.1}
                  min={0.1}
                  max={5.0}
                  onChange={(v) => setSettings({ ...settings, chunk_overlap_seconds: v })}
                />
                <div>
                  <label className="block text-sm font-medium mb-2">WebSocket URL</label>
                  <input
                    type="text"
                    value={settings.websocket_url}
                    onChange={(e) =>
                      setSettings({ ...settings, websocket_url: e.target.value })
                    }
                    className="w-full bg-slate-700 p-2 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="ws://localhost:8000/ws"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-2 mt-6">
                <button
                  className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-md"
                  onClick={() => setShowSettings(false)}
                >
                  Cancel
                </button>
                <button
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-md"
                  onClick={() => saveSettings(settings)}
                >
                  Save Settings
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </GoogleOAuthProvider>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-slate-700 bg-slate-700/50 p-3">
      <div className="text-xl font-bold">{value}</div>
      <div className="text-slate-300 text-xs">{label}</div>
    </div>
  );
}

function StatTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-slate-700 bg-slate-700/40 p-4">
      <div className="text-sm text-slate-300">{label}</div>
      <div className="text-xl font-bold mt-1">{value}</div>
    </div>
  );
}

function NumberField({
  label,
  value,
  onChange,
  step,
  min,
  max,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  step: number;
  min: number;
  max: number;
}) {
  return (
    <div>
      <label className="block text-sm font-medium mb-2">{label}</label>
      <input
        type="number"
        value={value}
        step={step}
        min={min}
        max={max}
        onChange={(e) => onChange(parseFloat(e.target.value) || 0)}
        className="w-full bg-slate-700 p-2 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
    </div>
  );
}

export default App;
