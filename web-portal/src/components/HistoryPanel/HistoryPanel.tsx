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
  activeConversationId?: string | null;
  onSelectConversation?: (conversationId: string) => void;
}

interface Conversation {
  id: string;
  originalTranscript: string;
  translatedTranscript: string;
  source_lang: string;
  target_lang: string;
  items: HistoryItem[];
  startedAt: Date;
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
      items: []
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
  activeConversationId,
  onSelectConversation,
}: HistoryPanelProps) {

  const [copiedConversationId, setCopiedConversationId] = useState<string | null>(null); 
  console.log("History from backend: ", history);
  const conversations = buildConversationTranscripts(history);
  console.log("Built conversations: ", conversations);

  return (
    <div id="history-panel" className="bg-slate-800 rounded-lg p-6 shadow-lg">
      <h2 className="text-2xl font-semibold mb-4 text-left">
        Translation History
      </h2>

      {isLoading && <p>Loading history...</p>}
      {error && <p className="text-red-400">{error}</p>}

      {!isLoading && !error && (
        <div className="text-left space-y-4 max-h-96 overflow-y-auto">
          {conversations.length === 0 ? (
            <p className="text-gray-400">
              No translations found in the database.
            </p>
          ) : (
            conversations.map((convo) => {
              const isActive = convo.id === activeConversationId;
              const isCopied = convo.id === copiedConversationId;

              return (
                <div key={convo.id} className={`border rounded-md p-3 transition ${
                  isActive ? "border-indigo-400 bg-slate-700" : "border-slate-700 hover:border-slate-500"
                }`}>
                  <div onClick={() => onSelectConversation?.(convo.id)}
                      className="flex w-full justify-between items-center cursor-pointer pb-2">
                      <p className="text-xs text-gray-400 m-0">
                        Conversation started: {convo.startedAt.toLocaleDateString()}
                      </p>

                      <div className="flex items-center gap-2">
                        {/* Copied badge */}
                        {isCopied && (
                          <span className="text-xs text-green-400">
                            Copied!
                          </span>
                        )}
                        
                        <button className="text-xs text-indigo-400 hover:underline cursor-pointer m-0"
                          onClick={(e) => {
                            e.stopPropagation();
                            navigator.clipboard.writeText(convo.translatedTranscript);
                            setCopiedConversationId(convo.id);
                            setTimeout(() => setCopiedConversationId(null), 2000);
                          }}>
                          Copy Translated Text
                        </button>
                    </div>
                    </div>
                    <div className="select-text">
                      <p className="text-gray-400 mb-1">
                        {convo.originalTranscript}{" "} <span className="text-xs">({convo.source_lang}):</span>
                      </p>
                      <p className="text-lg">
                        {convo.translatedTranscript}{" "} <span className="text-xs">({convo.target_lang}):</span>
                        </p>
                    </div>
                </div>
              );
            })
          )}
        </div>
      )}
    </div>
  );
}
