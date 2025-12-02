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
  // Backend-related (keep as-is)
  source_language: "en",
  target_language: "es",
  chunk_duration_seconds: 8.0,
  target_sample_rate: 48000,
  silence_threshold: 0.01,
  chunk_overlap_seconds: 0.5,
  websocket_url: "ws://localhost:8000/ws",

  // UX-facing settings (already added earlier)
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
        // Once logged in, refresh history
        await loadHistory();
      } catch (error) {
        console.error("Login process failed:", error);
        alert("Login failed. Please try again.");
        handleLogout();
      }
    },
    [fetchUserProfile, handleLogout],
  );

  // --- API HANDLERS ---
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
      // keep current (defaults) if it fails
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

  // --- RENDER ---
  return (
    <GoogleOAuthProvider clientId={googleClientId || ""}>
      <main className="bg-slate-900 min-h-screen text-white">
        {/* Sidebar */}
        <SideNavigation
          isOpen={showNavigation}
          activeTab={activeTab}
          onClose={() => setShowNavigation(false)}
          onTabChange={(tab) => {
            setActiveTab(tab);
            setShowNavigation(false);
          }}
        />

        {/* Main content container */}
        <div className="max-w-4xl mx-auto px-4 py-6 flex flex-col gap-6">
          <Header
            appUser={appUser}
            onLoginSuccess={handleLoginSuccess}
            onLoginError={handleLogout}
            onLogout={handleLogout}
            onShowSettings={() => setShowSettings(true)}
            onShowNavigation={() => setShowNavigation(true)}
          />

          <div className="space-y-6">
            {/* DASHBOARD */}
            {activeTab === "dashboard" && (
              <DashboardOverview
                onGoSummarization={() => setActiveTab("summarization")}
                onGoConversations={() => setActiveTab("conversations")}
                onOpenSettings={() => setShowSettings(true)}
              />
            )}

            {/* SUMMARIZATION */}
            {activeTab === "summarization" && <Summarizer />}

            {/* CONVERSATIONS / HISTORY */}
            {activeTab === "conversations" && (
              <HistoryPanel
                history={history}
                isLoading={isHistoryLoading}
                error={historyError}
              />
            )}
          </div>
        </div>

        {/* SETTINGS MODAL */}
        {showSettings && (
          <SettingsMenu
            initialSettings={settings}
            onSave={saveSettings}
            onClose={() => setShowSettings(false)}
            error={settingsError}
          />
        )}
      </main>
    </GoogleOAuthProvider>
  );
}

/**
 * Dashboard hero + quick actions
 * - Logo + name (style B)
 * - Warm/professional copy about what the portal does
 * - Buttons to jump to Summarization / Conversations / Settings
 */
function DashboardOverview({
  onGoSummarization,
  onGoConversations,
  onOpenSettings,
}: {
  onGoSummarization: () => void;
  onGoConversations: () => void;
  onOpenSettings: () => void;
}) {
  return (
    <section className="bg-gradient-to-br from-slate-800/90 via-slate-800 to-slate-900 rounded-2xl border border-slate-700/70 shadow-2xl p-6 md:p-8 space-y-6">
      {/* Top row: logo + title/description */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
        <div className="flex items-center gap-4">
          {/* Logo */}
          <div className="h-14 w-14 rounded-xl bg-slate-900/80 border border-slate-600/80 flex items-center justify-center overflow-hidden">
            {/* Change src to your actual logo path */}
            <img
              src="/translatar-logo.png"
              alt="TranslatAR logo"
              className="h-12 w-12 object-contain"
            />
          </div>
          <div>
            <h1 className="text-2xl md:text-3xl font-bold tracking-tight">
              TranslatAR Web Portal
            </h1>
            <p className="text-sm md:text-base text-slate-300 mt-1">
              Manage your conversations, summaries, and language settings for
              the TranslatAR headset—all in one place.
            </p>
          </div>
        </div>

        {/* Quick actions */}
        <div className="flex flex-wrap gap-2 md:justify-end">
          <button
            onClick={onGoSummarization}
            className="px-4 py-2 text-sm font-medium rounded-lg bg-blue-600 hover:bg-blue-700 transition-colors"
          >
            Open Summarization
          </button>
          <button
            onClick={onGoConversations}
            className="px-4 py-2 text-sm font-medium rounded-lg bg-slate-700 hover:bg-slate-600 transition-colors"
          >
            View Conversation History
          </button>
          <button
            onClick={onOpenSettings}
            className="px-4 py-2 text-sm font-medium rounded-lg border border-slate-600 hover:border-slate-400 hover:bg-slate-800/60 transition-colors"
          >
            Settings
          </button>
        </div>
      </div>

      {/* Body copy */}
      <div className="grid gap-4 md:grid-cols-3">
        <div className="md:col-span-2 space-y-2">
          <h2 className="text-lg font-semibold">What you can do here</h2>
          <p className="text-sm text-slate-200">
            The web portal is your control center for TranslatAR. Review
            translated conversations, generate AI-powered summaries, and adjust
            how subtitles and translations behave on your headset.
          </p>
          <p className="text-sm text-slate-300">
            Changes you make here—like language pairs and subtitle preferences—
            are designed to sync with the backend so your next AR session feels
            ready out of the box.
          </p>
        </div>

        {/* Feature highlights (static, not recent-activity) */}
        <div className="space-y-3">
          <h3 className="text-sm font-semibold text-slate-200">
            Highlights at a glance
          </h3>
          <ul className="space-y-2 text-xs text-slate-300">
            <li className="flex items-start gap-2">
              <span className="mt-1 h-1.5 w-1.5 rounded-full bg-emerald-400" />
              <span>
                Real-time AR subtitles and translations tailored to your
                preferred languages.
              </span>
            </li>
            <li className="flex items-start gap-2">
              <span className="mt-1 h-1.5 w-1.5 rounded-full bg-sky-400" />
              <span>
                Conversation logs and summaries so you never lose important
                meeting details.
              </span>
            </li>
            <li className="flex items-start gap-2">
              <span className="mt-1 h-1.5 w-1.5 rounded-full bg-violet-400" />
              <span>
                Accessibility options like subtitle size, style, and language
                pairing presets.
              </span>
            </li>
          </ul>
        </div>
      </div>
    </section>
  );
}

export default App;
