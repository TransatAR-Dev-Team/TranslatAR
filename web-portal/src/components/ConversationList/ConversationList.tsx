import { useState, useEffect, useCallback } from "react";

/**
 * Conversation info interface
 */
interface Conversation {
  _id: string;
  source_lang: string;
  target_lang: string;
  started_at: string;
  ended_at: string | null;
  is_active: boolean;
  translation_count: number;
}

/**
 * Translation item interface
 */
interface Translation {
  _id: string;
  original_text: string;
  translated_text: string;
  source_lang: string;
  target_lang: string;
  timestamp: string;
  sequence_number: number;
}

/**
 * Conversation detail interface
 */
interface ConversationDetail {
  conversation: Conversation;
  translations: Translation[];
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

/**
 * Component that displays conversation list and details
 */
export default function ConversationList() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConversation, setSelectedConversation] =
    useState<ConversationDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isDetailLoading, setIsDetailLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Fetch conversation list
   */
  const fetchConversations = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem("translatar_jwt");
      if (!token) {
        setConversations([]);
        setIsLoading(false);
        return;
      }

      const response = await fetch("/api/conversations", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          setConversations([]);
          return;
        }
        throw new Error("Failed to fetch conversations");
      }

      const data = await response.json();
      setConversations(data.conversations || []);
    } catch (err) {
      console.error("Failed to fetch conversations:", err);
      setError("Failed to load conversation list.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Fetch conversation detail
   */
  const fetchConversationDetail = useCallback(async (id: string) => {
    setIsDetailLoading(true);

    try {
      const token = localStorage.getItem("translatar_jwt");
      if (!token) return;

      const response = await fetch(`/api/conversations/${id}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch conversation detail");
      }

      const data = await response.json();
      setSelectedConversation(data);
    } catch (err) {
      console.error("Failed to fetch conversation detail:", err);
      setError("Failed to load conversation content.");
    } finally {
      setIsDetailLoading(false);
    }
  }, []);

  /**
   * Delete conversation
   */
  const deleteConversation = useCallback(
    async (id: string) => {
      if (!window.confirm("Are you sure you want to delete this conversation?")) {
        return;
      }

      try {
        const token = localStorage.getItem("translatar_jwt");
        if (!token) return;

        const response = await fetch(`/api/conversations/${id}`, {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error("Failed to delete conversation");
        }

        // Remove from list
        setConversations((prev) => prev.filter((c) => c._id !== id));

        // Deselect if deleted conversation was selected
        if (selectedConversation?.conversation._id === id) {
          setSelectedConversation(null);
        }
      } catch (err) {
        console.error("Failed to delete conversation:", err);
        setError("Failed to delete conversation.");
      }
    },
    [selectedConversation]
  );

  /**
   * Load conversation list on component mount
   */
  useEffect(() => {
    fetchConversations();
  }, [fetchConversations]);

  /**
   * Format date
   */
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
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
    <div className="bg-slate-800 rounded-lg p-6 shadow-lg">
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
              <button
                onClick={fetchConversations}
                className="text-sm text-blue-400 hover:text-blue-300 transition"
              >
                Refresh
              </button>
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
                    key={conv._id}
                    className={`p-3 rounded-lg cursor-pointer transition group ${
                      selectedConversation?.conversation._id === conv._id
                        ? "bg-blue-600"
                        : "bg-slate-600 hover:bg-slate-500"
                    }`}
                  >
                    <div
                      onClick={() => fetchConversationDetail(conv._id)}
                      className="flex-1"
                    >
                      <div className="flex justify-between items-start">
                        <div className="text-sm text-slate-300">
                          {formatDate(conv.started_at)}
                        </div>
                        {conv.is_active && (
                          <span className="text-xs bg-green-500 text-white px-2 py-0.5 rounded">
                            Active
                          </span>
                        )}
                      </div>
                      <div className="text-xs text-slate-400 mt-1">
                        {getLanguageName(conv.source_lang)} →{" "}
                        {getLanguageName(conv.target_lang)}
                      </div>
                      <div className="text-xs text-slate-400 mt-1">
                        {conv.translation_count} translations
                      </div>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteConversation(conv._id);
                      }}
                      className="text-red-400 hover:text-red-300 text-xs mt-2 opacity-0 group-hover:opacity-100 transition"
                    >
                      Delete
                    </button>
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

            {isDetailLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
                <p className="text-slate-400 mt-2">Loading...</p>
              </div>
            ) : selectedConversation ? (
              <div className="space-y-3">
                {selectedConversation.translations.length === 0 ? (
                  <p className="text-slate-400 text-center py-8">
                    No translations in this conversation.
                  </p>
                ) : (
                  selectedConversation.translations.map((trans, idx) => (
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
