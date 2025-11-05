interface HistoryItem {
  _id: string;
  original_text: string;
  translated_text: string;
  source_lang: string;
  target_lang: string;
}

interface HistoryPanelProps {
  history: HistoryItem[];
  isLoading: boolean;
  error: string | null;
}

export default function HistoryPanel({
  history,
  isLoading,
  error,
}: HistoryPanelProps) {
  return (
    <div className="bg-slate-800 rounded-lg p-6 shadow-lg">
      <h2 className="text-2xl font-semibold mb-4 text-left">
        Translation History
      </h2>

      {isLoading && <p>Loading history...</p>}
      {error && <p className="text-red-400">{error}</p>}

      {!isLoading && !error && (
        <div className="text-left space-y-4 max-h-96 overflow-y-auto">
          {history.length === 0 ? (
            <p className="text-gray-400">
              No translations found in the database.
            </p>
          ) : (
            history.map((item) => (
              <div key={item._id} className="border-b border-slate-700 pb-2">
                <p className="text-gray-400">
                  {item.original_text}{" "}
                  <span className="text-xs">({item.source_lang})</span>
                </p>
                <p className="text-lg">
                  {item.translated_text}{" "}
                  <span className="text-xs">({item.target_lang})</span>
                </p>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
