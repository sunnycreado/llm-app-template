import { useChatStore } from "../../store";

export function Sidebar() {
  const { sessions, activeSessionId, setActiveSession, createSession } = useChatStore();

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="logo-mark">LM</div>
        <span className="logo-text">LLM App</span>
      </div>

      <button className="new-chat-btn" onClick={() => createSession()}>
        + New chat
      </button>

      <nav className="sidebar-nav">
        {sessions.map((s) => (
          <button
            key={s.id}
            className={`nav-item ${activeSessionId === s.id ? "nav-item--active" : ""}`}
            onClick={() => setActiveSession(s.id)}
          >
            <span className="nav-icon">💬</span>
            <span className="nav-label">{s.title}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="model-badge">
          <span className="dot dot--green" />
          NIM Live
        </div>
      </div>
    </aside>
  );
}
