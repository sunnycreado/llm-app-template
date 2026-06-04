import { useChatStore } from "../../store";

export function TopBar() {
  const { isLoading } = useChatStore();

  return (
    <header className="topbar">
      <div className="topbar-title">
        <h1>Chat</h1>
      </div>
      <div className="topbar-right">
        <span className={`status-chip ${isLoading ? "status-chip--live" : ""}`}>
          {isLoading ? "Thinking" : "Ready"}
        </span>
      </div>
    </header>
  );
}
