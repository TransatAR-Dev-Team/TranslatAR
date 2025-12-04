interface SummaryHistoryProps {
  history: any[];
  loading?: boolean;
}

export default function SummaryHistory({
  history,
  loading = false,
}: SummaryHistoryProps) {
  if (loading) return <p>Loading...</p>;

  return (
    <div className="bg-slate-800 rounded-lg p-6 shadow-lg">
      <h2 className="text-2xl font-semibold mb-4">Summary History</h2>

      {history.length === 0 ? (
        <p>No saved summaries yet.</p>
      ) : (
        history.map((item) => (
          <div key={item.id || item._id} className="mb-4 border-b pb-2">
            <p className="text-white font-medium">{item.summary}</p>
            <p className="text-gray-400 text-xs mt-1">
              {new Date(item.created_at).toLocaleString()}
            </p>
          </div>
        ))
      )}
    </div>
  );
}
