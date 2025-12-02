export type TabKey =
  | "dashboard"
  | "live_translation"
  | "conversations";

interface SideNavigationProps {
  isOpen: boolean;
  activeTab: TabKey;
  onClose: () => void;
  onTabChange: (tab: TabKey) => void;
}

const tabs: { key: TabKey; label: string }[] = [
  { key: "dashboard", label: "Dashboard" },
  { key: "live_translation", label: "Live Translation" },
  { key: "conversations", label: "Conversations / History" },
];

export default function SideNavigation({
  isOpen,
  activeTab,
  onClose,
  onTabChange,
}: SideNavigationProps) {
  return (
    <div
      className={`fixed inset-0 z-40 transition-opacity duration-300 ${isOpen
        ? "opacity-100 pointer-events-auto"
        : "opacity-0 pointer-events-none"
        }`}
    >
      {/* Backdrop */}
      <div
        className={`absolute inset-0 bg-black/40 transition-opacity duration-300 ${isOpen ? "opacity-100" : "opacity-0"
          }`}
        onClick={onClose}
      />

      {/* Sliding panel */}
      <div
        className={`absolute left-0 top-0 h-full w-64 bg-slate-800 text-white shadow-xl
        transform transition-transform duration-300
        ${isOpen ? "translate-x-0" : "-translate-x-full"}`}
      >
        <div className="flex items-center justify-between px-4 py-4 border-b border-slate-700">
          <h2 className="text-xl font-semibold">Navigation</h2>
          <button
            onClick={onClose}
            className="text-slate-300 hover:text-white text-lg"
            aria-label="Close navigation"
          >
            ×
          </button>
        </div>

        <nav className="mt-4">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              type="button"
              onClick={() => {
                onTabChange(tab.key);
                onClose();
              }}
              className={`w-full text-left px-4 py-2 text-sm transition-colors ${activeTab === tab.key
                ? "bg-slate-700 text-white"
                : "text-slate-300 hover:bg-slate-700/70"
                }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div >
    </div >
  );
}