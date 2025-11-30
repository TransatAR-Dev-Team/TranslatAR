import { useState } from "react";

interface HistoryItem {
  _id: string;
  original_text: string;
  translated_text: string;
  source_lang: string;
  target_lang: string;
  conversationId?: string | null;
  timestamp: string;
}

interface HistoryPanelProps {
  history: HistoryItem[];
  isLoading: boolean;
  error: string | null;
}

interface Conversation {
  id: string;
  originalTranscript: string;
  translatedTranscript: string;
  source_lang: string;
  target_lang: string;
  items: HistoryItem[];
  startedAt: Date;
}

/**
 * Map of language codes to human-readable names
 */
const languageNames: Record<string, string> = {
  en: "English",
  es: "Spanish",
  ko: "Korean",
  ja: "Japanese",
  zh: "Chinese",
  fr: "French",
  de: "German",
  pt: "Portuguese",
  it: "Italian",
  ru: "Russian",
};

/**
 * Helper function to convert language code to name
 */
const getLanguageName = (code: string): string => {
  return languageNames[code] || code.toUpperCase();
};

export function buildConversationTranscripts(history: HistoryItem[]): Conversation[] {
  if (!history.length) return [];

  const convMap = new Map<string, HistoryItem[]>();

  // Group items by conversationId
  for (const item of history) {
    const id = item.conversationId || item._id; // fallback
    if (!convMap.has(id)) convMap.set(id, []);
    convMap.get(id)!.push(item);
  }

  const conversations: Conversation[] = [];

  for (const [id, items] of convMap.entries()) {
    // Sort by time
    items.sort(
      (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime(),
    );

    const startedAt = new Date(items[0].timestamp);
    const source_lang = items[0].source_lang;
    const target_lang = items[0].target_lang;

    // Merge all chunk texts into a single transcript
    const originalTranscript = items
      .map((i) => i.original_text)
      .filter((txt) => txt?.trim())
      .join(" ");

    const translatedTranscript = items
      .map((i) => i.translated_text)
      .filter((txt) => txt?.trim())
      .join(" ");

    conversations.push({
      id,
      originalTranscript,
      translatedTranscript,
      source_lang,
      target_lang,
      startedAt,
      items,
    });
  }

  // Sort by newest conversation
  return conversations.sort(
    (a, b) => b.startedAt.getTime() - a.startedAt.getTime(),
  );
}

export default function HistoryPanel({
  history,
  isLoading,
  error,
}: HistoryPanelProps) {
  const [selectedConversationId, setSelectedConversationId] = useState<string | null>(null);

  const conversations = buildConversationTranscripts(history);
  const selectedConversation = conversations.find((c) => c.id === selectedConversationId);

  /**
   * Format date
   */
  const formatDate = (date: Date): string => {
    return date.toLocaleString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  /**
   * Format time (short)
   */
  const formatTime = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  };

  return (
    <div id="history-panel" className="bg-slate-800 rounded-lg p-6 shadow-lg">
      <h2 className="text-2xl font-semibold mb-4">Conversations</h2>

      {error && (
        <div className="bg-red-900/50 border border-red-500 text-red-200 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="flex gap-4 flex-col lg:flex-row">
        {/* Conversation list panel */}
        <div className="lg:w-1/3 w-full">
          <div className="bg-slate-700 rounded-lg p-4 max-h-[500px] overflow-y-auto">
            <div className="flex justify-between items-center mb-3">
              <h3 className="text-lg font-medium text-slate-200">Sessions</h3>
              <span className="text-xs text-slate-400">
                {conversations.length} total
              </span>
            </div>

            {isLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
                <p className="text-slate-400 mt-2">Loading...</p>
              </div>
            ) : conversations.length === 0 ? (
              <p className="text-slate-400 text-center py-8">
                No saved conversations.
              </p>
            ) : (
              <div className="space-y-2">
                {conversations.map((conv) => (
                  <div
                    key={conv.id}
                    onClick={() => setSelectedConversationId(conv.id)}
                    className={`p-3 rounded-lg cursor-pointer transition ${
                      selectedConversationId === conv.id
                        ? "bg-blue-600"
                        : "bg-slate-600 hover:bg-slate-500"
                    }`}
                  >
                    <div className="flex justify-between items-start">
                      <div className="text-sm text-slate-300">
                        {formatDate(conv.startedAt)}
                      </div>
                    </div>
                    <div className="text-xs text-slate-400 mt-1">
                      {getLanguageName(conv.source_lang)} →{" "}
                      {getLanguageName(conv.target_lang)}
                    </div>
                    <div className="text-xs text-slate-400 mt-1">
                      {conv.items.length} translation{conv.items.length !== 1 ? "s" : ""}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Conversation detail panel */}
        <div className="lg:w-2/3 w-full">
          <div className="bg-slate-700 rounded-lg p-4 min-h-[500px] max-h-[500px] overflow-y-auto">
            <h3 className="text-lg font-medium text-slate-200 mb-3">
              Conversation Content
            </h3>

            {selectedConversation ? (
              <div className="space-y-3">
                {selectedConversation.items.length === 0 ? (
                  <p className="text-slate-400 text-center py-8">
                    No translations in this conversation.
                  </p>
                ) : (
                  selectedConversation.items.map((trans, idx) => (
                    <div
                      key={trans._id || idx}
                      className="border-l-2 border-blue-500 pl-3 py-2"
                    >
                      <div className="flex justify-between items-start">
                        <p className="text-slate-400 text-sm">
                          {trans.original_text}
                        </p>
                        <span className="text-xs text-slate-500 ml-2 whitespace-nowrap">
                          {formatTime(trans.timestamp)}
                        </span>
                      </div>
                      <p className="text-white mt-1">{trans.translated_text}</p>
                    </div>
                  ))
                )}
              </div>
            ) : (
              <div className="text-center py-16">
                <svg
                  className="w-16 h-16 mx-auto text-slate-500 mb-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                  />
                </svg>
                <p className="text-slate-400">
                  Select a conversation from the list
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
