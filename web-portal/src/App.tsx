import { useEffect, useState } from 'react';

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

function App() {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [textToSummarize, setTextToSummarize] = useState<string>('');
  const [summary, setSummary] = useState<string>('');
  const [summaryLength, setSummaryLength] = useState<string>('medium');
  const [isSummarizing, setIsSummarizing] = useState<boolean>(false);
  const [summaryError, setSummaryError] = useState<string | null>(null);

  const [settings, setSettings] = useState<Settings>({
    source_language: 'en',
    target_language: 'es',
    chunk_duration_seconds: 8.0,
    target_sample_rate: 48000,
    silence_threshold: 0.01,
    chunk_overlap_seconds: 0.5,
    websocket_url: 'ws://localhost:8000/ws'
  });
  const [isSettingsLoading, setIsSettingsLoading] = useState(true);
  const [settingsError, setSettingsError] = useState<string | null>(null);
  const [showSettings, setShowSettings] = useState(false);

  // NEW: connection + ping UI state
  const [connected, setConnected] = useState<boolean>(false);
  const [pingMsg, setPingMsg] = useState<string>('');

  useEffect(() => {
    loadHistory();
    loadSettings();
  }, []);

  // NEW: restore quickPair preset on mount
  useEffect(() => {
    const savedPair = localStorage.getItem('quickPair');
    if (savedPair) {
      const [src, tgt] = savedPair.split('→');
      if (src && tgt) {
        setSettings(s => ({
          ...s,
          source_language: src.toLowerCase(),
          target_language: tgt.toLowerCase(),
        }));
      }
    }
  }, []);

  // NEW: update naive connection state whenever ws url looks set
  useEffect(() => {
    setConnected(Boolean(settings.websocket_url));
  }, [settings.websocket_url]);

  const loadHistory = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/history');
      if (!response.ok) throw new Error('Network response was not ok');
      const data = await response.json();
      setHistory(data.history);
      setError(null);
    } catch (error) {
      console.error("Error fetching data:", error);
      setError("Failed to load translation history.");
    } finally {
      setIsLoading(false);
    }
  };

  const loadSettings = async () => {
    setIsSettingsLoading(true);
    try {
      const response = await fetch('/api/settings');
      if (!response.ok) throw new Error('Network response was not ok');
      const data = await response.json();
      setSettings(data.settings);
      setSettingsError(null);
    } catch (error) {
      console.error("Error fetching settings:", error);
      setSettingsError("Failed to load settings.");
    } finally {
      setIsSettingsLoading(false);
    }
  };

  const saveSettings = async (newSettings: Settings) => {
    try {
      const response = await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newSettings),
      });

      if (!response.ok) throw new Error('Failed to save settings');
      const data = await response.json();
      setSettings(data.settings);
      setShowSettings(false);
      setSettingsError(null);
    } catch (error) {
      console.error("Error saving settings:", error);
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
    setSummary('');

    try {
      const response = await fetch('/api/summarize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: textToSummarize, length: summaryLength }),
      });

      if (!response.ok) {
        throw new Error(`Server responded with status: ${response.status}`);
      }

      const data = await response.json();
      setSummary(data.summary);

    } catch (error) {
      console.error("Error summarizing text:", error);
      setSummaryError("Failed to generate summary. Please try again.");
    } finally {
      setIsSummarizing(false);
    }
  };

  // NEW: /api/health ping
  const handlePing = async () => {
    setPingMsg('Pinging…');
    try {
      const r = await fetch('/api/health');
      if (!r.ok) throw new Error('health failed');
      const text = await r.text();
      setConnected(true);
      setPingMsg(text || 'OK');
    } catch (e) {
      console.error(e);
      setConnected(false);
      setPingMsg('Unreachable');
    } finally {
      setTimeout(() => setPingMsg(''), 1800);
    }
  };

  return (
    <main className="bg-slate-900 min-h-screen flex flex-col items-center font-sans p-4 text-white">
      <div className="w-full max-w-2xl">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold">TranslatAR Web Portal</h1>
          <button
            onClick={() => setShowSettings(true)}
            className="bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded-md transition-colors duration-200"
          >
            Settings
          </button>
        </div>

        {/* NEW: Mini dashboard row (Quick Start / Connection / Quick Pair) */}
        <div className="grid gap-4 mb-8">
          {/* Quick Start (pair only + open settings) */}
          <section className="bg-slate-800 rounded-lg p-4 shadow">
            <h2 className="text-xl font-semibold mb-2 text-left">Quick Start</h2>
            <p className="text-slate-300 mb-2">
              Current pair:&nbsp;
              <b>{settings.source_language.toUpperCase()} → {settings.target_language.toUpperCase()}</b>
            </p>
            <button
              className="text-blue-300 underline"
              onClick={() => setShowSettings(true)}
            >
              Change languages
            </button>
          </section>

          {/* Connection (status + WS URL + ping) */}
          <section className="bg-slate-800 rounded-lg p-4 shadow">
            <h2 className="text-xl font-semibold mb-2 text-left">Connection</h2>
            <div className="flex items-center gap-2 mb-1">
              <span className={`inline-block w-2.5 h-2.5 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`} />
              <span>{connected ? 'Connected' : 'Disconnected'}</span>
            </div>
            <div className="text-sm text-slate-300 break-all">
              <span className="text-slate-400">WS URL:&nbsp;</span>
              {settings.websocket_url || 'not configured'}
            </div>
            <div className="mt-3 flex items-center gap-3">
              <button
                onClick={() => setShowSettings(true)}
                className="bg-slate-700 hover:bg-slate-600 px-3 py-1.5 rounded-md"
              >
                Configure backend
              </button>
              <button
                onClick={handlePing}
                className="bg-slate-700 hover:bg-slate-600 px-3 py-1.5 rounded-md"
              >
                Ping
              </button>
              {pingMsg && <span className="text-slate-300 text-sm">{pingMsg}</span>}
            </div>
          </section>

          {/* Quick Pair presets */}
          <section className="bg-slate-800 rounded-lg p-4 shadow">
            <h2 className="text-xl font-semibold mb-2 text-left">Quick Pair</h2>
            <div className="flex flex-wrap gap-2">
              {['EN→ES','EN→FR','EN→DE','EN→ZH','ES→EN','FR→EN'].map(p => (
                <button
                  key={p}
                  className="px-3 py-1.5 rounded-full border border-slate-600 bg-slate-700/60 hover:bg-slate-700"
                  onClick={() => {
                    const [src, tgt] = p.split('→');
                    const next = { ...settings, source_language: src.toLowerCase(), target_language: tgt.toLowerCase() };
                    setSettings(next);
                    localStorage.setItem('quickPair', p);
                  }}
                  title="Prefill languages"
                >
                  {p}
                </button>
              ))}
            </div>
            <p className="text-slate-400 text-xs mt-2">Your last pick is remembered.</p>
          </section>
        </div>

        {/* Summarize (unchanged) */}
        <div className="bg-slate-800 rounded-lg p-6 shadow-lg mb-8">
          <h2 className="text-2xl font-semibold mb-4 text-left">Summarize Text</h2>
          <textarea
            className="w-full bg-slate-700 p-3 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={6}
            value={textToSummarize}
            onChange={(e) => setTextToSummarize(e.target.value)}
            placeholder="Paste or type text here to summarize..."
          />

          <div className="flex items-center mt-4 space-x-4">
            <label htmlFor="summary-length" className="font-semibold">Summary Length:</label>
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
          </div>

          <button
            onClick={handleSummarize}
            disabled={isSummarizing}
            className="mt-4 w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:cursor-not-allowed text-white font-bold py-2 px-4 rounded-md transition-colors duration-200"
          >
            {isSummarizing ? 'Summarizing...' : 'Summarize'}
          </button>

          {summaryError && <p className="text-red-400 mt-4">{summaryError}</p>}
          {summary && (
            <div className="mt-4 bg-slate-700 p-4 rounded-md">
              <h3 className="font-semibold mb-2">Summary:</h3>
              <p>{summary}</p>
            </div>
          )}
        </div>

        {/* Translation History + Reload */}
        <div className="bg-slate-800 rounded-lg p-6 shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-semibold text-left">Translation History</h2>
            <button
              onClick={loadHistory}
              className="text-blue-300 underline"
              title="Reload history"
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
                      {item.original_text}{' '}
                      <span className="text-xs">({item.source_lang})</span>
                    </p>
                    <p className="text-lg">
                      {item.translated_text}{' '}
                      <span className="text-xs">({item.target_lang})</span>
                    </p>
                    <p className="text-xs text-slate-400 mt-1">
                      {new Date(item.timestamp).toLocaleString()}
                    </p>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>

      {/* Settings Modal (unchanged behavior) */}
      {showSettings && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" role="dialog" aria-modal="true">
          <div className="bg-slate-800 rounded-lg p-6 w-full max-w-md mx-4">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold">Settings</h2>
              <button
                onClick={() => setShowSettings(false)}
                className="text-gray-400 hover:text-white text-2xl"
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
              <div>
                <label className="block text-sm font-medium mb-2">Source Language</label>
                <select
                  value={settings.source_language}
                  onChange={(e) => setSettings({...settings, source_language: e.target.value})}
                  className="w-full bg-slate-700 p-2 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="en">English</option>
                  <option value="es">Spanish</option>
                  <option value="fr">French</option>
                  <option value="de">German</option>
                  <option value="it">Italian</option>
                  <option value="pt">Portuguese</option>
                  <option value="ru">Russian</option>
                  <option value="ja">Japanese</option>
                  <option value="ko">Korean</option>
                  <option value="zh">Chinese</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Target Language</label>
                <select
                  value={settings.target_language}
                  onChange={(e) => setSettings({...settings, target_language: e.target.value})}
                  className="w-full bg-slate-700 p-2 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="en">English</option>
                  <option value="es">Spanish</option>
                  <option value="fr">French</option>
                  <option value="de">German</option>
                  <option value="it">Italian</option>
                  <option value="pt">Portuguese</option>
                  <option value="ru">Russian</option>
                  <option value="ja">Japanese</option>
                  <option value="ko">Korean</option>
                  <option value="zh">Chinese</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Chunk Duration (seconds)</label>
                <input
                  type="number"
                  value={settings.chunk_duration_seconds}
                  onChange={(e) => setSettings({...settings, chunk_duration_seconds: parseFloat(e.target.value) || 8.0})}
                  className="w-full bg-slate-700 p-2 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  step="0.5"
                  min="1"
                  max="30"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Sample Rate (Hz)</label>
                <input
                  type="number"
                  value={settings.target_sample_rate}
                  onChange={(e) => setSettings({...settings, target_sample_rate: parseInt(e.target.value) || 48000})}
                  className="w-full bg-slate-700 p-2 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  step="1000"
                  min="8000"
                  max="96000"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Silence Threshold</label>
                <input
                  type="number"
                  value={settings.silence_threshold}
                  onChange={(e) => setSettings({...settings, silence_threshold: parseFloat(e.target.value) || 0.01})}
                  className="w-full bg-slate-700 p-2 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  step="0.001"
                  min="0.001"
                  max="1.0"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Chunk Overlap (seconds)</label>
                <input
                  type="number"
                  value={settings.chunk_overlap_seconds}
                  onChange={(e) => setSettings({...settings, chunk_overlap_seconds: parseFloat(e.target.value) || 0.5})}
                  className="w-full bg-slate-700 p-2 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  step="0.1"
                  min="0.1"
                  max="5.0"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">WebSocket URL</label>
                <input
                  type="text"
                  value={settings.websocket_url}
                  onChange={(e) => setSettings({...settings, websocket_url: e.target.value})}
                  className="w-full bg-slate-700 p-2 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="ws://localhost:8000/ws"
                />
              </div>
            </div>

            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowSettings(false)}
                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-md transition-colors duration-200"
              >
                Cancel
              </button>
              <button
                onClick={() => saveSettings(settings)}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors duration-200"
              >
                Save Settings
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}

export default App;
