import { act, use, useEffect, useRef, useState } from 'react';

interface HistoryItem {
  _id: string;
  conversation_id: string;
  username?: string;
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
  const [history, setHistory] = useState<Record<string, HistoryItem[]>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [activeConversation, setActiveConversation] = useState<string | null>(null);

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
    websocket_url: 'ws://localhost:8000/ws',
  });

  // TODO: add isSettingsLoading variable
  const [, setIsSettingsLoading] = useState(true);
  const [settingsError, setSettingsError] = useState<string | null>(null);
  const [showSettings, setShowSettings] = useState(false);

   
  const [expandedConversations, setExpandedConversations] = useState<{ [id: string]: boolean }>({});


  useEffect(() => {
    loadHistory();
    loadSettings();
  }, []);

  const groupByConversation = (history: HistoryItem[]) => {
    const grouped: { [key: string]: HistoryItem[] } = {};
    for (const item of history) {
      if (!grouped[item.conversation_id]) grouped[item.conversation_id] = [];
      grouped[item.conversation_id].push(item);
    }
    return grouped;
  };

  const loadHistory = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/history');
      if (!response.ok) throw new Error('Network response was not ok');
      const data = await response.json();

      const grouped = groupByConversation(data.history);
      setHistory(grouped);

      // Open the latest conversation by default
      const latest = Object.keys(grouped)[0] || null;
      setActiveConversation(latest);

    } catch (error) {
      console.error('Error fetching data:', error);
      setError('Failed to load translation history.');
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
    } catch (error) {
      console.error('Error fetching settings:', error);
      setSettingsError('Failed to load settings.');
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
    } catch (error) {
      console.error('Error saving settings:', error);
      setSettingsError('Failed to save settings.');
    }
  };

  const handleSummarize = async () => {
    if (!textToSummarize.trim()) {
      setSummaryError('Please enter some text to summarize.');
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
      console.error('Error summarizing text:', error);
      setSummaryError('Failed to generate summary. Please try again.');
    } finally {
      setIsSummarizing(false);
    }
  };

  const toggleConversation = (conversationId: string) => {
    setExpandedConversations((prev) => ({
      ...prev,
      [conversationId]: !prev[conversationId],
    }));
  };


  return (
    <main className="bg-slate-900 min-h-screen flex flex-col items-center font-sans p-4 text-white">
      <div className="w-full max-w-2xl">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold">TranslatAR Web Portal</h1>
          <button
            onClick={() => setShowSettings(true)}
            className="bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded-md transition-colors duration-200"
          >
            Settings
          </button>
        </div>

        <div className="bg-slate-800 rounded-lg p-6 shadow-lg mb-8">
          <h2 className="text-2xl font-semibold mb-4 text-left">
            Summarize Text
          </h2>
          <textarea
            className="w-full bg-slate-700 p-3 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={6}
            value={textToSummarize}
            onChange={(e) => setTextToSummarize(e.target.value)}
            placeholder="Paste or type text here to summarize..."
          />

          <div className="flex items-center mt-4 space-x-4">
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

        <div className="bg-slate-800 rounded-lg p-6 shadow-lg">
          <h2 className="text-2xl font-semibold mb-4 text-left">
            Translation History
          </h2>

          {isLoading && <p>Loading history...</p>}
          {error && <p className="text-red-400">{error}</p>}

          {!isLoading && !error && (
            <div className="text-left max-h-[600px] overflow-y-auto w-full max-w-3xl p-4 bg-slate-700 rounded-md">
              {Object.keys(history).length === 0 ? (
                <p className="text-gray-400">No translations found in the database.</p>
              ) : (
                <>
                  {/* Conversation Tabs */}
                  <div className="sticky top-0 z-20 bg-slate-800 py-2 border-b border-slate-600 flex items-center gap-2">
                    <button
                      onClick={() => {
                        const container = document.getElementById("conversationTabs");
                        if (container) container.scrollLeft -= 150;
                      }}
                      className="bg-slate-600 hover:bg-slate-500 text-white rounded-full px-2 py-1"
                    >
                      ←
                    </button>
                    <div
                      id="conversationTabs"
                      className="flex space-x-2 overflow-x-auto no-scrollbar flex-1"
                    >
                    {Object.keys(history).map((conversationId) => (
                      <button
                        id={`tab-${conversationId}`}
                        key={conversationId}
                        onClick={() => {
                          setActiveConversation(conversationId);
                          const container = document.getElementById("conversationTabs");
                          const tab = document.getElementById(`tab-${conversationId}`);
                          if (container && tab) {
                            const containerRect = container.getBoundingClientRect();
                            const tabRect = tab.getBoundingClientRect();
                            container.scrollBy({
                              left: tabRect.left - containerRect.left - containerRect.width / 2 + tabRect.width / 2,
                              behavior: 'smooth',
                            })
                          }
                        }}
                        className={`px-3 py-1 rounded-md text-sm font-medium transition relative ${
                          activeConversation === conversationId
                            ? "bg-blue-500 text-white"
                            : "bg-slate-600 text-gray-300 hover:bg-slate-500"
                        }`}
                      >
                        Conversation {conversationId.slice(0, 6)}...
                        {activeConversation === conversationId && (
                          <span className="absolute bottom-0 left-0 w-full h-1 bg-blue-300 rounded-full animate-pulse"></span>
                        )}

                      </button>
                    ))}
                    </div>
                  <button
                    onClick={() => {
                      const container = document.getElementById("conversationTabs");
                      if (container) container.scrollLeft += 150;
                    }}
                    className="bg-slate-600 hover:bg-slate-500 text-white rounded-full px-2 py-1"
                  >
                    →
                  </button>
                </div>

                  {/*Active Conversation Display */}
                  {activeConversation ? (
                    <div className="space-y-3">
                      {history[activeConversation].map((item) => (
                        <div
                          key={item._id}
                          className="border-b border-slate-600 pb-2"
                        >
                          <p className="text-gray-400">
                            {item.original_text}{" "}
                            <span className="text-xs">({item.source_lang})</span>
                          </p>
                          <p className="text-lg">
                            {item.translated_text}{" "}
                            <span className="text-xs">({item.target_lang})</span>
                          </p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-400">Select a conversation to view messages.</p>
                  )}
                </>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Settings Modal */}
      {showSettings && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
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
                <label className="block text-sm font-medium mb-2">
                  Source Language
                </label>
                <select
                  value={settings.source_language}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      source_language: e.target.value,
                    })
                  }
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
                <label className="block text-sm font-medium mb-2">
                  Target Language
                </label>
                <select
                  value={settings.target_language}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      target_language: e.target.value,
                    })
                  }
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
                <label className="block text-sm font-medium mb-2">
                  Chunk Duration (seconds)
                </label>
                <input
                  type="number"
                  value={settings.chunk_duration_seconds}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      chunk_duration_seconds: parseFloat(e.target.value) || 8.0,
                    })
                  }
                  className="w-full bg-slate-700 p-2 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  step="0.5"
                  min="1"
                  max="30"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Sample Rate (Hz)
                </label>
                <input
                  type="number"
                  value={settings.target_sample_rate}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      target_sample_rate: parseInt(e.target.value) || 48000,
                    })
                  }
                  className="w-full bg-slate-700 p-2 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  step="1000"
                  min="8000"
                  max="96000"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Silence Threshold
                </label>
                <input
                  type="number"
                  value={settings.silence_threshold}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      silence_threshold: parseFloat(e.target.value) || 0.01,
                    })
                  }
                  className="w-full bg-slate-700 p-2 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  step="0.001"
                  min="0.001"
                  max="1.0"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Chunk Overlap (seconds)
                </label>
                <input
                  type="number"
                  value={settings.chunk_overlap_seconds}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      chunk_overlap_seconds: parseFloat(e.target.value) || 0.5,
                    })
                  }
                  className="w-full bg-slate-700 p-2 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  step="0.1"
                  min="0.1"
                  max="5.0"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  WebSocket URL
                </label>
                <input
                  type="text"
                  value={settings.websocket_url}
                  onChange={(e) =>
                    setSettings({ ...settings, websocket_url: e.target.value })
                  }
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
