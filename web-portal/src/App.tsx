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

const LOCAL_STORAGE_JWT_KEY = "translatar_jwt";
const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
if (!googleClientId) {
  console.error("Error: VITE_GOOGLE_CLIENT_ID env variable not set.");
}

const DEFAULT_SETTINGS: Settings = {
  // Backend-related (unchanged)
  source_language: "en",
  target_language: "es",
  chunk_duration_seconds: 8.0,
  target_sample_rate: 48000,
  silence_threshold: 0.01,
  chunk_overlap_seconds: 0.5,
  websocket_url: "ws://localhost:8000/ws",

  // New UX-facing fields
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

  const [settings, setSettings] = useState<Settings>(DEFAULT_SETTINGS);
  const [settingsError, setSettingsError] = useState<string | null>(null);
  const [showSettings, setShowSettings] = useState(false);

  const [showNavigation, setShowNavigation] = useState(false);
  const [activeTab, setActiveTab] = useState<TabKey>("dashboard");
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);

  // --- AUTH HANDLERS ---
  const handleLogout = useCallback(() => {
    setAppUser(null);
    localStorage.removeItem(LOCAL_STORAGE_JWT_KEY);
    console.log("User logged out.");
  }, []);

  // --- DATA FETCHING & SIDE EFFECTS ---
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

    try {
      const token = localStorage.getItem(LOCAL_STORAGE_JWT_KEY);

      if (!token) {
        setHistory([]);
        setIsHistoryLoading(false);
        return;
      }

      const response = await fetch("/api/history", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          setHistory([]);
          return;
        }
        throw new Error("Network response was not ok");
      }

      const data = await response.json();
      setHistory(data.history);
    } catch (error) {
      console.error("Error fetching history:", error);
      setHistoryError("Failed to load translation history.");
    } finally {
      setIsHistoryLoading(false);
    }
  }, []);

  const loadSettings = useCallback(async () => {
    setSettingsError(null);
    try {
      const response = await fetch("/api/settings");
      if (!response.ok) throw new Error("Network response was not ok");
      const data = await response.json();

      setSettings({
        ...DEFAULT_SETTINGS,
        ...(data.settings ?? {}),
      });
    } catch (error) {
      console.error("Error fetching settings:", error);
      setSettingsError("Failed to load settings.");
    }
  }, []);

  useEffect(() => {
    const initialize = async () => {
      const token = localStorage.getItem(LOCAL_STORAGE_JWT_KEY);
      if (token) {
        await fetchUserProfile(token);
      }
      await loadSettings();
      await loadHistory();
    };
    void initialize();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fetchUserProfile]);

  useEffect(() => {
    if (appUser) {
      loadHistory();
    }
  }, [appUser, loadHistory]);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      const historyPanel = document.getElementById("history-panel");
      if (historyPanel && !historyPanel.contains(e.target as Node)) {
        setActiveConversationId(null);
      }
    };
    window.addEventListener("mousedown", handleClickOutside);
    return () => window.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const saveSettings = useCallback(async (newSettings: Settings) => {
    setSettingsError(null);
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
      setSettingsError("Failed to save settings. Please try again.");
    }
  }, []);

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

  // --- RENDER ---
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
            onShowNavigation={() => setShowNavigation(true)}   // NEW
          />

          {/*can later show different content based on activeTab maybe*/}
          <Summarizer />
          <HistoryPanel
            history={history}
            isLoading={isHistoryLoading}
            error={historyError}
            activeConversationId={activeConversationId}
            onSelectConversation={setActiveConversationId}
          />
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
