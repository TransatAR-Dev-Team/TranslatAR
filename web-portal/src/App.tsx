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

  const [history, setHistory] = useState<any[]>([]);
  const [isHistoryLoading, setIsHistoryLoading] = useState(true);
  const [historyError, setHistoryError] = useState<string | null>(null);

  const [settings, setSettings] = useState<Settings>(DEFAULT_SETTINGS);
  const [settingsError, setSettingsError] = useState<string | null>(null);
  const [showSettings, setShowSettings] = useState(false);

  const [showNavigation, setShowNavigation] = useState(false);
  const [activeTab, setActiveTab] = useState<TabKey>("dashboard");

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
      // keep defaults if backend not reachable
    }
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

  // --- INITIALIZE ---
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

  // --- RENDER HELPERS ---
  const renderMainContent = () => {
    switch (activeTab) {
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
          <>
            <DashboardOverview
              appUser={appUser}
              history={history}
              onOpenSummarization={() => setActiveTab("summarization")}
              onOpenHistory={() => setActiveTab("conversations")}
            />
          </>
        );
    }
  };

  // --- RENDER ---
  return (
    <GoogleOAuthProvider clientId={googleClientId || ""}>
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
    </GoogleOAuthProvider>
  );
}

function DashboardOverview({
  appUser,
  history,
  onOpenSummarization,
  onOpenHistory,
}: {
  appUser: User | null;
  history: any[];
  onOpenSummarization: () => void;
  onOpenHistory: () => void;
}) {
  const recentCount = history.length;
  const lastItem = history[0];

  return (
    <section className="bg-slate-800 rounded-lg p-6 shadow-xl space-y-6 border border-slate-700">
      {/* Title + intro */}
      <div>
        <h2 className="text-3xl font-bold mb-2">Dashboard</h2>
        <p className="text-sm text-slate-300">
          {appUser
            ? "Welcome back. From here you can manage your headset data, review translations, and generate summaries — all from the web portal."
            : "Log in with your Google account to sync your headset activity, review translations, and generate summaries from your conversations."}
        </p>
      </div>

      {/* What you can do here (paragraph style) */}
      <div className="bg-slate-900/40 rounded-lg p-4 border border-slate-700 shadow">
        <h3 className="text-lg font-semibold mb-2">What you can do here</h3>
        <p className="text-xs text-slate-300 leading-relaxed">
          The TranslatAR web portal is your companion to the headset experience.
          You can revisit translated conversations, quickly generate AI-powered
          summaries of long meetings, and adjust your default language settings
          so that the Unity app feels personalized the moment you put the headset
          on. Over time, this becomes the place where you review what happened,
          not just what was said.
        </p>
      </div>

      {/* Highlights at a glance (bullets with colored dots) */}
      <div className="bg-slate-900/40 rounded-lg p-4 border border-slate-700 shadow">
        <h3 className="text-lg font-semibold mb-2">Highlights at a glance</h3>
        <ul className="space-y-2">
          <li className="flex items-start gap-2 text-xs text-slate-200">
            <span className="mt-1 h-2 w-2 rounded-full bg-blue-400" />
            <span>Real-time subtitles and translations captured from your headset sessions.</span>
          </li>
          <li className="flex items-start gap-2 text-xs text-slate-200">
            <span className="mt-1 h-2 w-2 rounded-full bg-emerald-400" />
            <span>Conversation logs stored for later review and learning.</span>
          </li>
          <li className="flex items-start gap-2 text-xs text-slate-200">
            <span className="mt-1 h-2 w-2 rounded-full bg-amber-300" />
            <span>AI-generated summaries to condense long or complex discussions.</span>
          </li>
          <li className="flex items-start gap-2 text-xs text-slate-200">
            <span className="mt-1 h-2 w-2 rounded-full bg-pink-400" />
            <span>Accessibility-focused controls for subtitles and translation preferences.</span>
          </li>
        </ul>
      </div>

      {/* Quick actions + Activity snapshot (moved below) */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Quick Actions */}
        <div className="bg-slate-900/40 rounded-lg p-4 border border-slate-700 shadow">
          <h3 className="text-lg font-semibold mb-2">Quick Actions</h3>
          <p className="text-xs text-slate-300 mb-3">
            Jump straight into the tools you’ll use most often:
          </p>

          <div className="flex flex-col gap-3">
            <button
              onClick={onOpenSummarization}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium py-2 rounded-md"
            >
              Open Summarization
            </button>
            <button
              onClick={onOpenHistory}
              className="w-full bg-slate-700 hover:bg-slate-600 text-white text-sm font-medium py-2 rounded-md"
            >
              View Translation History
            </button>
          </div>
        </div>

        {/* Activity Snapshot */}
        <div className="bg-slate-900/40 rounded-lg p-4 border border-slate-700 shadow">
          <h3 className="text-lg font-semibold mb-2">Activity Snapshot</h3>

          {recentCount === 0 ? (
            <p className="text-xs text-slate-300">
              No conversations logged yet — once you start using your headset,
              your most recent translations will appear here.
            </p>
          ) : (
            <>
              <p className="text-xs text-slate-300 mb-2">
                You have{" "}
                <span className="font-semibold">{recentCount}</span> saved
                translation{recentCount === 1 ? "" : "s"}.
              </p>
              <div className="mt-2 p-3 rounded-md bg-slate-800 border border-slate-700 text-xs">
                <div className="text-slate-400 mb-1">Most recent conversation:</div>
                <div className="text-slate-100 line-clamp-2">
                  {lastItem?.original_text}
                </div>
                <div className="mt-1 text-slate-400">
                  → {lastItem?.translated_text}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </section>
  );
}

export default App;
