import { useEffect } from "react";
import { ChatInput } from "./components/chat/ChatInput";
import { ChatWindow } from "./components/chat/ChatWindow";
import { Sidebar } from "./components/ui/Sidebar";
import { TopBar } from "./components/ui/TopBar";
import { useChat } from "./hooks/useChat";
import { useChatStore } from "./store";

export default function App() {
  const { send, isLoading, messages } = useChat();
  const { createSession, activeSessionId } = useChatStore();

  // Start with one session on load
  useEffect(() => {
    if (!activeSessionId) createSession();
  }, []);

  return (
    <div className="shell">
      <Sidebar />
      <div className="main">
        <TopBar />
        <ChatWindow messages={messages} />
        <ChatInput onSend={send} disabled={isLoading} />
      </div>
    </div>
  );
}
