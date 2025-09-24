import { useEffect, useState } from 'react'

function App() {
  const [message, setMessage] = useState('')
  useEffect(() => {
    fetch('/api/db-hello')
      .then((response) => response.json())
      .then((data) => {
        setMessage(data.message)
      })
      .catch((error) => {
        console.error("Error fetching data:", error)
        setMessage("Failed to load message from backend.")
      });
  }, [])

  const [count, setCount] = useState(0)

  return (
    <main className="bg-slate-900 min-h-screen flex flex-col items-center justify-center font-sans p-4">
      <h1>TranslatAR Web Portal</h1>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
        <p>
          Message fetched from backend through database: <strong>{message}</strong>
        </p>
        <p>
          Edit <code>src/App.tsx</code> and save to test HMR
        </p>
      </div>
    </main>
  )
}

export default App
