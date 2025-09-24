import { useEffect, useState } from 'react';

interface HistoryItem {
  _id: string;
  original_text: string;
  translated_text: string;
  source_lang: string;
  target_lang: string;
  timestamp: string;
}

function App() {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setIsLoading(true);

    fetch('/api/history')
      .then((response) => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then((data) => {
        setHistory(data.history);
        setIsLoading(false);
      })
      .catch((error) => {
        console.error("Error fetching data:", error);
        setError("Failed to load translation history.");
        setIsLoading(false);
      });
  }, []);

  return (
    <main className="bg-slate-900 min-h-screen flex flex-col items-center font-sans p-4 text-white">
      <div>
        <h1 className="text-4xl font-bold mb-6">TranslatAR Web Portal</h1>
        <div>
          <p>
            Edit (and save) <code>web-portal/App.tsx</code> to test Hot Module Replacement.
          </p>
        </div>

        <div className="bg-slate-800 rounded-lg p-6 shadow-lg">
          <h2 className="text-2xl font-semibold mb-4 text-left">Translation History</h2>

          {isLoading && <p>Loading history...</p>}

          {error && <p className="text-red-400">{error}</p>}

          {!isLoading && !error && (
            <div className="text-left space-y-4 max-h-96 overflow-y-auto">
              {history.length === 0 ? (
                <p className="text-gray-400">No translations found in the database.</p>
              ) : (
                history.map((item) => (
                  <div key={item._id} className="border-b border-slate-700 pb-2">
                    <p className="text-gray-400">
                      {item.original_text} <span className="text-xs">({item.source_lang})</span>
                    </p>
                    <p className="text-lg">
                      {item.translated_text} <span className="text-xs">({item.target_lang})</span>
                    </p>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}

export default App;
