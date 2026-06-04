import { useEffect, useRef } from "react";
import type { Message } from "../../types";
import { ChatBubble } from "./ChatBubble";

export function ChatWindow({ messages }: { messages: Message[] }) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="messages">
      {messages.map((m) => (
        <ChatBubble key={m.id} message={m} />
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
