import { useState } from "react";

interface SummarizerProps {
  onSaveSuccess?: () => void;
}

export default function Summarizer({ onSaveSuccess }: SummarizerProps) {
  const [textToSummarize, setTextToSummarize] = useState<string>("");
  const [summary, setSummary] = useState<string>("");
  const [summaryLength, setSummaryLength] = useState<string>("medium");
  const [isSummarizing, setIsSummarizing] = useState<boolean>(false);
  const [summaryError, setSummaryError] = useState<string | null>(null);
  const [advice, setAdvice] = useState<string>("");
  const [isGettingAdvice, setIsGettingAdvice] = useState<boolean>(false);
  const [adviceError, setAdviceError] = useState<string | null>(null);
  const LOCAL_STORAGE_JWT_KEY = "translatar_jwt";
  const [isLoggedIn, setIsLoggedIn] = useState<string | null>(null);
  const handleSummarize = async () => {
    if (!textToSummarize.trim()) {
      setSummaryError("Please enter some text to summarize.");
      return;
    }

    setIsSummarizing(true);
    setSummaryError(null);
    setSummary("");

    try {
      const response = await fetch("/api/summarize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: textToSummarize, length: summaryLength }),
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

  const handleGetAdvice = async () => {
    if (!textToSummarize.trim()) {
      setAdviceError("Please enter some text to get advice.");
      return;
    }

    setIsGettingAdvice(true);
    setAdviceError(null);
    setAdvice("");

    try {
      const response = await fetch("/api/advice", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: textToSummarize }),
      });

      if (!response.ok) {
        throw new Error(`Server responded with status: ${response.status}`);
      }

      const data = await response.json();
      setAdvice(data.advice);
    } catch (error) {
      console.error("Error getting advice:", error);
      setAdviceError("Failed to generate advice. Please try again.");
    } finally {
      setIsGettingAdvice(false);
    }
  };

  const handleSaveSummary = async (summaryText: string) => {
    const token = localStorage.getItem(LOCAL_STORAGE_JWT_KEY);

    if (!token) {
      alert("You must be logged in to save a summary.");
      return;
    }

    try {
      const response = await fetch("/api/summarize/save", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          summary: summaryText,
          original_text: textToSummarize,
        }),
      });

      if (!response.ok) {
        const err = await response.text();
        console.error("Backend returned:", err);
        throw new Error("Failed to save summary");
      }

      alert("Summary saved!");
      if (onSaveSuccess) onSaveSuccess();
    } catch (error) {
      console.error("Error saving summary:", error);
      alert("Failed to save summary.");
    }
  };

  return (
    <div className="bg-slate-800 rounded-lg p-6 shadow-lg mb-8">
      <h2 className="text-2xl font-semibold mb-4 text-left">
        Insert Conversation
      </h2>
      <textarea
        className="w-full bg-slate-700 p-3 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
        rows={6}
        value={textToSummarize}
        onChange={(e) => setTextToSummarize(e.target.value)}
        placeholder="Paste or type text here to summarize..."
      />
      <div className="flex items-center mt-4 space-x-4">
        <label htmlFor="summary-length" className="font-semibold">
          Summary Length:
        </label>
        <select
          id="summary-length"
          value={summaryLength}
          onChange={(e) => setSummaryLength(e.target.value)}
          className="bg-slate-700 p-2 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="short">Short</option>
          <option value="medium">Medium</option>
          <option value="long">Long</option>
        </select>
      </div>
      <button
        onClick={handleSummarize}
        disabled={isSummarizing}
        className="mt-4 w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:cursor-not-allowed text-white font-bold py-2 px-4 rounded-md transition-colors duration-200"
      >
        {isSummarizing ? "Summarizing..." : "Summarize"}
      </button>
      {summaryError && <p className="text-red-400 mt-4">{summaryError}</p>}
      {summary && (
        <div className="mt-4 bg-slate-700 p-4 rounded-md">
          <h3 className="font-semibold mb-2">Summary:</h3>
          <p>{summary}</p>

          {/* Save Summary Button */}
          <button
            onClick={() => handleSaveSummary(summary)}
            className="mt-4 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold py-1 px-3 rounded-md transition-colors duration-200"
          >
            Save
          </button>
        </div>
      )}
      <button
        onClick={handleGetAdvice}
        disabled={isGettingAdvice}
        className="mt-4 w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:cursor-not-allowed text-white font-bold py-2 px-4 rounded-md transition-colors duration-200"
      >
        {isGettingAdvice ? "Getting Advice..." : "Give Me Advice"}
      </button>
      {adviceError && <p className="text-red-400 mt-4">{adviceError}</p>}
      {advice && (
        <div className="mt-4 bg-slate-700 p-4 rounded-md">
          <h3 className="font-semibold mb-2">Learning Advice:</h3>
          <p>{advice}</p>
        </div>
      )}
    </div>
  );
}
