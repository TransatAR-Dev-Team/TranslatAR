import { useEffect, useState, useCallback } from "react";
import { GoogleOAuthProvider } from "@react-oauth/google";
import type { GoogleIdTokenPayload } from "./models/GoogleIdTokenPayload";
import type { User } from "./models/User";
import { loginWithGoogleApi } from "./api/auth";
import GoogleLoginButton from "./components/GoogleLoginButton/GoogleLoginButton";

interface HistoryItem {
  _id: string;
  user_name: string;
  conversation_id: string;
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

const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
if (!googleClientId) {
  console.error("Error. VITE_GOOGLE_CLIENT_ID env variable not set.");
}

function App() {
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

  // TODO: add isSettingsLoading variable
  const [, setIsSettingsLoading] = useState(true);
  const [settingsError, setSettingsError] = useState<string | null>(null);
  const [showSettings, setShowSettings] = useState(false);

  useEffect(() => {
    // Load both history and settings on component mount
    localStorage.setItem('username', 'john'); // For testing purposes john is hardcoded as the username
    loadHistory();
    loadSettings();
    
  }, []);

  const loadHistory = async () => {
    setIsLoading(true);
    const username = localStorage.getItem('username')
    if(!username) return;
    try {
      const formData = new FormData();
      formData.append('username', username);
      const response = await fetch('/api/history/', {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) throw new Error('Network response was not ok');
      const data = await response.json();
      setHistory(data.history);
    } catch (error) {
      console.error("Error fetching data:", error);
      setError("Failed to load translation history.");
    } finally {
      setIsLoading(false);
    }
  };

  const loadSettings = async () => {
    try {
      const response = await fetch("/api/settings");
      if (!response.ok) throw new Error("Network response was not ok");
      const data = await response.json();
      setSettings(data.settings);
    } catch (error) {
      console.error("Error fetching settings:", error);
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
    setSummary("");

    try {
      const response = await fetch("/api/summarize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
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

  // Login state handlers
  const handleLogout = useCallback(() => {
    console.log("User logged out");
    setAppUser(null);
    localStorage.removeItem(LOCAL_STORAGE_USER_ID_KEY);
  }, []);

  const handleLoginError = useCallback(() => {
    console.log("Logging user out.");
    setAppUser(null);
  }, []);

  const handleLoginSuccess = useCallback(
    async (decodedToken: GoogleIdTokenPayload) => {
      console.log("Attempting Google login...");
      const googleId = decodedToken.sub;
      const email = decodedToken.email;

      console.log("Token Data:", { googleID: googleId, email });

      if (!googleId || !email) {
        alert("Missing required user information!");
        return;
      }

      try {
        const loginPayload = { googleId, email };
        const fetchedUser = await loginWithGoogleApi(loginPayload);

        if (!fetchedUser?._id) {
          console.error(
            "Login Error: Invalid user data received from backend.",
          );
          throw new Error("Invalid user data received after login.");
        }

        localStorage.setItem(LOCAL_STORAGE_USER_ID_KEY, fetchedUser._id);
        setAppUser(fetchedUser);
        console.log(`User logged in: ${fetchedUser.email}`);
      } catch (error) {
        console.error("Login failed:", error);
        handleLoginError();
      }
    },
    [handleLoginError],
  );

  return (
    <GoogleOAuthProvider clientId={googleClientId || ""}>
      <main className="bg-slate-900 min-h-screen flex flex-col items-center font-sans p-4 text-white">
        <div className="w-full max-w-2xl">
          <div className="flex justify-between items-center mb-8">
            <h1 className="text-4xl font-bold">TranslatAR Web Portal</h1>
            <div className="flex items-center space-x-4">
              {appUser ? (
                // Logged in state
                <>
                  <span className="text-gray-300">
                    Welcome, {appUser.email}
                  </span>
                  <button
                    onClick={handleLogout}
                    className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md transition-colors duration-200"
                  >
                    Logout
                  </button>
                </>
              ) : (
                // Logged out state
                <GoogleLoginButton
                  onLoginSuccess={handleLoginSuccess}
                  onLoginError={handleLoginError}
                />
              )}
              <button
                onClick={() => setShowSettings(true)}
                className="bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded-md transition-colors duration-200"
              >
                Settings
              </button>
            </div>
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
              {isSummarizing ? "Summarizing..." : "Summarize"}
            </button>

            {summaryError && (
              <p className="text-red-400 mt-4">{summaryError}</p>
            )}
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
              <div className="text-left space-y-4 max-h-96 overflow-y-auto">
                {history.length === 0 ? (
                  <p className="text-gray-400">
                    No translations found in the database.
                  </p>
                ) : (
                  history.map((item) => (
                    <div
                      key={item._id}
                      className="border-b border-slate-700 pb-2"
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
                  ))
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
                        chunk_duration_seconds:
                          parseFloat(e.target.value) || 8.0,
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
                        chunk_overlap_seconds:
                          parseFloat(e.target.value) || 0.5,
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
                      setSettings({
                        ...settings,
                        websocket_url: e.target.value,
                      })
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
    </GoogleOAuthProvider>
  );
}

export default App;
