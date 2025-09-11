import { useEffect, useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [message, setMessage] = useState('')
  useEffect(() => {
    // The URL '/api/data' works because of the proxy you set up in vite.config.ts
    fetch('http://127.0.0.1:8000/api/db-hello')
      .then((response) => response.json())
      .then((data) => {
        // 4. Update the state with the fetched message
        setMessage(data.message)
      })
      .catch((error) => {
        console.error("Error fetching data:", error)
        setMessage("Failed to load message from backend.")
      });
  }, []) // The empty array [] means this effect runs only once after the initial render



  const [count, setCount] = useState(0)

  return (
    <>
      <div>
        <a href="https://vite.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React</h1>
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
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
    </>
  )
}

export default App
