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

  const [textToSummarize, setTextToSummarize] = useState<string>('');
  const [summary, setSummary] = useState<string>('');
  const [isSummarizing, setIsSummarizing] = useState<boolean>(false);
  const [summaryError, setSummaryError] = useState<string | null>(null);


  useEffect(() => {
    setIsLoading(true);
    fetch('/api/history')
      .then((response) => {
        if (!response.ok) throw new Error('Network response was not ok');
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

  const handleSummarize = async () => {
    if (!textToSummarize.trim()) {
      setSummaryError("Please enter some text to summarize.");
      return;
    }
    
    setIsSummarizing(true);
    setSummaryError(null);
    setSummary('');

    try {
      const response = await fetch('/api/summarize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: textToSummarize }),
      });

      if (!response.ok) {
        throw new Error(`Server responded with status: ${response.status}`);
      }

      const data = await response.json();
      setSummary(data.summary);

    } catch (error) {
      console.error("Error summarizing text:", error);
      setSummaryError("Failed to generate summary. Please try again.");
    } finally {
      setIsSummarizing(false);
    }
  };


  return (
    <main className="bg-slate-900 min-h-screen flex flex-col items-center font-sans p-4 text-white">
      <div className="w-full max-w-2xl">
        <h1 className="text-4xl font-bold mb-8 text-center">TranslatAR Web Portal</h1>

        <div className="bg-slate-800 rounded-lg p-6 shadow-lg mb-8">
          <h2 className="text-2xl font-semibold mb-4 text-left">Summarize Text</h2>
          <textarea
            className="w-full bg-slate-700 p-3 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={6}
            value={textToSummarize}
            onChange={(e) => setTextToSummarize(e.target.value)}
            placeholder="Paste or type text here to summarize..."
          />
          <button
            onClick={handleSummarize}
            disabled={isSummarizing}
            className="mt-4 w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:cursor-not-allowed text-white font-bold py-2 px-4 rounded-md transition-colors duration-200"
          >
            {isSummarizing ? 'Summarizing...' : 'Summarize'}
          </button>

          {summaryError && <p className="text-red-400 mt-4">{summaryError}</p>}
          {summary && (
            <div className="mt-4 bg-slate-700 p-4 rounded-md">
              <h3 className="font-semibold mb-2">Summary:</h3>
              <p>{summary}</p>
            </div>
          )}
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
