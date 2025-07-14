import { useEffect, useState } from "react";
import "./App.css";
import logo from "./logo.svg";
import gameDataApi from "./services/api";

function App() {
  const [backendStatus, setBackendStatus] = useState<string>("Checking...");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await gameDataApi.ping();
        setBackendStatus(`Backend connected: ${response.message}`);
        setError(null);
      } catch (err) {
        setBackendStatus("Backend not available");
        setError(err instanceof Error ? err.message : "Unknown error");
      }
    };

    checkBackend();
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <h1>Mids-Web</h1>
        <p>Modern Web Rewrite of Mids Reborn Character Planner</p>
        <div className="status">
          <p>Status: {backendStatus}</p>
          {error && <p className="error">Error: {error}</p>}
        </div>
        <p>Welcome to the next generation of City of Heroes build planning!</p>
        <div className="features">
          <h3>Coming Soon:</h3>
          <ul>
            <li>✨ Archetype and Powerset Selection</li>
            <li>⚡ Real-time Build Calculations</li>
            <li>🎯 Enhancement Slotting Interface</li>
            <li>📊 Advanced Statistics Display</li>
            <li>💾 Build Import/Export</li>
            <li>🌐 Cross-platform Web Access</li>
          </ul>
        </div>
      </header>
    </div>
  );
}

export default App;
