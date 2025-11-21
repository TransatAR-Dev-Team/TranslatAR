import { useEffect, useState, useCallback } from "react";
import { GoogleOAuthProvider } from "@react-oauth/google";
import type { CredentialResponse } from "@react-oauth/google";

import type { User } from "./models/User";
import { loginWithGoogleApi, getMeApi } from "./api/auth";

import Header from "./components/Header/Header";
import Summarizer from "./components/Summarizer/Summarizer";
import HistoryPanel from "./components/HistoryPanel/HistoryPanel";
import SettingsMenu, {
  type Settings,
} from "./components/SettingsMenu/SettingsMenu";
import SideNavigation, {
  type TabKey,
} from "./components/Sidebar/NavigationSidebar";
import TranslationView from "./components/TranslationView/TranslationView";

const LOCAL_STORAGE_JWT_KEY = "translatar_jwt";
const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
if (!googleClientId) {
  console.error("Error: VITE_GOOGLE_CLIENT_ID env variable not set.");
}

const DEFAULT_SETTINGS: Settings = {
  // Backend-related
  source_language: "en",
  target_language: "es",
  chunk_duration_seconds: 8.0,
  target_sample_rate: 48000,
  silence_threshold: 0.01,
  chunk_overlap_seconds: 0.5,
  websocket_url: "ws://localhost:8000/ws",

  // UX-facing fields
  subtitles_enabled: true,
  translation_enabled: true,
  subtitle_font_size: 18,
  subtitle_style: "normal",
};

function App() {
  const [appUser, setAppUser] = useState<User | null>(null);

  const [history, setHistory] = useState<any[]>([]);
  const [isHistoryLoading, setIsHistoryLoading] = useState(true);
  const [historyError, setHistoryError] = useState<string | null>(null);

  const [logs, setLogs] = useState<any[]>([]);
  const [isLogsLoading, setIsLogsLoading] = useState(true);
  const [logsError, setLogsError] = useState<string | null>(null);

  const [settings, setSettings] = useState<Settings>(DEFAULT_SETTINGS);
  const [settingsError, setSettingsError] = useState<string | null>(null);
  const [showSettings, setShowSettings] = useState(false);

  const [showNavigation, setShowNavigation] = useState(false);
  const [activeTab, setActiveTab] = useState<TabKey>("dashboard");

  const handleLogout = useCallback(() => {
    setAppUser(null);
    localStorage.removeItem(LOCAL_STORAGE_JWT_KEY);
    console.log("User logged out.");
  }, []);

  const fetchUserProfile = useCallback(
    async (token: string) => {
      try {
        const userProfile = await getMeApi(token);
        setAppUser(userProfile);
        console.log(`User profile loaded: ${userProfile.email}`);
      } catch (error) {
        console.error("Failed to fetch user profile:", error);
        handleLogout();
      }
    },
    [handleLogout],
  );

  const loadHistory = useCallback(async () => {
    setIsHistoryLoading(true);
    setHistoryError(null);
    const token = localStorage.getItem(LOCAL_STORAGE_JWT_KEY);
    if (!token) {
      setHistory([]);
      setIsHistoryLoading(false);
      return;
    }
    try {
      const response = await fetch("/api/history", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) throw new Error("Network response was not ok");
      const data = await response.json();
      setHistory(data.history);
    } catch (error) {
      console.error("Error fetching history:", error);
      setHistoryError("Failed to load translation history.");
    } finally {
      setIsHistoryLoading(false);
    }
  }, []);

  const loadLogs = useCallback(async () => {
    setIsLogsLoading(true);
    setLogsError(null);
    try {
      const response = await fetch("/api/transcripts", { method: "POST" });
      if (!response.ok) throw new Error("Network response was not ok");
      const data = await response.json();
      setLogs(data);
    } catch (error) {
      console.error("Error fetching logs:", error);
      setLogsError("Failed to load transcription logs.");
    } finally {
      setIsLogsLoading(false);
    }
  }, []);

  const loadSettings = useCallback(async () => {
    setSettingsError(null);
    const token = localStorage.getItem(LOCAL_STORAGE_JWT_KEY);
    if (!token) {
      setSettings(DEFAULT_SETTINGS);
      return;
    }
    try {
      const response = await fetch("/api/settings", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) throw new Error("Network response was not ok");
      const data = await response.json();
      setSettings({ ...DEFAULT_SETTINGS, ...(data.settings ?? {}) });
    } catch (error) {
      console.error("Error fetching settings:", error);
      setSettingsError("Failed to load settings.");
    }
  }, []);

  const saveSettings = useCallback(
    async (newSettings: Settings) => {
      setSettingsError(null);
      const token = localStorage.getItem(LOCAL_STORAGE_JWT_KEY);
      if (!token) {
        setSettingsError("You must be logged in to save settings.");
        return;
      }

      try {
        const response = await fetch("/api/settings", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(newSettings),
        });

        if (!response.ok) throw new Error("Failed to save settings");

        // After a successful save, re-fetch the settings to ensure UI consistency.
        await loadSettings();
        setShowSettings(false);
      } catch (error) {
        console.error("Error saving settings:", error);
        setSettingsError("Failed to save settings. Please try again.");
      }
    },
    [loadSettings],
  );

  useEffect(() => {
    const initialize = async () => {
      const token = localStorage.getItem(LOCAL_STORAGE_JWT_KEY);
      if (token) {
        await fetchUserProfile(token);
      }
      await Promise.all([loadSettings(), loadHistory(), loadLogs()]);
    };
    void initialize();
  }, [fetchUserProfile, loadSettings, loadHistory, loadLogs]);

  useEffect(() => {
    if (appUser) {
      loadHistory();
      loadLogs();
      loadSettings(); // Reload settings on login
    } else {
      setHistory([]);
      setLogs([]);
      setSettings(DEFAULT_SETTINGS); // Reset to defaults on logout
    }
  }, [appUser, loadHistory, loadLogs, loadSettings]);

  const handleLoginSuccess = useCallback(
    async (credentialResponse: CredentialResponse) => {
      const googleIdToken = credentialResponse.credential;
      if (!googleIdToken) {
        alert("Missing required token from Google!");
        return handleLogout();
      }
      try {
        const { access_token } = await loginWithGoogleApi(googleIdToken);
        localStorage.setItem(LOCAL_STORAGE_JWT_KEY, access_token);
        await fetchUserProfile(access_token);
      } catch (error) {
        console.error("Login process failed:", error);
        alert("Login failed. Please try again.");
        handleLogout();
      }
    },
    [fetchUserProfile, handleLogout],
  );

  return (
    <GoogleOAuthProvider clientId={googleClientId || ""}>
      <main className="bg-slate-900 min-h-screen flex flex-col items-center font-sans p-4 text-white">
        <div className="w-full max-w-2xl">
          <Header
            appUser={appUser}
            onLoginSuccess={handleLoginSuccess}
            onLoginError={handleLogout}
            onLogout={handleLogout}
            onShowSettings={() => setShowSettings(true)}
            onShowNavigation={() => setShowNavigation(true)}
          />

          {activeTab === "dashboard" && (
            <div className="bg-slate-800 rounded-lg p-6 shadow-lg">
              <h2 className="text-2xl font-semibold mb-2">Dashboard</h2>
              <p className="text-slate-300 text-sm">
                Overview coming soon. Use the sidebar to jump to other pages.
              </p>
            </div>
          )}

          {activeTab === "live_translation" && (
            <TranslationView settings={settings} /> // Pass the settings prop
          )}

          {activeTab === "summarization" && <Summarizer />}

          {activeTab === "conversations" && (
            <HistoryPanel
              history={history}
              isLoading={isHistoryLoading}
              error={historyError}
            />
          )}
        </div>

        {/* Settings modal */}
        {showSettings && (
          <SettingsMenu
            initialSettings={settings}
            onSave={saveSettings}
            onClose={() => setShowSettings(false)}
            error={settingsError}
          />
        )}

        {/* Sidebar navigation */}
        <SideNavigation
          isOpen={showNavigation}
          activeTab={activeTab}
          onClose={() => setShowNavigation(false)}
          onTabChange={(tab) => {
            setActiveTab(tab);
            setShowNavigation(false);
          }}
        />
      </main>
    </GoogleOAuthProvider>
  );
}

export default App;
