import { useState } from "react";

const API_BASE = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

const suggestions = [
  "My Wi-Fi says connected, but there’s no internet",
  "My Windows PC is running slowly",
  "My printer isn’t showing up",
];

async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options.headers },
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = typeof body.detail === "string" ? body.detail : `Request failed (${response.status})`;
    throw new Error(detail);
  }
  return body;
}

function SourceLinks({ sources, label }) {
  if (!sources?.length) return null;
  return (
    <div className="source-list">
      <span className="source-label">{label}</span>
      {sources.map((source) => (
        <a key={source.url} href={source.url} target="_blank" rel="noreferrer">
          {source.title} <span aria-hidden="true">↗</span>
        </a>
      ))}
    </div>
  );
}

function GuideDetail({ guide, onClose }) {
  if (!guide) return null;
  return (
    <div className="guide-detail-backdrop" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
      <section className="guide-detail" role="dialog" aria-modal="true" aria-labelledby="guide-detail-title">
        <button className="icon-button close-button" onClick={onClose} aria-label="Close guide">×</button>
        <span className="eyebrow">{guide.category} · {guide.applicable_os}</span>
        <h2 id="guide-detail-title">{guide.title}</h2>
        <p>{guide.summary}</p>
        <h3>Try these steps</h3>
        <ol>{guide.steps.map((step, index) => <li key={index}>{step}</li>)}</ol>
        {guide.cautions?.length > 0 && <div className="caution-box"><strong>Take care</strong><ul>{guide.cautions.map((item) => <li key={item}>{item}</li>)}</ul></div>}
        <p className="escalation"><strong>When to get more help:</strong> {guide.escalation}</p>
        <SourceLinks sources={guide.sources} label="Official references" />
      </section>
    </div>
  );
}

export default function App() {
  const [messages, setMessages] = useState([]);
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [includeWebSearch, setIncludeWebSearch] = useState(false);
  const [query, setQuery] = useState("");
  const [guides, setGuides] = useState([]);
  const [searching, setSearching] = useState(false);
  const [searchMessage, setSearchMessage] = useState("");
  const [error, setError] = useState("");
  const [selectedGuide, setSelectedGuide] = useState(null);

  async function sendMessage(value = draft) {
    const message = value.trim();
    if (!message || busy) return;
    setError("");
    setDraft("");
    const current = [...messages, { role: "user", content: message }];
    setMessages(current);
    setBusy(true);
    try {
      const result = await apiRequest("/api/v1/chat", {
        method: "POST",
        body: JSON.stringify({
          message,
          history: messages.slice(-12).map(({ role, content }) => ({ role, content })),
          include_web_search: includeWebSearch,
        }),
      });
      setMessages([...current, {
        role: "assistant",
        content: result.answer,
        guideSources: result.guide_sources || [],
        webCitations: result.web_citations || [],
      }]);
    } catch (requestError) {
      setError(`${requestError.message}. Check that the backend is running and configured.`);
      setMessages(current);
    } finally {
      setBusy(false);
    }
  }

  async function searchGuides(event) {
    event.preventDefault();
    const search = query.trim();
    if (!search || searching) return;
    setSearching(true);
    setSearchMessage("");
    try {
      const result = await apiRequest(`/api/v1/guides/search?q=${encodeURIComponent(search)}`);
      setGuides(result.results || []);
      if (!result.results?.length) setSearchMessage("No approved guide matched. The current guide set is still marked as draft.");
    } catch (requestError) {
      setSearchMessage(`${requestError.message}. Check that the backend is running.`);
    } finally {
      setSearching(false);
    }
  }

  async function openGuide(guideId) {
    try {
      setSelectedGuide(await apiRequest(`/api/v1/guides/${encodeURIComponent(guideId)}`));
    } catch (requestError) {
      setSearchMessage(requestError.message);
    }
  }

  function resetChat() {
    setMessages([]);
    setDraft("");
    setError("");
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="#top" aria-label="Everette Supporter home">
          <span className="brand-mark">e</span>
          <span>Everette <strong>Supporter</strong></span>
        </a>
        <div className="topbar-right"><span className="status-dot" /> Windows support preview <span className="version-pill">Prototype</span></div>
      </header>

      <div className="workspace" id="top">
        <aside className="sidebar">
          <button className="new-chat-button" onClick={resetChat}><span>＋</span> New conversation</button>

          <div className="sidebar-section">
            <div className="section-heading"><span>GUIDE LIBRARY</span><span className="draft-count">16 drafts</span></div>
            <form className="guide-search" onSubmit={searchGuides}>
              <label className="sr-only" htmlFor="guide-search-input">Search troubleshooting guides</label>
              <span aria-hidden="true">⌕</span>
              <input id="guide-search-input" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search guides" />
              <button type="submit" aria-label="Search guides" disabled={searching || !query.trim()}>{searching ? "…" : "↵"}</button>
            </form>
            {searchMessage && <p className="search-message">{searchMessage}</p>}
            {guides.length > 0 && <div className="guide-results" aria-live="polite">{guides.map((guide) => <button className="guide-result" key={guide.guide_id} onClick={() => openGuide(guide.guide_id)}><span className="guide-icon">⌁</span><span>{guide.title}<small>{guide.category}</small></span><span className="result-arrow">›</span></button>)}</div>}
          </div>

          <div className="sidebar-note"><span className="note-icon">i</span><p>The guide library is being reviewed. Draft guides stay hidden until approved.</p></div>
          <div className="sidebar-footer"><span className="avatar">E</span><span><strong>Local preview</strong><small>Windows 10 / 11</small></span><span className="more">•••</span></div>
        </aside>

        <main className="chat-area">
          <div className="chat-header"><div><span className="eyebrow">YOUR IT SUPPORT ASSISTANT</span><h1>Let’s figure it out.</h1></div><span className="secure-chip"><span>✦</span> Guide-led support</span></div>

          <section className={`conversation ${messages.length ? "has-messages" : ""}`} aria-live="polite">
            {messages.length === 0 ? (
              <div className="welcome">
                <div className="welcome-illustration" aria-hidden="true"><span className="sparkle sparkle-one">✦</span><span className="sparkle sparkle-two">✦</span><div className="orb"><div className="orb-face"><i /><i /><b /></div></div><span className="orbit orbit-one" /><span className="orbit orbit-two" /></div>
                <h2>What’s going on with your PC?</h2>
                <p>Describe the issue in your own words. I’ll help you work through it, one step at a time.</p>
                <div className="suggestions">{suggestions.map((suggestion) => <button key={suggestion} onClick={() => sendMessage(suggestion)}>{suggestion}<span>↗</span></button>)}</div>
              </div>
            ) : (
              <div className="message-list">{messages.map((message, index) => (
                <article className={`message ${message.role}`} key={`${message.role}-${index}`}>
                  {message.role === "assistant" && <span className="message-avatar">e</span>}
                  <div className="message-body">
                    {message.role === "assistant" && <span className="message-author">Everette <small>Support assistant</small></span>}
                    <div className="message-text">{message.content}</div>
                    <SourceLinks sources={message.guideSources} label="From your guide library" />
                    <SourceLinks sources={message.webCitations} label="Web sources" />
                  </div>
                </article>
              ))}{busy && <article className="message assistant"><span className="message-avatar">e</span><div className="typing"><i /><i /><i /><span>Looking into this…</span></div></article>}</div>
            )}
            {error && <div className="error-banner" role="alert"><strong>Couldn’t reach the assistant.</strong><span>{error}</span></div>}
          </section>

          <div className="composer-area">
            <form className="composer" onSubmit={(event) => { event.preventDefault(); sendMessage(); }}>
              <label className="sr-only" htmlFor="chat-input">Describe your Windows issue</label>
              <textarea id="chat-input" rows="1" value={draft} onChange={(event) => setDraft(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); sendMessage(); } }} placeholder="Tell me what’s happening…" disabled={busy} />
              <div className="composer-bottom"><span>Enter to send · Shift + Enter for a new line</span><button className="send-button" type="submit" aria-label="Send message" disabled={busy || !draft.trim()}><span>↑</span></button></div>
            </form>
            <div className="composer-options">
              <label className="toggle-label"><input type="checkbox" checked={includeWebSearch} onChange={(event) => setIncludeWebSearch(event.target.checked)} /><span className="toggle" /><span>Search Microsoft support online</span></label>
              <span className="privacy-hint">{includeWebSearch ? "Your question goes to OpenAI and may be searched on Microsoft sites." : "Messages are sent to OpenAI to generate replies."}</span>
            </div>
            <p className="disclaimer">Preview only · I can guide you, but I can’t see or change your computer.</p>
          </div>
        </main>
      </div>
      <GuideDetail guide={selectedGuide} onClose={() => setSelectedGuide(null)} />
    </div>
  );
}
