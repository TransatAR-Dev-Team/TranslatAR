import { useEffect, useState, useCallback } from "react";
import { GoogleOAuthProvider } from "@react-oauth/google";
import type { CredentialResponse } from "@react-oauth/google";

import type { User } from "./models/User";
import { loginWithGoogleApi, getMeApi } from "./api/auth";

import DashboardOverview from "./components/DashboardOverview/DashboardOverview";
import Header from "./components/Header/Header";
import Summarizer from "./components/Summarizer/Summarizer";
import HistoryPanel from "./components/HistoryPanel/HistoryPanel";
import SettingsMenu, {
  type Settings,
} from "./components/SettingsMenu/SettingsMenu";
import SideNavigation, {
  type TabKey,
} from "./components/Sidebar/NavigationSidebar";
import LiveTranslationView from "./components/TranslationView/TranslationView";
import LandingPage from "./components/LandingPage/LandingPage";

const LOCAL_STORAGE_JWT_KEY = "translatar_jwt";
const LOCAL_STORAGE_TAB_KEY = "translatar_active_tab";

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

  // UX-facing
  subtitles_enabled: true,
  translation_enabled: true,
  subtitle_font_size: 18,
  subtitle_style: "normal",
};

function App() {
  const [appUser, setAppUser] = useState<User | null>(null);
  const [isAuthChecking, setIsAuthChecking] = useState(true); // Prevents flashing landing page on reload

  const [history, setHistory] = useState<any[]>([]);
  const [isHistoryLoading, setIsHistoryLoading] = useState(true);
  const [historyError, setHistoryError] = useState<string | null>(null);

  // Note: Logs state removed as the feature is deprecated
  const [settings, setSettings] = useState<Settings>(DEFAULT_SETTINGS);
  const [settingsError, setSettingsError] = useState<string | null>(null);
  const [showSettings, setShowSettings] = useState(false);

  const [showNavigation, setShowNavigation] = useState(false);
  // Initialize from LocalStorage
  const [activeTab, setActiveTab] = useState<TabKey>(() => {
    return (
      (localStorage.getItem(LOCAL_STORAGE_TAB_KEY) as TabKey) || "dashboard"
    );
  });

  // --- AUTH HANDLERS ---
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
        await loadHistory(); // refresh history once logged in
      } catch (error) {
        console.error("Login process failed:", error);
        alert("Login failed. Please try again.");
        handleLogout();
      }
    },
    [fetchUserProfile, handleLogout],
  );

  // --- DATA FETCHING ---
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

  // loadLogs removed here to resolve conflict

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
      // keep defaults if backend not reachable
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
        await loadSettings(); // Re-fetch after saving
        setShowSettings(false);
      } catch (error) {
        console.error("Error saving settings:", error);
        setSettingsError("Failed to save settings. Please try again.");
      }
    },
    [loadSettings],
  );

  // --- INITIALIZE ---
  useEffect(() => {
    const initialize = async () => {
      // Add this from "Incoming"
      setIsAuthChecking(true);
      const token = localStorage.getItem(LOCAL_STORAGE_JWT_KEY);
      if (token) {
        await fetchUserProfile(token);
      }
      // These are from "Current"
      await loadSettings();
      await loadHistory();
      // Add this from "Incoming"
      setIsAuthChecking(false);
    };
    void initialize();
    // Keep dependencies from "Current"
  }, [fetchUserProfile, loadSettings, loadHistory]);

  // --- RENDER HELPERS ---
  const renderMainContent = () => {
    switch (activeTab) {
      case "live_translation":
        return <LiveTranslationView settings={settings} />;

      case "summarization":
        return <Summarizer />;

      case "conversations":
        return (
          <HistoryPanel
            history={history}
            isLoading={isHistoryLoading}
            error={historyError}
          />
        );

      case "dashboard":
      default:
        return (
          <DashboardOverview
            appUser={appUser}
            history={history}
            onOpenSummarization={() => setActiveTab("summarization")}
            onOpenHistory={() => setActiveTab("conversations")}
          />
        );
    }
  };

  // --- RENDER ---
  if (isAuthChecking) {
    // spinner while loading
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <GoogleOAuthProvider clientId={googleClientId || ""}>
      {!appUser ? (
        <LandingPage
          onLoginSuccess={handleLoginSuccess}
          onLoginError={handleLogout}
        />
      ) : (
        <main className="bg-slate-900 min-h-screen flex flex-col items-center font-sans p-4 text-white">
          <div className="w-full max-w-5xl">
            <Header
              appUser={appUser}
              onLoginSuccess={handleLoginSuccess}
              onLoginError={handleLogout}
              onLogout={handleLogout}
              onShowSettings={() => setShowSettings(true)}
              onShowNavigation={() => setShowNavigation(true)}
            />

            {renderMainContent()}
          </div>

          {showSettings && (
            <SettingsMenu
              initialSettings={settings}
              onSave={saveSettings}
              onClose={() => setShowSettings(false)}
              error={settingsError}
            />
          )}

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
      )}
    </GoogleOAuthProvider>
  );
}

export default App;
