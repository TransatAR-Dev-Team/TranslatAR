import type { User } from "../../models/User";

interface DashboardOverviewProps {
  appUser: User | null;
  history: any[]; // You can refine this type later to match HistoryItem[]
  onOpenSummarization: () => void;
  onOpenHistory: () => void;
}

export default function DashboardOverview({
  appUser,
  history,
  onOpenSummarization,
  onOpenHistory,
}: DashboardOverviewProps) {
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

      {/* What you can do here */}
      <div className="bg-slate-900/40 rounded-lg p-4 border border-slate-700 shadow">
        <h3 className="text-lg font-semibold mb-2">What you can do here</h3>
        <p className="text-xs text-slate-300 leading-relaxed">
          The TranslatAR web portal is your companion to the headset experience.
          You can revisit translated conversations, quickly generate AI-powered
          summaries of long meetings, and adjust your default language settings
          so that the Unity app feels personalized the moment you put the
          headset on. Over time, this becomes the place where you review what
          happened, not just what was said.
        </p>
      </div>

      {/* Highlights at a glance */}
      <div className="bg-slate-900/40 rounded-lg p-4 border border-slate-700 shadow">
        <h3 className="text-lg font-semibold mb-2">Highlights at a glance</h3>
        <ul className="space-y-2">
          <li className="flex items-start gap-2 text-xs text-slate-200">
            <span className="mt-1 h-2 w-2 rounded-full bg-blue-400" />
            <span>
              Real-time subtitles and translations captured from your headset
              sessions.
            </span>
          </li>
          <li className="flex items-start gap-2 text-xs text-slate-200">
            <span className="mt-1 h-2 w-2 rounded-full bg-emerald-400" />
            <span>Conversation logs stored for later review and learning.</span>
          </li>
          <li className="flex items-start gap-2 text-xs text-slate-200">
            <span className="mt-1 h-2 w-2 rounded-full bg-amber-300" />
            <span>
              AI-generated summaries to condense long or complex discussions.
            </span>
          </li>
          <li className="flex items-start gap-2 text-xs text-slate-200">
            <span className="mt-1 h-2 w-2 rounded-full bg-pink-400" />
            <span>
              Accessibility-focused controls for subtitles and translation
              preferences.
            </span>
          </li>
        </ul>
      </div>

      {/* Quick actions + Activity snapshot */}
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
                You have <span className="font-semibold">{recentCount}</span>{" "}
                saved translation{recentCount === 1 ? "" : "s"}.
              </p>
              <div className="mt-2 p-3 rounded-md bg-slate-800 border border-slate-700 text-xs">
                <div className="text-slate-400 mb-1">
                  Most recent conversation:
                </div>
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
