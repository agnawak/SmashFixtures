import { useState, useRef } from 'react';
import './App.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [apiKey, setApiKey] = useState('');
  const [numTeams, setNumTeams] = useState(4);
  const [minGroups, setMinGroups] = useState(10);
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('idle'); // idle | loading | success | error
  const [errorMsg, setErrorMsg] = useState('');
  const fileInputRef = useRef(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setErrorMsg('Please select a file.');
      setStatus('error');
      return;
    }

    setStatus('loading');
    setErrorMsg('');

    const formData = new FormData();
    formData.append('file', file);

    const params = new URLSearchParams({
      num_teams: numTeams,
      min_groups: minGroups,
    });

    try {
      const res = await fetch(`${API_URL}/generate?${params}`, {
        method: 'POST',
        headers: { 'X-API-Key': apiKey },
        body: formData,
      });

      if (!res.ok) {
        const detail = await res.text();
        throw new Error(detail || `Server responded with ${res.status}`);
      }

      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'Fixtures.xlsx';
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);

      setStatus('success');
    } catch (err) {
      setErrorMsg(err.message);
      setStatus('error');
    }
  };

  return (
    <div className="card">
      <h1>Fixture Generator</h1>
      <p className="subtitle">Upload a spreadsheet to generate fixtures</p>

      <form onSubmit={handleSubmit}>
        <label>
          API Key
          <input
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="Enter your API key"
            required
          />
        </label>

        <label>
          Number of Teams
          <input
            type="number"
            min={2}
            value={numTeams}
            onChange={(e) => setNumTeams(Number(e.target.value))}
          />
        </label>

        <label>
          Minimum Groups
          <input
            type="number"
            min={1}
            value={minGroups}
            onChange={(e) => setMinGroups(Number(e.target.value))}
          />
        </label>

        <label>
          Upload File
          <input
            ref={fileInputRef}
            type="file"
            accept=".xlsx,.xls,.csv"
            onChange={(e) => setFile(e.target.files[0] || null)}
          />
        </label>

        <button type="submit" disabled={status === 'loading'}>
          {status === 'loading' ? 'Generating…' : 'Generate Fixtures'}
        </button>
      </form>

      {status === 'success' && (
        <p className="msg success">Fixtures downloaded successfully!</p>
      )}
      {status === 'error' && (
        <p className="msg error">{errorMsg}</p>
      )}
    </div>
  );
}

export default App;
