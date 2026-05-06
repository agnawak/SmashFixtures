import { useState, useRef, useEffect } from 'react';
import './App.css';

const API_URL = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? 'http://localhost:8001' : '/api');

function ChatPage({ apiKey }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (e) => {
    e.preventDefault();
    const text = input.trim();
    if (!text || loading) return;

    const userMsg = { role: 'user', text };
    const nextMessages = [...messages, userMsg];
    setMessages(nextMessages);
    setInput('');
    setLoading(true);
    setError('');

    try {
      const history = messages.map((m) => ({ role: m.role, text: m.text }));
      const res = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-API-Key': apiKey },
        body: JSON.stringify({ message: text, history }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || `Error ${res.status}`);
      }
      const { reply } = await res.json();
      setMessages([...nextMessages, { role: 'model', text: reply }]);
    } catch (err) {
      setError(err.message);
      setMessages(nextMessages.slice(0, -1));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-messages">
        {messages.length === 0 && (
          <p className="chat-empty">Ask Gemini anything…</p>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`chat-bubble ${m.role === 'user' ? 'chat-user' : 'chat-model'}`}>
            <span className="chat-role">{m.role === 'user' ? 'You' : 'Gemini'}</span>
            <p>{m.text}</p>
          </div>
        ))}
        {loading && (
          <div className="chat-bubble chat-model">
            <span className="chat-role">Gemini</span>
            <p className="chat-typing">Thinking…</p>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      {error && <p className="msg error" style={{ margin: '0.5rem 0' }}>{error}</p>}
      <form className="chat-form" onSubmit={sendMessage}>
        <input
          type="text"
          className="chat-input"
          placeholder="Type a message…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()} className="chat-send">
          Send
        </button>
      </form>
    </div>
  );
}

function AuthForm({ onAuth }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [mode, setMode] = useState('login');
  const [status, setStatus] = useState('idle');
  const [errorMsg, setErrorMsg] = useState('');

  const handleAuth = async (e) => {
    e.preventDefault();
    setStatus('loading');
    setErrorMsg('');
    try {
      const endpoint = mode === 'login' ? '/login' : '/signup';
      const res = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        const action = mode === 'login' ? 'Login' : 'Signup';
        throw new Error(data.detail || `${action} failed (${res.status})`);
      }
      const { api_key, username: confirmedUsername } = await res.json();
      onAuth(api_key, confirmedUsername || username);
    } catch (err) {
      setErrorMsg(err.message);
      setStatus('error');
    }
  };

  return (
    <div className="card">
      <h1>Fixture Generator</h1>
      <p className="subtitle">Sign in or create an account</p>
      <form onSubmit={handleAuth}>
        <label>
          Username
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Enter username"
            required
            autoComplete="username"
          />
        </label>
        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter password"
            required
            autoComplete="current-password"
          />
        </label>
        <label>
          Action
          <select value={mode} onChange={(e) => setMode(e.target.value)}>
            <option value="login">Login</option>
            <option value="signup">Sign Up</option>
          </select>
        </label>
        <button type="submit" disabled={status === 'loading'}>
          {status === 'loading' ? 'Please wait...' : mode === 'login' ? 'Sign In' : 'Create Account'}
        </button>
      </form>
      {status === 'error' && <p className="msg error">{errorMsg}</p>}
    </div>
  );
}

function App() {
  const [apiKey, setApiKey] = useState(null);
  const [currentUser, setCurrentUser] = useState('');
  const [page, setPage] = useState('fixtures'); // 'fixtures' | 'chat'
  const [mode, setMode] = useState('standard'); // 'standard' | 'custom'

  // Standard mode
  const [numTeams, setNumTeams] = useState(4);
  const [minGroups, setMinGroups] = useState(10);

  // Custom mode
  const [playersPerTeam, setPlayersPerTeam] = useState(7);
  const [customMinGroups, setCustomMinGroups] = useState(10);
  const [useSetters, setUseSetters] = useState(true);
  const [useTierlists, setUseTierlists] = useState(true);

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

    let url;
    if (mode === 'standard') {
      const params = new URLSearchParams({
        num_teams: numTeams,
        min_groups: minGroups,
      });
      url = `${API_URL}/generate?${params}`;
    } else {
      const params = new URLSearchParams({
        players_per_team: playersPerTeam,
        min_groups: customMinGroups,
        use_setters: useSetters,
        use_tierlists: useTierlists,
      });
      url = `${API_URL}/generate-custom?${params}`;
    }

    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'X-API-Key': apiKey },
        body: formData,
      });

      if (!res.ok) {
        const detail = await res.text();
        throw new Error(detail || `Server responded with ${res.status}`);
      }

      const blob = await res.blob();
      const objectUrl = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = objectUrl;
      a.download = mode === 'standard' ? 'Fixtures.xlsx' : 'CustomFixtures.xlsx';
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(objectUrl);

      setStatus('success');
    } catch (err) {
      setErrorMsg(err.message);
      setStatus('error');
    }
  };

  const handleAuthSuccess = (key, username) => {
    setApiKey(key);
    setCurrentUser(username || '');
  };

  if (!apiKey) {
    return <AuthForm onAuth={handleAuthSuccess} />;
  }

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>{page === 'fixtures' ? `Fixture Generator${currentUser ? ` (${currentUser})` : ''}` : 'AI Chat'}</h1>
        <button
          type="button"
          onClick={() => {
            setApiKey(null);
            setCurrentUser('');
          }}
          style={{ width: 'auto', padding: '0.4rem 0.8rem', fontSize: '0.85rem' }}
        >
          Sign Out
        </button>
      </div>

      <div className="tab-bar">
        <button
          type="button"
          className={`tab-btn${page === 'fixtures' ? ' active' : ''}`}
          onClick={() => setPage('fixtures')}
        >
          Fixtures
        </button>
        <button
          type="button"
          className={`tab-btn${page === 'chat' ? ' active' : ''}`}
          onClick={() => setPage('chat')}
        >
          AI Chat
        </button>
      </div>

      {page === 'chat' ? (
        <ChatPage apiKey={apiKey} />
      ) : (
        <>
      <p className="subtitle">Upload a spreadsheet to generate fixtures</p>

      <form onSubmit={handleSubmit}>
        <label>
          Mode
          <select value={mode} onChange={(e) => setMode(e.target.value)}>
            <option value="standard">Standard (fixed team count)</option>
            <option value="custom">Custom (players per team)</option>
          </select>
        </label>

        {mode === 'standard' ? (
          <>
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
          </>
        ) : (
          <>
            <label>
              Players Per Team
              <input
                type="number"
                min={2}
                value={playersPerTeam}
                onChange={(e) => setPlayersPerTeam(Number(e.target.value))}
              />
            </label>

            <label>
              Minimum Groups
              <input
                type="number"
                min={1}
                value={customMinGroups}
                onChange={(e) => setCustomMinGroups(Number(e.target.value))}
              />
            </label>

            <label style={{ flexDirection: 'row', alignItems: 'center', gap: '0.5rem' }}>
              <input
                type="checkbox"
                checked={useSetters}
                onChange={(e) => setUseSetters(e.target.checked)}
              />
              Include Setters (1 setter per team)
            </label>

            <label style={{ flexDirection: 'row', alignItems: 'center', gap: '0.5rem' }}>
              <input
                type="checkbox"
                checked={useTierlists}
                onChange={(e) => setUseTierlists(e.target.checked)}
              />
              Use Tier Lists (balance teams by tier points)
            </label>
          </>
        )}

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
        </>
      )}
    </div>
  );
}

export default App;
